from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from app.enums.stars_order import StarsPaymentProvider

_PAYMENT_FEE_ON_TOP_PROVIDERS = {
    StarsPaymentProvider.PLATEGA_PAY,
    StarsPaymentProvider.NICE_PAY_RU,
    StarsPaymentProvider.NICE_PAY_KZ,
}


@dataclass(frozen=True, slots=True)
class CheckoutPricing:
    net_amount_cents: int
    invoice_amount_cents: int
    customer_total_cents: int
    fee_percent_text: str


def build_checkout_pricing(
    *,
    provider: StarsPaymentProvider,
    net_amount_cents: int,
    payment_fee_percents: Mapping[StarsPaymentProvider, Decimal],
    payout_fee_percents: Mapping[StarsPaymentProvider, Decimal],
    payout_fixed_cents: Mapping[StarsPaymentProvider, int],
    error_type: type[Exception],
) -> CheckoutPricing:
    if provider == StarsPaymentProvider.BALANCE:
        return CheckoutPricing(
            net_amount_cents=net_amount_cents,
            invoice_amount_cents=net_amount_cents,
            customer_total_cents=net_amount_cents,
            fee_percent_text="0",
        )

    net_amount = Decimal(net_amount_cents) / Decimal("100")
    payment_rate = payment_fee_percents.get(provider, Decimal("0")) / Decimal("100")
    payout_rate = payout_fee_percents.get(provider, Decimal("0")) / Decimal("100")
    payout_fixed = Decimal(payout_fixed_cents.get(provider, 0)) / Decimal("100")
    payment_fee_on_top = provider in _PAYMENT_FEE_ON_TOP_PROVIDERS

    denominator = Decimal("1") - payout_rate
    if not payment_fee_on_top:
        denominator *= Decimal("1") - payment_rate
    if denominator <= 0:
        raise error_type("Invalid payment fee configuration.")

    invoice_amount = ((net_amount + payout_fixed) / denominator).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )
    if invoice_amount <= 0:
        raise error_type("Calculated checkout amount must be positive.")

    net_after_fees = calculate_net_after_fees(
        invoice_amount=invoice_amount,
        payment_rate=payment_rate,
        payout_rate=payout_rate,
        payout_fixed=payout_fixed,
        payment_fee_on_top=payment_fee_on_top,
    )
    while net_after_fees < net_amount:
        invoice_amount += Decimal("0.01")
        net_after_fees = calculate_net_after_fees(
            invoice_amount=invoice_amount,
            payment_rate=payment_rate,
            payout_rate=payout_rate,
            payout_fixed=payout_fixed,
            payment_fee_on_top=payment_fee_on_top,
        )

    customer_total = (
        (invoice_amount * (Decimal("1") + payment_rate)) if payment_fee_on_top else invoice_amount
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    fee_percent = display_fee_percent(
        provider=provider,
        payment_rate=payment_rate,
        payout_rate=payout_rate,
    )

    return CheckoutPricing(
        net_amount_cents=int((net_amount * Decimal("100")).quantize(Decimal("1"))),
        invoice_amount_cents=int((invoice_amount * Decimal("100")).quantize(Decimal("1"))),
        customer_total_cents=int((customer_total * Decimal("100")).quantize(Decimal("1"))),
        fee_percent_text=format_percent(fee_percent),
    )


def display_fee_percent(
    *,
    provider: StarsPaymentProvider,
    payment_rate: Decimal,
    payout_rate: Decimal,
) -> Decimal:
    if provider == StarsPaymentProvider.BALANCE:
        return Decimal("0")

    payout_multiplier = Decimal("1") - payout_rate
    if payout_multiplier <= 0:
        return Decimal("0")

    if provider in _PAYMENT_FEE_ON_TOP_PROVIDERS:
        ratio = (Decimal("1") + payment_rate) / payout_multiplier
    else:
        payment_multiplier = Decimal("1") - payment_rate
        if payment_multiplier <= 0:
            return Decimal("0")
        ratio = Decimal("1") / (payment_multiplier * payout_multiplier)

    fee = (ratio - Decimal("1")) * Decimal("100")
    return fee if fee > 0 else Decimal("0")


def checkout_fixed_component_cents(
    *,
    provider: StarsPaymentProvider,
    payment_fee_percents: Mapping[StarsPaymentProvider, Decimal],
    payout_fee_percents: Mapping[StarsPaymentProvider, Decimal],
    payout_fixed_cents: Mapping[StarsPaymentProvider, int],
) -> int:
    payout_fixed = max(0, int(payout_fixed_cents.get(provider, 0)))
    if payout_fixed <= 0:
        return 0

    payout_rate = payout_fee_percents.get(provider, Decimal("0")) / Decimal("100")
    payment_rate = payment_fee_percents.get(provider, Decimal("0")) / Decimal("100")
    payout_multiplier = Decimal("1") - payout_rate
    if payout_multiplier <= 0:
        return 0

    if provider in _PAYMENT_FEE_ON_TOP_PROVIDERS:
        factor = (Decimal("1") + payment_rate) / payout_multiplier
    else:
        payment_multiplier = Decimal("1") - payment_rate
        if payment_multiplier <= 0:
            return 0
        factor = Decimal("1") / (payment_multiplier * payout_multiplier)

    fixed_component = (Decimal(payout_fixed) / Decimal("100")) * factor
    cents = int(
        (fixed_component * Decimal("100")).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )
    return max(0, cents)


def parse_percent(value: str, *, default: str) -> Decimal:
    raw = (value or "").strip() or default
    try:
        parsed = Decimal(raw)
    except InvalidOperation, TypeError:
        parsed = Decimal(default)
    if parsed < 0:
        return Decimal("0")
    if parsed >= 100:
        return Decimal("99.99")
    return parsed


def parse_money_cents(value: str, *, default: str) -> int:
    raw = (value or "").strip() or default
    try:
        parsed = Decimal(raw)
    except InvalidOperation, TypeError:
        parsed = Decimal(default)
    if parsed < 0:
        parsed = Decimal("0")
    return int((parsed * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def format_percent(value: Decimal) -> str:
    normalized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    text = format(normalized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def format_amount(value: Decimal) -> str:
    normalized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    text = format(normalized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def calculate_net_after_fees(
    *,
    invoice_amount: Decimal,
    payment_rate: Decimal,
    payout_rate: Decimal,
    payout_fixed: Decimal,
    payment_fee_on_top: bool,
) -> Decimal:
    merchant_base = (
        invoice_amount if payment_fee_on_top else invoice_amount * (Decimal("1") - payment_rate)
    )
    return (merchant_base * (Decimal("1") - payout_rate)) - payout_fixed
