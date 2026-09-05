from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from app.stars import price_usd_for_cents

GIFT_PRICE_STANDARD_CENTS: Final[int] = 159
GIFT_PRICE_DEFAULT_BEAR_CENTS: Final[int] = 59


@dataclass(frozen=True, slots=True)
class TelegramGiftPack:
    key: str
    gift_id: str
    label: str
    price_cents: int

    @property
    def price_usd(self) -> str:
        return price_usd_for_cents(self.price_cents)


_GIFT_PACKS: Final[dict[str, TelegramGiftPack]] = {
    "new_year_tree": TelegramGiftPack(
        key="new_year_tree",
        gift_id="5922558454332916696",
        label="New Year Tree",
        price_cents=GIFT_PRICE_STANDARD_CENTS,
    ),
    "valentine_heart": TelegramGiftPack(
        key="valentine_heart",
        gift_id="5801108895304779062",
        label="Valentine Heart",
        price_cents=GIFT_PRICE_STANDARD_CENTS,
    ),
    "new_year_bear": TelegramGiftPack(
        key="new_year_bear",
        gift_id="5956217000635139069",
        label="New Year Bear",
        price_cents=GIFT_PRICE_STANDARD_CENTS,
    ),
    "bear_with_heart": TelegramGiftPack(
        key="bear_with_heart",
        gift_id="5800655655995968830",
        label="Bear With Heart",
        price_cents=GIFT_PRICE_STANDARD_CENTS,
    ),
    "bear_with_bouquet": TelegramGiftPack(
        key="bear_with_bouquet",
        gift_id="5866352046986232958",
        label="Bear With Bouquet",
        price_cents=GIFT_PRICE_STANDARD_CENTS,
    ),
    "irish_bear": TelegramGiftPack(
        key="irish_bear",
        gift_id="5893356958802511476",
        label="Irish Bear",
        price_cents=GIFT_PRICE_STANDARD_CENTS,
    ),
    "clown_bear": TelegramGiftPack(
        key="clown_bear",
        gift_id="5935895822435615975",
        label="Clown Bear",
        price_cents=GIFT_PRICE_STANDARD_CENTS,
    ),
    "easter_bear": TelegramGiftPack(
        key="easter_bear",
        gift_id="5969796561943660080",
        label="Easter Bear",
        price_cents=GIFT_PRICE_STANDARD_CENTS,
    ),
    "worker_bear": TelegramGiftPack(
        key="worker_bear",
        gift_id="6026193266406327981",
        label="Worker Bear",
        price_cents=GIFT_PRICE_STANDARD_CENTS,
    ),
    "military_bear": TelegramGiftPack(
        key="military_bear",
        gift_id="6046178578163303744",
        label="Military Bear",
        price_cents=GIFT_PRICE_STANDARD_CENTS,
    ),
    "football_bear": TelegramGiftPack(
        key="football_bear",
        gift_id="5974210632977745012",
        label="Football Bear",
        price_cents=GIFT_PRICE_STANDARD_CENTS,
    ),
    "default_bear": TelegramGiftPack(
        key="default_bear",
        gift_id="5170233102089322756",
        label="Bear",
        price_cents=GIFT_PRICE_DEFAULT_BEAR_CENTS,
    ),
}
_GIFT_PACK_BY_ID: Final[dict[str, TelegramGiftPack]] = {
    gift.gift_id: gift for gift in _GIFT_PACKS.values()
}


def list_gift_packs() -> tuple[TelegramGiftPack, ...]:
    return tuple(_GIFT_PACKS.values())


def get_gift_pack(*, key: str) -> TelegramGiftPack:
    gift = _GIFT_PACKS.get(key)
    if gift is None:
        raise ValueError("Unsupported gift key.")
    return gift


def get_gift_pack_by_id(*, gift_id: str) -> TelegramGiftPack | None:
    return _GIFT_PACK_BY_ID.get(gift_id.strip())
