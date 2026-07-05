from aiogram.enums.button_style import ButtonStyle
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format

from app.telegram.dialogs.common.premium_emoji import SETTINGS_EMOJI_ID

from ..getters import menu_getter
from ..handlers import (
    close_panel,
    open_stars_sell_admin_list,
    show_broadcast_content,
    show_orders_menu,
    show_promo_menu,
    show_stats,
    show_users_menu,
)
from ..ids import (
    ADMIN_MENU_CLOSE_BUTTON_ID,
    ADMIN_MENU_OPEN_BROADCAST_BUTTON_ID,
    ADMIN_MENU_OPEN_ORDERS_BUTTON_ID,
    ADMIN_MENU_OPEN_PROMO_BUTTON_ID,
    ADMIN_MENU_OPEN_STARS_SELL_MANAGE_BUTTON_ID,
    ADMIN_MENU_OPEN_STATS_BUTTON_ID,
    ADMIN_MENU_OPEN_USERS_BUTTON_ID,
)
from ..states import AdminSG

menu_window: Window = Window(
    Format("{text}"),
    Row(
        Button(
            Format("{broadcast_button_text}"),
            id=ADMIN_MENU_OPEN_BROADCAST_BUTTON_ID,
            on_click=show_broadcast_content,
            style=Style(style=ButtonStyle.PRIMARY),
        ),
        Button(
            Format("{promos_button_text}"),
            id=ADMIN_MENU_OPEN_PROMO_BUTTON_ID,
            on_click=show_promo_menu,
            style=Style(style=ButtonStyle.PRIMARY),
        ),
    ),
    Row(
        Button(
            Format("{stats_button_text}"),
            id=ADMIN_MENU_OPEN_STATS_BUTTON_ID,
            on_click=show_stats,
        ),
        Button(
            Format("{users_button_text}"),
            id=ADMIN_MENU_OPEN_USERS_BUTTON_ID,
            on_click=show_users_menu,
        ),
    ),
    Button(
        Format("{orders_button_text}"),
        id=ADMIN_MENU_OPEN_ORDERS_BUTTON_ID,
        on_click=show_orders_menu,
    ),
    Button(
        Format("{stars_sell_manage_button_text}"),
        id=ADMIN_MENU_OPEN_STARS_SELL_MANAGE_BUTTON_ID,
        on_click=open_stars_sell_admin_list,
        style=Style(emoji_id=SETTINGS_EMOJI_ID),
    ),
    Button(
        Format("{close_button_text}"),
        id=ADMIN_MENU_CLOSE_BUTTON_ID,
        on_click=close_panel,
        style=Style(style=ButtonStyle.DANGER),
    ),
    state=AdminSG.menu,
    getter=menu_getter,
)


__all__ = ["menu_window"]
