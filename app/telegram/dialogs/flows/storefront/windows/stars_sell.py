from operator import itemgetter

from aiogram.enums.button_style import ButtonStyle
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, ListGroup, Row
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format

from app.telegram.dialogs.common.premium_emoji import (
    CHECK_EMOJI_ID,
    DOCUMENT_EMOJI_ID,
    EDIT_2_EMOJI_ID,
    LEFT_CIRCLE_2_EMOJI_ID,
    LEFT_SQUARE_EMOJI_ID,
    PLUS_EMOJI_ID,
    RIGHT_CIRCLE_2_EMOJI_ID,
)

from ..getters import (
    stars_sell_history_details_getter,
    stars_sell_history_getter,
    stars_sell_menu_getter,
    stars_sell_payment_getter,
    stars_sell_stars_getter,
    stars_sell_wallet_getter,
)
from ..handlers import (
    handle_stars_sell_stars_input,
    handle_stars_sell_wallet_input,
    open_stars_sell_history_order,
    send_stars_sell_invoice,
    show_menu,
    show_stars_sell_history,
    show_stars_sell_history_page_info,
    show_stars_sell_menu,
    show_stars_sell_stars,
    show_stars_sell_wallet,
    stars_sell_history_next_page,
    stars_sell_history_prev_page,
)
from ..ids import (
    STOREFRONT_BACK_TO_MENU_BUTTON_ID,
    STOREFRONT_STARS_SELL_CHANGE_STARS_BUTTON_ID,
    STOREFRONT_STARS_SELL_CHANGE_WALLET_BUTTON_ID,
    STOREFRONT_STARS_SELL_CREATE_REQUEST_BUTTON_ID,
    STOREFRONT_STARS_SELL_HISTORY_BACK_TO_LIST_BUTTON_ID,
    STOREFRONT_STARS_SELL_HISTORY_BUTTON_ID,
    STOREFRONT_STARS_SELL_HISTORY_NEXT_BUTTON_ID,
    STOREFRONT_STARS_SELL_HISTORY_PAGE_BUTTON_ID,
    STOREFRONT_STARS_SELL_HISTORY_PREV_BUTTON_ID,
    STOREFRONT_STARS_SELL_HISTORY_SELECT_ID,
    STOREFRONT_STARS_SELL_SEND_INVOICE_BUTTON_ID,
)
from ..states import StorefrontSG
from .common import banner_preview

stars_sell_menu_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    Button(
        Format("{create_request_button_text}"),
        id=STOREFRONT_STARS_SELL_CREATE_REQUEST_BUTTON_ID,
        on_click=show_stars_sell_stars,
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=PLUS_EMOJI_ID),
    ),
    Button(
        Format("{history_button_text}"),
        id=STOREFRONT_STARS_SELL_HISTORY_BUTTON_ID,
        on_click=show_stars_sell_history,
        style=Style(emoji_id=DOCUMENT_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.stars_sell_menu,
    getter=stars_sell_menu_getter,
)

stars_sell_stars_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    MessageInput(handle_stars_sell_stars_input),
    Button(
        Format("{back_to_stars_sell_button_text}"),
        id=STOREFRONT_STARS_SELL_HISTORY_BACK_TO_LIST_BUTTON_ID,
        on_click=show_stars_sell_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    Button(
        Format("{back_to_menu_button_text}"),
        id=STOREFRONT_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.stars_sell_stars,
    getter=stars_sell_stars_getter,
)

stars_sell_wallet_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    MessageInput(handle_stars_sell_wallet_input),
    Button(
        Format("{change_stars_button_text}"),
        id=STOREFRONT_STARS_SELL_CHANGE_STARS_BUTTON_ID,
        on_click=show_stars_sell_stars,
        style=Style(emoji_id=EDIT_2_EMOJI_ID),
    ),
    Button(
        Format("{back_to_stars_sell_button_text}"),
        id=STOREFRONT_STARS_SELL_HISTORY_BACK_TO_LIST_BUTTON_ID,
        on_click=show_stars_sell_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    Button(
        Format("{back_to_menu_button_text}"),
        id=STOREFRONT_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.stars_sell_wallet,
    getter=stars_sell_wallet_getter,
)

stars_sell_payment_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    Button(
        Format("{send_invoice_button_text}"),
        id=STOREFRONT_STARS_SELL_SEND_INVOICE_BUTTON_ID,
        on_click=send_stars_sell_invoice,
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=CHECK_EMOJI_ID),
    ),
    Button(
        Format("{change_stars_button_text}"),
        id=STOREFRONT_STARS_SELL_CHANGE_STARS_BUTTON_ID,
        on_click=show_stars_sell_stars,
        style=Style(emoji_id=EDIT_2_EMOJI_ID),
    ),
    Button(
        Format("{change_wallet_button_text}"),
        id=STOREFRONT_STARS_SELL_CHANGE_WALLET_BUTTON_ID,
        on_click=show_stars_sell_wallet,
        style=Style(emoji_id=EDIT_2_EMOJI_ID),
    ),
    Button(
        Format("{back_to_stars_sell_button_text}"),
        id=STOREFRONT_STARS_SELL_HISTORY_BACK_TO_LIST_BUTTON_ID,
        on_click=show_stars_sell_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    Button(
        Format("{back_to_menu_button_text}"),
        id=STOREFRONT_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.stars_sell_payment,
    getter=stars_sell_payment_getter,
)

stars_sell_history_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    ListGroup(
        Button(
            Format("{item[button_text]}"),
            id=STOREFRONT_STARS_SELL_HISTORY_SELECT_ID,
            on_click=open_stars_sell_history_order,
        ),
        id="ssh",
        item_id_getter=itemgetter("id"),
        items="orders",
    ),
    Row(
        Button(
            Format("{prev_button_text}"),
            id=STOREFRONT_STARS_SELL_HISTORY_PREV_BUTTON_ID,
            on_click=stars_sell_history_prev_page,
            when="show_prev_page",
            style=Style(emoji_id=LEFT_CIRCLE_2_EMOJI_ID),
        ),
        Button(
            Format("{page_button_text}"),
            id=STOREFRONT_STARS_SELL_HISTORY_PAGE_BUTTON_ID,
            on_click=show_stars_sell_history_page_info,
            when="show_page_info",
        ),
        Button(
            Format("{next_button_text}"),
            id=STOREFRONT_STARS_SELL_HISTORY_NEXT_BUTTON_ID,
            on_click=stars_sell_history_next_page,
            when="show_next_page",
            style=Style(emoji_id=RIGHT_CIRCLE_2_EMOJI_ID),
        ),
    ),
    Button(
        Format("{back_to_stars_sell_button_text}"),
        id=STOREFRONT_STARS_SELL_HISTORY_BACK_TO_LIST_BUTTON_ID,
        on_click=show_stars_sell_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    Button(
        Format("{back_to_menu_button_text}"),
        id=STOREFRONT_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.stars_sell_history,
    getter=stars_sell_history_getter,
)

stars_sell_history_details_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    Button(
        Format("{back_to_history_button_text}"),
        id=STOREFRONT_STARS_SELL_HISTORY_BACK_TO_LIST_BUTTON_ID,
        on_click=show_stars_sell_history,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    Button(
        Format("{back_to_stars_sell_button_text}"),
        id=STOREFRONT_STARS_SELL_HISTORY_BUTTON_ID,
        on_click=show_stars_sell_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    Button(
        Format("{back_to_menu_button_text}"),
        id=STOREFRONT_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.stars_sell_history_details,
    getter=stars_sell_history_details_getter,
)


__all__ = [
    "stars_sell_history_details_window",
    "stars_sell_history_window",
    "stars_sell_menu_window",
    "stars_sell_payment_window",
    "stars_sell_stars_window",
    "stars_sell_wallet_window",
]
