from __future__ import annotations

import asyncio
from dataclasses import dataclass, replace
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlparse

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram_i18n import I18nContext

from app.services.crud.user import UserService
from app.utils.localization import normalize_i18n_locale
from app.utils.time import datetime_now

_MAX_BROADCAST_BUTTONS = 8
_MAX_BROADCAST_BUTTON_TEXT = 64
_CLOSE_NOTICE_CALLBACK = "storefront_close_result_notice"
_SKIP_WORDS = {"-", "skip", "пропустить", "пропустити"}
_BROADCAST_CLOSE_TRUE_TOKENS = {"close", "close=yes", "close=true", "with_close"}
_BROADCAST_CLOSE_FALSE_TOKENS = {"no_close", "noclose", "close=no", "close=false", "without_close"}
_BROADCAST_ALL_LOCALES_TOKENS = {"*", "all", "all_locales", "всі", "все", "все_локали"}


@dataclass(frozen=True, slots=True)
class BroadcastButton:
    text: str
    url: str


@dataclass(frozen=True, slots=True)
class BroadcastPayload:
    text_html: str | None
    photo_file_id: str | None
    buttons: list[BroadcastButton]
    target_languages: list[str] | None
    include_close_button: bool


@dataclass(frozen=True, slots=True)
class BroadcastDeliveryResult:
    total: int
    sent: int
    failed: int
    blocked: int


@dataclass(frozen=True, slots=True)
class _ParsedBroadcastOptions:
    locale_values: list[str]
    include_close_button: bool
    use_all_locales: bool


def parse_amount_cents(value: str) -> int | None:
    raw = value.strip().replace(" ", "").replace(",", ".")
    if not raw:
        return None
    try:
        amount = Decimal(raw)
    except InvalidOperation:
        return None
    if amount <= 0:
        return None
    cents = int((amount * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return cents if cents > 0 else None


def parse_user_balance_input(value: str) -> tuple[int, int, bool] | None:
    parts = value.split()
    if len(parts) != 2:
        return None
    user_id_raw, amount_raw = parts
    if not user_id_raw.isdigit():
        return None
    user_id = int(user_id_raw)
    if user_id <= 0:
        return None

    normalized_amount = amount_raw.strip().lower()
    if normalized_amount in {"clear", "reset", "zero", "0"}:
        return user_id, 0, True

    raw = amount_raw.strip().replace(" ", "").replace(",", ".")
    if not raw:
        return None
    try:
        amount = Decimal(raw)
    except InvalidOperation:
        return None
    if amount == 0:
        return None
    cents = int((amount * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    if cents == 0:
        return None
    return user_id, cents, False


def parse_user_lookup_input(value: str) -> int | None:
    raw = value.strip()
    if not raw.isdigit():
        return None
    user_id = int(raw)
    return user_id if user_id > 0 else None


def parse_order_id_input(value: str) -> int | None:
    raw = value.strip()
    if not raw.isdigit():
        return None
    order_id = int(raw)
    return order_id if order_id > 0 else None


def parse_promo_create_input(value: str) -> tuple[str, int, int | None] | None:
    parts = value.split()
    if len(parts) not in {2, 3}:
        return None
    code = parts[0]
    amount_cents = parse_amount_cents(parts[1])
    if amount_cents is None:
        return None
    max_activations: int | None = None
    if len(parts) == 3:
        limit_raw = parts[2]
        if not limit_raw.isdigit():
            return None
        parsed_limit = int(limit_raw)
        if parsed_limit < 0:
            return None
        max_activations = None if parsed_limit == 0 else parsed_limit
    return code, amount_cents, max_activations


def parse_promo_quick_input(value: str) -> tuple[int, int, str] | None:
    parts = value.split()
    if len(parts) not in {2, 3}:
        return None
    amount_cents = parse_amount_cents(parts[0])
    if amount_cents is None:
        return None
    if not parts[1].isdigit():
        return None
    count = int(parts[1])
    if count <= 0:
        return None
    prefix = parts[2] if len(parts) == 3 else "PROMO"
    return amount_cents, count, prefix


def parse_promo_quick_single_input(value: str) -> tuple[int, str] | None:
    parts = value.split()
    if len(parts) not in {1, 2}:
        return None
    amount_cents = parse_amount_cents(parts[0])
    if amount_cents is None:
        return None
    prefix = parts[1] if len(parts) == 2 else "PROMO"
    return amount_cents, prefix


def parse_promo_limit_input(value: str) -> tuple[str, int | None] | None:
    parts = value.split()
    if len(parts) != 2:
        return None
    code = parts[0]
    limit_raw = parts[1]
    if not limit_raw.isdigit():
        return None
    parsed = int(limit_raw)
    if parsed < 0:
        return None
    return code, (None if parsed == 0 else parsed)


def parse_promo_limit_value(value: str) -> int | None:
    raw = value.strip()
    if not raw.isdigit():
        return None
    parsed = int(raw)
    if parsed < 0:
        return None
    return parsed


def extract_broadcast_payload(message: Message) -> BroadcastPayload | None:
    text_html: str | None = None
    raw_html_text = getattr(message, "html_text", None)
    if isinstance(raw_html_text, str) and raw_html_text.strip():
        text_html = raw_html_text
    elif isinstance(message.caption, str) and message.caption.strip():
        text_html = message.caption
    elif isinstance(message.text, str) and message.text.strip():
        text_html = message.text

    if message.photo:
        return BroadcastPayload(
            text_html=text_html,
            photo_file_id=message.photo[-1].file_id,
            buttons=[],
            target_languages=None,
            include_close_button=False,
        )
    if text_html is None:
        return None
    return BroadcastPayload(
        text_html=text_html,
        photo_file_id=None,
        buttons=[],
        target_languages=None,
        include_close_button=False,
    )


def parse_link_buttons(value: str) -> list[BroadcastButton]:
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    if not lines:
        return []
    if len(lines) > _MAX_BROADCAST_BUTTONS:
        raise ValueError(f"Too many buttons, max {_MAX_BROADCAST_BUTTONS}.")

    result: list[BroadcastButton] = []
    for line in lines:
        text_part: str
        url_part: str
        if "|" in line:
            text_part, url_part = line.split("|", 1)
        elif " - " in line:
            text_part, url_part = line.split(" - ", 1)
        elif " — " in line:
            text_part, url_part = line.split(" — ", 1)
        else:
            raise ValueError("Use `Text | URL` or `Text - URL` format.")

        text = text_part.strip()
        if not text:
            raise ValueError("Button text cannot be empty.")
        if len(text) > _MAX_BROADCAST_BUTTON_TEXT:
            raise ValueError(
                f"Button text is too long (max {_MAX_BROADCAST_BUTTON_TEXT} chars).",
            )
        normalized_url = normalize_url(url_part)
        if normalized_url is None:
            raise ValueError(f"Invalid URL: {url_part.strip()}")

        result.append(BroadcastButton(text=text, url=normalized_url))
    return result


def normalize_url(value: str) -> str | None:
    url = value.strip()
    if not url:
        return None
    if url.startswith("t.me/") or url.startswith("telegram.me/"):
        url = f"https://{url}"
    elif not url.startswith("http://") and not url.startswith("https://"):
        if "." not in url:
            return None
        url = f"https://{url}"

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return None
    if not parsed.netloc:
        return None
    return url


def payload_with_buttons(
    payload: BroadcastPayload,
    buttons: list[BroadcastButton],
) -> BroadcastPayload:
    return replace(payload, buttons=buttons)


def payload_to_state(payload: BroadcastPayload) -> dict[str, Any]:
    return {
        "text_html": payload.text_html,
        "photo_file_id": payload.photo_file_id,
        "buttons": [{"text": button.text, "url": button.url} for button in payload.buttons],
        "target_languages": payload.target_languages,
        "include_close_button": payload.include_close_button,
    }


def _extract_buttons_from_state(raw_buttons: Any) -> list[BroadcastButton]:
    if not isinstance(raw_buttons, list):
        return []
    buttons: list[BroadcastButton] = []
    for item in raw_buttons:
        if not isinstance(item, dict):
            continue
        text = item.get("text")
        url = item.get("url")
        if isinstance(text, str) and isinstance(url, str) and text and url:
            buttons.append(BroadcastButton(text=text, url=url))
    return buttons


def _normalize_optional_text(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value
    return None


def _extract_target_languages(raw_target_languages: Any) -> list[str] | None:
    if not isinstance(raw_target_languages, list):
        return None
    parsed_languages: list[str] = []
    seen_languages: set[str] = set()
    for item in raw_target_languages:
        if not isinstance(item, str):
            continue
        value = item.strip().lower()
        if not value or value in seen_languages:
            continue
        seen_languages.add(value)
        parsed_languages.append(value)
    return parsed_languages or None


def payload_from_state(data: dict[str, Any]) -> BroadcastPayload | None:
    text_normalized = _normalize_optional_text(data.get("text_html"))
    photo_normalized = _normalize_optional_text(data.get("photo_file_id"))

    if text_normalized is None and photo_normalized is None:
        return None
    return BroadcastPayload(
        text_html=text_normalized,
        photo_file_id=photo_normalized,
        buttons=_extract_buttons_from_state(data.get("buttons")),
        target_languages=_extract_target_languages(data.get("target_languages")),
        include_close_button=bool(data.get("include_close_button", False)),
    )


def build_link_keyboard(
    buttons: list[BroadcastButton],
    *,
    close_button_text: str | None = None,
) -> InlineKeyboardMarkup | None:
    if not buttons and close_button_text is None:
        return None
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=button.text, url=button.url)] for button in buttons
    ]
    if close_button_text is not None:
        rows.append(
            [InlineKeyboardButton(text=close_button_text, callback_data=_CLOSE_NOTICE_CALLBACK)],
        )
    return InlineKeyboardMarkup(
        inline_keyboard=rows,
    )


async def send_broadcast_preview(
    *,
    bot: Bot,
    i18n: I18nContext,
    chat_id: int,
    payload: BroadcastPayload,
) -> None:
    await _send_payload(
        bot=bot,
        chat_id=chat_id,
        payload=payload,
        reply_markup=build_link_keyboard(
            payload.buttons,
            close_button_text=(
                _close_notice_button_text(i18n=i18n, language="en")
                if payload.include_close_button
                else None
            ),
        ),
    )


async def deliver_broadcast(
    *,
    bot: Bot,
    i18n: I18nContext,
    user_service: UserService,
    payload: BroadcastPayload,
    target_languages: list[str] | None = None,
    include_close_button: bool = False,
    batch_size: int = 300,
    concurrency: int = 25,
) -> BroadcastDeliveryResult:
    total = await user_service.count_active(locales=target_languages)
    if total <= 0:
        return BroadcastDeliveryResult(total=0, sent=0, failed=0, blocked=0)

    sent = 0
    failed = 0
    blocked = 0
    last_user_id: int | None = None
    while True:
        recipients = await user_service.list_recipients(
            limit=batch_size,
            after_id=last_user_id,
            only_active=True,
            locales=target_languages,
        )
        if not recipients:
            break
        last_user_id = recipients[-1][0]

        for index in range(0, len(recipients), concurrency):
            chunk = recipients[index : index + concurrency]
            results = await asyncio.gather(
                *[
                    _deliver_to_user(
                        bot=bot,
                        i18n=i18n,
                        user_service=user_service,
                        user_id=user_id,
                        language=language,
                        payload=payload,
                        include_close_button=include_close_button,
                    )
                    for user_id, language in chunk
                ]
            )
            for result in results:
                if result == "sent":
                    sent += 1
                elif result == "blocked":
                    blocked += 1
                else:
                    failed += 1

    return BroadcastDeliveryResult(total=total, sent=sent, failed=failed, blocked=blocked)


async def _deliver_to_user(
    *,
    bot: Bot,
    i18n: I18nContext,
    user_service: UserService,
    user_id: int,
    language: str | None,
    payload: BroadcastPayload,
    include_close_button: bool,
) -> str:
    close_button_text = (
        _close_notice_button_text(
            i18n=i18n,
            language=language or "en",
        )
        if include_close_button
        else None
    )
    markup = build_link_keyboard(payload.buttons, close_button_text=close_button_text)
    try:
        await _send_payload(
            bot=bot,
            chat_id=user_id,
            payload=payload,
            reply_markup=markup,
        )
    except TelegramRetryAfter as error:
        await asyncio.sleep(float(error.retry_after) + 0.1)
        try:
            await _send_payload(
                bot=bot,
                chat_id=user_id,
                payload=payload,
                reply_markup=markup,
            )
        except TelegramForbiddenError:
            await user_service.set_blocked_at(user_id=user_id, blocked_at=datetime_now())
            return "blocked"
        except Exception:
            return "failed"
        return "sent"
    except TelegramForbiddenError:
        await user_service.set_blocked_at(user_id=user_id, blocked_at=datetime_now())
        return "blocked"
    except Exception:
        return "failed"
    return "sent"


async def _send_payload(
    *,
    bot: Bot,
    chat_id: int,
    payload: BroadcastPayload,
    reply_markup: InlineKeyboardMarkup | None,
) -> None:
    if payload.photo_file_id is not None:
        await bot.send_photo(
            chat_id=chat_id,
            photo=payload.photo_file_id,
            caption=payload.text_html,
            parse_mode="HTML" if payload.text_html else None,
            reply_markup=reply_markup,
        )
        return

    if payload.text_html is None:
        raise ValueError("Broadcast payload has neither text nor photo.")
    await bot.send_message(
        chat_id=chat_id,
        text=payload.text_html,
        parse_mode="HTML",
        reply_markup=reply_markup,
        disable_web_page_preview=False,
    )


def parse_broadcast_options_input(
    *,
    value: str,
    available_locales: list[str],
) -> tuple[list[str] | None, bool]:
    normalized_available = _normalize_available_locales(available_locales)
    available_set = set(normalized_available)
    if not available_set:
        raise ValueError("No locales configured for broadcast.")

    raw = value.strip().lower()
    if not raw or raw in _SKIP_WORDS:
        return None, False

    tokens = _tokenize_options_input(raw)
    if not tokens:
        return None, False

    parsed = _parse_broadcast_options_tokens(tokens=tokens, available_set=available_set)
    if parsed.use_all_locales:
        return None, parsed.include_close_button
    if not parsed.locale_values:
        raise ValueError("Specify at least one locale or use `all`.")

    deduped_locales: list[str] = []
    selected_set = set(parsed.locale_values)
    for locale in normalized_available:
        if locale in selected_set:
            deduped_locales.append(locale)
    return deduped_locales, parsed.include_close_button


def _parse_broadcast_options_tokens(
    *,
    tokens: list[str],
    available_set: set[str],
) -> _ParsedBroadcastOptions:
    include_close_button = False
    use_all_locales = False
    locale_values: list[str] = []
    for token in tokens:
        token_kind = _classify_broadcast_option_token(token=token, available_set=available_set)
        if token_kind == "close_true":
            include_close_button = True
        elif token_kind == "close_false":
            include_close_button = False
        elif token_kind == "all_locales":
            use_all_locales = True
        elif token_kind == "locale":
            locale_values.append(token)
        else:
            raise ValueError(f"Unsupported token kind: {token_kind}")
    return _ParsedBroadcastOptions(
        locale_values=locale_values,
        include_close_button=include_close_button,
        use_all_locales=use_all_locales,
    )


def _classify_broadcast_option_token(*, token: str, available_set: set[str]) -> str:
    if token in available_set:
        return "locale"
    if token in _BROADCAST_CLOSE_TRUE_TOKENS:
        return "close_true"
    if token in _BROADCAST_CLOSE_FALSE_TOKENS:
        return "close_false"
    if token in _BROADCAST_ALL_LOCALES_TOKENS:
        return "all_locales"
    raise ValueError(f"Unknown token: {token}")


def _normalize_available_locales(available_locales: list[str]) -> list[str]:
    normalized_available: list[str] = []
    seen_locales: set[str] = set()
    for locale in available_locales:
        key = locale.strip().lower()
        if not key or key in seen_locales:
            continue
        seen_locales.add(key)
        normalized_available.append(key)
    return normalized_available


def _tokenize_options_input(value: str) -> list[str]:
    tokens: list[str] = []
    for chunk in value.replace("\n", " ").split():
        parts = [item.strip() for item in chunk.split(",") if item.strip()]
        tokens.extend(parts if parts else [chunk.strip()])
    return tokens


def _close_notice_button_text(*, i18n: I18nContext, language: str) -> str:
    locale = normalize_i18n_locale(language, fallback="en")
    return i18n.get("messages-admin_broadcast_close_button", locale)


def format_dt(dt: datetime) -> str:
    return dt.astimezone().strftime("%Y-%m-%d %H:%M")
