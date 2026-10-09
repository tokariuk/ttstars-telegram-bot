from operator import itemgetter

from aiogram.enums.button_style import ButtonStyle
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, ListGroup, Row
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format

from app.telegram.dialogs.common.ttstars_interface_emoji import (
    CHECK_EMOJI_ID,
    DOCUMENT_ADD_EMOJI_ID,
    DOCUMENT_EMOJI_ID,
    EDIT_2_EMOJI_ID,
    INFO_CIRCLE_EMOJI_ID,
    LEFT_CIRCLE_EMOJI_ID,
    LEFT_SQUARE_EMOJI_ID,
    LIGHTNING_EMOJI_ID,
    PAUSE_EMOJI_ID,
    PLUS_EMOJI_ID,
    RIGHT_CIRCLE_EMOJI_ID,
    SETTINGS_EMOJI_ID,
    TRASH_CAN_EMOJI_ID,
)

from ..getters import (
    promo_bulk_getter,
    promo_create_getter,
    promo_details_getter,
    promo_menu_getter,
    promo_quick_getter,
    promo_set_limit_getter,
)
from ..handlers import (
    handle_promo_bulk_input,
    handle_promo_create_input,
    handle_promo_quick_input,
    handle_promo_set_limit_input,
    open_promo_code,
    promo_cleanup_exhausted,
    promo_delete_bulk_selected,
    promo_delete_selected,
    promo_next_page,
    promo_prev_page,
    promo_set_selected_one_time,
    promo_set_selected_unlimited,
    promo_toggle_selected,
    show_menu,
    show_promo_bulk,
    show_promo_create,
    show_promo_details_current,
    show_promo_menu,
    show_promo_page_info,
    show_promo_quick,
    show_promo_set_limit,
    toggle_promo_bulk_mode,
)
from ..ids import (
    ADMIN_PROMO_BACK_TO_LIST_BUTTON_ID,
    ADMIN_PROMO_BACK_TO_MENU_BUTTON_ID,
    ADMIN_PROMO_BULK_BUTTON_ID,
    ADMIN_PROMO_BULK_DELETE_SELECTED_BUTTON_ID,
    ADMIN_PROMO_BULK_MODE_BUTTON_ID,
    ADMIN_PROMO_CLEANUP_BUTTON_ID,
    ADMIN_PROMO_CREATE_BUTTON_ID,
    ADMIN_PROMO_CUSTOM_LIMIT_BUTTON_ID,
    ADMIN_PROMO_DELETE_BUTTON_ID,
    ADMIN_PROMO_NEXT_BUTTON_ID,
    ADMIN_PROMO_ONE_TIME_BUTTON_ID,
    ADMIN_PROMO_PAGE_BUTTON_ID,
    ADMIN_PROMO_PREV_BUTTON_ID,
    ADMIN_PROMO_QUICK_BUTTON_ID,
    ADMIN_PROMO_SELECT_CODE_BUTTON_ID,
    ADMIN_PROMO_SET_LIMIT_BUTTON_ID,
    ADMIN_PROMO_TOGGLE_BUTTON_ID,
    ADMIN_PROMO_UNLIMITED_BUTTON_ID,
)
from ..states import AdminSG

promo_menu_window: Window = Window(
    Format("{text}"),
    ListGroup(
        Button(
            Format("{item[button_text]}"),
            id=ADMIN_PROMO_SELECT_CODE_BUTTON_ID,
            on_click=open_promo_code,
            style=Style(emoji_id=DOCUMENT_EMOJI_ID),
        ),
        id="apl",
        item_id_getter=itemgetter("id"),
        items="codes",
    ),
    Row(
        Button(
            Format("{prev_button_text}"),
            id=ADMIN_PROMO_PREV_BUTTON_ID,
            on_click=promo_prev_page,
            when="show_prev_page",
            style=Style(emoji_id=LEFT_CIRCLE_EMOJI_ID),
        ),
        Button(
            Format("{page_button_text}"),
            id=ADMIN_PROMO_PAGE_BUTTON_ID,
            on_click=show_promo_page_info,
            when="show_page_info",
            style=Style(emoji_id=INFO_CIRCLE_EMOJI_ID),
        ),
        Button(
            Format("{next_button_text}"),
            id=ADMIN_PROMO_NEXT_BUTTON_ID,
            on_click=promo_next_page,
            when="show_next_page",
            style=Style(emoji_id=RIGHT_CIRCLE_EMOJI_ID),
        ),
    ),
    Row(
        Button(
            Format("{create_button_text}"),
            id=ADMIN_PROMO_CREATE_BUTTON_ID,
            on_click=show_promo_create,
            style=Style(style=ButtonStyle.PRIMARY, emoji_id=PLUS_EMOJI_ID),
        ),
        Button(
            Format("{quick_button_text}"),
            id=ADMIN_PROMO_QUICK_BUTTON_ID,
            on_click=show_promo_quick,
            style=Style(style=ButtonStyle.PRIMARY, emoji_id=LIGHTNING_EMOJI_ID),
        ),
    ),
    Row(
        Button(
            Format("{bulk_button_text}"),
            id=ADMIN_PROMO_BULK_BUTTON_ID,
            on_click=show_promo_bulk,
            style=Style(emoji_id=DOCUMENT_ADD_EMOJI_ID),
        ),
        Button(
            Format("{bulk_mode_button_text}"),
            id=ADMIN_PROMO_BULK_MODE_BUTTON_ID,
            on_click=toggle_promo_bulk_mode,
            style=Style(emoji_id=CHECK_EMOJI_ID),
        ),
    ),
    Row(
        Button(
            Format("{bulk_delete_selected_button_text}"),
            id=ADMIN_PROMO_BULK_DELETE_SELECTED_BUTTON_ID,
            on_click=promo_delete_bulk_selected,
            when="show_bulk_delete_selected",
            style=Style(style=ButtonStyle.DANGER, emoji_id=TRASH_CAN_EMOJI_ID),
        ),
        Button(
            Format("{cleanup_button_text}"),
            id=ADMIN_PROMO_CLEANUP_BUTTON_ID,
            on_click=promo_cleanup_exhausted,
            when="show_cleanup",
            style=Style(emoji_id=TRASH_CAN_EMOJI_ID),
        ),
    ),
    Button(
        Format("{back_button_text}"),
        id=ADMIN_PROMO_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=AdminSG.promo_menu,
    getter=promo_menu_getter,
)

promo_details_window: Window = Window(
    Format("{text}"),
    Button(
        Format("{toggle_button_text}"),
        id=ADMIN_PROMO_TOGGLE_BUTTON_ID,
        on_click=promo_toggle_selected,
        when="has_code",
        style=Style(emoji_id=PAUSE_EMOJI_ID),
    ),
    Row(
        Button(
            Format("{set_one_time_button_text}"),
            id=ADMIN_PROMO_ONE_TIME_BUTTON_ID,
            on_click=promo_set_selected_one_time,
            style=Style(emoji_id=CHECK_EMOJI_ID),
        ),
        Button(
            Format("{set_unlimited_button_text}"),
            id=ADMIN_PROMO_UNLIMITED_BUTTON_ID,
            on_click=promo_set_selected_unlimited,
            style=Style(emoji_id=SETTINGS_EMOJI_ID),
        ),
        when="has_code",
    ),
    Row(
        Button(
            Format("{set_custom_limit_button_text}"),
            id=ADMIN_PROMO_CUSTOM_LIMIT_BUTTON_ID,
            on_click=show_promo_set_limit,
            style=Style(emoji_id=EDIT_2_EMOJI_ID),
        ),
        Button(
            Format("{delete_button_text}"),
            id=ADMIN_PROMO_DELETE_BUTTON_ID,
            on_click=promo_delete_selected,
            style=Style(style=ButtonStyle.DANGER, emoji_id=TRASH_CAN_EMOJI_ID),
        ),
        when="has_code",
    ),
    Button(
        Format("{back_to_list_button_text}"),
        id=ADMIN_PROMO_BACK_TO_LIST_BUTTON_ID,
        on_click=show_promo_menu,
        style=Style(emoji_id=LEFT_CIRCLE_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=ADMIN_PROMO_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=AdminSG.promo_details,
    getter=promo_details_getter,
)

promo_create_window: Window = Window(
    Format("{text}"),
    MessageInput(handle_promo_create_input),
    Button(
        Format("{back_button_text}"),
        id=ADMIN_PROMO_BACK_TO_LIST_BUTTON_ID,
        on_click=show_promo_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=AdminSG.promo_create,
    getter=promo_create_getter,
)

promo_quick_window: Window = Window(
    Format("{text}"),
    MessageInput(handle_promo_quick_input),
    Button(
        Format("{back_button_text}"),
        id=ADMIN_PROMO_BACK_TO_LIST_BUTTON_ID,
        on_click=show_promo_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=AdminSG.promo_quick,
    getter=promo_quick_getter,
)

promo_bulk_window: Window = Window(
    Format("{text}"),
    MessageInput(handle_promo_bulk_input),
    Button(
        Format("{back_button_text}"),
        id=ADMIN_PROMO_BACK_TO_LIST_BUTTON_ID,
        on_click=show_promo_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=AdminSG.promo_bulk,
    getter=promo_bulk_getter,
)

promo_set_limit_window: Window = Window(
    Format("{text}"),
    MessageInput(handle_promo_set_limit_input),
    Button(
        Format("{back_button_text}"),
        id=ADMIN_PROMO_SET_LIMIT_BUTTON_ID,
        on_click=show_promo_details_current,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=AdminSG.promo_set_limit,
    getter=promo_set_limit_getter,
)


__all__ = [
    "promo_bulk_window",
    "promo_create_window",
    "promo_details_window",
    "promo_menu_window",
    "promo_quick_window",
    "promo_set_limit_window",
]
