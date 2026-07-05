from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.services.crud.stars_order import StarsOrderService
from app.services.lzt_pay import LZTPayService
from app.utils import mjson

logger = logging.getLogger(__name__)

_PAID_STATUSES: set[str] = {"paid", "completed", "success"}


def _to_int(value: Any) -> int | None:
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, str) and value.isdigit():
        parsed = int(value)
        return parsed if parsed > 0 else None
    return None


def _to_str(value: Any) -> str | None:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return None


def _extract_payload(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    invoice = value.get("invoice")
    if isinstance(invoice, dict):
        return invoice
    return value


def create_router(path: str) -> APIRouter:
    normalized_path = path if path.startswith("/") else f"/{path}"
    router = APIRouter(include_in_schema=False)

    async def lzt_pay_webhook(request: Request) -> dict[str, bool]:
        lzt_pay_service: LZTPayService = request.app.state.lzt_pay_service
        stars_order_service: StarsOrderService = request.app.state.stars_order_service
        if not lzt_pay_service.configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LZT Pay is not configured.",
            )

        raw_body = await request.body()
        payload = mjson.decode(raw_body)
        data = _extract_payload(payload)
        if data is None:
            return {"ok": True}

        invoice_id = _to_int(data.get("invoice_id") or data.get("id"))
        payment_id = _to_str(data.get("payment_id"))
        status_raw = data.get("status")
        invoice_status = str(status_raw).strip().lower() if status_raw is not None else "unknown"

        if invoice_status not in _PAID_STATUSES:
            return {"ok": True}

        try:
            order = await stars_order_service.process_lzt_webhook_invoice(
                invoice_id=invoice_id,
                payment_id=payment_id,
            )
            logger.info(
                "LZTPay webhook processed: invoice_id=%s payment_id=%s order_id=%s",
                invoice_id,
                payment_id,
                order.id if order is not None else None,
            )
        except Exception:
            logger.exception(
                "Failed to process LZTPay webhook invoice_id=%s payment_id=%s",
                invoice_id,
                payment_id,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process invoice.",
            ) from None

        return {"ok": True}

    router.add_api_route(normalized_path, lzt_pay_webhook, methods=["POST"])
    if normalized_path != "/" and not normalized_path.endswith("/"):
        router.add_api_route(f"{normalized_path}/", lzt_pay_webhook, methods=["POST"])

    return router
