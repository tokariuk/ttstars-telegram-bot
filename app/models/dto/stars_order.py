from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.enums.stars_order import StarsOrderProductType, StarsOrderStatus, StarsPaymentProvider
from app.models.base import ActiveRecordModel


class StarsOrderDto(ActiveRecordModel):
    id: int
    user_id: int
    recipient_username: str
    stars_count: int
    product_type: StarsOrderProductType
    premium_months: Optional[int] = None
    recipient_user_id: Optional[int] = None
    gift_id: Optional[str] = None
    gift_message: Optional[str] = None
    gift_sender_private: Optional[bool] = None
    amount_cents: int
    payment_provider: StarsPaymentProvider
    payment_currency: str
    status: StarsOrderStatus
    payment_payload: Optional[str] = None
    provider_invoice_id: Optional[int] = None
    provider_reference: Optional[str] = None
    provider_amount_minor: Optional[int] = None
    provider_status: Optional[str] = None
    checkout_url: Optional[str] = None
    checkout_message_id: Optional[int] = None
    funding_topup_id: Optional[int] = None
    funding_provider: Optional[StarsPaymentProvider] = None
    fragment_tx_hash: Optional[str] = None
    fragment_error: Optional[str] = None
    referral_reward_total_cents: int = 0
    referral_reward_level1_cents: int = 0
    referral_reward_level2_cents: int = 0
    referral_reward_level3_cents: int = 0
    referral_processed_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    fulfilled_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @property
    def is_open(self) -> bool:
        return self.status in {
            StarsOrderStatus.CREATING_PAYMENT,
            StarsOrderStatus.PENDING_PAYMENT,
            StarsOrderStatus.PAYMENT_CONFIRMED,
            StarsOrderStatus.FULFILLING,
        }
