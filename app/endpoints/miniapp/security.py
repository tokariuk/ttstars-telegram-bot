from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass
from json import JSONDecodeError, loads
from urllib.parse import parse_qsl

from app.models.dto.miniapp import BrowserAuthRequest

from .errors import unauthorized, validation_error

_INIT_DATA_MAX_LENGTH = 8192


@dataclass(frozen=True, slots=True)
class VerifiedUser:
    user_id: int
    full_name: str
    language_code: str | None
    start_param: str | None


def _parse_init_data(init_data: str) -> dict[str, str]:
    normalized = init_data.strip()
    if not normalized or len(normalized) > _INIT_DATA_MAX_LENGTH:
        validation_error("initData is empty or too large.")
    try:
        pairs = parse_qsl(normalized, keep_blank_values=True, strict_parsing=True)
    except ValueError:
        validation_error("initData is malformed.")
    values: dict[str, str] = {}
    for key, value in pairs:
        if key in values:
            validation_error("initData contains duplicate keys.")
        values[key] = value
    if not values:
        validation_error("initData is empty.")
    return values


def _verify_init_data_hash(*, values: dict[str, str], bot_token: str) -> None:
    provided_hash = values.pop("hash", None)
    if not provided_hash:
        unauthorized("initData hash is missing.")
    data_check_string = "\n".join(f"{key}={values[key]}" for key in sorted(values))
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    expected_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(provided_hash, expected_hash):
        unauthorized("initData signature is invalid.")


def _verify_auth_date(*, auth_date_raw: str | None, max_age_seconds: int) -> None:
    if auth_date_raw is None or not auth_date_raw.isdigit():
        unauthorized("Authentication date is invalid.")
    auth_date = int(auth_date_raw)
    now = int(time.time())
    safe_max_age = max(60, max_age_seconds)
    if auth_date > now + 60:
        unauthorized("Authentication date is in the future.")
    if now - auth_date > safe_max_age:
        unauthorized("Authentication data has expired.")


def _full_name(*, first_name: str, last_name: str, username: str, user_id: int) -> str:
    full_name = " ".join(part for part in (first_name.strip(), last_name.strip()) if part)
    if full_name:
        return full_name
    return username.strip() or f"user_{user_id}"


def _parse_init_data_user(*, values: dict[str, str]) -> VerifiedUser:
    raw_user = values.get("user")
    if raw_user is None:
        unauthorized("initData user payload is missing.")
    try:
        parsed_user = loads(raw_user)
    except JSONDecodeError:
        unauthorized("initData user payload is malformed.")
    if not isinstance(parsed_user, dict):
        unauthorized("initData user payload is malformed.")

    user_id_raw = parsed_user.get("id")
    if not isinstance(user_id_raw, int) or user_id_raw <= 0:
        unauthorized("initData user id is invalid.")

    language_code_value = parsed_user.get("language_code")
    language_code = (
        str(language_code_value).strip().lower() if isinstance(language_code_value, str) else None
    )
    start_param_value = values.get("start_param")
    return VerifiedUser(
        user_id=user_id_raw,
        full_name=_full_name(
            first_name=str(parsed_user.get("first_name") or ""),
            last_name=str(parsed_user.get("last_name") or ""),
            username=str(parsed_user.get("username") or ""),
            user_id=user_id_raw,
        ),
        language_code=language_code,
        start_param=start_param_value.strip() if start_param_value else None,
    )


def verify_telegram_init_data(
    *,
    init_data: str,
    bot_token: str,
    max_age_seconds: int,
) -> VerifiedUser:
    """Validate a Telegram WebApp ``initData`` string and extract the user."""

    values = _parse_init_data(init_data)
    _verify_init_data_hash(values=values, bot_token=bot_token)
    _verify_auth_date(auth_date_raw=values.get("auth_date"), max_age_seconds=max_age_seconds)
    return _parse_init_data_user(values=values)


def _verify_login_hash(*, payload: BrowserAuthRequest, bot_token: str) -> None:
    values = payload.model_dump(exclude_none=True)
    provided_hash = str(values.pop("hash", "")).strip()
    if not provided_hash:
        unauthorized("Telegram login hash is missing.")
    normalized = {key: str(value) for key, value in values.items()}
    data_check_string = "\n".join(f"{key}={normalized[key]}" for key in sorted(normalized))
    secret_key = hashlib.sha256(bot_token.encode("utf-8")).digest()
    expected_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(provided_hash, expected_hash):
        unauthorized("Telegram login signature is invalid.")


def verify_telegram_login_data(
    *,
    payload: BrowserAuthRequest,
    bot_token: str,
    max_age_seconds: int,
) -> VerifiedUser:
    """Validate a Telegram Login Widget payload (browser fallback)."""

    _verify_login_hash(payload=payload, bot_token=bot_token)
    _verify_auth_date(auth_date_raw=str(payload.auth_date), max_age_seconds=max_age_seconds)
    language_code = (payload.language_code or "").strip().lower() or None
    return VerifiedUser(
        user_id=payload.id,
        full_name=_full_name(
            first_name=payload.first_name,
            last_name=payload.last_name or "",
            username=payload.username or "",
            user_id=payload.id,
        ),
        language_code=language_code,
        start_param=None,
    )
