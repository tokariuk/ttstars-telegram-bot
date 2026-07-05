from __future__ import annotations

from datetime import timezone
from typing import Any, Final

from aiogram_dialog import DialogManager

from app.services.promo_codes import PromoCodeInfo
from app.stars import price_usd_for_cents

from ..handlers.shared import (
    clear_promo_bulk_selected_codes,
    i18n,
    promo_bulk_mode,
    promo_bulk_selected_codes,
    promo_page,
    promo_selected_code,
    promo_service,
    set_promo_bulk_selected_codes,
    set_promo_page,
)
from .common import consume_notice, with_notice

PROMO_PAGE_SIZE: Final[int] = 8
PROMO_LIST_LIMIT: Final[int] = 250


def _is_active(code: PromoCodeInfo) -> bool:
    if code.max_activations is None:
        return True
    return code.activations < code.max_activations


def _max_activations_text(*, code: PromoCodeInfo, i18n_ctx: Any) -> str:
    return (
        str(code.max_activations)
        if code.max_activations is not None
        else str(i18n_ctx.messages.admin_limit_unlimited())
    )


def _promo_button_text(
    *,
    code: PromoCodeInfo,
    i18n_ctx: Any,
    is_bulk_mode: bool,
    is_selected: bool,
) -> str:
    base = str(
        i18n_ctx.messages.admin_promo_item_button(
            code=code.code,
            amount=price_usd_for_cents(code.amount_cents),
            activations=code.activations,
            max_activations=_max_activations_text(code=code, i18n_ctx=i18n_ctx),
        )
    )
    if not is_bulk_mode:
        return base
    marker = "☑️" if is_selected else "⬜️"
    return f"{marker} {base}"


def _format_created_at(code: PromoCodeInfo) -> str:
    dt_utc = (
        code.created_at.replace(tzinfo=timezone.utc)
        if code.created_at.tzinfo is None
        else code.created_at.astimezone(timezone.utc)
    )
    unix = int(dt_utc.timestamp())
    fallback = dt_utc.strftime("%Y-%m-%d %H:%M UTC")
    return f'<tg-time unix="{unix}" format="dt">{fallback}</tg-time>'


async def promo_menu_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    all_codes = await promo_service(dialog_manager).list_codes(limit=PROMO_LIST_LIMIT)
    active_codes = [code for code in all_codes if _is_active(code)]
    active_codes_set = {code.code for code in active_codes}
    is_bulk_mode = promo_bulk_mode(dialog_manager)
    selected_codes = promo_bulk_selected_codes(dialog_manager)
    selected_active_codes = [code for code in selected_codes if code in active_codes_set]
    if selected_active_codes != selected_codes:
        if selected_active_codes:
            set_promo_bulk_selected_codes(dialog_manager, selected_active_codes)
        else:
            clear_promo_bulk_selected_codes(dialog_manager)
    selected_set = set(selected_active_codes)

    page = promo_page(dialog_manager)
    total_pages = max(1, (len(active_codes) + PROMO_PAGE_SIZE - 1) // PROMO_PAGE_SIZE)
    if page >= total_pages:
        page = total_pages - 1
        set_promo_page(dialog_manager, page)

    start = page * PROMO_PAGE_SIZE
    page_codes = active_codes[start : start + PROMO_PAGE_SIZE]
    codes_items = [
        {
            "id": code.code,
            "button_text": _promo_button_text(
                code=code,
                i18n_ctx=i18n_ctx,
                is_bulk_mode=is_bulk_mode,
                is_selected=code.code in selected_set,
            ),
        }
        for code in page_codes
    ]

    base_text = str(
        i18n_ctx.messages.admin_promo_menu(
            active_codes=len(active_codes),
            total_codes=len(all_codes),
        )
    )
    if not codes_items:
        base_text = f"{base_text}\n\n{str(i18n_ctx.messages.admin_promo_list_empty())}"
    if is_bulk_mode:
        base_text = (
            f"{base_text}\n\n"
            f"{str(i18n_ctx.messages.admin_promo_bulk_mode_hint(selected=len(selected_set)))}"
        )

    text = with_notice(
        text=base_text,
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "codes": codes_items,
        "create_button_text": i18n_ctx.buttons.admin_create(),
        "quick_button_text": i18n_ctx.buttons.admin_quick_unique(),
        "bulk_button_text": i18n_ctx.buttons.admin_bulk_unique(),
        "bulk_mode_button_text": (
            i18n_ctx.buttons.admin_bulk_delete_cancel()
            if is_bulk_mode
            else i18n_ctx.buttons.admin_bulk_delete_mode()
        ),
        "bulk_delete_selected_button_text": i18n_ctx.buttons.admin_bulk_delete_selected(
            count=len(selected_set),
        ),
        "cleanup_button_text": i18n_ctx.buttons.admin_cleanup_exhausted(),
        "prev_button_text": i18n_ctx.buttons.admin_promo_prev(),
        "page_button_text": i18n_ctx.messages.admin_promo_page_indicator(
            current=page + 1,
            total=total_pages,
        ),
        "next_button_text": i18n_ctx.buttons.admin_promo_next(),
        "show_prev_page": page > 0,
        "show_next_page": page + 1 < total_pages,
        "show_page_info": bool(active_codes),
        "show_cleanup": bool(all_codes),
        "show_bulk_delete_selected": is_bulk_mode and bool(selected_set),
        "back_button_text": i18n_ctx.buttons.admin_back_menu(),
    }


async def promo_details_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    selected = promo_selected_code(dialog_manager)
    code: PromoCodeInfo | None = None
    if selected is not None:
        code = await promo_service(dialog_manager).get_code(selected)

    if code is None:
        text_body = str(i18n_ctx.messages.admin_promo_not_found())
        has_code = False
    else:
        is_active = _is_active(code)
        text_body = str(
            i18n_ctx.messages.admin_promo_details(
                code=code.code,
                amount=price_usd_for_cents(code.amount_cents),
                activations=code.activations,
                max_activations=_max_activations_text(code=code, i18n_ctx=i18n_ctx),
                created_at=_format_created_at(code),
                status=(
                    str(i18n_ctx.messages.admin_promo_status_active())
                    if is_active
                    else str(i18n_ctx.messages.admin_promo_status_exhausted())
                ),
            )
        )
        has_code = True

    text = with_notice(
        text=text_body,
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "has_code": has_code,
        "set_one_time_button_text": i18n_ctx.buttons.admin_make_one_time(),
        "set_unlimited_button_text": i18n_ctx.buttons.admin_make_unlimited(),
        "set_custom_limit_button_text": i18n_ctx.buttons.admin_set_custom_limit(),
        "delete_button_text": i18n_ctx.buttons.admin_delete(),
        "back_to_list_button_text": i18n_ctx.buttons.admin_promo_back_to_list(),
        "back_button_text": i18n_ctx.buttons.admin_back_menu(),
    }


async def promo_create_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    text = with_notice(
        text=str(i18n_ctx.messages.admin_promo_create_prompt()),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "back_button_text": i18n_ctx.buttons.admin_promo_back_to_list(),
    }


async def promo_quick_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    text = with_notice(
        text=str(i18n_ctx.messages.admin_promo_quick_prompt()),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "back_button_text": i18n_ctx.buttons.admin_promo_back_to_list(),
    }


async def promo_bulk_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    text = with_notice(
        text=str(i18n_ctx.messages.admin_promo_bulk_prompt()),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "back_button_text": i18n_ctx.buttons.admin_promo_back_to_list(),
    }


async def promo_set_limit_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    selected_code = promo_selected_code(dialog_manager) or "CODE"
    text = with_notice(
        text=str(i18n_ctx.messages.admin_promo_set_limit_prompt(code=selected_code)),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "back_button_text": i18n_ctx.buttons.admin_promo_back_to_list(),
    }


__all__ = [
    "promo_bulk_getter",
    "promo_create_getter",
    "promo_details_getter",
    "promo_menu_getter",
    "promo_quick_getter",
    "promo_set_limit_getter",
]
