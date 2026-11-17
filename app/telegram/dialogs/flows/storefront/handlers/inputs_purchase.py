from __future__ import annotations

import contextlib

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

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
    set_notice,
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
