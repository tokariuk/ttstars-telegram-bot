from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format

from app.telegram.dialogs.common.premium_emoji import LEFT_SQUARE_EMOJI_ID

from ..getters import calculator_getter
from ..handlers import handle_calculator_input, show_menu
from ..ids import STOREFRONT_BACK_TO_MENU_BUTTON_ID
from ..states import StorefrontSG
from .common import banner_preview

calculator_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    MessageInput(handle_calculator_input),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.calculator,
    getter=calculator_getter,
)
