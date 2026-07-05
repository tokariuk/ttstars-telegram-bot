from __future__ import annotations

from fastapi import FastAPI

from .errors import register_error_handlers
from .router import router

__all__ = ["register", "router"]


def register(app: FastAPI) -> None:
    """Attach the Mini App API: the ``/v1`` routes and the error envelope handler."""

    register_error_handlers(app)
    app.include_router(router)
