from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request, status

from app.services.crud.stars_order import StarsOrderService
from app.services.xrocket_pay import XRocketPayService
from app.utils import mjson

logger = logging.getLogger(__name__)


def create_router(path: str) -> APIRouter:
    normalized_path = path if path.startswith("/") else f"/{path}"
    router = APIRouter(include_in_schema=False)

    async def xrocket_pay_webhook(request: Request) -> dict[str, bool]:
        xrocket_pay_service: XRocketPayService = request.app.state.xrocket_pay_service
        stars_order_service: StarsOrderService = request.app.state.stars_order_service
        if not xrocket_pay_service.configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="xRocket Pay is not configured.",
            )

        payload = mjson.decode(await request.body())
        event = xrocket_pay_service.parse_webhook_event(payload)
        if event is None:
            return {"ok": True}

        if not event.is_paid:
            return {"ok": True}

        if event.payment_payload is None and event.invoice_id is None:
            return {"ok": True}

        try:
            order = await stars_order_service.process_xrocket_webhook_invoice(
                payment_payload=event.payment_payload,
                invoice_id=event.invoice_id,
                webhook_status=event.status,
            )
            logger.info(
                "xRocket webhook processed: payment_payload=%s invoice_id=%s local_order_id=%s",
                event.payment_payload,
                event.invoice_id,
                order.id if order is not None else None,
            )
        except Exception:
            logger.exception(
                "Failed to process xRocket webhook: payment_payload=%s invoice_id=%s",
                event.payment_payload,
                event.invoice_id,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process invoice.",
            ) from None

        return {"ok": True}

    router.add_api_route(normalized_path, xrocket_pay_webhook, methods=["POST"])
    if normalized_path != "/" and not normalized_path.endswith("/"):
        router.add_api_route(f"{normalized_path}/", xrocket_pay_webhook, methods=["POST"])

    return router
