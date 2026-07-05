from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from app.models.base import PydanticModel

from .user import UserResponse


class ReferralMemberResponse(PydanticModel):
    user_id: int
    name: str
    level: int
    joined_at: datetime


class ReferralsResponse(PydanticModel):
    referral_link: str
    referral_balance_cents: int
    referral_balance_usd: str
    referral_earned_cents: int
    referral_earned_usd: str
    level1_count: int
    level2_count: int
    level3_count: int
    members: list[ReferralMemberResponse]


class ReferralWithdrawRequest(PydanticModel):
    amount_cents: Optional[int] = Field(default=None, ge=1)


class ReferralWithdrawResponse(PydanticModel):
    transferred_amount_cents: int
    transferred_amount_usd: str
    user: UserResponse
