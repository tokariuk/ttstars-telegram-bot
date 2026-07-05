from __future__ import annotations

from typing import Any, Optional

from app.models.base import PydanticModel


class ErrorBody(PydanticModel):
    code: str
    message: str
    details: Optional[dict[str, Any]] = None


class ErrorResponse(PydanticModel):
    """Unified error envelope returned by every Mini App endpoint."""

    error: ErrorBody


class OkResponse(PydanticModel):
    ok: bool = True
