from __future__ import annotations

import contextlib
import html
import json
import logging
from typing import Any

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram_i18n import I18nContext, I18nMiddleware
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.enums.stars_order import (
    StarsOrderProductType,
    StarsOrderStatus,
)
from app.models.dto.stars_order import StarsOrderDto
from app.services.crud import StarsOrderService, UserService
from app.stars import price_usd_for_cents
from app.utils.localization import normalize_i18n_locale

logger = logging.getLogger(__name__)
_CLOSE_RESULT_NOTICE_CALLBACK = "storefront_close_result_notice"


def create_router(invoice_webhook_path: str) -> APIRouter:
    router = APIRouter(tags=["ton-pay"])
    normalized_invoice_webhook_path = _normalize_route_path(
        invoice_webhook_path,
        default="/ton-pay/webhook",
    )

    @router.post(normalized_invoice_webhook_path)
    async def ton_invoice_webhook(request: Request) -> JSONResponse:
        try:
            raw_body = await request.body()
            payload = json.loads(raw_body.decode("utf-8") if raw_body else "{}")
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            logger.warning("Invalid TONConsole invoice webhook payload: %s", error)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload.",
            ) from error

        invoice_payload = _extract_invoice_webhook_payload(payload)
        invoice_id = _string_or_none(invoice_payload.get("id"))
        invoice_status = _string_or_none(invoice_payload.get("status"))
        if invoice_id is None:
            logger.warning("TONConsole invoice webhook without id: %s", payload)
            return JSONResponse({"ok": True, "ignored": True})

        logger.info(
            "TONConsole invoice webhook received: invoice_id=%s status=%s",
            invoice_id,
            invoice_status or "-",
        )
        stars_order_service: StarsOrderService = request.app.state.stars_order_service
        order = await stars_order_service.process_ton_invoice_webhook_payment(
            invoice_id=invoice_id,
            webhook_status=invoice_status,
        )
        if order is None:
            logger.warning(
                "TONConsole invoice webhook did not match local payment: invoice_id=%s status=%s",
                invoice_id,
                invoice_status or "-",
            )
            return JSONResponse({"ok": True})

        logger.info(
            "TONConsole invoice webhook processed: "
            "invoice_id=%s order_id=%s status=%s provider_status=%s",
            invoice_id,
            order.id,
            order.status.value,
            order.provider_status or "-",
        )
        if order is not None and order.status in {
            StarsOrderStatus.COMPLETED,
            StarsOrderStatus.FAILED,
        }:
            if await _acquire_order_action_lock(
                stars_order_service=stars_order_service,
                order_id=order.id,
                action="notify",
            ):
                await _notify_user_order_terminal(request=request, order=order)
        return JSONResponse({"ok": True})

    return router


def _normalize_route_path(path: str, *, default: str) -> str:
    raw = path.strip()
    if not raw:
        return default
    normalized = raw if raw.startswith("/") else f"/{raw}"
    return normalized.rstrip("/")


def _extract_invoice_webhook_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    for key in ("invoice", "data", "payload"):
        nested = payload.get(key)
        if isinstance(nested, dict) and "id" in nested:
            return nested
    return payload


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _close_notice_button_text(*, i18n: I18nContext, language: str) -> str:
    with i18n.use_locale(normalize_i18n_locale(language)):
        return str(i18n.messages.check_notice_close_button())


def _i18n_context_for_language(*, i18n_middleware: I18nMiddleware, language: str) -> I18nContext:
    return i18n_middleware.new_context(
        locale=normalize_i18n_locale(language),
        data={},
    )


def _tx_line(tx_hash: str | None) -> str:
    if not tx_hash:
        return ""
    return f"\nTX: <code>{html.escape(tx_hash)}</code>"


def _completed_text(
    *,
    i18n: I18nContext,
    product_type: StarsOrderProductType,
    stars_count: int,
    recipient: str,
    recipient_user_id: int | None,
    premium_months: int | None,
    amount_usd: str,
    tx_hash: str | None,
) -> str:
    if product_type == StarsOrderProductType.TOPUP:
        return i18n.get("messages-order_result_completed_topup", amount=amount_usd)
    if product_type == StarsOrderProductType.GIFT:
        return i18n.get(
            "messages-order_result_completed_gift",
            recipient_user_id=recipient_user_id or 0,
            amount_usd=amount_usd,
        )
    if product_type == StarsOrderProductType.PREMIUM:
        return i18n.get(
            "messages-order_result_completed_premium",
            recipient=html.escape(recipient),
            premium_months=premium_months or 0,
            tx_line=_tx_line(tx_hash),
        )
    return i18n.get(
        "messages-order_result_completed_stars",
        recipient=html.escape(recipient),
        stars_count=stars_count,
        tx_line=_tx_line(tx_hash),
    )


def _failed_text(
    *,
    i18n: I18nContext,
    product_type: StarsOrderProductType,
    amount_usd: str,
) -> str:
    if product_type == StarsOrderProductType.TOPUP:
        return i18n.get("messages-order_result_failed_topup")
    if product_type == StarsOrderProductType.GIFT:
        return i18n.get("messages-order_result_failed_gift", amount_usd=amount_usd)
    if product_type == StarsOrderProductType.PREMIUM:
        return i18n.get("messages-order_result_failed_premium", amount_usd=amount_usd)
    return i18n.get("messages-order_result_failed_stars", amount_usd=amount_usd)


async def _notify_user_order_terminal(*, request: Request, order: StarsOrderDto) -> None:
    if order.status not in {StarsOrderStatus.COMPLETED, StarsOrderStatus.FAILED}:
        return
    bot: Bot = request.app.state.bot
    user_service: UserService = request.app.state.user_service
    i18n_middleware: I18nMiddleware = request.app.state.i18n_middleware

    user = await user_service.get(user_id=order.user_id)
    language = user.language if user is not None else "en"
    i18n = _i18n_context_for_language(
        i18n_middleware=i18n_middleware,
        language=language,
    )
    amount_usd = price_usd_for_cents(order.amount_cents)
    text = (
        _completed_text(
            i18n=i18n,
            product_type=order.product_type,
            stars_count=order.stars_count,
            recipient=order.recipient_username,
            recipient_user_id=order.recipient_user_id,
            premium_months=order.premium_months,
            amount_usd=amount_usd,
            tx_hash=order.fragment_tx_hash,
        )
        if order.status == StarsOrderStatus.COMPLETED
        else _failed_text(
            i18n=i18n,
            product_type=order.product_type,
            amount_usd=amount_usd,
        )
    )

    if order.checkout_message_id is not None:
        with contextlib.suppress(Exception):
            await bot.delete_message(
                chat_id=order.user_id,
                message_id=order.checkout_message_id,
            )
    with contextlib.suppress(Exception):
        await bot.send_message(
            chat_id=order.user_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=_close_notice_button_text(i18n=i18n, language=language),
                            callback_data=_CLOSE_RESULT_NOTICE_CALLBACK,
                        ),
                    ],
                ],
            ),
        )


async def _acquire_order_action_lock(
    *,
    stars_order_service: StarsOrderService,
    order_id: int,
    action: str,
) -> bool:
    key = f"ton_pay:order:{order_id}:{action}"
    try:
        locked = await stars_order_service.redis.set(
            key,
            "1",
            ex=86400,
            nx=True,
        )
        return bool(locked)
    except Exception:
        logger.exception("Failed to acquire TON order lock %s.", key)
        return False
