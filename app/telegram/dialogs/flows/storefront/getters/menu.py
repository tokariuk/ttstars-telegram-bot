from __future__ import annotations

from typing import Any

from aiogram_dialog import DialogManager

from .common import (
    banner_url,
    consume_notice,
    current_user,
    get_i18n,
    price_usd_for_cents,
)


async def menu_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = await current_user(dialog_manager=dialog_manager)
    text = str(
        i18n.messages.greeting(
            name=user.mention,
            balance=price_usd_for_cents(user.balance_cents),
        )
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "menu"),
        "miniapp_button_text": i18n.buttons.open_miniapp(),
        "miniapp_url": "https://ttstars.xyz",
        "buy_stars_button_text": i18n.buttons.buy_stars(),
        "buy_premium_button_text": i18n.buttons.buy_premium(),
        "sell_stars_button_text": i18n.buttons.sell_stars(),
        "buy_gifts_button_text": i18n.buttons.buy_gifts(),
        "topup_button_text": i18n.buttons.topup_balance(),
        "calculator_button_text": i18n.buttons.calculator(),
        "profile_button_text": i18n.buttons.profile(),
        "faq_button_text": i18n.buttons.faq(),
    }


__all__ = ["menu_getter"]
