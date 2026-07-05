from __future__ import annotations

import asyncio
import re
import secrets
from dataclasses import dataclass
from typing import Annotated, Awaitable, Callable, cast

from aiogram import Bot
from fastapi import Depends, Header, Request
from redis.asyncio import Redis

from app.models.config import AppConfig
from app.models.dto.stars_order import StarsOrderDto
from app.models.dto.user import UserDto
from app.services.crud import (
    CheckService,
    StarsOrderService,
    StarsSellOrderService,
    UserService,
)
from app.services.promo_codes import PromoCodeService
from app.utils.key_builder import build_key

from .errors import ErrorCode, conflict, forbidden, unauthorized, validation_error
from .sessions import resolve_session

_IDEMPOTENCY_PREFIX = "miniapp_idempotency"
_IDEMPOTENCY_KEY_RE = re.compile(r"^[A-Za-z0-9._-]{8,128}$")
_IDEMPOTENCY_TTL_SECONDS = 15 * 60


def get_config(request: Request) -> AppConfig:
    return cast(AppConfig, request.app.state.config)


def get_redis(request: Request) -> Redis:
    return cast(Redis, request.app.state.redis)


def get_user_service(request: Request) -> UserService:
    return cast(UserService, request.app.state.user_service)


def get_stars_order_service(request: Request) -> StarsOrderService:
    return cast(StarsOrderService, request.app.state.stars_order_service)


def get_stars_sell_order_service(request: Request) -> StarsSellOrderService:
    return cast(StarsSellOrderService, request.app.state.stars_sell_order_service)


def get_check_service(request: Request) -> CheckService:
    return cast(CheckService, request.app.state.check_service)


def get_promo_code_service(request: Request) -> PromoCodeService:
    return cast(PromoCodeService, request.app.state.promo_code_service)


def get_bot(request: Request) -> Bot:
    return cast(Bot, request.app.state.bot)


async def resolve_bot_username(request: Request) -> str:
    cached = getattr(request.app.state, "miniapp_bot_username", None)
    if isinstance(cached, str) and cached:
        return cached
    bot: Bot = request.app.state.bot
    try:
        me = await bot.get_me()
    except Exception:
        return "unknown_bot"
    username = (me.username or "unknown_bot").lstrip("@")
    request.app.state.miniapp_bot_username = username
    return username


ConfigDep = Annotated[AppConfig, Depends(get_config)]
RedisDep = Annotated[Redis, Depends(get_redis)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
StarsOrderServiceDep = Annotated[StarsOrderService, Depends(get_stars_order_service)]
StarsSellOrderServiceDep = Annotated[
    StarsSellOrderService, Depends(get_stars_sell_order_service)
]
CheckServiceDep = Annotated[CheckService, Depends(get_check_service)]
PromoCodeServiceDep = Annotated[PromoCodeService, Depends(get_promo_code_service)]
BotDep = Annotated[Bot, Depends(get_bot)]


@dataclass(frozen=True, slots=True)
class AuthContext:
    token: str
    user: UserDto


def _parse_bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.strip().partition(" ")
    if scheme.lower() != "bearer":
        return None
    token = token.strip()
    return token or None


async def require_user(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> AuthContext:
    token = _parse_bearer(authorization)
    if not token:
        unauthorized("Access token is missing.")
    config: AppConfig = request.app.state.config
    redis: Redis = request.app.state.redis
    resolved = await resolve_session(
        redis=redis,
        token=token,
        ttl_seconds=config.telegram.miniapp_session_ttl_seconds,
    )
    if resolved is None:
        unauthorized("Session is expired or invalid.")
    user_service: UserService = request.app.state.user_service
    user = await user_service.get(user_id=resolved.user_id)
    if user is None:
        unauthorized("User was not found.")
    return AuthContext(token=token, user=user)


CurrentUser = Annotated[AuthContext, Depends(require_user)]


async def require_admin(request: Request, auth: CurrentUser) -> AuthContext:
    config: AppConfig = request.app.state.config
    admin_chat_id = int(config.common.admin_chat_id)
    if admin_chat_id <= 0 or int(auth.user.id) != admin_chat_id:
        forbidden("Administrator access is required.")
    return auth


CurrentAdmin = Annotated[AuthContext, Depends(require_admin)]


def normalize_idempotency_key(idempotency_key: str | None) -> str | None:
    if idempotency_key is None:
        return None
    normalized = idempotency_key.strip()
    if not normalized:
        return None
    if not _IDEMPOTENCY_KEY_RE.fullmatch(normalized):
        validation_error(
            "Invalid Idempotency-Key. Use 8..128 chars: letters, digits, '.', '_' or '-'.",
        )
    return normalized


def _idempotency_storage_key(*, user_id: int, scope: str, key: str) -> str:
    return build_key(_IDEMPOTENCY_PREFIX, user_id, scope, key)


def _decode_redis_value(value: str | bytes | int | float) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    return str(value)


async def run_idempotent_order_create(
    *,
    redis: Redis,
    stars_order_service: StarsOrderService,
    user_id: int,
    scope: str,
    idempotency_key: str | None,
    create_order: Callable[[], Awaitable[StarsOrderDto]],
) -> StarsOrderDto:
    """Run ``create_order`` once per Idempotency-Key, returning the cached order on retry."""

    normalized_key = normalize_idempotency_key(idempotency_key)
    if normalized_key is None:
        return await create_order()

    storage_key = _idempotency_storage_key(user_id=user_id, scope=scope, key=normalized_key)
    lock_token = f"lock:{secrets.token_hex(8)}"
    acquired = await redis.set(storage_key, lock_token, ex=_IDEMPOTENCY_TTL_SECONDS, nx=True)
    if acquired:
        try:
            order = await create_order()
        except Exception:
            existing = await redis.get(storage_key)
            if existing is not None and _decode_redis_value(existing) == lock_token:
                await redis.delete(storage_key)
            raise
        await redis.set(storage_key, str(order.id), ex=_IDEMPOTENCY_TTL_SECONDS)
        return order

    for _ in range(6):
        existing = await redis.get(storage_key)
        if existing is None:
            break
        decoded = _decode_redis_value(existing)
        if decoded.isdigit():
            existing_order = await stars_order_service.get_user_order(
                user_id=user_id,
                order_id=int(decoded),
            )
            if existing_order is not None:
                return existing_order
            await redis.delete(storage_key)
            break
        await asyncio.sleep(0.2)

    conflict("Duplicate request is already being processed.", code=ErrorCode.DUPLICATE_REQUEST)
