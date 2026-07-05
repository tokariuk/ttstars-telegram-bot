from aiogram.enums.button_style import ButtonStyle
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format

from ..getters import (
    broadcast_buttons_getter,
    broadcast_confirm_getter,
    broadcast_content_getter,
    broadcast_options_getter,
)
from ..handlers import (
    broadcast_send,
    broadcast_skip_buttons,
    broadcast_skip_options,
    handle_broadcast_buttons_input,
    handle_broadcast_content_input,
    handle_broadcast_options_input,
    show_broadcast_content,
    show_menu,
)
from ..ids import (
    ADMIN_BROADCAST_BACK_TO_MENU_BUTTON_ID,
    ADMIN_BROADCAST_CONFIRM_RESTART_BUTTON_ID,
    ADMIN_BROADCAST_CONFIRM_SEND_BUTTON_ID,
    ADMIN_BROADCAST_SKIP_BUTTONS_BUTTON_ID,
    ADMIN_BROADCAST_SKIP_OPTIONS_BUTTON_ID,
)
from ..states import AdminSG

broadcast_content_window: Window = Window(
    Format("{text}"),
    MessageInput(handle_broadcast_content_input),
    Button(
        Format("{back_button_text}"),
        id=ADMIN_BROADCAST_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
    ),
    state=AdminSG.broadcast_content,
    getter=broadcast_content_getter,
)

broadcast_buttons_window: Window = Window(
    Format("{text}"),
    MessageInput(handle_broadcast_buttons_input),
    Row(
        Button(
            Format("{skip_button_text}"),
            id=ADMIN_BROADCAST_SKIP_BUTTONS_BUTTON_ID,
            on_click=broadcast_skip_buttons,
            style=Style(style=ButtonStyle.PRIMARY),
        ),
        Button(
            Format("{back_button_text}"),
            id=ADMIN_BROADCAST_BACK_TO_MENU_BUTTON_ID,
            on_click=show_menu,
        ),
    ),
    state=AdminSG.broadcast_buttons,
    getter=broadcast_buttons_getter,
)

broadcast_options_window: Window = Window(
    Format("{text}"),
    MessageInput(handle_broadcast_options_input),
    Row(
        Button(
            Format("{skip_button_text}"),
            id=ADMIN_BROADCAST_SKIP_OPTIONS_BUTTON_ID,
            on_click=broadcast_skip_options,
            style=Style(style=ButtonStyle.PRIMARY),
        ),
        Button(
            Format("{back_button_text}"),
            id=ADMIN_BROADCAST_BACK_TO_MENU_BUTTON_ID,
            on_click=show_menu,
        ),
    ),
    state=AdminSG.broadcast_options,
    getter=broadcast_options_getter,
)

broadcast_confirm_window: Window = Window(
    Format("{text}"),
    Row(
        Button(
            Format("{send_button_text}"),
            id=ADMIN_BROADCAST_CONFIRM_SEND_BUTTON_ID,
            on_click=broadcast_send,
            style=Style(style=ButtonStyle.PRIMARY),
        ),
        Button(
            Format("{restart_button_text}"),
            id=ADMIN_BROADCAST_CONFIRM_RESTART_BUTTON_ID,
            on_click=show_broadcast_content,
        ),
    ),
    Button(
        Format("{back_button_text}"),
        id=ADMIN_BROADCAST_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
    ),
    state=AdminSG.broadcast_confirm,
    getter=broadcast_confirm_getter,
)


__all__ = [
    "broadcast_buttons_window",
    "broadcast_confirm_window",
    "broadcast_content_window",
    "broadcast_options_window",
]
