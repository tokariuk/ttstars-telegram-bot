from __future__ import annotations

import asyncio
from decimal import Decimal

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from app.enums.stars_order import StarsOrderProductType, StarsPaymentProvider
from app.models.dto.metrics import (
    LolzForumMetricsResponse,
    OrdersStatsResponse,
    PaymentFeesResponse,
    PremiumPlanPricing,
    PremiumPricingResponse,
    ProductStatsResponse,
    ProviderFeesResponse,
    StarPricingResponse,
    StorefrontStatsResponse,
    UsersStatsResponse,
)
from app.services.crud import StarsOrderService, UserService
from app.stars import (
    MAX_STARS_COUNT,
    MIN_STARS_COUNT,
    STARS_MARKUP_PERCENT,
    build_stars_pack,
    current_star_price_usd,
    get_premium_pack,
    premium_months_options,
    price_usd_for_cents,
)

router: APIRouter = APIRouter(prefix="/api/metrics", tags=["metrics"])

_PROVIDER_DISPLAY_NAMES: dict[StarsPaymentProvider, str] = {
    StarsPaymentProvider.CRYPTO_BOT: "CryptoBot",
    StarsPaymentProvider.TON_PAY: "TON",
    StarsPaymentProvider.XROCKET_PAY: "xRocket",
    StarsPaymentProvider.HELEKET_PAY: "Heleket",
    StarsPaymentProvider.LZT_PAY: "LZT Pay",
    StarsPaymentProvider.NICE_PAY_RU: "NicePay RU",
    StarsPaymentProvider.NICE_PAY_KZ: "NicePay KZ",
    StarsPaymentProvider.PLATEGA_PAY: "Platega",
    StarsPaymentProvider.BALANCE: "Balance",
}


def _format_decimal(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text if text else "0"


def _provider_display_name(provider: StarsPaymentProvider) -> str:
    return _PROVIDER_DISPLAY_NAMES.get(provider, provider.value)


def _build_lolz_forum_metrics(stars_order_service: StarsOrderService) -> LolzForumMetricsResponse:
    premium_3 = get_premium_pack(months=3).price_usd
    premium_6 = get_premium_pack(months=6).price_usd
    premium_12 = get_premium_pack(months=12).price_usd
    stars_price = current_star_price_usd()

    providers = (
        StarsPaymentProvider.CRYPTO_BOT,
        StarsPaymentProvider.TON_PAY,
        StarsPaymentProvider.XROCKET_PAY,
        StarsPaymentProvider.HELEKET_PAY,
        StarsPaymentProvider.LZT_PAY,
        StarsPaymentProvider.NICE_PAY_RU,
        StarsPaymentProvider.NICE_PAY_KZ,
        StarsPaymentProvider.PLATEGA_PAY,
    )
    configured_providers = [
        provider
        for provider in providers
        if stars_order_service.provider_configured(provider=provider)
    ]
    fees_compact = " | ".join(
        [
            (
                f"{_provider_display_name(provider)} "
                f"{stars_order_service.provider_payment_fee_percent_text(provider=provider)}%"
            )
            for provider in configured_providers
        ]
    )
    if not fees_compact:
        fees_compact = "not configured"

    stars_line_plain = f"Stars price: {stars_price} USD"
    premium_line_plain = (
        f"Premium prices: 3m {premium_3} USD | 6m {premium_6} USD | 12m {premium_12} USD"
    )
    fees_line_plain = f"Payment fees: {fees_compact}"

    return LolzForumMetricsResponse(
        stars_price_usd=stars_price,
        premium_3m_price_usd=premium_3,
        premium_6m_price_usd=premium_6,
        premium_12m_price_usd=premium_12,
        fees_compact=fees_compact,
        stars_line_plain=stars_line_plain,
        premium_line_plain=premium_line_plain,
        fees_line_plain=fees_line_plain,
        line_plain=(f"{stars_line_plain} ; {premium_line_plain} ; {fees_line_plain}"),
        block_plain=(f"{stars_line_plain}\n{premium_line_plain}\n{fees_line_plain}"),
    )


@router.get("/pricing/star")
async def get_star_price() -> StarPricingResponse:
    return StarPricingResponse(
        star_price_usd=current_star_price_usd(),
        markup_percent=_format_decimal(STARS_MARKUP_PERCENT),
        min_stars=MIN_STARS_COUNT,
        max_stars=MAX_STARS_COUNT,
    )


@router.get("/pricing/premium")
async def get_premium_prices() -> PremiumPricingResponse:
    plans = [
        PremiumPlanPricing(
            months=months,
            price_usd=get_premium_pack(months=months).price_usd,
            price_cents=get_premium_pack(months=months).price_cents,
        )
        for months in premium_months_options()
    ]
    return PremiumPricingResponse(plans=plans)


@router.get("/fees")
async def get_payment_fees(request: Request) -> PaymentFeesResponse:
    stars_order_service: StarsOrderService = request.app.state.stars_order_service
    stars_50_cents = build_stars_pack(stars_count=50).price_cents
    premium_3_cents = get_premium_pack(months=3).price_cents
    premium_6_cents = get_premium_pack(months=6).price_cents
    premium_12_cents = get_premium_pack(months=12).price_cents
    topup_10usd_cents = 1000
    providers = (
        StarsPaymentProvider.CRYPTO_BOT,
        StarsPaymentProvider.TON_PAY,
        StarsPaymentProvider.XROCKET_PAY,
        StarsPaymentProvider.HELEKET_PAY,
        StarsPaymentProvider.LZT_PAY,
        StarsPaymentProvider.NICE_PAY_RU,
        StarsPaymentProvider.NICE_PAY_KZ,
        StarsPaymentProvider.PLATEGA_PAY,
        StarsPaymentProvider.BALANCE,
    )

    return PaymentFeesResponse(
        providers=[
            ProviderFeesResponse(
                provider=provider.value,
                currency=stars_order_service.provider_currency(provider=provider),
                configured=stars_order_service.provider_configured(provider=provider),
                payment_fee_percent=stars_order_service.provider_payment_fee_percent_text(
                    provider=provider
                ),
                payout_fee_percent=stars_order_service.provider_payout_fee_percent_text(
                    provider=provider
                ),
                payout_fixed_usd=stars_order_service.provider_payout_fixed_usd(provider=provider),
                effective_fee_stars_50_percent=stars_order_service.provider_checkout_fee_percent_text(
                    provider=provider,
                    net_amount_cents=stars_50_cents,
                ),
                effective_fee_premium_3m_percent=stars_order_service.provider_checkout_fee_percent_text(
                    provider=provider,
                    net_amount_cents=premium_3_cents,
                ),
                effective_fee_premium_6m_percent=stars_order_service.provider_checkout_fee_percent_text(
                    provider=provider,
                    net_amount_cents=premium_6_cents,
                ),
                effective_fee_premium_12m_percent=stars_order_service.provider_checkout_fee_percent_text(
                    provider=provider,
                    net_amount_cents=premium_12_cents,
                ),
                effective_fee_topup_10usd_percent=stars_order_service.provider_checkout_fee_percent_text(
                    provider=provider,
                    net_amount_cents=topup_10usd_cents,
                ),
            )
            for provider in providers
        ]
    )


@router.get("/stats")
async def get_storefront_stats(request: Request) -> StorefrontStatsResponse:
    stars_order_service: StarsOrderService = request.app.state.stars_order_service
    user_service: UserService = request.app.state.user_service

    (
        total_users,
        active_users,
        users_with_positive_balance,
        total_balance_cents,
        orders_stats,
    ) = await asyncio.gather(
        user_service.count(),
        user_service.count_active(),
        user_service.count_with_positive_balance(),
        user_service.sum_balances_cents(),
        stars_order_service.admin_stats(),
    )

    completed_products = {
        product_type.value: ProductStatsResponse(
            count=stats.count,
            amount_cents=stats.amount_cents,
            amount_usd=price_usd_for_cents(stats.amount_cents),
            stars_count=stats.stars_count,
        )
        for product_type, stats in orders_stats.completed_products.items()
    }

    premium_stats = orders_stats.completed_products.get(StarsOrderProductType.PREMIUM)
    topup_stats = orders_stats.completed_products.get(StarsOrderProductType.TOPUP)

    return StorefrontStatsResponse(
        users=UsersStatsResponse(
            total_users=total_users,
            active_users=active_users,
            users_with_positive_balance=users_with_positive_balance,
            total_balance_cents=total_balance_cents,
            total_balance_usd=price_usd_for_cents(total_balance_cents),
        ),
        orders=OrdersStatsResponse(
            total_orders=orders_stats.total_orders,
            created_last_24h=orders_stats.created_last_24h,
            created_last_7d=orders_stats.created_last_7d,
            paid_last_24h=orders_stats.paid_last_24h,
            paid_last_7d=orders_stats.paid_last_7d,
            paid_amount_last_24h_cents=orders_stats.paid_amount_last_24h_cents,
            paid_amount_last_24h_usd=price_usd_for_cents(orders_stats.paid_amount_last_24h_cents),
            paid_amount_last_7d_cents=orders_stats.paid_amount_last_7d_cents,
            paid_amount_last_7d_usd=price_usd_for_cents(orders_stats.paid_amount_last_7d_cents),
            completed_amount_cents=orders_stats.completed_amount_cents,
            completed_amount_usd=price_usd_for_cents(orders_stats.completed_amount_cents),
            completed_stars_count=orders_stats.completed_stars_count,
            completed_premiums_count=premium_stats.count if premium_stats is not None else 0,
            completed_topups_count=topup_stats.count if topup_stats is not None else 0,
            status_counts={
                status.value: count for status, count in orders_stats.status_counts.items()
            },
            completed_products=completed_products,
        ),
    )


@router.get("/forum/lolz")
async def get_lolz_forum_metrics(request: Request) -> LolzForumMetricsResponse:
    stars_order_service: StarsOrderService = request.app.state.stars_order_service
    return _build_lolz_forum_metrics(stars_order_service=stars_order_service)


@router.get("/forum/lolz/stars", response_class=PlainTextResponse)
async def get_lolz_forum_stars_line(request: Request) -> PlainTextResponse:
    stars_order_service: StarsOrderService = request.app.state.stars_order_service
    response = _build_lolz_forum_metrics(stars_order_service=stars_order_service)
    return PlainTextResponse(content=response.stars_line_plain)


@router.get("/forum/lolz/premium", response_class=PlainTextResponse)
async def get_lolz_forum_premium_line(request: Request) -> PlainTextResponse:
    stars_order_service: StarsOrderService = request.app.state.stars_order_service
    response = _build_lolz_forum_metrics(stars_order_service=stars_order_service)
    return PlainTextResponse(content=response.premium_line_plain)


@router.get("/forum/lolz/fees", response_class=PlainTextResponse)
async def get_lolz_forum_fees_line(request: Request) -> PlainTextResponse:
    stars_order_service: StarsOrderService = request.app.state.stars_order_service
    response = _build_lolz_forum_metrics(stars_order_service=stars_order_service)
    return PlainTextResponse(content=response.fees_line_plain)
