from __future__ import annotations

from app.enums.stars_order import StarsPaymentProvider

# Order here drives the order providers are presented in the Mini App catalog.
SUPPORTED_PAYMENT_PROVIDERS: tuple[StarsPaymentProvider, ...] = (
    StarsPaymentProvider.CRYPTO_BOT,
    StarsPaymentProvider.TON_PAY,
    StarsPaymentProvider.XROCKET_PAY,
    StarsPaymentProvider.HELEKET_PAY,
    StarsPaymentProvider.LZT_PAY,
    StarsPaymentProvider.NICE_PAY_RU,
    StarsPaymentProvider.NICE_PAY_KZ,
    StarsPaymentProvider.PLATEGA_PAY,
    StarsPaymentProvider.BALANCE,
)

# Every provider except the internal wallet can fund external invoices / top-ups.
EXTERNAL_PAYMENT_PROVIDERS: tuple[StarsPaymentProvider, ...] = tuple(
    provider
    for provider in SUPPORTED_PAYMENT_PROVIDERS
    if provider != StarsPaymentProvider.BALANCE
)
TOPUP_PAYMENT_PROVIDERS: tuple[StarsPaymentProvider, ...] = EXTERNAL_PAYMENT_PROVIDERS

_PROVIDER_TITLES: dict[StarsPaymentProvider, str] = {
    StarsPaymentProvider.CRYPTO_BOT: "CryptoBot",
    StarsPaymentProvider.TON_PAY: "TON",
    StarsPaymentProvider.XROCKET_PAY: "xRocket",
    StarsPaymentProvider.HELEKET_PAY: "Heleket",
    StarsPaymentProvider.LZT_PAY: "LZT Pay",
    StarsPaymentProvider.NICE_PAY_RU: "NicePay RU",
    StarsPaymentProvider.NICE_PAY_KZ: "NicePay KZ",
    StarsPaymentProvider.PLATEGA_PAY: "Platega",
    StarsPaymentProvider.BALANCE: "Balance",
}


def provider_title(provider: StarsPaymentProvider) -> str:
    return _PROVIDER_TITLES.get(provider, provider.value)


def supports_topup(provider: StarsPaymentProvider) -> bool:
    return provider in TOPUP_PAYMENT_PROVIDERS


def supports_gifts(provider: StarsPaymentProvider) -> bool:
    # Gifts are a balance-funded product: every supported provider (and the
    # internal wallet) can pay for them, exactly like Stars and Premium.
    return provider in SUPPORTED_PAYMENT_PROVIDERS
