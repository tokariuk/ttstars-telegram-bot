from __future__ import annotations

from typing import Any

from aiogram_dialog import DialogManager

from ..handlers.shared import i18n
from .common import consume_notice, with_notice


async def users_menu_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    text = with_notice(
        text=str(i18n_ctx.messages.admin_users_menu()),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "add_balance_button_text": i18n_ctx.buttons.admin_add_balance(),
        "lookup_button_text": i18n_ctx.buttons.admin_user_lookup(),
        "back_button_text": i18n_ctx.buttons.admin_back_menu(),
    }


async def users_add_balance_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    text = with_notice(
        text=str(i18n_ctx.messages.admin_users_add_balance_prompt()),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "back_button_text": i18n_ctx.buttons.admin_back_menu(),
    }


async def users_lookup_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    text = with_notice(
        text=str(i18n_ctx.messages.admin_users_lookup_prompt()),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "back_button_text": i18n_ctx.buttons.admin_back_menu(),
    }


__all__ = ["users_add_balance_getter", "users_lookup_getter", "users_menu_getter"]
