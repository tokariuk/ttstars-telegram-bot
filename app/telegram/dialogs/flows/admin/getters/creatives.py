from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Final

from aiogram_dialog import DialogManager

from app.gifts import list_gift_packs
from app.stars import get_premium_pack, price_usd_for_cents, price_usd_for_stars

from ..handlers.shared import i18n
from .common import admin_banner_url

CREATIVE_STARS_AMOUNTS: Final[tuple[int, ...]] = (100, 150, 250, 350, 500, 750, 1000)
CREATIVE_PREMIUM_MONTHS: Final[tuple[int, ...]] = (3, 6, 12)


@dataclass(frozen=True, slots=True)
class CreativeOffer:
    amount: int
    price_usd: str


def creative_stars_offers() -> tuple[CreativeOffer, ...]:
    return tuple(
        CreativeOffer(amount=amount, price_usd=price_usd_for_stars(amount))
        for amount in CREATIVE_STARS_AMOUNTS
    )


def creative_premium_offers() -> tuple[CreativeOffer, ...]:
    return tuple(
        CreativeOffer(
            amount=months,
            price_usd=get_premium_pack(months=months).price_usd,
        )
        for months in CREATIVE_PREMIUM_MONTHS
    )


def creative_gift_offers() -> tuple[CreativeOffer, ...]:
    counts_by_price = Counter(gift.price_cents for gift in list_gift_packs())
    return tuple(
        CreativeOffer(amount=count, price_usd=price_usd_for_cents(price_cents))
        for price_cents, count in sorted(counts_by_price.items())
    )


def _common_buttons(dialog_manager: DialogManager) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    return {
        "back_to_section_button_text": i18n_ctx.buttons.admin_creatives_back_to_section(),
        "back_to_menu_button_text": i18n_ctx.buttons.admin_creatives_back_to_menu(),
    }


async def creatives_menu_getter(
    dialog_manager: DialogManager,
    **_: Any,
) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    return {
        "text": i18n_ctx.messages.admin_creatives_menu_screen(),
        "banner_url": admin_banner_url(dialog_manager, "creatives"),
        "stars_button_text": i18n_ctx.buttons.admin_creatives_stars(),
        "premium_button_text": i18n_ctx.buttons.admin_creatives_premium(),
        "gifts_button_text": i18n_ctx.buttons.admin_creatives_gifts(),
        "overview_button_text": i18n_ctx.buttons.admin_creatives_overview(),
        "back_to_menu_button_text": i18n_ctx.buttons.admin_creatives_back_to_menu(),
    }


async def creatives_stars_getter(
    dialog_manager: DialogManager,
    **_: Any,
) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    offers = creative_stars_offers()
    result: dict[str, Any] = {
        "text": i18n_ctx.messages.admin_creatives_stars_screen(),
        "banner_url": admin_banner_url(dialog_manager, "creatives_stars"),
        **_common_buttons(dialog_manager),
    }
    for offer in offers:
        result[f"stars_{offer.amount}_button_text"] = i18n_ctx.buttons.admin_creatives_stars_offer(
            stars=offer.amount,
            price=offer.price_usd,
        )
    return result


async def creatives_premium_getter(
    dialog_manager: DialogManager,
    **_: Any,
) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    result: dict[str, Any] = {
        "text": i18n_ctx.messages.admin_creatives_premium_screen(),
        "banner_url": admin_banner_url(dialog_manager, "creatives_premium"),
        **_common_buttons(dialog_manager),
    }
    for offer in creative_premium_offers():
        result[f"premium_{offer.amount}_button_text"] = (
            i18n_ctx.buttons.admin_creatives_premium_offer(
                months=offer.amount,
                price=offer.price_usd,
            )
        )
    return result


async def creatives_gifts_getter(
    dialog_manager: DialogManager,
    **_: Any,
) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    basic, collection = creative_gift_offers()
    return {
        "text": i18n_ctx.messages.admin_creatives_gifts_screen(
            designs=basic.amount + collection.amount,
        ),
        "banner_url": admin_banner_url(dialog_manager, "creatives_gifts"),
        "basic_gift_button_text": i18n_ctx.buttons.admin_creatives_gift_basic(
            price=basic.price_usd,
        ),
        "gift_collection_button_text": i18n_ctx.buttons.admin_creatives_gift_collection(
            count=collection.amount,
            price=collection.price_usd,
        ),
        **_common_buttons(dialog_manager),
    }


async def creatives_overview_getter(
    dialog_manager: DialogManager,
    **_: Any,
) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    stars = creative_stars_offers()[0]
    premium = creative_premium_offers()[0]
    gifts = creative_gift_offers()[0]
    return {
        "text": i18n_ctx.messages.admin_creatives_overview_screen(),
        "banner_url": admin_banner_url(dialog_manager, "creatives"),
        "stars_button_text": i18n_ctx.buttons.admin_creatives_overview_stars(
            price=stars.price_usd,
        ),
        "premium_button_text": i18n_ctx.buttons.admin_creatives_overview_premium(
            price=premium.price_usd,
        ),
        "gifts_button_text": i18n_ctx.buttons.admin_creatives_overview_gifts(
            price=gifts.price_usd,
        ),
        **_common_buttons(dialog_manager),
    }


__all__ = [
    "CreativeOffer",
    "creative_gift_offers",
    "creative_premium_offers",
    "creative_stars_offers",
    "creatives_gifts_getter",
    "creatives_menu_getter",
    "creatives_overview_getter",
    "creatives_premium_getter",
    "creatives_stars_getter",
]
