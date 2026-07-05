from __future__ import annotations

from typing import Any

from aiogram_dialog import DialogManager

from ..handlers.shared import i18n
from .common import consume_notice, with_notice


async def menu_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    text = with_notice(
        text=str(i18n_ctx.messages.admin_menu()),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "broadcast_button_text": i18n_ctx.buttons.admin_broadcast(),
        "promos_button_text": i18n_ctx.buttons.admin_promos(),
        "orders_button_text": i18n_ctx.buttons.admin_orders(),
        "stars_sell_manage_button_text": i18n_ctx.buttons.admin_stars_sell_manage_root(),
        "stats_button_text": i18n_ctx.buttons.admin_stats(),
        "users_button_text": i18n_ctx.buttons.admin_users(),
        "close_button_text": i18n_ctx.buttons.admin_close(),
    }


__all__ = ["menu_getter"]
