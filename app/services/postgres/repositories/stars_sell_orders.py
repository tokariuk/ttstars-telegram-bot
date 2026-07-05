from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any, Optional, cast

from sqlalchemy import Select, and_, desc, func, or_, select

from app.enums.stars_sell_order import StarsSellOrderStatus
from app.models.sql import StarsSellOrder
from app.services.postgres.repositories.base import BaseRepository


class StarsSellOrdersRepository(BaseRepository):
    @staticmethod
    def _apply_admin_filters(
        query: Any,
        *,
        user_id: int | None,
        status: StarsSellOrderStatus | None,
        statuses: Sequence[StarsSellOrderStatus] | None,
        search: str | None,
    ) -> Any:
        if user_id is not None and user_id > 0:
            query = query.where(StarsSellOrder.user_id == user_id)
        if status is not None:
            query = query.where(StarsSellOrder.status == status.value)
        elif statuses:
            query = query.where(StarsSellOrder.status.in_([item.value for item in statuses]))

        normalized_search = (search or "").strip()
        if normalized_search:
            conditions: list[Any] = [
                StarsSellOrder.payout_wallet.ilike(f"%{normalized_search}%"),
                StarsSellOrder.invoice_payload.ilike(f"%{normalized_search}%"),
                StarsSellOrder.telegram_payment_charge_id.ilike(f"%{normalized_search}%"),
                StarsSellOrder.provider_payment_charge_id.ilike(f"%{normalized_search}%"),
            ]
            if normalized_search.isdigit():
                numeric = int(normalized_search)
                conditions.extend(
                    [
                        StarsSellOrder.id == numeric,
                        StarsSellOrder.user_id == numeric,
                        StarsSellOrder.stars_count == numeric,
                    ]
                )
            query = query.where(or_(*conditions))
        return query

    async def count(self) -> int:
        result = await self.session.scalar(select(func.count(StarsSellOrder.id)))
        return int(result or 0)

    async def count_for_admin(
        self,
        *,
        user_id: int | None = None,
        status: StarsSellOrderStatus | None = None,
        statuses: Sequence[StarsSellOrderStatus] | None = None,
        search: str | None = None,
    ) -> int:
        query = select(func.count(StarsSellOrder.id))
        query = self._apply_admin_filters(
            query,
            user_id=user_id,
            status=status,
            statuses=statuses,
            search=search,
        )
        result = await self.session.scalar(query)
        return int(result or 0)

    async def get(self, order_id: int) -> Optional[StarsSellOrder]:
        return await self._get(StarsSellOrder, StarsSellOrder.id == order_id)

    async def get_by_invoice_payload(self, *, invoice_payload: str) -> Optional[StarsSellOrder]:
        return await self._get(
            StarsSellOrder,
            StarsSellOrder.invoice_payload == invoice_payload,
        )

    async def get_open_payment_for_user(self, *, user_id: int) -> Optional[StarsSellOrder]:
        query: Select[tuple[StarsSellOrder]] = (
            select(StarsSellOrder)
            .where(
                and_(
                    StarsSellOrder.user_id == user_id,
                    StarsSellOrder.status == StarsSellOrderStatus.PENDING_PAYMENT.value,
                )
            )
            .order_by(desc(StarsSellOrder.created_at))
            .limit(1)
        )
        return cast(Optional[StarsSellOrder], await self.session.scalar(query))

    async def list_recent_by_user(self, *, user_id: int, limit: int) -> list[StarsSellOrder]:
        if limit <= 0:
            return []
        query: Select[tuple[StarsSellOrder]] = (
            select(StarsSellOrder)
            .where(StarsSellOrder.user_id == user_id)
            .order_by(desc(StarsSellOrder.created_at), desc(StarsSellOrder.id))
            .limit(limit)
        )
        return list(await self.session.scalars(query))

    async def count_by_user(self, *, user_id: int) -> int:
        query = select(func.count(StarsSellOrder.id)).where(StarsSellOrder.user_id == user_id)
        result = await self.session.scalar(query)
        return int(result or 0)

    async def list_by_user_page(
        self,
        *,
        user_id: int,
        limit: int,
        offset: int = 0,
    ) -> list[StarsSellOrder]:
        if limit <= 0:
            return []
        query: Select[tuple[StarsSellOrder]] = (
            select(StarsSellOrder)
            .where(StarsSellOrder.user_id == user_id)
            .order_by(desc(StarsSellOrder.created_at), desc(StarsSellOrder.id))
            .offset(max(offset, 0))
            .limit(limit)
        )
        return list(await self.session.scalars(query))

    async def get_by_user(self, *, user_id: int, order_id: int) -> Optional[StarsSellOrder]:
        return await self._get(
            StarsSellOrder,
            and_(StarsSellOrder.user_id == user_id, StarsSellOrder.id == order_id),
        )

    async def list_for_admin(
        self,
        *,
        limit: int,
        offset: int = 0,
        user_id: int | None = None,
        status: StarsSellOrderStatus | None = None,
        statuses: Sequence[StarsSellOrderStatus] | None = None,
        search: str | None = None,
    ) -> list[StarsSellOrder]:
        if limit <= 0:
            return []
        query: Select[tuple[StarsSellOrder]] = (
            select(StarsSellOrder)
            .order_by(desc(StarsSellOrder.created_at), desc(StarsSellOrder.id))
            .offset(max(offset, 0))
            .limit(limit)
        )
        query = self._apply_admin_filters(
            query,
            user_id=user_id,
            status=status,
            statuses=statuses,
            search=search,
        )
        return list(await self.session.scalars(query))

    async def sum_paid_stars(self) -> int:
        query = select(func.coalesce(func.sum(StarsSellOrder.paid_stars_amount), 0)).where(
            StarsSellOrder.paid_stars_amount.is_not(None)
        )
        result = await self.session.scalar(query)
        return int(result or 0)

    async def sum_completed_payout_cents(self) -> int:
        query = select(func.coalesce(func.sum(StarsSellOrder.payout_amount_cents), 0)).where(
            StarsSellOrder.status == StarsSellOrderStatus.COMPLETED.value
        )
        result = await self.session.scalar(query)
        return int(result or 0)

    async def count_ready_for_payout(self, *, now: datetime) -> int:
        query = select(func.count(StarsSellOrder.id)).where(
            and_(
                StarsSellOrder.status == StarsSellOrderStatus.PAID_HOLD.value,
                StarsSellOrder.payout_available_at.is_not(None),
                StarsSellOrder.payout_available_at <= now,
            )
        )
        result = await self.session.scalar(query)
        return int(result or 0)

    async def update(self, order_id: int, **data: Any) -> Optional[StarsSellOrder]:
        return await self._update(
            model=StarsSellOrder,
            conditions=[StarsSellOrder.id == order_id],
            load_result=True,
            **data,
        )

    async def update_if_status(
        self,
        *,
        order_id: int,
        current_statuses: Sequence[StarsSellOrderStatus],
        **data: Any,
    ) -> Optional[StarsSellOrder]:
        return await self._update(
            model=StarsSellOrder,
            conditions=[
                StarsSellOrder.id == order_id,
                StarsSellOrder.status.in_([status.value for status in current_statuses]),
            ],
            load_result=True,
            **data,
        )
