from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format

from app.telegram.dialogs.common.ttstars_interface_emoji import (
    LEFT_SQUARE_EMOJI_ID,
    SEARCH_EMOJI_ID,
    WALLET_EMOJI_ID,
)

from ..getters import users_add_balance_getter, users_lookup_getter, users_menu_getter
from ..handlers import (
    handle_user_add_balance_input,
    handle_user_lookup_input,
    show_menu,
    show_user_add_balance,
    show_user_lookup,
    show_users_menu,
)
from ..ids import (
    ADMIN_USERS_ADD_BALANCE_BUTTON_ID,
    ADMIN_USERS_BACK_TO_MENU_BUTTON_ID,
    ADMIN_USERS_LOOKUP_BUTTON_ID,
)
from ..states import AdminSG

users_menu_window: Window = Window(
    Format("{text}"),
    Button(
        Format("{add_balance_button_text}"),
        id=ADMIN_USERS_ADD_BALANCE_BUTTON_ID,
        on_click=show_user_add_balance,
        style=Style(emoji_id=WALLET_EMOJI_ID),
    ),
    Button(
        Format("{lookup_button_text}"),
        id=ADMIN_USERS_LOOKUP_BUTTON_ID,
        on_click=show_user_lookup,
        style=Style(emoji_id=SEARCH_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=ADMIN_USERS_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=AdminSG.users_menu,
    getter=users_menu_getter,
)

users_add_balance_window: Window = Window(
    Format("{text}"),
    MessageInput(handle_user_add_balance_input),
    Button(
        Format("{back_button_text}"),
        id=ADMIN_USERS_BACK_TO_MENU_BUTTON_ID,
        on_click=show_users_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=AdminSG.user_add_balance,
    getter=users_add_balance_getter,
)

users_lookup_window: Window = Window(
    Format("{text}"),
    MessageInput(handle_user_lookup_input),
    Button(
        Format("{back_button_text}"),
        id=ADMIN_USERS_BACK_TO_MENU_BUTTON_ID,
        on_click=show_users_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=AdminSG.user_lookup_contact,
    getter=users_lookup_getter,
)


__all__ = ["users_add_balance_window", "users_lookup_window", "users_menu_window"]
