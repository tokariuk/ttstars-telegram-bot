from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.enums.stars_order import StarsOrderProductType, StarsOrderStatus, StarsPaymentProvider
from app.models.base import ActiveRecordModel


class BalanceTopupDto(ActiveRecordModel):
    id: int
    user_id: int
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

    auto_product_type: Optional[StarsOrderProductType] = None
    auto_recipient_username: Optional[str] = None
    auto_stars_count: int = 0
    auto_premium_months: Optional[int] = None
    auto_recipient_user_id: Optional[int] = None
    auto_gift_id: Optional[str] = None
    auto_gift_message: Optional[str] = None
    auto_gift_sender_private: Optional[bool] = None

    linked_order_id: Optional[int] = None
    error_message: Optional[str] = None

    paid_at: Optional[datetime] = None
    credited_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
