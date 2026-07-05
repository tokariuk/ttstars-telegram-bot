from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal

from app.enums.stars_order import StarsPaymentProvider
from app.models.config import AppConfig

ParsePercent = Callable[..., Decimal]
ParseMoneyCents = Callable[..., int]


def build_nice_pay_provider_currencies(
    *,
    config: AppConfig,
) -> dict[StarsPaymentProvider, str]:
    return {
        StarsPaymentProvider.NICE_PAY_RU: config.nice_pay.currency_ru,
        StarsPaymentProvider.NICE_PAY_KZ: config.nice_pay.currency_kz,
    }


def build_payment_fee_percents(
    *,
    config: AppConfig,
    parse_percent: ParsePercent,
) -> dict[StarsPaymentProvider, Decimal]:
    return {
        StarsPaymentProvider.CRYPTO_BOT: parse_percent(
            config.crypto_pay.fee_percent,
            default="3",
        ),
        StarsPaymentProvider.TON_PAY: parse_percent(
            config.ton_pay.fee_percent,
            default="1",
        ),
        StarsPaymentProvider.LZT_PAY: parse_percent(config.lzt_pay.fee_percent, default="0"),
        StarsPaymentProvider.HELEKET_PAY: parse_percent(
            config.heleket_pay.fee_percent,
            default="2",
        ),
        StarsPaymentProvider.PLATEGA_PAY: parse_percent(
            config.platega_pay.fee_percent,
            default="0",
        ),
        StarsPaymentProvider.NICE_PAY_RU: parse_percent(
            config.nice_pay.fee_percent_ru,
            default="9",
        ),
        StarsPaymentProvider.NICE_PAY_KZ: parse_percent(
            config.nice_pay.fee_percent_kz,
            default="9",
        ),
        StarsPaymentProvider.XROCKET_PAY: parse_percent(
            config.xrocket_pay.fee_percent,
            default="0",
        ),
        StarsPaymentProvider.BALANCE: Decimal("0"),
    }


def build_payout_fee_percents(
    *,
    config: AppConfig,
    parse_percent: ParsePercent,
) -> dict[StarsPaymentProvider, Decimal]:
    return {
        StarsPaymentProvider.CRYPTO_BOT: parse_percent(
            config.crypto_pay.payout_fee_percent,
            default="0",
        ),
        StarsPaymentProvider.TON_PAY: parse_percent(
            config.ton_pay.payout_fee_percent,
            default="0",
        ),
        StarsPaymentProvider.LZT_PAY: parse_percent(
            config.lzt_pay.payout_fee_percent,
            default="0",
        ),
        StarsPaymentProvider.HELEKET_PAY: parse_percent(
            config.heleket_pay.payout_fee_percent,
            default="0",
        ),
        StarsPaymentProvider.PLATEGA_PAY: parse_percent(
            config.platega_pay.payout_fee_percent,
            default="0",
        ),
        StarsPaymentProvider.NICE_PAY_RU: parse_percent(
            config.nice_pay.payout_fee_percent,
            default="5.5",
        ),
        StarsPaymentProvider.NICE_PAY_KZ: parse_percent(
            config.nice_pay.payout_fee_percent,
            default="5.5",
        ),
        StarsPaymentProvider.XROCKET_PAY: parse_percent(
            config.xrocket_pay.payout_fee_percent,
            default="0",
        ),
        StarsPaymentProvider.BALANCE: Decimal("0"),
    }


def build_payout_fixed_cents(
    *,
    config: AppConfig,
    parse_money_cents: ParseMoneyCents,
) -> dict[StarsPaymentProvider, int]:
    return {
        StarsPaymentProvider.CRYPTO_BOT: parse_money_cents(
            config.crypto_pay.payout_fixed_usd,
            default="0",
        ),
        StarsPaymentProvider.TON_PAY: parse_money_cents(
            config.ton_pay.payout_fixed_usd,
            default="0",
        ),
        StarsPaymentProvider.LZT_PAY: parse_money_cents(
            config.lzt_pay.payout_fixed_usd,
            default="0",
        ),
        StarsPaymentProvider.HELEKET_PAY: parse_money_cents(
            config.heleket_pay.payout_fixed_usd,
            default="0",
        ),
        StarsPaymentProvider.PLATEGA_PAY: parse_money_cents(
            config.platega_pay.payout_fixed_usd,
            default="0",
        ),
        StarsPaymentProvider.NICE_PAY_RU: parse_money_cents(
            config.nice_pay.payout_fixed_usd,
            default="0",
        ),
        StarsPaymentProvider.NICE_PAY_KZ: parse_money_cents(
            config.nice_pay.payout_fixed_usd,
            default="0",
        ),
        StarsPaymentProvider.XROCKET_PAY: parse_money_cents(
            config.xrocket_pay.payout_fixed_usd,
            default="0",
        ),
        StarsPaymentProvider.BALANCE: 0,
    }


def build_min_payment_amount_cents(
    *,
    config: AppConfig,
    parse_money_cents: ParseMoneyCents,
) -> dict[StarsPaymentProvider, int]:
    return {
        StarsPaymentProvider.CRYPTO_BOT: parse_money_cents(
            config.crypto_pay.min_payment_usd or config.crypto_pay.min_topup_usd,
            default="1",
        ),
        StarsPaymentProvider.TON_PAY: parse_money_cents(
            config.ton_pay.min_payment_usd,
            default="1",
        ),
        StarsPaymentProvider.LZT_PAY: parse_money_cents(
            config.lzt_pay.min_payment_usd or config.lzt_pay.min_topup_usd,
            default="1",
        ),
        StarsPaymentProvider.HELEKET_PAY: parse_money_cents(
            config.heleket_pay.min_payment_usd or config.heleket_pay.min_topup_usd,
            default="1",
        ),
        StarsPaymentProvider.PLATEGA_PAY: parse_money_cents(
            config.platega_pay.min_payment_usd or config.platega_pay.min_topup_usd,
            default="1",
        ),
        StarsPaymentProvider.NICE_PAY_RU: parse_money_cents(
            config.nice_pay.min_payment_usd_ru or config.nice_pay.min_topup_usd_ru,
            default="1",
        ),
        StarsPaymentProvider.NICE_PAY_KZ: parse_money_cents(
            config.nice_pay.min_payment_usd_kz or config.nice_pay.min_topup_usd_kz,
            default="1",
        ),
        StarsPaymentProvider.XROCKET_PAY: parse_money_cents(
            config.xrocket_pay.min_payment_usd or config.xrocket_pay.min_topup_usd,
            default="1",
        ),
        StarsPaymentProvider.BALANCE: 0,
    }
