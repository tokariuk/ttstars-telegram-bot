from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from app.enums.stars_order import StarsPaymentProvider
from app.utils.routes import normalize_route_path

from .constants import (
    HELEKET_ORDER_ID_PREFIX,
    PLATEGA_PAYLOAD_PREFIX,
)

if TYPE_CHECKING:
    from app.services.crud.stars_order import StarsOrderService


def is_provider_configured(*, service: StarsOrderService, provider: StarsPaymentProvider) -> bool:
    if provider == StarsPaymentProvider.CRYPTO_BOT:
        return service.crypto_pay_service.configured
    if provider == StarsPaymentProvider.TON_PAY:
        return service.ton_pay_service.configured
    if provider == StarsPaymentProvider.LZT_PAY:
        return service.lzt_pay_service.configured
    if provider == StarsPaymentProvider.HELEKET_PAY:
        return service.heleket_pay_service.configured
    if provider == StarsPaymentProvider.PLATEGA_PAY:
        return service.platega_pay_service.configured
    if provider == StarsPaymentProvider.XROCKET_PAY:
        return service.xrocket_pay_service.configured
    if provider == StarsPaymentProvider.BALANCE:
        return True
    return False


def provider_currency(*, service: StarsOrderService, provider: StarsPaymentProvider) -> str:
    if provider == StarsPaymentProvider.CRYPTO_BOT:
        return service.crypto_pay_service.asset
    if provider == StarsPaymentProvider.TON_PAY:
        return "TON"
    if provider == StarsPaymentProvider.LZT_PAY:
        return service.lzt_pay_service.currency.upper()
    if provider == StarsPaymentProvider.HELEKET_PAY:
        return service.heleket_pay_service.currency
    if provider == StarsPaymentProvider.PLATEGA_PAY:
        return service.platega_pay_service.currency
    if provider == StarsPaymentProvider.XROCKET_PAY:
        return service.xrocket_pay_service.currency
    return "USD"


def build_platega_payload(*, local_order_id: int) -> str:
    # Random suffix prevents collisions after local DB resets.
    return f"{PLATEGA_PAYLOAD_PREFIX}-{local_order_id}-{uuid4().hex[:10]}"


def build_heleket_order_id(*, local_order_id: int) -> str:
    # Random suffix prevents collisions after local DB resets.
    return f"{HELEKET_ORDER_ID_PREFIX}-{local_order_id}-{uuid4().hex[:10]}"


def lzt_callback_url(*, service: StarsOrderService) -> str | None:
    return _provider_callback_url(
        base_url=service.config.server.url,
        webhook_path=service.config.lzt_pay.webhook_path,
    )


def xrocket_callback_url(*, service: StarsOrderService) -> str | None:
    return _provider_callback_url(
        base_url=service.config.server.url,
        webhook_path=service.config.xrocket_pay.webhook_path,
    )


def heleket_callback_url(*, service: StarsOrderService) -> str | None:
    explicit = service.config.heleket_pay.callback_url
    if explicit is not None and explicit.strip():
        return explicit.strip()
    return _provider_callback_url(
        base_url=service.config.server.url,
        webhook_path=service.config.heleket_pay.webhook_path,
    )


def _provider_callback_url(*, base_url: str, webhook_path: str) -> str | None:
    normalized_base = base_url.strip().rstrip("/")
    if not normalized_base:
        return None
    normalized_path_raw = webhook_path.strip()
    if not normalized_path_raw:
        return None
    normalized_path = normalize_route_path(normalized_path_raw)
    return f"{normalized_base}{normalized_path}"
