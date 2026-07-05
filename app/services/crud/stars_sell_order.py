from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from re import Pattern
from re import compile as re_compile
from typing import Optional
from uuid import uuid4

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.enums.stars_sell_order import (
    StarsSellOrderResolutionReason,
    StarsSellOrderStatus,
    StarsSellPayoutMethod,
)
from app.models.config import AppConfig
from app.models.dto.stars_sell_order import StarsSellOrderDto
from app.models.sql.stars_sell_order import StarsSellOrder
from app.services.crud.base import CrudService
from app.services.postgres import SQLSessionContext
from app.utils.time import datetime_now

_TON_ADDRESS_RE: Pattern[str] = re_compile(r"^(?:UQ|EQ)[A-Za-z0-9_-]{46}$")


class StarsSellOrderError(RuntimeError):
    pass


class ValidationError(StarsSellOrderError):
    pass


class OrderNotFoundError(StarsSellOrderError):
    pass


class StatusConflictError(StarsSellOrderError):
    pass


class NotReadyForPayoutError(StarsSellOrderError):
    def __init__(self, *, payout_available_at: datetime | None) -> None:
        self.payout_available_at = payout_available_at
        super().__init__("Sell order is not ready for payout yet.")


@dataclass(frozen=True, slots=True)
class StarsSellAdminStats:
    total_orders: int
    total_paid_stars: int
    completed_payout_cents: int
    ready_for_payout_count: int


@dataclass(frozen=True, slots=True)
class StarsSellQuote:
    stars_count: int
    payout_amount_cents: int
    invoice_total_amount: int
    hold_days: int


@dataclass(frozen=True, slots=True)
class StarsSellOrderCreateResult:
    order: StarsSellOrderDto
    reused_existing: bool
    replaced_existing: bool


class StarsSellOrderService(CrudService):
    def __init__(
        self,
        *,
        session_pool: async_sessionmaker[AsyncSession],
        redis: Redis,
        config: AppConfig,
    ) -> None:
        super().__init__(session_pool=session_pool, redis=redis, config=config)
        self.min_stars = max(1, int(config.payments.stars_sell_min_stars))
        self.max_stars = max(self.min_stars, int(config.payments.stars_sell_max_stars))
        self.hold_days = max(1, int(config.payments.stars_sell_hold_days))
        self.usd_per_star = self._parse_positive_decimal(
            config.payments.stars_sell_usd_per_star,
            default="0.0118",
        )

    @staticmethod
    def _parse_positive_decimal(raw: str, *, default: str) -> Decimal:
        normalized = (raw or "").strip().replace(",", ".")
        if not normalized:
            normalized = default
        try:
            parsed = Decimal(normalized)
        except InvalidOperation:
            parsed = Decimal(default)
        if parsed <= 0:
            parsed = Decimal(default)
        return parsed

    def _validate_stars_count(self, stars_count: int) -> int:
        value = int(stars_count)
        if value < self.min_stars or value > self.max_stars:
            raise ValidationError(
                f"Stars count must be between {self.min_stars} and {self.max_stars}."
            )
        return value

    @staticmethod
    def _normalize_payout_wallet(value: str) -> str:
        wallet = (value or "").strip()
        if not wallet:
            raise ValidationError("Payout wallet is required.")
        if not _TON_ADDRESS_RE.fullmatch(wallet):
            raise ValidationError("Payout wallet must be a valid TON address.")
        return wallet

    def _payout_amount_cents(self, *, stars_count: int) -> int:
        amount_cents = (Decimal(stars_count) * self.usd_per_star * Decimal("100")).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
        return max(0, int(amount_cents))

    def build_quote(self, *, stars_count: int) -> StarsSellQuote:
        normalized_stars = self._validate_stars_count(stars_count)
        return StarsSellQuote(
            stars_count=normalized_stars,
            payout_amount_cents=self._payout_amount_cents(stars_count=normalized_stars),
            invoice_total_amount=normalized_stars,
            hold_days=self.hold_days,
        )

    async def create_order(
        self,
        *,
        user_id: int,
        stars_count: int,
        payout_wallet: str,
        payout_method: StarsSellPayoutMethod = StarsSellPayoutMethod.TON_USDT,
    ) -> StarsSellOrderDto:
        result = await self.create_or_refresh_pending_order(
            user_id=user_id,
            stars_count=stars_count,
            payout_wallet=payout_wallet,
            payout_method=payout_method,
        )
        return result.order

    async def create_or_refresh_pending_order(
        self,
        *,
        user_id: int,
        stars_count: int,
        payout_wallet: str,
        payout_method: StarsSellPayoutMethod = StarsSellPayoutMethod.TON_USDT,
    ) -> StarsSellOrderCreateResult:
        normalized_stars = self._validate_stars_count(stars_count)
        normalized_wallet = self._normalize_payout_wallet(payout_wallet)
        payout_amount_cents = self._payout_amount_cents(stars_count=normalized_stars)

        def _same_pending_order(order: StarsSellOrder) -> bool:
            return (
                int(order.stars_count) == normalized_stars
                and order.payout_method == payout_method
                and order.payout_wallet == normalized_wallet
                and int(order.invoice_total_amount) == normalized_stars
                and int(order.payout_amount_cents) == payout_amount_cents
            )

        async with SQLSessionContext(session_pool=self.session_pool) as (repository, uow):
            pending = await repository.stars_sell_orders.get_open_payment_for_user(user_id=user_id)
            if pending is not None:
                if _same_pending_order(pending):
                    return StarsSellOrderCreateResult(
                        order=pending.dto(),
                        reused_existing=True,
                        replaced_existing=False,
                    )
                await repository.stars_sell_orders.update_if_status(
                    order_id=int(pending.id),
                    current_statuses=[StarsSellOrderStatus.PENDING_PAYMENT],
                    status=StarsSellOrderStatus.CANCELED,
                    failure_reason=None,
                    resolution_reason=StarsSellOrderResolutionReason.REPLACED_BY_NEW_REQUEST,
                    resolution_note=None,
                )

            order = StarsSellOrder(
                user_id=user_id,
                stars_count=normalized_stars,
                payout_method=payout_method,
                payout_wallet=normalized_wallet,
                payout_amount_cents=payout_amount_cents,
                invoice_payload=f"stars_sell:{uuid4().hex}",
                invoice_total_amount=normalized_stars,
                status=StarsSellOrderStatus.PENDING_PAYMENT,
                resolution_reason=None,
                resolution_note=None,
            )
            await uow.commit(order)
            return StarsSellOrderCreateResult(
                order=order.dto(),
                reused_existing=False,
                replaced_existing=pending is not None,
            )

    async def get(self, *, order_id: int) -> Optional[StarsSellOrderDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            order = await repository.stars_sell_orders.get(order_id=order_id)
            if order is None:
                return None
            return order.dto()

    async def get_open_payment_for_user(self, *, user_id: int) -> Optional[StarsSellOrderDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            order = await repository.stars_sell_orders.get_open_payment_for_user(user_id=user_id)
            if order is None:
                return None
            return order.dto()

    async def list_recent(self, *, user_id: int, limit: int = 8) -> list[StarsSellOrderDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            orders = await repository.stars_sell_orders.list_recent_by_user(
                user_id=user_id,
                limit=limit,
            )
            return [item.dto() for item in orders]

    async def list_recent_page(
        self,
        *,
        user_id: int,
        page: int,
        page_size: int,
    ) -> tuple[list[StarsSellOrderDto], bool, int]:
        safe_page = max(0, page)
        safe_page_size = max(1, page_size)
        offset = safe_page * safe_page_size
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            total_count = await repository.stars_sell_orders.count_by_user(user_id=user_id)
            orders = await repository.stars_sell_orders.list_by_user_page(
                user_id=user_id,
                limit=safe_page_size + 1,
                offset=offset,
            )
        total_pages = max(1, (total_count + safe_page_size - 1) // safe_page_size)
        has_next = safe_page + 1 < total_pages
        page_orders = orders[:safe_page_size]
        return [item.dto() for item in page_orders], has_next, total_pages

    async def get_user_order(
        self,
        *,
        user_id: int,
        order_id: int,
    ) -> Optional[StarsSellOrderDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            order = await repository.stars_sell_orders.get_by_user(
                user_id=user_id,
                order_id=order_id,
            )
            if order is None:
                return None
            return order.dto()

    async def list_admin_page(
        self,
        *,
        page: int,
        page_size: int,
        user_id: int | None = None,
        status: StarsSellOrderStatus | None = None,
        search: str | None = None,
    ) -> tuple[list[StarsSellOrderDto], bool, int]:
        safe_page = max(0, page)
        safe_page_size = max(1, page_size)
        safe_offset = safe_page * safe_page_size
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            total_count = await repository.stars_sell_orders.count_for_admin(
                user_id=user_id,
                status=status,
                search=search,
            )
            orders = await repository.stars_sell_orders.list_for_admin(
                limit=safe_page_size + 1,
                offset=safe_offset,
                user_id=user_id,
                status=status,
                search=search,
            )
        total_pages = max(1, (total_count + safe_page_size - 1) // safe_page_size)
        has_next = safe_page + 1 < total_pages
        return [item.dto() for item in orders[:safe_page_size]], has_next, total_pages

    async def admin_stats(self) -> StarsSellAdminStats:
        now = datetime_now()
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            total_orders = await repository.stars_sell_orders.count()
            total_paid_stars = await repository.stars_sell_orders.sum_paid_stars()
            completed_payout_cents = (
                await repository.stars_sell_orders.sum_completed_payout_cents()
            )
            ready_for_payout_count = await repository.stars_sell_orders.count_ready_for_payout(
                now=now
            )
        return StarsSellAdminStats(
            total_orders=total_orders,
            total_paid_stars=total_paid_stars,
            completed_payout_cents=completed_payout_cents,
            ready_for_payout_count=ready_for_payout_count,
        )

    async def attach_invoice_message(
        self,
        *,
        order_id: int,
        message_id: int,
    ) -> Optional[StarsSellOrderDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            order = await repository.stars_sell_orders.update_if_status(
                order_id=order_id,
                current_statuses=[StarsSellOrderStatus.PENDING_PAYMENT],
                invoice_message_id=message_id,
            )
            if order is None:
                order = await repository.stars_sell_orders.get(order_id=order_id)
            return order.dto() if order is not None else None

    async def mark_invoice_send_failed(
        self,
        *,
        order_id: int,
        reason: str,
    ) -> Optional[StarsSellOrderDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            order = await repository.stars_sell_orders.update_if_status(
                order_id=order_id,
                current_statuses=[StarsSellOrderStatus.PENDING_PAYMENT],
                status=StarsSellOrderStatus.FAILED,
                failure_reason=(reason or "").strip()[:512] or None,
                resolution_reason=None,
                resolution_note=None,
            )
            if order is None:
                order = await repository.stars_sell_orders.get(order_id=order_id)
            return order.dto() if order is not None else None

    async def validate_pre_checkout(
        self,
        *,
        user_id: int,
        payload: str,
        currency: str,
        total_amount: int,
    ) -> tuple[bool, str]:
        if currency != "XTR":
            return False, "Unsupported currency."
        if not payload.strip():
            return False, "Invoice payload is empty."
        if total_amount <= 0:
            return False, "Invalid payment amount."

        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            order = await repository.stars_sell_orders.get_by_invoice_payload(
                invoice_payload=payload.strip()
            )
            if order is None:
                return False, "Order not found."
            if int(order.user_id) != int(user_id):
                return False, "Order belongs to another user."
            if order.status != StarsSellOrderStatus.PENDING_PAYMENT:
                return False, "Order is not awaiting payment."
            if int(order.invoice_total_amount) != int(total_amount):
                return False, "Invoice amount mismatch."
        return True, ""

    async def process_successful_payment(
        self,
        *,
        user_id: int,
        payload: str,
        total_amount: int,
        telegram_payment_charge_id: str | None,
        provider_payment_charge_id: str | None,
    ) -> Optional[StarsSellOrderDto]:
        if not payload.strip():
            return None
        now = datetime_now()
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            order = await repository.stars_sell_orders.get_by_invoice_payload(
                invoice_payload=payload.strip()
            )
            if order is None:
                return None
            if int(order.user_id) != int(user_id):
                return None
            if int(order.invoice_total_amount) != int(total_amount):
                return None

            if order.status in {
                StarsSellOrderStatus.PAID_HOLD,
                StarsSellOrderStatus.COMPLETED,
            }:
                return order.dto()
            if order.status != StarsSellOrderStatus.PENDING_PAYMENT:
                return None

            updated = await repository.stars_sell_orders.update_if_status(
                order_id=int(order.id),
                current_statuses=[StarsSellOrderStatus.PENDING_PAYMENT],
                status=StarsSellOrderStatus.PAID_HOLD,
                paid_stars_amount=int(total_amount),
                telegram_payment_charge_id=(telegram_payment_charge_id or "").strip() or None,
                provider_payment_charge_id=(provider_payment_charge_id or "").strip() or None,
                paid_at=now,
                payout_available_at=now + timedelta(days=self.hold_days),
                failure_reason=None,
                resolution_reason=None,
                resolution_note=None,
                rejected_at=None,
                refunded_at=None,
            )
            if updated is None:
                updated = await repository.stars_sell_orders.get(order_id=int(order.id))
            return updated.dto() if updated is not None else None

    async def cancel_pending_order(
        self,
        *,
        user_id: int,
        order_id: int,
    ) -> Optional[StarsSellOrderDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            order = await repository.stars_sell_orders.get_by_user(
                user_id=user_id,
                order_id=order_id,
            )
            if order is None:
                return None

            if order.status != StarsSellOrderStatus.PENDING_PAYMENT:
                return order.dto()

            updated = await repository.stars_sell_orders.update_if_status(
                order_id=order_id,
                current_statuses=[StarsSellOrderStatus.PENDING_PAYMENT],
                status=StarsSellOrderStatus.CANCELED,
                failure_reason=None,
                resolution_reason=StarsSellOrderResolutionReason.USER_REQUEST,
                resolution_note=None,
            )
            if updated is None:
                updated = await repository.stars_sell_orders.get(order_id=order_id)
            return updated.dto() if updated is not None else None

    @staticmethod
    def _normalize_note(note: str | None) -> str | None:
        normalized = (note or "").strip()
        if not normalized:
            return None
        return normalized[:1024]

    async def mark_completed(
        self,
        *,
        order_id: int,
        allow_before_hold: bool = False,
        note: str | None = None,
    ) -> StarsSellOrderDto:
        now = datetime_now()
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            order = await repository.stars_sell_orders.get(order_id=order_id)
            if order is None:
                raise OrderNotFoundError(f"Sell order {order_id} not found.")
            if order.status != StarsSellOrderStatus.PAID_HOLD:
                raise StatusConflictError(
                    f"Sell order {order_id} status is {order.status.value}, expected paid_hold."
                )
            if (
                not allow_before_hold
                and (order.payout_available_at is None or order.payout_available_at > now)
            ):
                raise NotReadyForPayoutError(payout_available_at=order.payout_available_at)

            updated = await repository.stars_sell_orders.update_if_status(
                order_id=order_id,
                current_statuses=[StarsSellOrderStatus.PAID_HOLD],
                status=StarsSellOrderStatus.COMPLETED,
                completed_at=now,
                failure_reason=None,
                resolution_reason=None,
                resolution_note=self._normalize_note(note),
            )
            if updated is None:
                latest = await repository.stars_sell_orders.get(order_id=order_id)
                if latest is None:
                    raise OrderNotFoundError(f"Sell order {order_id} not found.")
                if latest.status != StarsSellOrderStatus.COMPLETED:
                    raise StatusConflictError("Failed to mark sell order completed.")
                return latest.dto()
            return updated.dto()

    async def mark_rejected(
        self,
        *,
        order_id: int,
        reason: StarsSellOrderResolutionReason,
        note: str | None = None,
    ) -> StarsSellOrderDto:
        now = datetime_now()
        allowed_statuses = [
            StarsSellOrderStatus.PENDING_PAYMENT,
            StarsSellOrderStatus.PAID_HOLD,
        ]
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            order = await repository.stars_sell_orders.get(order_id=order_id)
            if order is None:
                raise OrderNotFoundError(f"Sell order {order_id} not found.")
            if order.status not in allowed_statuses:
                raise StatusConflictError(
                    f"Sell order {order_id} status is {order.status.value}, cannot reject."
                )
            updated = await repository.stars_sell_orders.update_if_status(
                order_id=order_id,
                current_statuses=allowed_statuses,
                status=StarsSellOrderStatus.REJECTED,
                resolution_reason=reason,
                resolution_note=self._normalize_note(note),
                rejected_at=now,
                failure_reason=None,
            )
            if updated is None:
                latest = await repository.stars_sell_orders.get(order_id=order_id)
                if latest is None:
                    raise OrderNotFoundError(f"Sell order {order_id} not found.")
                if latest.status != StarsSellOrderStatus.REJECTED:
                    raise StatusConflictError("Failed to mark sell order rejected.")
                return latest.dto()
            return updated.dto()

    async def mark_refunded(
        self,
        *,
        order_id: int,
        note: str | None = None,
    ) -> StarsSellOrderDto:
        now = datetime_now()
        allowed_statuses = [
            StarsSellOrderStatus.PAID_HOLD,
            StarsSellOrderStatus.COMPLETED,
        ]
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            order = await repository.stars_sell_orders.get(order_id=order_id)
            if order is None:
                raise OrderNotFoundError(f"Sell order {order_id} not found.")
            if order.status not in allowed_statuses:
                raise StatusConflictError(
                    f"Sell order {order_id} status is {order.status.value}, cannot mark refunded."
                )
            updated = await repository.stars_sell_orders.update_if_status(
                order_id=order_id,
                current_statuses=allowed_statuses,
                status=StarsSellOrderStatus.REFUNDED,
                resolution_reason=StarsSellOrderResolutionReason.STARS_REFUNDED,
                resolution_note=self._normalize_note(note),
                refunded_at=now,
                failure_reason=None,
            )
            if updated is None:
                latest = await repository.stars_sell_orders.get(order_id=order_id)
                if latest is None:
                    raise OrderNotFoundError(f"Sell order {order_id} not found.")
                if latest.status != StarsSellOrderStatus.REFUNDED:
                    raise StatusConflictError("Failed to mark sell order refunded.")
                return latest.dto()
            return updated.dto()
