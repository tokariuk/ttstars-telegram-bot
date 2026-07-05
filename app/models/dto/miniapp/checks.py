from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from app.enums.check import CheckStatus
from app.models.base import PydanticModel


class CheckResponse(PydanticModel):
    id: int
    code: str
    creator_id: int
    stars_count: int
    amount_cents: int
    amount_usd: str
    status: CheckStatus
    claim_username: Optional[str] = None
    has_password: bool = False
    recipient_id: Optional[int] = None
    link: str
    last_error: Optional[str] = None
    redeemed_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ChecksPageResponse(PydanticModel):
    items: list[CheckResponse]
    page: int
    page_size: int
    total_pages: int
    has_next: bool


class CreateCheckRequest(PydanticModel):
    stars_count: int = Field(ge=1)
    claim_username: Optional[str] = Field(default=None, max_length=64)
    claim_password: Optional[str] = Field(default=None, max_length=64)


class UpdateCheckRequest(PydanticModel):
    # ``None`` clears the restriction; omit the field to leave it unchanged.
    claim_username: Optional[str] = Field(default=None, max_length=64)
    claim_password: Optional[str] = Field(default=None, max_length=64)
    update_username: bool = False
    update_password: bool = False
