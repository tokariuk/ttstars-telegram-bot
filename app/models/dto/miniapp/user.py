from __future__ import annotations

from typing import Optional

from app.models.base import PydanticModel


class UserResponse(PydanticModel):
    id: int
    name: str
    language: str
    language_code: Optional[str] = None
    balance_cents: int
    balance_usd: str
    referral_balance_cents: int
    referral_balance_usd: str
    referral_earned_cents: int
    referral_earned_usd: str
    referrer_id: Optional[int] = None
    bot_blocked: bool


class ProfileStatsResponse(PydanticModel):
    total_stars_purchased: int
    total_premiums_purchased: int
    total_stars_amount_cents: int
    total_stars_amount_usd: str
    total_premiums_amount_cents: int
    total_premiums_amount_usd: str


class MeResponse(PydanticModel):
    user: UserResponse
    stats: ProfileStatsResponse
