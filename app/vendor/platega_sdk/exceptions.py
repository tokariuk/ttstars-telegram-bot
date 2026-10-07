"""
Platega SDK Exceptions
"""

from typing import Any


class PlategaException(Exception):
    """Base exception for Platega SDK"""

    pass


class PlategaAPIError(PlategaException):
    """Exception raised when Platega API returns an error"""

    def __init__(
        self,
        message: str,
        http_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.http_code = http_code
        self.response_data = response_data or {}

    def __str__(self) -> str:
        if self.http_code:
            return f"[HTTP {self.http_code}] {self.args[0]}"
        return str(self.args[0])


class PlategaValidationError(PlategaException):
    """Exception raised when callback validation fails"""

    pass
