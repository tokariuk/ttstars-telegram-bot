from __future__ import annotations

import asyncio
import inspect
from typing import Any

from aiohttp import ClientResponse, ClientSession, ClientTimeout
from telethon import TelegramClient
from telethon.errors import RPCError
from telethon.sessions import StringSession
from telethon.tl import functions, types
from telethon.tl.types import payments as payment_types

from app.stars import normalize_recipient_username


class TelegramGiftService:
    def __init__(
        self,
        *,
        bot_token: str | None,
        base_url: str = "https://api.telegram.org",
        userbot_api_id: int | None = None,
        userbot_api_hash: str | None = None,
        userbot_session: str | None = None,
        userbot_device_model: str = "TTStars Gifts Userbot",
        userbot_system_version: str = "Linux",
        userbot_app_version: str = "TTStars/1.0",
        userbot_lang_code: str = "en",
        userbot_system_lang_code: str = "en",
    ) -> None:
        self.bot_token = (bot_token or "").strip()
        self.base_url = base_url.strip().rstrip("/")
        self.timeout = ClientTimeout(total=20)
        self.userbot_api_id = userbot_api_id
        self.userbot_api_hash = (userbot_api_hash or "").strip()
        self.userbot_session = (userbot_session or "").strip()
        self.userbot_device_model = userbot_device_model.strip() or "TTStars Gifts Userbot"
        self.userbot_system_version = userbot_system_version.strip() or "Linux"
        self.userbot_app_version = userbot_app_version.strip() or "TTStars/1.0"
        self.userbot_lang_code = userbot_lang_code.strip() or "en"
        self.userbot_system_lang_code = userbot_system_lang_code.strip() or "en"
        self._client: TelegramClient | None = None
        self._client_lock = asyncio.Lock()
        self._http_session: ClientSession | None = None
        self._http_session_lock = asyncio.Lock()

    @property
    def configured(self) -> bool:
        return self.userbot_configured or self.bot_api_configured

    @property
    def bot_api_configured(self) -> bool:
        return bool(self.bot_token and self.base_url)

    @property
    def userbot_configured(self) -> bool:
        return bool(self.userbot_api_id and self.userbot_api_hash and self.userbot_session)

    @property
    def userbot_config_incomplete(self) -> bool:
        has_any = bool(self.userbot_api_id or self.userbot_api_hash or self.userbot_session)
        return has_any and not self.userbot_configured

    async def send_gift(  # noqa: C901
        self,
        *,
        user_id: int | None,
        gift_id: str,
        recipient_username: str | None = None,
        text: str | None = None,
        is_private: bool | None = None,
        pay_for_upgrade: bool = False,
    ) -> None:
        if not self.configured:
            raise RuntimeError("Telegram gift service is not configured.")

        normalized_gift_id = gift_id.strip()
        if not normalized_gift_id:
            raise RuntimeError("Gift ID is empty.")
        try:
            gift_id_int = int(normalized_gift_id)
        except ValueError as error:
            raise RuntimeError("Gift ID must be numeric.") from error
        if gift_id_int <= 0:
            raise RuntimeError("Gift ID must be positive.")

        normalized_text = (text or "").strip()
        if len(normalized_text) > 128:
            raise RuntimeError("Gift message is too long (max 128 characters).")

        if self.userbot_configured:
            await self._send_gift_via_userbot(
                user_id=user_id,
                recipient_username=recipient_username,
                gift_id=gift_id_int,
                text=normalized_text or None,
                is_private=is_private,
            )
            return

        if user_id is None or user_id <= 0:
            raise RuntimeError("Gift recipient ID must be positive.")

        payload: dict[str, Any] = {
            "user_id": user_id,
            "gift_id": normalized_gift_id,
            "pay_for_upgrade": bool(pay_for_upgrade),
        }
        if normalized_text:
            payload["text"] = normalized_text
        if is_private is not None:
            payload["is_private"] = bool(is_private)

        try:
            await self._request_json(method="sendGift", payload=payload)
        except RuntimeError as error:
            # Fallback for Bot API versions that don't support is_private.
            if is_private is not None and self._is_private_param_unsupported(error):
                payload.pop("is_private", None)
                await self._request_json(method="sendGift", payload=payload)
                return
            raise

    async def resolve_user_id(self, *, recipient_username: str) -> int | None:
        normalized_username = self._normalize_username(recipient_username)
        if normalized_username is None:
            return None

        if self.userbot_config_incomplete:
            raise RuntimeError(
                "Telegram gifts userbot configuration is incomplete. "
                "Set TELEGRAM_GIFTS_USERBOT_API_ID, "
                "TELEGRAM_GIFTS_USERBOT_API_HASH and TELEGRAM_GIFTS_USERBOT_SESSION."
            )

        if self.userbot_configured:
            peer = await self._resolve_user_input_peer_by_username(
                username=normalized_username,
            )
            return int(peer.user_id)
        if not self.bot_api_configured:
            return None
        return await self._resolve_user_id_via_bot_api(username=normalized_username)

    async def close(self) -> None:
        async with self._client_lock:
            client = self._client
            self._client = None
        if client is not None:
            await self._disconnect_client(client)
        async with self._http_session_lock:
            http_session = self._http_session
            self._http_session = None
        if http_session is not None and not http_session.closed:
            await http_session.close()

    @staticmethod
    def _is_private_param_unsupported(error: RuntimeError) -> bool:
        text = str(error).lower()
        return "is_private" in text and ("parse" in text or "bad request" in text)

    async def _send_gift_via_userbot(
        self,
        *,
        user_id: int | None,
        recipient_username: str | None,
        gift_id: int,
        text: str | None,
        is_private: bool | None,
    ) -> None:
        client = await self._get_userbot_client()
        peer = await self._resolve_user_input_peer(
            client=client,
            user_id=user_id,
            recipient_username=recipient_username,
        )

        check_result = await client(
            functions.payments.CheckCanSendGiftRequest(gift_id=gift_id),
        )
        if isinstance(check_result, payment_types.CheckCanSendGiftResultFail):
            reason = (check_result.reason.text or "").strip() or "Gift cannot be sent."
            raise RuntimeError(f"Telegram userbot gift check failed: {reason}")

        message_with_entities: types.TextWithEntities | None = None
        if text:
            message_with_entities = types.TextWithEntities(text=text, entities=[])

        invoice = types.InputInvoiceStarGift(
            peer=peer,
            gift_id=gift_id,
            hide_name=is_private if is_private is not None else None,
            include_upgrade=False,
            message=message_with_entities,
        )
        payment_form = await client(functions.payments.GetPaymentFormRequest(invoice=invoice))
        form_id = getattr(payment_form, "form_id", None)
        if not isinstance(form_id, int):
            raise RuntimeError("Telegram userbot returned payment form without form_id.")

        payment_result = await client(
            functions.payments.SendStarsFormRequest(
                form_id=form_id,
                invoice=invoice,
            )
        )
        if isinstance(payment_result, payment_types.PaymentVerificationNeeded):
            raise RuntimeError(
                "Telegram userbot requested payment verification, stars gift was not sent."
            )
        if not isinstance(payment_result, payment_types.PaymentResult):
            raise RuntimeError("Telegram userbot returned unexpected payment result.")

    async def _get_userbot_client(self) -> TelegramClient:
        if not self.userbot_configured:
            raise RuntimeError("Telegram gifts userbot is not configured.")

        async with self._client_lock:
            if self._client is not None and self._client.is_connected():
                return self._client

            client = TelegramClient(
                StringSession(self.userbot_session),
                self._required_userbot_api_id(),
                self.userbot_api_hash,
                device_model=self.userbot_device_model,
                system_version=self.userbot_system_version,
                app_version=self.userbot_app_version,
                lang_code=self.userbot_lang_code,
                system_lang_code=self.userbot_system_lang_code,
            )
            await client.connect()
            if not await client.is_user_authorized():
                await self._disconnect_client(client)
                raise RuntimeError("Telegram gifts userbot session is not authorized.")
            self._client = client
            return client

    @staticmethod
    async def _disconnect_client(client: TelegramClient) -> None:
        disconnect_result = client.disconnect()
        if inspect.isawaitable(disconnect_result):
            await disconnect_result

    def _required_userbot_api_id(self) -> int:
        api_id = self.userbot_api_id
        if api_id is None:
            raise RuntimeError("Telegram gifts userbot API ID is not configured.")
        return int(api_id)

    async def _resolve_user_input_peer(
        self,
        *,
        client: TelegramClient,
        user_id: int | None,
        recipient_username: str | None,
    ) -> types.InputPeerUser:
        if user_id is not None and user_id > 0:
            try:
                entity = await client.get_input_entity(user_id)
            except (ValueError, RPCError):
                entity = None
            else:
                if isinstance(entity, types.InputPeerUser):
                    return entity

        normalized_username = self._normalize_username(recipient_username or "")
        if normalized_username is not None:
            return await self._resolve_user_input_peer_by_username(
                username=normalized_username,
                client=client,
            )

        raise RuntimeError("Gift recipient username is required.")

    async def _resolve_user_input_peer_by_username(
        self,
        *,
        username: str,
        client: TelegramClient | None = None,
    ) -> types.InputPeerUser:
        tg_client = client if client is not None else await self._get_userbot_client()
        try:
            entity = await tg_client.get_input_entity(f"@{username}")
        except (ValueError, RPCError) as error:
            raise RuntimeError(
                f"Failed to resolve gift recipient @{username} in Telegram userbot."
            ) from error

        if not isinstance(entity, types.InputPeerUser):
            raise RuntimeError(f"Recipient @{username} is not a Telegram user.")
        return entity

    async def _resolve_user_id_via_bot_api(self, *, username: str) -> int | None:
        try:
            response = await self._request_json(
                method="getChat",
                payload={"chat_id": f"@{username}"},
            )
        except RuntimeError:
            return None
        result = response.get("result")
        if not isinstance(result, dict):
            return None
        raw_chat_id = result.get("id")
        if not isinstance(raw_chat_id, int):
            return None
        if raw_chat_id <= 0:
            return None
        return raw_chat_id

    @staticmethod
    def _normalize_username(value: str) -> str | None:
        return normalize_recipient_username(value)

    async def _request_json(
        self,
        *,
        method: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/bot{self.bot_token}/{method}"
        session = await self._get_http_session()
        async with session.post(
            url,
            json=payload or {},
            timeout=self.timeout,
        ) as response:
            body = await self._safe_json(response=response)
            if response.status >= 400:
                message = self._error_message(payload=body) or f"HTTP {response.status}"
                raise RuntimeError(f"Telegram Bot API error: {message}")
            if body.get("ok") is not True:
                message = self._error_message(payload=body) or "Unknown API error"
                raise RuntimeError(f"Telegram Bot API error: {message}")
            return body

    async def _get_http_session(self) -> ClientSession:
        async with self._http_session_lock:
            if self._http_session is None or self._http_session.closed:
                self._http_session = ClientSession()
            return self._http_session

    @staticmethod
    async def _safe_json(*, response: ClientResponse) -> dict[str, Any]:
        payload = await response.json(content_type=None)
        if isinstance(payload, dict):
            return payload
        raise RuntimeError("Telegram Bot API returned invalid JSON payload.")

    @staticmethod
    def _error_message(*, payload: dict[str, Any]) -> str | None:
        for key in ("description", "message", "error"):
            raw = payload.get(key)
            if raw is None:
                continue
            text = str(raw).strip()
            if text:
                return text
        return None
