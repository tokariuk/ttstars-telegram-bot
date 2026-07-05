from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.enums.stars_order import StarsPaymentProvider

from .constants import (
    HELEKET_ORDER_ID_PREFIX,
    NICE_PAY_PROVIDER_VARIANTS,
    NICEPAY_ORDER_ID_PREFIX,
    PLATEGA_PAYLOAD_PREFIX,
)


def is_provider_configured(*, service: Any, provider: StarsPaymentProvider) -> bool:
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
    if provider in NICE_PAY_PROVIDER_VARIANTS:
        return service.nice_pay_service.configured
    if provider == StarsPaymentProvider.XROCKET_PAY:
        return service.xrocket_pay_service.configured
    if provider == StarsPaymentProvider.BALANCE:
        return True
    return False


def provider_currency(*, service: Any, provider: StarsPaymentProvider) -> str:
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
    if provider in NICE_PAY_PROVIDER_VARIANTS:
        return nice_pay_currency(service=service, provider=provider)
    if provider == StarsPaymentProvider.XROCKET_PAY:
        return service.xrocket_pay_service.currency
    return "USD"


def build_platega_payload(*, local_order_id: int) -> str:
    # Random suffix prevents collisions after local DB resets.
    return f"{PLATEGA_PAYLOAD_PREFIX}-{local_order_id}-{uuid4().hex[:10]}"


def build_nice_pay_order_id(*, provider: StarsPaymentProvider, local_order_id: int) -> str:
    # Random suffix prevents collisions after local DB resets.
    if provider == StarsPaymentProvider.NICE_PAY_RU:
        provider_suffix = "ru"
    elif provider == StarsPaymentProvider.NICE_PAY_KZ:
        provider_suffix = "kz"
    else:
        raise ValueError(f"Unsupported NicePay provider: {provider.value}")
    return f"{NICEPAY_ORDER_ID_PREFIX}-{provider_suffix}-{local_order_id}-{uuid4().hex[:10]}"


def nice_pay_currency(*, service: Any, provider: StarsPaymentProvider) -> str:
    value = service.nice_pay_provider_currencies.get(provider, service.nice_pay_service.currency)
    normalized = (value or "").strip().upper()
    return normalized or service.nice_pay_service.currency


def build_heleket_order_id(*, local_order_id: int) -> str:
    # Random suffix prevents collisions after local DB resets.
    return f"{HELEKET_ORDER_ID_PREFIX}-{local_order_id}-{uuid4().hex[:10]}"


def lzt_callback_url(*, service: Any) -> str | None:
    return _provider_callback_url(
        base_url=service.config.server.url,
        webhook_path=service.config.lzt_pay.webhook_path,
    )


def xrocket_callback_url(*, service: Any) -> str | None:
    return _provider_callback_url(
        base_url=service.config.server.url,
        webhook_path=service.config.xrocket_pay.webhook_path,
    )


def heleket_callback_url(*, service: Any) -> str | None:
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
    normalized_path = (
        normalized_path_raw
        if normalized_path_raw.startswith("/")
        else f"/{normalized_path_raw}"
    )
    return f"{normalized_base}{normalized_path}"
