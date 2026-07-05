from __future__ import annotations

import base64
import hashlib
import hmac
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from json import dumps
from typing import Any

from aiohttp import ClientResponse, ClientSession, ClientTimeout

from app.services.parsing import extract_optional_string

_PAID_STATUSES: set[str] = {"paid", "paid_over"}


@dataclass(frozen=True, slots=True)
class HeleketInvoice:
    invoice_uuid: str
    order_id: str
    pay_url: str
    status: str


@dataclass(frozen=True, slots=True)
class HeleketInvoiceStatus:
    is_paid: bool
    status: str
    invoice_uuid: str | None = None


@dataclass(frozen=True, slots=True)
class HeleketWebhookEvent:
    invoice_type: str
    invoice_uuid: str | None
    order_id: str | None
    status: str
    is_paid: bool
    is_final: bool


class HeleketPayService:
    def __init__(
        self,
        *,
        merchant_id: str | None,
        api_key: str | None,
        base_url: str,
        currency: str,
        to_currency: str | None = None,
        network: str | None = None,
        return_url: str | None = None,
        success_url: str | None = None,
        callback_url: str | None = None,
        lifetime_seconds: int = 3600,
        is_payment_multiple: bool = True,
        subtract_percent: int = 0,
    ) -> None:
        self.merchant_id = (merchant_id or "").strip()
        self.api_key = (api_key or "").strip()
        self.base_url = (base_url or "https://api.heleket.com").strip().rstrip("/")
        normalized_currency = (currency or "USD").strip().upper()
        self.currency = normalized_currency or "USD"
        self.to_currency = self._normalized_optional_upper(to_currency)
        self.network = self._normalized_optional(network)
        self.return_url = self._normalized_optional(return_url)
        self.success_url = self._normalized_optional(success_url)
        self.callback_url = self._normalized_optional(callback_url)
        self.lifetime_seconds = max(300, min(43_200, int(lifetime_seconds)))
        self.is_payment_multiple = bool(is_payment_multiple)
        self.subtract_percent = max(0, min(100, int(subtract_percent)))
        self.timeout = ClientTimeout(total=20)

    @property
    def configured(self) -> bool:
        return bool(self.merchant_id and self.api_key and self.base_url)

    async def create_invoice(
        self,
        *,
        amount: str,
        order_id: str,
        description: str,
        callback_url: str | None = None,
    ) -> HeleketInvoice:
        if not self.configured:
            raise RuntimeError("Heleket Pay service is not configured.")

        normalized_order_id = order_id.strip()
        if not normalized_order_id:
            raise RuntimeError("Heleket order_id is empty.")

        payload: dict[str, Any] = {
            "amount": self._format_amount_for_request(amount),
            "currency": self.currency,
            "order_id": normalized_order_id,
            "is_payment_multiple": self.is_payment_multiple,
            "lifetime": self.lifetime_seconds,
            "subtract": self.subtract_percent,
            "additional_data": description[:255],
        }
        if self.network:
            payload["network"] = self.network
        if self.to_currency:
            payload["to_currency"] = self.to_currency
        if self.return_url:
            payload["url_return"] = self.return_url
        if self.success_url:
            payload["url_success"] = self.success_url

        resolved_callback_url = self._normalized_optional(callback_url) or self.callback_url
        if resolved_callback_url:
            payload["url_callback"] = resolved_callback_url

        response = await self._request_json(
            method="POST",
            path="/v1/payment",
            json_payload=payload,
        )
        result = self._extract_result(response, context="create payment")
        invoice_uuid = self._extract_required_string(result.get("uuid"), field_name="uuid")
        pay_url = self._extract_required_string(result.get("url"), field_name="url")
        status = self._normalize_status(result.get("status") or result.get("payment_status"))
        result_order_id = self._extract_string(result.get("order_id")) or normalized_order_id
        return HeleketInvoice(
            invoice_uuid=invoice_uuid,
            order_id=result_order_id,
            pay_url=pay_url,
            status=status,
        )

    async def get_invoice_status(
        self,
        *,
        invoice_uuid: str | None = None,
        order_id: str | None = None,
    ) -> HeleketInvoiceStatus:
        if not self.configured:
            return HeleketInvoiceStatus(is_paid=False, status="unconfigured")

        normalized_uuid = self._normalized_optional(invoice_uuid)
        normalized_order_id = self._normalized_optional(order_id)
        if normalized_uuid is None and normalized_order_id is None:
            return HeleketInvoiceStatus(is_paid=False, status="invoice_missing")

        payload: dict[str, Any] = {}
        if normalized_uuid is not None:
            payload["uuid"] = normalized_uuid
        if normalized_order_id is not None:
            payload["order_id"] = normalized_order_id

        response = await self._request_json(
            method="POST",
            path="/v1/payment/info",
            json_payload=payload,
        )
        result = self._extract_result(response, context="check payment")
        status = self._normalize_status(result.get("status") or result.get("payment_status"))
        resolved_uuid = self._extract_string(result.get("uuid")) or normalized_uuid
        return HeleketInvoiceStatus(
            is_paid=status in _PAID_STATUSES,
            status=status,
            invoice_uuid=resolved_uuid,
        )

    def verify_webhook_signature(self, *, payload: dict[str, Any]) -> bool:
        if not self.api_key:
            return False
        sign_raw = payload.get("sign")
        if not isinstance(sign_raw, str):
            return False
        sign = sign_raw.strip().lower()
        if not sign:
            return False

        payload_without_sign = dict(payload)
        payload_without_sign.pop("sign", None)
        body = self._serialize_json(payload_without_sign, escape_slashes=True)
        expected_sign = self._build_signature(body)
        return hmac.compare_digest(expected_sign, sign)

    def parse_webhook_event(self, payload: Any) -> HeleketWebhookEvent | None:
        if not isinstance(payload, dict):
            return None

        invoice_type = self._normalize_status(payload.get("type"))
        status = self._normalize_status(payload.get("status") or payload.get("payment_status"))
        is_final_raw = payload.get("is_final")
        if isinstance(is_final_raw, bool):
            is_final = is_final_raw
        elif isinstance(is_final_raw, int):
            is_final = is_final_raw != 0
        elif isinstance(is_final_raw, str):
            is_final = is_final_raw.strip().lower() in {"1", "true", "yes"}
        else:
            is_final = False

        return HeleketWebhookEvent(
            invoice_type=invoice_type,
            invoice_uuid=self._extract_string(payload.get("uuid")),
            order_id=self._extract_string(payload.get("order_id")),
            status=status,
            is_paid=status in _PAID_STATUSES,
            is_final=is_final,
        )

    async def _request_json(
        self,
        *,
        method: str,
        path: str,
        json_payload: dict[str, Any],
    ) -> dict[str, Any]:
        body = self._serialize_json(json_payload, escape_slashes=True)
        headers = {
            "merchant": self.merchant_id,
            "sign": self._build_signature(body),
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}{path}"
        async with ClientSession() as session:
            async with session.request(
                method.upper(),
                url,
                data=body.encode("utf-8"),
                headers=headers,
                timeout=self.timeout,
            ) as response:
                payload = await self._safe_json(response=response)
                self._raise_for_http_error(response=response, payload=payload)
                return payload

    def _build_signature(self, body: str) -> str:
        encoded_body = base64.b64encode(body.encode("utf-8")).decode("ascii")
        hash_source = f"{encoded_body}{self.api_key}".encode("utf-8")
        return hashlib.md5(hash_source).hexdigest()

    @staticmethod
    def _serialize_json(payload: dict[str, Any], *, escape_slashes: bool) -> str:
        serialized = dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return serialized.replace("/", "\\/") if escape_slashes else serialized

    @staticmethod
    async def _safe_json(*, response: ClientResponse) -> dict[str, Any]:
        payload = await response.json(content_type=None)
        if isinstance(payload, dict):
            return payload
        raise RuntimeError("Heleket API returned invalid JSON payload.")

    @staticmethod
    def _raise_for_http_error(*, response: ClientResponse, payload: dict[str, Any]) -> None:
        if response.status < 400:
            return
        message = HeleketPayService._extract_error_message(payload) or f"HTTP {response.status}"
        raise RuntimeError(f"Heleket API error: {message}")

    @staticmethod
    def _extract_result(payload: dict[str, Any], *, context: str) -> dict[str, Any]:
        state_raw = payload.get("state")
        state = 0
        if isinstance(state_raw, int):
            state = state_raw
        elif isinstance(state_raw, str):
            normalized_state = state_raw.strip()
            if normalized_state:
                try:
                    state = int(normalized_state)
                except ValueError:
                    state = 0
        if state != 0:
            message = HeleketPayService._extract_error_message(payload) or "Unknown error"
            raise RuntimeError(f"Heleket {context} failed: {message}")

        result = payload.get("result")
        if isinstance(result, dict):
            return result
        raise RuntimeError(f"Heleket {context} returned invalid payload.")

    @staticmethod
    def _extract_error_message(payload: dict[str, Any]) -> str | None:
        message = payload.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()

        errors = payload.get("errors")
        if isinstance(errors, dict):
            first_key = next(iter(errors.keys()), None)
            if first_key is None:
                return None
            first_value = errors[first_key]
            if isinstance(first_value, list) and first_value:
                return f"{first_key}: {first_value[0]}"
            return f"{first_key}: {first_value}"
        return None

    @staticmethod
    def _extract_string(value: Any) -> str | None:
        return extract_optional_string(value)

    @staticmethod
    def _extract_required_string(value: Any, *, field_name: str) -> str:
        normalized = HeleketPayService._extract_string(value)
        if normalized is None:
            raise RuntimeError(f"Heleket did not return valid {field_name}.")
        return normalized

    @staticmethod
    def _normalize_status(value: Any) -> str:
        if value is None:
            return "unknown"
        normalized = str(value).strip().lower()
        return normalized or "unknown"

    @staticmethod
    def _normalized_optional(value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @staticmethod
    def _normalized_optional_upper(value: str | None) -> str | None:
        normalized = HeleketPayService._normalized_optional(value)
        return normalized.upper() if normalized is not None else None

    @staticmethod
    def _format_amount_for_request(value: str) -> str:
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, TypeError) as error:
            raise RuntimeError("Invalid amount for Heleket invoice.") from error
        if amount <= 0:
            raise RuntimeError("Amount for Heleket invoice must be positive.")
        quantized = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return format(quantized, "f")
