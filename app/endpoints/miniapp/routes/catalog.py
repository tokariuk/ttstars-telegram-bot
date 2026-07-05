from __future__ import annotations

import time
from typing import cast

from fastapi import APIRouter, Request

from app.enums.stars_sell_order import StarsSellPayoutMethod
from app.gifts import list_gift_packs
from app.models.dto.miniapp import (
    CatalogResponse,
    GiftPackResponse,
    PaymentProviderResponse,
    PremiumPlanResponse,
    ReferralProgramResponse,
    SellConfigResponse,
    StarsPricingResponse,
)
from app.services.crud import StarsOrderService, StarsSellOrderService
from app.stars import (
    MAX_STARS_COUNT,
    MIN_STARS_COUNT,
    current_star_price_usd,
    get_premium_pack,
    premium_months_options,
)

from ..deps import StarsOrderServiceDep, StarsSellOrderServiceDep
from ..providers import (
    SUPPORTED_PAYMENT_PROVIDERS,
    provider_title,
    supports_gifts,
    supports_topup,
)

router = APIRouter(tags=["catalog"])

_CACHE_TTL_SECONDS = 60.0
_CACHE_ATTR = "miniapp_catalog_cache"


def _build_catalog(
    service: StarsOrderService,
    sell_service: StarsSellOrderService,
) -> CatalogResponse:
    premium_plans = [
        PremiumPlanResponse(
            months=pack.months,
            price_cents=pack.price_cents,
            price_usd=pack.price_usd,
        )
        for pack in (get_premium_pack(months=months) for months in premium_months_options())
    ]
    gifts = [
        GiftPackResponse(
            key=pack.key,
            gift_id=pack.gift_id,
            label=pack.label,
            price_cents=pack.price_cents,
            price_usd=pack.price_usd,
        )
        for pack in list_gift_packs()
    ]
    providers = [
        PaymentProviderResponse(
            provider=provider,
            title=provider_title(provider),
            currency=service.provider_currency(provider=provider),
            configured=service.provider_configured(provider=provider),
            payment_fee_percent=service.provider_payment_fee_percent_text(provider=provider),
            payout_fee_percent=service.provider_payout_fee_percent_text(provider=provider),
            payout_fixed_usd=service.provider_payout_fixed_usd(provider=provider),
            supports_stars=True,
            supports_premium=True,
            supports_gifts=supports_gifts(provider),
            supports_topup=supports_topup(provider),
        )
        for provider in SUPPORTED_PAYMENT_PROVIDERS
    ]
    level1, level2, level3 = service.referral_level_percent_texts()
    return CatalogResponse(
        stars=StarsPricingResponse(
            star_price_usd=current_star_price_usd(),
            min_stars=MIN_STARS_COUNT,
            max_stars=MAX_STARS_COUNT,
        ),
        premium_plans=premium_plans,
        gifts=gifts,
        sell=SellConfigResponse(
            min_stars=sell_service.min_stars,
            max_stars=sell_service.max_stars,
            hold_days=sell_service.hold_days,
            usd_per_star=f"{sell_service.usd_per_star:f}",
            payout_methods=list(StarsSellPayoutMethod),
        ),
        payment_providers=providers,
        referral_program=ReferralProgramResponse(
            level1_percent=level1,
            level2_percent=level2,
            level3_percent=level3,
        ),
    )


@router.get("/catalog", summary="Products, pricing, payment providers and referral terms")
async def get_catalog(
    request: Request,
    stars_order_service: StarsOrderServiceDep,
    stars_sell_order_service: StarsSellOrderServiceDep,
) -> CatalogResponse:
    cached: tuple[float, CatalogResponse] | None = getattr(request.app.state, _CACHE_ATTR, None)
    now = time.monotonic()
    if cached is not None and now - cached[0] < _CACHE_TTL_SECONDS:
        return cast(CatalogResponse, cached[1])
    response = _build_catalog(stars_order_service, stars_sell_order_service)
    setattr(request.app.state, _CACHE_ATTR, (now, response))
    return response
