from __future__ import annotations

import logging
import secrets
import string
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Final, cast

from redis.asyncio import Redis
from sqlalchemy import delete, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.sql import PromoCode, PromoCodeActivation, User
from app.utils.key_builder import build_key

logger: Final[logging.Logger] = logging.getLogger(__name__)
_CODE_ALPHABET: Final[str] = string.ascii_uppercase + string.digits


@dataclass(frozen=True, slots=True)
class PromoCodeInfo:
    code: str
    amount_cents: int
    activations: int
    max_activations: int | None
    is_enabled: bool
    created_at: datetime


@dataclass(frozen=True, slots=True)
class PromoCodeActivationInfo:
    user_id: int
    user_name: str
    amount_cents: int
    activated_at: datetime


class PromoCodeService:
    class Error(RuntimeError):
        pass

    class InvalidCodeError(Error):
        pass

    class CodeAlreadyExistsError(Error):
        pass

    class CodeNotFoundError(Error):
        pass

    class AlreadyUsedError(Error):
        pass

    class LimitReachedError(Error):
        pass

    class DisabledError(Error):
        pass

    class ActivationFailedError(Error):
        pass

    def __init__(
        self,
        *,
        session_pool: async_sessionmaker[AsyncSession],
        redis: Redis | None = None,
    ) -> None:
        self.session_pool = session_pool
        self.redis = redis

    async def list_codes(self, *, limit: int = 50) -> list[PromoCodeInfo]:
        if limit <= 0:
            return []
        async with self.session_pool() as session:
            rows = await session.scalars(
                select(PromoCode).order_by(PromoCode.created_at.desc()).limit(limit)
            )
            return [self._to_info(row) for row in rows]

    async def get_code(self, code: str) -> PromoCodeInfo | None:
        normalized = self.normalize_code(code)
        async with self.session_pool() as session:
            row = await session.get(PromoCode, normalized)
            return self._to_info(row) if row is not None else None

    async def list_activations(
        self,
        *,
        code: str,
        limit: int = 100,
    ) -> list[PromoCodeActivationInfo]:
        normalized = self.normalize_code(code)
        if limit <= 0:
            return []
        async with self.session_pool() as session:
            if await session.get(PromoCode, normalized) is None:
                raise self.CodeNotFoundError("Promo code not found.")
            rows = await session.execute(
                select(PromoCodeActivation, User.name)
                .join(User, User.id == PromoCodeActivation.user_id)
                .where(PromoCodeActivation.promo_code == normalized)
                .order_by(PromoCodeActivation.created_at.desc())
                .limit(limit)
            )
            return [
                PromoCodeActivationInfo(
                    user_id=int(activation.user_id),
                    user_name=user_name,
                    amount_cents=activation.amount_cents,
                    activated_at=activation.created_at,
                )
                for activation, user_name in rows
            ]

    async def create_code(
        self,
        *,
        code: str,
        amount_cents: int,
        max_activations: int | None,
    ) -> PromoCodeInfo:
        normalized = self.normalize_code(code)
        self._validate_values(amount_cents=amount_cents, max_activations=max_activations)
        row = PromoCode(
            code=normalized,
            amount_cents=amount_cents,
            max_activations=max_activations,
            activations=0,
            is_enabled=True,
        )
        async with self.session_pool() as session:
            session.add(row)
            try:
                await session.commit()
            except IntegrityError as error:
                await session.rollback()
                raise self.CodeAlreadyExistsError("Promo code already exists.") from error
            await session.refresh(row)
        return self._to_info(row)

    async def create_unique_one_time_codes(
        self,
        *,
        amount_cents: int,
        count: int,
        prefix: str = "PROMO",
    ) -> list[PromoCodeInfo]:
        if count <= 0 or count > 200:
            raise self.InvalidCodeError("Count must be between 1 and 200.")
        if amount_cents <= 0:
            raise self.InvalidCodeError("Amount must be positive.")
        normalized_prefix = "".join(
            ch for ch in prefix.upper() if ch in _CODE_ALPHABET or ch in {"_", "-"}
        )
        normalized_prefix = normalized_prefix[:12] or "PROMO"
        created: list[PromoCodeInfo] = []
        attempts = 0
        while len(created) < count and attempts < count * 20:
            attempts += 1
            suffix = "".join(secrets.choice(_CODE_ALPHABET) for _ in range(8))
            try:
                info = await self.create_code(
                    code=f"{normalized_prefix}-{suffix}",
                    amount_cents=amount_cents,
                    max_activations=1,
                )
            except self.CodeAlreadyExistsError:
                continue
            created.append(info)
        if len(created) != count:
            raise self.Error("Could not generate requested number of unique promo codes.")
        return created

    async def delete_code(self, code: str) -> bool:
        normalized = self.normalize_code(code)
        async with self.session_pool() as session:
            result = cast(
                CursorResult[Any],
                await session.execute(delete(PromoCode).where(PromoCode.code == normalized)),
            )
            await session.commit()
            return bool(result.rowcount)

    async def set_max_activations(
        self,
        *,
        code: str,
        max_activations: int | None,
    ) -> PromoCodeInfo:
        normalized = self.normalize_code(code)
        if max_activations is not None and max_activations <= 0:
            raise self.InvalidCodeError("Activation limit must be positive or unlimited.")
        async with self.session_pool() as session:
            row = await session.get(PromoCode, normalized)
            if row is None:
                raise self.CodeNotFoundError("Promo code not found.")
            row.max_activations = max_activations
            await session.commit()
            await session.refresh(row)
            return self._to_info(row)

    async def set_enabled(self, *, code: str, enabled: bool) -> PromoCodeInfo:
        normalized = self.normalize_code(code)
        async with self.session_pool() as session:
            row = await session.get(PromoCode, normalized)
            if row is None:
                raise self.CodeNotFoundError("Promo code not found.")
            row.is_enabled = enabled
            await session.commit()
            await session.refresh(row)
            return self._to_info(row)

    async def activate_code(self, *, user_id: int, code: str) -> int:
        normalized = self.normalize_code(code)
        async with self.session_pool() as session:
            row = await session.scalar(
                select(PromoCode).where(PromoCode.code == normalized).with_for_update()
            )
            if row is None:
                raise self.CodeNotFoundError("Promo code not found.")
            if not row.is_enabled:
                raise self.DisabledError("Promo code is disabled.")
            already_used = await session.scalar(
                select(PromoCodeActivation.id).where(
                    PromoCodeActivation.promo_code == normalized,
                    PromoCodeActivation.user_id == user_id,
                )
            )
            if already_used is not None:
                raise self.AlreadyUsedError("Promo code already used.")
            if row.max_activations is not None and row.activations >= row.max_activations:
                raise self.LimitReachedError("Promo activation limit reached.")
            user = await session.scalar(select(User).where(User.id == user_id).with_for_update())
            if user is None:
                raise self.ActivationFailedError("Promo user was not found.")
            session.add(
                PromoCodeActivation(
                    promo_code=normalized,
                    user_id=user_id,
                    amount_cents=row.amount_cents,
                    created_at=datetime.now(UTC),
                )
            )
            row.activations += 1
            user.balance_cents += row.amount_cents
            try:
                await session.commit()
            except IntegrityError as error:
                await session.rollback()
                raise self.AlreadyUsedError("Promo code already used.") from error
            return row.amount_cents

    async def rollback_activation(self, *, user_id: int, code: str) -> None:
        """Compatibility no-op: activation and balance credit share one transaction."""

    async def migrate_legacy_redis_data(self) -> int:  # noqa: C901
        """Move legacy Redis promo state into PostgreSQL once, preserving activations."""
        if self.redis is None:
            return 0
        raw_codes = await self.redis.zrange(self._legacy_index_key(), 0, -1)
        migrated = 0
        for raw_code in raw_codes:
            code = raw_code.decode("utf-8") if isinstance(raw_code, bytes) else str(raw_code)
            try:
                normalized = self.normalize_code(code)
            except self.InvalidCodeError:
                continue
            legacy_key = self._legacy_code_key(normalized)
            data = await self.redis.hgetall(legacy_key)
            if not data:
                continue
            legacy = self._parse_legacy_hash(normalized, data)
            activation_keys = [
                key async for key in self.redis.scan_iter(
                    match=f"promo:activation:*:{normalized}", count=200
                )
            ]
            async with self.session_pool() as session:
                existing = await session.get(PromoCode, normalized)
                if existing is None:
                    promo = PromoCode(
                        code=normalized,
                        amount_cents=legacy.amount_cents,
                        activations=legacy.activations,
                        max_activations=legacy.max_activations,
                        is_enabled=True,
                        created_at=legacy.created_at,
                        updated_at=legacy.created_at,
                    )
                    session.add(promo)
                    await session.flush()
                    for activation_key in activation_keys:
                        key_text = (
                            activation_key.decode("utf-8")
                            if isinstance(activation_key, bytes)
                            else str(activation_key)
                        )
                        try:
                            activation_user_id = int(key_text.split(":")[-2])
                        except (ValueError, IndexError):
                            continue
                        if await session.get(User, activation_user_id) is not None:
                            session.add(
                                PromoCodeActivation(
                                    promo_code=normalized,
                                    user_id=activation_user_id,
                                    amount_cents=legacy.amount_cents,
                                    created_at=legacy.created_at,
                                )
                            )
                    await session.commit()
                    migrated += 1
            if activation_keys:
                await self.redis.delete(*activation_keys)
            await self.redis.delete(legacy_key)
            await self.redis.zrem(self._legacy_index_key(), normalized)
        if migrated:
            logger.info("Migrated %s legacy promo code(s) from Redis to PostgreSQL", migrated)
        return migrated

    @staticmethod
    def normalize_code(value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) < 4 or len(normalized) > 40:
            raise PromoCodeService.InvalidCodeError("Promo code length must be between 4 and 40.")
        if any(ch not in _CODE_ALPHABET and ch not in {"_", "-"} for ch in normalized):
            raise PromoCodeService.InvalidCodeError(
                "Promo code can contain only A-Z, 0-9, _ and -.",
            )
        return normalized

    @staticmethod
    def _validate_values(*, amount_cents: int, max_activations: int | None) -> None:
        if amount_cents <= 0:
            raise PromoCodeService.InvalidCodeError("Promo amount must be positive.")
        if max_activations is not None and max_activations <= 0:
            raise PromoCodeService.InvalidCodeError(
                "Activation limit must be positive or unlimited."
            )

    @staticmethod
    def _to_info(row: PromoCode) -> PromoCodeInfo:
        return PromoCodeInfo(
            code=row.code,
            amount_cents=row.amount_cents,
            activations=row.activations,
            max_activations=row.max_activations,
            is_enabled=row.is_enabled,
            created_at=row.created_at,
        )

    @staticmethod
    def _parse_legacy_hash(code: str, data: dict[Any, Any]) -> PromoCodeInfo:
        def value(key: str) -> str:
            raw: Any = data.get(key) or data.get(key.encode("utf-8"), b"")  # type: ignore[arg-type]
            return raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)

        max_raw = int(value("max_activations") or "0")
        created_ts = int(value("created_at") or "0")
        return PromoCodeInfo(
            code=code,
            amount_cents=int(value("amount_cents") or "0"),
            activations=max(0, int(value("activations") or "0")),
            max_activations=None if max_raw <= 0 else max_raw,
            is_enabled=True,
            created_at=(
                datetime.fromtimestamp(created_ts, tz=UTC)
                if created_ts > 0
                else datetime.now(UTC)
            ),
        )

    @staticmethod
    def _legacy_index_key() -> str:
        return build_key("promo", "codes")

    @staticmethod
    def _legacy_code_key(code: str) -> str:
        return build_key("promo", "code", code=code)
