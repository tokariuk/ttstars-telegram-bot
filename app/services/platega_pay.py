from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.services.parsing import extract_optional_string
from app.vendor.platega_sdk import Platega, PlategaAPIError, PlategaCallback

_FIAT_RATE_API_URL = "https://open.er-api.com/v6/latest/USD"
_FIAT_RATE_CACHE_TTL_SECONDS = 15 * 60
_PAID_STATUSES: set[str] = {"confirmed"}
_TERMINAL_FAILURE_STATUSES: set[str] = {
    "canceled",
    "chargebacked",
    "chargeback",
    "expired",
    "failed",
}


@dataclass(frozen=True, slots=True)
class PlategaInvoice:
    transaction_id: str
    payment_payload: str
    pay_url: str
    status: str
    amount_minor: int
    currency: str


@dataclass(frozen=True, slots=True)
class PlategaInvoiceStatus:
    is_paid: bool
    status: str
    transaction_id: str | None = None
    payment_payload: str | None = None


@dataclass(frozen=True, slots=True)
class PlategaWebhookEvent:
    transaction_id: str | None
    payment_payload: str | None
    status: str
    is_paid: bool
    is_terminal: bool


class PlategaPayService:
    def __init__(
        self,
        *,
        merchant_id: str | None,
        secret_key: str | None,
        base_url: str,
        currency: str,
        payment_method: int = Platega.METHOD_SBP_QR,
        success_url: str | None = None,
        fail_url: str | None = None,
        usd_to_currency_rate: str | None = None,
    ) -> None:
        self.merchant_id = (merchant_id or "").strip()
        self.secret_key = (secret_key or "").strip()
        self.base_url = (base_url or "https://app.platega.io").strip().rstrip("/")
        self.currency = ((currency or "RUB").strip().upper() or "RUB")
        self.payment_method = int(payment_method)
        self.success_url = (success_url or "").strip()
        self.fail_url = (fail_url or "").strip()
        self.usd_to_currency_rate = self._parse_optional_positive_decimal(
            usd_to_currency_rate,
            label="Platega USD rate",
        )
        self._rate_cache: dict[str, tuple[Decimal, float]] = {}

    @property
    def configured(self) -> bool:
        return bool(
            self.merchant_id
            and self.secret_key
            and self.base_url
            and self.payment_method > 0
        )

    async def create_invoice(
        self,
        *,
        amount_usd: str,
        payment_payload: str,
        description: str,
    ) -> PlategaInvoice:
        if not self.configured:
            raise RuntimeError("Platega service is not configured.")

        payload = payment_payload.strip()
        if not payload:
            raise RuntimeError("Platega payment payload is empty.")
        usd_amount = self._parse_positive_decimal(amount_usd, label="Platega amount")
        provider_amount = await self._convert_usd_to_provider_amount(usd_amount=usd_amount)
        amount_minor = self._to_minor_units(provider_amount)
        client = self._build_client()
        description_normalized = description.strip()[:250]

        try:
            response = await asyncio.to_thread(
                client.create_payment,
                float(provider_amount),
                self.currency,
                self.payment_method,
                description_normalized,
                self.success_url or None,
                self.fail_url or None,
                payload,
            )
        except PlategaAPIError as error:
            raise RuntimeError(f"Platega API error: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Platega request failed: {error}") from error

        transaction_id = self._extract_required_string(
            response.get("transactionId"),
            field_name="transactionId",
        )
        pay_url = self._extract_required_string(response.get("redirect"), field_name="redirect")
        status = self._normalize_status(response.get("status"))
        returned_payload = self._extract_optional_string(response.get("payload")) or payload
        return PlategaInvoice(
            transaction_id=transaction_id,
            payment_payload=returned_payload,
            pay_url=pay_url,
            status=status,
            amount_minor=amount_minor,
            currency=self.currency,
        )

    async def get_invoice_status(self, *, transaction_id: str) -> PlategaInvoiceStatus:
        if not self.configured:
            return PlategaInvoiceStatus(is_paid=False, status="unconfigured")
        normalized_id = transaction_id.strip()
        if not normalized_id:
            return PlategaInvoiceStatus(is_paid=False, status="transaction_missing")

        client = self._build_client()
        try:
            response = await asyncio.to_thread(client.get_payment_status, normalized_id)
        except PlategaAPIError as error:
            return PlategaInvoiceStatus(
                is_paid=False,
                status=f"api_error:{str(error).strip() or 'request_failed'}",
            )
        except Exception as error:
            return PlategaInvoiceStatus(
                is_paid=False,
                status=f"request_error:{str(error).strip() or 'request_failed'}",
            )

        status = self._normalize_status(response.get("status"))
        resolved_id = (
            self._extract_optional_string(response.get("id"))
            or self._extract_optional_string(response.get("transactionId"))
            or normalized_id
        )
        return PlategaInvoiceStatus(
            is_paid=status in _PAID_STATUSES,
            status=status,
            transaction_id=resolved_id,
            payment_payload=self._extract_optional_string(response.get("payload")),
        )

    def verify_webhook_signature(self, *, raw_body: bytes, headers: dict[str, str]) -> bool:
        if not self.configured:
            return False
        body_text = raw_body.decode("utf-8", errors="replace")
        callback = self._build_callback()
        return bool(callback.validate_raw(headers=headers, body=body_text))

    def parse_webhook_event(self, payload: Any) -> PlategaWebhookEvent | None:
        if not isinstance(payload, dict):
            return None
        status = self._normalize_status(payload.get("status"))
        if not status:
            return None
        transaction_id = (
            self._extract_optional_string(payload.get("id"))
            or self._extract_optional_string(payload.get("transactionId"))
        )
        payment_payload = self._extract_optional_string(payload.get("payload"))
        is_paid = status in _PAID_STATUSES
        is_terminal = bool(is_paid or status in _TERMINAL_FAILURE_STATUSES)
        return PlategaWebhookEvent(
            transaction_id=transaction_id,
            payment_payload=payment_payload,
            status=status,
            is_paid=is_paid,
            is_terminal=is_terminal,
        )

    async def _convert_usd_to_provider_amount(self, *, usd_amount: Decimal) -> Decimal:
        if self.currency in {"USD", "USDT"}:
            return usd_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        rate = await self._get_usd_to_currency_rate(currency=self.currency)
        converted = usd_amount * rate
        return converted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    async def _get_usd_to_currency_rate(self, *, currency: str) -> Decimal:
        normalized_currency = currency.strip().upper()
        if not normalized_currency:
            raise RuntimeError("Platega currency is empty.")
        if normalized_currency in {"USD", "USDT"}:
            return Decimal("1")
        if self.usd_to_currency_rate is not None:
            return self.usd_to_currency_rate

        now = time.monotonic()
        cached = self._rate_cache.get(normalized_currency)
        if cached is not None:
            cached_rate, cached_until = cached
            if now < cached_until:
                return cached_rate

        rate = await asyncio.to_thread(
            self._fetch_public_usd_to_currency_rate,
            normalized_currency,
        )
        self._rate_cache[normalized_currency] = (
            rate,
            now + _FIAT_RATE_CACHE_TTL_SECONDS,
        )
        return rate

    @staticmethod
    def _fetch_public_usd_to_currency_rate(currency: str) -> Decimal:
        request = Request(
            _FIAT_RATE_API_URL,
            headers={
                "Accept": "application/json",
                "User-Agent": "TTStars/1.0",
            },
            method="GET",
        )
        try:
            with urlopen(request, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            raise RuntimeError(f"Failed to fetch USD/{currency} rate.") from error

        if not isinstance(payload, dict) or payload.get("result") != "success":
            raise RuntimeError(f"USD/{currency} rate source returned an error.")
        rates = payload.get("rates")
        if not isinstance(rates, dict):
            raise RuntimeError(f"USD/{currency} rate source returned invalid payload.")
        return PlategaPayService._parse_positive_decimal(
            rates.get(currency),
            label=f"USD/{currency} rate",
        )

    def _build_client(self) -> Platega:
        client = Platega(
            merchant_id=self.merchant_id,
            secret=self.secret_key,
            timeout=30,
        )
        client.API_URL = self.base_url
        return client

    def _build_callback(self) -> PlategaCallback:
        return PlategaCallback(merchant_id=self.merchant_id, secret=self.secret_key)

    @staticmethod
    def _normalize_status(value: Any) -> str:
        if value is None:
            return "unknown"
        normalized = str(value).strip().lower()
        return normalized or "unknown"

    @staticmethod
    def _extract_required_string(value: Any, *, field_name: str) -> str:
        normalized = PlategaPayService._extract_optional_string(value)
        if normalized is None:
            raise RuntimeError(f"Platega did not return valid {field_name}.")
        return normalized

    @staticmethod
    def _extract_optional_string(value: Any) -> str | None:
        return extract_optional_string(value)

    @staticmethod
    def _parse_positive_decimal(value: Any, *, label: str) -> Decimal:
        try:
            parsed = Decimal(str(value))
        except (InvalidOperation, TypeError) as error:
            raise RuntimeError(f"{label} is invalid.") from error
        if parsed <= 0:
            raise RuntimeError(f"{label} must be positive.")
        return parsed

    @staticmethod
    def _parse_optional_positive_decimal(value: Any, *, label: str) -> Decimal | None:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return PlategaPayService._parse_positive_decimal(value, label=label)

    @staticmethod
    def _to_minor_units(value: Decimal) -> int:
        return int((value * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
