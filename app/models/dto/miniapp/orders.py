from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from app.enums.stars_order import StarsOrderProductType, StarsOrderStatus, StarsPaymentProvider
from app.models.base import PydanticModel


class OrderResponse(PydanticModel):
    id: int
    product_type: StarsOrderProductType
    status: StarsOrderStatus
    is_open: bool
    recipient_username: str
    stars_count: int
    premium_months: Optional[int] = None
    amount_cents: int
    amount_usd: str
    payment_provider: StarsPaymentProvider
    payment_currency: str
    checkout_total_cents: int
    checkout_total_usd: str
    checkout_fee_percent: str
    checkout_url: Optional[str] = None
    provider_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None
    fulfilled_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None


class OrdersPageResponse(PydanticModel):
    items: list[OrderResponse]
    page: int
    page_size: int
    total_pages: int
    has_next: bool


class CreateStarsOrderRequest(PydanticModel):
    provider: StarsPaymentProvider
    recipient_username: str = Field(min_length=5, max_length=64)
    stars_count: int = Field(ge=1)


class CreatePremiumOrderRequest(PydanticModel):
    provider: StarsPaymentProvider
    recipient_username: str = Field(min_length=5, max_length=64)
    months: int = Field(ge=1)


class CreateTopupOrderRequest(PydanticModel):
    provider: StarsPaymentProvider
    amount_usd: str = Field(min_length=1, max_length=32)


class QuoteRequest(PydanticModel):
    product_type: StarsOrderProductType
    provider: StarsPaymentProvider
    stars_count: Optional[int] = Field(default=None, ge=1)
    months: Optional[int] = Field(default=None, ge=1)
    amount_usd: Optional[str] = Field(default=None, max_length=32)


class QuoteResponse(PydanticModel):
    product_type: StarsOrderProductType
    provider: StarsPaymentProvider
    currency: str
    net_amount_cents: int
    net_amount_usd: str
    checkout_total_cents: int
    checkout_total_usd: str
    fee_percent: str
    fee_display: str


class PaymentCheckResponse(PydanticModel):
    outcome: str
    provider_status: Optional[str] = None
    order: Optional[OrderResponse] = None


class RecipientValidateRequest(PydanticModel):
    username: str = Field(min_length=1, max_length=64)


class RecipientValidateResponse(PydanticModel):
    valid: bool
    normalized: Optional[str] = None
