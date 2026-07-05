from __future__ import annotations

import logging
from typing import Annotated, Optional

from aiogram.types import LabeledPrice
from fastapi import APIRouter, Query

from app.models.dto.miniapp import (
    CreateSellOrderRequest,
    SellOrderResponse,
    SellOrdersPageResponse,
    SellQuoteRequest,
    SellQuoteResponse,
)
from app.services.crud.stars_sell_order import StarsSellOrderError
from app.services.crud.stars_sell_order import ValidationError as SellValidationError
from app.stars import price_usd_for_cents

from ..deps import BotDep, CurrentUser, StarsSellOrderServiceDep
from ..errors import not_found, validation_error
from ..serializers import build_sell_order_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sell", tags=["sell"])


@router.post("/quote", summary="Preview the payout for selling Stars")
async def quote_sell(
    payload: SellQuoteRequest,
    _auth: CurrentUser,
    stars_sell_order_service: StarsSellOrderServiceDep,
) -> SellQuoteResponse:
    try:
        quote = stars_sell_order_service.build_quote(stars_count=payload.stars_count)
    except SellValidationError as error:
        validation_error(str(error))
    return SellQuoteResponse(
        stars_count=quote.stars_count,
        payout_amount_cents=quote.payout_amount_cents,
        payout_amount_usd=price_usd_for_cents(quote.payout_amount_cents),
        invoice_total_amount=quote.invoice_total_amount,
        hold_days=quote.hold_days,
    )


@router.post("", summary="Create a sell-Stars order and a Telegram Stars invoice link")
async def create_sell_order(
    payload: CreateSellOrderRequest,
    auth: CurrentUser,
    bot: BotDep,
    stars_sell_order_service: StarsSellOrderServiceDep,
) -> SellOrderResponse:
    try:
        result = await stars_sell_order_service.create_or_refresh_pending_order(
            user_id=auth.user.id,
            stars_count=payload.stars_count,
            payout_wallet=payload.payout_wallet,
            payout_method=payload.payout_method,
        )
    except SellValidationError as error:
        validation_error(str(error))
    except StarsSellOrderError as error:
        validation_error(str(error))
    order = result.order
    invoice_link: str | None = None
    try:
        invoice_link = await bot.create_invoice_link(
            title="Sell Stars",
            description=f"Sell {order.stars_count} Telegram Stars",
            payload=order.invoice_payload,
            currency="XTR",
            prices=[LabeledPrice(label="Stars", amount=order.invoice_total_amount)],
        )
    except Exception:
        logger.exception("Failed to create Stars invoice link for sell order %s", order.id)
    return build_sell_order_response(order=order, invoice_link=invoice_link)


@router.get("", summary="Paginated sell-order history")
async def list_sell_orders(
    auth: CurrentUser,
    stars_sell_order_service: StarsSellOrderServiceDep,
    page: Annotated[int, Query(ge=0)] = 0,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> SellOrdersPageResponse:
    orders, has_next, total_pages = await stars_sell_order_service.list_recent_page(
        user_id=auth.user.id,
        page=page,
        page_size=page_size,
    )
    return SellOrdersPageResponse(
        items=[build_sell_order_response(order=order) for order in orders],
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
    )


@router.get("/open", summary="The user's current sell order awaiting payment, if any")
async def get_open_sell_order(
    auth: CurrentUser,
    stars_sell_order_service: StarsSellOrderServiceDep,
) -> Optional[SellOrderResponse]:
    order = await stars_sell_order_service.get_open_payment_for_user(user_id=auth.user.id)
    if order is None:
        return None
    return build_sell_order_response(order=order)


@router.get("/{order_id}", summary="Fetch a single sell order by id")
async def get_sell_order(
    order_id: int,
    auth: CurrentUser,
    stars_sell_order_service: StarsSellOrderServiceDep,
) -> SellOrderResponse:
    order = await stars_sell_order_service.get_user_order(
        user_id=auth.user.id,
        order_id=order_id,
    )
    if order is None:
        not_found("Sell order was not found.")
    return build_sell_order_response(order=order)


@router.post("/{order_id}/cancel", summary="Cancel a sell order still awaiting payment")
async def cancel_sell_order(
    order_id: int,
    auth: CurrentUser,
    stars_sell_order_service: StarsSellOrderServiceDep,
) -> SellOrderResponse:
    order = await stars_sell_order_service.cancel_pending_order(
        user_id=auth.user.id,
        order_id=order_id,
    )
    if order is None:
        not_found("Sell order was not found.")
    return build_sell_order_response(order=order)
