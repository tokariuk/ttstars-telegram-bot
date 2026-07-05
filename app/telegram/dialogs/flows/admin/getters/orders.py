from __future__ import annotations

from typing import Any

from aiogram_dialog import DialogManager

from ..handlers.shared import i18n
from .common import consume_notice, with_notice


async def orders_menu_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    text = with_notice(
        text=str(i18n_ctx.messages.admin_orders_menu()),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "retry_button_text": i18n_ctx.buttons.admin_order_retry(),
        "force_button_text": i18n_ctx.buttons.admin_order_force(),
        "back_button_text": i18n_ctx.buttons.admin_back_menu(),
    }


async def order_retry_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    text = with_notice(
        text=str(i18n_ctx.messages.admin_orders_retry_prompt()),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "back_button_text": i18n_ctx.buttons.admin_back_menu(),
    }


async def order_force_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    text = with_notice(
        text=str(i18n_ctx.messages.admin_orders_force_prompt()),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "back_button_text": i18n_ctx.buttons.admin_back_menu(),
    }


__all__ = [
    "order_force_getter",
    "order_retry_getter",
    "orders_menu_getter",
]
