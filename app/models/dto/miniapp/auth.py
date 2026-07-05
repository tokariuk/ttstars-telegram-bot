from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from app.models.base import PydanticModel

from .user import UserResponse


class TelegramAuthRequest(PydanticModel):
    """Telegram WebApp ``initData`` string captured inside the Mini App."""

    init_data: str = Field(min_length=1, max_length=8192)


class BrowserAuthRequest(PydanticModel):
    """Telegram Login Widget payload (browser fallback outside Telegram)."""

    id: int = Field(gt=0)
    first_name: str = Field(min_length=1, max_length=255)
    last_name: Optional[str] = Field(default=None, max_length=255)
    username: Optional[str] = Field(default=None, max_length=255)
    photo_url: Optional[str] = Field(default=None, max_length=2048)
    language_code: Optional[str] = Field(default=None, max_length=16)
    auth_date: int = Field(gt=0)
    hash: str = Field(min_length=1, max_length=128)


class AuthConfigResponse(PydanticModel):
    bot_username: str


class AuthResponse(PydanticModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    expires_at: datetime
    user: UserResponse


class SessionResponse(PydanticModel):
    user: UserResponse
    expires_at: datetime
