from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import Field

from app.models.base import PydanticModel

from .checks import CheckResponse
from .orders import OrderResponse
from .sell import SellOrderResponse
from .user import ProfileStatsResponse


class AdminUserResponse(PydanticModel):
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
    blocked_at: Optional[datetime] = None


class AdminUsersPageResponse(PydanticModel):
    items: list[AdminUserResponse]
    page: int
    page_size: int
    total_pages: int
    has_next: bool


class AdminUserDetailResponse(PydanticModel):
    user: AdminUserResponse
    stats: ProfileStatsResponse


class AdminBalanceOperation(StrEnum):
    SET = "set"
    ADD = "add"
    SUBTRACT = "subtract"


class AdminBalanceRequest(PydanticModel):
    operation: AdminBalanceOperation
    amount_cents: int = Field(ge=0)


class AdminBlockRequest(PydanticModel):
    blocked: bool


class AdminOrdersPageResponse(PydanticModel):
    items: list[OrderResponse]
    page: int
    page_size: int
    total_pages: int
    has_next: bool


class AdminSellOrdersPageResponse(PydanticModel):
    items: list[SellOrderResponse]
    page: int
    page_size: int
    total_pages: int
    has_next: bool


class AdminSellResolveRequest(PydanticModel):
    note: Optional[str] = Field(default=None, max_length=1024)


class AdminSellCompleteRequest(AdminSellResolveRequest):
    allow_before_hold: bool = False


class AdminSellRejectRequest(AdminSellResolveRequest):
    reason: str = Field(min_length=1, max_length=64)


class AdminChecksPageResponse(PydanticModel):
    items: list[CheckResponse]
    page: int
    page_size: int
    total_pages: int
    has_next: bool


class AdminPromoResponse(PydanticModel):
    code: str
    amount_cents: int
    amount_usd: str
    activations: int
    max_activations: Optional[int] = None
    created_at: datetime


class AdminPromosResponse(PydanticModel):
    items: list[AdminPromoResponse]


class AdminPromoCreateRequest(PydanticModel):
    code: Optional[str] = Field(default=None, max_length=40)
    amount_usd: str = Field(min_length=1, max_length=32)
    max_activations: Optional[int] = Field(default=None, ge=1)


class AdminUserStatsResponse(PydanticModel):
    total_users: int
    active_users: int
    users_with_balance: int
    total_balance_cents: int
    total_balance_usd: str


class AdminProductStatResponse(PydanticModel):
    count: int
    amount_cents: int
    amount_usd: str
    stars_count: int


class AdminOrderStatsResponse(PydanticModel):
    total_orders: int
    created_last_24h: int
    created_last_7d: int
    paid_last_24h: int
    paid_last_7d: int
    paid_amount_last_24h_cents: int
    paid_amount_last_24h_usd: str
    paid_amount_last_7d_cents: int
    paid_amount_last_7d_usd: str
    completed_amount_cents: int
    completed_amount_usd: str
    completed_stars_count: int
    status_counts: dict[str, int]
    completed_products: dict[str, AdminProductStatResponse]


class AdminSellStatsResponse(PydanticModel):
    total_orders: int
    total_paid_stars: int
    completed_payout_cents: int
    completed_payout_usd: str
    ready_for_payout_count: int


class AdminStatsResponse(PydanticModel):
    users: AdminUserStatsResponse
    orders: AdminOrderStatsResponse
    sell: AdminSellStatsResponse
