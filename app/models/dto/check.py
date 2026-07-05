from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.enums.check import CheckStatus
from app.models.base import ActiveRecordModel


class CheckDto(ActiveRecordModel):
    id: int
    code: str
    creator_id: int
    stars_count: int
    amount_cents: int
    status: CheckStatus
    claim_username: Optional[str] = None
    claim_password_hash: Optional[str] = None
    recipient_id: Optional[int] = None
    inline_message_id: Optional[str] = None
    provider_tx_hash: Optional[str] = None
    last_error: Optional[str] = None
    redeemed_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
