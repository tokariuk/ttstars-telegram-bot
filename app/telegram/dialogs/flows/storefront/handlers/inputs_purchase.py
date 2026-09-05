from __future__ import annotations

import contextlib

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from app.gifts import get_gift_pack
from app.stars import (
    get_premium_pack,
    get_stars_pack,
    normalize_recipient_username,
    parse_stars_count,
    price_usd_for_cents,
)
from app.telegram.dialogs.common import get_i18n

from ..states import StorefrontSG
from .shared import (
    MAX_GIFT_MESSAGE_LENGTH,
    MAX_STARS_COUNT,
    MAX_TOPUP_CENTS,
    MIN_STARS_COUNT,
    MIN_TOPUP_CENTS,
    PREMIUM_RECIPIENT_USERNAME_KEY,
    SELECTED_PREMIUM_MONTHS_KEY,
    SELECTED_STARS_COUNT_KEY,
    STARS_RECIPIENT_USERNAME_KEY,
    TOPUP_AMOUNT_CENTS_KEY,
    clear_notice,
    parse_topup_amount_cents,
    selected_gift_key,
    selected_gift_recipient_username,
    set_notice,
    set_selected_gift_key,
    set_selected_gift_message,
    set_selected_gift_recipient_user_id,
    set_selected_gift_recipient_username,
    set_selected_gift_sender_private,
)


async def _delete_user_message(message: Message) -> None:
    with contextlib.suppress(TelegramBadRequest):
        await message.delete()


async def handle_stars_count_input(
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
                i18n.messages.stars_count_invalid(
                    min_stars=MIN_STARS_COUNT,
                    max_stars=MAX_STARS_COUNT,
                )
            ),
        )
        await dialog_manager.switch_to(StorefrontSG.stars_amount, show_mode=ShowMode.EDIT)
    else:
        dialog_manager.dialog_data[SELECTED_STARS_COUNT_KEY] = str(stars_count)
        clear_notice(dialog_manager)
        await dialog_manager.switch_to(StorefrontSG.stars_payment, show_mode=ShowMode.EDIT)
    await _delete_user_message(message)


async def handle_stars_recipient_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    username = normalize_recipient_username(message.text or "")
    if username is None:
        set_notice(dialog_manager, str(i18n.messages.recipient_invalid()))
        await dialog_manager.switch_to(StorefrontSG.stars_recipient, show_mode=ShowMode.EDIT)
    else:
        dialog_manager.dialog_data[STARS_RECIPIENT_USERNAME_KEY] = username
        clear_notice(dialog_manager)
        await dialog_manager.switch_to(StorefrontSG.stars_amount, show_mode=ShowMode.EDIT)
    await _delete_user_message(message)


async def buy_stars_for_self(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    raw_username = callback.from_user.username if callback.from_user is not None else None
    username = normalize_recipient_username(raw_username or "")
    if username is None:
        set_notice(dialog_manager, str(i18n.messages.recipient_self_missing()))
        await dialog_manager.switch_to(StorefrontSG.stars_recipient, show_mode=ShowMode.EDIT)
        return

    dialog_manager.dialog_data[STARS_RECIPIENT_USERNAME_KEY] = username
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.stars_amount, show_mode=ShowMode.EDIT)


async def select_premium_3_months(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    await _select_premium_months(dialog_manager=dialog_manager, months=3)


async def select_premium_6_months(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    await _select_premium_months(dialog_manager=dialog_manager, months=6)


async def select_premium_12_months(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    await _select_premium_months(dialog_manager=dialog_manager, months=12)


async def _select_premium_months(
    *,
    dialog_manager: DialogManager,
    months: int,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    try:
        pack = get_premium_pack(months=months)
    except ValueError:
        set_notice(dialog_manager, str(i18n.messages.premium_plan_invalid()))
        await dialog_manager.switch_to(StorefrontSG.premium_plans, show_mode=ShowMode.EDIT)
        return

    dialog_manager.dialog_data[SELECTED_PREMIUM_MONTHS_KEY] = pack.months
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.premium_payment, show_mode=ShowMode.EDIT)


async def handle_premium_recipient_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    username = normalize_recipient_username(message.text or "")
    if username is None:
        set_notice(dialog_manager, str(i18n.messages.recipient_invalid()))
        await dialog_manager.switch_to(StorefrontSG.premium_recipient, show_mode=ShowMode.EDIT)
    else:
        dialog_manager.dialog_data[PREMIUM_RECIPIENT_USERNAME_KEY] = username
        clear_notice(dialog_manager)
        await dialog_manager.switch_to(StorefrontSG.premium_plans, show_mode=ShowMode.EDIT)
    await _delete_user_message(message)


async def buy_premium_for_self(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    raw_username = callback.from_user.username if callback.from_user is not None else None
    username = normalize_recipient_username(raw_username or "")
    if username is None:
        set_notice(dialog_manager, str(i18n.messages.recipient_self_missing()))
        await dialog_manager.switch_to(StorefrontSG.premium_recipient, show_mode=ShowMode.EDIT)
        return

    dialog_manager.dialog_data[PREMIUM_RECIPIENT_USERNAME_KEY] = username
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.premium_plans, show_mode=ShowMode.EDIT)


async def handle_topup_amount_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    amount_cents = parse_topup_amount_cents(message.text or "")
    if amount_cents is None:
        set_notice(
            dialog_manager,
            str(
                i18n.messages.topup_amount_invalid(
                    min_amount=price_usd_for_cents(MIN_TOPUP_CENTS),
                    max_amount=price_usd_for_cents(MAX_TOPUP_CENTS),
                )
            ),
        )
        await dialog_manager.switch_to(StorefrontSG.topup_amount, show_mode=ShowMode.EDIT)
    else:
        dialog_manager.dialog_data[TOPUP_AMOUNT_CENTS_KEY] = amount_cents
        clear_notice(dialog_manager)
        await dialog_manager.switch_to(StorefrontSG.topup_payment, show_mode=ShowMode.EDIT)
    await _delete_user_message(message)


async def handle_calculator_input(
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
                i18n.messages.calculator_invalid(
                    min_stars=MIN_STARS_COUNT,
                    max_stars=MAX_STARS_COUNT,
                )
            ),
        )
    else:
        price = get_stars_pack(str(stars_count)).price_usd
        set_notice(
            dialog_manager,
            str(i18n.messages.calculator_result(stars=stars_count, amount=price)),
        )
    await dialog_manager.switch_to(StorefrontSG.calculator, show_mode=ShowMode.EDIT)
    await _delete_user_message(message)


def _resolve_gift_recipient(text: str) -> str | None:
    return normalize_recipient_username(text or "")


async def handle_gift_recipient_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    recipient_username = _resolve_gift_recipient(message.text or "")
    if recipient_username is None:
        set_notice(dialog_manager, str(i18n.messages.gift_recipient_invalid()))
        await dialog_manager.switch_to(StorefrontSG.gifts_recipient, show_mode=ShowMode.EDIT)
    else:
        set_selected_gift_recipient_user_id(dialog_manager, None)
        set_selected_gift_recipient_username(dialog_manager, recipient_username)
        clear_notice(dialog_manager)
        await dialog_manager.switch_to(StorefrontSG.gifts_catalog, show_mode=ShowMode.EDIT)
    await _delete_user_message(message)


async def buy_gift_for_self(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    if callback.from_user is None or callback.from_user.id <= 0:
        set_notice(dialog_manager, str(i18n.messages.gift_recipient_invalid()))
        await dialog_manager.switch_to(StorefrontSG.gifts_recipient, show_mode=ShowMode.EDIT)
        return
    username = normalize_recipient_username(callback.from_user.username or "")
    if username is None:
        set_notice(dialog_manager, str(i18n.messages.gift_recipient_invalid()))
        await dialog_manager.switch_to(StorefrontSG.gifts_recipient, show_mode=ShowMode.EDIT)
        return

    set_selected_gift_recipient_user_id(dialog_manager, callback.from_user.id)
    set_selected_gift_recipient_username(dialog_manager, username)
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.gifts_catalog, show_mode=ShowMode.EDIT)


async def _select_gift(
    *,
    dialog_manager: DialogManager,
    gift_key: str,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    recipient_username = selected_gift_recipient_username(dialog_manager)
    if normalize_recipient_username(recipient_username or "") is None:
        set_notice(dialog_manager, str(i18n.messages.gift_recipient_missing()))
        await dialog_manager.switch_to(StorefrontSG.gifts_recipient, show_mode=ShowMode.EDIT)
        return

    try:
        get_gift_pack(key=gift_key)
    except ValueError:
        set_notice(dialog_manager, str(i18n.messages.gift_invalid()))
        await dialog_manager.switch_to(StorefrontSG.gifts_catalog, show_mode=ShowMode.EDIT)
        return

    set_selected_gift_key(dialog_manager, gift_key)
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.gifts_message, show_mode=ShowMode.EDIT)


async def select_gift_new_year_tree(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    await _select_gift(dialog_manager=dialog_manager, gift_key="new_year_tree")


async def select_gift_valentine_heart(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    await _select_gift(dialog_manager=dialog_manager, gift_key="valentine_heart")


async def select_gift_new_year_bear(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    await _select_gift(dialog_manager=dialog_manager, gift_key="new_year_bear")


async def select_gift_bear_with_heart(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    await _select_gift(dialog_manager=dialog_manager, gift_key="bear_with_heart")


async def select_gift_bear_with_bouquet(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    await _select_gift(dialog_manager=dialog_manager, gift_key="bear_with_bouquet")


async def select_gift_irish_bear(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    await _select_gift(dialog_manager=dialog_manager, gift_key="irish_bear")


async def select_gift_clown_bear(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    await _select_gift(dialog_manager=dialog_manager, gift_key="clown_bear")


async def select_gift_easter_bear(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    await _select_gift(dialog_manager=dialog_manager, gift_key="easter_bear")


async def select_gift_worker_bear(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    await _select_gift(dialog_manager=dialog_manager, gift_key="worker_bear")


async def select_gift_military_bear(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    await _select_gift(dialog_manager=dialog_manager, gift_key="military_bear")


async def select_gift_football_bear(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    await _select_gift(dialog_manager=dialog_manager, gift_key="football_bear")


async def select_gift_default_bear(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    await _select_gift(dialog_manager=dialog_manager, gift_key="default_bear")


async def handle_gift_message_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    gift_key = selected_gift_key(dialog_manager)
    if gift_key is None:
        set_notice(dialog_manager, str(i18n.messages.gift_invalid()))
        await dialog_manager.switch_to(StorefrontSG.gifts_catalog, show_mode=ShowMode.EDIT)
        await _delete_user_message(message)
        return

    normalized = (message.text or "").strip()
    if len(normalized) > MAX_GIFT_MESSAGE_LENGTH:
        set_notice(
            dialog_manager,
            str(i18n.messages.gift_message_too_long(max_chars=MAX_GIFT_MESSAGE_LENGTH)),
        )
        await dialog_manager.switch_to(StorefrontSG.gifts_message, show_mode=ShowMode.EDIT)
        await _delete_user_message(message)
        return

    set_selected_gift_message(dialog_manager, normalized or None)
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.gifts_sender_privacy, show_mode=ShowMode.EDIT)
    await _delete_user_message(message)


async def skip_gift_message(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_selected_gift_message(dialog_manager, None)
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.gifts_sender_privacy, show_mode=ShowMode.EDIT)


async def select_gift_sender_visible(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    if selected_gift_key(dialog_manager) is None:
        set_notice(dialog_manager, str(i18n.messages.gift_invalid()))
        await dialog_manager.switch_to(StorefrontSG.gifts_catalog, show_mode=ShowMode.EDIT)
        return
    recipient_username = selected_gift_recipient_username(dialog_manager) or ""
    if normalize_recipient_username(recipient_username) is None:
        set_notice(dialog_manager, str(i18n.messages.gift_recipient_missing()))
        await dialog_manager.switch_to(StorefrontSG.gifts_recipient, show_mode=ShowMode.EDIT)
        return
    set_selected_gift_sender_private(dialog_manager, False)
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.gifts_payment, show_mode=ShowMode.EDIT)


async def select_gift_sender_private(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    if selected_gift_key(dialog_manager) is None:
        set_notice(dialog_manager, str(i18n.messages.gift_invalid()))
        await dialog_manager.switch_to(StorefrontSG.gifts_catalog, show_mode=ShowMode.EDIT)
        return
    recipient_username = selected_gift_recipient_username(dialog_manager) or ""
    if normalize_recipient_username(recipient_username) is None:
        set_notice(dialog_manager, str(i18n.messages.gift_recipient_missing()))
        await dialog_manager.switch_to(StorefrontSG.gifts_recipient, show_mode=ShowMode.EDIT)
        return
    set_selected_gift_sender_private(dialog_manager, True)
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.gifts_payment, show_mode=ShowMode.EDIT)
