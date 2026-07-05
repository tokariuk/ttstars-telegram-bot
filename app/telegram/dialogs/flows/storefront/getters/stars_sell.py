from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Final

from aiogram_dialog import DialogManager

from app.enums.stars_sell_order import StarsSellOrderStatus
from app.stars import price_usd_for_cents
from app.telegram.dialogs.common import get_i18n, get_user
from app.utils.time import datetime_now

from ..handlers.shared import (
    set_stars_sell_history_page,
    stars_sell_count,
    stars_sell_history_page,
    stars_sell_history_selected_order_id,
    stars_sell_order_service,
    stars_sell_wallet,
)
from .common import banner_url, consume_notice

STARS_SELL_HISTORY_PAGE_SIZE: Final[int] = 6
_INVISIBLE_BUTTON_TEXT: Final[str] = "\u200b"


def _decimal_to_text(value: Decimal) -> str:
    return format(value.normalize(), "f")


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


def _status_text(*, dialog_manager: DialogManager, status: StarsSellOrderStatus) -> str:
    i18n = get_i18n(dialog_manager=dialog_manager)
    if status == StarsSellOrderStatus.PENDING_PAYMENT:
        return str(i18n.messages.stars_sell_status_pending_payment())
    if status == StarsSellOrderStatus.PAID_HOLD:
        return str(i18n.messages.stars_sell_status_paid_hold())
    if status == StarsSellOrderStatus.COMPLETED:
        return str(i18n.messages.stars_sell_status_completed())
    if status == StarsSellOrderStatus.CANCELED:
        return str(i18n.messages.stars_sell_status_canceled())
    if status == StarsSellOrderStatus.REJECTED:
        return str(i18n.messages.stars_sell_status_rejected())
    if status == StarsSellOrderStatus.REFUNDED:
        return str(i18n.messages.stars_sell_status_rejected())
    return str(i18n.messages.stars_sell_status_failed())


def _status_text_for_order(*, dialog_manager: DialogManager, order: Any) -> str:
    if (
        order.status == StarsSellOrderStatus.PAID_HOLD
        and order.payout_available_at is not None
        and order.payout_available_at <= datetime_now()
    ):
        i18n = get_i18n(dialog_manager=dialog_manager)
        return str(i18n.messages.stars_sell_status_paid_hold_ready())
    return _status_text(dialog_manager=dialog_manager, status=order.status)


async def stars_sell_menu_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    service = stars_sell_order_service(dialog_manager)
    text = str(
        i18n.messages.stars_sell_menu_screen(
            rate_usd=_decimal_to_text(service.usd_per_star)
        )
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"

    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "stars_sell"),
        "create_request_button_text": i18n.buttons.stars_sell_create_request(),
        "history_button_text": i18n.buttons.stars_sell_history(),
        "back_button_text": i18n.buttons.back_to_menu(),
    }


async def stars_sell_stars_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    service = stars_sell_order_service(dialog_manager)
    hold_days_text = str(i18n.messages.stars_sell_days(count=service.hold_days))
    text = str(
        i18n.messages.stars_sell_stars_screen(
            min_stars=service.min_stars,
            max_stars=service.max_stars,
            hold_days_text=hold_days_text,
        )
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"

    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "stars_sell"),
        "back_to_stars_sell_button_text": i18n.buttons.stars_sell_back_to_menu(),
        "back_to_menu_button_text": i18n.buttons.back_to_menu(),
    }


async def stars_sell_wallet_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    text = str(i18n.messages.stars_sell_wallet_screen())
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"

    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "stars_sell"),
        "change_stars_button_text": i18n.buttons.stars_sell_change_stars(),
        "back_to_stars_sell_button_text": i18n.buttons.stars_sell_back_to_menu(),
        "back_to_menu_button_text": i18n.buttons.back_to_menu(),
    }


async def stars_sell_payment_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    service = stars_sell_order_service(dialog_manager)
    selected_count = stars_sell_count(dialog_manager)
    wallet = stars_sell_wallet(dialog_manager)
    quote = (
        service.build_quote(stars_count=selected_count)
        if selected_count is not None
        else service.build_quote(stars_count=service.min_stars)
    )
    wallet_text = wallet or "—"
    hold_days_text = str(i18n.messages.stars_sell_days(count=quote.hold_days))

    text = str(
        i18n.messages.stars_sell_payment_screen(
            stars_count=quote.stars_count,
            payout_amount=price_usd_for_cents(quote.payout_amount_cents),
            wallet=wallet_text,
            hold_days_text=hold_days_text,
        )
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"

    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "stars_sell"),
        "send_invoice_button_text": i18n.buttons.stars_sell_send_invoice(),
        "change_stars_button_text": i18n.buttons.stars_sell_change_stars(),
        "change_wallet_button_text": i18n.buttons.stars_sell_change_wallet(),
        "back_to_stars_sell_button_text": i18n.buttons.stars_sell_back_to_menu(),
        "back_to_menu_button_text": i18n.buttons.back_to_menu(),
    }


async def stars_sell_history_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    service = stars_sell_order_service(dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    page = stars_sell_history_page(dialog_manager)

    orders, has_next, total_pages = await service.list_recent_page(
        user_id=user.id,
        page=page,
        page_size=STARS_SELL_HISTORY_PAGE_SIZE,
    )
    if page > 0 and page >= total_pages:
        page = max(0, total_pages - 1)
        set_stars_sell_history_page(dialog_manager, page)
        orders, has_next, total_pages = await service.list_recent_page(
            user_id=user.id,
            page=page,
            page_size=STARS_SELL_HISTORY_PAGE_SIZE,
        )

    items = [
        {
            "id": str(order.id),
            "button_text": str(
                i18n.messages.stars_sell_history_item_button(
                    order_id=order.id,
                    status=_status_text_for_order(dialog_manager=dialog_manager, order=order),
                    stars_count=order.stars_count,
                    payout_amount=price_usd_for_cents(order.payout_amount_cents),
                )
            ),
        }
        for order in orders
    ]

    text = (
        str(i18n.messages.stars_sell_history_list_screen())
        if items
        else str(i18n.messages.stars_sell_history_list_empty_screen())
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"

    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "stars_sell"),
        "orders": items,
        "prev_button_text": _INVISIBLE_BUTTON_TEXT,
        "page_button_text": i18n.messages.stars_sell_history_page_indicator(
            current=page + 1,
            total=total_pages,
        ),
        "next_button_text": _INVISIBLE_BUTTON_TEXT,
        "show_prev_page": page > 0,
        "show_next_page": has_next,
        "show_page_info": bool(items),
        "back_to_stars_sell_button_text": i18n.buttons.stars_sell_back_to_menu(),
        "back_to_menu_button_text": i18n.buttons.back_to_menu(),
    }


async def stars_sell_history_details_getter(
    dialog_manager: DialogManager,
    **_: Any,
) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    service = stars_sell_order_service(dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    selected_id = stars_sell_history_selected_order_id(dialog_manager)

    order = None
    if selected_id is not None:
        order = await service.get_user_order(user_id=user.id, order_id=selected_id)

    if order is None:
        text_body = str(i18n.messages.stars_sell_history_detail_not_found())
    else:
        paid_stars = order.paid_stars_amount if order.paid_stars_amount is not None else "—"
        text_body = str(
            i18n.messages.stars_sell_history_detail_screen(
                order_id=order.id,
                status=_status_text_for_order(dialog_manager=dialog_manager, order=order),
                stars_count=order.stars_count,
                payout_amount=price_usd_for_cents(order.payout_amount_cents),
                wallet=order.payout_wallet,
                invoice_stars=order.invoice_total_amount,
                invoice_payload=order.invoice_payload,
                paid_stars=paid_stars,
                created_at=_format_tg_time(order.created_at),
                paid_at=_format_tg_time(order.paid_at),
                payout_available_at=_format_tg_time(order.payout_available_at),
                completed_at=_format_tg_time(order.completed_at),
                rejected_at=_format_tg_time(order.rejected_at),
                refunded_at=_format_tg_time(order.refunded_at),
                failure_reason=order.failure_reason or "—",
                resolution_reason=order.resolution_reason.value
                if order.resolution_reason is not None
                else "—",
                resolution_note=order.resolution_note or "—",
            )
        )

    text = text_body
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"

    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "stars_sell"),
        "back_to_history_button_text": i18n.buttons.stars_sell_history_back_to_list(),
        "back_to_stars_sell_button_text": i18n.buttons.stars_sell_back_to_menu(),
        "back_to_menu_button_text": i18n.buttons.back_to_menu(),
    }


__all__ = [
    "stars_sell_history_details_getter",
    "stars_sell_history_getter",
    "stars_sell_menu_getter",
    "stars_sell_payment_getter",
    "stars_sell_stars_getter",
    "stars_sell_wallet_getter",
]
