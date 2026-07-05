from __future__ import annotations

import re

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from app.telegram.dialogs.common import reset_stack_to
from app.telegram.dialogs.flows.storefront.states import StorefrontSG

from ..states import AdminSG
from .shared import (
    clear_broadcast_payload,
    clear_promo_bulk_selected_codes,
    clear_stars_sell_draft,
    consume_notice,
    i18n,
    promo_bulk_mode,
    promo_page,
    promo_selected_code,
    set_promo_bulk_mode,
    set_promo_page,
    set_promo_selected_code,
    set_stars_sell_admin_page,
    set_stars_sell_admin_selected_order_id,
    set_stars_sell_history_page,
    set_stars_sell_history_selected_order_id,
    stars_sell_admin_page,
    stars_sell_history_page,
    toggle_promo_bulk_selected_code,
)


def _clear_notice(dialog_manager: DialogManager) -> None:
    consume_notice(dialog_manager)


_DIALOG_ITEM_ID_RE = re.compile(r"(\d+)$")


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
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.menu, show_mode=ShowMode.EDIT)


async def close_panel(_: CallbackQuery, __: Button, dialog_manager: DialogManager) -> None:
    _clear_notice(dialog_manager)
    clear_broadcast_payload(dialog_manager)
    await reset_stack_to(dialog_manager=dialog_manager, state=StorefrontSG.menu)


async def show_broadcast_content(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    clear_broadcast_payload(dialog_manager)
    await dialog_manager.switch_to(AdminSG.broadcast_content, show_mode=ShowMode.EDIT)


async def show_promo_menu(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    set_promo_bulk_mode(dialog_manager, enabled=False)
    clear_promo_bulk_selected_codes(dialog_manager)
    set_promo_selected_code(dialog_manager, None)
    await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)


async def show_stats(_: CallbackQuery, __: Button, dialog_manager: DialogManager) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.stats, show_mode=ShowMode.EDIT)


async def show_users_menu(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.users_menu, show_mode=ShowMode.EDIT)


async def show_orders_menu(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.orders_menu, show_mode=ShowMode.EDIT)


async def open_stars_sell(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    clear_stars_sell_draft(dialog_manager)
    set_stars_sell_history_page(dialog_manager, 0)
    set_stars_sell_history_selected_order_id(dialog_manager, None)
    set_stars_sell_admin_page(dialog_manager, 0)
    set_stars_sell_admin_selected_order_id(dialog_manager, None)
    await dialog_manager.switch_to(AdminSG.stars_sell_menu, show_mode=ShowMode.EDIT)


async def show_stars_sell_menu(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.stars_sell_menu, show_mode=ShowMode.EDIT)


async def show_stars_sell_stars(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.stars_sell_stars, show_mode=ShowMode.EDIT)


async def show_stars_sell_wallet(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.stars_sell_wallet, show_mode=ShowMode.EDIT)


async def show_stars_sell_payment(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.stars_sell_payment, show_mode=ShowMode.EDIT)


async def show_stars_sell_history(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    set_stars_sell_history_selected_order_id(dialog_manager, None)
    await dialog_manager.switch_to(AdminSG.stars_sell_history, show_mode=ShowMode.EDIT)


async def show_stars_sell_admin_list(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    set_stars_sell_admin_selected_order_id(dialog_manager, None)
    await dialog_manager.switch_to(AdminSG.stars_sell_admin_list, show_mode=ShowMode.EDIT)


async def open_stars_sell_admin_list(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    set_stars_sell_admin_page(dialog_manager, 0)
    set_stars_sell_admin_selected_order_id(dialog_manager, None)
    await dialog_manager.switch_to(AdminSG.stars_sell_admin_list, show_mode=ShowMode.EDIT)


async def stars_sell_history_prev_page(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_stars_sell_history_selected_order_id(dialog_manager, None)
    set_stars_sell_history_page(dialog_manager, stars_sell_history_page(dialog_manager) - 1)
    await dialog_manager.switch_to(AdminSG.stars_sell_history, show_mode=ShowMode.EDIT)


async def stars_sell_history_next_page(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_stars_sell_history_selected_order_id(dialog_manager, None)
    set_stars_sell_history_page(dialog_manager, stars_sell_history_page(dialog_manager) + 1)
    await dialog_manager.switch_to(AdminSG.stars_sell_history, show_mode=ShowMode.EDIT)


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
    _clear_notice(dialog_manager)
    raw_order_id = _dialog_item_id(dialog_manager, callback)
    if raw_order_id.isdigit():
        set_stars_sell_history_selected_order_id(dialog_manager, int(raw_order_id))
        await dialog_manager.switch_to(AdminSG.stars_sell_history_details, show_mode=ShowMode.EDIT)
    await callback.answer()


async def stars_sell_admin_prev_page(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_stars_sell_admin_selected_order_id(dialog_manager, None)
    set_stars_sell_admin_page(dialog_manager, stars_sell_admin_page(dialog_manager) - 1)
    await dialog_manager.switch_to(AdminSG.stars_sell_admin_list, show_mode=ShowMode.EDIT)


async def stars_sell_admin_next_page(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_stars_sell_admin_selected_order_id(dialog_manager, None)
    set_stars_sell_admin_page(dialog_manager, stars_sell_admin_page(dialog_manager) + 1)
    await dialog_manager.switch_to(AdminSG.stars_sell_admin_list, show_mode=ShowMode.EDIT)


async def show_stars_sell_admin_page_info(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
) -> None:
    await callback.answer()


async def open_stars_sell_admin_order(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    raw_order_id = _dialog_item_id(dialog_manager, callback)
    if raw_order_id.isdigit():
        set_stars_sell_admin_selected_order_id(dialog_manager, int(raw_order_id))
        await dialog_manager.switch_to(AdminSG.stars_sell_admin_details, show_mode=ShowMode.EDIT)
    await callback.answer()


async def show_broadcast_buttons(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.broadcast_buttons, show_mode=ShowMode.EDIT)


async def show_broadcast_confirm(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.broadcast_confirm, show_mode=ShowMode.EDIT)


async def show_promo_create(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.promo_create, show_mode=ShowMode.EDIT)


async def show_promo_quick(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.promo_quick, show_mode=ShowMode.EDIT)


async def show_promo_bulk(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.promo_bulk, show_mode=ShowMode.EDIT)


async def show_promo_set_limit(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.promo_set_limit, show_mode=ShowMode.EDIT)


async def show_promo_details_current(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    target_state = (
        AdminSG.promo_details
        if promo_selected_code(dialog_manager) is not None
        else AdminSG.promo_menu
    )
    await dialog_manager.switch_to(target_state, show_mode=ShowMode.EDIT)


async def promo_prev_page(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_promo_selected_code(dialog_manager, None)
    set_promo_page(dialog_manager, promo_page(dialog_manager) - 1)
    await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)


async def promo_next_page(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    set_promo_selected_code(dialog_manager, None)
    set_promo_page(dialog_manager, promo_page(dialog_manager) + 1)
    await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)


async def show_promo_page_info(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
) -> None:
    await callback.answer()


async def open_promo_code(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    code = _dialog_item_id(dialog_manager, callback)
    if code:
        if promo_bulk_mode(dialog_manager):
            selected_now = toggle_promo_bulk_selected_code(dialog_manager, code)
            i18n_ctx = i18n(dialog_manager)
            await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)
            await callback.answer(
                str(
                    (
                        i18n_ctx.messages.admin_promo_bulk_item_selected(code=code.upper())
                        if selected_now
                        else i18n_ctx.messages.admin_promo_bulk_item_unselected(
                            code=code.upper()
                        )
                    )
                ),
            )
            return
        set_promo_selected_code(dialog_manager, code)
        await dialog_manager.switch_to(AdminSG.promo_details, show_mode=ShowMode.EDIT)
    await callback.answer()


async def toggle_promo_bulk_mode(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    is_enabled = promo_bulk_mode(dialog_manager)
    if is_enabled:
        set_promo_bulk_mode(dialog_manager, enabled=False)
        clear_promo_bulk_selected_codes(dialog_manager)
    else:
        set_promo_bulk_mode(dialog_manager, enabled=True)
        clear_promo_bulk_selected_codes(dialog_manager)
        set_promo_selected_code(dialog_manager, None)
    await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)


async def show_user_add_balance(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.user_add_balance, show_mode=ShowMode.EDIT)


async def show_user_lookup(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.user_lookup_contact, show_mode=ShowMode.EDIT)


async def show_order_retry(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.order_retry, show_mode=ShowMode.EDIT)


async def show_order_force(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    _clear_notice(dialog_manager)
    await dialog_manager.switch_to(AdminSG.order_force, show_mode=ShowMode.EDIT)


__all__ = [
    "close_panel",
    "open_stars_sell_admin_list",
    "open_stars_sell_history_order",
    "open_stars_sell_admin_order",
    "open_stars_sell",
    "open_promo_code",
    "promo_next_page",
    "promo_prev_page",
    "show_order_force",
    "show_order_retry",
    "show_orders_menu",
    "show_broadcast_buttons",
    "show_broadcast_confirm",
    "show_broadcast_content",
    "show_menu",
    "show_promo_bulk",
    "show_promo_create",
    "show_promo_details_current",
    "toggle_promo_bulk_mode",
    "show_promo_menu",
    "show_promo_page_info",
    "show_promo_quick",
    "show_promo_set_limit",
    "show_stars_sell_menu",
    "show_stars_sell_payment",
    "show_stars_sell_history",
    "show_stars_sell_admin_list",
    "show_stars_sell_admin_page_info",
    "show_stars_sell_history_page_info",
    "show_stars_sell_stars",
    "show_stars_sell_wallet",
    "stars_sell_admin_next_page",
    "stars_sell_admin_prev_page",
    "stars_sell_history_next_page",
    "stars_sell_history_prev_page",
    "show_stats",
    "show_user_add_balance",
    "show_user_lookup",
    "show_users_menu",
]
