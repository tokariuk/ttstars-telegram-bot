from __future__ import annotations

import contextlib
import json
import re
from dataclasses import dataclass
from typing import Final
from uuid import uuid4

from aiogram import Bot, html
from aiogram.types import (
    ChosenInlineResult,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputRichMessage,
)
from aiogram_i18n import I18nContext

from app.models.dto.check import CheckDto
from app.services.crud.check import CheckClaimOutcome, CheckService
from app.services.crud.user import UserService
from app.stars import price_usd_for_cents
from app.telegram.dialogs.common import normalize_i18n_locale
from app.utils.key_builder import build_key

from ..check_card import build_check_card_preview_url

INLINE_DRAFT_TTL_SECONDS: Final[int] = 30 * 60
INLINE_CREATE_RESULT_RE = re.compile(r"^check:create:([a-f0-9]{16})$")
INLINE_SHARE_RESULT_RE = re.compile(r"^check:share:([a-f0-9]{16})$")
INLINE_SHARE_QUERY_RE = re.compile(r"^c_([a-f0-9]{16})$")
CLOSE_NOTICE_CALLBACK: Final[str] = "storefront_close_result_notice"
CHECK_CLAIMED_NOOP_CALLBACK: Final[str] = "storefront_check_claimed_notice"
CHECK_PENDING_NOOP_CALLBACK: Final[str] = "storefront_check_pending_notice"


@dataclass(frozen=True, slots=True)
class InlineCheckDraftRecord:
    creator_id: int
    stars_count: int
    amount_cents: int


def inline_draft_key(*, nonce: str) -> str:
    return build_key("inline_check_draft", nonce=nonce)


def parse_inline_create_result_id(result_id: str) -> str | None:
    match = INLINE_CREATE_RESULT_RE.fullmatch(result_id.strip())
    if match is None:
        return None
    return match.group(1)


def parse_inline_share_result_id(result_id: str) -> str | None:
    match = INLINE_SHARE_RESULT_RE.fullmatch(result_id.strip())
    if match is None:
        return None
    return match.group(1)


def parse_inline_share_query(query: str) -> str | None:
    match = INLINE_SHARE_QUERY_RE.fullmatch(query.strip().lower())
    if match is None:
        return None
    return match.group(1)


def decode_inline_draft_record(raw: bytes | str | None) -> InlineCheckDraftRecord | None:
    if raw is None:
        return None
    try:
        decoded = raw.decode() if isinstance(raw, bytes) else raw
        payload = json.loads(decoded)
        creator_id = int(payload["creator_id"])
        stars_count = int(payload["stars_count"])
        amount_cents = int(payload["amount_cents"])
    except Exception:
        return None
    if creator_id <= 0 or stars_count <= 0 or amount_cents <= 0:
        return None
    return InlineCheckDraftRecord(
        creator_id=creator_id,
        stars_count=stars_count,
        amount_cents=amount_cents,
    )


async def store_inline_draft(
    *,
    check_service: CheckService,
    creator_id: int,
    stars_count: int,
    amount_cents: int,
) -> str:
    nonce = uuid4().hex[:16]
    payload = json.dumps(
        {
            "creator_id": creator_id,
            "stars_count": stars_count,
            "amount_cents": amount_cents,
        }
    )
    await check_service.redis.set(
        inline_draft_key(nonce=nonce),
        payload,
        ex=INLINE_DRAFT_TTL_SECONDS,
    )
    return nonce


async def consume_inline_draft_record(
    *,
    check_service: CheckService,
    nonce: str,
) -> InlineCheckDraftRecord | None:
    raw = await check_service.redis.getdel(inline_draft_key(nonce=nonce))
    return decode_inline_draft_record(raw)


def card_preview_url(
    *,
    stars_count: int,
    amount_usd: str,
    seed: str,
    base_url: str | None,
) -> str:
    return build_check_card_preview_url(
        stars_count=stars_count,
        amount_usd=amount_usd,
        seed=seed,
        base_url=base_url,
    )


def activate_markup(*, i18n: I18nContext, activate_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=str(i18n.buttons.checks_activate()),
                    url=activate_url,
                )
            ],
        ]
    )


def claimed_markup(*, i18n: I18nContext) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=str(i18n.messages.check_inline_received_button()),
                    callback_data=CHECK_CLAIMED_NOOP_CALLBACK,
                )
            ],
        ]
    )


def pending_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏳",
                    callback_data=CHECK_PENDING_NOOP_CALLBACK,
                )
            ]
        ]
    )


def inline_check_message_text(
    *,
    i18n: I18nContext,
    image_url: str,
    check: CheckDto,
) -> str:
    if not check.claim_username:
        return str(
            i18n.messages.check_inline_card_message_any(
                image_url=image_url,
                stars=check.stars_count,
                amount=price_usd_for_cents(check.amount_cents),
            )
        )
    return str(
        i18n.messages.check_inline_card_message(
            image_url=image_url,
            stars=check.stars_count,
            amount=price_usd_for_cents(check.amount_cents),
            target=f"@{check.claim_username}",
        )
    )


async def send_inline_fallback_message(
    *,
    event: ChosenInlineResult,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    bot = event.bot
    if not isinstance(bot, Bot):
        return
    await bot.send_message(
        chat_id=event.from_user.id,
        text=text,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


def claim_notice(*, i18n: I18nContext, check: CheckDto | None, outcome: CheckClaimOutcome) -> str:
    tx_hash = check.provider_tx_hash if check is not None and check.provider_tx_hash else "—"
    stars_count = check.stars_count if check is not None else 0
    if outcome == CheckClaimOutcome.CLAIMED:
        return str(i18n.messages.check_claim_done_stars(stars=stars_count, tx_hash=tx_hash))

    static_notices: dict[CheckClaimOutcome, str] = {
        CheckClaimOutcome.ALREADY_REDEEMED: str(i18n.messages.check_claim_already_redeemed()),
        CheckClaimOutcome.ALREADY_CLOSED: str(i18n.messages.check_claim_already_closed()),
        CheckClaimOutcome.USERNAME_REQUIRED: str(i18n.messages.check_claim_username_required()),
        CheckClaimOutcome.RECIPIENT_MISMATCH: str(i18n.messages.check_claim_recipient_mismatch()),
        CheckClaimOutcome.PASSWORD_REQUIRED: str(i18n.messages.check_claim_password_required()),
        CheckClaimOutcome.PASSWORD_INVALID: str(i18n.messages.check_claim_password_invalid()),
        CheckClaimOutcome.DELIVERY_UNAVAILABLE: str(
            i18n.messages.check_claim_delivery_unavailable()
        ),
        CheckClaimOutcome.DELIVERY_FAILED: str(i18n.messages.check_claim_delivery_failed()),
        CheckClaimOutcome.PROCESSING: str(i18n.messages.check_claim_processing()),
    }
    if outcome in static_notices:
        return static_notices[outcome]
    return str(i18n.messages.check_claim_not_found())


def close_notice_button_text(*, i18n: I18nContext, language: str) -> str:
    with i18n.use_locale(normalize_i18n_locale(language)):
        return str(i18n.messages.check_notice_close_button())


def creator_claim_text(
    *,
    i18n: I18nContext,
    language: str,
    claimer: str,
    check: CheckDto,
) -> str:
    amount_usd = price_usd_for_cents(check.amount_cents)
    with i18n.use_locale(normalize_i18n_locale(language)):
        return str(
            i18n.messages.check_creator_claimed(
                claimer=html.quote(claimer),
                stars=check.stars_count,
                amount=amount_usd,
            )
        )


async def notify_creator_claimed(
    *,
    bot: Bot,
    i18n: I18nContext,
    user_service: UserService,
    check: CheckDto,
    claimer_label: str,
) -> None:
    if check.creator_id == check.recipient_id:
        return
    creator = await user_service.get(user_id=check.creator_id)
    language = creator.language if creator is not None else "en"
    with contextlib.suppress(Exception):
        await bot.send_rich_message(
            chat_id=check.creator_id,
            rich_message=InputRichMessage(
                html=creator_claim_text(
                    i18n=i18n,
                    language=language,
                    claimer=claimer_label,
                    check=check,
                ),
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=close_notice_button_text(i18n=i18n, language=language),
                            callback_data=CLOSE_NOTICE_CALLBACK,
                        )
                    ]
                ]
            ),
        )


async def mark_inline_claimed(
    *,
    bot: Bot,
    i18n: I18nContext,
    check: CheckDto,
) -> None:
    if not check.inline_message_id:
        return
    with contextlib.suppress(Exception):
        await bot.edit_message_reply_markup(
            inline_message_id=check.inline_message_id,
            reply_markup=claimed_markup(i18n=i18n),
        )

