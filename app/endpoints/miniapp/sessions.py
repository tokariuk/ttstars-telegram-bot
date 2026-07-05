from __future__ import annotations

import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timedelta

from redis.asyncio import Redis

from app.utils import mjson
from app.utils.key_builder import build_key
from app.utils.time import datetime_now

_SESSION_PREFIX = "miniapp_session"
_TOKEN_BYTES = 32
_MIN_TTL_SECONDS = 60


@dataclass(frozen=True, slots=True)
class IssuedSession:
    token: str
    expires_in: int
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class ResolvedSession:
    user_id: int
    expires_at: datetime


def _session_key(token: str) -> str:
    return build_key(_SESSION_PREFIX, token)


def _safe_ttl(ttl_seconds: int) -> int:
    return max(_MIN_TTL_SECONDS, int(ttl_seconds))


def _decode_user_id(value: str | bytes) -> int | None:
    try:
        payload = mjson.decode(value if isinstance(value, bytes) else value.encode())
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    user_id = payload.get("user_id")
    if isinstance(user_id, int) and user_id > 0:
        return user_id
    if isinstance(user_id, str) and user_id.isdigit():
        parsed = int(user_id)
        return parsed if parsed > 0 else None
    return None


async def issue_session(*, redis: Redis, user_id: int, ttl_seconds: int) -> IssuedSession:
    token = secrets.token_urlsafe(_TOKEN_BYTES)
    ttl = _safe_ttl(ttl_seconds)
    payload = {"user_id": user_id, "issued_at": int(time.time())}
    await redis.set(_session_key(token), mjson.encode(payload), ex=ttl)
    return IssuedSession(
        token=token,
        expires_in=ttl,
        expires_at=datetime_now() + timedelta(seconds=ttl),
    )


async def resolve_session(
    *,
    redis: Redis,
    token: str,
    ttl_seconds: int,
) -> ResolvedSession | None:
    key = _session_key(token)
    value = await redis.get(key)
    if value is None:
        return None
    user_id = _decode_user_id(value)
    if user_id is None:
        await redis.delete(key)
        return None
    ttl = _safe_ttl(ttl_seconds)
    await redis.expire(key, ttl)  # sliding expiration
    return ResolvedSession(user_id=user_id, expires_at=datetime_now() + timedelta(seconds=ttl))


async def revoke_session(*, redis: Redis, token: str) -> None:
    await redis.delete(_session_key(token))
