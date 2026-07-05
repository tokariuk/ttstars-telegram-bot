from operator import itemgetter

from aiogram.enums.button_style import ButtonStyle
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Button,
    ListGroup,
    Row,
    SwitchInlineQueryChosenChatButton,
)
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format

from app.telegram.dialogs.common.premium_emoji import (
    CHECK_EMOJI_ID,
    CLOSE_EMOJI_ID,
    DOCUMENT_EMOJI_ID,
    EDIT_2_EMOJI_ID,
    LEFT_CIRCLE_2_EMOJI_ID,
    LEFT_SQUARE_EMOJI_ID,
    PLUS_EMOJI_ID,
    RECEIPT_EMOJI_ID,
    RIGHT_CIRCLE_2_EMOJI_ID,
    SETTINGS_EMOJI_ID,
    SHARE_EMOJI_ID,
)

from ..getters import (
    checks_claim_password_getter,
    checks_create_confirm_getter,
    checks_create_password_getter,
    checks_create_recipient_getter,
    checks_create_stars_getter,
    checks_details_getter,
    checks_edit_password_getter,
    checks_edit_recipient_getter,
    checks_history_details_getter,
    checks_history_getter,
    checks_list_getter,
    checks_settings_getter,
)
from ..handlers import (
    checks_history_next_page,
    checks_history_prev_page,
    checks_next_page,
    checks_prev_page,
    clear_selected_check_password,
    clear_selected_check_recipient,
    close_selected_check,
    confirm_check_create,
    handle_check_activation_password_input,
    handle_check_claim_password_input,
    handle_check_claim_recipient_input,
    handle_check_edit_password_input,
    handle_check_edit_recipient_input,
    handle_check_stars_input,
    open_check,
    open_check_history,
    show_checks_create_password,
    show_checks_create_recipient,
    show_checks_create_stars,
    show_checks_current,
    show_checks_details_current,
    show_checks_edit_password,
    show_checks_edit_recipient,
    show_checks_history,
    show_checks_history_list,
    show_checks_history_page_info,
    show_checks_page_info,
    show_checks_settings,
    show_menu,
    show_profile,
    skip_check_claim_password,
    skip_check_claim_recipient,
)
from ..ids import (
    STOREFRONT_CHECK_BACK_TO_LIST_BUTTON_ID,
    STOREFRONT_CHECK_CLAIM_PASSWORD_CANCEL_ID,
    STOREFRONT_CHECK_CLOSE_BUTTON_ID,
    STOREFRONT_CHECK_CREATE_CHANGE_AMOUNT_ID,
    STOREFRONT_CHECK_CREATE_CHANGE_PASSWORD_ID,
    STOREFRONT_CHECK_CREATE_CHANGE_RECIPIENT_ID,
    STOREFRONT_CHECK_CREATE_CONFIRM_ID,
    STOREFRONT_CHECK_CREATE_FROM_CHAT_ID,
    STOREFRONT_CHECK_CREATE_SKIP_PASSWORD_ID,
    STOREFRONT_CHECK_CREATE_SKIP_RECIPIENT_ID,
    STOREFRONT_CHECK_SELECT_ID,
    STOREFRONT_CHECK_SETTINGS_BACK_ID,
    STOREFRONT_CHECK_SETTINGS_BUTTON_ID,
    STOREFRONT_CHECK_SETTINGS_CLEAR_PASSWORD_ID,
    STOREFRONT_CHECK_SETTINGS_CLEAR_RECIPIENT_ID,
    STOREFRONT_CHECK_SETTINGS_EDIT_PASSWORD_ID,
    STOREFRONT_CHECK_SETTINGS_EDIT_RECIPIENT_ID,
    STOREFRONT_CHECK_SHARE_URL_ID,
    STOREFRONT_CHECKS_EDIT_BACK_ID,
    STOREFRONT_CHECKS_HISTORY_BACK_TO_LIST_BUTTON_ID,
    STOREFRONT_CHECKS_HISTORY_NEXT_BUTTON_ID,
    STOREFRONT_CHECKS_HISTORY_OPEN_BUTTON_ID,
    STOREFRONT_CHECKS_HISTORY_PAGE_BUTTON_ID,
    STOREFRONT_CHECKS_HISTORY_PREV_BUTTON_ID,
    STOREFRONT_CHECKS_HISTORY_SELECT_ID,
    STOREFRONT_CHECKS_NEXT_BUTTON_ID,
    STOREFRONT_CHECKS_PAGE_BUTTON_ID,
    STOREFRONT_CHECKS_PREV_BUTTON_ID,
    STOREFRONT_CREATE_STARS_CHECK_BUTTON_ID,
    STOREFRONT_OPEN_PROFILE_BUTTON_ID,
)
from ..states import StorefrontSG
from .common import banner_preview

checks_list_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    ListGroup(
        Button(
            Format("{item[button_text]}"),
            id=STOREFRONT_CHECK_SELECT_ID,
            on_click=open_check,
        ),
        id="cl",
        item_id_getter=itemgetter("id"),
        items="checks",
    ),
    Row(
        Button(
            Format("{prev_button_text}"),
            id=STOREFRONT_CHECKS_PREV_BUTTON_ID,
            on_click=checks_prev_page,
            when="show_prev_page",
            style=Style(emoji_id=LEFT_CIRCLE_2_EMOJI_ID),
        ),
        Button(
            Format("{page_button_text}"),
            id=STOREFRONT_CHECKS_PAGE_BUTTON_ID,
            on_click=show_checks_page_info,
            when="show_page_info",
        ),
        Button(
            Format("{next_button_text}"),
            id=STOREFRONT_CHECKS_NEXT_BUTTON_ID,
            on_click=checks_next_page,
            when="show_next_page",
            style=Style(emoji_id=RIGHT_CIRCLE_2_EMOJI_ID),
        ),
    ),
    Button(
        Format("{create_stars_text}"),
        id=STOREFRONT_CREATE_STARS_CHECK_BUTTON_ID,
        on_click=show_checks_create_stars,
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=PLUS_EMOJI_ID),
    ),
    SwitchInlineQueryChosenChatButton(
        Format("{create_from_chat_text}"),
        Format("{create_from_chat_query}"),
        id=STOREFRONT_CHECK_CREATE_FROM_CHAT_ID,
        allow_user_chats=True,
        allow_group_chats=True,
        allow_channel_chats=True,
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=RECEIPT_EMOJI_ID),
    ),
    Button(
        Format("{history_button_text}"),
        id=STOREFRONT_CHECKS_HISTORY_OPEN_BUTTON_ID,
        on_click=show_checks_history,
        style=Style(emoji_id=DOCUMENT_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_OPEN_PROFILE_BUTTON_ID,
        on_click=show_profile,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.checks_list,
    getter=checks_list_getter,
)

checks_history_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    ListGroup(
        Button(
            Format("{item[button_text]}"),
            id=STOREFRONT_CHECKS_HISTORY_SELECT_ID,
            on_click=open_check_history,
        ),
        id="chl",
        item_id_getter=itemgetter("id"),
        items="checks",
    ),
    Row(
        Button(
            Format("{prev_button_text}"),
            id=STOREFRONT_CHECKS_HISTORY_PREV_BUTTON_ID,
            on_click=checks_history_prev_page,
            when="show_prev_page",
            style=Style(emoji_id=LEFT_CIRCLE_2_EMOJI_ID),
        ),
        Button(
            Format("{page_button_text}"),
            id=STOREFRONT_CHECKS_HISTORY_PAGE_BUTTON_ID,
            on_click=show_checks_history_page_info,
            when="show_page_info",
        ),
        Button(
            Format("{next_button_text}"),
            id=STOREFRONT_CHECKS_HISTORY_NEXT_BUTTON_ID,
            on_click=checks_history_next_page,
            when="show_next_page",
            style=Style(emoji_id=RIGHT_CIRCLE_2_EMOJI_ID),
        ),
    ),
    Button(
        Format("{back_to_checks_text}"),
        id=STOREFRONT_CHECKS_HISTORY_BACK_TO_LIST_BUTTON_ID,
        on_click=show_checks_current,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_OPEN_PROFILE_BUTTON_ID,
        on_click=show_profile,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.checks_history,
    getter=checks_history_getter,
)

checks_details_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    SwitchInlineQueryChosenChatButton(
        Format("{share_text}"),
        Format("{share_query}"),
        id=STOREFRONT_CHECK_SHARE_URL_ID,
        allow_user_chats=True,
        allow_group_chats=True,
        allow_channel_chats=True,
        when="show_actions",
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=SHARE_EMOJI_ID),
    ),
    Button(
        Format("{settings_text}"),
        id=STOREFRONT_CHECK_SETTINGS_BUTTON_ID,
        on_click=show_checks_settings,
        when="show_actions",
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=SETTINGS_EMOJI_ID),
    ),
    Button(
        Format("{close_text}"),
        id=STOREFRONT_CHECK_CLOSE_BUTTON_ID,
        on_click=close_selected_check,
        when="show_actions",
        style=Style(style=ButtonStyle.DANGER, emoji_id=CLOSE_EMOJI_ID),
    ),
    Button(
        Format("{back_to_list_text}"),
        id=STOREFRONT_CHECK_BACK_TO_LIST_BUTTON_ID,
        on_click=show_checks_current,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_OPEN_PROFILE_BUTTON_ID,
        on_click=show_profile,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.checks_details,
    getter=checks_details_getter,
)

checks_create_stars_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    MessageInput(handle_check_stars_input),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_CHECK_BACK_TO_LIST_BUTTON_ID,
        on_click=show_checks_current,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.checks_create_stars,
    getter=checks_create_stars_getter,
)

checks_create_recipient_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    MessageInput(handle_check_claim_recipient_input),
    Button(
        Format("{skip_button_text}"),
        id=STOREFRONT_CHECK_CREATE_SKIP_RECIPIENT_ID,
        on_click=skip_check_claim_recipient,
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=CHECK_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_CHECK_BACK_TO_LIST_BUTTON_ID,
        on_click=show_checks_create_stars,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.checks_create_recipient,
    getter=checks_create_recipient_getter,
)

checks_create_password_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    MessageInput(handle_check_claim_password_input),
    Button(
        Format("{skip_button_text}"),
        id=STOREFRONT_CHECK_CREATE_SKIP_PASSWORD_ID,
        on_click=skip_check_claim_password,
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=CHECK_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_CHECK_BACK_TO_LIST_BUTTON_ID,
        on_click=show_checks_create_recipient,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.checks_create_password,
    getter=checks_create_password_getter,
)

checks_create_confirm_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    Button(
        Format("{confirm_text}"),
        id=STOREFRONT_CHECK_CREATE_CONFIRM_ID,
        on_click=confirm_check_create,
        when="can_confirm",
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=CHECK_EMOJI_ID),
    ),
    Row(
        Button(
            Format("{change_amount_text}"),
            id=STOREFRONT_CHECK_CREATE_CHANGE_AMOUNT_ID,
            on_click=show_checks_create_stars,
            style=Style(emoji_id=EDIT_2_EMOJI_ID),
        ),
        Button(
            Format("{change_recipient_text}"),
            id=STOREFRONT_CHECK_CREATE_CHANGE_RECIPIENT_ID,
            on_click=show_checks_create_recipient,
            style=Style(emoji_id=EDIT_2_EMOJI_ID),
        ),
    ),
    Button(
        Format("{change_password_text}"),
        id=STOREFRONT_CHECK_CREATE_CHANGE_PASSWORD_ID,
        on_click=show_checks_create_password,
        style=Style(emoji_id=EDIT_2_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_CHECK_BACK_TO_LIST_BUTTON_ID,
        on_click=show_checks_current,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.checks_create_confirm,
    getter=checks_create_confirm_getter,
)

checks_settings_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    Button(
        Format("{edit_recipient_text}"),
        id=STOREFRONT_CHECK_SETTINGS_EDIT_RECIPIENT_ID,
        on_click=show_checks_edit_recipient,
        when="show_actions",
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=EDIT_2_EMOJI_ID),
    ),
    Button(
        Format("{edit_password_text}"),
        id=STOREFRONT_CHECK_SETTINGS_EDIT_PASSWORD_ID,
        on_click=show_checks_edit_password,
        when="show_actions",
        style=Style(style=ButtonStyle.PRIMARY, emoji_id=EDIT_2_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_CHECK_SETTINGS_BACK_ID,
        on_click=show_checks_details_current,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.checks_settings,
    getter=checks_settings_getter,
)

checks_edit_recipient_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    MessageInput(handle_check_edit_recipient_input),
    Button(
        Format("{clear_button_text}"),
        id=STOREFRONT_CHECK_SETTINGS_CLEAR_RECIPIENT_ID,
        on_click=clear_selected_check_recipient,
        style=Style(style=ButtonStyle.DANGER, emoji_id=CLOSE_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_CHECKS_EDIT_BACK_ID,
        on_click=show_checks_settings,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.checks_edit_recipient,
    getter=checks_edit_recipient_getter,
)

checks_edit_password_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    MessageInput(handle_check_edit_password_input),
    Button(
        Format("{clear_button_text}"),
        id=STOREFRONT_CHECK_SETTINGS_CLEAR_PASSWORD_ID,
        on_click=clear_selected_check_password,
        style=Style(style=ButtonStyle.DANGER, emoji_id=CLOSE_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_CHECKS_EDIT_BACK_ID,
        on_click=show_checks_settings,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.checks_edit_password,
    getter=checks_edit_password_getter,
)

checks_claim_password_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    MessageInput(handle_check_activation_password_input),
    Button(
        Format("{cancel_button_text}"),
        id=STOREFRONT_CHECK_CLAIM_PASSWORD_CANCEL_ID,
        on_click=show_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.checks_claim_password,
    getter=checks_claim_password_getter,
)

checks_history_details_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    Button(
        Format("{back_to_history_text}"),
        id=STOREFRONT_CHECKS_HISTORY_BACK_TO_LIST_BUTTON_ID,
        on_click=show_checks_history_list,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_OPEN_PROFILE_BUTTON_ID,
        on_click=show_profile,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.checks_history_details,
    getter=checks_history_details_getter,
)
