from __future__ import annotations

from enum import StrEnum


class StarsPaymentProvider(StrEnum):
    CRYPTO_BOT = "crypto_bot"
    TON_PAY = "ton_pay"
    PLATEGA_PAY = "platega_pay"
    XROCKET_PAY = "xrocket_pay"
    LZT_PAY = "lzt_pay"
    NICE_PAY_RU = "nice_pay_ru"
    NICE_PAY_KZ = "nice_pay_kz"
    HELEKET_PAY = "heleket_pay"
    BALANCE = "balance"


class StarsOrderProductType(StrEnum):
    STARS = "stars"
    PREMIUM = "premium"
    GIFT = "gift"
    TOPUP = "topup"


class StarsOrderStatus(StrEnum):
    CREATING_PAYMENT = "creating_payment"
    PENDING_PAYMENT = "pending_payment"
    PAYMENT_CONFIRMED = "payment_confirmed"
    FULFILLING = "fulfilling"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
