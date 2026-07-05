from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.enums.stars_sell_order import (
    StarsSellOrderResolutionReason,
    StarsSellOrderStatus,
    StarsSellPayoutMethod,
)
from app.models.base import ActiveRecordModel


class StarsSellOrderDto(ActiveRecordModel):
    id: int
    user_id: int
    stars_count: int
    payout_method: StarsSellPayoutMethod
    payout_wallet: str
    payout_amount_cents: int
    invoice_payload: str
    invoice_message_id: Optional[int] = None
    invoice_total_amount: int
    telegram_payment_charge_id: Optional[str] = None
    provider_payment_charge_id: Optional[str] = None
    paid_stars_amount: Optional[int] = None
    status: StarsSellOrderStatus
    failure_reason: Optional[str] = None
    resolution_reason: Optional[StarsSellOrderResolutionReason] = None
    resolution_note: Optional[str] = None
    paid_at: Optional[datetime] = None
    payout_available_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
