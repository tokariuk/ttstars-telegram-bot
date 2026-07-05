from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any, Optional, cast

from sqlalchemy import Select, and_, desc, func, or_, select

from app.enums.stars_order import StarsOrderProductType, StarsOrderStatus, StarsPaymentProvider
from app.models.sql.balance_topup import BalanceTopup
from app.services.postgres.repositories.base import BaseRepository


class BalanceTopupsRepository(BaseRepository):
    @staticmethod
    def _visibility_condition(*, include_linked: bool) -> Any:
        if include_linked:
            return None
        return BalanceTopup.linked_order_id.is_(None)

    @staticmethod
    def _apply_filters(
        query: Any,
        *,
        user_id: int | None,
        status: StarsOrderStatus | None,
        provider: StarsPaymentProvider | None,
        allowed_providers: Sequence[StarsPaymentProvider] | None,
        product_type: StarsOrderProductType | None,
        search: str | None,
        include_linked: bool,
    ) -> Any:
        visibility_condition = BalanceTopupsRepository._visibility_condition(
            include_linked=include_linked
        )
        if visibility_condition is not None:
            query = query.where(visibility_condition)

        if user_id is not None and user_id > 0:
            query = query.where(BalanceTopup.user_id == user_id)
        if status is not None:
            query = query.where(BalanceTopup.status == status.value)
        if provider is not None:
            query = query.where(BalanceTopup.payment_provider == provider.value)
        elif allowed_providers:
            query = query.where(
                BalanceTopup.payment_provider.in_([item.value for item in allowed_providers])
            )
        if product_type is not None:
            if product_type == StarsOrderProductType.TOPUP:
                query = query.where(BalanceTopup.auto_product_type.is_(None))
            else:
                query = query.where(BalanceTopup.auto_product_type == product_type.value)

        normalized_search = (search or "").strip()
        if normalized_search:
            conditions: list[Any] = [
                BalanceTopup.provider_reference.ilike(f"%{normalized_search}%"),
                BalanceTopup.payment_payload.ilike(f"%{normalized_search}%"),
                BalanceTopup.auto_recipient_username.ilike(f"%{normalized_search}%"),
            ]
            if normalized_search.isdigit():
                numeric = int(normalized_search)
                conditions.extend(
                    [
                        BalanceTopup.id == numeric,
                        BalanceTopup.user_id == numeric,
                        BalanceTopup.provider_invoice_id == numeric,
                        BalanceTopup.linked_order_id == numeric,
                    ]
                )
            query = query.where(or_(*conditions))
        return query

    async def count(self) -> int:
        result = await self.session.scalar(select(func.count(BalanceTopup.id)))
        return int(result or 0)

    async def count_created_since(self, *, since: datetime, include_linked: bool = True) -> int:
        query = select(func.count(BalanceTopup.id)).where(BalanceTopup.created_at >= since)
        visibility_condition = self._visibility_condition(include_linked=include_linked)
        if visibility_condition is not None:
            query = query.where(visibility_condition)
        result = await self.session.scalar(query)
        return int(result or 0)

    async def count_paid_since(self, *, since: datetime, include_linked: bool = True) -> int:
        query = select(func.count(BalanceTopup.id)).where(
            and_(
                BalanceTopup.paid_at.is_not(None),
                BalanceTopup.paid_at >= since,
            )
        )
        visibility_condition = self._visibility_condition(include_linked=include_linked)
        if visibility_condition is not None:
            query = query.where(visibility_condition)
        result = await self.session.scalar(query)
        return int(result or 0)

    async def sum_paid_amount_since(self, *, since: datetime, include_linked: bool = True) -> int:
        query = select(func.coalesce(func.sum(BalanceTopup.amount_cents), 0)).where(
            and_(
                BalanceTopup.paid_at.is_not(None),
                BalanceTopup.paid_at >= since,
            )
        )
        visibility_condition = self._visibility_condition(include_linked=include_linked)
        if visibility_condition is not None:
            query = query.where(visibility_condition)
        result = await self.session.scalar(query)
        return int(result or 0)

    async def sum_completed_amount(self, *, include_linked: bool = True) -> int:
        query = select(func.coalesce(func.sum(BalanceTopup.amount_cents), 0)).where(
            BalanceTopup.status == StarsOrderStatus.COMPLETED.value
        )
        visibility_condition = self._visibility_condition(include_linked=include_linked)
        if visibility_condition is not None:
            query = query.where(visibility_condition)
        result = await self.session.scalar(query)
        return int(result or 0)

    async def count_completed(self, *, include_linked: bool = True) -> int:
        query = select(func.count(BalanceTopup.id)).where(
            BalanceTopup.status == StarsOrderStatus.COMPLETED.value
        )
        visibility_condition = self._visibility_condition(include_linked=include_linked)
        if visibility_condition is not None:
            query = query.where(visibility_condition)
        result = await self.session.scalar(query)
        return int(result or 0)

    async def count_by_status(self, *, include_linked: bool = True) -> dict[str, int]:
        query = select(BalanceTopup.status, func.count(BalanceTopup.id)).group_by(
            BalanceTopup.status
        )
        visibility_condition = self._visibility_condition(include_linked=include_linked)
        if visibility_condition is not None:
            query = query.where(visibility_condition)
        rows = (await self.session.execute(query)).all()
        return {str(status): int(total) for status, total in rows}

    async def count_by_user(self, *, user_id: int, include_linked: bool = True) -> int:
        query = select(func.count(BalanceTopup.id)).where(BalanceTopup.user_id == user_id)
        visibility_condition = self._visibility_condition(include_linked=include_linked)
        if visibility_condition is not None:
            query = query.where(visibility_condition)
        result = await self.session.scalar(query)
        return int(result or 0)

    async def get(self, *, topup_id: int) -> Optional[BalanceTopup]:
        return await self._get(BalanceTopup, BalanceTopup.id == topup_id)

    async def get_by_user(self, *, user_id: int, topup_id: int) -> Optional[BalanceTopup]:
        return await self._get(
            BalanceTopup,
            BalanceTopup.user_id == user_id,
            BalanceTopup.id == topup_id,
        )

    async def get_open_for_user(self, *, user_id: int) -> Optional[BalanceTopup]:
        open_statuses = (
            StarsOrderStatus.CREATING_PAYMENT.value,
            StarsOrderStatus.PENDING_PAYMENT.value,
            StarsOrderStatus.PAYMENT_CONFIRMED.value,
            StarsOrderStatus.FULFILLING.value,
        )
        query: Select[tuple[BalanceTopup]] = (
            select(BalanceTopup)
            .where(
                and_(
                    BalanceTopup.user_id == user_id,
                    BalanceTopup.status.in_(open_statuses),
                )
            )
            .order_by(desc(BalanceTopup.created_at))
            .limit(1)
        )
        return cast(Optional[BalanceTopup], await self.session.scalar(query))

    async def get_by_provider_invoice(
        self,
        *,
        provider: StarsPaymentProvider,
        provider_invoice_id: int,
    ) -> Optional[BalanceTopup]:
        return await self._get(
            BalanceTopup,
            BalanceTopup.payment_provider == provider.value,
            BalanceTopup.provider_invoice_id == provider_invoice_id,
        )

    async def get_by_provider_payload(
        self,
        *,
        provider: StarsPaymentProvider,
        payment_payload: str,
    ) -> Optional[BalanceTopup]:
        return await self._get(
            BalanceTopup,
            BalanceTopup.payment_provider == provider.value,
            BalanceTopup.payment_payload == payment_payload,
        )

    async def get_by_provider_reference(
        self,
        *,
        provider: StarsPaymentProvider,
        provider_reference: str,
    ) -> Optional[BalanceTopup]:
        return await self._get(
            BalanceTopup,
            BalanceTopup.payment_provider == provider.value,
            BalanceTopup.provider_reference == provider_reference,
        )

    async def list_pending_for_polling(
        self,
        *,
        limit: int,
        provider: StarsPaymentProvider | None = None,
    ) -> list[BalanceTopup]:
        if limit <= 0:
            return []
        statuses = (
            StarsOrderStatus.CREATING_PAYMENT.value,
            StarsOrderStatus.PENDING_PAYMENT.value,
            StarsOrderStatus.PAYMENT_CONFIRMED.value,
            StarsOrderStatus.FULFILLING.value,
        )
        query: Select[tuple[BalanceTopup]] = select(BalanceTopup).where(
            BalanceTopup.status.in_(statuses)
        )
        if provider is not None:
            query = query.where(BalanceTopup.payment_provider == provider.value)
        query = query.order_by(BalanceTopup.created_at.asc()).limit(limit)
        return list(await self.session.scalars(query))

    async def list_recent_by_user(
        self,
        *,
        user_id: int,
        limit: int,
        include_linked: bool = True,
    ) -> list[BalanceTopup]:
        if limit <= 0:
            return []
        query: Select[tuple[BalanceTopup]] = select(BalanceTopup).where(
            BalanceTopup.user_id == user_id
        )
        visibility_condition = self._visibility_condition(include_linked=include_linked)
        if visibility_condition is not None:
            query = query.where(visibility_condition)
        query = query.order_by(desc(BalanceTopup.created_at)).limit(limit)
        return list(await self.session.scalars(query))

    async def list_recent_by_user_page(
        self,
        *,
        user_id: int,
        limit: int,
        offset: int,
        include_linked: bool = True,
    ) -> list[BalanceTopup]:
        if limit <= 0:
            return []
        query: Select[tuple[BalanceTopup]] = select(BalanceTopup).where(
            BalanceTopup.user_id == user_id
        )
        visibility_condition = self._visibility_condition(include_linked=include_linked)
        if visibility_condition is not None:
            query = query.where(visibility_condition)
        query = query.order_by(desc(BalanceTopup.created_at)).offset(max(offset, 0)).limit(limit)
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
        include_linked: bool = True,
    ) -> list[BalanceTopup]:
        if limit <= 0:
            return []
        query: Select[tuple[BalanceTopup]] = (
            select(BalanceTopup)
            .order_by(desc(BalanceTopup.created_at), desc(BalanceTopup.id))
            .offset(max(offset, 0))
            .limit(limit)
        )
        query = self._apply_filters(
            query,
            user_id=user_id,
            status=status,
            provider=provider,
            allowed_providers=allowed_providers,
            product_type=product_type,
            search=search,
            include_linked=include_linked,
        )
        return list(await self.session.scalars(query))

    async def count_for_admin(
        self,
        *,
        user_id: int | None = None,
        status: StarsOrderStatus | None = None,
        provider: StarsPaymentProvider | None = None,
        allowed_providers: Sequence[StarsPaymentProvider] | None = None,
        product_type: StarsOrderProductType | None = None,
        search: str | None = None,
        include_linked: bool = True,
    ) -> int:
        query = select(func.count(BalanceTopup.id))
        query = self._apply_filters(
            query,
            user_id=user_id,
            status=status,
            provider=provider,
            allowed_providers=allowed_providers,
            product_type=product_type,
            search=search,
            include_linked=include_linked,
        )
        result = await self.session.scalar(query)
        return int(result or 0)

    async def update(self, *, topup_id: int, **data: Any) -> Optional[BalanceTopup]:
        return await self._update(
            model=BalanceTopup,
            conditions=[BalanceTopup.id == topup_id],
            load_result=True,
            **data,
        )

    async def update_if_status(
        self,
        *,
        topup_id: int,
        current_statuses: list[StarsOrderStatus],
        **data: Any,
    ) -> Optional[BalanceTopup]:
        return await self._update(
            model=BalanceTopup,
            conditions=[
                BalanceTopup.id == topup_id,
                BalanceTopup.status.in_([status.value for status in current_statuses]),
            ],
            load_result=True,
            **data,
        )
