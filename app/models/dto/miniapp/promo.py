from __future__ import annotations

from pydantic import Field

from app.models.base import PydanticModel

from .user import UserResponse


class PromoActivateRequest(PydanticModel):
    code: str = Field(min_length=1, max_length=64)


class PromoActivateResponse(PydanticModel):
    activated_amount_cents: int
    activated_amount_usd: str
    user: UserResponse
