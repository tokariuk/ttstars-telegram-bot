from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
from typing import Final

STARS_CRYPTO_PAYLOAD_PREFIX: Final[str] = "stars_crypto"
STAR_PRICE_USD: Final[Decimal] = Decimal("0.015")
STARS_MARKUP_PERCENT: Final[Decimal] = Decimal("8")
STAR_SELL_PRICE_USD: Final[Decimal] = STAR_PRICE_USD * (
    Decimal("1") + (STARS_MARKUP_PERCENT / Decimal("100"))
)
MIN_STARS_COUNT: Final[int] = 50
MAX_STARS_COUNT: Final[int] = 10_000
DEFAULT_STARS_COUNT: Final[int] = 50

RECIPIENT_USERNAME_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9_]{5,32}$")


@dataclass(frozen=True, slots=True)
class StarsPack:
    key: str
    stars_count: int
    price_cents: int

    @property
    def price_usd(self) -> str:
        return price_usd_for_stars(self.stars_count)


@dataclass(frozen=True, slots=True)
class PremiumPack:
    months: int
    price_cents: int

    @property
    def price_usd(self) -> str:
        return price_usd_for_cents(self.price_cents)


_PREMIUM_PACKS: Final[dict[int, int]] = {
    3: 1299,
    6: 1699,
    12: 3099,
}


def get_stars_pack(pack_key: str | None) -> StarsPack:
    stars_count = parse_stars_count(pack_key)
    if stars_count is None:
        stars_count = DEFAULT_STARS_COUNT
    return build_stars_pack(stars_count=stars_count)


def build_stars_pack(*, stars_count: int) -> StarsPack:
    if stars_count < MIN_STARS_COUNT or stars_count > MAX_STARS_COUNT:
        raise ValueError(
            f"Stars count must be between {MIN_STARS_COUNT} and {MAX_STARS_COUNT}."
        )
    return StarsPack(
        key=str(stars_count),
        stars_count=stars_count,
        price_cents=_price_cents(stars_count=stars_count),
    )


def parse_stars_count(value: str | None) -> int | None:
    if value is None:
        return None
    raw = value.strip()
    if not raw.isdigit():
        return None
    stars_count = int(raw)
    if stars_count < MIN_STARS_COUNT or stars_count > MAX_STARS_COUNT:
        return None
    return stars_count


def price_usd_for_stars(stars_count: int) -> str:
    total = (Decimal(stars_count) * STAR_SELL_PRICE_USD).quantize(
        Decimal("0.0001"),
        rounding=ROUND_HALF_UP,
    )
    return _format_usd(total)


def current_star_price_usd() -> str:
    return _format_usd(STAR_SELL_PRICE_USD)


def price_usd_for_cents(cents: int) -> str:
    total = (Decimal(cents) / Decimal("100")).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )
    return _format_usd(total)


def affordable_stars_for_balance_cents(balance_cents: int) -> int:
    if balance_cents <= 0:
        return 0
    balance_usd = Decimal(balance_cents) / Decimal("100")
    stars = (balance_usd / STAR_SELL_PRICE_USD).to_integral_value(rounding=ROUND_DOWN)
    return int(stars)


def get_premium_pack(months: int) -> PremiumPack:
    price_cents = _PREMIUM_PACKS.get(months)
    if price_cents is None:
        raise ValueError("Unsupported premium period.")
    return PremiumPack(months=months, price_cents=price_cents)


def premium_months_options() -> tuple[int, ...]:
    return tuple(sorted(_PREMIUM_PACKS.keys()))


def _price_cents(*, stars_count: int) -> int:
    cents = (Decimal(stars_count) * STAR_SELL_PRICE_USD * Decimal("100")).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP,
    )
    return int(cents)


def _format_usd(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text if text else "0"


def normalize_recipient_username(value: str) -> str | None:
    username = value.strip().lstrip("@")
    if not RECIPIENT_USERNAME_RE.fullmatch(username):
        return None
    return username


def build_crypto_payload(*, order_id: int, user_id: int) -> str:
    return f"{STARS_CRYPTO_PAYLOAD_PREFIX}:{order_id}:{user_id}"


def parse_crypto_payload(payload: str) -> tuple[int, int] | None:
    parts = payload.split(":")
    if len(parts) != 3 or parts[0] != STARS_CRYPTO_PAYLOAD_PREFIX:
        return None
    try:
        order_id = int(parts[1])
        user_id = int(parts[2])
    except ValueError:
        return None
    if order_id <= 0 or user_id <= 0:
        return None
    return order_id, user_id
