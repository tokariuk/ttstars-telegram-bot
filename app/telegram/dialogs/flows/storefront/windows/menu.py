from aiogram.enums.button_style import ButtonStyle
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Row, WebApp
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format

from app.telegram.dialogs.common.premium_emoji import (
    CALCULATOR_EMOJI_ID,
    GIFT_EMOJI_ID,
    INFO_SQUARE_EMOJI_ID,
    LIGHTNING_EMOJI_ID,
    PLUS_EMOJI_ID,
    TELEGRAM_STAR_EMOJI_ID,
    USER_EMOJI_ID,
)
from app.telegram.dialogs.common.ttstars_interface_emoji import COMPASS_EMOJI_ID

from ..getters import menu_getter
from ..handlers import (
    show_calculator,
    show_faq,
    show_gifts,
    show_premium_recipient,
    show_profile,
    show_stars_recipient,
    show_stars_sell,
    show_topup_amount,
)
from ..ids import (
    STOREFRONT_OPEN_CALCULATOR_BUTTON_ID,
    STOREFRONT_OPEN_FAQ_BUTTON_ID,
    STOREFRONT_OPEN_GIFTS_BUTTON_ID,
    STOREFRONT_OPEN_MINIAPP_BUTTON_ID,
    STOREFRONT_OPEN_PREMIUM_BUTTON_ID,
    STOREFRONT_OPEN_PROFILE_BUTTON_ID,
    STOREFRONT_OPEN_STARS_BUTTON_ID,
    STOREFRONT_OPEN_STARS_SELL_BUTTON_ID,
    STOREFRONT_OPEN_TOPUP_BUTTON_ID,
)
from ..states import StorefrontSG
from .common import banner_preview

menu_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    WebApp(
        Format("{miniapp_button_text}"),
        Format("{miniapp_url}"),
        id=STOREFRONT_OPEN_MINIAPP_BUTTON_ID,
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=COMPASS_EMOJI_ID),
    ),
    Row(
        Button(
            Format("{buy_stars_button_text}"),
            id=STOREFRONT_OPEN_STARS_BUTTON_ID,
            on_click=show_stars_recipient,
            style=Style(style=ButtonStyle.PRIMARY, emoji_id=TELEGRAM_STAR_EMOJI_ID),
        ),
        Button(
            Format("{buy_premium_button_text}"),
            id=STOREFRONT_OPEN_PREMIUM_BUTTON_ID,
            on_click=show_premium_recipient,
            style=Style(style=ButtonStyle.PRIMARY, emoji_id=LIGHTNING_EMOJI_ID),
        ),
    ),
    Button(
        Format("{buy_gifts_button_text}"),
        id=STOREFRONT_OPEN_GIFTS_BUTTON_ID,
        on_click=show_gifts,
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=GIFT_EMOJI_ID),
    ),
    Button(
        Format("{sell_stars_button_text}"),
        id=STOREFRONT_OPEN_STARS_SELL_BUTTON_ID,
        on_click=show_stars_sell,
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=TELEGRAM_STAR_EMOJI_ID),
    ),
    Button(
        Format("{topup_button_text}"),
        id=STOREFRONT_OPEN_TOPUP_BUTTON_ID,
        on_click=show_topup_amount,
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=PLUS_EMOJI_ID),
    ),
    Button(
        Format("{profile_button_text}"),
        id=STOREFRONT_OPEN_PROFILE_BUTTON_ID,
        on_click=show_profile,
        style=Style(emoji_id=USER_EMOJI_ID),
    ),
    Button(
        Format("{calculator_button_text}"),
        id=STOREFRONT_OPEN_CALCULATOR_BUTTON_ID,
        on_click=show_calculator,
        style=Style(emoji_id=CALCULATOR_EMOJI_ID),
    ),
    Button(
        Format("{faq_button_text}"),
        id=STOREFRONT_OPEN_FAQ_BUTTON_ID,
        on_click=show_faq,
        style=Style(emoji_id=INFO_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.menu,
    getter=menu_getter,
)
