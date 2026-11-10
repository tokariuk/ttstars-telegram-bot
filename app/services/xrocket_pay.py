from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

from aiohttp import ClientResponse, ClientSession, ClientTimeout

from app.services.parsing import extract_optional_string

_PAID_STATUSES: set[str] = {"paid"}


@dataclass(frozen=True, slots=True)
class XRocketInvoice:
    invoice_id: str
    payment_payload: str | None
    pay_url: str
    status: str


@dataclass(frozen=True, slots=True)
class XRocketInvoiceStatus:
    is_paid: bool
    status: str
    invoice_id: str | None = None


@dataclass(frozen=True, slots=True)
class XRocketWebhookEvent:
    payment_payload: str | None
    invoice_id: str | None
    status: str
    is_paid: bool


class XRocketPayService:
    def __init__(
        self,
        *,
        api_key: str | None,
        webhook_secret: str | None,
        base_url: str,
        currency: str,
        success_url: str | None = None,
    ) -> None:
        self.api_key = (api_key or "").strip()
        self.webhook_secret = (webhook_secret or "").strip()
        self.base_url = base_url.rstrip("/")
        self.currency = (currency or "USD").strip().upper() or "USD"
        self.success_url = (success_url or "").strip()
        self.timeout = ClientTimeout(total=20)

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.webhook_secret and self.base_url)

    @property
    def api_configured(self) -> bool:
        return bool(self.api_key and self.base_url)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def create_invoice(
        self,
        *,
        amount: str,
        description: str,
        payment_payload: str,
        callback_url: str | None = None,
    ) -> XRocketInvoice:
        if not self.configured:
            raise RuntimeError("xRocket Pay service is not configured.")

        normalized_payload = payment_payload.strip()
        if not normalized_payload:
            raise RuntimeError("xRocket payload is empty.")

        request_payload: dict[str, Any] = {
            "priceAmount": self._format_amount_for_request(amount),
            "numPayments": 1,
            "priceCurrency": self.currency,
            "payoutCurrency": self.currency,
            "payCurrencies": [self.currency],
            "clientInvoiceId": normalized_payload,
            "description": description,
        }
        if callback_url:
            request_payload["callback"] = {
                "callbackUrl": callback_url,
                "payload": {"paymentPayload": normalized_payload},
            }
        if self.success_url:
            request_payload["url"] = {"successUrl": self.success_url}

        payload = await self._request_json(
            method="POST",
            path="/api/v1/invoices",
            json=request_payload,
        )
        invoice = self._extract_invoice(payload)
        invoice_id = self._extract_string(invoice.get("id"))
        if invoice_id is None:
            raise RuntimeError("xRocket Pay did not return invoice ID.")
        return XRocketInvoice(
            invoice_id=invoice_id,
            payment_payload=(
                self._extract_string(invoice.get("clientInvoiceId")) or normalized_payload
            ),
            pay_url=self._extract_checkout_url(invoice),
            status=self._extract_status(invoice),
        )

    async def get_invoice_status(
        self,
        *,
        payment_payload: str | None = None,
        invoice_id: str | None = None,
    ) -> XRocketInvoiceStatus:
        if not self.api_configured:
            return XRocketInvoiceStatus(is_paid=False, status="unconfigured")

        normalized_payment_payload = (
            payment_payload.strip() if isinstance(payment_payload, str) else ""
        )
        normalized_invoice_id = invoice_id.strip() if isinstance(invoice_id, str) else ""
        if not normalized_invoice_id and not normalized_payment_payload:
            return XRocketInvoiceStatus(is_paid=False, status="invoice_missing")

        params = (
            {"invoiceId": normalized_invoice_id}
            if normalized_invoice_id
            else {"clientInvoiceId": normalized_payment_payload}
        )

        payload = await self._request_json(
            method="GET",
            path="/api/v1/invoice",
            params=params,
        )
        invoice = self._extract_invoice(payload)
        status = self._extract_status(invoice)
        resolved_invoice_id = self._extract_string(invoice.get("id")) or normalized_invoice_id
        return XRocketInvoiceStatus(
            is_paid=status in _PAID_STATUSES,
            status=status,
            invoice_id=resolved_invoice_id,
        )

    def parse_webhook_event(self, payload: Any) -> XRocketWebhookEvent | None:
        if not isinstance(payload, dict):
            return None
        if (self._extract_string(payload.get("type")) or "").lower() != "invoice":
            return None
        data = payload.get("data")
        if not isinstance(data, dict):
            return None
        event_name = (self._extract_string(data.get("event")) or "").lower()
        if event_name not in {"invoice_status_changed", "payment_status_changed"}:
            return None
        invoice = data.get("invoice")
        if not isinstance(invoice, dict):
            return None
        status = self._extract_status(invoice)
        callback = invoice.get("callback")
        callback_payload: Any = None
        if isinstance(callback, dict):
            callback_payload = callback.get("payload")
        embedded_payment_payload: str | None = None
        if isinstance(callback_payload, dict):
            embedded_payment_payload = self._extract_string(
                callback_payload.get("paymentPayload")
            )
        return XRocketWebhookEvent(
            payment_payload=(
                self._extract_string(invoice.get("clientInvoiceId"))
                or embedded_payment_payload
            ),
            invoice_id=self._extract_string(invoice.get("id")),
            status=status,
            is_paid=status in _PAID_STATUSES,
        )

    def verify_webhook_signature(
        self,
        *,
        raw_body: bytes,
        signature: str | None,
        signature_version: str | None,
        signature_timestamp: str | None,
        now_ms: int | None = None,
    ) -> bool:
        if not self.webhook_secret or signature_version != "v1":
            return False
        normalized_signature = (signature or "").strip().lower()
        normalized_timestamp = (signature_timestamp or "").strip()
        if not normalized_signature or not normalized_timestamp:
            return False
        try:
            timestamp_ms = int(normalized_timestamp)
        except ValueError:
            return False
        current_ms = int(time.time() * 1000) if now_ms is None else now_ms
        if abs(current_ms - timestamp_ms) > 300_000:
            return False
        signed_payload = normalized_timestamp.encode() + b"." + raw_body
        expected = hmac.new(
            self.webhook_secret.encode(),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, normalized_signature)

    async def _request_json(
        self,
        *,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        async with ClientSession() as session:
            async with session.request(
                method.upper(),
                url,
                json=json,
                params=params,
                headers=self._headers(),
                timeout=self.timeout,
            ) as response:
                payload = await self._safe_json(response)
                self._raise_for_error(response=response, payload=payload)
                return payload

    @staticmethod
    async def _safe_json(response: ClientResponse) -> dict[str, Any]:
        payload = await response.json(content_type=None)
        if isinstance(payload, dict):
            return payload
        raise RuntimeError("xRocket Pay returned invalid JSON payload.")

    @staticmethod
    def _raise_for_error(*, response: ClientResponse, payload: dict[str, Any]) -> None:
        if response.status < 400:
            return
        message = ""
        for key in ("message", "error", "detail"):
            value = payload.get(key)
            if value is not None:
                message = str(value).strip()
                if message:
                    break
        if not message:
            errors_value = payload.get("errors")
            if isinstance(errors_value, list) and errors_value:
                first_error = errors_value[0]
                if isinstance(first_error, dict):
                    prop = str(first_error.get("property", "")).strip()
                    text = str(first_error.get("error", "")).strip()
                    parts = [part for part in (prop, text) if part]
                    if parts:
                        message = ": ".join(parts)
        if not message:
            message = f"HTTP {response.status}"
        raise RuntimeError(f"xRocket Pay API error: {message}")

    @staticmethod
    def _extract_invoice(payload: dict[str, Any]) -> dict[str, Any]:
        if any(k in payload for k in ("id", "clientInvoiceId", "status", "links")):
            return payload

        raise RuntimeError("xRocket Pay did not return invoice payload.")

    @staticmethod
    def _extract_checkout_url(invoice: dict[str, Any]) -> str:
        links = invoice.get("links")
        if not isinstance(links, dict):
            raise RuntimeError("xRocket Pay did not return invoice checkout URL.")
        for key in ("telegramBotLink", "webLink"):
            value = links.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        raise RuntimeError("xRocket Pay did not return invoice checkout URL.")

    @staticmethod
    def _extract_status(invoice: dict[str, Any]) -> str:
        for key in ("status",):
            value = invoice.get(key)
            if value is not None:
                normalized = str(value).strip().lower()
                if normalized:
                    return normalized
        return "unknown"

    @staticmethod
    def _extract_string(value: Any) -> str | None:
        return extract_optional_string(value)

    @staticmethod
    def _format_amount_for_request(value: str) -> str:
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, TypeError) as error:
            raise RuntimeError("Invalid amount for xRocket Pay invoice.") from error
        if amount <= 0:
            raise RuntimeError("Amount for xRocket Pay invoice must be positive.")
        quantized = amount.quantize(Decimal("0.000000001"), rounding=ROUND_HALF_UP)
        return format(quantized, "f")
