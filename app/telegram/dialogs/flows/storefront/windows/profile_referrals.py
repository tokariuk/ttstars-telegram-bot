from operator import itemgetter

from aiogram.enums.button_style import ButtonStyle
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, ListGroup, Row
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format

from app.telegram.dialogs.common.premium_emoji import (
    LEFT_CIRCLE_2_EMOJI_ID,
    LEFT_SQUARE_EMOJI_ID,
    RIGHT_CIRCLE_2_EMOJI_ID,
    USERS_EMOJI_ID,
    WALLET_EMOJI_ID,
)

from ..getters import (
    referral_details_getter,
    referral_getter,
    referral_list_getter,
    referral_withdraw_getter,
)
from ..handlers import (
    handle_referral_withdraw_input,
    open_referral_member,
    referrals_next_page,
    referrals_prev_page,
    show_profile,
    show_referrals,
    show_referrals_list,
    show_referrals_list_current,
    show_referrals_page_info,
    withdraw_referral_balance,
)
from ..ids import (
    STOREFRONT_OPEN_PROFILE_BUTTON_ID,
    STOREFRONT_OPEN_REFERRALS_BUTTON_ID,
    STOREFRONT_OPEN_REFERRALS_LIST_BUTTON_ID,
    STOREFRONT_REFERRAL_BACK_TO_LIST_BUTTON_ID,
    STOREFRONT_REFERRAL_NEXT_BUTTON_ID,
    STOREFRONT_REFERRAL_PAGE_BUTTON_ID,
    STOREFRONT_REFERRAL_PREV_BUTTON_ID,
    STOREFRONT_REFERRAL_SELECT_USER_ID,
    STOREFRONT_WITHDRAW_REFERRAL_BALANCE_BUTTON_ID,
)
from ..states import StorefrontSG
from .common import banner_preview

referral_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    Button(
        Format("{list_button_text}"),
        id=STOREFRONT_OPEN_REFERRALS_LIST_BUTTON_ID,
        on_click=show_referrals_list,
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=USERS_EMOJI_ID),
    ),
    Button(
        Format("{withdraw_button_text}"),
        id=STOREFRONT_WITHDRAW_REFERRAL_BALANCE_BUTTON_ID,
        on_click=withdraw_referral_balance,
        when="can_withdraw",
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=WALLET_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_OPEN_PROFILE_BUTTON_ID,
        on_click=show_profile,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.referrals,
    getter=referral_getter,
)

referral_withdraw_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    MessageInput(handle_referral_withdraw_input),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_OPEN_REFERRALS_BUTTON_ID,
        on_click=show_referrals,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.referrals_withdraw,
    getter=referral_withdraw_getter,
)

referral_list_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    ListGroup(
        Button(
            Format("{item[button_text]}"),
            id=STOREFRONT_REFERRAL_SELECT_USER_ID,
            on_click=open_referral_member,
        ),
        id="rl",
        item_id_getter=itemgetter("id"),
        items="members",
    ),
    Row(
        Button(
            Format("{prev_button_text}"),
            id=STOREFRONT_REFERRAL_PREV_BUTTON_ID,
            on_click=referrals_prev_page,
            when="show_prev_page",
            style=Style(emoji_id=LEFT_CIRCLE_2_EMOJI_ID),
        ),
        Button(
            Format("{page_button_text}"),
            id=STOREFRONT_REFERRAL_PAGE_BUTTON_ID,
            on_click=show_referrals_page_info,
            when="show_page_info",
        ),
        Button(
            Format("{next_button_text}"),
            id=STOREFRONT_REFERRAL_NEXT_BUTTON_ID,
            on_click=referrals_next_page,
            when="show_next_page",
            style=Style(emoji_id=RIGHT_CIRCLE_2_EMOJI_ID),
        ),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_OPEN_REFERRALS_BUTTON_ID,
        on_click=show_referrals,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.referrals_list,
    getter=referral_list_getter,
)

referral_details_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    Button(
        Format("{back_to_list_text}"),
        id=STOREFRONT_REFERRAL_BACK_TO_LIST_BUTTON_ID,
        on_click=show_referrals_list_current,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_OPEN_REFERRALS_BUTTON_ID,
        on_click=show_referrals,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.referrals_details,
    getter=referral_details_getter,
)

