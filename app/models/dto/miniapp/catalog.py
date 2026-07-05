from __future__ import annotations

from app.enums.stars_order import StarsPaymentProvider
from app.models.base import PydanticModel

from .gifts import GiftPackResponse
from .sell import SellConfigResponse


class StarsPricingResponse(PydanticModel):
    star_price_usd: str
    min_stars: int
    max_stars: int


class PremiumPlanResponse(PydanticModel):
    months: int
    price_cents: int
    price_usd: str


class PaymentProviderResponse(PydanticModel):
    provider: StarsPaymentProvider
    title: str
    currency: str
    configured: bool
    payment_fee_percent: str
    payout_fee_percent: str
    payout_fixed_usd: str
    supports_stars: bool
    supports_premium: bool
    supports_gifts: bool
    supports_topup: bool


class ReferralProgramResponse(PydanticModel):
    level1_percent: str
    level2_percent: str
    level3_percent: str


class CatalogResponse(PydanticModel):
    stars: StarsPricingResponse
    premium_plans: list[PremiumPlanResponse]
    gifts: list[GiftPackResponse]
    sell: SellConfigResponse
    payment_providers: list[PaymentProviderResponse]
    referral_program: ReferralProgramResponse
