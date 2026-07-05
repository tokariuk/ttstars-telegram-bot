from operator import itemgetter

from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, ListGroup, Row
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format

from app.telegram.dialogs.common.premium_emoji import (
    LEFT_CIRCLE_2_EMOJI_ID,
    LEFT_SQUARE_EMOJI_ID,
    RIGHT_CIRCLE_2_EMOJI_ID,
)

from ..getters import history_details_getter, history_getter
from ..handlers import (
    history_next_page,
    history_prev_page,
    open_history_order,
    show_history_list,
    show_history_page_info,
    show_profile,
)
from ..ids import (
    STOREFRONT_HISTORY_BACK_TO_LIST_BUTTON_ID,
    STOREFRONT_HISTORY_NEXT_BUTTON_ID,
    STOREFRONT_HISTORY_PAGE_BUTTON_ID,
    STOREFRONT_HISTORY_PREV_BUTTON_ID,
    STOREFRONT_HISTORY_SELECT_ORDER_ID,
    STOREFRONT_OPEN_PROFILE_BUTTON_ID,
)
from ..states import StorefrontSG
from .common import banner_preview

history_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    ListGroup(
        Button(
            Format("{item[button_text]}"),
            id=STOREFRONT_HISTORY_SELECT_ORDER_ID,
            on_click=open_history_order,
        ),
        id="hl",
        item_id_getter=itemgetter("id"),
        items="operations",
    ),
    Row(
        Button(
            Format("{prev_button_text}"),
            id=STOREFRONT_HISTORY_PREV_BUTTON_ID,
            on_click=history_prev_page,
            when="show_prev_page",
            style=Style(emoji_id=LEFT_CIRCLE_2_EMOJI_ID),
        ),
        Button(
            Format("{page_button_text}"),
            id=STOREFRONT_HISTORY_PAGE_BUTTON_ID,
            on_click=show_history_page_info,
            when="show_page_info",
        ),
        Button(
            Format("{next_button_text}"),
            id=STOREFRONT_HISTORY_NEXT_BUTTON_ID,
            on_click=history_next_page,
            when="show_next_page",
            style=Style(emoji_id=RIGHT_CIRCLE_2_EMOJI_ID),
        ),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_OPEN_PROFILE_BUTTON_ID,
        on_click=show_profile,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.history,
    getter=history_getter,
)

history_details_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    Button(
        Format("{back_to_history_text}"),
        id=STOREFRONT_HISTORY_BACK_TO_LIST_BUTTON_ID,
        on_click=show_history_list,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_OPEN_PROFILE_BUTTON_ID,
        on_click=show_profile,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.history_details,
    getter=history_details_getter,
)

