from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request, status

from app.services.crud.stars_order import StarsOrderService
from app.services.platega_pay import PlategaPayService
from app.utils import mjson

logger = logging.getLogger(__name__)


def create_router(path: str) -> APIRouter:
    normalized_path = path if path.startswith("/") else f"/{path}"
    router = APIRouter(include_in_schema=False)

    async def platega_pay_webhook(request: Request) -> dict[str, bool]:
        platega_pay_service: PlategaPayService = request.app.state.platega_pay_service
        stars_order_service: StarsOrderService = request.app.state.stars_order_service
        if not platega_pay_service.configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Platega Pay is not configured.",
            )

        raw_body = await request.body()
        if not platega_pay_service.verify_webhook_signature(
            raw_body=raw_body,
            headers=dict(request.headers.items()),
        ):
            logger.warning("Platega webhook rejected: invalid signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature.",
            )

        try:
            payload = mjson.decode(raw_body)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payload.",
            ) from None
        event = platega_pay_service.parse_webhook_event(payload)
        if event is None:
            return {"ok": True}
        if not event.is_terminal:
            return {"ok": True}
        if event.transaction_id is None and event.payment_payload is None:
            return {"ok": True}

        try:
            order = await stars_order_service.process_platega_webhook_payment(
                transaction_id=event.transaction_id,
                payment_payload=event.payment_payload,
                webhook_status=event.status,
            )
            logger.info(
                (
                    "Platega webhook processed: transaction_id=%s payload=%s "
                    "status=%s local_order_id=%s"
                ),
                event.transaction_id,
                event.payment_payload,
                event.status,
                order.id if order is not None else None,
            )
        except Exception:
            logger.exception(
                (
                    "Failed to process Platega webhook transaction_id=%s "
                    "payload=%s status=%s"
                ),
                event.transaction_id,
                event.payment_payload,
                event.status,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process payment.",
            ) from None

        return {"ok": True}

    router.add_api_route(normalized_path, platega_pay_webhook, methods=["POST"])
    if normalized_path != "/" and not normalized_path.endswith("/"):
        router.add_api_route(f"{normalized_path}/", platega_pay_webhook, methods=["POST"])

    return router
