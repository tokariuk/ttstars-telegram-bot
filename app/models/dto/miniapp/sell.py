from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from app.enums.stars_sell_order import (
    StarsSellOrderResolutionReason,
    StarsSellOrderStatus,
    StarsSellPayoutMethod,
)
from app.models.base import PydanticModel


class SellConfigResponse(PydanticModel):
    """Terms for selling Stars back to the service."""

    min_stars: int
    max_stars: int
    hold_days: int
    usd_per_star: str
    payout_methods: list[StarsSellPayoutMethod]


class SellQuoteRequest(PydanticModel):
    stars_count: int = Field(ge=1)


class SellQuoteResponse(PydanticModel):
    stars_count: int
    payout_amount_cents: int
    payout_amount_usd: str
    invoice_total_amount: int
    hold_days: int


class CreateSellOrderRequest(PydanticModel):
    stars_count: int = Field(ge=1)
    payout_wallet: str = Field(min_length=4, max_length=128)
    payout_method: StarsSellPayoutMethod = StarsSellPayoutMethod.TON_USDT


class SellOrderResponse(PydanticModel):
    id: int
    stars_count: int
    payout_method: StarsSellPayoutMethod
    payout_wallet: str
    payout_amount_cents: int
    payout_amount_usd: str
    invoice_total_amount: int
    status: StarsSellOrderStatus
    failure_reason: Optional[str] = None
    resolution_reason: Optional[StarsSellOrderResolutionReason] = None
    resolution_note: Optional[str] = None
    paid_stars_amount: Optional[int] = None
    invoice_link: Optional[str] = None
    paid_at: Optional[datetime] = None
    payout_available_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class SellOrdersPageResponse(PydanticModel):
    items: list[SellOrderResponse]
    page: int
    page_size: int
    total_pages: int
    has_next: bool
