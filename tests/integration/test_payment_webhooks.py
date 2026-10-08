from __future__ import annotations

import hashlib
import hmac
import unittest
from typing import Any

from fastapi import APIRouter, FastAPI

from app.endpoints.crypto_pay import create_router as create_crypto_router
from app.endpoints.heleket_pay import create_router as create_heleket_router
from app.endpoints.lzt_pay import create_router as create_lzt_router
from app.endpoints.nice_pay import create_router as create_nice_router
from app.endpoints.platega_pay import create_router as create_platega_router
from app.endpoints.ton_pay import create_router as create_ton_router
from app.endpoints.xrocket_pay import create_router as create_xrocket_router
from app.services.heleket_pay import HeleketWebhookEvent
from app.services.nice_pay import NicePayWebhookEvent
from app.services.platega_pay import PlategaWebhookEvent
from app.services.xrocket_pay import XRocketWebhookEvent
from app.utils import mjson

from .fakes import ASGIResponse, asgi_request


class ProviderFake:
    configured = True
    api_token = "integration-token"

    def __init__(self, *, event: Any = None, signature_valid: bool = True) -> None:
        self.event = event
        self.signature_valid = signature_valid

    def verify_webhook_signature(self, **_: Any) -> bool:
        return self.signature_valid

    def parse_webhook_event(self, *_: Any, **__: Any) -> Any:
        return self.event


class StarsOrderServiceFake:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def _record(self, name: str, kwargs: dict[str, Any]) -> None:
        self.calls.append((name, kwargs))

    async def process_crypto_webhook_invoice(self, **kwargs: Any) -> None:
        await self._record("crypto", kwargs)

    async def process_lzt_webhook_invoice(self, **kwargs: Any) -> None:
        await self._record("lzt", kwargs)

    async def process_nice_pay_webhook_payment(self, **kwargs: Any) -> None:
        await self._record("nice", kwargs)

    async def process_platega_webhook_payment(self, **kwargs: Any) -> None:
        await self._record("platega", kwargs)

    async def process_xrocket_webhook_invoice(self, **kwargs: Any) -> None:
        await self._record("xrocket", kwargs)

    async def process_heleket_webhook_invoice(self, **kwargs: Any) -> None:
        await self._record("heleket", kwargs)

    async def process_ton_invoice_webhook_payment(self, **kwargs: Any) -> None:
        await self._record("ton", kwargs)


def create_test_app(
    router: APIRouter,
    *,
    provider_name: str | None = None,
    provider: ProviderFake | None = None,
) -> tuple[FastAPI, StarsOrderServiceFake]:
    app = FastAPI()
    app.include_router(router)
    orders = StarsOrderServiceFake()
    app.state.stars_order_service = orders
    if provider_name is not None:
        setattr(app.state, provider_name, provider)
    return app, orders


class PaymentWebhookIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_crypto_webhook_verifies_signature_and_forwards_invoice(self) -> None:
        provider = ProviderFake()
        app, orders = create_test_app(
            create_crypto_router("/crypto"),
            provider_name="crypto_pay_service",
            provider=provider,
        )
        body = mjson.bytes_encode({"update_type": "invoice_paid", "payload": {"invoice_id": 41}})
        secret = hashlib.sha256(provider.api_token.encode()).digest()
        signature = hmac.new(secret, body, hashlib.sha256).hexdigest()

        response = await asgi_request(
            app,
            method="POST",
            path="/crypto",
            body=body,
            headers={"crypto-pay-api-signature": signature},
        )

        self.assert_webhook_ok(response)
        self.assertEqual(orders.calls, [("crypto", {"invoice_id": 41})])

    async def test_lzt_webhook_forwards_paid_invoice(self) -> None:
        app, orders = create_test_app(
            create_lzt_router("/lzt"),
            provider_name="lzt_pay_service",
            provider=ProviderFake(),
        )
        response = await asgi_request(
            app,
            method="POST",
            path="/lzt",
            body=mjson.bytes_encode(
                {"invoice": {"invoice_id": "42", "payment_id": "pay-42", "status": "paid"}}
            ),
        )

        self.assert_webhook_ok(response)
        self.assertEqual(
            orders.calls,
            [("lzt", {"invoice_id": 42, "payment_id": "pay-42"})],
        )

    async def test_nice_webhook_verifies_signature_and_forwards_payment(self) -> None:
        event = NicePayWebhookEvent(
            result="success",
            payment_id="nice-43",
            order_id="43",
            is_paid=True,
        )
        app, orders = create_test_app(
            create_nice_router("/nice"),
            provider_name="nice_pay_service",
            provider=ProviderFake(event=event),
        )
        response = await asgi_request(
            app,
            method="GET",
            path="/nice",
            query={"result": "success", "hash": "valid"},
        )

        self.assert_webhook_ok(response)
        self.assertEqual(
            orders.calls,
            [
                (
                    "nice",
                    {"payment_id": "nice-43", "order_id": "43", "webhook_result": "success"},
                )
            ],
        )

    async def test_platega_webhook_verifies_signature_and_forwards_payment(self) -> None:
        event = PlategaWebhookEvent(
            transaction_id="tx-44",
            payment_payload="order-44",
            status="confirmed",
            is_paid=True,
            is_terminal=True,
        )
        app, orders = create_test_app(
            create_platega_router("/platega"),
            provider_name="platega_pay_service",
            provider=ProviderFake(event=event),
        )
        response = await asgi_request(
            app,
            method="POST",
            path="/platega",
            body=mjson.bytes_encode({"status": "confirmed"}),
        )

        self.assert_webhook_ok(response)
        self.assertEqual(
            orders.calls,
            [
                (
                    "platega",
                    {
                        "transaction_id": "tx-44",
                        "payment_payload": "order-44",
                        "webhook_status": "confirmed",
                    },
                )
            ],
        )

    async def test_xrocket_webhook_forwards_paid_invoice(self) -> None:
        event = XRocketWebhookEvent(
            payment_payload="order-45",
            invoice_id="invoice-45",
            status="paid",
            is_paid=True,
        )
        app, orders = create_test_app(
            create_xrocket_router("/xrocket"),
            provider_name="xrocket_pay_service",
            provider=ProviderFake(event=event),
        )
        response = await asgi_request(
            app,
            method="POST",
            path="/xrocket",
            body=mjson.bytes_encode({"type": "invoicePay", "data": {"id": "invoice-45"}}),
        )

        self.assert_webhook_ok(response)
        self.assertEqual(
            orders.calls,
            [
                (
                    "xrocket",
                    {
                        "payment_payload": "order-45",
                        "invoice_id": "invoice-45",
                        "webhook_status": "paid",
                    },
                )
            ],
        )

    async def test_heleket_webhook_verifies_signature_and_forwards_payment(self) -> None:
        event = HeleketWebhookEvent(
            invoice_type="payment",
            invoice_uuid="invoice-46",
            order_id="46",
            status="paid",
            is_paid=True,
            is_final=True,
        )
        app, orders = create_test_app(
            create_heleket_router("/heleket", trusted_ips="127.0.0.1"),
            provider_name="heleket_pay_service",
            provider=ProviderFake(event=event),
        )
        response = await asgi_request(
            app,
            method="POST",
            path="/heleket",
            body=mjson.bytes_encode({"status": "paid"}),
        )

        self.assert_webhook_ok(response)
        self.assertEqual(
            orders.calls,
            [
                (
                    "heleket",
                    {
                        "invoice_uuid": "invoice-46",
                        "order_id": "46",
                        "webhook_status": "paid",
                    },
                )
            ],
        )

    async def test_ton_webhook_forwards_invoice(self) -> None:
        app, orders = create_test_app(create_ton_router("/ton"))
        response = await asgi_request(
            app,
            method="POST",
            path="/ton",
            body=mjson.bytes_encode({"invoice": {"id": "invoice-47", "status": "paid"}}),
        )

        self.assert_webhook_ok(response)
        self.assertEqual(
            orders.calls,
            [("ton", {"invoice_id": "invoice-47", "webhook_status": "paid"})],
        )

    async def test_signed_webhooks_reject_invalid_signatures(self) -> None:
        cases = (
            (create_crypto_router("/hook"), "crypto_pay_service", ProviderFake(), "POST"),
            (
                create_nice_router("/hook"),
                "nice_pay_service",
                ProviderFake(signature_valid=False),
                "GET",
            ),
            (
                create_platega_router("/hook"),
                "platega_pay_service",
                ProviderFake(signature_valid=False),
                "POST",
            ),
            (
                create_heleket_router("/hook"),
                "heleket_pay_service",
                ProviderFake(signature_valid=False),
                "POST",
            ),
        )
        for router, provider_name, provider, method in cases:
            with self.subTest(provider=provider_name):
                app, orders = create_test_app(
                    router,
                    provider_name=provider_name,
                    provider=provider,
                )
                response = await asgi_request(
                    app,
                    method=method,
                    path="/hook",
                    body=b"{}",
                    query={"hash": "invalid"},
                    headers={"crypto-pay-api-signature": "invalid"},
                )
                self.assertEqual(response.status_code, 401)
                self.assertEqual(orders.calls, [])

    async def test_malformed_payloads_are_rejected_or_ignored_without_facade_calls(self) -> None:
        rejected_cases = (
            (create_platega_router("/hook"), "platega_pay_service", ProviderFake(), "POST"),
            (create_heleket_router("/hook"), "heleket_pay_service", ProviderFake(), "POST"),
        )
        for router, provider_name, provider, method in rejected_cases:
            with self.subTest(provider=provider_name):
                app, orders = create_test_app(
                    router,
                    provider_name=provider_name,
                    provider=provider,
                )
                response = await asgi_request(
                    app,
                    method=method,
                    path="/hook",
                    body=b"not-json",
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(orders.calls, [])

        ton_app, ton_orders = create_test_app(create_ton_router("/hook"))
        ton_response = await asgi_request(
            ton_app,
            method="POST",
            path="/hook",
            body=b"not-json",
        )
        self.assertEqual(ton_response.status_code, 400)
        self.assertEqual(ton_orders.calls, [])

        ignored_cases = (
            (create_lzt_router("/hook"), "lzt_pay_service"),
            (create_xrocket_router("/hook"), "xrocket_pay_service"),
        )
        for router, provider_name in ignored_cases:
            with self.subTest(provider=provider_name):
                app, orders = create_test_app(
                    router,
                    provider_name=provider_name,
                    provider=ProviderFake(),
                )
                response = await asgi_request(
                    app,
                    method="POST",
                    path="/hook",
                    body=b"[]",
                )
                self.assert_webhook_ok(response)
                self.assertEqual(orders.calls, [])

    @staticmethod
    def assert_webhook_ok(response: ASGIResponse) -> None:
        if response.status_code != 200 or response.json() != {"ok": True}:
            raise AssertionError(
                f"Expected 200 {{'ok': True}}, got {response.status_code} {response.body!r}"
            )


if __name__ == "__main__":
    unittest.main()
