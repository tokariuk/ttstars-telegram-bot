from __future__ import annotations

from typing import Any

from aiogram_dialog import DialogManager

from app.utils.localization import normalize_i18n_locale

from .common import (
    FAQ_NEWS_URL,
    FAQ_PRIVACY_PATH,
    FAQ_SUPPORT_URL,
    FAQ_TERMS_PATH,
    banner_url,
    get_i18n,
    get_user,
    server_base_url,
)


async def faq_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    locale = normalize_i18n_locale(user.language, fallback="ru")
    base_url = server_base_url(dialog_manager=dialog_manager)
    faq_privacy_url = (
        f"{base_url}{FAQ_PRIVACY_PATH}?lang={locale}" if base_url else FAQ_PRIVACY_PATH
    )
    faq_terms_url = f"{base_url}{FAQ_TERMS_PATH}?lang={locale}" if base_url else FAQ_TERMS_PATH
    text = str(i18n.messages.faq_screen())
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "faq"),
        "faq_privacy_text": i18n.buttons.faq_privacy(),
        "faq_terms_text": i18n.buttons.faq_terms(),
        "faq_support_text": i18n.buttons.faq_support(),
        "faq_news_text": i18n.buttons.faq_news(),
        "faq_privacy_url": faq_privacy_url,
        "faq_terms_url": faq_terms_url,
        "faq_support_url": FAQ_SUPPORT_URL,
        "faq_news_url": FAQ_NEWS_URL,
        "back_button_text": i18n.buttons.back_to_menu(),
    }


__all__ = ["faq_getter"]
