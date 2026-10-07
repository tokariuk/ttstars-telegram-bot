from __future__ import annotations

from collections.abc import MutableMapping


def read_non_negative_int(data: MutableMapping[str, object], key: str) -> int:
    raw = data.get(key)
    if isinstance(raw, int):
        return max(raw, 0)
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    return 0


def read_optional_int(data: MutableMapping[str, object], key: str) -> int | None:
    raw = data.get(key)
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    return None


def read_positive_int(data: MutableMapping[str, object], key: str) -> int | None:
    value = read_optional_int(data, key)
    if value is None or value <= 0:
        return None
    return value


def read_stripped_string(data: MutableMapping[str, object], key: str) -> str | None:
    raw = data.get(key)
    if not isinstance(raw, str):
        return None
    value = raw.strip()
    return value or None


def set_optional_int(
    data: MutableMapping[str, object],
    key: str,
    value: int | None,
) -> None:
    if value is None:
        data.pop(key, None)
        return
    data[key] = value


def set_positive_int(
    data: MutableMapping[str, object],
    key: str,
    value: int | None,
) -> None:
    if value is None:
        data.pop(key, None)
        return
    normalized = int(value)
    if normalized <= 0:
        data.pop(key, None)
        return
    data[key] = normalized


def set_stripped_string(
    data: MutableMapping[str, object],
    key: str,
    value: str | None,
) -> None:
    normalized = value.strip() if value is not None else ""
    if not normalized:
        data.pop(key, None)
        return
    data[key] = normalized


def clear_state_keys(data: MutableMapping[str, object], *keys: str) -> None:
    for key in keys:
        data.pop(key, None)
