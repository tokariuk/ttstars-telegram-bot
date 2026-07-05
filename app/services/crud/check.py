from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional
from uuid import uuid4

from redis.asyncio import Redis
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.enums.check import CheckStatus
from app.models.config import AppConfig
from app.models.dto.check import CheckDto
from app.models.sql import User, UserCheck
from app.services.crud.base import CrudService
from app.services.fragment_stars import FragmentStarsService
from app.services.postgres import SQLSessionContext
from app.stars import get_stars_pack, normalize_recipient_username
from app.utils.key_builder import build_key
from app.utils.time import datetime_now

_CODE_RE = re.compile(r"^[a-f0-9]{16}$")
_START_RE = re.compile(r"^check_([a-f0-9]{16})$")
_MAX_CODE_GENERATION_ATTEMPTS = 20
_MAX_PASSWORD_LEN = 64


class CheckServiceError(RuntimeError):
    pass


class ValidationError(CheckServiceError):
    pass


class InsufficientBalanceError(CheckServiceError):
    pass


class CheckClaimOutcome(StrEnum):
    CLAIMED = "claimed"
    NOT_FOUND = "not_found"
    ALREADY_REDEEMED = "already_redeemed"
    ALREADY_CLOSED = "already_closed"
    PROCESSING = "processing"
    USERNAME_REQUIRED = "username_required"
    RECIPIENT_MISMATCH = "recipient_mismatch"
    PASSWORD_REQUIRED = "password_required"
    PASSWORD_INVALID = "password_invalid"
    DELIVERY_UNAVAILABLE = "delivery_unavailable"
    DELIVERY_FAILED = "delivery_failed"


class CheckCloseOutcome(StrEnum):
    CLOSED = "closed"
    NOT_FOUND = "not_found"
    ALREADY_REDEEMED = "already_redeemed"
    ALREADY_CLOSED = "already_closed"
    PROCESSING = "processing"


@dataclass(frozen=True, slots=True)
class CheckClaimResult:
    outcome: CheckClaimOutcome
    check: Optional[CheckDto] = None
    tx_hash: Optional[str] = None
    error: Optional[str] = None


@dataclass(frozen=True, slots=True)
class CheckCloseResult:
    outcome: CheckCloseOutcome
    check: Optional[CheckDto] = None


class CheckService(CrudService):
    def __init__(
        self,
        *,
        session_pool: async_sessionmaker[AsyncSession],
        redis: Redis,
        config: AppConfig,
        fragment_stars_service: FragmentStarsService,
    ) -> None:
        super().__init__(session_pool=session_pool, redis=redis, config=config)
        self.fragment_stars_service = fragment_stars_service

    @staticmethod
    def build_start_payload(*, code: str) -> str:
        return f"check_{code}"

    @classmethod
    def parse_start_payload(cls, payload: str) -> str | None:
        match = _START_RE.fullmatch(payload.strip())
        if match is None:
            return None
        return match.group(1)

    @classmethod
    def is_valid_code(cls, code: str) -> bool:
        return _CODE_RE.fullmatch(code.strip()) is not None

    @staticmethod
    def build_start_link(*, bot_username: str, code: str) -> str:
        username = bot_username.lstrip("@")
        return f"https://t.me/{username}?start=check_{code}"

    async def get(self, check_id: int) -> Optional[CheckDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            check = await repository.checks.get(check_id=check_id)
            if check is None:
                return None
            return check.dto()

    async def get_by_code(self, *, code: str) -> Optional[CheckDto]:
        normalized_code = code.strip().lower()
        if not self.is_valid_code(normalized_code):
            return None
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            check = await repository.checks.get_by_code(code=normalized_code)
            if check is None:
                return None
            return check.dto()

    async def list_active_page(
        self,
        *,
        creator_id: int,
        page: int,
        page_size: int,
    ) -> tuple[list[CheckDto], bool, int]:
        safe_page = max(0, page)
        safe_page_size = max(1, page_size)
        offset = safe_page * safe_page_size

        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            total_count = await repository.checks.count_active_by_creator(creator_id=creator_id)
            checks = await repository.checks.list_active_by_creator_page(
                creator_id=creator_id,
                limit=safe_page_size + 1,
                offset=offset,
            )
        total_pages = max(1, (total_count + safe_page_size - 1) // safe_page_size)
        has_next = safe_page + 1 < total_pages
        page_checks = checks[:safe_page_size]
        return [check.dto() for check in page_checks], has_next, total_pages

    async def list_recent_page(
        self,
        *,
        creator_id: int,
        page: int,
        page_size: int,
    ) -> tuple[list[CheckDto], bool, int]:
        safe_page = max(0, page)
        safe_page_size = max(1, page_size)
        offset = safe_page * safe_page_size

        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            total_count = await repository.checks.count_by_creator(creator_id=creator_id)
            checks = await repository.checks.list_by_creator_page(
                creator_id=creator_id,
                limit=safe_page_size + 1,
                offset=offset,
            )
        total_pages = max(1, (total_count + safe_page_size - 1) // safe_page_size)
        has_next = safe_page + 1 < total_pages
        page_checks = checks[:safe_page_size]
        return [check.dto() for check in page_checks], has_next, total_pages

    async def list_admin_page(
        self,
        *,
        page: int,
        page_size: int,
        creator_id: int | None = None,
        status: CheckStatus | None = None,
    ) -> tuple[list[CheckDto], bool, int]:
        safe_page = max(0, page)
        safe_page_size = max(1, page_size)
        offset = safe_page * safe_page_size

        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            total_count = await repository.checks.count_for_admin(
                creator_id=creator_id,
                status=status,
            )
            checks = await repository.checks.list_for_admin(
                limit=safe_page_size + 1,
                offset=offset,
                creator_id=creator_id,
                status=status,
            )
        total_pages = max(1, (total_count + safe_page_size - 1) // safe_page_size)
        has_next = safe_page + 1 < total_pages
        page_checks = checks[:safe_page_size]
        return [check.dto() for check in page_checks], has_next, total_pages

    async def get_creator_check(self, *, creator_id: int, check_id: int) -> Optional[CheckDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            check = await repository.checks.get_by_creator(
                creator_id=creator_id,
                check_id=check_id,
            )
            if check is None:
                return None
            return check.dto()

    async def create_stars_check(
        self,
        *,
        creator_id: int,
        stars_count: int,
        claim_username: str | None = None,
        claim_password: str | None = None,
        inline_message_id: str | None = None,
    ) -> CheckDto:
        try:
            pack = get_stars_pack(str(stars_count))
        except ValueError as error:
            raise ValidationError("Invalid stars amount for check.") from error
        return await self._create_check(
            creator_id=creator_id,
            stars_count=pack.stars_count,
            amount_cents=pack.price_cents,
            claim_username=claim_username,
            claim_password=claim_password,
            inline_message_id=inline_message_id,
        )

    async def _create_check(
        self,
        *,
        creator_id: int,
        stars_count: int,
        amount_cents: int,
        claim_username: str | None,
        claim_password: str | None,
        inline_message_id: str | None,
    ) -> CheckDto:
        if creator_id <= 0:
            raise ValidationError("Invalid creator id.")
        normalized_claim_username = self._normalize_claim_username(claim_username)
        claim_password_hash = self._normalize_and_hash_password(claim_password)
        generated_code = await self._generate_unique_code()

        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            session = repository.session
            creator = await session.scalar(
                select(User).where(User.id == creator_id).with_for_update()
            )
            if creator is None:
                raise ValidationError("Creator not found.")
            if int(creator.balance_cents) < amount_cents:
                raise InsufficientBalanceError("Insufficient user balance.")

            creator.balance_cents = int(creator.balance_cents) - amount_cents
            check = UserCheck(
                code=generated_code,
                creator_id=creator_id,
                stars_count=stars_count,
                amount_cents=amount_cents,
                status=CheckStatus.ACTIVE,
                claim_username=normalized_claim_username,
                claim_password_hash=claim_password_hash,
                inline_message_id=inline_message_id,
            )
            session.add(check)
            await session.commit()
            await session.refresh(check)

        await self._clear_user_cache(user_id=creator_id)
        return check.dto()

    async def update_claim_username(
        self,
        *,
        creator_id: int,
        check_id: int,
        claim_username: str | None,
    ) -> CheckDto | None:
        normalized_claim_username = self._normalize_claim_username(claim_username)
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            session = repository.session
            check = await repository.checks.get_by_creator_for_update(
                creator_id=creator_id,
                check_id=check_id,
            )
            if check is None or check.status != CheckStatus.ACTIVE:
                return None
            check.claim_username = normalized_claim_username
            await session.commit()
            await session.refresh(check)
            return check.dto()

    async def update_claim_password(
        self,
        *,
        creator_id: int,
        check_id: int,
        claim_password: str | None,
    ) -> CheckDto | None:
        password_hash = self._normalize_and_hash_password(claim_password)
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            session = repository.session
            check = await repository.checks.get_by_creator_for_update(
                creator_id=creator_id,
                check_id=check_id,
            )
            if check is None or check.status != CheckStatus.ACTIVE:
                return None
            check.claim_password_hash = password_hash
            await session.commit()
            await session.refresh(check)
            return check.dto()

    async def attach_inline_message_id(
        self,
        *,
        creator_id: int,
        check_id: int,
        inline_message_id: str | None,
    ) -> CheckDto | None:
        if inline_message_id is None:
            return None
        normalized = inline_message_id.strip()
        if not normalized:
            return None
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            session = repository.session
            check = await repository.checks.get_by_creator_for_update(
                creator_id=creator_id,
                check_id=check_id,
            )
            if check is None:
                return None
            check.inline_message_id = normalized
            await session.commit()
            await session.refresh(check)
            return check.dto()

    async def close_check(self, *, creator_id: int, check_id: int) -> CheckCloseResult:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            session = repository.session
            check = await repository.checks.get_by_creator_for_update(
                creator_id=creator_id,
                check_id=check_id,
            )
            if check is None:
                return CheckCloseResult(outcome=CheckCloseOutcome.NOT_FOUND)
            if check.status == CheckStatus.REDEEMED:
                return CheckCloseResult(
                    outcome=CheckCloseOutcome.ALREADY_REDEEMED,
                    check=check.dto(),
                )
            if check.status == CheckStatus.CLOSED:
                return CheckCloseResult(
                    outcome=CheckCloseOutcome.ALREADY_CLOSED,
                    check=check.dto(),
                )
            if check.status == CheckStatus.PROCESSING:
                return CheckCloseResult(
                    outcome=CheckCloseOutcome.PROCESSING,
                    check=check.dto(),
                )

            creator = await session.scalar(
                select(User).where(User.id == creator_id).with_for_update()
            )
            if creator is None:
                return CheckCloseResult(outcome=CheckCloseOutcome.NOT_FOUND)
            creator.balance_cents = int(creator.balance_cents) + int(check.amount_cents)
            check.status = CheckStatus.CLOSED
            check.closed_at = datetime_now()
            await session.commit()
            await session.refresh(check)

        await self._clear_user_cache(user_id=creator_id)
        return CheckCloseResult(outcome=CheckCloseOutcome.CLOSED, check=check.dto())

    async def claim_check(
        self,
        *,
        code: str,
        recipient_user_id: int,
        recipient_username: str | None,
        claim_password: str | None = None,
    ) -> CheckClaimResult:
        normalized_code = code.strip().lower()
        if not self.is_valid_code(normalized_code):
            return CheckClaimResult(outcome=CheckClaimOutcome.NOT_FOUND)

        reserved_result = await self._reserve_for_claim(
            code=normalized_code,
            recipient_user_id=recipient_user_id,
            recipient_username=recipient_username,
            claim_password=claim_password,
        )
        if reserved_result.outcome != CheckClaimOutcome.CLAIMED or reserved_result.check is None:
            return reserved_result

        reserved = reserved_result.check
        if not self.fragment_stars_service.configured:
            await self._release_processing_check(
                check_id=reserved.id,
                error_text="Fragment service is not configured.",
            )
            updated = await self.get(check_id=reserved.id)
            return CheckClaimResult(
                outcome=CheckClaimOutcome.DELIVERY_UNAVAILABLE,
                check=updated or reserved,
            )

        username = normalize_recipient_username(recipient_username or "")
        if username is None:
            await self._release_processing_check(
                check_id=reserved.id,
                error_text="Recipient username is missing.",
            )
            updated = await self.get(check_id=reserved.id)
            return CheckClaimResult(
                outcome=CheckClaimOutcome.USERNAME_REQUIRED,
                check=updated or reserved,
            )

        try:
            purchase = await self.fragment_stars_service.buy_stars(
                recipient_username=username,
                stars_count=reserved.stars_count,
            )
        except Exception as error:
            error_text = str(error).strip() or "Unknown delivery error."
            await self._release_processing_check(
                check_id=reserved.id,
                error_text=error_text,
            )
            updated = await self.get(check_id=reserved.id)
            return CheckClaimResult(
                outcome=CheckClaimOutcome.DELIVERY_FAILED,
                check=updated or reserved,
                error=error_text,
            )

        finalized = await self._finalize_claim(
            check_id=reserved.id,
            recipient_user_id=recipient_user_id,
            tx_hash=purchase.tx_hash,
        )
        return CheckClaimResult(
            outcome=CheckClaimOutcome.CLAIMED,
            check=finalized or reserved,
            tx_hash=purchase.tx_hash,
        )

    async def _reserve_for_claim(  # noqa: C901
        self,
        *,
        code: str,
        recipient_user_id: int,
        recipient_username: str | None,
        claim_password: str | None,
    ) -> CheckClaimResult:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            session = repository.session
            check = await repository.checks.get_by_code_for_update(code=code)
            if check is None:
                return CheckClaimResult(outcome=CheckClaimOutcome.NOT_FOUND)
            if check.status == CheckStatus.REDEEMED:
                return CheckClaimResult(
                    outcome=CheckClaimOutcome.ALREADY_REDEEMED,
                    check=check.dto(),
                )
            if check.status == CheckStatus.CLOSED:
                return CheckClaimResult(
                    outcome=CheckClaimOutcome.ALREADY_CLOSED,
                    check=check.dto(),
                )
            if check.status == CheckStatus.PROCESSING:
                return CheckClaimResult(
                    outcome=CheckClaimOutcome.PROCESSING,
                    check=check.dto(),
                )

            recipient = await session.scalar(
                select(User).where(User.id == recipient_user_id).with_for_update()
            )
            if recipient is None:
                return CheckClaimResult(outcome=CheckClaimOutcome.NOT_FOUND)

            normalized_username = normalize_recipient_username(recipient_username or "")
            if check.claim_username:
                if normalized_username is None:
                    return CheckClaimResult(
                        outcome=CheckClaimOutcome.USERNAME_REQUIRED,
                        check=check.dto(),
                    )
                if normalized_username.lower() != check.claim_username.lower():
                    return CheckClaimResult(
                        outcome=CheckClaimOutcome.RECIPIENT_MISMATCH,
                        check=check.dto(),
                    )

            if check.claim_password_hash:
                normalized_password = self._normalize_password(claim_password)
                if normalized_password is None:
                    return CheckClaimResult(
                        outcome=CheckClaimOutcome.PASSWORD_REQUIRED,
                        check=check.dto(),
                    )
                if self._hash_password(normalized_password) != check.claim_password_hash:
                    return CheckClaimResult(
                        outcome=CheckClaimOutcome.PASSWORD_INVALID,
                        check=check.dto(),
                    )

            check.status = CheckStatus.PROCESSING
            check.recipient_id = recipient_user_id
            check.last_error = None
            await session.commit()
            await session.refresh(check)
            return CheckClaimResult(outcome=CheckClaimOutcome.CLAIMED, check=check.dto())

    async def _finalize_claim(
        self,
        *,
        check_id: int,
        recipient_user_id: int,
        tx_hash: str | None,
    ) -> Optional[CheckDto]:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            session = repository.session
            db_check = await session.scalar(
                select(UserCheck)
                .where(
                    and_(
                        UserCheck.id == check_id,
                        UserCheck.status == CheckStatus.PROCESSING.value,
                        UserCheck.recipient_id == recipient_user_id,
                    )
                )
                .with_for_update()
            )
            if db_check is None:
                check = await repository.checks.get(check_id=check_id)
                return check.dto() if check is not None else None

            db_check.status = CheckStatus.REDEEMED
            db_check.redeemed_at = datetime_now()
            db_check.provider_tx_hash = tx_hash
            db_check.last_error = None
            await session.commit()
            await session.refresh(db_check)
            return db_check.dto()

    async def _release_processing_check(
        self,
        *,
        check_id: int,
        error_text: str,
    ) -> None:
        async with SQLSessionContext(session_pool=self.session_pool) as (repository, _uow):
            session = repository.session
            check = await session.scalar(
                select(UserCheck)
                .where(
                    and_(
                        UserCheck.id == check_id,
                        UserCheck.status == CheckStatus.PROCESSING.value,
                    )
                )
                .with_for_update()
            )
            if check is None:
                return
            check.status = CheckStatus.ACTIVE
            check.recipient_id = None
            check.last_error = error_text
            await session.commit()

    async def _generate_unique_code(self) -> str:
        for _ in range(_MAX_CODE_GENERATION_ATTEMPTS):
            code = uuid4().hex[:16]
            exists = await self.get_by_code(code=code)
            if exists is None:
                return code
        raise CheckServiceError("Failed to generate unique check code.")

    async def _clear_user_cache(self, *, user_id: int) -> None:
        cache_key = build_key("cache", "get_user", user_id=user_id)
        await self.redis.delete(cache_key)

    @staticmethod
    def _normalize_claim_username(value: str | None) -> str | None:
        if value is None:
            return None
        normalized = normalize_recipient_username(value)
        if normalized is None:
            raise ValidationError("Invalid claim username.")
        return normalized

    @staticmethod
    def _normalize_password(value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        if len(normalized) > _MAX_PASSWORD_LEN:
            raise ValidationError("Claim password is too long.")
        return normalized

    @classmethod
    def _normalize_and_hash_password(cls, value: str | None) -> str | None:
        normalized = cls._normalize_password(value)
        if normalized is None:
            return None
        return cls._hash_password(normalized)

    @staticmethod
    def _hash_password(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()
