from __future__ import annotations

from typing import Optional

from pydantic import Field

from app.enums.stars_order import StarsPaymentProvider
from app.models.base import PydanticModel


class GiftPackResponse(PydanticModel):
    """A purchasable archived/limited Telegram gift exposed in the catalog."""

    key: str
    gift_id: str
    label: str
    price_cents: int
    price_usd: str


class CreateGiftOrderRequest(PydanticModel):
    provider: StarsPaymentProvider
    recipient_username: str = Field(min_length=5, max_length=64)
    gift_key: str = Field(min_length=1, max_length=64)
    gift_message: Optional[str] = Field(default=None, max_length=128)
    sender_private: bool = False
