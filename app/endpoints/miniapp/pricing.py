from __future__ import annotations

from decimal import Decimal, InvalidOperation

from app.enums.stars_order import StarsOrderProductType
from app.stars import build_stars_pack, get_premium_pack

from .errors import validation_error

_TOPUP_MIN_CENTS = 100


def parse_usd_amount_to_cents(value: str) -> int:
    normalized = value.strip().replace(",", ".")
    if not normalized:
        validation_error("Amount must not be empty.")
    try:
        amount = Decimal(normalized)
    except InvalidOperation:
        validation_error("Amount must be a valid decimal number.")
    if amount <= 0:
        validation_error("Amount must be positive.")
    cents_decimal = amount * Decimal("100")
    if cents_decimal != cents_decimal.to_integral_value():
        validation_error("Amount supports at most 2 decimal places.")
    cents = int(cents_decimal)
    if cents < _TOPUP_MIN_CENTS:
        validation_error("Top-up amount must be at least 1 USD.")
    return cents


def net_amount_cents_for_quote(
    *,
    product_type: StarsOrderProductType,
    stars_count: int | None,
    months: int | None,
    amount_usd: str | None,
) -> int:
    """Resolve the net (pre-fee) USD-cent amount a quote is priced against."""

    if product_type == StarsOrderProductType.STARS:
        if stars_count is None:
            validation_error("stars_count is required for stars quotes.")
        try:
            return build_stars_pack(stars_count=stars_count).price_cents
        except ValueError as error:
            validation_error(str(error))
    if product_type == StarsOrderProductType.PREMIUM:
        if months is None:
            validation_error("months is required for premium quotes.")
        try:
            return get_premium_pack(months=months).price_cents
        except ValueError as error:
            validation_error(str(error))
    if product_type == StarsOrderProductType.TOPUP:
        if amount_usd is None:
            validation_error("amount_usd is required for top-up quotes.")
        return parse_usd_amount_to_cents(amount_usd)
    validation_error("Unsupported product type for quote.")
