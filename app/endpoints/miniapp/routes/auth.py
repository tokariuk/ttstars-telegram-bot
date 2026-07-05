from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Request

from app.models.dto.miniapp import (
    AuthConfigResponse,
    AuthResponse,
    BrowserAuthRequest,
    OkResponse,
    SessionResponse,
    TelegramAuthRequest,
)
from app.utils.time import datetime_now

from ..deps import ConfigDep, CurrentUser, RedisDep, UserServiceDep, resolve_bot_username
from ..security import verify_telegram_init_data, verify_telegram_login_data
from ..serializers import build_user_response
from ..sessions import issue_session, revoke_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/config", summary="Public config required to start a login session")
async def auth_config(request: Request) -> AuthConfigResponse:
    return AuthConfigResponse(bot_username=await resolve_bot_username(request))


@router.post("/telegram", summary="Authenticate with Telegram WebApp initData")
async def auth_telegram(
    payload: TelegramAuthRequest,
    config: ConfigDep,
    redis: RedisDep,
    user_service: UserServiceDep,
) -> AuthResponse:
    verified = verify_telegram_init_data(
        init_data=payload.init_data,
        bot_token=config.telegram.bot_token.get_secret_value(),
        max_age_seconds=config.telegram.miniapp_auth_max_age_seconds,
    )
    user = await user_service.ensure_telegram_user(
        user_id=verified.user_id,
        full_name=verified.full_name,
        language_code=verified.language_code,
    )
    if verified.start_param:
        await user_service.try_bind_referrer_from_start_payload(
            user_id=user.id,
            payload=verified.start_param,
        )
        user = await user_service.get(user_id=user.id) or user
    issued = await issue_session(
        redis=redis,
        user_id=user.id,
        ttl_seconds=config.telegram.miniapp_session_ttl_seconds,
    )
    return AuthResponse(
        access_token=issued.token,
        expires_in=issued.expires_in,
        expires_at=issued.expires_at,
        user=build_user_response(user),
    )


@router.post("/browser", summary="Authenticate with the Telegram Login Widget (browser)")
async def auth_browser(
    payload: BrowserAuthRequest,
    config: ConfigDep,
    redis: RedisDep,
    user_service: UserServiceDep,
) -> AuthResponse:
    verified = verify_telegram_login_data(
        payload=payload,
        bot_token=config.telegram.bot_token.get_secret_value(),
        max_age_seconds=config.telegram.miniapp_auth_max_age_seconds,
    )
    user = await user_service.ensure_telegram_user(
        user_id=verified.user_id,
        full_name=verified.full_name,
        language_code=verified.language_code,
    )
    issued = await issue_session(
        redis=redis,
        user_id=user.id,
        ttl_seconds=config.telegram.miniapp_session_ttl_seconds,
    )
    return AuthResponse(
        access_token=issued.token,
        expires_in=issued.expires_in,
        expires_at=issued.expires_at,
        user=build_user_response(user),
    )


@router.get("/session", summary="Validate the current token and refresh its lifetime")
async def auth_session(auth: CurrentUser, config: ConfigDep) -> SessionResponse:
    # ``require_user`` (the CurrentUser dependency) has already validated the token
    # and slid its TTL, so the session is now valid for the full window again.
    ttl = max(60, int(config.telegram.miniapp_session_ttl_seconds))
    return SessionResponse(
        user=build_user_response(auth.user),
        expires_at=datetime_now() + timedelta(seconds=ttl),
    )


@router.post("/logout", summary="Revoke the current session token")
async def auth_logout(auth: CurrentUser, redis: RedisDep) -> OkResponse:
    await revoke_session(redis=redis, token=auth.token)
    return OkResponse(ok=True)
