from __future__ import annotations

from typing import Any


def extract_optional_string(value: Any) -> str | None:
    """Normalize a provider-response value into a non-empty string, or None.

    Strings are stripped (an empty result becomes None); integers are
    stringified; any other type yields None. Shared by the payment services
    so they parse provider API payloads identically.
    """
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    if isinstance(value, int):
        return str(value)
    return None
