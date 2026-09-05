import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from aiogram.types import User as AiogramUser
from aiogram_i18n.cores import BaseCore
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.const import DEFAULT_LOCALE, TIME_1M
from app.models.config import AppConfig
from app.models.dto.user import UserDto
from app.models.sql import User
from app.services.crud.base import CrudService
from app.services.postgres import SQLSessionContext
from app.services.promo_codes import PromoCodeInfo, PromoCodeService
from app.services.redis import redis_cache
from app.utils.key_builder import build_key

_REFERRAL_START_RE = re.compile(r"^ref_(\d{1,20})$")
_MAX_REFERRER_LOOKUP_DEPTH = 64


@dataclass(frozen=True, slots=True)
class ReferralMember:
    user_id: int
    name: str
    level: int
    joined_at: datetime


@dataclass(frozen=True, slots=True)
class ReferralOverview:
    referral_link: str
    referral_balance_cents: int
    referral_earned_cents: int
    level1_count: int
    level2_count: int
    level3_count: int
    referrals: list[ReferralMember]


class UserService(CrudService):
    class PromoCodeError(RuntimeError):
        pass

    class PromoCodeInvalidError(PromoCodeError):
        pass

    class PromoCodeAlreadyUsedError(PromoCodeError):
        pass

    class ReferralError(RuntimeError):
        pass

    def __init__(
        self,
        *,
        session_pool: async_sessionmaker[AsyncSession],
        redis: Redis,
        config: AppConfig,
        promo_code_service: PromoCodeService | None = None,
    ) -> None:
        super().__init__(session_pool=session_pool, redis=redis, config=config)
        self.promo_code_service = promo_code_service or PromoCodeService(
            session_pool=session_pool,
            redis=redis,
        )

    async def clear_cache(self, user_id: int) -> None:
        cache_key: str = build_key("cache", "get_user", user_id=user_id)
        await self.redis.delete(cache_key)

    async def create(self, aiogram_user: AiogramUser, i18n_core: BaseCore[Any]) -> UserDto:
        db_user: User = User(
            id=aiogram_user.id,
            name=aiogram_user.full_name,
            language=(
                aiogram_user.language_code
                if aiogram_user.language_code in i18n_core.available_locales
                else DEFAULT_LOCALE
            ),
            language_code=aiogram_user.language_code,
        )

        async with SQLSessionContext(session_pool=self.session_pool) as (repository, uow):
            await uow.commit(db_user)

        await self.clear_cache(user_id=aiogram_user.id)
        return db_user.dto()

    async def ensure_telegram_user(
        self,
        *,
        user_id: int,
        full_name: str,
        language_code: str | None,
    ) -> UserDto:
        if user_id <= 0:
            raise ValueError("user_id must be positive")

        normalized_name = full_name.strip() or f"user_{user_id}"
        normalized_language_code = (
            language_code.strip().lower() if isinstance(language_code, str) else None
        )
        available_locales = {locale.strip().lower() for locale in self.config.telegram.locales}
        selected_language = (
            normalized_language_code
            if normalized_language_code in available_locales
            else DEFAULT_LOCALE
        )

        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            session = repository.session
            user_db = await repository.users.get(user_id=user_id)
            if user_db is None:
                user_db = User(
                    id=user_id,
                    name=normalized_name,
                    language=selected_language,
                    language_code=normalized_language_code,
                )
                session.add(user_db)
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()
                    existing = await repository.users.get(user_id=user_id)
                    if existing is None:
                        raise
                    user_db = existing
                else:
                    await session.refresh(user_db)

            changed = False
            if user_db.name != normalized_name:
                user_db.name = normalized_name
                changed = True
            if user_db.language != selected_language:
                user_db.language = selected_language
                changed = True
            if user_db.language_code != normalized_language_code:
                user_db.language_code = normalized_language_code
                changed = True
            if changed:
                await session.commit()
                await session.refresh(user_db)

        await self.clear_cache(user_id=user_id)
        return user_db.dto()

    @redis_cache(prefix="get_user", ttl=TIME_1M)
    async def get(self, user_id: int) -> Optional[UserDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, uow):
            user = await repository.users.get(user_id=user_id)
            if user is None:
                return None
            return user.dto()

    async def count(self) -> int:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            return await repository.users.count()

    async def count_active(self, *, locales: list[str] | None = None) -> int:
        normalized_locales = self._normalize_locales(locales)
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            if normalized_locales is None:
                return await repository.users.count_active()
            return await repository.users.count_active_by_locales(locales=normalized_locales)

    async def count_with_positive_balance(self) -> int:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            return await repository.users.count_with_positive_balance()

    async def sum_balances_cents(self) -> int:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            return await repository.users.sum_balances_cents()

    async def list_user_ids(
        self,
        *,
        limit: int,
        offset: int = 0,
        after_id: int | None = None,
        only_active: bool = True,
    ) -> list[int]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            return await repository.users.list_ids(
                limit=limit,
                offset=offset,
                after_id=after_id,
                only_active=only_active,
            )

    async def list_recipients(
        self,
        *,
        limit: int,
        offset: int = 0,
        after_id: int | None = None,
        only_active: bool = True,
        locales: list[str] | None = None,
    ) -> list[tuple[int, str]]:
        normalized_locales = self._normalize_locales(locales)
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            return await repository.users.list_recipients(
                limit=limit,
                offset=offset,
                after_id=after_id,
                only_active=only_active,
                locales=normalized_locales,
            )

    async def list_admin_page(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        locale: str | None = None,
        include_blocked: bool = True,
    ) -> tuple[list[UserDto], bool, int]:
        safe_page = max(0, page)
        safe_page_size = max(1, page_size)
        safe_offset = safe_page * safe_page_size
        locale_filter: str | None = None
        if locale is not None:
            normalized_locale = locale.strip().lower()
            available_locales = {item.strip().lower() for item in self.config.telegram.locales}
            if normalized_locale in available_locales:
                locale_filter = normalized_locale

        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            total_count = await repository.users.count_for_admin(
                search=search,
                locale=locale_filter,
                include_blocked=include_blocked,
            )
            users = await repository.users.list_for_admin(
                limit=safe_page_size + 1,
                offset=safe_offset,
                search=search,
                locale=locale_filter,
                include_blocked=include_blocked,
            )

        total_pages = max(1, (total_count + safe_page_size - 1) // safe_page_size)
        has_next = safe_page + 1 < total_pages
        page_users = users[:safe_page_size]
        return [item.dto() for item in page_users], has_next, total_pages

    async def update(self, user: UserDto, **data: Any) -> Optional[UserDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, uow):
            for key, value in data.items():
                setattr(user, key, value)
            await self.clear_cache(user_id=user.id)
            user_db = await repository.users.update(user_id=user.id, **user.model_state)
            if user_db is None:
                return None
            return user_db.dto()

    async def set_blocked_at(
        self,
        *,
        user_id: int,
        blocked_at: datetime | None,
    ) -> Optional[UserDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            user_db = await repository.users.set_blocked_at(
                user_id=user_id,
                blocked_at=blocked_at,
            )
            if user_db is None:
                return None
        await self.clear_cache(user_id=user_id)
        return user_db.dto()

    async def add_balance(self, *, user_id: int, amount_cents: int) -> Optional[UserDto]:
        if amount_cents < 0:
            raise ValueError("amount_cents must be non-negative")
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            user_db = await repository.users.add_balance(
                user_id=user_id,
                amount_cents=amount_cents,
            )
            if user_db is None:
                return None
        await self.clear_cache(user_id=user_id)
        return user_db.dto()

    async def subtract_balance_clamped(
        self,
        *,
        user_id: int,
        amount_cents: int,
    ) -> Optional[UserDto]:
        if amount_cents < 0:
            raise ValueError("amount_cents must be non-negative")
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            user_db = await repository.users.subtract_balance_clamped(
                user_id=user_id,
                amount_cents=amount_cents,
            )
            if user_db is None:
                return None
        await self.clear_cache(user_id=user_id)
        return user_db.dto()

    async def set_balance(self, *, user_id: int, balance_cents: int) -> Optional[UserDto]:
        if balance_cents < 0:
            raise ValueError("balance_cents must be non-negative")
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            user_db = await repository.users.set_balance(
                user_id=user_id,
                balance_cents=balance_cents,
            )
            if user_db is None:
                return None
        await self.clear_cache(user_id=user_id)
        return user_db.dto()

    async def debit_balance_if_enough(
        self,
        *,
        user_id: int,
        amount_cents: int,
    ) -> Optional[UserDto]:
        if amount_cents < 0:
            raise ValueError("amount_cents must be non-negative")
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            user_db = await repository.users.debit_balance_if_enough(
                user_id=user_id,
                amount_cents=amount_cents,
            )
            if user_db is None:
                return None
        await self.clear_cache(user_id=user_id)
        return user_db.dto()

    def _normalize_locales(self, locales: list[str] | None) -> list[str] | None:
        if locales is None:
            return None
        available = {locale.strip().lower() for locale in self.config.telegram.locales}
        normalized: list[str] = []
        seen: set[str] = set()
        for locale in locales:
            key = locale.strip().lower()
            if not key or key in seen or key not in available:
                continue
            seen.add(key)
            normalized.append(key)
        return normalized or []

    async def activate_promo_code(self, *, user_id: int, code: str) -> int:
        try:
            normalized = self.promo_code_service.normalize_code(code)
        except PromoCodeService.InvalidCodeError as error:
            raise self.PromoCodeInvalidError("Promo code is invalid.") from error

        try:
            amount_cents = await self.promo_code_service.activate_code(
                user_id=user_id,
                code=normalized,
            )
        except PromoCodeService.AlreadyUsedError as error:
            raise self.PromoCodeAlreadyUsedError("Promo code is already used.") from error
        except (
            PromoCodeService.CodeNotFoundError,
            PromoCodeService.LimitReachedError,
            PromoCodeService.DisabledError,
            PromoCodeService.InvalidCodeError,
        ) as error:
            raise self.PromoCodeInvalidError("Promo code is invalid.") from error
        except PromoCodeService.Error as error:
            raise self.PromoCodeError("Failed to activate promo code.") from error

        await self.clear_cache(user_id=user_id)
        return amount_cents

    async def list_promo_codes(self, *, limit: int = 12) -> list[PromoCodeInfo]:
        return await self.promo_code_service.list_codes(limit=limit)

    @staticmethod
    def build_referral_start_payload(*, user_id: int) -> str:
        return f"ref_{user_id}"

    @staticmethod
    def parse_referral_start_payload(payload: str) -> int | None:
        match = _REFERRAL_START_RE.fullmatch(payload.strip())
        if match is None:
            return None
        value = int(match.group(1))
        return value if value > 0 else None

    async def try_bind_referrer_from_start_payload(
        self,
        *,
        user_id: int,
        payload: str,
    ) -> bool:
        referrer_id = self.parse_referral_start_payload(payload)
        if referrer_id is None:
            return False
        return await self.try_bind_referrer(user_id=user_id, referrer_id=referrer_id)

    async def try_bind_referrer(self, *, user_id: int, referrer_id: int) -> bool:
        if user_id <= 0 or referrer_id <= 0 or user_id == referrer_id:
            return False

        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            user = await repository.users.get(user_id=user_id)
            referrer = await repository.users.get(user_id=referrer_id)
            if user is None or referrer is None:
                return False
            if user.referrer_id is not None:
                return False

            # Prevent referral loops for users that already have descendants.
            cursor_id = referrer_id
            depth = 0
            while depth < _MAX_REFERRER_LOOKUP_DEPTH:
                current = await repository.users.get(user_id=cursor_id)
                if current is None or current.referrer_id is None:
                    break
                if current.referrer_id == user_id:
                    return False
                if current.referrer_id == cursor_id:
                    break
                cursor_id = int(current.referrer_id)
                depth += 1

            bound = await repository.users.bind_referrer_if_empty(
                user_id=user_id,
                referrer_id=referrer_id,
            )
            if not bound:
                return False

        await self.clear_cache(user_id=user_id)
        return True

    async def referral_overview(
        self,
        *,
        user_id: int,
        bot_username: str,
        referrals_limit: int = 120,
    ) -> Optional[ReferralOverview]:
        user = await self.get(user_id=user_id)
        if user is None:
            return None

        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            level_counts = await repository.users.count_referrals_by_level(referrer_id=user_id)
            tree_rows = await repository.users.list_referral_tree(
                referrer_id=user_id,
                max_depth=3,
                limit=max(1, referrals_limit),
            )

        members = [
            ReferralMember(
                user_id=row_user_id,
                name=row_name,
                level=row_level,
                joined_at=row_joined_at,
            )
            for row_user_id, row_name, row_level, row_joined_at in tree_rows
        ]
        return ReferralOverview(
            referral_link=(
                f"https://t.me/{bot_username}"
                f"?start={self.build_referral_start_payload(user_id=user_id)}"
            ),
            referral_balance_cents=user.referral_balance_cents,
            referral_earned_cents=user.referral_earned_cents,
            level1_count=int(level_counts.get(1, 0)),
            level2_count=int(level_counts.get(2, 0)),
            level3_count=int(level_counts.get(3, 0)),
            referrals=members,
        )

    async def withdraw_referral_balance_to_main(
        self,
        *,
        user_id: int,
        amount_cents: int | None = None,
    ) -> int:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            amount_cents = await repository.users.withdraw_referral_balance_to_main(
                user_id=user_id,
                amount_cents=amount_cents,
            )
        await self.clear_cache(user_id=user_id)
        return amount_cents
