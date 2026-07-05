from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Url, WebApp
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format

from app.telegram.dialogs.common.premium_emoji import (
    DOCUMENT_2_EMOJI_ID,
    HEADPHONES_EMOJI_ID,
    LEFT_SQUARE_EMOJI_ID,
    LOCK_EMOJI_ID,
    TELEGRAM_EMOJI_ID,
)

from ..getters import faq_getter
from ..handlers import show_menu
from ..ids import (
    STOREFRONT_BACK_TO_MENU_BUTTON_ID,
    STOREFRONT_FAQ_NEWS_URL_ID,
    STOREFRONT_FAQ_PRIVACY_WEBAPP_ID,
    STOREFRONT_FAQ_SUPPORT_URL_ID,
    STOREFRONT_FAQ_TERMS_WEBAPP_ID,
)
from ..states import StorefrontSG
from .common import banner_preview

faq_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    WebApp(
        Format("{faq_privacy_text}"),
        Format("{faq_privacy_url}"),
        id=STOREFRONT_FAQ_PRIVACY_WEBAPP_ID,
        style=Style(emoji_id=LOCK_EMOJI_ID),
    ),
    WebApp(
        Format("{faq_terms_text}"),
        Format("{faq_terms_url}"),
        id=STOREFRONT_FAQ_TERMS_WEBAPP_ID,
        style=Style(emoji_id=DOCUMENT_2_EMOJI_ID),
    ),
    Url(
        Format("{faq_support_text}"),
        Format("{faq_support_url}"),
        id=STOREFRONT_FAQ_SUPPORT_URL_ID,
        style=Style(emoji_id=HEADPHONES_EMOJI_ID),
    ),
    Url(
        Format("{faq_news_text}"),
        Format("{faq_news_url}"),
        id=STOREFRONT_FAQ_NEWS_URL_ID,
        style=Style(emoji_id=TELEGRAM_EMOJI_ID),
    ),
    Button(
        Format("{back_button_text}"),
        id=STOREFRONT_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=StorefrontSG.faq,
    getter=faq_getter,
)
