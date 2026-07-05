from __future__ import annotations

from typing import Any, Optional, cast

from sqlalchemy import Select, and_, desc, func, select

from app.enums.check import CheckStatus
from app.models.sql import UserCheck
from app.services.postgres.repositories.base import BaseRepository


class ChecksRepository(BaseRepository):
    async def get(self, check_id: int) -> Optional[UserCheck]:
        return await self._get(UserCheck, UserCheck.id == check_id)

    async def get_by_code(self, *, code: str) -> Optional[UserCheck]:
        return await self._get(UserCheck, UserCheck.code == code)

    async def get_by_code_for_update(self, *, code: str) -> Optional[UserCheck]:
        query: Select[tuple[UserCheck]] = (
            select(UserCheck).where(UserCheck.code == code).with_for_update()
        )
        return cast(Optional[UserCheck], await self.session.scalar(query))

    async def get_by_creator(self, *, creator_id: int, check_id: int) -> Optional[UserCheck]:
        return await self._get(
            UserCheck,
            UserCheck.id == check_id,
            UserCheck.creator_id == creator_id,
        )

    async def get_by_creator_for_update(
        self,
        *,
        creator_id: int,
        check_id: int,
    ) -> Optional[UserCheck]:
        query: Select[tuple[UserCheck]] = (
            select(UserCheck)
            .where(
                and_(
                    UserCheck.id == check_id,
                    UserCheck.creator_id == creator_id,
                )
            )
            .with_for_update()
        )
        return cast(Optional[UserCheck], await self.session.scalar(query))

    async def count_active_by_creator(self, *, creator_id: int) -> int:
        query = select(func.count(UserCheck.id)).where(
            and_(
                UserCheck.creator_id == creator_id,
                UserCheck.status == CheckStatus.ACTIVE.value,
            )
        )
        result = await self.session.scalar(query)
        return int(result or 0)

    async def count_by_creator(self, *, creator_id: int) -> int:
        query = select(func.count(UserCheck.id)).where(UserCheck.creator_id == creator_id)
        result = await self.session.scalar(query)
        return int(result or 0)

    async def list_active_by_creator_page(
        self,
        *,
        creator_id: int,
        limit: int,
        offset: int,
    ) -> list[UserCheck]:
        if limit <= 0:
            return []
        query: Select[tuple[UserCheck]] = (
            select(UserCheck)
            .where(
                and_(
                    UserCheck.creator_id == creator_id,
                    UserCheck.status == CheckStatus.ACTIVE.value,
                )
            )
            .order_by(desc(UserCheck.created_at))
            .offset(max(0, offset))
            .limit(limit)
        )
        return list(await self.session.scalars(query))

    async def list_by_creator_page(
        self,
        *,
        creator_id: int,
        limit: int,
        offset: int,
    ) -> list[UserCheck]:
        if limit <= 0:
            return []
        query: Select[tuple[UserCheck]] = (
            select(UserCheck)
            .where(UserCheck.creator_id == creator_id)
            .order_by(desc(UserCheck.created_at))
            .offset(max(0, offset))
            .limit(limit)
        )
        return list(await self.session.scalars(query))

    @staticmethod
    def _admin_conditions(
        *,
        creator_id: int | None,
        status: CheckStatus | None,
    ) -> list[Any]:
        conditions: list[Any] = []
        if creator_id is not None:
            conditions.append(UserCheck.creator_id == creator_id)
        if status is not None:
            conditions.append(UserCheck.status == status.value)
        return conditions

    async def count_for_admin(
        self,
        *,
        creator_id: int | None = None,
        status: CheckStatus | None = None,
    ) -> int:
        conditions = self._admin_conditions(creator_id=creator_id, status=status)
        query = select(func.count(UserCheck.id))
        if conditions:
            query = query.where(and_(*conditions))
        result = await self.session.scalar(query)
        return int(result or 0)

    async def list_for_admin(
        self,
        *,
        limit: int,
        offset: int,
        creator_id: int | None = None,
        status: CheckStatus | None = None,
    ) -> list[UserCheck]:
        if limit <= 0:
            return []
        conditions = self._admin_conditions(creator_id=creator_id, status=status)
        query: Select[tuple[UserCheck]] = select(UserCheck)
        if conditions:
            query = query.where(and_(*conditions))
        query = query.order_by(desc(UserCheck.created_at)).offset(max(0, offset)).limit(limit)
        return list(await self.session.scalars(query))

    async def update(self, check_id: int, **data: Any) -> Optional[UserCheck]:
        return await self._update(
            model=UserCheck,
            conditions=[UserCheck.id == check_id],
            load_result=True,
            **data,
        )
