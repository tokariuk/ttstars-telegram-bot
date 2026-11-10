from __future__ import annotations

import hashlib
import hmac
import unittest
from typing import Any

from app.services.xrocket_pay import XRocketPayService


class RecordingXRocketPayService(XRocketPayService):
    def __init__(self, *, responses: list[dict[str, Any]]) -> None:
        super().__init__(
            api_key="current-api-token",
            webhook_secret="webhook-secret",
            base_url="https://pay.api.xrocket.exchange",
            currency="USDT",
            success_url="https://t.me/ttstarsbot",
        )
        self.responses = responses
        self.requests: list[dict[str, Any]] = []

    async def _request_json(
        self,
        *,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        self.requests.append(
            {"method": method, "path": path, "json": json, "params": params}
        )
        return self.responses.pop(0)


class XRocketPayServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_invoice_uses_current_api_contract(self) -> None:
        service = RecordingXRocketPayService(
            responses=[
                {
                    "id": "invoice-42",
                    "clientInvoiceId": "order-42",
                    "status": "created",
                    "links": {
                        "telegramBotLink": "https://t.me/xrocket?start=invoice-42",
                        "webLink": "https://pay.xrocket.exchange/invoice-42",
                    },
                }
            ]
        )

        invoice = await service.create_invoice(
            amount="1.2300000004",
            description="50 Telegram Stars",
            payment_payload="order-42",
            callback_url="https://example.test/xrocket-pay/webhook",
        )

        self.assertEqual(invoice.invoice_id, "invoice-42")
        self.assertEqual(invoice.payment_payload, "order-42")
        self.assertEqual(invoice.pay_url, "https://t.me/xrocket?start=invoice-42")
        self.assertEqual(
            service.requests,
            [
                {
                    "method": "POST",
                    "path": "/api/v1/invoices",
                    "params": None,
                    "json": {
                        "priceAmount": "1.230000000",
                        "numPayments": 1,
                        "priceCurrency": "USDT",
                        "payoutCurrency": "USDT",
                        "payCurrencies": ["USDT"],
                        "clientInvoiceId": "order-42",
                        "description": "50 Telegram Stars",
                        "callback": {
                            "callbackUrl": "https://example.test/xrocket-pay/webhook",
                            "payload": {"paymentPayload": "order-42"},
                        },
                        "url": {"successUrl": "https://t.me/ttstarsbot"},
                    },
                }
            ],
        )

    async def test_get_invoice_status_queries_by_known_identifier(self) -> None:
        service = RecordingXRocketPayService(
            responses=[{"id": "invoice-43", "clientInvoiceId": "order-43", "status": "paid"}]
        )

        result = await service.get_invoice_status(payment_payload="order-43")

        self.assertTrue(result.is_paid)
        self.assertEqual(result.invoice_id, "invoice-43")
        self.assertEqual(
            service.requests,
            [
                {
                    "method": "GET",
                    "path": "/api/v1/invoice",
                    "json": None,
                    "params": {"clientInvoiceId": "order-43"},
                }
            ],
        )

    def test_current_api_uses_bearer_authorization(self) -> None:
        service = RecordingXRocketPayService(responses=[])

        self.assertEqual(
            service._headers(),
            {
                "Authorization": "Bearer current-api-token",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

    def test_parse_current_invoice_webhook(self) -> None:
        service = RecordingXRocketPayService(responses=[])

        event = service.parse_webhook_event(
            {
                "id": "event-44",
                "type": "invoice",
                "timestamp": "2026-11-11T10:00:00Z",
                "data": {
                    "event": "invoice_status_changed",
                    "invoice": {
                        "id": "invoice-44",
                        "clientInvoiceId": "order-44",
                        "status": "paid",
                        "callback": {"payload": {"paymentPayload": "order-44"}},
                    },
                },
            }
        )

        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event.payment_payload, "order-44")
        self.assertEqual(event.invoice_id, "invoice-44")
        self.assertEqual(event.status, "paid")
        self.assertTrue(event.is_paid)

    def test_webhook_signature_requires_valid_recent_v1_signature(self) -> None:
        service = RecordingXRocketPayService(responses=[])
        body = b'{"type":"invoice"}'
        timestamp = "1773223200000"
        signature = hmac.new(
            b"webhook-secret",
            timestamp.encode() + b"." + body,
            hashlib.sha256,
        ).hexdigest()

        self.assertTrue(
            service.verify_webhook_signature(
                raw_body=body,
                signature=signature,
                signature_version="v1",
                signature_timestamp=timestamp,
                now_ms=1773223201000,
            )
        )
        self.assertFalse(
            service.verify_webhook_signature(
                raw_body=body,
                signature=signature,
                signature_version="v1",
                signature_timestamp=timestamp,
                now_ms=1773223500001,
            )
        )
        self.assertFalse(
            service.verify_webhook_signature(
                raw_body=body,
                signature="wrong",
                signature_version="v1",
                signature_timestamp=timestamp,
                now_ms=1773223201000,
            )
        )

    def test_service_is_not_exposed_without_webhook_secret(self) -> None:
        service = XRocketPayService(
            api_key="current-api-token",
            webhook_secret=None,
            base_url="https://pay.api.xrocket.exchange",
            currency="USDT",
        )

        self.assertFalse(service.configured)


if __name__ == "__main__":
    unittest.main()
