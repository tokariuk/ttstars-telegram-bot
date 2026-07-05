from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.services.crud.stars_order import StarsOrderService
from app.services.crypto_pay import CryptoPayService
from app.utils import mjson

logger = logging.getLogger(__name__)


def _verify_signature(*, raw_body: bytes, signature: str | None, api_token: str) -> bool:
    if not signature:
        return False
    secret = hashlib.sha256(api_token.encode("utf-8")).digest()
    expected = hmac.new(secret, raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature.strip().lower())


def _parse_invoice_id(value: Any) -> int | None:
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, str) and value.isdigit():
        parsed = int(value)
        return parsed if parsed > 0 else None
    return None


def create_router(path: str) -> APIRouter:
    normalized_path = path if path.startswith("/") else f"/{path}"
    router = APIRouter(include_in_schema=False)

    async def crypto_pay_webhook(request: Request) -> dict[str, bool]:
        crypto_pay_service: CryptoPayService = request.app.state.crypto_pay_service
        stars_order_service: StarsOrderService = request.app.state.stars_order_service
        if not crypto_pay_service.configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Crypto Pay is not configured.",
            )

        raw_body = await request.body()
        signature = request.headers.get("crypto-pay-api-signature")
        if not _verify_signature(
            raw_body=raw_body,
            signature=signature,
            api_token=crypto_pay_service.api_token,
        ):
            logger.warning("CryptoPay webhook rejected: invalid signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature.",
            )

        payload = mjson.decode(raw_body)
        if not isinstance(payload, dict):
            return {"ok": True}
        if str(payload.get("update_type", "")).lower() != "invoice_paid":
            return {"ok": True}
        invoice_payload = payload.get("payload")
        if not isinstance(invoice_payload, dict):
            return {"ok": True}

        invoice_id = _parse_invoice_id(
            invoice_payload.get("invoice_id") or invoice_payload.get("id")
        )
        if invoice_id is None:
            return {"ok": True}

        try:
            await stars_order_service.process_crypto_webhook_invoice(invoice_id=invoice_id)
            logger.info("CryptoPay webhook processed: invoice_id=%s", invoice_id)
        except Exception:
            logger.exception("Failed to process CryptoPay webhook invoice_id=%s", invoice_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process invoice.",
            ) from None

        return {"ok": True}

    router.add_api_route(normalized_path, crypto_pay_webhook, methods=["POST"])
    if normalized_path != "/" and not normalized_path.endswith("/"):
        router.add_api_route(f"{normalized_path}/", crypto_pay_webhook, methods=["POST"])

    return router
