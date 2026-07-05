from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

from aiohttp import ClientSession, ClientTimeout

_ALLOWED_CURRENCIES: set[str] = {
    "rub",
    "uah",
    "kzt",
    "byn",
    "usd",
    "eur",
    "gbp",
    "cny",
    "try",
    "jpy",
    "brl",
}


@dataclass(frozen=True, slots=True)
class LZTPayInvoice:
    invoice_id: int
    payment_id: str
    pay_url: str
    status: str


@dataclass(frozen=True, slots=True)
class LZTPayInvoiceStatus:
    is_paid: bool
    status: str


class LZTPayService:
    def __init__(
        self,
        *,
        api_token: str | None,
        base_url: str,
        merchant_id: int | None,
        merchant_key: str | None,
        currency: str,
        success_url: str,
    ) -> None:
        self.api_token = (api_token or "").strip()
        self.base_url = base_url.rstrip("/")
        self.merchant_id = int(merchant_id) if merchant_id is not None else 0
        self.merchant_key = (merchant_key or "").strip()
        normalized_currency = (currency or "usd").strip().lower()
        self.currency = (
            normalized_currency
            if normalized_currency in _ALLOWED_CURRENCIES
            else "usd"
        )
        self.success_url = success_url.strip()
        self.timeout = ClientTimeout(total=20)

    @property
    def configured(self) -> bool:
        return bool(self.api_token and self.merchant_id > 0 and self.success_url)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    async def create_invoice(
        self,
        *,
        amount: str,
        description: str,
        payment_id: str,
        required_telegram_id: int | None = None,
        required_telegram_username: str | None = None,
        callback_url: str | None = None,
    ) -> LZTPayInvoice:
        if not self.configured:
            raise RuntimeError("LZT Pay service is not configured.")

        request_payload: dict[str, Any] = {
            "currency": self.currency,
            "amount": self._parse_amount(amount),
            "payment_id": payment_id,
            "comment": description,
            "url_success": self.success_url,
            "merchant_id": self.merchant_id,
        }
        if callback_url:
            request_payload["url_callback"] = callback_url
        if required_telegram_id is not None and required_telegram_id > 0:
            request_payload["required_telegram_id"] = required_telegram_id
        if required_telegram_username:
            request_payload["required_telegram_username"] = required_telegram_username

        async with ClientSession() as session:
            async with session.post(
                f"{self.base_url}/invoice",
                json=request_payload,
                headers=self._headers(),
                timeout=self.timeout,
            ) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)

        invoice = self._extract_invoice(payload)
        invoice_id = self._parse_int(
            invoice.get("invoice_id") or invoice.get("id"),
            field_name="invoice_id",
        )
        payment_id_raw = invoice.get("payment_id")
        payment_id_value = str(payment_id_raw) if payment_id_raw is not None else payment_id
        pay_url_raw = invoice.get("url")
        if not isinstance(pay_url_raw, str) or not pay_url_raw:
            raise RuntimeError("LZT Pay did not return invoice URL.")
        status_raw = invoice.get("status")
        status = str(status_raw).strip().lower() if status_raw is not None else "unknown"
        return LZTPayInvoice(
            invoice_id=invoice_id,
            payment_id=payment_id_value,
            pay_url=pay_url_raw,
            status=status or "unknown",
        )

    async def get_invoice_status(self, *, invoice_id: int) -> LZTPayInvoiceStatus:
        if not self.configured:
            return LZTPayInvoiceStatus(is_paid=False, status="unconfigured")
        if invoice_id <= 0:
            return LZTPayInvoiceStatus(is_paid=False, status="invoice_missing")

        async with ClientSession() as session:
            async with session.get(
                f"{self.base_url}/invoice",
                params={"invoice_id": str(invoice_id)},
                headers=self._headers(),
                timeout=self.timeout,
            ) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)

        invoice = self._extract_invoice(payload)
        status_raw = invoice.get("status")
        status = str(status_raw).strip().lower() if status_raw is not None else "unknown"
        is_paid = status in {"paid", "completed", "success"}
        return LZTPayInvoiceStatus(is_paid=is_paid, status=status or "unknown")

    @staticmethod
    def _parse_amount(value: str) -> float:
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, TypeError) as error:
            raise RuntimeError("Invalid amount for LZT Pay invoice.") from error
        if amount <= 0:
            raise RuntimeError("Amount for LZT Pay invoice must be positive.")
        quantized = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return float(quantized)

    @staticmethod
    def _parse_int(value: Any, *, field_name: str) -> int:
        if isinstance(value, int) and value > 0:
            return value
        if isinstance(value, str) and value.isdigit():
            parsed = int(value)
            if parsed > 0:
                return parsed
        raise RuntimeError(f"LZT Pay did not return valid {field_name}.")

    @staticmethod
    def _extract_invoice(payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise RuntimeError("LZT Pay returned invalid payload.")

        invoice = payload.get("invoice")
        if isinstance(invoice, dict):
            return invoice

        result = payload.get("result")
        if isinstance(result, dict):
            nested_invoice = result.get("invoice")
            if isinstance(nested_invoice, dict):
                return nested_invoice
            if "invoice_id" in result:
                return result

        raise RuntimeError("LZT Pay did not return invoice data.")
