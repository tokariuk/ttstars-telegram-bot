from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Header, Query

from app.models.dto.miniapp import (
    CreateGiftOrderRequest,
    CreatePremiumOrderRequest,
    CreateStarsOrderRequest,
    CreateTopupOrderRequest,
    OrderResponse,
    OrdersPageResponse,
    PaymentCheckResponse,
    QuoteRequest,
    QuoteResponse,
    RecipientValidateRequest,
    RecipientValidateResponse,
)
from app.stars import normalize_recipient_username, price_usd_for_cents

from ..deps import (
    CurrentUser,
    RedisDep,
    StarsOrderServiceDep,
    run_idempotent_order_create,
)
from ..errors import ApiError, map_service_error, not_found, validation_error
from ..pricing import net_amount_cents_for_quote, parse_usd_amount_to_cents
from ..providers import TOPUP_PAYMENT_PROVIDERS
from ..serializers import build_order_response, build_payment_check_response

router = APIRouter(prefix="/orders", tags=["orders"])

IdempotencyKey = Annotated[Optional[str], Header(alias="Idempotency-Key")]


@router.post("/quote", summary="Preview the checkout total (incl. fees) without creating an order")
async def quote_order(
    payload: QuoteRequest,
    _auth: CurrentUser,
    stars_order_service: StarsOrderServiceDep,
) -> QuoteResponse:
    net_cents = net_amount_cents_for_quote(
        product_type=payload.product_type,
        stars_count=payload.stars_count,
        months=payload.months,
        amount_usd=payload.amount_usd,
    )
    try:
        pricing = stars_order_service.preview_checkout_pricing(
            provider=payload.provider,
            net_amount_cents=net_cents,
        )
    except Exception as error:  # invalid provider fee configuration
        map_service_error(error)
    fee_display = stars_order_service.provider_checkout_fee_display_text(
        provider=payload.provider,
        net_amount_cents=net_cents,
    )
    return QuoteResponse(
        product_type=payload.product_type,
        provider=payload.provider,
        currency=stars_order_service.provider_currency(provider=payload.provider),
        net_amount_cents=net_cents,
        net_amount_usd=price_usd_for_cents(net_cents),
        checkout_total_cents=pricing.customer_total_cents,
        checkout_total_usd=price_usd_for_cents(pricing.customer_total_cents),
        fee_percent=pricing.fee_percent_text,
        fee_display=fee_display,
    )


@router.post("/stars", summary="Create a Stars purchase order")
async def create_stars_order(
    payload: CreateStarsOrderRequest,
    auth: CurrentUser,
    redis: RedisDep,
    stars_order_service: StarsOrderServiceDep,
    idempotency_key: IdempotencyKey = None,
) -> OrderResponse:
    try:
        order = await run_idempotent_order_create(
            redis=redis,
            stars_order_service=stars_order_service,
            user_id=auth.user.id,
            scope="stars",
            idempotency_key=idempotency_key,
            create_order=lambda: stars_order_service.create_stars_order(
                provider=payload.provider,
                user_id=auth.user.id,
                recipient_username=payload.recipient_username,
                stars_count=payload.stars_count,
            ),
        )
    except ApiError:
        raise
    except Exception as error:
        map_service_error(error)
    return build_order_response(stars_order_service=stars_order_service, order=order)


@router.post("/premium", summary="Create a Telegram Premium order")
async def create_premium_order(
    payload: CreatePremiumOrderRequest,
    auth: CurrentUser,
    redis: RedisDep,
    stars_order_service: StarsOrderServiceDep,
    idempotency_key: IdempotencyKey = None,
) -> OrderResponse:
    try:
        order = await run_idempotent_order_create(
            redis=redis,
            stars_order_service=stars_order_service,
            user_id=auth.user.id,
            scope="premium",
            idempotency_key=idempotency_key,
            create_order=lambda: stars_order_service.create_premium_order(
                provider=payload.provider,
                user_id=auth.user.id,
                recipient_username=payload.recipient_username,
                months=payload.months,
            ),
        )
    except ApiError:
        raise
    except Exception as error:
        map_service_error(error)
    return build_order_response(stars_order_service=stars_order_service, order=order)


@router.post("/gift", summary="Create an archived/limited Telegram gift order")
async def create_gift_order(
    payload: CreateGiftOrderRequest,
    auth: CurrentUser,
    redis: RedisDep,
    stars_order_service: StarsOrderServiceDep,
    idempotency_key: IdempotencyKey = None,
) -> OrderResponse:
    try:
        order = await run_idempotent_order_create(
            redis=redis,
            stars_order_service=stars_order_service,
            user_id=auth.user.id,
            scope="gift",
            idempotency_key=idempotency_key,
            create_order=lambda: stars_order_service.create_gift_order(
                provider=payload.provider,
                user_id=auth.user.id,
                recipient_username=payload.recipient_username,
                recipient_user_id=None,
                gift_key=payload.gift_key,
                gift_message=payload.gift_message,
                gift_sender_private=payload.sender_private,
            ),
        )
    except ApiError:
        raise
    except Exception as error:
        map_service_error(error)
    return build_order_response(stars_order_service=stars_order_service, order=order)


@router.post("/topup", summary="Create a balance top-up order")
async def create_topup_order(
    payload: CreateTopupOrderRequest,
    auth: CurrentUser,
    redis: RedisDep,
    stars_order_service: StarsOrderServiceDep,
    idempotency_key: IdempotencyKey = None,
) -> OrderResponse:
    if payload.provider not in TOPUP_PAYMENT_PROVIDERS:
        validation_error("This provider does not support balance top-ups.")
    amount_cents = parse_usd_amount_to_cents(payload.amount_usd)
    try:
        order = await run_idempotent_order_create(
            redis=redis,
            stars_order_service=stars_order_service,
            user_id=auth.user.id,
            scope="topup",
            idempotency_key=idempotency_key,
            create_order=lambda: stars_order_service.create_topup_order(
                provider=payload.provider,
                user_id=auth.user.id,
                amount_cents=amount_cents,
            ),
        )
    except ApiError:
        raise
    except Exception as error:
        map_service_error(error)
    return build_order_response(stars_order_service=stars_order_service, order=order)


@router.post("/validate-recipient", summary="Check that a recipient @username is well-formed")
async def validate_recipient(
    payload: RecipientValidateRequest,
    _auth: CurrentUser,
) -> RecipientValidateResponse:
    normalized = normalize_recipient_username(payload.username)
    return RecipientValidateResponse(valid=normalized is not None, normalized=normalized)


@router.get("", summary="Paginated order & top-up history")
async def list_orders(
    auth: CurrentUser,
    stars_order_service: StarsOrderServiceDep,
    page: Annotated[int, Query(ge=0)] = 0,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> OrdersPageResponse:
    orders, has_next, total_pages = await stars_order_service.list_recent_page(
        user_id=auth.user.id,
        page=page,
        page_size=page_size,
    )
    return OrdersPageResponse(
        items=[
            build_order_response(stars_order_service=stars_order_service, order=order)
            for order in orders
        ],
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
    )


@router.get("/open", summary="The user's current open order, if any")
async def get_open_order(
    auth: CurrentUser,
    stars_order_service: StarsOrderServiceDep,
) -> Optional[OrderResponse]:
    order = await stars_order_service.get_open_order(user_id=auth.user.id)
    if order is None:
        return None
    return build_order_response(stars_order_service=stars_order_service, order=order)


@router.get("/{order_id}", summary="Fetch a single order by id")
async def get_order(
    order_id: int,
    auth: CurrentUser,
    stars_order_service: StarsOrderServiceDep,
) -> OrderResponse:
    order = await stars_order_service.get_user_order(user_id=auth.user.id, order_id=order_id)
    if order is None:
        not_found("Order was not found.")
    return build_order_response(stars_order_service=stars_order_service, order=order)


@router.post("/{order_id}/verify", summary="Re-check the payment status with the provider")
async def verify_order(
    order_id: int,
    auth: CurrentUser,
    stars_order_service: StarsOrderServiceDep,
) -> PaymentCheckResponse:
    order = await stars_order_service.get_user_order(user_id=auth.user.id, order_id=order_id)
    if order is None:
        not_found("Order was not found.")
    result = await stars_order_service.verify_order(order_id=order.id)
    if result.order is not None and result.order.user_id != auth.user.id:
        not_found("Order was not found.")
    return build_payment_check_response(stars_order_service=stars_order_service, result=result)


@router.post("/{order_id}/cancel", summary="Cancel an order that is still awaiting payment")
async def cancel_order(
    order_id: int,
    auth: CurrentUser,
    stars_order_service: StarsOrderServiceDep,
) -> OrderResponse:
    order = await stars_order_service.cancel_order(user_id=auth.user.id, order_id=order_id)
    if order is None:
        not_found("Order was not found.")
    return build_order_response(stars_order_service=stars_order_service, order=order)
