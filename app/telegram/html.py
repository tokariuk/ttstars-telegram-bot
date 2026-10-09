"""Small, explicit safety boundary for Telegram HTML rendering.

Values received from users, the database, or external services must pass through
``escape_text`` (or a fragment builder below) before they are interpolated into
messages rendered with Telegram's HTML parse mode.  The returned fragments from
``code`` and ``spoiler_code`` are trusted markup and must not be escaped again.
"""

from __future__ import annotations

import html
from html.parser import HTMLParser
from urllib.parse import urlsplit

DEFAULT_PLACEHOLDER = "—"
DIAGNOSTIC_TEXT_LIMIT = 120


def escape_text(value: str) -> str:
    """Escape untrusted plain text for Telegram HTML."""

    return html.escape(value, quote=True)


def escape_attribute(value: str) -> str:
    """Escape an untrusted value used inside a quoted HTML attribute."""

    return html.escape(value, quote=True)


def link(text: str, url: str) -> str:
    """Build a trusted Telegram link from untrusted label and URL values."""

    escaped_text = escape_text(text)
    if urlsplit(url).scheme.lower() not in {"http", "https", "tg"}:
        return escaped_text
    return f'<a href="{escape_attribute(url)}">{escaped_text}</a>'


def code(value: str) -> str:
    """Render untrusted plain text as a copyable code fragment."""

    return f"<code>{escape_text(value)}</code>"


def spoiler_code(value: str | None, *, placeholder: str = DEFAULT_PLACEHOLDER) -> str:
    """Render an optional identifier as copyable, visually compact markup."""

    if value is None:
        return placeholder
    normalized = value.strip()
    if not normalized or normalized == placeholder:
        return placeholder
    return f"<code><tg-spoiler>{escape_text(normalized)}</tg-spoiler></code>"


def username(value: str | None, *, placeholder: str = DEFAULT_PLACEHOLDER) -> str:
    """Render an optional Telegram username as escaped plain text."""

    if value is None:
        return placeholder
    normalized = value.strip().lstrip("@").strip()
    return f"@{escape_text(normalized)}" if normalized else placeholder


def truncate_plain_text(value: str, *, max_length: int, suffix: str = "…") -> str:
    """Truncate plain text to a maximum character count, including the suffix."""

    if max_length < 0:
        raise ValueError("max_length must not be negative")
    if len(value) <= max_length:
        return value
    if max_length == 0:
        return ""
    if len(suffix) >= max_length:
        return suffix[:max_length]
    return f"{value[: max_length - len(suffix)]}{suffix}"


def safe_diagnostic(
    value: str | None,
    *,
    max_length: int = DIAGNOSTIC_TEXT_LIMIT,
    placeholder: str = DEFAULT_PLACEHOLDER,
) -> str:
    """Render bounded external diagnostics as escaped plain text."""

    if value is None:
        return placeholder
    normalized = value.strip()
    if not normalized:
        return placeholder
    return escape_text(truncate_plain_text(normalized, max_length=max_length))


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def visible_text_length(value: str) -> int:
    """Count the text Telegram displays after supported HTML is parsed."""

    parser = _VisibleTextParser()
    parser.feed(value)
    parser.close()
    return len("".join(parser.parts))


__all__ = [
    "code",
    "DIAGNOSTIC_TEXT_LIMIT",
    "escape_attribute",
    "escape_text",
    "link",
    "safe_diagnostic",
    "spoiler_code",
    "truncate_plain_text",
    "username",
    "visible_text_length",
]
