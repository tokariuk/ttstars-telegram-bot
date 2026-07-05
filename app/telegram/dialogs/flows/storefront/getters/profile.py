from __future__ import annotations

from typing import Any

from aiogram_dialog import DialogManager

from app.services.crud.stars_order import StarsOrderService
from app.services.crud.user import UserService

from .common import (
    banner_url,
    consume_notice,
    current_user,
    get_i18n,
    price_usd_for_cents,
)


async def profile_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = await current_user(dialog_manager=dialog_manager)
    stars_order_service: StarsOrderService = dialog_manager.middleware_data["stars_order_service"]
    stats = await stars_order_service.profile_stats(user_id=user.id)
    text = str(
        i18n.messages.profile_screen(
            user_id=user.id,
            balance=price_usd_for_cents(user.balance_cents),
            referral_balance=price_usd_for_cents(user.referral_balance_cents),
            total_stars=stats.total_stars_purchased,
            total_premiums=stats.total_premiums_purchased,
            total_stars_usd=price_usd_for_cents(stats.total_stars_amount_cents),
            total_premiums_usd=price_usd_for_cents(stats.total_premiums_amount_cents),
        )
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "profile"),
        "checks_button_text": i18n.buttons.checks(),
        "history_button_text": i18n.buttons.history(),
        "promo_button_text": i18n.buttons.activate_promo(),
        "referrals_button_text": i18n.buttons.referrals(),
        "topup_button_text": i18n.buttons.topup_balance(),
        "back_button_text": i18n.buttons.back_to_menu(),
    }


async def promo_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    promo_codes = await user_service.list_promo_codes(limit=12)
    active_codes = [
        code
        for code in promo_codes
        if code.max_activations is None or code.activations < code.max_activations
    ]
    available_codes = ", ".join(code.code for code in active_codes) if active_codes else "—"
    text = str(i18n.messages.promo_screen(available_codes=available_codes))
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "promo"),
        "back_button_text": i18n.buttons.back_to_profile(),
    }


__all__ = [
    "profile_getter",
    "promo_getter",
]
