from __future__ import annotations

import asyncio
import base64
import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Any, Literal, cast

import aiohttp
from pytoniq_core import Cell
from ton_core import NetworkGlobalID
from tonutils.clients import TonapiClient
from tonutils.contracts.wallet import WalletV4R2, WalletV5R1

WalletVersion = Literal["V4R2", "V5R1"]

_FRAGMENT_STARS_PAGE: str = "https://fragment.com/stars/buy"
_FRAGMENT_PREMIUM_PAGE: str = "https://fragment.com/premium/gift"
_FRAGMENT_API_URL: str = "https://fragment.com/api"
_HASH_RE = re.compile(r"(?:https://fragment\.com)?/api\?hash=([a-f0-9]+)")
_MIN_STARS_AMOUNT = 50
_ALLOWED_PREMIUM_MONTHS: set[int] = {3, 6, 12}
_FRAGMENT_PAYMENT_METHOD = "ton"
_MIN_NETWORK_FEE_NANO = 50_000_000  # 0.05 TON safety reserve for fees
_SEQNO_WAIT_SECONDS = 45
_REQUIRED_COOKIE_KEYS: tuple[str, ...] = (
    "stel_ssid",
    "stel_dt",
    "stel_token",
    "stel_ton_token",
)
_DEVICE: str = json.dumps(
    {
        "platform": "iphone",
        "appName": "Tonkeeper",
        "appVersion": "5.5.2",
        "maxProtocolVersion": 2,
        "features": [
            "SendTransaction",
            {"name": "SendTransaction", "maxMessages": 255},
            {"name": "SignData", "types": ["text", "binary", "cell"]},
        ],
    }
)
_BASE_HEADERS: dict[str, str] = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9,uk;q=0.8,ru;q=0.7",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://fragment.com",
    "priority": "u=1, i",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 "
        "Mobile/15E148 Safari/604.1"
    ),
    "x-requested-with": "XMLHttpRequest",
}
_WALLET_BY_VERSION: dict[WalletVersion, type[WalletV4R2] | type[WalletV5R1]] = {
    "V4R2": WalletV4R2,
    "V5R1": WalletV5R1,
}
logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class FragmentRecipient:
    name: str
    address: str


@dataclass(frozen=True, slots=True)
class FragmentPurchaseResult:
    tx_hash: str
    recipient: FragmentRecipient


class FragmentStarsService:
    def __init__(
        self,
        *,
        cookies: str | None,
        fragment_hash: str | None,
        wallet_api_key: str | None,
        wallet_mnemonic: str | None,
        wallet_version: WalletVersion | str | None = None,
    ) -> None:
        self.cookies_raw = (cookies or "").strip()
        self.fragment_hash = (fragment_hash or "").strip()
        self.wallet_api_key = (wallet_api_key or "").strip()
        self.wallet_mnemonic_raw = (wallet_mnemonic or "").strip()

        raw_wallet_version = (wallet_version or "V5R1").strip().upper()
        self.wallet_version: WalletVersion
        if raw_wallet_version in _WALLET_BY_VERSION:
            self.wallet_version = cast(WalletVersion, raw_wallet_version)
        else:
            self.wallet_version = "V5R1"

    @property
    def configured(self) -> bool:
        return (
            bool(self.cookies_raw)
            and bool(self.wallet_api_key)
            and len(self.wallet_mnemonic) >= 12
        )

    @property
    def wallet_mnemonic(self) -> list[str]:
        words = self.wallet_mnemonic_raw.replace(",", " ").split()
        return [word.strip() for word in words if word.strip()]

    async def buy_stars(  # noqa: C901
        self,
        *,
        recipient_username: str,
        stars_count: int,
    ) -> FragmentPurchaseResult:
        if not self.configured:
            raise RuntimeError("Fragment service is not configured.")
        if stars_count < _MIN_STARS_AMOUNT:
            raise RuntimeError(f"Invalid stars count. Minimal amount is {_MIN_STARS_AMOUNT}.")

        username = recipient_username.lstrip("@")
        if not username:
            raise RuntimeError("Recipient username is invalid.")

        cookies = self._parse_cookies()
        account = await self._get_wallet_account()

        async with aiohttp.ClientSession(cookies=cookies) as session:
            for attempt in range(2):
                fragment_hash = await self._resolve_fragment_hash(
                    session=session,
                    page_url=_FRAGMENT_STARS_PAGE,
                    context_name="stars",
                    use_configured_hash=(attempt == 0),
                )
                if attempt == 1:
                    try:
                        await self._link_wallet(
                            session=session,
                            fragment_hash=fragment_hash,
                            account=account,
                        )
                    except Exception:
                        logger.warning(
                            "Fragment stars pre-link attempt failed before retry.",
                            exc_info=True,
                        )
                try:
                    recipient = await self._search_recipient(
                        session=session,
                        fragment_hash=fragment_hash,
                        username=username,
                    )
                    req_id = await self._init_buy_stars_request(
                        session=session,
                        fragment_hash=fragment_hash,
                        recipient=recipient.address,
                        stars_count=stars_count,
                    )
                    transaction = await self._get_buy_stars_link(
                        session=session,
                        fragment_hash=fragment_hash,
                        account=account,
                        req_id=req_id,
                        show_sender=True,
                    )
                    if self._requires_wallet_verification(transaction):
                        linked = await self._link_wallet(
                            session=session,
                            fragment_hash=fragment_hash,
                            account=account,
                        )
                        if not linked:
                            raise RuntimeError("Failed to link TON wallet in Fragment session.")

                        transaction = await self._get_buy_stars_link(
                            session=session,
                            fragment_hash=fragment_hash,
                            account=account,
                            req_id=req_id,
                            show_sender=True,
                        )
                    tx_hash = await self._send_transaction(transaction)
                    await self._confirm_fragment_transaction(
                        session=session,
                        fragment_hash=fragment_hash,
                        payload=transaction,
                        headers=self._headers_for_stars(),
                    )
                    return FragmentPurchaseResult(tx_hash=tx_hash, recipient=recipient)
                except RuntimeError as error:
                    if attempt == 0 and self._is_fragment_access_denied(error):
                        logger.warning(
                            (
                                "Fragment stars purchase got access denial, "
                                "retrying with refreshed hash."
                            )
                        )
                        continue
                    raise

        raise RuntimeError("Fragment stars purchase failed after retry.")

    async def buy_premium(  # noqa: C901
        self,
        *,
        recipient_username: str,
        months: int,
    ) -> FragmentPurchaseResult:
        if not self.configured:
            raise RuntimeError("Fragment service is not configured.")
        if months not in _ALLOWED_PREMIUM_MONTHS:
            raise RuntimeError("Invalid premium period. Allowed: 3, 6, 12 months.")

        username = recipient_username.lstrip("@")
        if not username:
            raise RuntimeError("Recipient username is invalid.")

        cookies = self._parse_cookies()
        account = await self._get_wallet_account()

        async with aiohttp.ClientSession(cookies=cookies) as session:
            for attempt in range(2):
                fragment_hash = await self._resolve_fragment_hash(
                    session=session,
                    page_url=_FRAGMENT_PREMIUM_PAGE,
                    context_name="premium",
                    use_configured_hash=(attempt == 0),
                )
                if attempt == 1:
                    try:
                        await self._link_wallet(
                            session=session,
                            fragment_hash=fragment_hash,
                            account=account,
                        )
                    except Exception:
                        logger.warning(
                            "Fragment premium pre-link attempt failed before retry.",
                            exc_info=True,
                        )
                try:
                    recipient = await self._search_premium_recipient(
                        session=session,
                        fragment_hash=fragment_hash,
                        username=username,
                        months=months,
                    )
                    req_id = await self._init_buy_premium_request(
                        session=session,
                        fragment_hash=fragment_hash,
                        recipient=recipient.address,
                        months=months,
                    )
                    transaction = await self._get_buy_premium_link(
                        session=session,
                        fragment_hash=fragment_hash,
                        account=account,
                        req_id=req_id,
                        show_sender=True,
                    )
                    if self._requires_wallet_verification(transaction):
                        linked = await self._link_wallet(
                            session=session,
                            fragment_hash=fragment_hash,
                            account=account,
                        )
                        if not linked:
                            raise RuntimeError("Failed to link TON wallet in Fragment session.")

                        transaction = await self._get_buy_premium_link(
                            session=session,
                            fragment_hash=fragment_hash,
                            account=account,
                            req_id=req_id,
                            show_sender=True,
                        )
                    tx_hash = await self._send_transaction(transaction)
                    await self._confirm_fragment_transaction(
                        session=session,
                        fragment_hash=fragment_hash,
                        payload=transaction,
                        headers=self._headers_for_premium(),
                    )
                    return FragmentPurchaseResult(tx_hash=tx_hash, recipient=recipient)
                except RuntimeError as error:
                    if attempt == 0 and self._is_fragment_access_denied(error):
                        logger.warning(
                            (
                                "Fragment premium purchase got access denial, "
                                "retrying with refreshed hash."
                            )
                        )
                        continue
                    raise

        raise RuntimeError("Fragment premium purchase failed after retry.")

    async def _resolve_fragment_hash(
        self,
        *,
        session: aiohttp.ClientSession,
        page_url: str,
        context_name: str,
        use_configured_hash: bool,
    ) -> str:
        if use_configured_hash:
            configured_hash = self.fragment_hash.strip()
            if configured_hash:
                return configured_hash
        return await self._fetch_fragment_hash(
            session=session,
            page_url=page_url,
            context_name=context_name,
        )

    @staticmethod
    def _is_fragment_access_denied(error: RuntimeError) -> bool:
        text = str(error).strip().lower()
        if not text:
            return False
        return "access denied" in text

    def _fragment_api_url(self, fragment_hash: str) -> str:
        return f"{_FRAGMENT_API_URL}?hash={fragment_hash}"

    def _headers_for_stars(self) -> dict[str, str]:
        return {
            **_BASE_HEADERS,
            "referer": _FRAGMENT_STARS_PAGE,
            "x-aj-referer": _FRAGMENT_STARS_PAGE,
        }

    def _headers_for_premium(self) -> dict[str, str]:
        return {
            **_BASE_HEADERS,
            "referer": _FRAGMENT_PREMIUM_PAGE,
            "x-aj-referer": _FRAGMENT_PREMIUM_PAGE,
        }

    def _headers_for_hash_page(self) -> dict[str, str]:
        headers = {
            key: value
            for key, value in _BASE_HEADERS.items()
            if key not in {"accept", "content-type", "x-requested-with"}
        }
        headers.update(
            {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "referer": "https://fragment.com/",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "upgrade-insecure-requests": "1",
            }
        )
        return headers

    async def _fetch_fragment_hash(
        self,
        *,
        session: aiohttp.ClientSession,
        page_url: str = _FRAGMENT_STARS_PAGE,
        context_name: str = "stars",
    ) -> str:
        async with session.get(
            page_url,
            headers=self._headers_for_hash_page(),
        ) as response:
            if response.status != 200:
                raise RuntimeError(
                    f"Failed to fetch Fragment {context_name} page: HTTP {response.status}."
                )
            page_source = await response.text()

        match = _HASH_RE.search(page_source)
        if match is None:
            raise RuntimeError(f"Failed to parse Fragment hash from {context_name} page.")
        return match.group(1)

    async def _fragment_request(
        self,
        *,
        session: aiohttp.ClientSession,
        fragment_hash: str,
        method: str,
        data: dict[str, str],
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        async with session.post(
            self._fragment_api_url(fragment_hash=fragment_hash),
            headers=headers if headers is not None else self._headers_for_stars(),
            data=data,
        ) as response:
            response.raise_for_status()
            return await self._parse_response_json(response=response, method=method)

    async def _parse_response_json(
        self,
        *,
        response: aiohttp.ClientResponse,
        method: str,
    ) -> dict[str, Any]:
        try:
            payload = await response.json(content_type=None)
        except Exception as error:
            raise RuntimeError(
                f"Fragment returned unreadable JSON for method '{method}'."
            ) from error
        if not isinstance(payload, dict):
            raise RuntimeError(f"Fragment returned invalid payload for method '{method}'.")
        return payload

    async def _search_recipient(
        self,
        *,
        session: aiohttp.ClientSession,
        fragment_hash: str,
        username: str,
    ) -> FragmentRecipient:
        payload = await self._fragment_request(
            session=session,
            fragment_hash=fragment_hash,
            method="searchStarsRecipient",
            data={
                "query": username,
                "quantity": "",
                "method": "searchStarsRecipient",
            },
            headers=self._headers_for_stars(),
        )
        found = payload.get("found")
        if not isinstance(found, dict):
            raise RuntimeError("Recipient not found on Fragment.")
        name = found.get("name")
        recipient_address = found.get("recipient")
        if not isinstance(name, str) or not name:
            raise RuntimeError("Recipient not found on Fragment.")
        if not isinstance(recipient_address, str) or not recipient_address:
            raise RuntimeError("Fragment recipient address is missing.")
        return FragmentRecipient(name=name, address=recipient_address)

    async def _init_buy_stars_request(
        self,
        *,
        session: aiohttp.ClientSession,
        fragment_hash: str,
        recipient: str,
        stars_count: int,
    ) -> str:
        payload = await self._fragment_request(
            session=session,
            fragment_hash=fragment_hash,
            method="initBuyStarsRequest",
            data={
                "recipient": recipient,
                "quantity": str(stars_count),
                "payment_method": _FRAGMENT_PAYMENT_METHOD,
                "method": "initBuyStarsRequest",
            },
            headers=self._headers_for_stars(),
        )
        return self._extract_req_id(
            payload=payload,
            request_name="initBuyStarsRequest",
        )

    async def _get_buy_stars_link(
        self,
        *,
        session: aiohttp.ClientSession,
        fragment_hash: str,
        account: dict[str, str],
        req_id: str,
        show_sender: bool,
    ) -> dict[str, Any]:
        return await self._fragment_request(
            session=session,
            fragment_hash=fragment_hash,
            method="getBuyStarsLink",
            data={
                "account": json.dumps(account),
                "device": _DEVICE,
                "transaction": "1",
                "id": req_id,
                "show_sender": str(int(show_sender)),
                "method": "getBuyStarsLink",
            },
            headers=self._headers_for_stars(),
        )

    async def _search_premium_recipient(
        self,
        *,
        session: aiohttp.ClientSession,
        fragment_hash: str,
        username: str,
        months: int,
    ) -> FragmentRecipient:
        payload = await self._fragment_request(
            session=session,
            fragment_hash=fragment_hash,
            method="searchPremiumGiftRecipient",
            data={
                "query": username,
                "months": str(months),
                "method": "searchPremiumGiftRecipient",
            },
            headers=self._headers_for_premium(),
        )
        found = payload.get("found")
        if not isinstance(found, dict):
            raise RuntimeError("Recipient not found on Fragment.")
        name = found.get("name")
        recipient_address = found.get("recipient")
        if not isinstance(name, str) or not name:
            raise RuntimeError("Recipient not found on Fragment.")
        if not isinstance(recipient_address, str) or not recipient_address:
            raise RuntimeError("Fragment recipient address is missing.")
        return FragmentRecipient(name=name, address=recipient_address)

    async def _init_buy_premium_request(
        self,
        *,
        session: aiohttp.ClientSession,
        fragment_hash: str,
        recipient: str,
        months: int,
    ) -> str:
        await self._fragment_request(
            session=session,
            fragment_hash=fragment_hash,
            method="updatePremiumState",
            data={
                "mode": "new",
                "lv": "false",
                "dh": str(int(time.time())),
                "method": "updatePremiumState",
            },
            headers=self._headers_for_premium(),
        )
        payload = await self._fragment_request(
            session=session,
            fragment_hash=fragment_hash,
            method="initGiftPremiumRequest",
            data={
                "recipient": recipient,
                "months": str(months),
                "payment_method": _FRAGMENT_PAYMENT_METHOD,
                "method": "initGiftPremiumRequest",
            },
            headers=self._headers_for_premium(),
        )
        return self._extract_req_id(
            payload=payload,
            request_name="initGiftPremiumRequest",
        )

    @staticmethod
    def _extract_req_id(
        *,
        payload: dict[str, Any],
        request_name: str,
    ) -> str:
        req_id = payload.get("req_id")
        if isinstance(req_id, str) and req_id.strip():
            return req_id

        message_parts: list[str] = []
        error_text = payload.get("error")
        if isinstance(error_text, str) and error_text.strip():
            message_parts.append(error_text.strip())
        message_text = payload.get("message")
        if isinstance(message_text, str) and message_text.strip():
            message_parts.append(message_text.strip())
        description_text = payload.get("description")
        if isinstance(description_text, str) and description_text.strip():
            message_parts.append(description_text.strip())

        if message_parts:
            details = " | ".join(message_parts)
            raise RuntimeError(f"Fragment {request_name} failed: {details}")
        raise RuntimeError(f"Fragment {request_name} did not return req_id.")

    async def _get_buy_premium_link(
        self,
        *,
        session: aiohttp.ClientSession,
        fragment_hash: str,
        account: dict[str, str],
        req_id: str,
        show_sender: bool,
    ) -> dict[str, Any]:
        return await self._fragment_request(
            session=session,
            fragment_hash=fragment_hash,
            method="getGiftPremiumLink",
            data={
                "account": json.dumps(account),
                "device": _DEVICE,
                "transaction": "1",
                "id": req_id,
                "show_sender": str(int(show_sender)),
                "method": "getGiftPremiumLink",
            },
            headers=self._headers_for_premium(),
        )

    async def _link_wallet(
        self,
        *,
        session: aiohttp.ClientSession,
        fragment_hash: str,
        account: dict[str, str],
    ) -> bool:
        payload = await self._fragment_request(
            session=session,
            fragment_hash=fragment_hash,
            method="linkWallet",
            data={
                "account": json.dumps(account),
                "device": _DEVICE,
                "method": "linkWallet",
            },
        )
        if payload.get("ok"):
            return True

        if isinstance(payload.get("transaction"), dict):
            try:
                await self._send_transaction(payload)
                return True
            except RuntimeError:
                return False
        return False

    async def _confirm_fragment_transaction(
        self,
        *,
        session: aiohttp.ClientSession,
        fragment_hash: str,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> None:
        confirm_method_raw = payload.get("confirm_method")
        if not isinstance(confirm_method_raw, str):
            return
        confirm_method = confirm_method_raw.strip()
        if not confirm_method:
            return

        confirm_params = payload.get("confirm_params")
        if not isinstance(confirm_params, dict):
            return

        data: dict[str, str] = {"method": confirm_method}
        for key, value in confirm_params.items():
            normalized_key = str(key).strip()
            if not normalized_key:
                continue
            data[normalized_key] = self._to_form_value(value)

        try:
            response = await self._fragment_request(
                session=session,
                fragment_hash=fragment_hash,
                method=confirm_method,
                data=data,
                headers=headers,
            )
        except Exception:
            logger.warning(
                "Fragment confirmation request failed for method %s.",
                confirm_method,
                exc_info=True,
            )
            return

        ok = response.get("ok")
        if ok is False:
            logger.warning(
                "Fragment confirmation returned non-ok response for method %s: %s",
                confirm_method,
                response,
            )

    @staticmethod
    def _to_form_value(value: Any) -> str:
        if isinstance(value, bool):
            return str(int(value))
        if value is None:
            return ""
        if isinstance(value, (int, float, str)):
            return str(value)
        return json.dumps(value, separators=(",", ":"), ensure_ascii=False)

    def _wallet_class(self) -> type[WalletV4R2] | type[WalletV5R1]:
        return _WALLET_BY_VERSION[self.wallet_version]

    async def _get_wallet_account(self) -> dict[str, str]:
        async with TonapiClient(NetworkGlobalID.MAINNET, api_key=self.wallet_api_key) as client:
            wallet_cls = self._wallet_class()
            wallet: Any
            public_key: Any
            wallet, public_key, *_ = wallet_cls.from_mnemonic(
                client=client,  # pyright: ignore[reportArgumentType]
                mnemonic=self.wallet_mnemonic,
            )
            state_init_boc = wallet.state_init.serialize().to_boc()

        return {
            "address": wallet.address.to_str(False, False),
            "publicKey": public_key.as_hex,
            "chain": "-239",
            "walletStateInit": base64.b64encode(state_init_boc).decode("utf-8"),
        }

    @staticmethod
    def _extract_transaction_message(payload: dict[str, Any]) -> dict[str, Any]:
        transaction = payload.get("transaction")
        if not isinstance(transaction, dict):
            raise RuntimeError("Fragment transaction payload is missing.")
        messages = transaction.get("messages")
        if not isinstance(messages, list) or not messages:
            raise RuntimeError("Fragment transaction messages are missing.")
        first_message = messages[0]
        if not isinstance(first_message, dict):
            raise RuntimeError("Fragment transaction message is malformed.")
        return first_message

    @staticmethod
    def _decode_payload(payload: str) -> str:
        encoded_payload = payload.strip()
        if not encoded_payload:
            return ""

        encoded_payload += "=" * (-len(encoded_payload) % 4)
        decoded = base64.b64decode(encoded_payload)
        try:
            cell = Cell.one_from_boc(decoded)
            slice_ = cell.begin_parse()
            # For text comments Fragment returns BOC with 32-bit opcode + snake string.
            slice_.load_uint(32)
            return slice_.load_snake_string().strip()
        except Exception as error:
            raise RuntimeError(
                "Fragment transaction payload is not a valid BOC comment."
            ) from error

    @staticmethod
    def _requires_wallet_verification(payload: dict[str, Any]) -> bool:
        need_verify = payload.get("need_verify")
        if isinstance(need_verify, bool):
            return need_verify
        if isinstance(need_verify, int):
            return need_verify != 0
        if isinstance(need_verify, str):
            return need_verify.strip().lower() in {"1", "true", "yes"}
        return False

    def _parse_cookies(self) -> dict[str, str]:
        raw = self.cookies_raw.strip()
        if not raw:
            raise RuntimeError("Fragment cookies are missing.")

        cookies: dict[str, str]
        if raw.startswith("{"):
            try:
                loaded = json.loads(raw)
            except Exception as error:
                raise RuntimeError("Fragment cookies JSON is invalid.") from error
            if not isinstance(loaded, dict):
                raise RuntimeError("Fragment cookies JSON must be an object.")
            cookies = {
                str(key).strip(): str(value).strip()
                for key, value in loaded.items()
                if str(key).strip() and str(value).strip()
            }
        else:
            cookies = {}
            for pair in raw.split(";"):
                token = pair.strip()
                if not token or "=" not in token:
                    continue
                key, value = token.split("=", 1)
                normalized_key = key.strip()
                normalized_value = value.strip()
                if normalized_key and normalized_value:
                    cookies[normalized_key] = normalized_value

        missing_keys = [key for key in _REQUIRED_COOKIE_KEYS if not cookies.get(key)]
        if missing_keys:
            raise RuntimeError(
                "Fragment cookies are missing required keys: " + ", ".join(missing_keys) + "."
            )
        return cookies

    async def _send_transaction(self, payload: dict[str, Any]) -> str:  # noqa: C901
        message = self._extract_transaction_message(payload)
        tx_address = message.get("address")
        tx_amount = message.get("amount")
        tx_payload = message.get("payload")

        if not isinstance(tx_address, str) or not tx_address:
            raise RuntimeError("Fragment transaction address is missing.")
        if isinstance(tx_amount, int):
            amount = tx_amount
        elif isinstance(tx_amount, str) and tx_amount.isdigit():
            amount = int(tx_amount)
        else:
            raise RuntimeError("Fragment transaction amount is invalid.")
        if amount <= 0:
            raise RuntimeError("Fragment transaction amount must be positive.")
        if not isinstance(tx_payload, str) or not tx_payload:
            raise RuntimeError("Fragment transaction payload is missing.")

        comment = self._decode_payload(tx_payload)

        async with TonapiClient(NetworkGlobalID.MAINNET, api_key=self.wallet_api_key) as client:
            wallet_cls = self._wallet_class()
            wallet: Any
            wallet, *_ = wallet_cls.from_mnemonic(
                client=client,  # pyright: ignore[reportArgumentType]
                mnemonic=self.wallet_mnemonic,
            )
            await wallet.refresh()
            initial_seqno = int(await wallet.seqno())
            balance = int(wallet.balance)
            required_balance = amount + _MIN_NETWORK_FEE_NANO
            if balance < required_balance:
                raise RuntimeError(
                    "TON wallet balance is too low for Fragment payment transaction."
                )
            transfer_result = await wallet.transfer(
                destination=tx_address,
                amount=amount,
                body=comment,
            )
            # Best-effort confirmation wait.
            # If transfer already returned tx hash, we must not fail fulfillment due transient
            # TonAPI errors here because it can cause duplicate star delivery on retries.
            for _ in range(_SEQNO_WAIT_SECONDS):
                await asyncio.sleep(1)
                try:
                    await wallet.refresh()
                    if int(await wallet.seqno()) > initial_seqno:
                        break
                except Exception:
                    continue

        tx_hash = transfer_result.normalized_hash
        if not isinstance(tx_hash, str) or not tx_hash:
            raise RuntimeError("Wallet transfer did not return transaction hash.")
        return tx_hash
