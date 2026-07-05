from __future__ import annotations

import logging
from enum import StrEnum
from typing import Any, NoReturn, Optional, cast

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.services.crud.stars_order import (
    BalanceOrderInProgressError,
    InsufficientBalanceError,
    PaymentMinAmountError,
    ProviderUnavailableError,
    StarsOrderError,
)
from app.services.crud.stars_order import (
    ValidationError as OrderValidationError,
)

logger: logging.Logger = logging.getLogger(name=__name__)

_AUTH_SCHEME = "Bearer"


class ErrorCode(StrEnum):
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    VALIDATION_ERROR = "validation_error"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    INSUFFICIENT_BALANCE = "insufficient_balance"
    ORDER_IN_PROGRESS = "order_in_progress"
    PAYMENT_MIN_AMOUNT = "payment_min_amount"
    PROMO_INVALID = "promo_invalid"
    PROMO_ALREADY_USED = "promo_already_used"
    NOTHING_TO_WITHDRAW = "nothing_to_withdraw"
    DUPLICATE_REQUEST = "duplicate_request"
    PAYMENT_FAILED = "payment_failed"
    INTERNAL = "internal"


class ApiError(Exception):
    """Domain error rendered as ``{"error": {"code", "message", "details?"}}``."""

    def __init__(
        self,
        *,
        status_code: int,
        code: ErrorCode,
        message: str,
        details: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        self.headers = headers
        super().__init__(message)


def unauthorized(message: str = "Authentication is required.") -> NoReturn:
    raise ApiError(
        status_code=status.HTTP_401_UNAUTHORIZED,
        code=ErrorCode.UNAUTHORIZED,
        message=message,
        headers={"WWW-Authenticate": _AUTH_SCHEME},
    )


def forbidden(message: str = "Access to this resource is denied.") -> NoReturn:
    raise ApiError(
        status_code=status.HTTP_403_FORBIDDEN,
        code=ErrorCode.FORBIDDEN,
        message=message,
    )


def not_found(message: str = "Resource was not found.") -> NoReturn:
    raise ApiError(
        status_code=status.HTTP_404_NOT_FOUND,
        code=ErrorCode.NOT_FOUND,
        message=message,
    )


def validation_error(
    message: str,
    *,
    code: ErrorCode = ErrorCode.VALIDATION_ERROR,
    details: Optional[dict[str, Any]] = None,
) -> NoReturn:
    raise ApiError(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code=code,
        message=message,
        details=details,
    )


def conflict(message: str, *, code: ErrorCode) -> NoReturn:
    raise ApiError(status_code=status.HTTP_409_CONFLICT, code=code, message=message)


def map_service_error(error: Exception) -> NoReturn:
    """Translate a service-layer exception into an :class:`ApiError`."""

    if isinstance(error, ProviderUnavailableError):
        raise ApiError(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code=ErrorCode.PROVIDER_UNAVAILABLE,
            message=str(error),
        ) from error
    if isinstance(error, PaymentMinAmountError):
        raise ApiError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=ErrorCode.PAYMENT_MIN_AMOUNT,
            message=str(error),
            details={
                "provider": error.provider.value,
                "currency": error.currency,
                "min_amount": error.min_amount_text,
            },
        ) from error
    if isinstance(error, OrderValidationError):
        raise ApiError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=ErrorCode.VALIDATION_ERROR,
            message=str(error),
        ) from error
    if isinstance(error, InsufficientBalanceError):
        raise ApiError(
            status_code=status.HTTP_409_CONFLICT,
            code=ErrorCode.INSUFFICIENT_BALANCE,
            message=str(error),
        ) from error
    if isinstance(error, BalanceOrderInProgressError):
        raise ApiError(
            status_code=status.HTTP_409_CONFLICT,
            code=ErrorCode.ORDER_IN_PROGRESS,
            message=str(error),
        ) from error
    if isinstance(error, StarsOrderError):
        raise ApiError(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code=ErrorCode.PAYMENT_FAILED,
            message=str(error),
        ) from error
    raise error


async def _api_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    error = cast(ApiError, exc)
    body: dict[str, Any] = {"code": error.code.value, "message": error.message}
    if error.details:
        body["details"] = error.details
    return JSONResponse(
        status_code=error.status_code,
        content={"error": body},
        headers=error.headers,
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApiError, _api_error_handler)
