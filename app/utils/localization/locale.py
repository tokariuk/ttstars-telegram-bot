from __future__ import annotations

from typing import Final, Iterable

SUPPORTED_I18N_LOCALES: Final[frozenset[str]] = frozenset({"uk", "ru", "en"})


def normalize_i18n_locale(
    value: str | None,
    *,
    fallback: str = "en",
    supported_locales: Iterable[str] = SUPPORTED_I18N_LOCALES,
) -> str:
    normalized_fallback = _normalize_locale_key(fallback)
    supported = {_normalize_locale_key(locale) for locale in supported_locales}
    if normalized_fallback not in supported:
        raise ValueError("Fallback locale must be included in supported_locales.")

    normalized = _normalize_locale_key(value)
    return normalized if normalized in supported else normalized_fallback


def _normalize_locale_key(value: str | None) -> str:
    if not isinstance(value, str):
        return ""
    locale = value.strip().lower().replace("_", "-")
    if "-" in locale:
        locale = locale.split("-", 1)[0]
    return locale

