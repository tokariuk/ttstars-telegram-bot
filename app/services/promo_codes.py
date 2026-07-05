from __future__ import annotations

import secrets
import string
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Final

from app.utils.key_builder import build_key

_CODE_ALPHABET: Final[str] = string.ascii_uppercase + string.digits
_ACTIVATE_LUA: Final[str] = """
local code_key = KEYS[1]
local user_key = KEYS[2]
if redis.call('exists', code_key) == 0 then
  return {0, 'not_found'}
end
if redis.call('exists', user_key) == 1 then
  return {0, 'already_used'}
end
local amount = tonumber(redis.call('hget', code_key, 'amount_cents') or '0')
if amount <= 0 then
  return {0, 'invalid_amount'}
end
local max_activations = tonumber(redis.call('hget', code_key, 'max_activations') or '0')
local activations = tonumber(redis.call('hget', code_key, 'activations') or '0')
if max_activations > 0 and activations >= max_activations then
  return {0, 'limit_reached'}
end
redis.call('set', user_key, '1')
redis.call('hincrby', code_key, 'activations', 1)
return {1, tostring(amount)}
"""


@dataclass(frozen=True, slots=True)
class PromoCodeInfo:
    code: str
    amount_cents: int
    activations: int
    max_activations: int | None
    created_at: datetime


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

    class ActivationFailedError(Error):
        pass

    def __init__(self, *, redis: Any) -> None:
        # NOTE: redis-py async client methods are awaitable at runtime, but
        # static typing in redis package can be inconsistent for pyright.
        # Keep runtime behavior strict and avoid false-positive await errors.
        self.redis = redis

    async def list_codes(self, *, limit: int = 50) -> list[PromoCodeInfo]:
        if limit <= 0:
            return []
        raw_codes = await self.redis.zrevrange(self._index_key(), 0, max(limit - 1, 0))
        codes = [
            code.decode("utf-8") if isinstance(code, bytes) else str(code)
            for code in raw_codes
        ]
        result: list[PromoCodeInfo] = []
        for code in codes:
            details = await self.get_code(code)
            if details is not None:
                result.append(details)
        return result

    async def get_code(self, code: str) -> PromoCodeInfo | None:
        normalized = self.normalize_code(code)
        data = await self.redis.hgetall(self._code_key(normalized))
        if not data:
            return None
        return self._parse_code_hash(normalized, data)

    async def create_code(
        self,
        *,
        code: str,
        amount_cents: int,
        max_activations: int | None,
    ) -> PromoCodeInfo:
        normalized = self.normalize_code(code)
        if await self.redis.exists(self._code_key(normalized)):
            raise self.CodeAlreadyExistsError("Promo code already exists.")
        return await self._create_code(
            code=normalized,
            amount_cents=amount_cents,
            max_activations=max_activations,
        )

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
            code = f"{normalized_prefix}-{suffix}"
            if await self.redis.exists(self._code_key(code)):
                continue
            created.append(
                await self._create_code(
                    code=code,
                    amount_cents=amount_cents,
                    max_activations=1,
                )
            )
        if len(created) != count:
            raise self.Error("Could not generate requested number of unique promo codes.")
        return created

    async def delete_code(self, code: str) -> bool:
        normalized = self.normalize_code(code)
        key = self._code_key(normalized)
        deleted = await self.redis.delete(key)
        await self.redis.zrem(self._index_key(), normalized)
        return bool(deleted)

    async def set_max_activations(
        self,
        *,
        code: str,
        max_activations: int | None,
    ) -> PromoCodeInfo:
        normalized = self.normalize_code(code)
        key = self._code_key(normalized)
        if not await self.redis.exists(key):
            raise self.CodeNotFoundError("Promo code not found.")
        max_value = 0 if max_activations is None else max(max_activations, 0)
        await self.redis.hset(key, mapping={"max_activations": str(max_value)})
        data = await self.redis.hgetall(key)
        return self._parse_code_hash(normalized, data)

    async def activate_code(self, *, user_id: int, code: str) -> int:
        normalized = self.normalize_code(code)
        key = self._code_key(normalized)
        activation_key = self._activation_key(user_id=user_id, code=normalized)
        raw = await self.redis.eval(_ACTIVATE_LUA, 2, key, activation_key)
        if not isinstance(raw, list) or len(raw) < 2:
            raise self.ActivationFailedError("Unexpected promo activation response.")
        success_raw = raw[0]
        detail_raw = raw[1]
        success = (
            int(success_raw)
            if not isinstance(success_raw, bytes)
            else int(success_raw.decode("utf-8"))
        )
        detail = detail_raw.decode("utf-8") if isinstance(detail_raw, bytes) else str(detail_raw)
        if success != 1:
            if detail == "already_used":
                raise self.AlreadyUsedError("Promo code already used.")
            if detail == "limit_reached":
                raise self.LimitReachedError("Promo activation limit reached.")
            if detail == "not_found":
                raise self.CodeNotFoundError("Promo code not found.")
            raise self.ActivationFailedError("Promo activation failed.")
        amount_cents = int(detail)
        if amount_cents <= 0:
            raise self.ActivationFailedError("Promo amount is invalid.")
        return amount_cents

    async def rollback_activation(self, *, user_id: int, code: str) -> None:
        normalized = self.normalize_code(code)
        activation_key = self._activation_key(user_id=user_id, code=normalized)
        deleted = await self.redis.delete(activation_key)
        if not deleted:
            return
        key = self._code_key(normalized)
        if await self.redis.exists(key):
            await self.redis.hincrby(key, "activations", -1)

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

    async def _create_code(
        self,
        *,
        code: str,
        amount_cents: int,
        max_activations: int | None,
    ) -> PromoCodeInfo:
        if amount_cents <= 0:
            raise self.InvalidCodeError("Promo amount must be positive.")
        created_at = datetime.now(UTC)
        key = self._code_key(code)
        max_value = 0 if max_activations is None else max(max_activations, 0)
        await self.redis.hset(
            key,
            mapping={
                "amount_cents": str(amount_cents),
                "max_activations": str(max_value),
                "activations": "0",
                "created_at": str(int(created_at.timestamp())),
            },
        )
        await self.redis.zadd(self._index_key(), {code: created_at.timestamp()})
        return PromoCodeInfo(
            code=code,
            amount_cents=amount_cents,
            activations=0,
            max_activations=max_activations,
            created_at=created_at,
        )

    @staticmethod
    def _parse_code_hash(code: str, data: dict[bytes, bytes] | dict[str, str]) -> PromoCodeInfo:
        def _get_value(key: str) -> str:
            if key in data:
                value = data[key]  # type: ignore[index]
            else:
                value = data.get(key.encode("utf-8"), b"")  # type: ignore[arg-type]
            if isinstance(value, bytes):
                return value.decode("utf-8")
            return str(value)

        amount_cents = int(_get_value("amount_cents") or "0")
        activations = int(_get_value("activations") or "0")
        max_activations_raw = int(_get_value("max_activations") or "0")
        created_ts = int(_get_value("created_at") or "0")
        created_at = (
            datetime.fromtimestamp(created_ts, tz=UTC)
            if created_ts > 0
            else datetime.now(UTC)
        )
        return PromoCodeInfo(
            code=code,
            amount_cents=amount_cents,
            activations=max(0, activations),
            max_activations=(None if max_activations_raw <= 0 else max_activations_raw),
            created_at=created_at,
        )

    @staticmethod
    def _index_key() -> str:
        return build_key("promo", "codes")

    @staticmethod
    def _code_key(code: str) -> str:
        return build_key("promo", "code", code=code)

    @staticmethod
    def _activation_key(*, user_id: int, code: str) -> str:
        return build_key("promo", "activation", user_id=user_id, code=code)
