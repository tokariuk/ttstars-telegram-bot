from __future__ import annotations

from app.utils.localization import (
    SUPPORTED_I18N_LOCALES,
)
from app.utils.localization import (
    normalize_i18n_locale as _normalize_i18n_locale,
)


def normalize_i18n_locale(value: str | None, *, fallback: str = "en") -> str:
    return _normalize_i18n_locale(
        value,
        fallback=fallback,
        supported_locales=SUPPORTED_I18N_LOCALES,
    )
