from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import timedelta
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal, InvalidOperation
from enum import StrEnum
from typing import Any, Awaitable, Optional, cast
from uuid import uuid4

from aiohttp import ClientError
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.enums.stars_order import (
    StarsOrderProductType,
    StarsOrderStatus,
    StarsPaymentProvider,
)
from app.gifts import TelegramGiftPack, get_gift_pack
from app.models.config import AppConfig
from app.models.dto.balance_topup import BalanceTopupDto
from app.models.dto.stars_order import StarsOrderDto
from app.models.sql.balance_topup import BalanceTopup
from app.models.sql.stars_order import StarsOrder
from app.models.sql.user import User
from app.services.crud.base import CrudService
from app.services.crud.stars_order_support import (
    apply_referral_rewards as apply_referral_rewards_support,
)
from app.services.crud.stars_order_support import (
    build_heleket_order_id as build_heleket_order_id_support,
)
from app.services.crud.stars_order_support import (
    build_min_payment_amount_cents as build_min_payment_amount_cents_support,
)
from app.services.crud.stars_order_support import (
    build_nice_pay_order_id as build_nice_pay_order_id_support,
)
from app.services.crud.stars_order_support import (
    build_nice_pay_provider_currencies as build_nice_pay_provider_currencies_support,
)
from app.services.crud.stars_order_support import (
    build_payment_fee_percents as build_payment_fee_percents_support,
)
from app.services.crud.stars_order_support import (
    build_payout_fee_percents as build_payout_fee_percents_support,
)
from app.services.crud.stars_order_support import (
    build_payout_fixed_cents as build_payout_fixed_cents_support,
)
from app.services.crud.stars_order_support import (
    build_platega_payload as build_platega_payload_support,
)
from app.services.crud.stars_order_support import (
    create_and_attach_invoice as create_and_attach_invoice_support,
)
from app.services.crud.stars_order_support import (
    create_balance_product_order as create_balance_product_order_support,
)
from app.services.crud.stars_order_support import (
    create_external_order as create_external_order_support,
)
from app.services.crud.stars_order_support import (
    create_gift_order as create_gift_order_support,
)
from app.services.crud.stars_order_support import (
    create_premium_order as create_premium_order_support,
)
from app.services.crud.stars_order_support import (
    create_stars_order as create_stars_order_support,
)
from app.services.crud.stars_order_support import (
    force_fulfill_order as force_fulfill_order_support,
)
from app.services.crud.stars_order_support import (
    fulfill_paid_order as fulfill_paid_order_support,
)
from app.services.crud.stars_order_support import (
    heleket_callback_url as heleket_callback_url_support,
)
from app.services.crud.stars_order_support import (
    is_order_paid as is_order_paid_support,
)
from app.services.crud.stars_order_support import (
    is_provider_configured as is_provider_configured_support,
)
from app.services.crud.stars_order_support import (
    lzt_callback_url as lzt_callback_url_support,
)
from app.services.crud.stars_order_support import (
    mark_failed_and_refund as mark_failed_and_refund_support,
)
from app.services.crud.stars_order_support import (
    nice_pay_currency as nice_pay_currency_support,
)
from app.services.crud.stars_order_support import (
    poll_pending_orders as poll_pending_orders_support,
)
from app.services.crud.stars_order_support import (
    prepare_balance_order_payload as prepare_balance_order_payload_support,
)
from app.services.crud.stars_order_support import (
    prepare_external_order_payload as prepare_external_order_payload_support,
)
from app.services.crud.stars_order_support import (
    process_crypto_webhook_invoice as process_crypto_webhook_invoice_support,
)
from app.services.crud.stars_order_support import (
    process_heleket_webhook_invoice as process_heleket_webhook_invoice_support,
)
from app.services.crud.stars_order_support import (
    process_lzt_webhook_invoice as process_lzt_webhook_invoice_support,
)
from app.services.crud.stars_order_support import (
    process_nice_pay_webhook_payment as process_nice_pay_webhook_payment_support,
)
from app.services.crud.stars_order_support import (
    process_platega_webhook_payment as process_platega_webhook_payment_support,
)
from app.services.crud.stars_order_support import (
    process_xrocket_webhook_invoice as process_xrocket_webhook_invoice_support,
)
from app.services.crud.stars_order_support import (
    provider_currency as provider_currency_support,
)
from app.services.crud.stars_order_support import (
    verify_order as verify_order_support,
)
from app.services.crud.stars_order_support import (
    xrocket_callback_url as xrocket_callback_url_support,
)
from app.services.crud.stars_order_support.constants import (
    EXTERNAL_PAYMENT_PROVIDERS,
    FULFILL_LOCK_KEY_PREFIX,
    FULFILL_LOCK_TTL_SECONDS,
    RETRYABLE_DELIVERY_ERROR_MARKERS,
)
from app.services.crypto_pay import CryptoPayService
from app.services.fragment_stars import FragmentStarsService
from app.services.heleket_pay import HeleketPayService
from app.services.lzt_pay import LZTPayService
from app.services.nice_pay import NicePayService
from app.services.platega_pay import PlategaPayService
from app.services.postgres import SQLSessionContext
from app.services.telegram_gifts import TelegramGiftService
from app.services.ton_pay import TonPayService
from app.services.xrocket_pay import XRocketPayService
from app.stars import build_crypto_payload, get_premium_pack, price_usd_for_cents
from app.utils.key_builder import build_key
from app.utils.time import datetime_now


class StarsOrderError(RuntimeError):
    pass


class ProviderUnavailableError(StarsOrderError):
    pass


class ValidationError(StarsOrderError):
    pass


class PaymentMinAmountError(ValidationError):
    def __init__(
        self,
        *,
        provider: StarsPaymentProvider,
        currency: str,
        min_amount_text: str,
    ) -> None:
        self.provider = provider
        self.currency = currency
        self.min_amount_text = min_amount_text
        super().__init__(
            f"Minimum payment amount for {provider.value}: {min_amount_text} {currency}."
        )


class InsufficientBalanceError(StarsOrderError):
    pass


class BalanceOrderInProgressError(StarsOrderError):
    pass


class PaymentCheckOutcome(StrEnum):
    NO_PENDING = "no_pending"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


@dataclass(frozen=True, slots=True)
class PaymentCheckResult:
    outcome: PaymentCheckOutcome
    order: Optional[StarsOrderDto] = None
    provider_status: Optional[str] = None


@dataclass(frozen=True, slots=True)
class UserProfileStats:
    total_stars_purchased: int
    total_premiums_purchased: int
    total_stars_amount_cents: int
    total_premiums_amount_cents: int


@dataclass(frozen=True, slots=True)
class AdminProductStats:
    count: int = 0
    amount_cents: int = 0
    stars_count: int = 0


@dataclass(frozen=True, slots=True)
class AdminOrdersStats:
    total_orders: int
    created_last_24h: int
    created_last_7d: int
    paid_last_24h: int
    paid_last_7d: int
    paid_amount_last_24h_cents: int
    paid_amount_last_7d_cents: int
    completed_amount_cents: int
    completed_stars_count: int
    status_counts: dict[StarsOrderStatus, int]
    completed_products: dict[StarsOrderProductType, AdminProductStats]


@dataclass(frozen=True, slots=True)
class CheckoutPricing:
    net_amount_cents: int
    invoice_amount_cents: int
    customer_total_cents: int
    fee_percent_text: str


logger: logging.Logger = logging.getLogger(name=__name__)
_TOPUP_ORDER_ID_OFFSET = 1_000_000_000
_UNPAID_TERMINAL_PROVIDER_STATUSES: set[str] = {
    "canceled",
    "cancelled",
    "expired",
}


class StarsOrderService(CrudService):
    def __init__(
        self,
        *,
        session_pool: async_sessionmaker[AsyncSession],
        redis: Redis,
        config: AppConfig,
        crypto_pay_service: CryptoPayService,
        heleket_pay_service: HeleketPayService,
        lzt_pay_service: LZTPayService,
        nice_pay_service: NicePayService,
        platega_pay_service: PlategaPayService,
        telegram_gift_service: TelegramGiftService,
        ton_pay_service: TonPayService,
        xrocket_pay_service: XRocketPayService,
        fragment_stars_service: FragmentStarsService,
    ) -> None:
        super().__init__(session_pool=session_pool, redis=redis, config=config)
        self.crypto_pay_service = crypto_pay_service
        self.heleket_pay_service = heleket_pay_service
        self.lzt_pay_service = lzt_pay_service
        self.nice_pay_service = nice_pay_service
        self.platega_pay_service = platega_pay_service
        self.telegram_gift_service = telegram_gift_service
        self.ton_pay_service = ton_pay_service
        self.xrocket_pay_service = xrocket_pay_service
        self.fragment_stars_service = fragment_stars_service
        self.nice_pay_provider_currencies = build_nice_pay_provider_currencies_support(
            config=config,
        )
        self.payment_fee_percents = build_payment_fee_percents_support(
            config=config,
            parse_percent=self._parse_percent,
        )
        self.payout_fee_percents = build_payout_fee_percents_support(
            config=config,
            parse_percent=self._parse_percent,
        )
        self.payout_fixed_cents = build_payout_fixed_cents_support(
            config=config,
            parse_money_cents=self._parse_money_cents,
        )
        self.min_payment_amount_cents = build_min_payment_amount_cents_support(
            config=config,
            parse_money_cents=self._parse_money_cents,
        )
        self.poll_concurrency = max(1, int(config.payments.poll_concurrency))
        self.poll_unpaid_max_age = timedelta(
            hours=max(1, int(config.payments.poll_unpaid_max_age_hours))
        )
        self.referral_level_percents: tuple[Decimal, Decimal, Decimal] = (
            self._parse_percent(config.payments.referral_level1_percent, default="2"),
            self._parse_percent(config.payments.referral_level2_percent, default="1"),
            self._parse_percent(config.payments.referral_level3_percent, default="0.5"),
        )

    @staticmethod
    def _encode_topup_order_id(*, topup_id: int) -> int:
        return _TOPUP_ORDER_ID_OFFSET + int(topup_id)

    @staticmethod
    def _decode_topup_order_id(*, order_id: int) -> int | None:
        parsed = int(order_id)
        if parsed <= _TOPUP_ORDER_ID_OFFSET:
            return None
        return parsed - _TOPUP_ORDER_ID_OFFSET

    @staticmethod
    def _is_topup_virtual_order_id(*, order_id: int) -> bool:
        return StarsOrderService._decode_topup_order_id(order_id=order_id) is not None

    @staticmethod
    def _is_unpaid_terminal_provider_status(provider_status: str) -> bool:
        return provider_status.strip().lower() in _UNPAID_TERMINAL_PROVIDER_STATUSES

    def _topup_to_order_dto(self, *, topup: BalanceTopupDto) -> StarsOrderDto:
        product_type = topup.auto_product_type or StarsOrderProductType.TOPUP
        recipient_username = (
            topup.auto_recipient_username
            if isinstance(topup.auto_recipient_username, str) and topup.auto_recipient_username
            else "balance"
        )
        fulfilled_at = topup.completed_at or topup.credited_at
        return StarsOrderDto(
            id=self._encode_topup_order_id(topup_id=topup.id),
            user_id=topup.user_id,
            recipient_username=recipient_username,
            stars_count=int(topup.auto_stars_count or 0),
            product_type=product_type,
            premium_months=topup.auto_premium_months,
            recipient_user_id=topup.auto_recipient_user_id,
            gift_id=topup.auto_gift_id,
            gift_message=topup.auto_gift_message,
            gift_sender_private=topup.auto_gift_sender_private,
            amount_cents=topup.amount_cents,
            payment_provider=topup.payment_provider,
            payment_currency=topup.payment_currency,
            status=topup.status,
            payment_payload=topup.payment_payload,
            provider_invoice_id=topup.provider_invoice_id,
            provider_reference=topup.provider_reference,
            provider_amount_minor=topup.provider_amount_minor,
            provider_status=topup.provider_status,
            checkout_url=topup.checkout_url,
            checkout_message_id=topup.checkout_message_id,
            funding_topup_id=topup.id,
            funding_provider=topup.payment_provider,
            fragment_tx_hash=None,
            fragment_error=topup.error_message,
            referral_reward_total_cents=0,
            referral_reward_level1_cents=0,
            referral_reward_level2_cents=0,
            referral_reward_level3_cents=0,
            referral_processed_at=None,
            paid_at=topup.paid_at,
            fulfilled_at=fulfilled_at,
            canceled_at=topup.canceled_at,
            failed_at=topup.failed_at,
            created_at=topup.created_at,
            updated_at=topup.updated_at,
        )

    async def get(self, order_id: int) -> Optional[StarsOrderDto]:
        topup_id = self._decode_topup_order_id(order_id=order_id)
        if topup_id is not None:
            async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
                topup = await repository.balance_topups.get(topup_id=topup_id)
                if topup is None:
                    return None
                return self._topup_to_order_dto(topup=topup.dto())

        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            order = await repository.stars_orders.get(order_id=order_id)
            if order is None:
                return None
            return order.dto()

    async def get_by_provider_payload(
        self,
        *,
        provider: StarsPaymentProvider,
        payment_payload: str,
    ) -> Optional[StarsOrderDto]:
        normalized_payload = payment_payload.strip()
        if not normalized_payload:
            return None
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            order = await repository.stars_orders.get_by_provider_payload(
                provider=provider,
                payment_payload=normalized_payload,
            )
            if order is not None:
                return order.dto()
            topup = await repository.balance_topups.get_by_provider_payload(
                provider=provider,
                payment_payload=normalized_payload,
            )
            if topup is None:
                return None
            return self._topup_to_order_dto(topup=topup.dto())

    async def list_recent(self, *, user_id: int, limit: int = 5) -> list[StarsOrderDto]:
        if limit <= 0:
            return []
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            orders = await repository.stars_orders.list_recent_by_user(
                user_id=user_id,
                limit=limit,
            )
            topups = await repository.balance_topups.list_recent_by_user(
                user_id=user_id,
                limit=limit,
                include_linked=False,
            )
        merged = [order.dto() for order in orders]
        merged.extend(self._topup_to_order_dto(topup=item.dto()) for item in topups)
        merged.sort(key=lambda item: (item.created_at, item.id), reverse=True)
        return merged[:limit]

    async def list_recent_page(
        self,
        *,
        user_id: int,
        page: int,
        page_size: int,
    ) -> tuple[list[StarsOrderDto], bool, int]:
        safe_page = max(0, page)
        safe_page_size = max(1, page_size)
        offset = safe_page * safe_page_size
        fetch_limit = offset + safe_page_size + 1
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            orders_count = await repository.stars_orders.count_by_user(user_id=user_id)
            topups_count = await repository.balance_topups.count_by_user(
                user_id=user_id,
                include_linked=False,
            )
            orders = await repository.stars_orders.list_recent_by_user_page(
                user_id=user_id,
                limit=fetch_limit,
                offset=0,
            )
            topups = await repository.balance_topups.list_recent_by_user_page(
                user_id=user_id,
                limit=fetch_limit,
                offset=0,
                include_linked=False,
            )
        merged = [order.dto() for order in orders]
        merged.extend(self._topup_to_order_dto(topup=item.dto()) for item in topups)
        merged.sort(key=lambda item: (item.created_at, item.id), reverse=True)

        total_count = orders_count + topups_count
        total_pages = max(1, (total_count + safe_page_size - 1) // safe_page_size)
        has_next = safe_page + 1 < total_pages
        page_orders = merged[offset:offset + safe_page_size]
        return page_orders, has_next, total_pages

    async def list_admin_page(
        self,
        *,
        page: int,
        page_size: int,
        user_id: int | None = None,
        status: StarsOrderStatus | None = None,
        provider: StarsPaymentProvider | None = None,
        allowed_providers: Sequence[StarsPaymentProvider] | None = None,
        product_type: StarsOrderProductType | None = None,
        search: str | None = None,
    ) -> tuple[list[StarsOrderDto], bool, int]:
        safe_page = max(0, page)
        safe_page_size = max(1, page_size)
        safe_offset = safe_page * safe_page_size
        fetch_limit = safe_offset + safe_page_size + 1
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            orders_count = await repository.stars_orders.count_for_admin(
                user_id=user_id,
                status=status,
                provider=provider,
                allowed_providers=allowed_providers,
                product_type=product_type,
                search=search,
            )
            topups_count = await repository.balance_topups.count_for_admin(
                user_id=user_id,
                status=status,
                provider=provider,
                allowed_providers=allowed_providers,
                product_type=product_type,
                search=search,
                include_linked=False,
            )
            orders = await repository.stars_orders.list_for_admin(
                limit=fetch_limit,
                offset=0,
                user_id=user_id,
                status=status,
                provider=provider,
                allowed_providers=allowed_providers,
                product_type=product_type,
                search=search,
            )
            topups = await repository.balance_topups.list_for_admin(
                limit=fetch_limit,
                offset=0,
                user_id=user_id,
                status=status,
                provider=provider,
                allowed_providers=allowed_providers,
                product_type=product_type,
                search=search,
                include_linked=False,
            )
        merged = [order.dto() for order in orders]
        merged.extend(self._topup_to_order_dto(topup=item.dto()) for item in topups)
        merged.sort(key=lambda item: (item.created_at, item.id), reverse=True)

        total_count = orders_count + topups_count
        total_pages = max(1, (total_count + safe_page_size - 1) // safe_page_size)
        has_next = safe_page + 1 < total_pages
        page_orders = merged[safe_offset:safe_offset + safe_page_size]
        return page_orders, has_next, total_pages

    async def get_user_order(self, *, user_id: int, order_id: int) -> Optional[StarsOrderDto]:
        topup_id = self._decode_topup_order_id(order_id=order_id)
        if topup_id is not None:
            async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
                topup = await repository.balance_topups.get_by_user(
                    user_id=user_id,
                    topup_id=topup_id,
                )
                if topup is None:
                    return None
                return self._topup_to_order_dto(topup=topup.dto())

        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            order = await repository.stars_orders.get_by_user(
                user_id=user_id,
                order_id=order_id,
            )
            if order is None:
                return None
            return order.dto()

    async def profile_stats(self, *, user_id: int) -> UserProfileStats:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            total_stars = await repository.stars_orders.sum_completed_stars_by_user(
                user_id=user_id
            )
            total_premiums = await repository.stars_orders.count_completed_premiums_by_user(
                user_id=user_id
            )
            total_stars_amount = await repository.stars_orders.sum_completed_stars_amount_by_user(
                user_id=user_id
            )
            total_premiums_amount = (
                await repository.stars_orders.sum_completed_premiums_amount_by_user(
                    user_id=user_id
                )
            )
        return UserProfileStats(
            total_stars_purchased=total_stars,
            total_premiums_purchased=total_premiums,
            total_stars_amount_cents=total_stars_amount,
            total_premiums_amount_cents=total_premiums_amount,
        )

    async def admin_stats(self) -> AdminOrdersStats:
        now = datetime_now()
        since_24h = now - timedelta(hours=24)
        since_7d = now - timedelta(days=7)
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            orders_total = await repository.stars_orders.count()
            topups_total = await repository.balance_topups.count_for_admin(
                include_linked=False
            )
            created_last_24h = (
                await repository.stars_orders.count_created_since(since=since_24h)
                + await repository.balance_topups.count_created_since(
                    since=since_24h,
                    include_linked=False,
                )
            )
            created_last_7d = (
                await repository.stars_orders.count_created_since(since=since_7d)
                + await repository.balance_topups.count_created_since(
                    since=since_7d,
                    include_linked=False,
                )
            )
            paid_last_24h = (
                await repository.stars_orders.count_paid_since(since=since_24h)
                + await repository.balance_topups.count_paid_since(
                    since=since_24h,
                    include_linked=False,
                )
            )
            paid_last_7d = (
                await repository.stars_orders.count_paid_since(since=since_7d)
                + await repository.balance_topups.count_paid_since(
                    since=since_7d,
                    include_linked=False,
                )
            )
            paid_amount_last_24h_cents = await repository.stars_orders.sum_paid_amount_since(
                since=since_24h
            ) + await repository.balance_topups.sum_paid_amount_since(
                since=since_24h,
                include_linked=False,
            )
            paid_amount_last_7d_cents = await repository.stars_orders.sum_paid_amount_since(
                since=since_7d
            ) + await repository.balance_topups.sum_paid_amount_since(
                since=since_7d,
                include_linked=False,
            )
            completed_amount_cents = await repository.stars_orders.sum_completed_amount()
            completed_stars_count = await repository.stars_orders.sum_completed_stars()
            status_counts_raw = await repository.stars_orders.count_by_status()
            topup_status_counts_raw = await repository.balance_topups.count_by_status(
                include_linked=False
            )
            completed_products_raw = await repository.stars_orders.completed_breakdown_by_product()
            topups_completed_count = await repository.balance_topups.count_completed(
                include_linked=False
            )
            topups_completed_amount = await repository.balance_topups.sum_completed_amount(
                include_linked=False
            )

        legacy_topup = completed_products_raw.get(StarsOrderProductType.TOPUP.value, {})
        merged_topup_count = int(legacy_topup.get("count", 0)) + int(topups_completed_count)
        merged_topup_amount = int(legacy_topup.get("amount_cents", 0)) + int(
            topups_completed_amount
        )
        completed_products_raw[StarsOrderProductType.TOPUP.value] = {
            "count": merged_topup_count,
            "amount_cents": merged_topup_amount,
            "stars_count": int(legacy_topup.get("stars_count", 0)),
        }

        status_counts = {
            status: (
                int(status_counts_raw.get(status.value, 0))
                + int(topup_status_counts_raw.get(status.value, 0))
            )
            for status in StarsOrderStatus
        }
        completed_products = {
            product: AdminProductStats(
                count=int(completed_products_raw.get(product.value, {}).get("count", 0)),
                amount_cents=int(
                    completed_products_raw.get(product.value, {}).get("amount_cents", 0)
                ),
                stars_count=int(
                    completed_products_raw.get(product.value, {}).get("stars_count", 0)
                ),
            )
            for product in StarsOrderProductType
        }
        return AdminOrdersStats(
            total_orders=orders_total + topups_total,
            created_last_24h=created_last_24h,
            created_last_7d=created_last_7d,
            paid_last_24h=paid_last_24h,
            paid_last_7d=paid_last_7d,
            paid_amount_last_24h_cents=paid_amount_last_24h_cents,
            paid_amount_last_7d_cents=paid_amount_last_7d_cents,
            completed_amount_cents=completed_amount_cents,
            completed_stars_count=completed_stars_count,
            status_counts=status_counts,
            completed_products=completed_products,
        )

    async def get_open_order(self, *, user_id: int) -> Optional[StarsOrderDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            order = await repository.stars_orders.get_open_for_user(user_id=user_id)
            topup = await repository.balance_topups.get_open_for_user(user_id=user_id)
            order_dto = order.dto() if order is not None else None
            topup_dto = self._topup_to_order_dto(topup=topup.dto()) if topup is not None else None
            if order_dto is None:
                return topup_dto
            if topup_dto is None:
                return order_dto
            if topup_dto.created_at >= order_dto.created_at:
                return topup_dto
            return order_dto

    async def set_checkout_message_id(self, *, order_id: int, message_id: int) -> None:
        topup_id = self._decode_topup_order_id(order_id=order_id)
        if topup_id is not None:
            async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
                await repository.balance_topups.update(
                    topup_id=topup_id,
                    checkout_message_id=message_id,
                )
            return
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            await repository.stars_orders.update(order_id=order_id, checkout_message_id=message_id)

    def _is_provider_configured(self, *, provider: StarsPaymentProvider) -> bool:
        return is_provider_configured_support(service=self, provider=provider)

    def _ensure_provider_configured(self, *, provider: StarsPaymentProvider) -> None:
        if not self._is_provider_configured(provider=provider):
            raise ProviderUnavailableError(f"{provider.value} payment is not configured.")

    async def create_stars_order(
        self,
        *,
        provider: StarsPaymentProvider,
        user_id: int,
        recipient_username: str,
        stars_count: int,
    ) -> StarsOrderDto:
        if provider == StarsPaymentProvider.BALANCE:
            return await create_stars_order_support(
                service=self,
                provider=provider,
                user_id=user_id,
                recipient_username=recipient_username,
                stars_count=stars_count,
                provider_unavailable_error_cls=ProviderUnavailableError,
                validation_error_cls=ValidationError,
                insufficient_balance_error_cls=InsufficientBalanceError,
                balance_in_progress_error_cls=BalanceOrderInProgressError,
                stars_order_error_cls=StarsOrderError,
            )
        if provider not in EXTERNAL_PAYMENT_PROVIDERS:
            raise ProviderUnavailableError(f"{provider.value} payment is not supported.")
        self._ensure_provider_configured(provider=provider)
        prepared = await self._prepare_external_order_payload(
            user_id=user_id,
            recipient_username=recipient_username,
            stars_count=stars_count,
            product_type=StarsOrderProductType.STARS,
            premium_months=None,
            forced_amount_cents=None,
            recipient_user_id=None,
            gift_id=None,
            gift_message=None,
            gift_sender_private=None,
            validation_error_cls=ValidationError,
        )
        return await self._create_external_topup(
            user_id=user_id,
            provider=provider,
            amount_cents=prepared.amount_cents,
            description=prepared.description,
            auto_product_type=StarsOrderProductType.STARS,
            auto_recipient_username=prepared.recipient_username,
            auto_stars_count=prepared.stars_count,
        )

    async def create_premium_order(
        self,
        *,
        provider: StarsPaymentProvider,
        user_id: int,
        recipient_username: str,
        months: int,
    ) -> StarsOrderDto:
        if provider == StarsPaymentProvider.BALANCE:
            return await create_premium_order_support(
                service=self,
                provider=provider,
                user_id=user_id,
                recipient_username=recipient_username,
                months=months,
                provider_unavailable_error_cls=ProviderUnavailableError,
                validation_error_cls=ValidationError,
                insufficient_balance_error_cls=InsufficientBalanceError,
                balance_in_progress_error_cls=BalanceOrderInProgressError,
                stars_order_error_cls=StarsOrderError,
            )
        if provider not in EXTERNAL_PAYMENT_PROVIDERS:
            raise ProviderUnavailableError(f"{provider.value} payment is not supported.")
        self._ensure_provider_configured(provider=provider)
        premium_pack = get_premium_pack(months=months)
        prepared = await self._prepare_external_order_payload(
            user_id=user_id,
            recipient_username=recipient_username,
            stars_count=0,
            product_type=StarsOrderProductType.PREMIUM,
            premium_months=premium_pack.months,
            forced_amount_cents=premium_pack.price_cents,
            recipient_user_id=None,
            gift_id=None,
            gift_message=None,
            gift_sender_private=None,
            validation_error_cls=ValidationError,
        )
        return await self._create_external_topup(
            user_id=user_id,
            provider=provider,
            amount_cents=prepared.amount_cents,
            description=prepared.description,
            auto_product_type=StarsOrderProductType.PREMIUM,
            auto_recipient_username=prepared.recipient_username,
            auto_stars_count=prepared.stars_count,
            auto_premium_months=prepared.premium_months,
        )

    async def create_gift_order(
        self,
        *,
        provider: StarsPaymentProvider,
        user_id: int,
        recipient_username: str,
        recipient_user_id: int | None,
        gift_key: str,
        gift_message: str | None,
        gift_sender_private: bool,
    ) -> StarsOrderDto:
        if provider == StarsPaymentProvider.BALANCE:
            return await create_gift_order_support(
                service=self,
                provider=provider,
                user_id=user_id,
                recipient_username=recipient_username,
                recipient_user_id=recipient_user_id,
                gift_key=gift_key,
                gift_message=gift_message,
                gift_sender_private=gift_sender_private,
                provider_unavailable_error_cls=ProviderUnavailableError,
                validation_error_cls=ValidationError,
                insufficient_balance_error_cls=InsufficientBalanceError,
                balance_in_progress_error_cls=BalanceOrderInProgressError,
                stars_order_error_cls=StarsOrderError,
            )
        if provider not in EXTERNAL_PAYMENT_PROVIDERS:
            raise ProviderUnavailableError(f"{provider.value} payment is not supported.")
        self._ensure_provider_configured(provider=provider)
        gift = self._resolve_gift_pack(gift_key=gift_key)
        normalized_message = self._normalize_gift_message(gift_message)
        prepared = await self._prepare_external_order_payload(
            user_id=user_id,
            recipient_username=recipient_username,
            stars_count=0,
            product_type=StarsOrderProductType.GIFT,
            premium_months=None,
            forced_amount_cents=gift.price_cents,
            recipient_user_id=recipient_user_id,
            gift_id=gift.gift_id,
            gift_message=normalized_message,
            gift_sender_private=gift_sender_private,
            validation_error_cls=ValidationError,
        )
        return await self._create_external_topup(
            user_id=user_id,
            provider=provider,
            amount_cents=prepared.amount_cents,
            description=prepared.description,
            auto_product_type=StarsOrderProductType.GIFT,
            auto_recipient_username=prepared.recipient_username,
            auto_stars_count=prepared.stars_count,
            auto_recipient_user_id=prepared.recipient_user_id,
            auto_gift_id=prepared.gift_id,
            auto_gift_message=prepared.gift_message,
            auto_gift_sender_private=prepared.gift_sender_private,
        )

    async def create_topup_order(
        self,
        *,
        provider: StarsPaymentProvider,
        user_id: int,
        amount_cents: int,
    ) -> StarsOrderDto:
        if provider == StarsPaymentProvider.BALANCE:
            raise ProviderUnavailableError("Balance provider is not supported for top-up orders.")
        if provider not in EXTERNAL_PAYMENT_PROVIDERS:
            raise ProviderUnavailableError(f"{provider.value} payment is not supported.")
        self._ensure_provider_configured(provider=provider)
        prepared = await self._prepare_external_order_payload(
            user_id=user_id,
            recipient_username="balance",
            stars_count=0,
            product_type=StarsOrderProductType.TOPUP,
            premium_months=None,
            forced_amount_cents=amount_cents,
            recipient_user_id=None,
            gift_id=None,
            gift_message=None,
            gift_sender_private=None,
            validation_error_cls=ValidationError,
        )
        return await self._create_external_topup(
            user_id=user_id,
            provider=provider,
            amount_cents=prepared.amount_cents,
            description=prepared.description,
        )

    async def _create_balance_product_order(  # noqa: C901
        self,
        *,
        user_id: int,
        recipient_username: str,
        stars_count: int,
        amount_cents: int,
        product_type: StarsOrderProductType,
        premium_months: int | None = None,
        recipient_user_id: int | None = None,
        gift_id: str | None = None,
        gift_message: str | None = None,
        gift_sender_private: bool | None = None,
    ) -> StarsOrderDto:
        return await create_balance_product_order_support(
            service=self,
            user_id=user_id,
            recipient_username=recipient_username,
            stars_count=stars_count,
            amount_cents=amount_cents,
            product_type=product_type,
            premium_months=premium_months,
            recipient_user_id=recipient_user_id,
            gift_id=gift_id,
            gift_message=gift_message,
            gift_sender_private=gift_sender_private,
            validation_error_cls=ValidationError,
            insufficient_balance_error_cls=InsufficientBalanceError,
            balance_in_progress_error_cls=BalanceOrderInProgressError,
        )

    async def _create_external_order(  # noqa: C901
        self,
        *,
        user_id: int,
        recipient_username: str,
        stars_count: int,
        provider: StarsPaymentProvider,
        product_type: StarsOrderProductType,
        premium_months: int | None = None,
        forced_amount_cents: int | None = None,
        recipient_user_id: int | None = None,
        gift_id: str | None = None,
        gift_message: str | None = None,
        gift_sender_private: bool | None = None,
    ) -> StarsOrderDto:
        return await create_external_order_support(
            service=self,
            user_id=user_id,
            recipient_username=recipient_username,
            stars_count=stars_count,
            provider=provider,
            product_type=product_type,
            premium_months=premium_months,
            forced_amount_cents=forced_amount_cents,
            recipient_user_id=recipient_user_id,
            gift_id=gift_id,
            gift_message=gift_message,
            gift_sender_private=gift_sender_private,
            validation_error_cls=ValidationError,
            provider_unavailable_error_cls=ProviderUnavailableError,
            stars_order_error_cls=StarsOrderError,
        )

    async def _create_topup_record(
        self,
        *,
        user_id: int,
        amount_cents: int,
        payment_provider: StarsPaymentProvider,
        payment_currency: str,
        status: StarsOrderStatus,
        auto_product_type: StarsOrderProductType | None = None,
        auto_recipient_username: str | None = None,
        auto_stars_count: int = 0,
        auto_premium_months: int | None = None,
        auto_recipient_user_id: int | None = None,
        auto_gift_id: str | None = None,
        auto_gift_message: str | None = None,
        auto_gift_sender_private: bool | None = None,
    ) -> BalanceTopupDto:
        topup = BalanceTopup(
            user_id=user_id,
            amount_cents=amount_cents,
            payment_provider=payment_provider.value,
            payment_currency=payment_currency,
            status=status.value,
            auto_product_type=auto_product_type.value if auto_product_type is not None else None,
            auto_recipient_username=auto_recipient_username,
            auto_stars_count=auto_stars_count,
            auto_premium_months=auto_premium_months,
            auto_recipient_user_id=auto_recipient_user_id,
            auto_gift_id=auto_gift_id,
            auto_gift_message=auto_gift_message,
            auto_gift_sender_private=auto_gift_sender_private,
        )
        async with SQLSessionContext(session_pool=self.session_pool) as (_repository, uow):
            await uow.commit(topup)
        return topup.dto()

    async def _update_topup(self, *, topup_id: int, **data: Any) -> BalanceTopupDto | None:
        serialized = {
            key: value.value if isinstance(value, StrEnum) else value
            for key, value in data.items()
        }
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            updated = await repository.balance_topups.update(topup_id=topup_id, **serialized)
            if updated is None:
                return None
            return updated.dto()

    async def _transition_topup_status(
        self,
        *,
        topup_id: int,
        from_statuses: list[StarsOrderStatus],
        to_status: StarsOrderStatus,
        **data: Any,
    ) -> BalanceTopupDto | None:
        serialized = {
            key: value.value if isinstance(value, StrEnum) else value
            for key, value in data.items()
        }
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            updated = await repository.balance_topups.update_if_status(
                topup_id=topup_id,
                current_statuses=from_statuses,
                status=to_status.value,
                **serialized,
            )
            if updated is None:
                return None
            return updated.dto()

    async def _create_and_attach_topup_invoice(
        self,
        *,
        topup: BalanceTopupDto,
        provider: StarsPaymentProvider,
        user_id: int,
        checkout_pricing: CheckoutPricing,
        checkout_amount_usd: str,
        description: str,
    ) -> BalanceTopupDto | None:
        virtual_order_id = self._encode_topup_order_id(topup_id=topup.id)
        if provider == StarsPaymentProvider.CRYPTO_BOT:
            payload = build_crypto_payload(order_id=virtual_order_id, user_id=user_id)
            crypto_invoice = await self.crypto_pay_service.create_invoice(
                amount=checkout_amount_usd,
                description=description,
                invoice_payload=payload,
            )
            return await self._update_topup(
                topup_id=topup.id,
                status=StarsOrderStatus.PENDING_PAYMENT,
                payment_payload=payload,
                provider_invoice_id=crypto_invoice.invoice_id,
                checkout_url=crypto_invoice.pay_url,
                provider_status="pending",
            )
        if provider == StarsPaymentProvider.TON_PAY:
            payment_token = f"ton-topup-{virtual_order_id}-{uuid4().hex[:12]}"
            ton_invoice = await self.ton_pay_service.create_invoice(
                order_id=virtual_order_id,
                payment_token=payment_token,
                amount_usd=checkout_amount_usd,
            )
            return await self._update_topup(
                topup_id=topup.id,
                status=StarsOrderStatus.PENDING_PAYMENT,
                payment_payload=ton_invoice.payment_token,
                provider_reference=ton_invoice.invoice_id,
                provider_amount_minor=ton_invoice.expected_amount_nano,
                checkout_url=ton_invoice.pay_url,
                provider_status=ton_invoice.status,
            )
        if provider == StarsPaymentProvider.LZT_PAY:
            payment_id = f"topup-{virtual_order_id}"
            callback_url = self._lzt_callback_url()
            lzt_invoice = await self.lzt_pay_service.create_invoice(
                amount=checkout_amount_usd,
                description=description,
                payment_id=payment_id,
                callback_url=callback_url,
            )
            return await self._update_topup(
                topup_id=topup.id,
                status=StarsOrderStatus.PENDING_PAYMENT,
                payment_payload=lzt_invoice.payment_id,
                provider_invoice_id=lzt_invoice.invoice_id,
                checkout_url=lzt_invoice.pay_url,
                provider_status=lzt_invoice.status,
            )
        if provider == StarsPaymentProvider.HELEKET_PAY:
            heleket_order_id = self._build_heleket_order_id(local_order_id=virtual_order_id)
            heleket_invoice = await self.heleket_pay_service.create_invoice(
                amount=checkout_amount_usd,
                order_id=heleket_order_id,
                description=description,
                callback_url=self._heleket_callback_url(),
            )
            return await self._update_topup(
                topup_id=topup.id,
                status=StarsOrderStatus.PENDING_PAYMENT,
                payment_payload=heleket_invoice.invoice_uuid,
                provider_reference=heleket_invoice.order_id,
                checkout_url=heleket_invoice.pay_url,
                provider_status=heleket_invoice.status,
            )
        if provider == StarsPaymentProvider.PLATEGA_PAY:
            platega_payload = self._build_platega_payload(local_order_id=virtual_order_id)
            platega_invoice = await self.platega_pay_service.create_invoice(
                amount_usd=checkout_amount_usd,
                payment_payload=platega_payload,
                description=description,
            )
            return await self._update_topup(
                topup_id=topup.id,
                status=StarsOrderStatus.PENDING_PAYMENT,
                payment_payload=platega_invoice.payment_payload,
                provider_reference=platega_invoice.transaction_id,
                provider_amount_minor=platega_invoice.amount_minor,
                checkout_url=platega_invoice.pay_url,
                provider_status=platega_invoice.status,
            )
        if provider in {
            StarsPaymentProvider.NICE_PAY_RU,
            StarsPaymentProvider.NICE_PAY_KZ,
        }:
            nice_order_id = self._build_nice_pay_order_id(
                provider=provider,
                local_order_id=virtual_order_id,
            )
            nice_currency = self._nice_pay_currency(provider=provider)
            nice_amount_minor = await self.nice_pay_service.invoice_amount_minor_from_usd_cents(
                usd_cents=checkout_pricing.invoice_amount_cents,
                currency=nice_currency,
            )
            nice_invoice = await self.nice_pay_service.create_invoice(
                amount_minor=nice_amount_minor,
                order_id=nice_order_id,
                customer=f"user_{user_id}",
                description=description,
                currency=nice_currency,
            )
            return await self._update_topup(
                topup_id=topup.id,
                status=StarsOrderStatus.PENDING_PAYMENT,
                payment_payload=nice_invoice.payment_id,
                provider_reference=nice_invoice.order_id,
                provider_amount_minor=nice_invoice.amount_minor,
                checkout_url=nice_invoice.pay_url,
                provider_status=nice_invoice.status,
            )
        if provider == StarsPaymentProvider.XROCKET_PAY:
            payment_payload = f"topup-{virtual_order_id}"
            xrocket_invoice = await self.xrocket_pay_service.create_invoice(
                amount=checkout_amount_usd,
                description=description,
                payment_payload=payment_payload,
                callback_url=self._xrocket_callback_url(),
            )
            return await self._update_topup(
                topup_id=topup.id,
                status=StarsOrderStatus.PENDING_PAYMENT,
                payment_payload=xrocket_invoice.payment_payload,
                provider_reference=xrocket_invoice.invoice_id,
                checkout_url=xrocket_invoice.pay_url,
                provider_status=xrocket_invoice.status,
            )
        raise ValidationError("Unsupported payment provider.")

    async def _create_external_topup(
        self,
        *,
        user_id: int,
        provider: StarsPaymentProvider,
        amount_cents: int,
        description: str,
        auto_product_type: StarsOrderProductType | None = None,
        auto_recipient_username: str | None = None,
        auto_stars_count: int = 0,
        auto_premium_months: int | None = None,
        auto_recipient_user_id: int | None = None,
        auto_gift_id: str | None = None,
        auto_gift_message: str | None = None,
        auto_gift_sender_private: bool | None = None,
    ) -> StarsOrderDto:
        self._validate_provider_min_payment_amount(
            provider=provider,
            amount_cents=amount_cents,
        )
        checkout_pricing = self._build_checkout_pricing(
            provider=provider,
            net_amount_cents=amount_cents,
        )
        checkout_amount_usd = price_usd_for_cents(checkout_pricing.invoice_amount_cents)

        created = await self._create_topup_record(
            user_id=user_id,
            amount_cents=amount_cents,
            payment_provider=provider,
            payment_currency=self._provider_currency(provider=provider),
            status=StarsOrderStatus.CREATING_PAYMENT,
            auto_product_type=auto_product_type,
            auto_recipient_username=auto_recipient_username,
            auto_stars_count=auto_stars_count,
            auto_premium_months=auto_premium_months,
            auto_recipient_user_id=auto_recipient_user_id,
            auto_gift_id=auto_gift_id,
            auto_gift_message=auto_gift_message,
            auto_gift_sender_private=auto_gift_sender_private,
        )

        try:
            updated = await self._create_and_attach_topup_invoice(
                topup=created,
                provider=provider,
                user_id=user_id,
                checkout_pricing=checkout_pricing,
                checkout_amount_usd=checkout_amount_usd,
                description=description,
            )
        except Exception as error:
            error_text = str(error).strip() or error.__class__.__name__
            await self._update_topup(
                topup_id=created.id,
                status=StarsOrderStatus.FAILED,
                failed_at=datetime_now(),
                error_message=error_text,
            )
            if isinstance(error, ValidationError):
                raise
            if isinstance(error, (asyncio.TimeoutError, TimeoutError, ClientError)):
                raise ProviderUnavailableError("Payment provider is unavailable.") from error
            raise StarsOrderError("Failed to create payment invoice.") from error

        if updated is None:
            raise StarsOrderError("Failed to persist top-up invoice.")
        return self._topup_to_order_dto(topup=updated)

    async def _prepare_balance_order_payload(
        self,
        *,
        recipient_username: str,
        product_type: StarsOrderProductType,
        recipient_user_id: int | None,
        gift_id: str | None,
        gift_message: str | None,
        gift_sender_private: bool | None,
        validation_error_cls: type[Exception],
    ) -> Any:
        return await prepare_balance_order_payload_support(
            service=self,
            recipient_username=recipient_username,
            product_type=product_type,
            recipient_user_id=recipient_user_id,
            gift_id=gift_id,
            gift_message=gift_message,
            gift_sender_private=gift_sender_private,
            validation_error_cls=validation_error_cls,
        )

    async def _prepare_external_order_payload(
        self,
        *,
        user_id: int,
        recipient_username: str,
        stars_count: int,
        product_type: StarsOrderProductType,
        premium_months: int | None,
        forced_amount_cents: int | None,
        recipient_user_id: int | None,
        gift_id: str | None,
        gift_message: str | None,
        gift_sender_private: bool | None,
        validation_error_cls: type[Exception],
    ) -> Any:
        return await prepare_external_order_payload_support(
            service=self,
            user_id=user_id,
            recipient_username=recipient_username,
            stars_count=stars_count,
            product_type=product_type,
            premium_months=premium_months,
            forced_amount_cents=forced_amount_cents,
            recipient_user_id=recipient_user_id,
            gift_id=gift_id,
            gift_message=gift_message,
            gift_sender_private=gift_sender_private,
            validation_error_cls=validation_error_cls,
        )

    async def _create_and_attach_invoice(
        self,
        *,
        order: StarsOrderDto,
        provider: StarsPaymentProvider,
        user_id: int,
        checkout_pricing: CheckoutPricing,
        checkout_amount_usd: str,
        description: str,
    ) -> StarsOrderDto | None:
        return await create_and_attach_invoice_support(
            service=self,
            order=order,
            provider=provider,
            user_id=user_id,
            checkout_pricing=checkout_pricing,
            checkout_amount_usd=checkout_amount_usd,
            description=description,
            validation_error_cls=ValidationError,
        )

    async def _get_topup(self, *, topup_id: int) -> BalanceTopupDto | None:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            topup = await repository.balance_topups.get(topup_id=topup_id)
            if topup is None:
                return None
            return topup.dto()

    async def _is_topup_paid(self, *, topup: BalanceTopupDto) -> tuple[bool, str]:
        topup_order = self._topup_to_order_dto(topup=topup)
        return await self._is_order_paid(order=topup_order)

    async def _fulfill_paid_topup(self, *, topup_id: int) -> StarsOrderDto:  # noqa: C901
        encoded_topup_order_id = self._encode_topup_order_id(topup_id=topup_id)
        lock_token = await self._acquire_fulfill_lock(order_id=encoded_topup_order_id)
        if lock_token is None:
            latest = await self._get_topup(topup_id=topup_id)
            if latest is None:
                raise StarsOrderError("Top-up not found during fulfillment.")
            return self._topup_to_order_dto(topup=latest)
        try:
            topup = await self._get_topup(topup_id=topup_id)
            if topup is None:
                raise StarsOrderError("Top-up not found during fulfillment.")
            if topup.status in {
                StarsOrderStatus.COMPLETED,
                StarsOrderStatus.FAILED,
                StarsOrderStatus.CANCELED,
            }:
                return self._topup_to_order_dto(topup=topup)

            if topup.status == StarsOrderStatus.PAYMENT_CONFIRMED:
                transitioned = await self._transition_topup_status(
                    topup_id=topup.id,
                    from_statuses=[StarsOrderStatus.PAYMENT_CONFIRMED],
                    to_status=StarsOrderStatus.FULFILLING,
                )
                if transitioned is not None:
                    topup = transitioned

            if topup.status != StarsOrderStatus.FULFILLING:
                return self._topup_to_order_dto(topup=topup)

            linked_order_id: int | None = None
            return_after_locked_tx = False

            async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
                session = repository.session
                current = await session.scalar(
                    select(BalanceTopup).where(BalanceTopup.id == topup.id).with_for_update()
                )
                if current is None:
                    raise StarsOrderError("Top-up not found during fulfillment.")
                if current.status in {
                    StarsOrderStatus.COMPLETED.value,
                    StarsOrderStatus.CANCELED.value,
                    StarsOrderStatus.FAILED.value,
                }:
                    return_after_locked_tx = True
                else:
                    user = await session.scalar(
                        select(User).where(User.id == current.user_id).with_for_update()
                    )
                    if user is None:
                        current.status = StarsOrderStatus.FAILED
                        current.failed_at = datetime_now()
                        current.error_message = "Top-up user not found."
                        await session.commit()
                        return_after_locked_tx = True
                    else:
                        if int(current.amount_cents) > 0:
                            user.balance_cents = (
                                int(user.balance_cents) + int(current.amount_cents)
                            )
                        current.credited_at = current.credited_at or datetime_now()

                        linked_order: StarsOrder | None = None
                        if current.auto_product_type is not None:
                            product_type = StarsOrderProductType(str(current.auto_product_type))
                            amount_cents = int(current.amount_cents)
                            if int(user.balance_cents) < amount_cents:
                                current.status = StarsOrderStatus.FAILED
                                current.failed_at = datetime_now()
                                current.error_message = "Insufficient balance after top-up credit."
                                await session.commit()
                                return_after_locked_tx = True
                            else:
                                user.balance_cents = int(user.balance_cents) - amount_cents
                                linked_order = StarsOrder(
                                    user_id=int(current.user_id),
                                    recipient_username=(
                                        current.auto_recipient_username
                                        if current.auto_recipient_username
                                        else "balance"
                                    ),
                                    stars_count=int(current.auto_stars_count or 0),
                                    product_type=product_type.value,
                                    premium_months=current.auto_premium_months,
                                    recipient_user_id=current.auto_recipient_user_id,
                                    gift_id=current.auto_gift_id,
                                    gift_message=current.auto_gift_message,
                                    gift_sender_private=current.auto_gift_sender_private,
                                    amount_cents=amount_cents,
                                    payment_provider=current.payment_provider,
                                    payment_currency=current.payment_currency,
                                    status=StarsOrderStatus.PAYMENT_CONFIRMED.value,
                                    provider_status="paid_via_balance_topup",
                                    paid_at=datetime_now(),
                                    funding_topup_id=current.id,
                                    funding_provider=current.payment_provider,
                                )
                                session.add(linked_order)
                                await session.flush()
                                current.linked_order_id = linked_order.id
                                linked_order_id = int(linked_order.id)
                        if not return_after_locked_tx:
                            current.status = StarsOrderStatus.COMPLETED
                            current.completed_at = datetime_now()
                            current.error_message = None
                            await session.commit()

            topup_dto = await self._get_topup(topup_id=topup.id)
            if topup_dto is None:
                raise StarsOrderError("Top-up disappeared after fulfillment transaction.")
            if return_after_locked_tx:
                return self._topup_to_order_dto(topup=topup_dto)

            await self._clear_user_cache(user_id=topup.user_id)

            if linked_order_id is not None:
                try:
                    await self._fulfill_paid_order(order_id=linked_order_id)
                except Exception as error:
                    error_text = str(error).strip() or "Auto purchase fulfillment failed."
                    failed = await self._update_topup(
                        topup_id=topup_dto.id,
                        status=StarsOrderStatus.FAILED,
                        failed_at=datetime_now(),
                        error_message=error_text,
                    )
                    if failed is not None:
                        return self._topup_to_order_dto(topup=failed)
            refreshed = await self._get_topup(topup_id=topup_id)
            if refreshed is None:
                raise StarsOrderError("Top-up disappeared after fulfillment.")
            return self._topup_to_order_dto(topup=refreshed)
        finally:
            await self._release_fulfill_lock(
                order_id=encoded_topup_order_id,
                lock_token=lock_token,
            )

    async def _verify_topup(self, *, order_id: int) -> PaymentCheckResult:  # noqa: C901
        topup_id = self._decode_topup_order_id(order_id=order_id)
        if topup_id is None:
            return PaymentCheckResult(outcome=PaymentCheckOutcome.NO_PENDING)
        topup = await self._get_topup(topup_id=topup_id)
        if topup is None:
            return PaymentCheckResult(outcome=PaymentCheckOutcome.NO_PENDING)

        if topup.status == StarsOrderStatus.CANCELED:
            return PaymentCheckResult(
                outcome=PaymentCheckOutcome.CANCELED,
                order=self._topup_to_order_dto(topup=topup),
            )
        if topup.status == StarsOrderStatus.COMPLETED:
            return PaymentCheckResult(
                outcome=PaymentCheckOutcome.COMPLETED,
                order=self._topup_to_order_dto(topup=topup),
            )
        if topup.status == StarsOrderStatus.FAILED:
            return PaymentCheckResult(
                outcome=PaymentCheckOutcome.FAILED,
                order=self._topup_to_order_dto(topup=topup),
            )

        if topup.status in {StarsOrderStatus.CREATING_PAYMENT, StarsOrderStatus.PENDING_PAYMENT}:
            is_paid, provider_status = await self._is_topup_paid(topup=topup)
            topup = (
                await self._update_topup(
                    topup_id=topup.id,
                    provider_status=provider_status,
                )
                or topup
            )
            if not is_paid:
                if self._is_unpaid_terminal_provider_status(provider_status):
                    canceled = await self._transition_topup_status(
                        topup_id=topup.id,
                        from_statuses=[
                            StarsOrderStatus.CREATING_PAYMENT,
                            StarsOrderStatus.PENDING_PAYMENT,
                        ],
                        to_status=StarsOrderStatus.CANCELED,
                        provider_status=provider_status,
                        canceled_at=datetime_now(),
                    )
                    return PaymentCheckResult(
                        outcome=PaymentCheckOutcome.CANCELED,
                        order=self._topup_to_order_dto(topup=canceled or topup),
                        provider_status=provider_status,
                    )
                return PaymentCheckResult(
                    outcome=PaymentCheckOutcome.PENDING,
                    order=self._topup_to_order_dto(topup=topup),
                    provider_status=provider_status,
                )
            transitioned = await self._transition_topup_status(
                topup_id=topup.id,
                from_statuses=[
                    StarsOrderStatus.CREATING_PAYMENT,
                    StarsOrderStatus.PENDING_PAYMENT,
                ],
                to_status=StarsOrderStatus.PAYMENT_CONFIRMED,
                provider_status=provider_status,
                paid_at=datetime_now(),
            )
            if transitioned is not None:
                topup = transitioned

        if topup.status in {StarsOrderStatus.PAYMENT_CONFIRMED, StarsOrderStatus.FULFILLING}:
            fulfilled = await self._fulfill_paid_topup(topup_id=topup.id)
            if fulfilled.status == StarsOrderStatus.COMPLETED:
                return PaymentCheckResult(outcome=PaymentCheckOutcome.COMPLETED, order=fulfilled)
            if fulfilled.status == StarsOrderStatus.FAILED:
                return PaymentCheckResult(outcome=PaymentCheckOutcome.FAILED, order=fulfilled)
            if fulfilled.status == StarsOrderStatus.CANCELED:
                return PaymentCheckResult(outcome=PaymentCheckOutcome.CANCELED, order=fulfilled)
            return PaymentCheckResult(outcome=PaymentCheckOutcome.PROCESSING, order=fulfilled)

        return PaymentCheckResult(
            outcome=PaymentCheckOutcome.PROCESSING,
            order=self._topup_to_order_dto(topup=topup),
        )

    async def cancel_open_order(self, *, user_id: int) -> Optional[StarsOrderDto]:
        open_order = await self.get_open_order(user_id=user_id)
        if open_order is None:
            return None
        if open_order.status not in {
            StarsOrderStatus.CREATING_PAYMENT,
            StarsOrderStatus.PENDING_PAYMENT,
        }:
            return open_order
        topup_id = self._decode_topup_order_id(order_id=open_order.id)
        if topup_id is not None:
            canceled_topup = await self._transition_topup_status(
                topup_id=topup_id,
                from_statuses=[
                    StarsOrderStatus.CREATING_PAYMENT,
                    StarsOrderStatus.PENDING_PAYMENT,
                ],
                to_status=StarsOrderStatus.CANCELED,
                canceled_at=datetime_now(),
            )
            if canceled_topup is not None:
                return self._topup_to_order_dto(topup=canceled_topup)
            latest_topup = await self._get_topup(topup_id=topup_id)
            if latest_topup is None:
                return None
            return self._topup_to_order_dto(topup=latest_topup)
        return await self._update_order(
            order_id=open_order.id,
            status=StarsOrderStatus.CANCELED,
            canceled_at=datetime_now(),
        )

    async def cancel_order(self, *, user_id: int, order_id: int) -> Optional[StarsOrderDto]:
        topup_id = self._decode_topup_order_id(order_id=order_id)
        if topup_id is not None:
            topup = await self._get_topup(topup_id=topup_id)
            if topup is None or topup.user_id != user_id:
                return None
            if topup.status not in {
                StarsOrderStatus.CREATING_PAYMENT,
                StarsOrderStatus.PENDING_PAYMENT,
            }:
                return self._topup_to_order_dto(topup=topup)
            canceled = await self._transition_topup_status(
                topup_id=topup.id,
                from_statuses=[
                    StarsOrderStatus.CREATING_PAYMENT,
                    StarsOrderStatus.PENDING_PAYMENT,
                ],
                to_status=StarsOrderStatus.CANCELED,
                canceled_at=datetime_now(),
            )
            if canceled is not None:
                return self._topup_to_order_dto(topup=canceled)
            latest = await self._get_topup(topup_id=topup.id)
            if latest is None or latest.user_id != user_id:
                return None
            return self._topup_to_order_dto(topup=latest)

        order = await self.get(order_id=order_id)
        if order is None or order.user_id != user_id:
            return None
        if order.status not in {
            StarsOrderStatus.CREATING_PAYMENT,
            StarsOrderStatus.PENDING_PAYMENT,
        }:
            return order

        canceled = await self._transition_order_status(
            order_id=order.id,
            from_statuses=[
                StarsOrderStatus.CREATING_PAYMENT,
                StarsOrderStatus.PENDING_PAYMENT,
            ],
            to_status=StarsOrderStatus.CANCELED,
            canceled_at=datetime_now(),
        )
        if canceled is not None:
            return canceled

        latest = await self.get(order_id=order.id)
        if latest is None or latest.user_id != user_id:
            return None
        return latest

    async def verify_open_order(self, *, user_id: int) -> PaymentCheckResult:
        open_order = await self.get_open_order(user_id=user_id)
        if open_order is None:
            return PaymentCheckResult(outcome=PaymentCheckOutcome.NO_PENDING)
        return await self.verify_order(order_id=open_order.id)

    async def retry_fulfill_order(self, *, order_id: int) -> PaymentCheckResult:
        return await self.verify_order(order_id=order_id)

    async def force_fulfill_order(self, *, order_id: int) -> PaymentCheckResult:
        if self._is_topup_virtual_order_id(order_id=order_id):
            return await self._verify_topup(order_id=order_id)
        return await force_fulfill_order_support(
            service=self,
            order_id=order_id,
            outcome_enum=PaymentCheckOutcome,
            result_cls=PaymentCheckResult,
        )

    async def verify_order(self, *, order_id: int) -> PaymentCheckResult:
        if self._is_topup_virtual_order_id(order_id=order_id):
            return await self._verify_topup(order_id=order_id)
        return await verify_order_support(
            service=self,
            order_id=order_id,
            outcome_enum=PaymentCheckOutcome,
            result_cls=PaymentCheckResult,
        )

    async def _find_topup_for_webhook(
        self,
        *,
        providers: Sequence[StarsPaymentProvider],
        provider_invoice_id: int | None = None,
        payment_payload: str | None = None,
        provider_reference: str | None = None,
    ) -> BalanceTopupDto | None:
        normalized_payload = (payment_payload or "").strip()
        normalized_reference = (provider_reference or "").strip()
        normalized_invoice = (
            int(provider_invoice_id)
            if provider_invoice_id is not None and provider_invoice_id > 0
            else None
        )
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            if normalized_invoice is not None:
                for provider in providers:
                    found = await repository.balance_topups.get_by_provider_invoice(
                        provider=provider,
                        provider_invoice_id=normalized_invoice,
                    )
                    if found is not None:
                        return found.dto()
            if normalized_payload:
                for provider in providers:
                    found = await repository.balance_topups.get_by_provider_payload(
                        provider=provider,
                        payment_payload=normalized_payload,
                    )
                    if found is not None:
                        return found.dto()
            if normalized_reference:
                for provider in providers:
                    found = await repository.balance_topups.get_by_provider_reference(
                        provider=provider,
                        provider_reference=normalized_reference,
                    )
                    if found is not None:
                        return found.dto()
        return None

    async def _process_topup_webhook(
        self,
        *,
        topup: BalanceTopupDto,
        provider_status: str | None = None,
        provider_invoice_id: int | None = None,
        payment_payload: str | None = None,
        provider_reference: str | None = None,
    ) -> StarsOrderDto:
        normalized_status = (provider_status or "").strip().lower() or None
        normalized_payload = (payment_payload or "").strip() or None
        normalized_reference = (provider_reference or "").strip() or None
        normalized_invoice = (
            int(provider_invoice_id)
            if provider_invoice_id is not None and provider_invoice_id > 0
            else None
        )

        update_data: dict[str, Any] = {}
        if normalized_status is not None:
            update_data["provider_status"] = normalized_status
        if normalized_invoice is not None:
            update_data["provider_invoice_id"] = normalized_invoice
        if normalized_payload is not None:
            update_data["payment_payload"] = normalized_payload
        if normalized_reference is not None:
            update_data["provider_reference"] = normalized_reference

        updated_topup = (
            await self._update_topup(topup_id=topup.id, **update_data)
            if update_data
            else topup
        )
        if updated_topup is None:
            refreshed = await self._get_topup(topup_id=topup.id)
            if refreshed is None:
                raise StarsOrderError("Top-up disappeared during webhook processing.")
            updated_topup = refreshed
        if updated_topup.status in {
            StarsOrderStatus.COMPLETED,
            StarsOrderStatus.FAILED,
            StarsOrderStatus.CANCELED,
        }:
            return self._topup_to_order_dto(topup=updated_topup)

        result = await self.verify_order(
            order_id=self._encode_topup_order_id(topup_id=updated_topup.id)
        )
        if result.order is not None:
            return result.order
        latest = await self._get_topup(topup_id=updated_topup.id)
        if latest is None:
            raise StarsOrderError("Top-up disappeared after webhook verification.")
        return self._topup_to_order_dto(topup=latest)

    async def process_ton_invoice_webhook_payment(
        self,
        *,
        invoice_id: str | None = None,
        webhook_status: str | None = None,
    ) -> Optional[StarsOrderDto]:
        normalized_invoice_id = (invoice_id or "").strip()
        if not normalized_invoice_id:
            return None

        normalized_status = (webhook_status or "").strip().lower() or None
        self.ton_pay_service.clear_invoice_status_cache(invoice_id=normalized_invoice_id)

        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            order_raw = await repository.stars_orders.get_by_provider_reference(
                provider=StarsPaymentProvider.TON_PAY,
                provider_reference=normalized_invoice_id,
            )
        if order_raw is not None:
            order = order_raw.dto()
            if normalized_status is not None and order.provider_status != normalized_status:
                order = (
                    await self._update_order(
                        order_id=order.id,
                        provider_status=normalized_status,
                    )
                    or order
                )
            if normalized_status != "paid" or order.status in {
                StarsOrderStatus.COMPLETED,
                StarsOrderStatus.FAILED,
                StarsOrderStatus.CANCELED,
            }:
                return order
            result = await self.verify_order(order_id=order.id)
            if result.order is not None:
                return result.order
            return await self.get(order_id=order.id)

        topup = await self._find_topup_for_webhook(
            providers=[StarsPaymentProvider.TON_PAY],
            provider_reference=normalized_invoice_id,
        )
        if topup is None:
            return None
        if normalized_status != "paid" and normalized_status is not None:
            updated = await self._update_topup(
                topup_id=topup.id,
                provider_status=normalized_status,
            )
            return self._topup_to_order_dto(topup=updated or topup)
        return await self._process_topup_webhook(
            topup=topup,
            provider_status=normalized_status,
            provider_reference=normalized_invoice_id,
        )

    async def process_crypto_webhook_invoice(self, *, invoice_id: int) -> Optional[StarsOrderDto]:
        order = await process_crypto_webhook_invoice_support(
            service=self,
            invoice_id=invoice_id,
        )
        if order is not None:
            return order
        topup = await self._find_topup_for_webhook(
            providers=[StarsPaymentProvider.CRYPTO_BOT],
            provider_invoice_id=invoice_id,
        )
        if topup is None:
            return None
        return await self._process_topup_webhook(
            topup=topup,
            provider_status="paid",
            provider_invoice_id=invoice_id,
        )

    async def process_lzt_webhook_invoice(
        self,
        *,
        invoice_id: int | None = None,
        payment_id: str | None = None,
    ) -> Optional[StarsOrderDto]:
        order = await process_lzt_webhook_invoice_support(
            service=self,
            invoice_id=invoice_id,
            payment_id=payment_id,
        )
        if order is not None:
            return order
        topup = await self._find_topup_for_webhook(
            providers=[StarsPaymentProvider.LZT_PAY],
            provider_invoice_id=invoice_id,
            payment_payload=payment_id,
        )
        if topup is None:
            return None
        return await self._process_topup_webhook(
            topup=topup,
            provider_invoice_id=invoice_id,
            payment_payload=payment_id,
        )

    async def process_platega_webhook_payment(
        self,
        *,
        transaction_id: str | None = None,
        payment_payload: str | None = None,
        webhook_status: str | None = None,
    ) -> Optional[StarsOrderDto]:
        order = await process_platega_webhook_payment_support(
            service=self,
            transaction_id=transaction_id,
            payment_payload=payment_payload,
            webhook_status=webhook_status,
        )
        if order is not None:
            return order
        topup = await self._find_topup_for_webhook(
            providers=[StarsPaymentProvider.PLATEGA_PAY],
            payment_payload=payment_payload,
            provider_reference=transaction_id,
        )
        if topup is None:
            return None
        return await self._process_topup_webhook(
            topup=topup,
            provider_status=webhook_status,
            payment_payload=payment_payload,
            provider_reference=transaction_id,
        )

    async def process_nice_pay_webhook_payment(
        self,
        *,
        payment_id: str | None = None,
        order_id: str | None = None,
        webhook_result: str | None = None,
    ) -> Optional[StarsOrderDto]:
        order = await process_nice_pay_webhook_payment_support(
            service=self,
            payment_id=payment_id,
            order_id=order_id,
            webhook_result=webhook_result,
        )
        if order is not None:
            return order
        topup = await self._find_topup_for_webhook(
            providers=[StarsPaymentProvider.NICE_PAY_RU, StarsPaymentProvider.NICE_PAY_KZ],
            payment_payload=payment_id,
            provider_reference=order_id,
        )
        if topup is None:
            return None
        return await self._process_topup_webhook(
            topup=topup,
            provider_status=webhook_result,
            payment_payload=payment_id,
            provider_reference=order_id,
        )

    async def process_heleket_webhook_invoice(
        self,
        *,
        invoice_uuid: str | None = None,
        order_id: str | None = None,
        webhook_status: str | None = None,
    ) -> Optional[StarsOrderDto]:
        order = await process_heleket_webhook_invoice_support(
            service=self,
            invoice_uuid=invoice_uuid,
            order_id=order_id,
            webhook_status=webhook_status,
        )
        if order is not None:
            return order
        topup = await self._find_topup_for_webhook(
            providers=[StarsPaymentProvider.HELEKET_PAY],
            payment_payload=invoice_uuid,
            provider_reference=order_id,
        )
        if topup is None:
            return None
        return await self._process_topup_webhook(
            topup=topup,
            provider_status=webhook_status,
            payment_payload=invoice_uuid,
            provider_reference=order_id,
        )

    async def process_xrocket_webhook_invoice(
        self,
        *,
        payment_payload: str | None = None,
        invoice_id: str | None = None,
        webhook_status: str | None = None,
    ) -> Optional[StarsOrderDto]:
        order = await process_xrocket_webhook_invoice_support(
            service=self,
            payment_payload=payment_payload,
            invoice_id=invoice_id,
            webhook_status=webhook_status,
        )
        if order is not None:
            return order
        topup = await self._find_topup_for_webhook(
            providers=[StarsPaymentProvider.XROCKET_PAY],
            payment_payload=payment_payload,
            provider_reference=invoice_id,
        )
        if topup is None:
            return None
        return await self._process_topup_webhook(
            topup=topup,
            provider_status=webhook_status,
            payment_payload=payment_payload,
            provider_reference=invoice_id,
        )

    async def poll_pending_orders(self, *, limit: int) -> list[PaymentCheckResult]:
        pending_created_after = datetime_now() - self.poll_unpaid_max_age
        order_results = await poll_pending_orders_support(
            service=self,
            limit=limit,
            logger=logger,
            pending_created_after=pending_created_after,
        )
        if limit <= 0:
            return order_results

        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            pending_topups = await repository.balance_topups.list_pending_for_polling(
                limit=limit,
                pending_created_after=pending_created_after,
            )
        if not pending_topups:
            return order_results

        semaphore = asyncio.Semaphore(self.poll_concurrency)

        async def verify_topup_one(topup_id: int) -> PaymentCheckResult | None:
            async with semaphore:
                try:
                    return await self.verify_order(
                        order_id=self._encode_topup_order_id(topup_id=topup_id)
                    )
                except Exception:
                    logger.exception(
                        "Failed to verify pending top-up %s in polling loop.",
                        topup_id,
                    )
                    return None

        topup_results = await asyncio.gather(
            *(verify_topup_one(int(topup.id)) for topup in pending_topups),
        )
        merged = list(order_results)
        merged.extend(item for item in topup_results if item is not None)
        return merged

    async def poll_pending_provider_orders(
        self,
        *,
        provider: StarsPaymentProvider,
        limit: int,
    ) -> list[PaymentCheckResult]:
        if limit <= 0:
            return []
        pending_created_after = datetime_now() - self.poll_unpaid_max_age
        order_results = await poll_pending_orders_support(
            service=self,
            limit=limit,
            logger=logger,
            provider=provider,
            pending_created_after=pending_created_after,
        )

        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            pending_topups = await repository.balance_topups.list_pending_for_polling(
                limit=limit,
                provider=provider,
                pending_created_after=pending_created_after,
            )
        if not pending_topups:
            return order_results

        semaphore = asyncio.Semaphore(self.poll_concurrency)

        async def verify_topup_one(topup_id: int) -> PaymentCheckResult | None:
            async with semaphore:
                try:
                    return await self.verify_order(
                        order_id=self._encode_topup_order_id(topup_id=topup_id)
                    )
                except Exception:
                    logger.exception(
                        "Failed to verify pending %s top-up %s in polling loop.",
                        provider.value,
                        topup_id,
                    )
                    return None

        topup_results = await asyncio.gather(
            *(verify_topup_one(int(topup.id)) for topup in pending_topups),
        )
        merged = list(order_results)
        merged.extend(item for item in topup_results if item is not None)
        return merged

    async def _is_order_paid(self, *, order: StarsOrderDto) -> tuple[bool, str]:  # noqa: C901
        return await is_order_paid_support(service=self, order=order)

    async def _fulfill_paid_order(self, *, order_id: int) -> StarsOrderDto:  # noqa: C901
        return await fulfill_paid_order_support(
            service=self,
            order_id=order_id,
            order_error_cls=StarsOrderError,
            logger=logger,
        )

    async def _apply_referral_rewards(self, *, order_id: int) -> None:  # noqa: C901
        await apply_referral_rewards_support(
            service=self,
            order_id=order_id,
        )

    async def _mark_failed_and_refund(
        self,
        *,
        order: StarsOrderDto,
        error_text: str,
    ) -> StarsOrderDto:
        return await mark_failed_and_refund_support(
            service=self,
            order=order,
            error_text=error_text,
            order_error_cls=StarsOrderError,
            logger=logger,
        )

    async def _debit_user_balance_if_enough(self, *, user_id: int, amount_cents: int) -> bool:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            debited = await repository.users.debit_balance_if_enough(
                user_id=user_id,
                amount_cents=amount_cents,
            )
        await self._clear_user_cache(user_id=user_id)
        return debited is not None

    async def _credit_user_balance(self, *, user_id: int, amount_cents: int) -> bool:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            credited = await repository.users.add_balance(
                user_id=user_id,
                amount_cents=amount_cents,
            )
        await self._clear_user_cache(user_id=user_id)
        return credited is not None

    async def _clear_user_cache(self, *, user_id: int) -> None:
        cache_key: str = build_key("cache", "get_user", user_id=user_id)
        await self.redis.delete(cache_key)

    async def _create_order_record(
        self,
        *,
        user_id: int,
        recipient_username: str,
        stars_count: int,
        product_type: StarsOrderProductType,
        premium_months: int | None = None,
        recipient_user_id: int | None = None,
        gift_id: str | None = None,
        gift_message: str | None = None,
        gift_sender_private: bool | None = None,
        amount_cents: int,
        payment_provider: StarsPaymentProvider,
        payment_currency: str,
        status: StarsOrderStatus,
    ) -> StarsOrderDto:
        order = StarsOrder(
            user_id=user_id,
            recipient_username=recipient_username,
            stars_count=stars_count,
            product_type=product_type.value,
            premium_months=premium_months,
            recipient_user_id=recipient_user_id,
            gift_id=gift_id,
            gift_message=gift_message,
            gift_sender_private=gift_sender_private,
            amount_cents=amount_cents,
            payment_provider=payment_provider.value,
            payment_currency=payment_currency,
            status=status.value,
        )
        async with SQLSessionContext(session_pool=self.session_pool) as (_repository, uow):
            await uow.commit(order)
        return order.dto()

    async def _transition_order_status(
        self,
        *,
        order_id: int,
        from_statuses: list[StarsOrderStatus],
        to_status: StarsOrderStatus,
        **data: Any,
    ) -> Optional[StarsOrderDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            updated = await repository.stars_orders.update_if_status(
                order_id=order_id,
                current_statuses=from_statuses,
                status=to_status.value,
                **data,
            )
            if updated is None:
                return None
            return updated.dto()

    async def _update_order(self, *, order_id: int, **data: Any) -> Optional[StarsOrderDto]:
        serialized_data = {
            key: value.value if isinstance(value, StrEnum) else value
            for key, value in data.items()
        }
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            updated = await repository.stars_orders.update(order_id=order_id, **serialized_data)
            if updated is None:
                return None
            return updated.dto()

    @staticmethod
    def _is_retryable_delivery_error(error_text: str) -> bool:
        lowered = error_text.lower()
        if "payload is not a valid boc comment" in lowered:
            return False
        if "balance is too low" in lowered:
            return False
        if "transaction was not confirmed on-chain in time" in lowered:
            return False
        return any(marker in lowered for marker in RETRYABLE_DELIVERY_ERROR_MARKERS)

    @staticmethod
    def _fulfill_lock_key(*, order_id: int) -> str:
        return f"{FULFILL_LOCK_KEY_PREFIX}:{order_id}"

    async def _acquire_fulfill_lock(self, *, order_id: int) -> str | None:
        lock_key = self._fulfill_lock_key(order_id=order_id)
        lock_token = uuid4().hex
        acquired = await self.redis.set(
            lock_key,
            lock_token,
            ex=FULFILL_LOCK_TTL_SECONDS,
            nx=True,
        )
        return lock_token if acquired else None

    async def _release_fulfill_lock(self, *, order_id: int, lock_token: str) -> None:
        lock_key = self._fulfill_lock_key(order_id=order_id)
        release_script = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
"""
        try:
            await cast(
                Awaitable[Any],
                self.redis.eval(release_script, 1, lock_key, lock_token),
            )
        except Exception:
            # Lock cleanup is best-effort; TTL guarantees eventual release.
            return

    def provider_payment_fee_percent_text(self, *, provider: StarsPaymentProvider) -> str:
        value = self.payment_fee_percents.get(provider, Decimal("0"))
        return self._format_percent(value)

    def provider_payout_fee_percent_text(self, *, provider: StarsPaymentProvider) -> str:
        value = self.payout_fee_percents.get(provider, Decimal("0"))
        return self._format_percent(value)

    def provider_payout_fixed_usd(self, *, provider: StarsPaymentProvider) -> str:
        payout_fixed_cents = self.payout_fixed_cents.get(provider, 0)
        return price_usd_for_cents(payout_fixed_cents)

    def provider_configured(self, *, provider: StarsPaymentProvider) -> bool:
        return self._is_provider_configured(provider=provider)

    def referral_level_percent_texts(self) -> tuple[str, str, str]:
        return (
            self._format_percent(self.referral_level_percents[0]),
            self._format_percent(self.referral_level_percents[1]),
            self._format_percent(self.referral_level_percents[2]),
        )

    def provider_checkout_fee_percent_text(
        self,
        *,
        provider: StarsPaymentProvider,
        net_amount_cents: int,
    ) -> str:
        if net_amount_cents <= 0:
            return self.provider_payment_fee_percent_text(provider=provider)
        try:
            pricing = self._build_checkout_pricing(
                provider=provider,
                net_amount_cents=net_amount_cents,
            )
        except ValidationError:
            return self.provider_payment_fee_percent_text(provider=provider)
        return pricing.fee_percent_text

    def provider_checkout_fee_display_text(
        self,
        *,
        provider: StarsPaymentProvider,
        net_amount_cents: int,
        compact: bool = False,
    ) -> str:
        if net_amount_cents <= 0:
            return f"{self.provider_payment_fee_percent_text(provider=provider)}%"
        try:
            percent_value = self._display_fee_percent(
                provider=provider,
                payment_rate=self.payment_fee_percents.get(provider, Decimal("0"))
                / Decimal("100"),
                payout_rate=self.payout_fee_percents.get(provider, Decimal("0"))
                / Decimal("100"),
            )
        except ValidationError:
            return f"{self.provider_payment_fee_percent_text(provider=provider)}%"

        percent_text = self._format_percent(percent_value)
        fixed_component_cents = self._checkout_fixed_component_cents(provider=provider)
        if fixed_component_cents <= 0:
            return f"{percent_text}%"
        fixed_text = price_usd_for_cents(fixed_component_cents)
        if compact:
            return f"{percent_text}%+${fixed_text}"
        return f"{percent_text}% + {fixed_text} USD"

    def provider_currency(self, *, provider: StarsPaymentProvider) -> str:
        return self._provider_currency(provider=provider)

    def provider_supports_payment_amount(
        self,
        *,
        provider: StarsPaymentProvider,
        amount_cents: int,
    ) -> bool:
        if amount_cents <= 0:
            return False
        try:
            self._validate_provider_min_payment_amount(
                provider=provider,
                amount_cents=amount_cents,
            )
        except PaymentMinAmountError:
            return False
        return True

    def checkout_pricing_for_order(self, *, order: StarsOrderDto) -> CheckoutPricing:
        return self._build_checkout_pricing(
            provider=order.payment_provider,
            net_amount_cents=order.amount_cents,
        )

    def preview_checkout_pricing(
        self,
        *,
        provider: StarsPaymentProvider,
        net_amount_cents: int,
    ) -> CheckoutPricing:
        """Compute checkout pricing for a hypothetical order without persisting it."""

        return self._build_checkout_pricing(
            provider=provider,
            net_amount_cents=net_amount_cents,
        )

    def _build_checkout_pricing(
        self,
        *,
        provider: StarsPaymentProvider,
        net_amount_cents: int,
    ) -> CheckoutPricing:
        if provider == StarsPaymentProvider.BALANCE:
            return CheckoutPricing(
                net_amount_cents=net_amount_cents,
                invoice_amount_cents=net_amount_cents,
                customer_total_cents=net_amount_cents,
                fee_percent_text="0",
            )

        net_amount = Decimal(net_amount_cents) / Decimal("100")
        payment_fee_percent = self.payment_fee_percents.get(provider, Decimal("0"))
        payout_fee_percent = self.payout_fee_percents.get(provider, Decimal("0"))
        payout_fixed_cents = self.payout_fixed_cents.get(provider, 0)
        payout_fixed = Decimal(payout_fixed_cents) / Decimal("100")

        payment_rate = payment_fee_percent / Decimal("100")
        payout_rate = payout_fee_percent / Decimal("100")
        payment_fee_on_top = provider in {
            StarsPaymentProvider.PLATEGA_PAY,
            StarsPaymentProvider.NICE_PAY_RU,
            StarsPaymentProvider.NICE_PAY_KZ,
        }

        denominator = Decimal("1") - payout_rate
        if not payment_fee_on_top:
            denominator *= Decimal("1") - payment_rate
        if denominator <= 0:
            raise ValidationError("Invalid payment fee configuration.")

        invoice_amount = ((net_amount + payout_fixed) / denominator).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        if invoice_amount <= 0:
            raise ValidationError("Calculated checkout amount must be positive.")

        net_after_fees = self._net_after_fees(
            invoice_amount=invoice_amount,
            payment_rate=payment_rate,
            payout_rate=payout_rate,
            payout_fixed=payout_fixed,
            payment_fee_on_top=payment_fee_on_top,
        )
        while net_after_fees < net_amount:
            invoice_amount += Decimal("0.01")
            net_after_fees = self._net_after_fees(
                invoice_amount=invoice_amount,
                payment_rate=payment_rate,
                payout_rate=payout_rate,
                payout_fixed=payout_fixed,
                payment_fee_on_top=payment_fee_on_top,
            )

        customer_total = (
            (invoice_amount * (Decimal("1") + payment_rate))
            if payment_fee_on_top
            else invoice_amount
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        fee_percent = self._display_fee_percent(
            provider=provider,
            payment_rate=payment_rate,
            payout_rate=payout_rate,
        )

        return CheckoutPricing(
            net_amount_cents=int((net_amount * Decimal("100")).quantize(Decimal("1"))),
            invoice_amount_cents=int((invoice_amount * Decimal("100")).quantize(Decimal("1"))),
            customer_total_cents=int((customer_total * Decimal("100")).quantize(Decimal("1"))),
            fee_percent_text=self._format_percent(fee_percent),
        )

    @staticmethod
    def _display_fee_percent(
        *,
        provider: StarsPaymentProvider,
        payment_rate: Decimal,
        payout_rate: Decimal,
    ) -> Decimal:
        if provider == StarsPaymentProvider.BALANCE:
            return Decimal("0")

        payout_multiplier = Decimal("1") - payout_rate
        if payout_multiplier <= 0:
            return Decimal("0")

        if provider in {
            StarsPaymentProvider.PLATEGA_PAY,
            StarsPaymentProvider.NICE_PAY_RU,
            StarsPaymentProvider.NICE_PAY_KZ,
        }:
            ratio = (Decimal("1") + payment_rate) / payout_multiplier
        else:
            payment_multiplier = Decimal("1") - payment_rate
            if payment_multiplier <= 0:
                return Decimal("0")
            ratio = Decimal("1") / (payment_multiplier * payout_multiplier)

        fee = (ratio - Decimal("1")) * Decimal("100")
        return fee if fee > 0 else Decimal("0")

    def _checkout_fixed_component_cents(self, *, provider: StarsPaymentProvider) -> int:
        payout_fixed_cents = max(0, int(self.payout_fixed_cents.get(provider, 0)))
        if payout_fixed_cents <= 0:
            return 0

        payout_rate = self.payout_fee_percents.get(provider, Decimal("0")) / Decimal("100")
        payment_rate = self.payment_fee_percents.get(provider, Decimal("0")) / Decimal("100")
        payout_multiplier = Decimal("1") - payout_rate
        if payout_multiplier <= 0:
            return 0

        if provider in {
            StarsPaymentProvider.PLATEGA_PAY,
            StarsPaymentProvider.NICE_PAY_RU,
            StarsPaymentProvider.NICE_PAY_KZ,
        }:
            factor = (Decimal("1") + payment_rate) / payout_multiplier
        else:
            payment_multiplier = Decimal("1") - payment_rate
            if payment_multiplier <= 0:
                return 0
            factor = Decimal("1") / (payment_multiplier * payout_multiplier)

        fixed_component = (Decimal(payout_fixed_cents) / Decimal("100")) * factor
        cents = int(
            (fixed_component * Decimal("100")).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP,
            )
        )
        return max(0, cents)

    @staticmethod
    def _net_after_fees(
        *,
        invoice_amount: Decimal,
        payment_rate: Decimal,
        payout_rate: Decimal,
        payout_fixed: Decimal,
        payment_fee_on_top: bool,
    ) -> Decimal:
        merchant_base = (
            invoice_amount
            if payment_fee_on_top
            else invoice_amount * (Decimal("1") - payment_rate)
        )
        return (merchant_base * (Decimal("1") - payout_rate)) - payout_fixed

    @staticmethod
    def _parse_percent(value: str, *, default: str) -> Decimal:
        raw = (value or "").strip() or default
        try:
            parsed = Decimal(raw)
        except (InvalidOperation, TypeError):
            parsed = Decimal(default)
        if parsed < 0:
            return Decimal("0")
        if parsed >= 100:
            return Decimal("99.99")
        return parsed

    @staticmethod
    def _parse_money_cents(value: str, *, default: str) -> int:
        raw = (value or "").strip() or default
        try:
            parsed = Decimal(raw)
        except (InvalidOperation, TypeError):
            parsed = Decimal(default)
        if parsed < 0:
            parsed = Decimal("0")
        return int((parsed * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    @staticmethod
    def _format_percent(value: Decimal) -> str:
        normalized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        text = format(normalized, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text or "0"

    @staticmethod
    def _format_amount(value: Decimal) -> str:
        normalized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        text = format(normalized, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text or "0"

    @staticmethod
    def _calculate_referral_reward_cents(*, amount_cents: int, percent: Decimal) -> int:
        if amount_cents <= 0 or percent <= 0:
            return 0
        reward = (Decimal(amount_cents) * percent / Decimal("100")).quantize(
            Decimal("1"),
            rounding=ROUND_DOWN,
        )
        return max(0, int(reward))

    def _provider_currency(self, *, provider: StarsPaymentProvider) -> str:
        return provider_currency_support(service=self, provider=provider)

    def _provider_min_payment_cents(self, *, provider: StarsPaymentProvider) -> int:
        configured = self.min_payment_amount_cents.get(provider, 100)
        return max(1, int(configured))

    def _validate_provider_min_payment_amount(
        self,
        *,
        provider: StarsPaymentProvider,
        amount_cents: int,
    ) -> None:
        minimum_cents = self._provider_min_payment_cents(provider=provider)
        if amount_cents >= minimum_cents:
            return
        min_amount_text = self._format_amount(Decimal(minimum_cents) / Decimal("100"))
        raise PaymentMinAmountError(
            provider=provider,
            currency="USD",
            min_amount_text=min_amount_text,
        )

    async def _resolve_gift_recipient_user_id(
        self,
        *,
        recipient_username: str,
        recipient_user_id: int | None,
    ) -> int | None:
        if recipient_user_id is not None and recipient_user_id > 0:
            return recipient_user_id
        try:
            resolved_user_id = await self.telegram_gift_service.resolve_user_id(
                recipient_username=recipient_username,
            )
            if resolved_user_id is not None and resolved_user_id > 0:
                return resolved_user_id
            if self.telegram_gift_service.userbot_configured:
                raise ValidationError("Gift recipient username is invalid.")
            raise ValidationError(
                "Gift recipient cannot be verified without userbot session. "
                "Configure TELEGRAM_GIFTS_USERBOT_SESSION or ask recipient to start the bot."
            )
        except RuntimeError as error:
            raise ValidationError(str(error)) from error

    @staticmethod
    def _normalize_gift_message(value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        if len(normalized) > 128:
            raise ValidationError("Gift message is too long.")
        return normalized

    @staticmethod
    def _resolve_gift_pack(*, gift_key: str) -> TelegramGiftPack:
        normalized = gift_key.strip()
        if not normalized:
            raise ValidationError("Gift is not selected.")
        try:
            return get_gift_pack(key=normalized)
        except ValueError as error:
            raise ValidationError("Unsupported gift.") from error

    @staticmethod
    def _build_platega_payload(*, local_order_id: int) -> str:
        return build_platega_payload_support(local_order_id=local_order_id)

    @staticmethod
    def _build_nice_pay_order_id(*, provider: StarsPaymentProvider, local_order_id: int) -> str:
        return build_nice_pay_order_id_support(
            provider=provider,
            local_order_id=local_order_id,
        )

    def _nice_pay_currency(self, *, provider: StarsPaymentProvider) -> str:
        return nice_pay_currency_support(service=self, provider=provider)

    @staticmethod
    def _build_heleket_order_id(*, local_order_id: int) -> str:
        return build_heleket_order_id_support(local_order_id=local_order_id)

    def _lzt_callback_url(self) -> str | None:
        return lzt_callback_url_support(service=self)

    def _xrocket_callback_url(self) -> str | None:
        return xrocket_callback_url_support(service=self)

    def _heleket_callback_url(self) -> str | None:
        return heleket_callback_url_support(service=self)
