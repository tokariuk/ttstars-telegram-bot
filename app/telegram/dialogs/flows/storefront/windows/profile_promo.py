from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format

from app.telegram.dialogs.common.premium_emoji import LEFT_SQUARE_EMOJI_ID

from ..getters import promo_getter
from ..handlers import handle_promo_input, show_profile
from ..ids import STOREFRONT_OPEN_PROFILE_BUTTON_ID
from ..states import StorefrontSG
from .common import banner_preview

promo_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    MessageInput(handle_promo_input),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_OPEN_PROFILE_BUTTON_ID,
        on_click=show_profile,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.promo,
    getter=promo_getter,
)

