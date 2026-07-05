from aiogram.enums.button_style import ButtonStyle
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format

from app.telegram.dialogs.common.premium_emoji import (
    DOCUMENT_EMOJI_ID,
    LEFT_SQUARE_EMOJI_ID,
    PLUS_EMOJI_ID,
    RECEIPT_EMOJI_ID,
    SALE_EMOJI_ID,
    USERS_EMOJI_ID,
)

from ..getters import profile_getter
from ..handlers import (
    show_checks,
    show_history,
    show_menu,
    show_promo,
    show_referrals,
    show_topup_amount_from_profile,
)
from ..ids import (
    STOREFRONT_BACK_TO_MENU_BUTTON_ID,
    STOREFRONT_OPEN_CHECKS_BUTTON_ID,
    STOREFRONT_OPEN_HISTORY_BUTTON_ID,
    STOREFRONT_OPEN_PROMO_BUTTON_ID,
    STOREFRONT_OPEN_REFERRALS_BUTTON_ID,
    STOREFRONT_OPEN_TOPUP_BUTTON_ID,
)
from ..states import StorefrontSG
from .common import banner_preview

profile_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    Button(
        Format("{topup_button_text}"),
        id=STOREFRONT_OPEN_TOPUP_BUTTON_ID,
        on_click=show_topup_amount_from_profile,
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=PLUS_EMOJI_ID),
    ),
    Button(
        Format("{promo_button_text}"),
        id=STOREFRONT_OPEN_PROMO_BUTTON_ID,
        on_click=show_promo,
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=SALE_EMOJI_ID),
    ),
    Button(
        Format("{referrals_button_text}"),
        id=STOREFRONT_OPEN_REFERRALS_BUTTON_ID,
        on_click=show_referrals,
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=USERS_EMOJI_ID),
    ),
    Button(
        Format("{checks_button_text}"),
        id=STOREFRONT_OPEN_CHECKS_BUTTON_ID,
        on_click=show_checks,
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=RECEIPT_EMOJI_ID),
    ),
    Button(
        Format("{history_button_text}"),
        id=STOREFRONT_OPEN_HISTORY_BUTTON_ID,
        on_click=show_history,
        style=Style(emoji_id=DOCUMENT_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.profile,
    getter=profile_getter,
)

