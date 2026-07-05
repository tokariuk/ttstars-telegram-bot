from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from aiogram_dialog import DialogManager

from app.models.config import AppConfig
from app.stars import price_usd_for_cents
from app.telegram.dialogs.common import get_user

from ..handlers.shared import consume_notice

ADMIN_BANNER_KEY = Literal["stars_sell"]

ADMIN_BANNER_FILENAMES: dict[ADMIN_BANNER_KEY, dict[str, str]] = {
    "stars_sell": {
        "uk": "stars-sell.jpg",
        "ru": "stars-sell.jpg",
        "en": "stars-sell.jpg",
    }
}


def _assets_root() -> Path:
    current = Path(__file__).resolve()
    return current.parents[6] / "assets"


def _normalize_banner_locale(raw_locale: str | None) -> str:
    if not raw_locale:
        return "ru"
    value = raw_locale.strip().lower().replace("_", "-")
    language = value.split("-", 1)[0]
    return language if language in {"uk", "en", "ru"} else "ru"


@lru_cache(maxsize=64)
def _resolve_admin_banner_relative_path(*, key: ADMIN_BANNER_KEY, locale: str) -> str | None:
    assets_root = _assets_root()
    filename = ADMIN_BANNER_FILENAMES[key][locale]
    for locale_code in (locale, "ru", "uk", "en"):
        path = assets_root / "banners" / locale_code / filename
        if path.is_file():
            return f"/assets/banners/{locale_code}/{filename}"
    return None


def server_base_url(dialog_manager: DialogManager) -> str:
    raw_config = dialog_manager.middleware_data.get("config")
    if isinstance(raw_config, AppConfig):
        return raw_config.server.url.strip().rstrip("/")
    return os.getenv("SERVER_URL", "").strip().rstrip("/")


def admin_banner_url(dialog_manager: DialogManager, key: ADMIN_BANNER_KEY) -> str:
    user = get_user(dialog_manager=dialog_manager)
    locale = _normalize_banner_locale(user.language)
    relative_path = _resolve_admin_banner_relative_path(key=key, locale=locale)
    if relative_path is None:
        return ""
    base_url = server_base_url(dialog_manager=dialog_manager)
    if not base_url:
        return ""
    return f"{base_url}{relative_path}"


def with_notice(*, text: str, notice: str) -> str:
    if not notice:
        return text
    return f"{text}\n\n{notice}"


__all__ = [
    "admin_banner_url",
    "consume_notice",
    "price_usd_for_cents",
    "with_notice",
]
