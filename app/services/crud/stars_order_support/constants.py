from __future__ import annotations

from app.enums.stars_order import StarsOrderStatus, StarsPaymentProvider

RETRYABLE_DELIVERY_ERROR_MARKERS: tuple[str, ...] = (
    "429",
    "rate limit",
    "timeout",
    "timed out",
    "temporar",
    "connection reset",
    "connection aborted",
    "connection refused",
    "network is unreachable",
    "service unavailable",
)
FULFILL_LOCK_KEY_PREFIX = "stars_order_fulfill_lock"
FULFILL_LOCK_TTL_SECONDS = 180
PLATEGA_PAYLOAD_PREFIX = "tts-pltg"
NICEPAY_ORDER_ID_PREFIX = "tts-nice"
HELEKET_ORDER_ID_PREFIX = "tts-hkt"
REFERRAL_LEVELS_COUNT = 3

NICE_PAY_PROVIDER_VARIANTS: tuple[StarsPaymentProvider, ...] = (
    StarsPaymentProvider.NICE_PAY_RU,
    StarsPaymentProvider.NICE_PAY_KZ,
)

EXTERNAL_PAYMENT_PROVIDERS: tuple[StarsPaymentProvider, ...] = (
    StarsPaymentProvider.CRYPTO_BOT,
    StarsPaymentProvider.TON_PAY,
    StarsPaymentProvider.LZT_PAY,
    StarsPaymentProvider.HELEKET_PAY,
    StarsPaymentProvider.PLATEGA_PAY,
    StarsPaymentProvider.NICE_PAY_RU,
    StarsPaymentProvider.NICE_PAY_KZ,
    StarsPaymentProvider.XROCKET_PAY,
)

BALANCE_IN_PROGRESS_ORDER_STATUSES: tuple[StarsOrderStatus, ...] = (
    StarsOrderStatus.PAYMENT_CONFIRMED,
    StarsOrderStatus.FULFILLING,
)
