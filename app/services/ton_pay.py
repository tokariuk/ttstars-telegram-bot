from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, ROUND_UP, Decimal, InvalidOperation
from typing import Any
from urllib.parse import quote

from aiohttp import ClientResponse, ClientSession, ClientTimeout

from app.services.parsing import extract_optional_string

_NANOTON = Decimal("1000000000")
logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class TonPayInvoice:
    payment_token: str
    pay_url: str
    invoice_id: str
    expected_amount_nano: int
    expected_amount_ton: str
    usd_per_ton: str
    status: str = "pending"


@dataclass(frozen=True, slots=True)
class TonPayPaymentStatus:
    is_paid: bool
    status: str
    expected_amount_nano: int
    paid_amount_nano: int
    remaining_amount_nano: int
    last_transaction_at: int | None = None
    payment_link: str | None = None
    pay_to_address: str | None = None


class TonPayService:
    def __init__(
        self,
        *,
        tonapi_base_url: str = "https://tonapi.io",
        tonapi_api_key: str | None = None,
        invoice_api_key: str | None = None,
        invoice_base_url: str = "https://tonconsole.com",
        invoice_lifetime_seconds: int = 1800,
        invoice_currency: str = "TON",
        invoice_status_cache_ttl_seconds: int = 5,
        invoice_tx_scan_limit: int = 50,
        rate_cache_ttl_seconds: int = 30,
    ) -> None:
        self.tonapi_base_url = (
            (tonapi_base_url or "https://tonapi.io").strip().rstrip("/")
        )
        self.tonapi_api_key = (tonapi_api_key or "").strip()
        self.invoice_api_key = (invoice_api_key or "").strip()
        self.invoice_base_url = (
            (invoice_base_url or "https://tonconsole.com").strip().rstrip("/")
        )
        self.invoice_lifetime_seconds = max(60, int(invoice_lifetime_seconds))
        self.invoice_currency = ((invoice_currency or "TON").strip().upper() or "TON")
        self.invoice_status_cache_ttl_seconds = max(5, int(invoice_status_cache_ttl_seconds))
        self.invoice_tx_scan_limit = min(200, max(10, int(invoice_tx_scan_limit)))
        self.rate_cache_ttl_seconds = max(3, int(rate_cache_ttl_seconds))
        self._rate_cache_value: Decimal | None = None
        self._rate_cache_expires_at: float = 0.0
        self.timeout = ClientTimeout(total=20)
        self._http_session: ClientSession | None = None
        self._http_session_lock = asyncio.Lock()
        self._invoice_status_cache: dict[str, tuple[float, TonPayPaymentStatus]] = {}

    @property
    def configured(self) -> bool:
        return bool(self.invoice_api_key and self.invoice_base_url)

    async def create_invoice(
        self,
        *,
        order_id: int,
        payment_token: str,
        amount_usd: str,
    ) -> TonPayInvoice:
        if not self.configured:
            raise RuntimeError("TON Pay invoice service is not configured.")

        usd_amount = self._parse_positive_decimal(amount_usd, label="TON checkout amount")
        usd_per_ton = await self.get_ton_rate_usd()
        if usd_per_ton <= 0:
            raise RuntimeError("TON/USD rate is invalid.")

        expected_amount_nano = self._usd_to_nano_ton(
            usd_amount=usd_amount,
            usd_per_ton=usd_per_ton,
        )
        response = await self._request_tonconsole_json(
            method="POST",
            path="/api/v1/services/invoices/invoice",
            json_body={
                "amount": str(expected_amount_nano),
                "life_time": self.invoice_lifetime_seconds,
                "currency": self.invoice_currency,
                "description": payment_token,
            },
        )
        invoice_id = self._extract_required_string(response.get("id"), field_name="id")
        payment_link = self._extract_required_string(
            response.get("payment_link"),
            field_name="payment_link",
        )
        status = self._extract_optional_string(response.get("status")) or "pending"
        return TonPayInvoice(
            payment_token=payment_token,
            pay_url=payment_link,
            invoice_id=invoice_id,
            expected_amount_nano=expected_amount_nano,
            expected_amount_ton=self.nano_to_ton_text(expected_amount_nano),
            usd_per_ton=self._format_decimal(usd_per_ton, precision="0.000001"),
            status=status.lower(),
        )

    async def get_invoice_status(
        self,
        *,
        invoice_id: str,
        expected_amount_nano: int | None = None,
        use_cache: bool = True,
    ) -> TonPayPaymentStatus:
        normalized_invoice_id = invoice_id.strip()
        expected_nano = max(0, int(expected_amount_nano or 0))
        if not normalized_invoice_id:
            return TonPayPaymentStatus(
                is_paid=False,
                status="invoice_missing",
                expected_amount_nano=expected_nano,
                paid_amount_nano=0,
                remaining_amount_nano=expected_nano,
            )
        if not self.configured:
            return TonPayPaymentStatus(
                is_paid=False,
                status="invoice_unconfigured",
                expected_amount_nano=expected_nano,
                paid_amount_nano=0,
                remaining_amount_nano=expected_nano,
            )

        now = time.monotonic()
        if use_cache:
            cached = self._invoice_status_cache.get(normalized_invoice_id)
            if cached is not None and now < cached[0]:
                return cached[1]

        try:
            payload = await self._request_tonconsole_json(
                method="GET",
                path=f"/api/v1/services/invoices/{quote(normalized_invoice_id, safe='')}",
            )
        except RuntimeError as error:
            if "no rows in result set" not in str(error).lower():
                raise
            result = TonPayPaymentStatus(
                is_paid=False,
                status="invoice_not_found",
                expected_amount_nano=expected_nano,
                paid_amount_nano=0,
                remaining_amount_nano=expected_nano,
            )
            self._invoice_status_cache.pop(normalized_invoice_id, None)
            return result
        status = (
            self._extract_optional_string(payload.get("status")) or "unknown"
        ).lower()
        amount_nano = self._extract_int(payload.get("amount")) or expected_nano
        amount_nano = max(0, int(amount_nano))
        overpayment_nano = max(0, int(self._extract_int(payload.get("overpayment")) or 0))
        is_paid = status == "paid"
        paid_amount_nano = amount_nano + overpayment_nano if is_paid else 0
        remaining_nano = 0 if is_paid else max(0, amount_nano - paid_amount_nano)
        pay_to_address = self._extract_optional_string(payload.get("pay_to_address"))
        payment_link = self._extract_optional_string(payload.get("payment_link"))
        result = TonPayPaymentStatus(
            is_paid=is_paid,
            status=status,
            expected_amount_nano=amount_nano,
            paid_amount_nano=paid_amount_nano,
            remaining_amount_nano=remaining_nano,
            last_transaction_at=self._extract_int(payload.get("date_change")),
            payment_link=payment_link,
            pay_to_address=pay_to_address,
        )
        if not is_paid and pay_to_address is not None and amount_nano > 0:
            chain_result = await self._get_invoice_chain_status(
                invoice_id=normalized_invoice_id,
                pay_to_address=pay_to_address,
                expected_amount_nano=amount_nano,
                payment_link=payment_link,
            )
            if chain_result is not None:
                result = chain_result
        if use_cache and not result.is_paid and result.status not in {
            "paid",
            "paid_chain",
            "cancelled",
            "expired",
        }:
            self._invoice_status_cache[normalized_invoice_id] = (
                now + self.invoice_status_cache_ttl_seconds,
                result,
            )
        else:
            self._invoice_status_cache.pop(normalized_invoice_id, None)
        return result

    async def _get_invoice_chain_status(
        self,
        *,
        invoice_id: str,
        pay_to_address: str,
        expected_amount_nano: int,
        payment_link: str | None,
    ) -> TonPayPaymentStatus | None:
        try:
            payload = await self._request_tonapi_json(
                method="GET",
                path=(
                    "/v2/blockchain/accounts/"
                    f"{quote(pay_to_address.strip(), safe='')}/transactions"
                ),
                params={"limit": str(self.invoice_tx_scan_limit)},
            )
        except Exception as error:
            logger.warning(
                "TON chain invoice check failed: invoice_id=%s error=%s",
                invoice_id,
                error,
            )
            return None

        transactions = payload.get("transactions")
        if not isinstance(transactions, list):
            return None

        paid_amount_nano = 0
        last_transaction_at: int | None = None
        for transaction in transactions:
            if not isinstance(transaction, dict):
                continue
            payment = self._extract_invoice_transaction_payment(
                transaction=transaction,
                invoice_id=invoice_id,
                pay_to_address=pay_to_address,
            )
            if payment is None:
                continue
            amount_nano, paid_at = payment
            paid_amount_nano += amount_nano
            if paid_at is not None:
                last_transaction_at = max(last_transaction_at or 0, paid_at)

        if paid_amount_nano <= 0:
            return None

        expected_nano = max(0, int(expected_amount_nano))
        remaining_nano = max(0, expected_nano - paid_amount_nano)
        is_paid = expected_nano > 0 and paid_amount_nano >= expected_nano
        return TonPayPaymentStatus(
            is_paid=is_paid,
            status="paid_chain" if is_paid else "underpaid_chain",
            expected_amount_nano=expected_nano,
            paid_amount_nano=paid_amount_nano,
            remaining_amount_nano=remaining_nano,
            last_transaction_at=last_transaction_at,
            payment_link=payment_link,
            pay_to_address=pay_to_address,
        )

    def _extract_invoice_transaction_payment(
        self,
        *,
        transaction: dict[str, Any],
        invoice_id: str,
        pay_to_address: str,
    ) -> tuple[int, int | None] | None:
        in_msg = transaction.get("in_msg")
        if not isinstance(in_msg, dict):
            return None
        amount_nano = self._extract_message_amount_nano(in_msg.get("value"))
        if amount_nano <= 0:
            return None
        destination = self._extract_message_address(
            in_msg.get("destination") or in_msg.get("dest")
        )
        if not self._addresses_match(destination, pay_to_address):
            return None
        comment = self._extract_message_comment(in_msg)
        if comment != invoice_id:
            return None
        paid_at = (
            self._extract_int(transaction.get("utime"))
            or self._extract_int(in_msg.get("created_at"))
        )
        return amount_nano, paid_at

    @classmethod
    def _extract_message_amount_nano(cls, value: Any) -> int:
        amount = cls._extract_int(value)
        if amount is not None:
            return max(0, amount)
        if isinstance(value, dict):
            grams = cls._extract_int(value.get("grams"))
            if grams is not None:
                return max(0, grams)
        return 0

    @staticmethod
    def _extract_message_address(value: Any) -> str | None:
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None
        if isinstance(value, dict):
            address = value.get("address")
            if isinstance(address, str):
                normalized = address.strip()
                return normalized or None
        return None

    @staticmethod
    def _addresses_match(left: str | None, right: str | None) -> bool:
        if left is None or right is None:
            return False
        return left.strip().lower() == right.strip().lower()

    @classmethod
    def _extract_message_comment(cls, message: dict[str, Any]) -> str | None:
        decoded_body = message.get("decoded_body")
        comment = cls._find_text_value(decoded_body)
        if comment is not None:
            return comment.strip()
        body = message.get("body")
        comment = cls._find_text_value(body)
        if comment is not None:
            return comment.strip()
        return None

    @classmethod
    def _find_text_value(cls, value: Any) -> str | None:
        if isinstance(value, dict):
            text = value.get("text")
            if isinstance(text, str) and text.strip():
                return text
            for nested in value.values():
                result = cls._find_text_value(nested)
                if result is not None:
                    return result
        if isinstance(value, list):
            for nested in value:
                result = cls._find_text_value(nested)
                if result is not None:
                    return result
        return None

    def clear_invoice_status_cache(self, *, invoice_id: str | None) -> None:
        normalized_invoice_id = (invoice_id or "").strip()
        if normalized_invoice_id:
            self._invoice_status_cache.pop(normalized_invoice_id, None)

    async def get_ton_rate_usd(self) -> Decimal:
        now = time.monotonic()
        if self._rate_cache_value is not None and now < self._rate_cache_expires_at:
            return self._rate_cache_value
        payload = await self._request_tonapi_json(
            method="GET",
            path="/v2/rates",
            params={"tokens": "ton", "currencies": "usd"},
        )
        rate_raw: Any = None
        rates = payload.get("rates")
        if isinstance(rates, dict):
            ton = rates.get("TON")
            if isinstance(ton, dict):
                prices = ton.get("prices")
                if isinstance(prices, dict):
                    rate_raw = prices.get("USD")
        rate = self._parse_positive_decimal(rate_raw, label="TON/USD rate")
        self._rate_cache_value = rate
        self._rate_cache_expires_at = now + float(self.rate_cache_ttl_seconds)
        return rate

    @staticmethod
    def nano_to_ton_text(value: int) -> str:
        amount = (Decimal(max(0, int(value))) / _NANOTON).quantize(
            Decimal("0.000000001"),
            rounding=ROUND_HALF_UP,
        )
        text = format(amount, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text or "0"

    @staticmethod
    def _usd_to_nano_ton(*, usd_amount: Decimal, usd_per_ton: Decimal) -> int:
        amount_ton = (usd_amount / usd_per_ton).quantize(
            Decimal("0.000000001"),
            rounding=ROUND_UP,
        )
        amount_nano = int(
            (amount_ton * _NANOTON).quantize(
                Decimal("1"),
                rounding=ROUND_UP,
            )
        )
        if amount_nano <= 0:
            raise RuntimeError("Calculated TON amount is invalid.")
        return amount_nano

    async def _request_tonapi_json(
        self,
        *,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.tonapi_base_url}{path}"
        headers: dict[str, str] = {}
        if self.tonapi_api_key:
            headers["Authorization"] = f"Bearer {self.tonapi_api_key}"
        session = await self._get_http_session()
        async with session.request(
            method.upper(),
            url,
            params=params,
            headers=headers or None,
            timeout=self.timeout,
        ) as response:
            payload = await self._safe_json(response=response)
            self._raise_for_http_error(response=response, payload=payload)
            return payload

    async def _request_tonconsole_json(
        self,
        *,
        method: str,
        path: str,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.invoice_base_url}{path}"
        session = await self._get_http_session()
        async with session.request(
            method.upper(),
            url,
            json=json_body,
            headers={
                "Authorization": f"Bearer {self.invoice_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=self.timeout,
        ) as response:
            payload = await self._safe_json(response=response)
            self._raise_for_http_error(response=response, payload=payload)
            return payload

    async def close(self) -> None:
        async with self._http_session_lock:
            if self._http_session is not None and not self._http_session.closed:
                await self._http_session.close()
            self._http_session = None

    async def _get_http_session(self) -> ClientSession:
        session = self._http_session
        if session is not None and not session.closed:
            return session
        async with self._http_session_lock:
            session = self._http_session
            if session is not None and not session.closed:
                return session
            self._http_session = ClientSession(timeout=self.timeout)
            return self._http_session

    @staticmethod
    async def _safe_json(*, response: ClientResponse) -> dict[str, Any]:
        payload = await response.json(content_type=None)
        if isinstance(payload, dict):
            return payload
        raise RuntimeError("TON API returned invalid JSON payload.")

    @staticmethod
    def _raise_for_http_error(*, response: ClientResponse, payload: dict[str, Any]) -> None:
        if response.status < 400:
            return
        message = ""
        error_value = payload.get("error")
        if isinstance(error_value, str):
            message = error_value.strip()
        if not message:
            message_value = payload.get("message")
            if isinstance(message_value, str):
                message = message_value.strip()
        if not message:
            message = f"HTTP {response.status}"
        raise RuntimeError(f"TON API error: {message}")

    @staticmethod
    def _extract_int(value: Any) -> int | None:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            raw = value.strip()
            if raw and (raw.isdigit() or (raw.startswith("-") and raw[1:].isdigit())):
                try:
                    return int(raw)
                except ValueError:
                    return None
        return None

    @staticmethod
    def _extract_required_string(value: Any, *, field_name: str) -> str:
        normalized = TonPayService._extract_optional_string(value)
        if normalized is None:
            raise RuntimeError(f"TONConsole did not return valid {field_name}.")
        return normalized

    @staticmethod
    def _extract_optional_string(value: Any) -> str | None:
        return extract_optional_string(value)

    @staticmethod
    def _parse_positive_decimal(value: Any, *, label: str) -> Decimal:
        try:
            parsed = Decimal(str(value))
        except (InvalidOperation, TypeError) as error:
            raise RuntimeError(f"Invalid {label}.") from error
        if parsed <= 0:
            raise RuntimeError(f"{label.capitalize()} must be positive.")
        return parsed

    @staticmethod
    def _format_decimal(value: Decimal, *, precision: str) -> str:
        quantized = value.quantize(Decimal(precision), rounding=ROUND_HALF_UP)
        text = format(quantized, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text or "0"
