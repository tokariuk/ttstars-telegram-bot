from __future__ import annotations

from typing import Any

from aiogram_dialog import DialogManager

from app.stars import MAX_STARS_COUNT, MIN_STARS_COUNT, current_star_price_usd

from .common import banner_url, consume_notice, get_i18n


async def calculator_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    text = str(
        i18n.messages.calculator_screen(
            min_stars=MIN_STARS_COUNT,
            max_stars=MAX_STARS_COUNT,
            star_price=current_star_price_usd(),
        )
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "calculator"),
        "back_button_text": i18n.buttons.back_to_menu(),
    }


__all__ = ["calculator_getter"]
