from __future__ import annotations

import unittest
from typing import Any

from app.vendor.platega_sdk import Platega, PlategaAPIError


class RecordingPlatega(Platega):
    def __init__(self) -> None:
        super().__init__(merchant_id="merchant", secret="secret")
        self.request: tuple[str, str, dict[str, Any] | None] | None = None

    def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.request = (method, endpoint, data)
        return {"transactionId": "tx-1"}


class PlategaClientTests(unittest.TestCase):
    def test_create_payment_omits_empty_optional_fields(self) -> None:
        client = RecordingPlatega()

        client.create_payment(12.5, "RUB", Platega.METHOD_SBP_QR)

        self.assertEqual(
            client.request,
            (
                "POST",
                "/transaction/process",
                {
                    "paymentMethod": 2,
                    "paymentDetails": {"amount": 12.5, "currency": "RUB"},
                },
            ),
        )

    def test_create_payment_preserves_all_supplied_fields(self) -> None:
        client = RecordingPlatega()

        client.create_payment(
            7,
            "USD",
            Platega.METHOD_CRYPTO,
            "Order 42",
            "https://example.test/success",
            "https://example.test/failure",
            "order-42",
        )

        assert client.request is not None
        self.assertEqual(
            client.request[2],
            {
                "paymentMethod": 13,
                "paymentDetails": {"amount": 7.0, "currency": "USD"},
                "description": "Order 42",
                "return": "https://example.test/success",
                "failedUrl": "https://example.test/failure",
                "payload": "order-42",
            },
        )

    def test_api_url_remains_configurable_per_client(self) -> None:
        client = RecordingPlatega()

        client.API_URL = "https://payments.example.test"

        self.assertEqual(client.API_URL, "https://payments.example.test")


class PlategaErrorTests(unittest.TestCase):
    def test_error_string_includes_http_code_when_present(self) -> None:
        error = PlategaAPIError("denied", 403, {"status": "error"})

        self.assertEqual(str(error), "[HTTP 403] denied")
        self.assertEqual(error.response_data, {"status": "error"})

    def test_error_string_without_http_code_is_plain_message(self) -> None:
        self.assertEqual(str(PlategaAPIError("offline")), "offline")


if __name__ == "__main__":
    unittest.main()
