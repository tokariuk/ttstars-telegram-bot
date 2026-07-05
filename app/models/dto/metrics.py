from __future__ import annotations

from app.models.base import PydanticModel


class StarPricingResponse(PydanticModel):
    star_price_usd: str
    markup_percent: str
    min_stars: int
    max_stars: int


class PremiumPlanPricing(PydanticModel):
    months: int
    price_usd: str
    price_cents: int


class PremiumPricingResponse(PydanticModel):
    plans: list[PremiumPlanPricing]


class ProviderFeesResponse(PydanticModel):
    provider: str
    currency: str
    configured: bool
    payment_fee_percent: str
    payout_fee_percent: str
    payout_fixed_usd: str
    effective_fee_stars_50_percent: str
    effective_fee_premium_3m_percent: str
    effective_fee_premium_6m_percent: str
    effective_fee_premium_12m_percent: str
    effective_fee_topup_10usd_percent: str


class PaymentFeesResponse(PydanticModel):
    providers: list[ProviderFeesResponse]


class ProductStatsResponse(PydanticModel):
    count: int
    amount_cents: int
    amount_usd: str
    stars_count: int


class UsersStatsResponse(PydanticModel):
    total_users: int
    active_users: int
    users_with_positive_balance: int
    total_balance_cents: int
    total_balance_usd: str


class OrdersStatsResponse(PydanticModel):
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
    completed_premiums_count: int
    completed_topups_count: int
    status_counts: dict[str, int]
    completed_products: dict[str, ProductStatsResponse]


class StorefrontStatsResponse(PydanticModel):
    users: UsersStatsResponse
    orders: OrdersStatsResponse


class LolzForumMetricsResponse(PydanticModel):
    stars_price_usd: str
    premium_3m_price_usd: str
    premium_6m_price_usd: str
    premium_12m_price_usd: str
    fees_compact: str
    stars_line_plain: str
    premium_line_plain: str
    fees_line_plain: str
    line_plain: str
    block_plain: str
