from typing import Any, Optional

from fluent.runtime.types import FluentType


class FluentBool(FluentType):
    def __init__(self, value: Any) -> None:
        self.value = bool(value)

    def format(self, locale: Any) -> str:
        _ = locale
        if self.value:
            return "true"
        return "false"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.format(locale=None) == other
        return False

    def __bool__(self) -> bool:
        return self.value


class FluentNullable(FluentType):
    def __init__(self, value: Optional[Any] = None) -> None:
        self.value = value

    def format(self, locale: Any) -> str:
        _ = locale
        if self.value is not None:
            return str(self.value)
        return "null"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.format(locale=None) == other
        return False
