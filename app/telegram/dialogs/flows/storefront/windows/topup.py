from aiogram.enums.button_style import ButtonStyle
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format

from app.telegram.dialogs.common.premium_emoji import (
    CRYPTOBOT_PAY_EMOJI_ID,
    EDIT_2_EMOJI_ID,
    HELEKET_PAY_EMOJI_ID,
    LEFT_SQUARE_EMOJI_ID,
    LZT_PAY_EMOJI_ID,
    NICEPAY_EMOJI_ID,
    SPB_PAY_EMOJI_ID,
    TON_EMOJI_ID,
    XROCKET_EMOJI_ID,
)

from ..getters import topup_amount_getter, topup_payment_getter
from ..handlers import (
    handle_topup_amount_input,
    pay_topup_with_crypto,
    pay_topup_with_heleket,
    pay_topup_with_lzt,
    pay_topup_with_nicepay_kz,
    pay_topup_with_nicepay_ru,
    pay_topup_with_platega,
    pay_topup_with_ton,
    pay_topup_with_xrocket,
    show_menu,
    show_profile,
    show_topup_amount,
)
from ..ids import (
    STOREFRONT_BACK_TO_MENU_BUTTON_ID,
    STOREFRONT_OPEN_PROFILE_BUTTON_ID,
    STOREFRONT_OPEN_TOPUP_BUTTON_ID,
    STOREFRONT_PAY_TOPUP_CRYPTO_BUTTON_ID,
    STOREFRONT_PAY_TOPUP_CRYPTO_DANGER_BUTTON_ID,
    STOREFRONT_PAY_TOPUP_HELEKET_BUTTON_ID,
    STOREFRONT_PAY_TOPUP_HELEKET_DANGER_BUTTON_ID,
    STOREFRONT_PAY_TOPUP_LZT_BUTTON_ID,
    STOREFRONT_PAY_TOPUP_LZT_DANGER_BUTTON_ID,
    STOREFRONT_PAY_TOPUP_NICEPAY_KZ_BUTTON_ID,
    STOREFRONT_PAY_TOPUP_NICEPAY_KZ_DANGER_BUTTON_ID,
    STOREFRONT_PAY_TOPUP_NICEPAY_RU_BUTTON_ID,
    STOREFRONT_PAY_TOPUP_NICEPAY_RU_DANGER_BUTTON_ID,
    STOREFRONT_PAY_TOPUP_PLATEGA_BUTTON_ID,
    STOREFRONT_PAY_TOPUP_PLATEGA_DANGER_BUTTON_ID,
    STOREFRONT_PAY_TOPUP_TON_BUTTON_ID,
    STOREFRONT_PAY_TOPUP_TON_DANGER_BUTTON_ID,
    STOREFRONT_PAY_TOPUP_XROCKET_BUTTON_ID,
    STOREFRONT_PAY_TOPUP_XROCKET_DANGER_BUTTON_ID,
)
from ..states import StorefrontSG
from .common import banner_preview

topup_amount_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    MessageInput(handle_topup_amount_input),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
        when="show_back_to_menu",
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    Button(
        Format("{back_profile_text}"),
        id=STOREFRONT_OPEN_PROFILE_BUTTON_ID,
        on_click=show_profile,
        when="show_back_to_profile",
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.topup_amount,
    getter=topup_amount_getter,
)

topup_payment_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    Button(
        Format("{pay_crypto_text}"),
        id=STOREFRONT_PAY_TOPUP_CRYPTO_BUTTON_ID,
        on_click=pay_topup_with_crypto,
        when="can_pay_crypto_primary",
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=CRYPTOBOT_PAY_EMOJI_ID),
    ),
    Button(
        Format("{pay_crypto_text}"),
        id=STOREFRONT_PAY_TOPUP_CRYPTO_DANGER_BUTTON_ID,
        on_click=pay_topup_with_crypto,
        when="can_pay_crypto_danger",
        style=Style(style=ButtonStyle.DANGER, emoji_id=CRYPTOBOT_PAY_EMOJI_ID),
    ),
    Button(
        Format("{pay_ton_text}"),
        id=STOREFRONT_PAY_TOPUP_TON_BUTTON_ID,
        on_click=pay_topup_with_ton,
        when="can_pay_ton_primary",
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=TON_EMOJI_ID),
    ),
    Button(
        Format("{pay_ton_text}"),
        id=STOREFRONT_PAY_TOPUP_TON_DANGER_BUTTON_ID,
        on_click=pay_topup_with_ton,
        when="can_pay_ton_danger",
        style=Style(style=ButtonStyle.DANGER, emoji_id=TON_EMOJI_ID),
    ),
    Button(
        Format("{pay_platega_text}"),
        id=STOREFRONT_PAY_TOPUP_PLATEGA_BUTTON_ID,
        on_click=pay_topup_with_platega,
        when="can_pay_platega_primary",
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=SPB_PAY_EMOJI_ID),
    ),
    Button(
        Format("{pay_platega_text}"),
        id=STOREFRONT_PAY_TOPUP_PLATEGA_DANGER_BUTTON_ID,
        on_click=pay_topup_with_platega,
        when="can_pay_platega_danger",
        style=Style(style=ButtonStyle.DANGER, emoji_id=SPB_PAY_EMOJI_ID),
    ),
    Button(
        Format("{pay_lzt_text}"),
        id=STOREFRONT_PAY_TOPUP_LZT_BUTTON_ID,
        on_click=pay_topup_with_lzt,
        when="can_pay_lzt_primary",
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=LZT_PAY_EMOJI_ID),
    ),
    Button(
        Format("{pay_lzt_text}"),
        id=STOREFRONT_PAY_TOPUP_LZT_DANGER_BUTTON_ID,
        on_click=pay_topup_with_lzt,
        when="can_pay_lzt_danger",
        style=Style(style=ButtonStyle.DANGER, emoji_id=LZT_PAY_EMOJI_ID),
    ),
    Button(
        Format("{pay_nicepay_ru_text}"),
        id=STOREFRONT_PAY_TOPUP_NICEPAY_RU_BUTTON_ID,
        on_click=pay_topup_with_nicepay_ru,
        when="can_pay_nicepay_ru_primary",
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=NICEPAY_EMOJI_ID),
    ),
    Button(
        Format("{pay_nicepay_ru_text}"),
        id=STOREFRONT_PAY_TOPUP_NICEPAY_RU_DANGER_BUTTON_ID,
        on_click=pay_topup_with_nicepay_ru,
        when="can_pay_nicepay_ru_danger",
        style=Style(style=ButtonStyle.DANGER, emoji_id=NICEPAY_EMOJI_ID),
    ),
    Button(
        Format("{pay_nicepay_kz_text}"),
        id=STOREFRONT_PAY_TOPUP_NICEPAY_KZ_BUTTON_ID,
        on_click=pay_topup_with_nicepay_kz,
        when="can_pay_nicepay_kz_primary",
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=NICEPAY_EMOJI_ID),
    ),
    Button(
        Format("{pay_nicepay_kz_text}"),
        id=STOREFRONT_PAY_TOPUP_NICEPAY_KZ_DANGER_BUTTON_ID,
        on_click=pay_topup_with_nicepay_kz,
        when="can_pay_nicepay_kz_danger",
        style=Style(style=ButtonStyle.DANGER, emoji_id=NICEPAY_EMOJI_ID),
    ),
    Button(
        Format("{pay_heleket_text}"),
        id=STOREFRONT_PAY_TOPUP_HELEKET_BUTTON_ID,
        on_click=pay_topup_with_heleket,
        when="can_pay_heleket_primary",
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=HELEKET_PAY_EMOJI_ID),
    ),
    Button(
        Format("{pay_heleket_text}"),
        id=STOREFRONT_PAY_TOPUP_HELEKET_DANGER_BUTTON_ID,
        on_click=pay_topup_with_heleket,
        when="can_pay_heleket_danger",
        style=Style(style=ButtonStyle.DANGER, emoji_id=HELEKET_PAY_EMOJI_ID),
    ),
    Button(
        Format("{pay_xrocket_text}"),
        id=STOREFRONT_PAY_TOPUP_XROCKET_BUTTON_ID,
        on_click=pay_topup_with_xrocket,
        when="can_pay_xrocket_primary",
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=XROCKET_EMOJI_ID),
    ),
    Button(
        Format("{pay_xrocket_text}"),
        id=STOREFRONT_PAY_TOPUP_XROCKET_DANGER_BUTTON_ID,
        on_click=pay_topup_with_xrocket,
        when="can_pay_xrocket_danger",
        style=Style(style=ButtonStyle.DANGER, emoji_id=XROCKET_EMOJI_ID),
    ),
    Button(
        Format("{change_amount_text}"),
        id=STOREFRONT_OPEN_TOPUP_BUTTON_ID,
        on_click=show_topup_amount,
        style=Style(emoji_id=EDIT_2_EMOJI_ID),
    ),
    Button(
        Format("{back_profile_text}"),
        id=STOREFRONT_OPEN_PROFILE_BUTTON_ID,
        on_click=show_profile,
        when="show_back_to_profile",
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
        when="show_back_to_menu",
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.topup_payment,
    getter=topup_payment_getter,
)
