from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final

from aiogram import Bot
from aiogram_dialog import DialogManager

from app.enums.check import CheckStatus
from app.models.dto.check import CheckDto
from app.services.crud.check import CheckService
from app.stars import MAX_STARS_COUNT, MIN_STARS_COUNT, get_stars_pack, price_usd_for_cents
from app.telegram.dialogs.flows.storefront.handlers.shared import (
    check_service,
    checks_create_claim_password,
    checks_create_claim_username,
    checks_create_stars_count,
    checks_history_page,
    checks_history_selected_check_id,
    checks_page,
    selected_check_id,
    set_checks_history_page,
    set_checks_page,
)

from .common import (
    banner_url,
    consume_notice,
    current_user,
    get_i18n,
    get_user,
    secret_code_view,
)

CHECKS_PAGE_SIZE: Final[int] = 6
CHECKS_HISTORY_PAGE_SIZE: Final[int] = 6
_INVISIBLE_BUTTON_TEXT: Final[str] = "\u200b"


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


def _check_item_button_text(i18n: Any, *, check: CheckDto) -> str:
    return str(
        i18n.messages.check_item_button(
            check_id=check.id,
            stars=check.stars_count,
            amount=price_usd_for_cents(check.amount_cents),
        )
    )


def _check_history_item_button_text(i18n: Any, *, check: CheckDto) -> str:
    return str(
        i18n.messages.check_history_item_button(
            check_id=check.id,
            status=_check_status_label(i18n=i18n, status=check.status),
            stars=check.stars_count,
            amount=price_usd_for_cents(check.amount_cents),
        )
    )


def _claim_username_view(i18n: Any, *, username: str | None) -> str:
    if username is None:
        return str(i18n.messages.check_claim_username_any())
    return f"@{username}"


def _password_view(i18n: Any, *, has_password: bool) -> str:
    return str(
        i18n.messages.check_claim_password_set()
        if has_password
        else i18n.messages.check_claim_password_empty()
    )


def _check_status_label(i18n: Any, *, status: CheckStatus) -> str:
    if status == CheckStatus.ACTIVE:
        return str(i18n.messages.check_status_active())
    if status == CheckStatus.PROCESSING:
        return str(i18n.messages.check_status_processing())
    if status == CheckStatus.REDEEMED:
        return str(i18n.messages.check_status_redeemed())
    if status == CheckStatus.CLOSED:
        return str(i18n.messages.check_status_closed())
    return str(status.value)


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


def _check_claim_code(dialog_manager: DialogManager) -> str | None:
    raw_start_data = dialog_manager.start_data
    if not isinstance(raw_start_data, dict):
        return None
    raw_code = raw_start_data.get("check_code")
    if not isinstance(raw_code, str):
        return None
    code = raw_code.strip().lower()
    return code if CheckService.is_valid_code(code) else None


async def checks_list_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    service = check_service(dialog_manager=dialog_manager)
    page = checks_page(dialog_manager)

    checks, has_next, total_pages = await service.list_active_page(
        creator_id=user.id,
        page=page,
        page_size=CHECKS_PAGE_SIZE,
    )
    if page > 0 and page >= total_pages:
        page = max(0, total_pages - 1)
        set_checks_page(dialog_manager, page)
        checks, has_next, total_pages = await service.list_active_page(
            creator_id=user.id,
            page=page,
            page_size=CHECKS_PAGE_SIZE,
        )

    items = [
        {
            "id": str(check.id),
            "button_text": _check_item_button_text(i18n=i18n, check=check),
        }
        for check in checks
    ]
    text = (
        str(
            i18n.messages.checks_list_screen(
                active_count=len(items),
                page=page + 1,
            )
        )
        if items
        else str(i18n.messages.checks_list_empty_screen())
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "checks"),
        "checks": items,
        "create_stars_text": i18n.buttons.checks_create_stars(),
        "create_from_chat_text": i18n.buttons.checks_create_from_chat(),
        "create_from_chat_query": "",
        "history_button_text": i18n.buttons.checks_history(),
        "prev_button_text": _INVISIBLE_BUTTON_TEXT,
        "page_button_text": i18n.messages.checks_page_indicator(
            current=page + 1,
            total=total_pages,
        ),
        "next_button_text": _INVISIBLE_BUTTON_TEXT,
        "show_prev_page": page > 0,
        "show_next_page": has_next,
        "show_page_info": bool(items),
        "back_button_text": i18n.buttons.back_to_profile(),
    }


async def checks_details_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = await current_user(dialog_manager=dialog_manager)
    service = check_service(dialog_manager=dialog_manager)
    selected_id = selected_check_id(dialog_manager)
    check = None
    if selected_id is not None:
        check = await service.get_creator_check(
            creator_id=user.id,
            check_id=selected_id,
        )

    check_url = ""
    share_query = ""
    text: str
    if check is None:
        text = str(i18n.messages.check_detail_not_found())
    else:
        bot_username = await _resolve_bot_username(dialog_manager)
        check_url = CheckService.build_start_link(bot_username=bot_username, code=check.code)
        share_query = f"c_{check.code}"
        text = str(
            i18n.messages.check_detail_screen(
                check_id=check.id,
                stars=check.stars_count,
                amount=price_usd_for_cents(check.amount_cents),
                claim_username=_claim_username_view(i18n=i18n, username=check.claim_username),
                has_password=_password_view(
                    i18n=i18n,
                    has_password=bool(check.claim_password_hash),
                ),
                created=_format_tg_time(check.created_at),
                link=check_url,
            )
        )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "checks"),
        "share_query": share_query,
        "show_actions": check is not None and check.status == CheckStatus.ACTIVE,
        "share_text": i18n.buttons.checks_share(),
        "settings_text": i18n.buttons.checks_settings(),
        "close_text": i18n.buttons.checks_close(),
        "back_to_list_text": i18n.buttons.checks_back_to_list(),
        "back_button_text": i18n.buttons.back_to_profile(),
    }


async def checks_history_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    service = check_service(dialog_manager=dialog_manager)
    page = checks_history_page(dialog_manager)

    checks, has_next, total_pages = await service.list_recent_page(
        creator_id=user.id,
        page=page,
        page_size=CHECKS_HISTORY_PAGE_SIZE,
    )
    if page > 0 and page >= total_pages:
        page = max(0, total_pages - 1)
        set_checks_history_page(dialog_manager, page)
        checks, has_next, total_pages = await service.list_recent_page(
            creator_id=user.id,
            page=page,
            page_size=CHECKS_HISTORY_PAGE_SIZE,
        )

    items = [
        {
            "id": str(check.id),
            "button_text": _check_history_item_button_text(i18n=i18n, check=check),
        }
        for check in checks
    ]
    text = (
        str(
            i18n.messages.checks_history_list_screen(
                total_count=len(items),
                page=page + 1,
            )
        )
        if items
        else str(i18n.messages.checks_history_list_empty_screen())
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "checks"),
        "checks": items,
        "prev_button_text": _INVISIBLE_BUTTON_TEXT,
        "page_button_text": i18n.messages.checks_history_page_indicator(
            current=page + 1,
            total=total_pages,
        ),
        "next_button_text": _INVISIBLE_BUTTON_TEXT,
        "show_prev_page": page > 0,
        "show_next_page": has_next,
        "show_page_info": bool(items),
        "back_to_checks_text": i18n.buttons.checks_back_to_list(),
        "back_button_text": i18n.buttons.back_to_profile(),
    }


async def checks_history_details_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = await current_user(dialog_manager=dialog_manager)
    service = check_service(dialog_manager=dialog_manager)
    selected_id = checks_history_selected_check_id(dialog_manager)
    check = None
    if selected_id is not None:
        check = await service.get_creator_check(
            creator_id=user.id,
            check_id=selected_id,
        )

    if check is None:
        text = str(i18n.messages.check_detail_not_found())
    else:
        bot_username = await _resolve_bot_username(dialog_manager)
        check_url = CheckService.build_start_link(bot_username=bot_username, code=check.code)
        text = str(
            i18n.messages.check_history_detail_screen(
                check_id=check.id,
                status=_check_status_label(i18n=i18n, status=check.status),
                stars=check.stars_count,
                amount=price_usd_for_cents(check.amount_cents),
                claim_username=_claim_username_view(i18n=i18n, username=check.claim_username),
                has_password=_password_view(
                    i18n=i18n,
                    has_password=bool(check.claim_password_hash),
                ),
                recipient_id=check.recipient_id if check.recipient_id is not None else "—",
                tx_hash=secret_code_view(check.provider_tx_hash),
                last_error=check.last_error or "—",
                created=_format_tg_time(check.created_at),
                redeemed=_format_tg_time(check.redeemed_at),
                closed=_format_tg_time(check.closed_at),
                link=check_url,
            )
        )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "checks"),
        "back_to_history_text": i18n.buttons.checks_history_back_to_list(),
        "back_button_text": i18n.buttons.back_to_profile(),
    }


async def checks_create_stars_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    text = str(
        i18n.messages.checks_create_stars_screen(
            min_stars=MIN_STARS_COUNT,
            max_stars=MAX_STARS_COUNT,
        )
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "checks"),
        "back_button_text": i18n.buttons.checks_back_to_list(),
    }


async def checks_create_recipient_getter(
    dialog_manager: DialogManager, **_: Any
) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    current_username = checks_create_claim_username(dialog_manager)
    text = str(
        i18n.messages.checks_create_recipient_screen(
            recipient=(
                _claim_username_view(i18n=i18n, username=current_username)
                if current_username is not None
                else str(i18n.messages.check_claim_username_any())
            ),
        )
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "checks"),
        "skip_button_text": i18n.buttons.checks_skip_recipient(),
        "back_button_text": i18n.buttons.checks_back_to_amount(),
    }


async def checks_create_password_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    current_password = checks_create_claim_password(dialog_manager)
    text = str(
        i18n.messages.checks_create_password_screen(
            status=_password_view(i18n=i18n, has_password=bool(current_password)),
        )
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "checks"),
        "skip_button_text": i18n.buttons.checks_skip_password(),
        "back_button_text": i18n.buttons.checks_back_to_recipient(),
    }


async def checks_create_confirm_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    stars_count = checks_create_stars_count(dialog_manager)
    claim_username = checks_create_claim_username(dialog_manager)
    claim_password = checks_create_claim_password(dialog_manager)
    if stars_count is None:
        text = str(
            i18n.messages.check_create_stars_invalid(
                min_stars=MIN_STARS_COUNT,
                max_stars=MAX_STARS_COUNT,
            )
        )
    else:
        pack = get_stars_pack(str(stars_count))
        text = str(
            i18n.messages.checks_create_confirm_screen(
                stars=pack.stars_count,
                amount=pack.price_usd,
                claim_username=_claim_username_view(i18n=i18n, username=claim_username),
                has_password=_password_view(i18n=i18n, has_password=bool(claim_password)),
            )
        )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "checks"),
        "confirm_text": i18n.buttons.checks_finalize_create(),
        "change_amount_text": i18n.buttons.checks_change_amount(),
        "change_recipient_text": i18n.buttons.checks_change_recipient(),
        "change_password_text": i18n.buttons.checks_change_password(),
        "back_button_text": i18n.buttons.checks_back_to_list(),
        "can_confirm": stars_count is not None,
    }


async def checks_settings_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = await current_user(dialog_manager=dialog_manager)
    service = check_service(dialog_manager=dialog_manager)
    selected_id = selected_check_id(dialog_manager)
    check = None
    if selected_id is not None:
        check = await service.get_creator_check(
            creator_id=user.id,
            check_id=selected_id,
        )
    if check is None:
        text = str(i18n.messages.check_detail_not_found())
    else:
        text = str(
            i18n.messages.check_settings_screen(
                check_id=check.id,
                claim_username=_claim_username_view(i18n=i18n, username=check.claim_username),
                has_password=_password_view(
                    i18n=i18n,
                    has_password=bool(check.claim_password_hash),
                ),
            )
        )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "checks"),
        "edit_recipient_text": i18n.buttons.checks_edit_recipient(),
        "edit_password_text": i18n.buttons.checks_edit_password(),
        "back_button_text": i18n.buttons.checks_back_to_details(),
        "show_actions": check is not None,
    }


async def checks_edit_recipient_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    text = str(i18n.messages.check_settings_edit_recipient_screen())
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "checks"),
        "clear_button_text": i18n.buttons.checks_clear_recipient(),
        "back_button_text": i18n.buttons.checks_back_to_settings(),
    }


async def checks_edit_password_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    text = str(i18n.messages.check_settings_edit_password_screen())
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "checks"),
        "clear_button_text": i18n.buttons.checks_clear_password(),
        "back_button_text": i18n.buttons.checks_back_to_settings(),
    }


async def checks_claim_password_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    service = check_service(dialog_manager=dialog_manager)
    claim_code = _check_claim_code(dialog_manager)
    check = await service.get_by_code(code=claim_code) if claim_code else None
    if check is None:
        text = str(i18n.messages.check_claim_not_found())
    else:
        text = str(
            i18n.messages.check_claim_password_required_screen(
                stars=check.stars_count,
                amount=price_usd_for_cents(check.amount_cents),
            )
        )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "checks"),
        "cancel_button_text": i18n.buttons.back_to_menu(),
    }


__all__ = [
    "checks_claim_password_getter",
    "checks_create_password_getter",
    "checks_create_confirm_getter",
    "checks_create_recipient_getter",
    "checks_create_stars_getter",
    "checks_details_getter",
    "checks_edit_password_getter",
    "checks_edit_recipient_getter",
    "checks_history_details_getter",
    "checks_history_getter",
    "checks_list_getter",
    "checks_settings_getter",
]
