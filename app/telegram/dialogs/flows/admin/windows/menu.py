from aiogram.enums.button_style import ButtonStyle
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format

from app.telegram.dialogs.common.ttstars_interface_emoji import (
    BELL_EMOJI_ID,
    BOX_1_EMOJI_ID,
    CHART_1_EMOJI_ID,
    CLOSE_EMOJI_ID,
    COLOR_PALETTE_EMOJI_ID,
    KEY_EMOJI_ID,
    SETTINGS_EMOJI_ID,
    USERS_EMOJI_ID,
)

from ..getters import menu_getter
from ..handlers import (
    close_panel,
    open_stars_sell_admin_list,
    show_broadcast_content,
    show_creatives_menu,
    show_orders_menu,
    show_promo_menu,
    show_stats,
    show_users_menu,
)
from ..ids import (
    ADMIN_MENU_CLOSE_BUTTON_ID,
    ADMIN_MENU_OPEN_BROADCAST_BUTTON_ID,
    ADMIN_MENU_OPEN_CREATIVES_BUTTON_ID,
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
            Format("{orders_button_text}"),
            id=ADMIN_MENU_OPEN_ORDERS_BUTTON_ID,
            on_click=show_orders_menu,
            style=Style(style=ButtonStyle.PRIMARY, emoji_id=BOX_1_EMOJI_ID),
        ),
        Button(
            Format("{users_button_text}"),
            id=ADMIN_MENU_OPEN_USERS_BUTTON_ID,
            on_click=show_users_menu,
            style=Style(style=ButtonStyle.PRIMARY, emoji_id=USERS_EMOJI_ID),
        ),
    ),
    Row(
        Button(
            Format("{promos_button_text}"),
            id=ADMIN_MENU_OPEN_PROMO_BUTTON_ID,
            on_click=show_promo_menu,
            style=Style(emoji_id=KEY_EMOJI_ID),
        ),
        Button(
            Format("{broadcast_button_text}"),
            id=ADMIN_MENU_OPEN_BROADCAST_BUTTON_ID,
            on_click=show_broadcast_content,
            style=Style(emoji_id=BELL_EMOJI_ID),
        ),
    ),
    Row(
        Button(
            Format("{stats_button_text}"),
            id=ADMIN_MENU_OPEN_STATS_BUTTON_ID,
            on_click=show_stats,
            style=Style(emoji_id=CHART_1_EMOJI_ID),
        ),
        Button(
            Format("{stars_sell_manage_button_text}"),
            id=ADMIN_MENU_OPEN_STARS_SELL_MANAGE_BUTTON_ID,
            on_click=open_stars_sell_admin_list,
            style=Style(emoji_id=SETTINGS_EMOJI_ID),
        ),
    ),
    Button(
        Format("{creatives_button_text}"),
        id=ADMIN_MENU_OPEN_CREATIVES_BUTTON_ID,
        on_click=show_creatives_menu,
        style=Style(emoji_id=COLOR_PALETTE_EMOJI_ID),
    ),
    Button(
        Format("{close_button_text}"),
        id=ADMIN_MENU_CLOSE_BUTTON_ID,
        on_click=close_panel,
        style=Style(style=ButtonStyle.DANGER, emoji_id=CLOSE_EMOJI_ID),
    ),
    state=AdminSG.menu,
    getter=menu_getter,
)


__all__ = ["menu_window"]
