from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final

from aiogram import Bot, html
from aiogram_dialog import DialogManager

from app.services.crud.stars_order import StarsOrderService
from app.services.crud.user import UserService
from app.telegram.dialogs.flows.storefront.handlers.shared import (
    referrals_page,
    referrals_selected_user_id,
    set_referrals_page,
)

from .common import (
    banner_url,
    consume_notice,
    current_user,
    get_i18n,
    get_user,
    price_usd_for_cents,
)

REFERRALS_PAGE_SIZE: Final[int] = 6
REFERRAL_MEMBERS_LIMIT: Final[int] = 60
_INVISIBLE_BUTTON_TEXT: Final[str] = "\u200B"


def _format_tg_time(value: datetime | None, *, fmt: str = "dt") -> str:
    if value is None:
        return "—"
    dt_utc = (
        value.replace(tzinfo=timezone.utc)
        if value.tzinfo is None
        else value.astimezone(timezone.utc)
    )
    unix = int(dt_utc.timestamp())
    fallback = dt_utc.strftime("%Y-%m-%d %H:%M UTC")
    return f'<tg-time unix="{unix}" format="{fmt}">{fallback}</tg-time>'


def _referral_button_name(value: str, *, limit: int = 20) -> str:
    cleaned = " ".join(value.split())
    if not cleaned:
        return "User"
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 1]}…"


def _referral_level_percent(
    level: int,
    *,
    level1: str,
    level2: str,
    level3: str,
) -> str:
    if level == 1:
        return level1
    if level == 2:
        return level2
    return level3


async def _resolve_bot_username(dialog_manager: DialogManager) -> str:
    bot = dialog_manager.middleware_data.get("bot") or dialog_manager.middleware_data.get(
        "event_bot"
    )
    if isinstance(bot, Bot):
        username = getattr(bot, "username", None)
        if username:
            return str(username)
        me = await bot.get_me()
        if me.username:
            return me.username
    return "unknown_bot"


async def referral_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    stars_order_service: StarsOrderService = dialog_manager.middleware_data["stars_order_service"]
    bot_username = await _resolve_bot_username(dialog_manager)

    overview = await user_service.referral_overview(
        user_id=user.id,
        bot_username=bot_username,
        referrals_limit=REFERRAL_MEMBERS_LIMIT,
    )
    if overview is None:
        text = str(i18n.messages.referral_unavailable())
        referral_balance_cents = 0
    else:
        level1_percent, level2_percent, level3_percent = (
            stars_order_service.referral_level_percent_texts()
        )
        total_referrals = overview.level1_count + overview.level2_count + overview.level3_count
        text = str(
            i18n.messages.referral_screen(
                link=overview.referral_link,
                balance=price_usd_for_cents(overview.referral_balance_cents),
                earned=price_usd_for_cents(overview.referral_earned_cents),
                total=total_referrals,
                level1=overview.level1_count,
                level2=overview.level2_count,
                level3=overview.level3_count,
                percent1=level1_percent,
                percent2=level2_percent,
                percent3=level3_percent,
            )
        )
        referral_balance_cents = overview.referral_balance_cents
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "referrals"),
        "withdraw_button_text": i18n.buttons.referral_withdraw(),
        "list_button_text": i18n.buttons.referral_list(),
        "back_button_text": i18n.buttons.back_to_profile(),
        "can_withdraw": referral_balance_cents > 0,
    }


async def referral_withdraw_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = await current_user(dialog_manager=dialog_manager)
    text = str(
        i18n.messages.referral_withdraw_screen(
            balance=price_usd_for_cents(user.referral_balance_cents),
        )
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "referrals"),
        "back_button_text": i18n.buttons.back_to_referrals(),
    }


async def referral_list_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    bot_username = await _resolve_bot_username(dialog_manager)
    page = referrals_page(dialog_manager)

    overview = await user_service.referral_overview(
        user_id=user.id,
        bot_username=bot_username,
        referrals_limit=REFERRAL_MEMBERS_LIMIT,
    )
    if overview is None:
        text = str(i18n.messages.referral_unavailable())
        members: list[dict[str, str]] = []
        total_pages = 1
        has_next = False
        show_prev_page = False
        show_page_info = False
    elif not overview.referrals:
        text = str(i18n.messages.referral_list_empty_screen())
        members = []
        total_pages = 1
        has_next = False
        show_prev_page = False
        show_page_info = False
    else:
        total_referrals = overview.level1_count + overview.level2_count + overview.level3_count
        all_members = overview.referrals
        total_pages = max(1, (len(all_members) + REFERRALS_PAGE_SIZE - 1) // REFERRALS_PAGE_SIZE)
        if page > 0 and page >= total_pages:
            page = total_pages - 1
            set_referrals_page(dialog_manager, page)
        start = page * REFERRALS_PAGE_SIZE
        visible_members = all_members[start : start + REFERRALS_PAGE_SIZE]
        members = [
            {
                "id": str(member.user_id),
                "button_text": str(
                    i18n.messages.referral_member_button(
                        level=member.level,
                        user_id=member.user_id,
                        name=_referral_button_name(member.name),
                    )
                ),
            }
            for member in visible_members
        ]
        text = str(
            i18n.messages.referral_list_screen(
                total=total_referrals,
                page=page + 1,
            )
        )
        show_prev_page = page > 0
        has_next = page + 1 < total_pages
        show_page_info = bool(members)
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "referrals"),
        "members": members,
        "prev_button_text": _INVISIBLE_BUTTON_TEXT,
        "page_button_text": i18n.messages.referral_list_page_indicator(
            current=page + 1,
            total=total_pages,
        ),
        "next_button_text": _INVISIBLE_BUTTON_TEXT,
        "show_prev_page": show_prev_page,
        "show_next_page": has_next,
        "show_page_info": show_page_info,
        "back_button_text": i18n.buttons.back_to_referrals(),
    }


async def referral_details_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    stars_order_service: StarsOrderService = dialog_manager.middleware_data["stars_order_service"]
    bot_username = await _resolve_bot_username(dialog_manager)
    selected_user_id = referrals_selected_user_id(dialog_manager)

    overview = await user_service.referral_overview(
        user_id=user.id,
        bot_username=bot_username,
        referrals_limit=REFERRAL_MEMBERS_LIMIT,
    )
    if overview is None or selected_user_id is None:
        text = str(i18n.messages.referral_detail_not_found())
    else:
        member = next(
            (item for item in overview.referrals if item.user_id == selected_user_id),
            None,
        )
        if member is None:
            text = str(i18n.messages.referral_detail_not_found())
        else:
            level1_percent, level2_percent, level3_percent = (
                stars_order_service.referral_level_percent_texts()
            )
            text = str(
                i18n.messages.referral_detail_screen(
                    user_id=member.user_id,
                    name=html.quote(member.name),
                    level=member.level,
                    percent=_referral_level_percent(
                        member.level,
                        level1=level1_percent,
                        level2=level2_percent,
                        level3=level3_percent,
                    ),
                    joined=_format_tg_time(member.joined_at),
                )
            )

    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "referrals"),
        "back_to_list_text": i18n.buttons.referral_back_to_list(),
        "back_button_text": i18n.buttons.back_to_referrals(),
    }


__all__ = [
    "referral_details_getter",
    "referral_getter",
    "referral_list_getter",
    "referral_withdraw_getter",
]
