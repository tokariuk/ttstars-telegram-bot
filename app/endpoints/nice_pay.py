from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request, status

from app.services.crud.stars_order import StarsOrderService
from app.services.nice_pay import NicePayService

logger = logging.getLogger(__name__)


def create_router(path: str) -> APIRouter:
    normalized_path = path if path.startswith("/") else f"/{path}"
    router = APIRouter(include_in_schema=False)

    async def nice_pay_webhook(request: Request) -> dict[str, bool]:
        nice_pay_service: NicePayService = request.app.state.nice_pay_service
        stars_order_service: StarsOrderService = request.app.state.stars_order_service
        if not nice_pay_service.configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="NicePay is not configured.",
            )

        query_params = dict(request.query_params.items())
        if not nice_pay_service.verify_webhook_signature(query_params=query_params):
            logger.warning("NicePay webhook rejected: invalid signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature.",
            )

        event = nice_pay_service.parse_webhook_event(query_params=query_params)
        if event is None:
            return {"ok": True}
        if not event.is_paid:
            return {"ok": True}
        if event.payment_id is None and event.order_id is None:
            return {"ok": True}

        try:
            order = await stars_order_service.process_nice_pay_webhook_payment(
                payment_id=event.payment_id,
                order_id=event.order_id,
                webhook_result=event.result,
            )
            logger.info(
                "NicePay webhook processed: payment_id=%s order_id=%s local_order_id=%s",
                event.payment_id,
                event.order_id,
                order.id if order is not None else None,
            )
        except Exception:
            logger.exception(
                "Failed to process NicePay webhook: payment_id=%s order_id=%s",
                event.payment_id,
                event.order_id,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process payment.",
            ) from None

        return {"ok": True}

    router.add_api_route(normalized_path, nice_pay_webhook, methods=["GET"])
    if normalized_path != "/" and not normalized_path.endswith("/"):
        router.add_api_route(f"{normalized_path}/", nice_pay_webhook, methods=["GET"])

    return router
