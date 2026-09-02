from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any, Optional, cast

from sqlalchemy import Select, and_, desc, func, or_, select

from app.enums.stars_order import StarsOrderProductType, StarsOrderStatus, StarsPaymentProvider
from app.models.sql import StarsOrder
from app.services.postgres.repositories.base import BaseRepository


class StarsOrdersRepository(BaseRepository):
    @staticmethod
    def _apply_admin_filters(
        query: Any,
        *,
        user_id: int | None,
        status: StarsOrderStatus | None,
        provider: StarsPaymentProvider | None,
        allowed_providers: Sequence[StarsPaymentProvider] | None,
        product_type: StarsOrderProductType | None,
        search: str | None,
    ) -> Any:
        if user_id is not None and user_id > 0:
            query = query.where(StarsOrder.user_id == user_id)
        if status is not None:
            query = query.where(StarsOrder.status == status.value)
        if provider is not None:
            query = query.where(StarsOrder.payment_provider == provider.value)
        elif allowed_providers:
            query = query.where(
                StarsOrder.payment_provider.in_([item.value for item in allowed_providers])
            )
        if product_type is not None:
            query = query.where(StarsOrder.product_type == product_type.value)

        normalized_search = (search or "").strip()
        if normalized_search:
            conditions: list[Any] = [
                StarsOrder.recipient_username.ilike(f"%{normalized_search}%"),
                StarsOrder.provider_reference.ilike(f"%{normalized_search}%"),
                StarsOrder.payment_payload.ilike(f"%{normalized_search}%"),
                StarsOrder.gift_id.ilike(f"%{normalized_search}%"),
            ]
            if normalized_search.isdigit():
                numeric_value = int(normalized_search)
                conditions.extend(
                    [
                        StarsOrder.id == numeric_value,
                        StarsOrder.user_id == numeric_value,
                        StarsOrder.provider_invoice_id == numeric_value,
                    ]
                )
            query = query.where(or_(*conditions))
        return query

    async def count(self) -> int:
        result = await self.session.scalar(select(func.count(StarsOrder.id)))
        return int(result or 0)

    async def count_for_admin(
        self,
        *,
        user_id: int | None = None,
        status: StarsOrderStatus | None = None,
        provider: StarsPaymentProvider | None = None,
        allowed_providers: Sequence[StarsPaymentProvider] | None = None,
        product_type: StarsOrderProductType | None = None,
        search: str | None = None,
    ) -> int:
        query = select(func.count(StarsOrder.id))
        query = self._apply_admin_filters(
            query,
            user_id=user_id,
            status=status,
            provider=provider,
            allowed_providers=allowed_providers,
            product_type=product_type,
            search=search,
        )
        result = await self.session.scalar(query)
        return int(result or 0)

    async def count_by_user(self, *, user_id: int) -> int:
        result = await self.session.scalar(
            select(func.count(StarsOrder.id)).where(StarsOrder.user_id == user_id)
        )
        return int(result or 0)

    async def count_created_since(self, *, since: datetime) -> int:
        query = select(func.count(StarsOrder.id)).where(StarsOrder.created_at >= since)
        result = await self.session.scalar(query)
        return int(result or 0)

    async def count_paid_since(self, *, since: datetime) -> int:
        query = select(func.count(StarsOrder.id)).where(
            and_(
                StarsOrder.paid_at.is_not(None),
                StarsOrder.paid_at >= since,
            )
        )
        result = await self.session.scalar(query)
        return int(result or 0)

    async def sum_paid_amount_since(self, *, since: datetime) -> int:
        query = select(func.coalesce(func.sum(StarsOrder.amount_cents), 0)).where(
            and_(
                StarsOrder.paid_at.is_not(None),
                StarsOrder.paid_at >= since,
            )
        )
        result = await self.session.scalar(query)
        return int(result or 0)

    async def sum_completed_amount(self) -> int:
        query = select(func.coalesce(func.sum(StarsOrder.amount_cents), 0)).where(
            StarsOrder.status == StarsOrderStatus.COMPLETED.value
        )
        result = await self.session.scalar(query)
        return int(result or 0)

    async def sum_completed_stars(self) -> int:
        query = select(func.coalesce(func.sum(StarsOrder.stars_count), 0)).where(
            and_(
                StarsOrder.status == StarsOrderStatus.COMPLETED.value,
                StarsOrder.product_type == StarsOrderProductType.STARS.value,
            )
        )
        result = await self.session.scalar(query)
        return int(result or 0)

    async def count_by_status(self) -> dict[str, int]:
        query = select(StarsOrder.status, func.count(StarsOrder.id)).group_by(StarsOrder.status)
        rows = (await self.session.execute(query)).all()
        return {str(status): int(total) for status, total in rows}

    async def completed_breakdown_by_product(self) -> dict[str, dict[str, int]]:
        query = (
            select(
                StarsOrder.product_type,
                func.count(StarsOrder.id),
                func.coalesce(func.sum(StarsOrder.amount_cents), 0),
                func.coalesce(func.sum(StarsOrder.stars_count), 0),
            )
            .where(StarsOrder.status == StarsOrderStatus.COMPLETED.value)
            .group_by(StarsOrder.product_type)
        )
        rows = (await self.session.execute(query)).all()
        return {
            str(product_type): {
                "count": int(count_value),
                "amount_cents": int(amount_cents),
                "stars_count": int(stars_count),
            }
            for product_type, count_value, amount_cents, stars_count in rows
        }

    async def get(self, order_id: int) -> Optional[StarsOrder]:
        return await self._get(StarsOrder, StarsOrder.id == order_id)

    async def get_open_for_user(self, user_id: int) -> Optional[StarsOrder]:
        open_statuses = (
            StarsOrderStatus.CREATING_PAYMENT.value,
            StarsOrderStatus.PENDING_PAYMENT.value,
            StarsOrderStatus.PAYMENT_CONFIRMED.value,
            StarsOrderStatus.FULFILLING.value,
        )
        query: Select[tuple[StarsOrder]] = (
            select(StarsOrder)
            .where(
                and_(
                    StarsOrder.user_id == user_id,
                    StarsOrder.status.in_(open_statuses),
                )
            )
            .order_by(desc(StarsOrder.created_at))
            .limit(1)
        )
        return cast(Optional[StarsOrder], await self.session.scalar(query))

    async def get_by_provider_invoice(
        self,
        *,
        provider: StarsPaymentProvider,
        provider_invoice_id: int,
    ) -> Optional[StarsOrder]:
        return await self._get(
            StarsOrder,
            StarsOrder.payment_provider == provider.value,
            StarsOrder.provider_invoice_id == provider_invoice_id,
        )

    async def get_by_provider_payload(
        self,
        *,
        provider: StarsPaymentProvider,
        payment_payload: str,
    ) -> Optional[StarsOrder]:
        return await self._get(
            StarsOrder,
            StarsOrder.payment_provider == provider.value,
            StarsOrder.payment_payload == payment_payload,
        )

    async def get_by_provider_reference(
        self,
        *,
        provider: StarsPaymentProvider,
        provider_reference: str,
    ) -> Optional[StarsOrder]:
        return await self._get(
            StarsOrder,
            StarsOrder.payment_provider == provider.value,
            StarsOrder.provider_reference == provider_reference,
        )

    async def list_pending_for_polling(
        self,
        *,
        limit: int,
        provider: StarsPaymentProvider | None = None,
        pending_created_after: datetime | None = None,
    ) -> list[StarsOrder]:
        if limit <= 0:
            return []
        statuses = (
            StarsOrderStatus.CREATING_PAYMENT.value,
            StarsOrderStatus.PENDING_PAYMENT.value,
            StarsOrderStatus.PAYMENT_CONFIRMED.value,
            StarsOrderStatus.FULFILLING.value,
        )
        query: Select[tuple[StarsOrder]] = select(StarsOrder).where(
            StarsOrder.status.in_(statuses)
        )
        if pending_created_after is not None:
            query = query.where(
                or_(
                    StarsOrder.status.in_(
                        (
                            StarsOrderStatus.PAYMENT_CONFIRMED.value,
                            StarsOrderStatus.FULFILLING.value,
                        )
                    ),
                    StarsOrder.created_at >= pending_created_after,
                )
            )
        if provider is not None:
            query = query.where(StarsOrder.payment_provider == provider.value)
        query = query.order_by(StarsOrder.created_at.asc()).limit(limit)
        return list(await self.session.scalars(query))

    async def list_for_admin(
        self,
        *,
        limit: int,
        offset: int = 0,
        user_id: int | None = None,
        status: StarsOrderStatus | None = None,
        provider: StarsPaymentProvider | None = None,
        allowed_providers: Sequence[StarsPaymentProvider] | None = None,
        product_type: StarsOrderProductType | None = None,
        search: str | None = None,
    ) -> list[StarsOrder]:
        if limit <= 0:
            return []
        query: Select[tuple[StarsOrder]] = (
            select(StarsOrder)
            .order_by(desc(StarsOrder.created_at), desc(StarsOrder.id))
            .offset(max(offset, 0))
            .limit(limit)
        )
        query = self._apply_admin_filters(
            query,
            user_id=user_id,
            status=status,
            provider=provider,
            allowed_providers=allowed_providers,
            product_type=product_type,
            search=search,
        )
        return list(await self.session.scalars(query))

    async def list_recent_by_user(self, *, user_id: int, limit: int) -> list[StarsOrder]:
        if limit <= 0:
            return []
        query: Select[tuple[StarsOrder]] = (
            select(StarsOrder)
            .where(StarsOrder.user_id == user_id)
            .order_by(desc(StarsOrder.created_at))
            .limit(limit)
        )
        return list(await self.session.scalars(query))

    async def list_recent_by_user_page(
        self,
        *,
        user_id: int,
        limit: int,
        offset: int,
    ) -> list[StarsOrder]:
        if limit <= 0:
            return []
        query: Select[tuple[StarsOrder]] = (
            select(StarsOrder)
            .where(StarsOrder.user_id == user_id)
            .order_by(desc(StarsOrder.created_at))
            .offset(max(offset, 0))
            .limit(limit)
        )
        return list(await self.session.scalars(query))

    async def get_by_user(self, *, user_id: int, order_id: int) -> Optional[StarsOrder]:
        return await self._get(
            StarsOrder,
            StarsOrder.id == order_id,
            StarsOrder.user_id == user_id,
        )

    async def sum_completed_stars_by_user(self, *, user_id: int) -> int:
        query = select(
            func.coalesce(func.sum(StarsOrder.stars_count), 0),
        ).where(
            and_(
                StarsOrder.user_id == user_id,
                StarsOrder.status == StarsOrderStatus.COMPLETED.value,
                StarsOrder.product_type == StarsOrderProductType.STARS.value,
            )
        )
        result = await self.session.scalar(query)
        return int(result or 0)

    async def count_completed_premiums_by_user(self, *, user_id: int) -> int:
        query = select(
            func.coalesce(func.count(StarsOrder.id), 0),
        ).where(
            and_(
                StarsOrder.user_id == user_id,
                StarsOrder.status == StarsOrderStatus.COMPLETED.value,
                StarsOrder.product_type == StarsOrderProductType.PREMIUM.value,
            )
        )
        result = await self.session.scalar(query)
        return int(result or 0)

    async def sum_completed_stars_amount_by_user(self, *, user_id: int) -> int:
        query = select(
            func.coalesce(func.sum(StarsOrder.amount_cents), 0),
        ).where(
            and_(
                StarsOrder.user_id == user_id,
                StarsOrder.status == StarsOrderStatus.COMPLETED.value,
                StarsOrder.product_type == StarsOrderProductType.STARS.value,
            )
        )
        result = await self.session.scalar(query)
        return int(result or 0)

    async def sum_completed_premiums_amount_by_user(self, *, user_id: int) -> int:
        query = select(
            func.coalesce(func.sum(StarsOrder.amount_cents), 0),
        ).where(
            and_(
                StarsOrder.user_id == user_id,
                StarsOrder.status == StarsOrderStatus.COMPLETED.value,
                StarsOrder.product_type == StarsOrderProductType.PREMIUM.value,
            )
        )
        result = await self.session.scalar(query)
        return int(result or 0)

    async def update(self, order_id: int, **data: Any) -> Optional[StarsOrder]:
        return await self._update(
            model=StarsOrder,
            conditions=[StarsOrder.id == order_id],
            load_result=True,
            **data,
        )

    async def update_if_status(
        self,
        *,
        order_id: int,
        current_statuses: list[StarsOrderStatus],
        **data: Any,
    ) -> Optional[StarsOrder]:
        return await self._update(
            model=StarsOrder,
            conditions=[
                StarsOrder.id == order_id,
                StarsOrder.status.in_([status.value for status in current_statuses]),
            ],
            load_result=True,
            **data,
        )
