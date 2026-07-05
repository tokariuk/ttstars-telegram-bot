from __future__ import annotations

import re

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from app.services.crud.check import CheckCloseOutcome
from app.telegram.dialogs.common import get_i18n, get_user

from ..states import StorefrontSG
from .shared import (
    check_service,
    checks_history_page,
    checks_page,
    clear_checks_create_draft,
    clear_gift_draft,
    clear_notice,
    clear_stars_sell_draft,
    history_page,
    referrals_page,
    selected_check_id,
    set_checks_history_page,
    set_checks_history_selected_check_id,
    set_checks_page,
    set_history_page,
    set_history_selected_order_id,
    set_notice,
    set_referrals_page,
    set_referrals_selected_user_id,
    set_selected_check_id,
    set_stars_sell_history_page,
    set_stars_sell_history_selected_order_id,
    stars_sell_history_page,
)

TOPUP_FROM_PROFILE_KEY = "topup_from_profile"
_DIALOG_ITEM_ID_RE = re.compile(r"(\d+)$")


def _set_topup_origin(dialog_manager: DialogManager, *, from_profile: bool) -> None:
    dialog_manager.dialog_data[TOPUP_FROM_PROFILE_KEY] = from_profile


def _dialog_item_id(dialog_manager: DialogManager, callback: CallbackQuery) -> str:
    raw = getattr(dialog_manager, "item_id", None)
    if raw is None:
        data = (callback.data or "").strip()
        if data:
            raw = data.rsplit(":", maxsplit=1)[-1]
    if raw is None:
        return ""
    value = str(raw).strip()
    if value.isdigit():
        return value
    for part in reversed(value.split(":")):
        normalized = part.strip()
        if normalized.isdigit():
            return normalized
    match = _DIALOG_ITEM_ID_RE.search(value)
    if match is not None:
        return match.group(1)
    return ""


async def show_menu(_: CallbackQuery, __: Button, dialog_manager: DialogManager) -> None:
    clear_notice(dialog_manager)
    _set_topup_origin(dialog_manager, from_profile=False)
    await dialog_manager.switch_to(StorefrontSG.menu, show_mode=ShowMode.EDIT)


async def show_gifts(_: CallbackQuery, __: Button, dialog_manager: DialogManager) -> None:
    clear_notice(dialog_manager)
    clear_gift_draft(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.gifts_recipient, show_mode=ShowMode.EDIT)


async def show_gifts_catalog(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.gifts_catalog, show_mode=ShowMode.EDIT)


async def show_gifts_message(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.gifts_message, show_mode=ShowMode.EDIT)


async def show_gifts_sender_privacy(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.gifts_sender_privacy, show_mode=ShowMode.EDIT)


async def show_stars_amount(_: CallbackQuery, __: Button, dialog_manager: DialogManager) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.stars_amount, show_mode=ShowMode.EDIT)


async def show_stars_recipient(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.stars_recipient, show_mode=ShowMode.EDIT)


async def show_stars_sell(_: CallbackQuery, __: Button, dialog_manager: DialogManager) -> None:
    clear_notice(dialog_manager)
    clear_stars_sell_draft(dialog_manager)
    set_stars_sell_history_page(dialog_manager, 0)
    set_stars_sell_history_selected_order_id(dialog_manager, None)
    await dialog_manager.switch_to(StorefrontSG.stars_sell_menu, show_mode=ShowMode.EDIT)


async def show_stars_sell_menu(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.stars_sell_menu, show_mode=ShowMode.EDIT)


async def show_stars_sell_stars(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.stars_sell_stars, show_mode=ShowMode.EDIT)


async def show_stars_sell_wallet(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.stars_sell_wallet, show_mode=ShowMode.EDIT)


async def show_stars_sell_payment(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.stars_sell_payment, show_mode=ShowMode.EDIT)


async def show_stars_sell_history(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    set_stars_sell_history_selected_order_id(dialog_manager, None)
    await dialog_manager.switch_to(StorefrontSG.stars_sell_history, show_mode=ShowMode.EDIT)


async def stars_sell_history_prev_page(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_stars_sell_history_selected_order_id(dialog_manager, None)
    set_stars_sell_history_page(dialog_manager, stars_sell_history_page(dialog_manager) - 1)
    await dialog_manager.switch_to(StorefrontSG.stars_sell_history, show_mode=ShowMode.EDIT)


async def stars_sell_history_next_page(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_stars_sell_history_selected_order_id(dialog_manager, None)
    set_stars_sell_history_page(dialog_manager, stars_sell_history_page(dialog_manager) + 1)
    await dialog_manager.switch_to(StorefrontSG.stars_sell_history, show_mode=ShowMode.EDIT)


async def show_stars_sell_history_page_info(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
) -> None:
    await callback.answer()


async def open_stars_sell_history_order(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    item_id = _dialog_item_id(dialog_manager, callback)
    if item_id.isdigit():
        set_stars_sell_history_selected_order_id(dialog_manager, int(item_id))
        await dialog_manager.switch_to(
            StorefrontSG.stars_sell_history_details,
            show_mode=ShowMode.EDIT,
        )
    await callback.answer()


async def show_calculator(_: CallbackQuery, __: Button, dialog_manager: DialogManager) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.calculator, show_mode=ShowMode.EDIT)


async def show_profile(_: CallbackQuery, __: Button, dialog_manager: DialogManager) -> None:
    clear_notice(dialog_manager)
    _set_topup_origin(dialog_manager, from_profile=False)
    await dialog_manager.switch_to(StorefrontSG.profile, show_mode=ShowMode.EDIT)


async def show_checks(_: CallbackQuery, __: Button, dialog_manager: DialogManager) -> None:
    clear_notice(dialog_manager)
    clear_checks_create_draft(dialog_manager)
    set_checks_page(dialog_manager, 0)
    set_selected_check_id(dialog_manager, None)
    set_checks_history_selected_check_id(dialog_manager, None)
    await dialog_manager.switch_to(StorefrontSG.checks_list, show_mode=ShowMode.EDIT)


async def show_checks_current(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    clear_checks_create_draft(dialog_manager)
    set_selected_check_id(dialog_manager, None)
    await dialog_manager.switch_to(StorefrontSG.checks_list, show_mode=ShowMode.EDIT)


async def show_checks_history(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    set_checks_history_page(dialog_manager, 0)
    set_checks_history_selected_check_id(dialog_manager, None)
    await dialog_manager.switch_to(StorefrontSG.checks_history, show_mode=ShowMode.EDIT)


async def show_checks_history_list(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    set_checks_history_selected_check_id(dialog_manager, None)
    await dialog_manager.switch_to(StorefrontSG.checks_history, show_mode=ShowMode.EDIT)


async def show_checks_details_current(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.checks_details, show_mode=ShowMode.EDIT)


async def show_checks_create_stars(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    clear_checks_create_draft(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.checks_create_stars, show_mode=ShowMode.EDIT)


async def show_checks_create_recipient(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.checks_create_recipient, show_mode=ShowMode.EDIT)


async def show_checks_create_password(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.checks_create_password, show_mode=ShowMode.EDIT)


async def show_checks_create_confirm(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.checks_create_confirm, show_mode=ShowMode.EDIT)


async def checks_prev_page(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_selected_check_id(dialog_manager, None)
    set_checks_page(dialog_manager, checks_page(dialog_manager) - 1)
    await dialog_manager.switch_to(StorefrontSG.checks_list, show_mode=ShowMode.EDIT)


async def checks_next_page(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_selected_check_id(dialog_manager, None)
    set_checks_page(dialog_manager, checks_page(dialog_manager) + 1)
    await dialog_manager.switch_to(StorefrontSG.checks_list, show_mode=ShowMode.EDIT)


async def show_checks_page_info(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
) -> None:
    await callback.answer()


async def open_check(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    item_id = _dialog_item_id(dialog_manager, callback)
    if item_id.isdigit():
        set_selected_check_id(dialog_manager, int(item_id))
        await dialog_manager.switch_to(StorefrontSG.checks_details, show_mode=ShowMode.EDIT)
    await callback.answer()


async def checks_history_prev_page(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_checks_history_selected_check_id(dialog_manager, None)
    set_checks_history_page(dialog_manager, checks_history_page(dialog_manager) - 1)
    await dialog_manager.switch_to(StorefrontSG.checks_history, show_mode=ShowMode.EDIT)


async def checks_history_next_page(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_checks_history_selected_check_id(dialog_manager, None)
    set_checks_history_page(dialog_manager, checks_history_page(dialog_manager) + 1)
    await dialog_manager.switch_to(StorefrontSG.checks_history, show_mode=ShowMode.EDIT)


async def show_checks_history_page_info(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
) -> None:
    await callback.answer()


async def open_check_history(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    item_id = _dialog_item_id(dialog_manager, callback)
    if item_id.isdigit():
        set_checks_history_selected_check_id(dialog_manager, int(item_id))
        await dialog_manager.switch_to(
            StorefrontSG.checks_history_details,
            show_mode=ShowMode.EDIT,
        )
    await callback.answer()


async def show_checks_settings(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.checks_settings, show_mode=ShowMode.EDIT)


async def show_checks_edit_recipient(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.checks_edit_recipient, show_mode=ShowMode.EDIT)


async def show_checks_edit_password(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.checks_edit_password, show_mode=ShowMode.EDIT)


async def clear_selected_check_recipient(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    check_id = selected_check_id(dialog_manager)
    if check_id is None:
        set_notice(dialog_manager, str(i18n.messages.check_detail_not_found()))
        await dialog_manager.switch_to(StorefrontSG.checks_list, show_mode=ShowMode.EDIT)
        await callback.answer()
        return

    updated = await check_service(dialog_manager=dialog_manager).update_claim_username(
        creator_id=user.id,
        check_id=check_id,
        claim_username=None,
    )
    if updated is None:
        set_notice(dialog_manager, str(i18n.messages.check_detail_not_found()))
        await dialog_manager.switch_to(StorefrontSG.checks_list, show_mode=ShowMode.EDIT)
    else:
        set_notice(dialog_manager, str(i18n.messages.check_settings_recipient_cleared()))
        await dialog_manager.switch_to(StorefrontSG.checks_settings, show_mode=ShowMode.EDIT)
    await callback.answer()


async def clear_selected_check_password(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    check_id = selected_check_id(dialog_manager)
    if check_id is None:
        set_notice(dialog_manager, str(i18n.messages.check_detail_not_found()))
        await dialog_manager.switch_to(StorefrontSG.checks_list, show_mode=ShowMode.EDIT)
        await callback.answer()
        return

    updated = await check_service(dialog_manager=dialog_manager).update_claim_password(
        creator_id=user.id,
        check_id=check_id,
        claim_password=None,
    )
    if updated is None:
        set_notice(dialog_manager, str(i18n.messages.check_detail_not_found()))
        await dialog_manager.switch_to(StorefrontSG.checks_list, show_mode=ShowMode.EDIT)
    else:
        set_notice(dialog_manager, str(i18n.messages.check_settings_password_cleared()))
        await dialog_manager.switch_to(StorefrontSG.checks_settings, show_mode=ShowMode.EDIT)
    await callback.answer()


async def close_selected_check(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    check_id = selected_check_id(dialog_manager)
    if check_id is None:
        set_notice(dialog_manager, str(i18n.messages.check_close_not_found()))
        await dialog_manager.switch_to(StorefrontSG.checks_list, show_mode=ShowMode.EDIT)
        await callback.answer()
        return

    result = await check_service(dialog_manager=dialog_manager).close_check(
        creator_id=user.id,
        check_id=check_id,
    )
    if result.outcome == CheckCloseOutcome.CLOSED:
        set_notice(dialog_manager, str(i18n.messages.check_close_done()))
    elif result.outcome == CheckCloseOutcome.ALREADY_REDEEMED:
        set_notice(dialog_manager, str(i18n.messages.check_close_already_redeemed()))
    elif result.outcome == CheckCloseOutcome.ALREADY_CLOSED:
        set_notice(dialog_manager, str(i18n.messages.check_close_already_closed()))
    elif result.outcome == CheckCloseOutcome.PROCESSING:
        set_notice(dialog_manager, str(i18n.messages.check_close_processing()))
    else:
        set_notice(dialog_manager, str(i18n.messages.check_close_not_found()))

    set_selected_check_id(dialog_manager, None)
    await dialog_manager.switch_to(StorefrontSG.checks_list, show_mode=ShowMode.EDIT)
    await callback.answer()


async def show_history(_: CallbackQuery, __: Button, dialog_manager: DialogManager) -> None:
    clear_notice(dialog_manager)
    set_history_page(dialog_manager, 0)
    set_history_selected_order_id(dialog_manager, None)
    await dialog_manager.switch_to(StorefrontSG.history, show_mode=ShowMode.EDIT)


async def show_history_list(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    set_history_selected_order_id(dialog_manager, None)
    await dialog_manager.switch_to(StorefrontSG.history, show_mode=ShowMode.EDIT)


async def show_promo(_: CallbackQuery, __: Button, dialog_manager: DialogManager) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.promo, show_mode=ShowMode.EDIT)


async def show_referrals(_: CallbackQuery, __: Button, dialog_manager: DialogManager) -> None:
    clear_notice(dialog_manager)
    set_referrals_selected_user_id(dialog_manager, None)
    await dialog_manager.switch_to(StorefrontSG.referrals, show_mode=ShowMode.EDIT)


async def show_referrals_list(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    set_referrals_page(dialog_manager, 0)
    set_referrals_selected_user_id(dialog_manager, None)
    await dialog_manager.switch_to(StorefrontSG.referrals_list, show_mode=ShowMode.EDIT)


async def show_referrals_list_current(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    set_referrals_selected_user_id(dialog_manager, None)
    await dialog_manager.switch_to(StorefrontSG.referrals_list, show_mode=ShowMode.EDIT)


async def withdraw_referral_balance(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.referrals_withdraw, show_mode=ShowMode.EDIT)


async def show_faq(_: CallbackQuery, __: Button, dialog_manager: DialogManager) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.faq, show_mode=ShowMode.EDIT)


async def show_premium_plans(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.premium_plans, show_mode=ShowMode.EDIT)


async def show_premium_recipient(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    await dialog_manager.switch_to(StorefrontSG.premium_recipient, show_mode=ShowMode.EDIT)


async def show_topup_amount(_: CallbackQuery, __: Button, dialog_manager: DialogManager) -> None:
    clear_notice(dialog_manager)
    _set_topup_origin(dialog_manager, from_profile=False)
    await dialog_manager.switch_to(StorefrontSG.topup_amount, show_mode=ShowMode.EDIT)


async def show_topup_amount_from_profile(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    _set_topup_origin(dialog_manager, from_profile=True)
    await dialog_manager.switch_to(StorefrontSG.topup_amount, show_mode=ShowMode.EDIT)


async def history_prev_page(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_history_selected_order_id(dialog_manager, None)
    set_history_page(dialog_manager, history_page(dialog_manager) - 1)
    await dialog_manager.switch_to(StorefrontSG.history, show_mode=ShowMode.EDIT)


async def history_next_page(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_history_selected_order_id(dialog_manager, None)
    set_history_page(dialog_manager, history_page(dialog_manager) + 1)
    await dialog_manager.switch_to(StorefrontSG.history, show_mode=ShowMode.EDIT)


async def show_history_page_info(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
) -> None:
    await callback.answer()


async def referrals_prev_page(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_referrals_selected_user_id(dialog_manager, None)
    set_referrals_page(dialog_manager, referrals_page(dialog_manager) - 1)
    await dialog_manager.switch_to(StorefrontSG.referrals_list, show_mode=ShowMode.EDIT)


async def referrals_next_page(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_referrals_selected_user_id(dialog_manager, None)
    set_referrals_page(dialog_manager, referrals_page(dialog_manager) + 1)
    await dialog_manager.switch_to(StorefrontSG.referrals_list, show_mode=ShowMode.EDIT)


async def show_referrals_page_info(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
) -> None:
    await callback.answer()


async def open_referral_member(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    item_id = _dialog_item_id(dialog_manager, callback)
    if item_id.isdigit():
        set_referrals_selected_user_id(dialog_manager, int(item_id))
        await dialog_manager.switch_to(StorefrontSG.referrals_details, show_mode=ShowMode.EDIT)
    await callback.answer()


async def open_history_order(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    clear_notice(dialog_manager)
    item_id = _dialog_item_id(dialog_manager, callback)
    if item_id.isdigit():
        set_history_selected_order_id(dialog_manager, int(item_id))
        await dialog_manager.switch_to(StorefrontSG.history_details, show_mode=ShowMode.EDIT)
    await callback.answer()


__all__ = [
    "clear_selected_check_password",
    "clear_selected_check_recipient",
    "checks_history_next_page",
    "checks_history_prev_page",
    "checks_next_page",
    "checks_prev_page",
    "history_next_page",
    "history_prev_page",
    "close_selected_check",
    "open_check",
    "open_check_history",
    "open_history_order",
    "open_referral_member",
    "referrals_next_page",
    "referrals_prev_page",
    "show_referrals_page_info",
    "show_history_page_info",
    "show_checks",
    "show_checks_history",
    "show_checks_history_list",
    "show_checks_history_page_info",
    "show_checks_create_password",
    "show_checks_create_confirm",
    "show_checks_create_recipient",
    "show_checks_create_stars",
    "show_checks_details_current",
    "show_checks_current",
    "show_checks_edit_password",
    "show_checks_edit_recipient",
    "show_checks_page_info",
    "show_checks_settings",
    "show_calculator",
    "show_faq",
    "show_gifts",
    "show_gifts_catalog",
    "show_gifts_message",
    "show_gifts_sender_privacy",
    "show_history",
    "show_history_list",
    "show_menu",
    "show_premium_plans",
    "show_premium_recipient",
    "show_profile",
    "show_promo",
    "show_referrals",
    "show_referrals_list",
    "show_referrals_list_current",
    "show_stars_amount",
    "show_stars_sell",
    "show_stars_sell_history",
    "show_stars_sell_history_page_info",
    "show_stars_sell_menu",
    "show_stars_sell_payment",
    "show_stars_sell_stars",
    "show_stars_sell_wallet",
    "show_stars_recipient",
    "open_stars_sell_history_order",
    "stars_sell_history_next_page",
    "stars_sell_history_prev_page",
    "show_topup_amount",
    "show_topup_amount_from_profile",
    "withdraw_referral_balance",
    "TOPUP_FROM_PROFILE_KEY",
]
