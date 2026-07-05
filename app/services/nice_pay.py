from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal, InvalidOperation
from time import monotonic
from typing import Any

from aiohttp import ClientResponse, ClientSession, ClientTimeout

from app.services.parsing import extract_optional_string

_ALLOWED_CURRENCIES: set[str] = {"USD", "EUR", "RUB", "UAH", "KZT"}
_CURRENCY_LIMITS_MINOR: dict[str, tuple[int, int]] = {
    # NicePay docs limits:
    # https://nicepay.io/docs/ru/merchant/limits.md
    "USD": (1_000, 99_000),
    "EUR": (1_000, 85_000),
    "RUB": (20_000, 8_500_000),
    "UAH": (10_000, 3_500_000),
    "KZT": (100_000, 41_000_000),
}
_H2H_STATUS_PAID = 5
_RATE_CACHE_TTL_SECONDS = 300.0


@dataclass(frozen=True, slots=True)
class NicePayInvoice:
    payment_id: str
    order_id: str
    pay_url: str
    status: str
    amount_minor: int
    currency: str
    expired_unix: int | None


@dataclass(frozen=True, slots=True)
class NicePayInvoiceStatus:
    is_paid: bool
    status: str


@dataclass(frozen=True, slots=True)
class NicePayWebhookEvent:
    result: str
    payment_id: str | None
    order_id: str | None
    is_paid: bool


class NicePayService:
    def __init__(
        self,
        *,
        merchant_id: str | None,
        secret_key: str | None,
        base_url: str,
        currency: str,
        method: str | None = None,
        success_url: str | None = None,
        fail_url: str | None = None,
    ) -> None:
        self.merchant_id = (merchant_id or "").strip()
        self.secret_key = (secret_key or "").strip()
        self.base_url = base_url.rstrip("/")
        normalized_currency = (currency or "UAH").strip().upper()
        self.currency = (
            normalized_currency if normalized_currency in _ALLOWED_CURRENCIES else "UAH"
        )
        self.method = (method or "").strip()
        self.success_url = (success_url or "").strip()
        self.fail_url = (fail_url or "").strip()
        self.timeout = ClientTimeout(total=20)
        self._usd_to_currency_rate_cache: dict[str, Decimal] = {}
        self._usd_to_currency_rate_cached_until: dict[str, float] = {}

    @property
    def configured(self) -> bool:
        return bool(self.merchant_id and self.secret_key and self.base_url)

    @staticmethod
    def amount_limits_minor(*, currency: str) -> tuple[int, int] | None:
        normalized_currency = currency.strip().upper()
        return _CURRENCY_LIMITS_MINOR.get(normalized_currency)

    async def min_usd_cents_for_currency(self, *, currency: str) -> int | None:
        resolved_currency = self._resolve_currency(currency)
        limits = self.amount_limits_minor(currency=resolved_currency)
        if limits is None:
            return None

        min_minor, _max_minor = limits
        if resolved_currency == "USD":
            return min_minor

        rate = await self._get_usd_to_currency_rate(currency=resolved_currency)
        if rate <= 0:
            raise RuntimeError(f"Invalid USD/{resolved_currency} rate.")

        estimated_cents = int(
            (Decimal(min_minor) / rate).quantize(Decimal("1"), rounding=ROUND_CEILING)
        )
        usd_cents = max(1, estimated_cents)
        converted_minor = await self.invoice_amount_minor_from_usd_cents(
            usd_cents=usd_cents,
            currency=resolved_currency,
        )
        while converted_minor < min_minor:
            usd_cents += 1
            converted_minor = await self.invoice_amount_minor_from_usd_cents(
                usd_cents=usd_cents,
                currency=resolved_currency,
            )
        return usd_cents

    def verify_webhook_signature(self, *, query_params: dict[str, str]) -> bool:
        if not self.secret_key:
            return False
        provided_hash_raw = query_params.get("hash")
        if not isinstance(provided_hash_raw, str):
            return False
        provided_hash = provided_hash_raw.strip().lower()
        if not provided_hash:
            return False

        payload = {key: value for key, value in query_params.items() if key != "hash"}
        expected_hash = self._build_signature(payload)
        return hmac.compare_digest(expected_hash, provided_hash)

    def parse_webhook_event(self, *, query_params: dict[str, str]) -> NicePayWebhookEvent | None:
        result_raw = query_params.get("result")
        if not isinstance(result_raw, str):
            return None
        result = result_raw.strip().lower()
        if not result:
            return None
        return NicePayWebhookEvent(
            result=result,
            payment_id=self._extract_string(query_params.get("payment_id")),
            order_id=self._extract_string(query_params.get("order_id")),
            is_paid=result == "success",
        )

    async def invoice_amount_minor_from_usd_cents(
        self,
        *,
        usd_cents: int,
        currency: str | None = None,
    ) -> int:
        if usd_cents <= 0:
            raise RuntimeError("NicePay amount must be positive.")

        resolved_currency = self._resolve_currency(currency)
        if resolved_currency == "USD":
            return usd_cents
        rate = await self._get_usd_to_currency_rate(currency=resolved_currency)
        usd_amount = Decimal(usd_cents) / Decimal("100")
        target_amount = (usd_amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return int((target_amount * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    async def create_invoice(
        self,
        *,
        amount_minor: int,
        order_id: str,
        customer: str,
        description: str,
        currency: str | None = None,
    ) -> NicePayInvoice:
        if not self.configured:
            raise RuntimeError("NicePay service is not configured.")

        normalized_order_id = order_id.strip()
        if not normalized_order_id:
            raise RuntimeError("NicePay order_id is empty.")
        normalized_customer = customer.strip()
        if not normalized_customer:
            raise RuntimeError("NicePay customer is empty.")
        if amount_minor <= 0:
            raise RuntimeError("NicePay amount must be positive.")

        resolved_currency = self._resolve_currency(currency)
        self._validate_amount_limits(amount_minor=amount_minor, currency=resolved_currency)
        payload: dict[str, Any] = {
            "merchant_id": self.merchant_id,
            "secret": self.secret_key,
            "order_id": normalized_order_id,
            # Docs use `customer`, older examples may still use `account`.
            "customer": normalized_customer,
            "account": normalized_customer,
            "amount": amount_minor,
            "currency": resolved_currency,
            "description": description[:150],
        }
        if self.method:
            payload["method"] = self.method
        if self.success_url:
            payload["success_url"] = self.success_url
        if self.fail_url:
            payload["fail_url"] = self.fail_url

        response = await self._request_json(
            method="POST",
            path="/public/api/payment",
            json=payload,
        )
        data = self._extract_success_data(response, context="create payment")
        payment_id = self._extract_required_string(data.get("payment_id"), field_name="payment_id")
        pay_url = self._extract_required_string(data.get("link"), field_name="link")
        expired_unix = self._extract_int(data.get("expired"))
        amount_from_provider = self._extract_int(data.get("amount")) or amount_minor
        currency_from_provider = self._extract_string(data.get("currency")) or resolved_currency
        return NicePayInvoice(
            payment_id=payment_id,
            order_id=normalized_order_id,
            pay_url=pay_url,
            status="pending",
            amount_minor=amount_from_provider,
            currency=currency_from_provider.upper(),
            expired_unix=expired_unix,
        )

    async def get_invoice_status(self, *, payment_id: str) -> NicePayInvoiceStatus:
        if not self.configured:
            return NicePayInvoiceStatus(is_paid=False, status="unconfigured")

        normalized_payment_id = payment_id.strip()
        if not normalized_payment_id:
            return NicePayInvoiceStatus(is_paid=False, status="payment_missing")

        payload = {
            "merchant_id": self.merchant_id,
            "secret": self.secret_key,
            "payment": normalized_payment_id,
        }
        response = await self._request_json(
            method="POST",
            path="/public/api/h2hPaymentInfo",
            json=payload,
        )
        status_raw = self._extract_string(response.get("status"))
        if status_raw == "error":
            return NicePayInvoiceStatus(
                is_paid=False,
                status=self._extract_error_message(response) or "error",
            )

        data = response.get("data")
        if not isinstance(data, dict):
            return NicePayInvoiceStatus(is_paid=False, status="invalid_status_payload")

        h2h_status = self._extract_int(data.get("status"))
        if h2h_status is None:
            return NicePayInvoiceStatus(is_paid=False, status="h2h_status_unknown")
        return NicePayInvoiceStatus(
            is_paid=h2h_status == _H2H_STATUS_PAID,
            status=f"h2h_status_{h2h_status}",
        )

    async def _get_usd_to_currency_rate(self, *, currency: str) -> Decimal:
        if currency == "USD":
            return Decimal("1")

        now = monotonic()
        cached_rate = self._usd_to_currency_rate_cache.get(currency)
        cached_until = self._usd_to_currency_rate_cached_until.get(currency, 0.0)
        if cached_rate is not None and now < cached_until:
            return cached_rate

        if currency == "UAH":
            usd_to_uah_rate = await self._get_nbu_rate_per_unit(currency="USD")
            self._usd_to_currency_rate_cache[currency] = usd_to_uah_rate
            self._usd_to_currency_rate_cached_until[currency] = now + _RATE_CACHE_TTL_SECONDS
            return usd_to_uah_rate

        usd_to_uah_rate = await self._get_nbu_rate_per_unit(currency="USD")
        target_to_uah_rate = await self._get_nbu_rate_per_unit(currency=currency)
        if target_to_uah_rate <= 0:
            raise RuntimeError(f"Invalid NBU rate for {currency}.")
        usd_to_target_rate = (usd_to_uah_rate / target_to_uah_rate).quantize(
            Decimal("0.000001"),
            rounding=ROUND_HALF_UP,
        )
        if usd_to_target_rate <= 0:
            raise RuntimeError(f"USD/{currency} rate must be positive.")

        self._usd_to_currency_rate_cache[currency] = usd_to_target_rate
        self._usd_to_currency_rate_cached_until[currency] = now + _RATE_CACHE_TTL_SECONDS
        return usd_to_target_rate

    async def _get_nbu_rate_per_unit(self, *, currency: str) -> Decimal:
        normalized_currency = currency.strip().upper()
        if normalized_currency == "UAH":
            return Decimal("1")

        today = datetime.now(tz=UTC).date()
        start_date = (today - timedelta(days=7)).strftime("%Y%m%d")
        end_date = today.strftime("%Y%m%d")
        payload = await self._request_json(
            method="GET",
            path="/NBU_Exchange/exchange_site",
            params={
                "start": start_date,
                "end": end_date,
                "valcode": normalized_currency,
                "sort": "exchangedate",
                "order": "desc",
                "json": "",
            },
            absolute_url="https://bank.gov.ua",
        )
        data_list = payload.get("data_list")
        if not isinstance(data_list, list) or not data_list:
            payload = await self._request_json(
                method="GET",
                path="/NBU_Exchange/exchange_site",
                params={
                    "valcode": normalized_currency,
                    "sort": "exchangedate",
                    "order": "desc",
                    "json": "",
                },
                absolute_url="https://bank.gov.ua",
            )
            data_list = payload.get("data_list")
        if not isinstance(data_list, list) or not data_list:
            raise RuntimeError(f"Failed to fetch NBU rate for {normalized_currency}.")

        latest_item = self._select_latest_nbu_item(data_list)
        if latest_item is None:
            raise RuntimeError(f"Failed to parse NBU rate for {normalized_currency}.")
        rate_per_unit_raw = latest_item.get("rate_per_unit")
        rate_raw = latest_item.get("rate")
        try:
            if rate_per_unit_raw is not None:
                rate = Decimal(str(rate_per_unit_raw))
            else:
                rate = Decimal(str(rate_raw))
        except (InvalidOperation, TypeError) as error:
            raise RuntimeError(f"NBU rate for {normalized_currency} is invalid.") from error
        if rate <= 0:
            raise RuntimeError(f"NBU rate for {normalized_currency} must be positive.")
        return rate

    @staticmethod
    def _select_latest_nbu_item(data_list: list[Any]) -> dict[str, Any] | None:
        latest_item: dict[str, Any] | None = None
        latest_date: date | None = None

        for item in data_list:
            if not isinstance(item, dict):
                continue
            exchangedate = item.get("exchangedate")
            parsed_date = None
            if isinstance(exchangedate, str):
                parsed_date = NicePayService._parse_nbu_date(exchangedate.strip())

            if parsed_date is not None:
                if latest_date is None or parsed_date > latest_date:
                    latest_date = parsed_date
                    latest_item = item
                continue

            if latest_item is None:
                latest_item = item

        return latest_item

    @staticmethod
    def _parse_nbu_date(value: str) -> date | None:
        day_str, separator, remainder = value.partition(".")
        month_str, separator2, year_str = remainder.partition(".")
        if separator != "." or separator2 != ".":
            return None
        try:
            return date(int(year_str), int(month_str), int(day_str))
        except ValueError:
            return None

    def _resolve_currency(self, currency: str | None) -> str:
        if currency is None:
            return self.currency
        normalized_currency = currency.strip().upper()
        if normalized_currency not in _ALLOWED_CURRENCIES:
            raise RuntimeError(f"NicePay currency {normalized_currency} is not supported.")
        return normalized_currency

    async def _request_json(
        self,
        *,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
        absolute_url: str | None = None,
    ) -> dict[str, Any]:
        base = (absolute_url or self.base_url).rstrip("/")
        url = f"{base}{path}"
        async with ClientSession() as session:
            async with session.request(
                method.upper(),
                url,
                json=json,
                params=params,
                timeout=self.timeout,
            ) as response:
                payload = await self._safe_json(response=response)
                self._raise_for_http_error(response=response, payload=payload)
                return payload

    @staticmethod
    async def _safe_json(*, response: ClientResponse) -> dict[str, Any]:
        payload = await response.json(content_type=None)
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, list):
            # NBU API returns list; normalize it into dict payload.
            return {"data_list": payload}
        raise RuntimeError("NicePay returned invalid JSON payload.")

    @staticmethod
    def _raise_for_http_error(*, response: ClientResponse, payload: dict[str, Any]) -> None:
        if response.status < 400:
            return
        message = NicePayService._extract_error_message(payload) or f"HTTP {response.status}"
        raise RuntimeError(f"NicePay API error: {message}")

    @staticmethod
    def _extract_success_data(payload: dict[str, Any], *, context: str) -> dict[str, Any]:
        status = NicePayService._extract_string(payload.get("status"))
        if status != "success":
            message = NicePayService._extract_error_message(payload) or "Unknown error"
            raise RuntimeError(f"NicePay {context} failed: {message}")
        data = payload.get("data")
        if isinstance(data, dict):
            return data
        raise RuntimeError(f"NicePay {context} returned invalid payload.")

    @staticmethod
    def _extract_error_message(payload: dict[str, Any]) -> str | None:
        data = payload.get("data")
        if isinstance(data, dict):
            message = NicePayService._extract_string(data.get("message"))
            if message:
                return message
        return NicePayService._extract_string(payload.get("message"))

    @staticmethod
    def _extract_string(value: Any) -> str | None:
        return extract_optional_string(value)

    @staticmethod
    def _extract_required_string(value: Any, *, field_name: str) -> str:
        normalized = NicePayService._extract_string(value)
        if normalized is None:
            raise RuntimeError(f"NicePay did not return valid {field_name}.")
        return normalized

    @staticmethod
    def _extract_int(value: Any) -> int | None:
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
        return None

    def _build_signature(self, params: dict[str, str]) -> str:
        values: list[str] = []
        for key in sorted(params):
            values.append(str(params[key]))
        values.append(self.secret_key)
        hash_source = "{np}".join(values)
        return hashlib.sha256(hash_source.encode("utf-8")).hexdigest()

    @staticmethod
    def _validate_amount_limits(*, amount_minor: int, currency: str) -> None:
        limits = _CURRENCY_LIMITS_MINOR.get(currency)
        if limits is None:
            return
        min_minor, max_minor = limits
        if amount_minor < min_minor or amount_minor > max_minor:
            min_value = Decimal(min_minor) / Decimal("100")
            max_value = Decimal(max_minor) / Decimal("100")
            raise RuntimeError(
                f"NicePay amount is out of limits for {currency}: "
                f"{min_value}..{max_value} {currency}."
            )
