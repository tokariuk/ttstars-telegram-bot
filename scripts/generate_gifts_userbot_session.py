from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from telethon import TelegramClient
from telethon.errors import (
    ApiIdInvalidError,
    PasswordHashInvalidError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    SessionPasswordNeededError,
)
from telethon.sessions import StringSession


@dataclass(slots=True)
class UserbotConfig:
    api_id: int
    api_hash: str
    device_model: str
    system_version: str
    app_version: str
    lang_code: str
    system_lang_code: str


def _env_int(name: str) -> int | None:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate TELEGRAM_GIFTS_USERBOT_SESSION without interactive input() calls."
        ),
    )
    parser.add_argument(
        "--api-id",
        type=int,
        default=_env_int("TELEGRAM_GIFTS_USERBOT_API_ID"),
        help="Telegram API ID (or TELEGRAM_GIFTS_USERBOT_API_ID env).",
    )
    parser.add_argument(
        "--api-hash",
        default=(os.getenv("TELEGRAM_GIFTS_USERBOT_API_HASH") or "").strip(),
        help="Telegram API hash (or TELEGRAM_GIFTS_USERBOT_API_HASH env).",
    )
    parser.add_argument(
        "--phone",
        required=True,
        help="Phone in international format, for example +380XXXXXXXXX.",
    )
    parser.add_argument(
        "--code",
        help="Login code from Telegram app/SMS. If omitted, script only sends code.",
    )
    parser.add_argument(
        "--phone-code-hash",
        help="Value returned by 'send-code' step: PHONE_CODE_HASH.",
    )
    parser.add_argument(
        "--password",
        default="",
        help="2FA password (if enabled).",
    )
    parser.add_argument(
        "--state-file",
        default=".telegram_gifts_userbot_login_state.json",
        help=(
            "Path to temporary login state file used between step 1 and step 2."
        ),
    )
    parser.add_argument(
        "--device-model",
        default=(os.getenv("TELEGRAM_GIFTS_USERBOT_DEVICE_MODEL") or "TTStars Gifts Userbot"),
    )
    parser.add_argument(
        "--system-version",
        default=(os.getenv("TELEGRAM_GIFTS_USERBOT_SYSTEM_VERSION") or "Linux"),
    )
    parser.add_argument(
        "--app-version",
        default=(os.getenv("TELEGRAM_GIFTS_USERBOT_APP_VERSION") or "TTStars/1.0"),
    )
    parser.add_argument(
        "--lang-code",
        default=(os.getenv("TELEGRAM_GIFTS_USERBOT_LANG_CODE") or "en"),
    )
    parser.add_argument(
        "--system-lang-code",
        default=(os.getenv("TELEGRAM_GIFTS_USERBOT_SYSTEM_LANG_CODE") or "en"),
    )
    return parser


def _build_config(args: argparse.Namespace) -> UserbotConfig:
    if not args.api_id:
        raise ValueError(
            "Missing --api-id (or TELEGRAM_GIFTS_USERBOT_API_ID).",
        )
    api_hash = (args.api_hash or "").strip()
    if not api_hash:
        raise ValueError(
            "Missing --api-hash (or TELEGRAM_GIFTS_USERBOT_API_HASH).",
        )
    return UserbotConfig(
        api_id=args.api_id,
        api_hash=api_hash,
        device_model=(args.device_model or "TTStars Gifts Userbot").strip(),
        system_version=(args.system_version or "Linux").strip(),
        app_version=(args.app_version or "TTStars/1.0").strip(),
        lang_code=(args.lang_code or "en").strip(),
        system_lang_code=(args.system_lang_code or "en").strip(),
    )


def _build_client(config: UserbotConfig) -> TelegramClient:
    return TelegramClient(
        StringSession(),
        config.api_id,
        config.api_hash,
        device_model=config.device_model,
        system_version=config.system_version,
        app_version=config.app_version,
        lang_code=config.lang_code,
        system_lang_code=config.system_lang_code,
    )


def _build_client_with_session(config: UserbotConfig, session: str) -> TelegramClient:
    return TelegramClient(
        StringSession(session),
        config.api_id,
        config.api_hash,
        device_model=config.device_model,
        system_version=config.system_version,
        app_version=config.app_version,
        lang_code=config.lang_code,
        system_lang_code=config.system_lang_code,
    )


def _read_state(state_path: Path) -> dict[str, str] | None:
    if not state_path.exists():
        return None
    raw = state_path.read_text(encoding="utf-8").strip()
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    result: dict[str, str] = {}
    for key in ("phone", "phone_code_hash", "login_session"):
        value = payload.get(key)
        if isinstance(value, str):
            result[key] = value
    return result


def _write_state(
    state_path: Path,
    *,
    phone: str,
    phone_code_hash: str,
    login_session: str,
) -> None:
    payload = {
        "phone": phone,
        "phone_code_hash": phone_code_hash,
        "login_session": login_session,
    }
    state_path.write_text(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":")),
        encoding="utf-8",
    )


def _out(message: str) -> None:
    sys.stdout.write(f"{message}\n")


def _err(message: str) -> None:
    sys.stderr.write(f"{message}\n")


async def _run(args: argparse.Namespace) -> int:  # noqa: C901
    try:
        config = _build_config(args)
    except ValueError as error:
        _err(f"Error: {error}")
        return 2

    state_path = Path(args.state_file).expanduser().resolve()
    state_payload = _read_state(state_path)

    if not args.code:
        client = _build_client(config)
    else:
        login_session = ""
        if state_payload is not None:
            login_session = (state_payload.get("login_session") or "").strip()
        if not login_session:
            _err(
                f"Error: state file not found or invalid: {state_path}. "
                "Run step 1 first (without --code)."
            )
            return 2
        client = _build_client_with_session(config, login_session)

    await client.connect()
    try:
        if not args.code:
            sent = await client.send_code_request(phone=args.phone)
            login_session = client.session.save()
            if not login_session:
                _err("Error: failed to store temporary login session.")
                return 1
            _write_state(
                state_path,
                phone=args.phone,
                phone_code_hash=sent.phone_code_hash,
                login_session=login_session,
            )
            _out("Code sent.")
            _out(f"STATE_FILE={state_path}")
            _out("Run again with --code to generate final session.")
            return 0

        phone_code_hash = ""
        if state_payload is not None:
            phone_code_hash = (state_payload.get("phone_code_hash") or "").strip()
            state_phone = (state_payload.get("phone") or "").strip()
            if state_phone and state_phone != args.phone:
                _err("Error: --phone does not match phone from state file.")
                return 2
        if not phone_code_hash:
            phone_code_hash = (args.phone_code_hash or "").strip()
        if not phone_code_hash:
            _err("Error: missing phone_code_hash in state.")
            return 2

        try:
            await client.sign_in(
                phone=args.phone,
                code=args.code,
                phone_code_hash=phone_code_hash,
            )
        except SessionPasswordNeededError:
            password = (args.password or "").strip()
            if not password:
                _err("Error: 2FA is enabled, provide --password.")
                return 2
            await client.sign_in(password=password)

        session = client.session.save()
        if not session:
            _err("Error: failed to generate session string.")
            return 1
        if state_path.exists():
            state_path.unlink()
        _out(f"TELEGRAM_GIFTS_USERBOT_SESSION={session}")
        return 0
    except ApiIdInvalidError:
        _err("Error: invalid API ID or API hash.")
        return 2
    except PhoneCodeInvalidError:
        _err("Error: invalid confirmation code.")
        return 2
    except PhoneCodeExpiredError:
        _err("Error: code expired. Request a new one.")
        return 2
    except PasswordHashInvalidError:
        _err("Error: invalid 2FA password.")
        return 2
    finally:
        await client.disconnect()


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    exit_code = asyncio.run(_run(args))
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
