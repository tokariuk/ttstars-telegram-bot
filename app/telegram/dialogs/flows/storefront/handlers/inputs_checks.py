from __future__ import annotations

import contextlib
from typing import Any

from aiogram import Bot, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputRichMessage,
    Message,
)
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_i18n import I18nContext

from app.services.crud.check import CheckClaimOutcome
from app.services.crud.check import InsufficientBalanceError as CheckInsufficientBalanceError
from app.services.crud.check import ValidationError as CheckValidationError
from app.stars import normalize_recipient_username, parse_stars_count, price_usd_for_cents
from app.telegram.dialogs.common import get_i18n, get_user, normalize_i18n_locale

from ..states import StorefrontSG
from .shared import (
    MAX_STARS_COUNT,
    MIN_STARS_COUNT,
    check_service,
    checks_create_claim_password,
    checks_create_claim_username,
    checks_create_stars_count,
    clear_checks_create_draft,
    clear_notice,
    selected_check_id,
    set_checks_create_claim_password,
    set_checks_create_claim_username,
    set_checks_create_stars_count,
    set_notice,
    set_selected_check_id,
    user_service,
)


async def _delete_user_message(message: Message) -> None:
    with contextlib.suppress(TelegramBadRequest):
        await message.delete()


async def _notify_check_created(
    *,
    dialog_manager: DialogManager,
    check_id: int,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    clear_checks_create_draft(dialog_manager)
    set_notice(dialog_manager, str(i18n.messages.check_create_done()))
    set_selected_check_id(dialog_manager, check_id)
    await dialog_manager.switch_to(StorefrontSG.checks_details, show_mode=ShowMode.EDIT)


def _check_claim_notice(
    *,
    i18n: Any,
    outcome: CheckClaimOutcome,
    stars_count: int,
    tx_hash: str,
) -> str:
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


def _close_notice_button_text(*, i18n: I18nContext, language: str) -> str:
    with i18n.use_locale(normalize_i18n_locale(language)):
        return str(i18n.messages.check_notice_close_button())


def _creator_claim_text(
    *,
    i18n: I18nContext,
    language: str,
    claimer: str,
    stars_count: int,
    amount_usd: str,
) -> str:
    with i18n.use_locale(normalize_i18n_locale(language)):
        return str(
            i18n.messages.check_creator_claimed(
                claimer=html.quote(claimer),
                stars=stars_count,
                amount=amount_usd,
            )
        )


async def _notify_check_creator_claimed(
    *,
    dialog_manager: DialogManager,
    check: Any,
    claimer_label: str,
) -> None:
    if check.creator_id <= 0:
        return
    if check.creator_id == check.recipient_id:
        return

    bot = dialog_manager.middleware_data.get("bot") or dialog_manager.middleware_data.get(
        "event_bot"
    )
    if not isinstance(bot, Bot):
        return

    i18n = get_i18n(dialog_manager=dialog_manager)
    creator = await user_service(dialog_manager=dialog_manager).get(user_id=check.creator_id)
    language = creator.language if creator is not None else "en"
    with contextlib.suppress(Exception):
        await bot.send_rich_message(
            chat_id=check.creator_id,
            rich_message=InputRichMessage(
                html=_creator_claim_text(
                    i18n=i18n,
                    language=language,
                    claimer=claimer_label,
                    stars_count=check.stars_count,
                    amount_usd=price_usd_for_cents(check.amount_cents),
                ),
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=_close_notice_button_text(i18n=i18n, language=language),
                            callback_data="storefront_close_result_notice",
                        )
                    ]
                ]
            ),
        )


async def _mark_inline_check_claimed(
    *,
    dialog_manager: DialogManager,
    check: Any,
) -> None:
    inline_message_id = getattr(check, "inline_message_id", None)
    if not isinstance(inline_message_id, str) or not inline_message_id:
        return
    bot = dialog_manager.middleware_data.get("bot") or dialog_manager.middleware_data.get(
        "event_bot"
    )
    if not isinstance(bot, Bot):
        return
    i18n = get_i18n(dialog_manager=dialog_manager)
    with contextlib.suppress(Exception):
        await bot.edit_message_reply_markup(
            inline_message_id=inline_message_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=str(i18n.messages.check_inline_received_button()),
                            callback_data="storefront_check_claimed_notice",
                        )
                    ]
                ]
            ),
        )


async def handle_check_stars_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    stars_count = parse_stars_count(message.text or "")
    if stars_count is None:
        set_notice(
            dialog_manager,
            str(
                i18n.messages.check_create_stars_invalid(
                    min_stars=MIN_STARS_COUNT,
                    max_stars=MAX_STARS_COUNT,
                )
            ),
        )
        await dialog_manager.switch_to(StorefrontSG.checks_create_stars, show_mode=ShowMode.EDIT)
        await _delete_user_message(message)
        return

    set_checks_create_stars_count(dialog_manager, stars_count)
    set_checks_create_claim_username(dialog_manager, None)
    set_checks_create_claim_password(dialog_manager, None)
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.checks_create_recipient, show_mode=ShowMode.EDIT)
    await _delete_user_message(message)


async def handle_check_claim_recipient_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    username = normalize_recipient_username(message.text or "")
    if username is None:
        set_notice(dialog_manager, str(i18n.messages.recipient_invalid()))
        await dialog_manager.switch_to(
            StorefrontSG.checks_create_recipient, show_mode=ShowMode.EDIT
        )
        await _delete_user_message(message)
        return

    set_checks_create_claim_username(dialog_manager, username)
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.checks_create_password, show_mode=ShowMode.EDIT)
    await _delete_user_message(message)


async def skip_check_claim_recipient(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_checks_create_claim_username(dialog_manager, None)
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.checks_create_password, show_mode=ShowMode.EDIT)


async def handle_check_claim_password_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    password = (message.text or "").strip()
    if not password:
        set_notice(dialog_manager, str(i18n.messages.check_create_password_invalid()))
        await dialog_manager.switch_to(
            StorefrontSG.checks_create_password, show_mode=ShowMode.EDIT
        )
        await _delete_user_message(message)
        return
    set_checks_create_claim_password(dialog_manager, password)
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.checks_create_confirm, show_mode=ShowMode.EDIT)
    await _delete_user_message(message)


async def skip_check_claim_password(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_checks_create_claim_password(dialog_manager, None)
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.checks_create_confirm, show_mode=ShowMode.EDIT)


async def confirm_check_create(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    stars_count = checks_create_stars_count(dialog_manager)
    if stars_count is None:
        set_notice(
            dialog_manager,
            str(
                i18n.messages.check_create_stars_invalid(
                    min_stars=MIN_STARS_COUNT,
                    max_stars=MAX_STARS_COUNT,
                )
            ),
        )
        await dialog_manager.switch_to(StorefrontSG.checks_create_stars, show_mode=ShowMode.EDIT)
        return

    try:
        check = await check_service(dialog_manager=dialog_manager).create_stars_check(
            creator_id=user.id,
            stars_count=stars_count,
            claim_username=checks_create_claim_username(dialog_manager),
            claim_password=checks_create_claim_password(dialog_manager),
        )
    except CheckValidationError:
        set_notice(dialog_manager, str(i18n.messages.check_create_failed()))
        await dialog_manager.switch_to(StorefrontSG.checks_create_confirm, show_mode=ShowMode.EDIT)
    except CheckInsufficientBalanceError:
        set_notice(dialog_manager, str(i18n.messages.balance_not_enough()))
        await dialog_manager.switch_to(StorefrontSG.checks_create_confirm, show_mode=ShowMode.EDIT)
    else:
        await _notify_check_created(
            dialog_manager=dialog_manager,
            check_id=check.id,
        )


async def handle_check_edit_recipient_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    check_id = selected_check_id(dialog_manager)
    if check_id is None:
        set_notice(dialog_manager, str(i18n.messages.check_detail_not_found()))
        await dialog_manager.switch_to(StorefrontSG.checks_list, show_mode=ShowMode.EDIT)
        await _delete_user_message(message)
        return

    username = normalize_recipient_username(message.text or "")
    if username is None:
        set_notice(dialog_manager, str(i18n.messages.recipient_invalid()))
        await dialog_manager.switch_to(StorefrontSG.checks_edit_recipient, show_mode=ShowMode.EDIT)
        await _delete_user_message(message)
        return

    updated = await check_service(dialog_manager=dialog_manager).update_claim_username(
        creator_id=user.id,
        check_id=check_id,
        claim_username=username,
    )
    if updated is None:
        set_notice(dialog_manager, str(i18n.messages.check_detail_not_found()))
        await dialog_manager.switch_to(StorefrontSG.checks_list, show_mode=ShowMode.EDIT)
    else:
        set_notice(dialog_manager, str(i18n.messages.check_settings_recipient_saved()))
        await dialog_manager.switch_to(StorefrontSG.checks_settings, show_mode=ShowMode.EDIT)
    await _delete_user_message(message)


async def handle_check_edit_password_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    check_id = selected_check_id(dialog_manager)
    if check_id is None:
        set_notice(dialog_manager, str(i18n.messages.check_detail_not_found()))
        await dialog_manager.switch_to(StorefrontSG.checks_list, show_mode=ShowMode.EDIT)
        await _delete_user_message(message)
        return

    password = (message.text or "").strip()
    if not password:
        set_notice(dialog_manager, str(i18n.messages.check_create_password_invalid()))
        await dialog_manager.switch_to(StorefrontSG.checks_edit_password, show_mode=ShowMode.EDIT)
        await _delete_user_message(message)
        return

    try:
        updated = await check_service(dialog_manager=dialog_manager).update_claim_password(
            creator_id=user.id,
            check_id=check_id,
            claim_password=password,
        )
    except CheckValidationError:
        set_notice(dialog_manager, str(i18n.messages.check_create_password_invalid()))
        await dialog_manager.switch_to(StorefrontSG.checks_edit_password, show_mode=ShowMode.EDIT)
        await _delete_user_message(message)
        return

    if updated is None:
        set_notice(dialog_manager, str(i18n.messages.check_detail_not_found()))
        await dialog_manager.switch_to(StorefrontSG.checks_list, show_mode=ShowMode.EDIT)
    else:
        set_notice(dialog_manager, str(i18n.messages.check_settings_password_saved()))
        await dialog_manager.switch_to(StorefrontSG.checks_settings, show_mode=ShowMode.EDIT)
    await _delete_user_message(message)


async def handle_check_activation_password_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    start_data = dialog_manager.start_data if isinstance(dialog_manager.start_data, dict) else {}
    check_code_raw = start_data.get("check_code")
    check_code = check_code_raw.strip().lower() if isinstance(check_code_raw, str) else ""
    if not check_service(dialog_manager=dialog_manager).is_valid_code(check_code):
        set_notice(dialog_manager, str(i18n.messages.check_claim_not_found()))
        await dialog_manager.switch_to(StorefrontSG.menu, show_mode=ShowMode.EDIT)
        await _delete_user_message(message)
        return

    claim_password = (message.text or "").strip()
    result = await check_service(dialog_manager=dialog_manager).claim_check(
        code=check_code,
        recipient_user_id=user.id,
        recipient_username=message.from_user.username if message.from_user else None,
        claim_password=claim_password,
    )
    check = result.check
    tx_hash = result.tx_hash or (check.provider_tx_hash if check else None) or "—"
    if result.outcome in {
        CheckClaimOutcome.PASSWORD_REQUIRED,
        CheckClaimOutcome.PASSWORD_INVALID,
    }:
        set_notice(
            dialog_manager,
            _check_claim_notice(
                i18n=i18n,
                outcome=result.outcome,
                stars_count=check.stars_count if check is not None else 0,
                tx_hash=tx_hash,
            ),
        )
        await dialog_manager.switch_to(StorefrontSG.checks_claim_password, show_mode=ShowMode.EDIT)
        await _delete_user_message(message)
        return

    if result.outcome == CheckClaimOutcome.CLAIMED and check is not None:
        claimer_label = (
            f"@{message.from_user.username}"
            if message.from_user and message.from_user.username
            else (message.from_user.full_name if message.from_user else str(user.id))
        )
        await _notify_check_creator_claimed(
            dialog_manager=dialog_manager,
            check=check,
            claimer_label=claimer_label,
        )
        await _mark_inline_check_claimed(
            dialog_manager=dialog_manager,
            check=check,
        )

    set_notice(
        dialog_manager,
        _check_claim_notice(
            i18n=i18n,
            outcome=result.outcome,
            stars_count=check.stars_count if check is not None else 0,
            tx_hash=tx_hash,
        ),
    )
    await dialog_manager.switch_to(StorefrontSG.menu, show_mode=ShowMode.EDIT)
    await _delete_user_message(message)
