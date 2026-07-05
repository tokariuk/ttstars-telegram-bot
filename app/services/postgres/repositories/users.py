from datetime import datetime
from typing import Any, Optional, cast

from sqlalchemy import Integer, and_, func, literal, or_, select, update
from sqlalchemy.sql.functions import count

from app.models.sql import User
from app.services.postgres.repositories.base import BaseRepository


# noinspection PyTypeChecker
class UsersRepository(BaseRepository):
    @staticmethod
    def _apply_admin_filters(
        query: Any,
        *,
        search: str | None,
        locale: str | None,
        include_blocked: bool,
    ) -> Any:
        if not include_blocked:
            query = query.where(User.blocked_at.is_(None))
        if locale is not None:
            normalized_locale = locale.strip().lower()
            if normalized_locale:
                query = query.where(User.language == normalized_locale)

        normalized_search = (search or "").strip()
        if normalized_search:
            conditions: list[Any] = [User.name.ilike(f"%{normalized_search}%")]
            if normalized_search.isdigit():
                conditions.append(User.id == int(normalized_search))
            query = query.where(or_(*conditions))
        return query

    async def get(self, user_id: int) -> Optional[User]:
        return await self._get(User, User.id == user_id)

    async def update(self, user_id: int, **data: Any) -> Optional[User]:
        return await self._update(
            model=User,
            conditions=[User.id == user_id],
            load_result=True,
            **data,
        )

    async def count(self) -> int:
        return cast(int, await self.session.scalar(select(count(User.id))))

    async def count_for_admin(
        self,
        *,
        search: str | None = None,
        locale: str | None = None,
        include_blocked: bool = True,
    ) -> int:
        query = select(count(User.id))
        query = self._apply_admin_filters(
            query,
            search=search,
            locale=locale,
            include_blocked=include_blocked,
        )
        return cast(int, await self.session.scalar(query))

    async def count_active(self) -> int:
        query = select(count(User.id)).where(User.blocked_at.is_(None))
        return cast(int, await self.session.scalar(query))

    async def count_active_by_locales(self, *, locales: list[str] | None) -> int:
        query = select(count(User.id)).where(User.blocked_at.is_(None))
        if locales:
            query = query.where(User.language.in_(locales))
        return cast(int, await self.session.scalar(query))

    async def count_with_positive_balance(self) -> int:
        query = select(count(User.id)).where(User.balance_cents > 0)
        return cast(int, await self.session.scalar(query))

    async def sum_balances_cents(self) -> int:
        query = select(func.coalesce(func.sum(User.balance_cents), 0))
        result = await self.session.scalar(query)
        return int(result or 0)

    async def list_ids(
        self,
        *,
        limit: int,
        offset: int = 0,
        after_id: int | None = None,
        only_active: bool = True,
    ) -> list[int]:
        if limit <= 0:
            return []
        query = select(User.id).order_by(User.id.asc()).offset(max(offset, 0)).limit(limit)
        if only_active:
            query = query.where(User.blocked_at.is_(None))
        if after_id is not None:
            query = query.where(User.id > after_id)
        ids = await self.session.scalars(query)
        return [int(user_id) for user_id in ids]

    async def list_for_admin(
        self,
        *,
        limit: int,
        offset: int = 0,
        search: str | None = None,
        locale: str | None = None,
        include_blocked: bool = True,
    ) -> list[User]:
        if limit <= 0:
            return []
        query = (
            select(User)
            .order_by(User.id.asc())
            .offset(max(offset, 0))
            .limit(limit)
        )
        query = self._apply_admin_filters(
            query,
            search=search,
            locale=locale,
            include_blocked=include_blocked,
        )
        return list(await self.session.scalars(query))

    async def list_recipients(
        self,
        *,
        limit: int,
        offset: int = 0,
        after_id: int | None = None,
        only_active: bool = True,
        locales: list[str] | None = None,
    ) -> list[tuple[int, str]]:
        if limit <= 0:
            return []
        query = (
            select(User.id, User.language)
            .order_by(User.id.asc())
            .offset(max(offset, 0))
            .limit(limit)
        )
        if only_active:
            query = query.where(User.blocked_at.is_(None))
        if after_id is not None:
            query = query.where(User.id > after_id)
        if locales:
            query = query.where(User.language.in_(locales))
        rows = (await self.session.execute(query)).all()
        return [(int(user_id), str(language or "en")) for user_id, language in rows]

    async def set_blocked_at(self, *, user_id: int, blocked_at: datetime | None) -> Optional[User]:
        query = (
            update(User)
            .where(User.id == user_id)
            .values(blocked_at=blocked_at)
            .returning(User)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return cast(Optional[User], result.scalar_one_or_none())

    async def add_balance(self, *, user_id: int, amount_cents: int) -> Optional[User]:
        if amount_cents <= 0:
            return await self.get(user_id=user_id)
        query = (
            update(User)
            .where(User.id == user_id)
            .values(balance_cents=User.balance_cents + amount_cents)
            .returning(User)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return cast(Optional[User], result.scalar_one_or_none())

    async def subtract_balance_clamped(self, *, user_id: int, amount_cents: int) -> Optional[User]:
        if amount_cents <= 0:
            return await self.get(user_id=user_id)
        query = (
            update(User)
            .where(User.id == user_id)
            .values(balance_cents=func.greatest(User.balance_cents - amount_cents, 0))
            .returning(User)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return cast(Optional[User], result.scalar_one_or_none())

    async def set_balance(self, *, user_id: int, balance_cents: int) -> Optional[User]:
        if balance_cents < 0:
            balance_cents = 0
        query = (
            update(User)
            .where(User.id == user_id)
            .values(balance_cents=balance_cents)
            .returning(User)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return cast(Optional[User], result.scalar_one_or_none())

    async def add_referral_reward(self, *, user_id: int, amount_cents: int) -> Optional[User]:
        if amount_cents <= 0:
            return await self.get(user_id=user_id)
        query = (
            update(User)
            .where(User.id == user_id)
            .values(
                referral_balance_cents=User.referral_balance_cents + amount_cents,
                referral_earned_cents=User.referral_earned_cents + amount_cents,
            )
            .returning(User)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return cast(Optional[User], result.scalar_one_or_none())

    async def bind_referrer_if_empty(self, *, user_id: int, referrer_id: int) -> bool:
        if user_id <= 0 or referrer_id <= 0 or user_id == referrer_id:
            return False
        query = (
            update(User)
            .where(
                and_(
                    User.id == user_id,
                    User.referrer_id.is_(None),
                )
            )
            .values(referrer_id=referrer_id)
            .returning(User.id)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none() is not None

    async def withdraw_referral_balance_to_main(
        self,
        *,
        user_id: int,
        amount_cents: int | None = None,
    ) -> int:
        user = cast(
            Optional[User],
            await self.session.scalar(
                select(User).where(User.id == user_id).with_for_update()
            ),
        )
        if user is None:
            return 0
        available_cents = int(user.referral_balance_cents)
        if available_cents <= 0:
            return 0
        if amount_cents is None:
            transfer_cents = available_cents
        else:
            transfer_cents = int(amount_cents)
            if transfer_cents <= 0:
                return 0
            if transfer_cents > available_cents:
                return 0
        user.referral_balance_cents = available_cents - transfer_cents
        user.balance_cents = int(user.balance_cents) + transfer_cents
        await self.session.commit()
        return transfer_cents

    async def list_referral_tree(
        self,
        *,
        referrer_id: int,
        max_depth: int = 3,
        limit: int = 200,
    ) -> list[tuple[int, str, int, datetime]]:
        if referrer_id <= 0 or max_depth <= 0 or limit <= 0:
            return []

        base = select(
            User.id.label("user_id"),
            User.name.label("name"),
            User.created_at.label("created_at"),
            literal(1, type_=Integer).label("level"),
        ).where(User.referrer_id == referrer_id)

        tree = base.cte(name="ref_tree", recursive=True)
        next_level = select(
            User.id.label("user_id"),
            User.name.label("name"),
            User.created_at.label("created_at"),
            (tree.c.level + 1).label("level"),
        ).where(
            and_(
                User.referrer_id == tree.c.user_id,
                tree.c.level < max_depth,
            )
        )
        tree = tree.union_all(next_level)

        query = (
            select(tree.c.user_id, tree.c.name, tree.c.level, tree.c.created_at)
            .order_by(tree.c.level.asc(), tree.c.created_at.desc(), tree.c.user_id.asc())
            .limit(limit)
        )
        rows = (await self.session.execute(query)).all()
        return [
            (int(user_id), str(name), int(level), created_at)
            for user_id, name, level, created_at in rows
        ]

    async def count_referrals_by_level(
        self,
        *,
        referrer_id: int,
        max_depth: int = 3,
    ) -> dict[int, int]:
        if referrer_id <= 0 or max_depth <= 0:
            return {}

        base = select(
            User.id.label("user_id"),
            literal(1, type_=Integer).label("level"),
        ).where(User.referrer_id == referrer_id)

        tree = base.cte(name="ref_count_tree", recursive=True)
        next_level = select(
            User.id.label("user_id"),
            (tree.c.level + 1).label("level"),
        ).where(
            and_(
                User.referrer_id == tree.c.user_id,
                tree.c.level < max_depth,
            )
        )
        tree = tree.union_all(next_level)

        query = select(tree.c.level, func.count()).group_by(tree.c.level)
        rows = (await self.session.execute(query)).all()
        return {int(level): int(total) for level, total in rows}

    async def debit_balance_if_enough(
        self,
        *,
        user_id: int,
        amount_cents: int,
    ) -> Optional[User]:
        if amount_cents <= 0:
            return await self.get(user_id=user_id)
        query = (
            update(User)
            .where(
                and_(
                    User.id == user_id,
                    User.balance_cents >= amount_cents,
                )
            )
            .values(balance_cents=User.balance_cents - amount_cents)
            .returning(User)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return cast(Optional[User], result.scalar_one_or_none())
