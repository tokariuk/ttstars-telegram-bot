from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aiohttp import ClientSession, ClientTimeout


@dataclass(frozen=True, slots=True)
class CryptoPayInvoice:
    invoice_id: int
    pay_url: str


@dataclass(frozen=True, slots=True)
class CryptoPayInvoiceStatus:
    is_paid: bool
    status: str


class CryptoPayService:
    def __init__(
        self,
        *,
        api_token: str | None,
        base_url: str,
        currency_type: str = "fiat",
        fiat: str = "USD",
        accepted_assets: str | None = None,
        asset: str,
    ) -> None:
        self.api_token = (api_token or "").strip()
        self.base_url = base_url.rstrip("/")
        normalized_currency_type = (currency_type or "").strip().lower()
        self.currency_type = (
            normalized_currency_type if normalized_currency_type in {"fiat", "crypto"} else "fiat"
        )
        self.fiat = (fiat or "USD").strip().upper()
        self.accepted_assets = ",".join(
            [
                token
                for token in [
                    part.strip().upper()
                    for part in (accepted_assets or "").split(",")
                ]
                if token
            ]
        )
        self.asset = (asset or "USDT").strip().upper()
        self.timeout = ClientTimeout(total=20)

    @property
    def configured(self) -> bool:
        return bool(self.api_token)

    def _headers(self) -> dict[str, str]:
        return {
            "Crypto-Pay-API-Token": self.api_token,
            "Content-Type": "application/json",
        }

    @staticmethod
    def _extract_result(data: dict[str, Any]) -> dict[str, Any]:
        result = data.get("result", data)
        if isinstance(result, list):
            if not result:
                return {}
            first = result[0]
            return first if isinstance(first, dict) else {}
        if isinstance(result, dict):
            items = result.get("items")
            if isinstance(items, list):
                if not items:
                    return {}
                first = items[0]
                return first if isinstance(first, dict) else {}
            return result
        return {}

    async def create_invoice(
        self,
        *,
        amount: str,
        description: str,
        invoice_payload: str | None = None,
    ) -> CryptoPayInvoice:
        request_payload: dict[str, Any] = {
            "amount": amount,
            "description": description,
            "allow_comments": False,
            "allow_anonymous": True,
        }
        if self.currency_type == "fiat":
            request_payload["currency_type"] = "fiat"
            request_payload["fiat"] = self.fiat
            if self.accepted_assets:
                request_payload["accepted_assets"] = self.accepted_assets
        else:
            request_payload["currency_type"] = "crypto"
            request_payload["asset"] = self.asset
        if invoice_payload is not None and invoice_payload != "":
            request_payload["payload"] = invoice_payload
        async with ClientSession() as session:
            async with session.post(
                f"{self.base_url}/createInvoice",
                json=request_payload,
                headers=self._headers(),
                timeout=self.timeout,
            ) as response:
                response.raise_for_status()
                data = await response.json(content_type=None)

        result = self._extract_result(data)
        invoice_id_raw = result.get("invoice_id") or result.get("id")
        if not isinstance(invoice_id_raw, int):
            raise RuntimeError("Crypto Pay did not return invoice ID.")

        pay_url = (
            result.get("bot_invoice_url")
            or result.get("mini_app_invoice_url")
            or result.get("pay_url")
            or result.get("url")
        )
        if not isinstance(pay_url, str) or not pay_url:
            raise RuntimeError("Crypto Pay did not return invoice URL.")

        return CryptoPayInvoice(invoice_id=invoice_id_raw, pay_url=pay_url)

    async def get_invoice_status(self, *, invoice_id: int) -> CryptoPayInvoiceStatus:
        payload = {"invoice_ids": str(invoice_id)}
        async with ClientSession() as session:
            async with session.post(
                f"{self.base_url}/getInvoices",
                json=payload,
                headers=self._headers(),
                timeout=self.timeout,
            ) as response:
                response.raise_for_status()
                data = await response.json(content_type=None)

        result = self._extract_result(data)
        status_raw = result.get("status") or ""
        status = str(status_raw).strip().lower() or "unknown"
        is_paid = status in {"paid", "confirmed", "completed"}
        return CryptoPayInvoiceStatus(is_paid=is_paid, status=status)

    async def set_webhook(self, *, webhook_url: str) -> bool:
        url = webhook_url.strip()
        if not url:
            raise RuntimeError("Crypto Pay webhook URL is empty.")

        payload = {"url": url}
        async with ClientSession() as session:
            async with session.post(
                f"{self.base_url}/setWebhook",
                json=payload,
                headers=self._headers(),
                timeout=self.timeout,
            ) as response:
                data = await response.json(content_type=None)
                if response.status == 405:
                    return False
                response.raise_for_status()

        result = self._extract_result(data)
        if isinstance(result.get("url"), str):
            return result.get("url") == url
        if isinstance(result.get("webhook_url"), str):
            return result.get("webhook_url") == url
        # Some Crypto Pay responses only return boolean in `result`.
        if isinstance(data.get("result"), bool):
            return bool(data.get("result"))
        return bool(data.get("ok"))
