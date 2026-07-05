from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Final

from aiogram_dialog import DialogManager

from app.enums.stars_sell_order import StarsSellOrderResolutionReason, StarsSellOrderStatus
from app.stars import price_usd_for_cents
from app.telegram.dialogs.common import get_user
from app.utils.time import datetime_now

from ..handlers.shared import (
    i18n,
    set_stars_sell_admin_page,
    set_stars_sell_history_page,
    stars_sell_admin_page,
    stars_sell_admin_selected_order_id,
    stars_sell_count,
    stars_sell_history_page,
    stars_sell_history_selected_order_id,
    stars_sell_order_service,
    stars_sell_wallet,
)
from .common import admin_banner_url, consume_notice, with_notice

STARS_SELL_HISTORY_PAGE_SIZE: Final[int] = 6
STARS_SELL_ADMIN_PAGE_SIZE: Final[int] = 6
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
    i18n_ctx = i18n(dialog_manager)
    if status == StarsSellOrderStatus.PENDING_PAYMENT:
        return str(i18n_ctx.messages.admin_stars_sell_status_pending_payment())
    if status == StarsSellOrderStatus.PAID_HOLD:
        return str(i18n_ctx.messages.admin_stars_sell_status_paid_hold())
    if status == StarsSellOrderStatus.COMPLETED:
        return str(i18n_ctx.messages.admin_stars_sell_status_completed())
    if status == StarsSellOrderStatus.CANCELED:
        return str(i18n_ctx.messages.admin_stars_sell_status_canceled())
    if status == StarsSellOrderStatus.REJECTED:
        return str(i18n_ctx.messages.admin_stars_sell_status_rejected())
    if status == StarsSellOrderStatus.REFUNDED:
        return str(i18n_ctx.messages.admin_stars_sell_status_rejected())
    return str(i18n_ctx.messages.admin_stars_sell_status_failed())


def _status_text_for_order(*, dialog_manager: DialogManager, order: Any) -> str:
    if (
        order.status == StarsSellOrderStatus.PAID_HOLD
        and order.payout_available_at is not None
        and order.payout_available_at <= datetime_now()
    ):
        i18n_ctx = i18n(dialog_manager)
        return str(i18n_ctx.messages.admin_stars_sell_status_paid_hold_ready())
    return _status_text(dialog_manager=dialog_manager, status=order.status)


def _resolution_reason_text(
    *,
    dialog_manager: DialogManager,
    reason: StarsSellOrderResolutionReason | None,
) -> str:
    i18n_ctx = i18n(dialog_manager)
    if reason is None:
        return "—"
    labels = {
        StarsSellOrderResolutionReason.REPLACED_BY_NEW_REQUEST: str(
            i18n_ctx.messages.admin_stars_sell_reason_replaced_by_new_request()
        ),
        StarsSellOrderResolutionReason.USER_REQUEST: str(
            i18n_ctx.messages.admin_stars_sell_reason_user_request()
        ),
        StarsSellOrderResolutionReason.INVALID_PAYOUT_WALLET: str(
            i18n_ctx.messages.admin_stars_sell_reason_invalid_payout_wallet()
        ),
        StarsSellOrderResolutionReason.STARS_REFUNDED: str(
            i18n_ctx.messages.admin_stars_sell_reason_stars_refunded()
        ),
        StarsSellOrderResolutionReason.STARS_NOT_WITHDRAWABLE: str(
            i18n_ctx.messages.admin_stars_sell_reason_stars_not_withdrawable()
        ),
        StarsSellOrderResolutionReason.FRAUD_SUSPECTED: str(
            i18n_ctx.messages.admin_stars_sell_reason_fraud_suspected()
        ),
        StarsSellOrderResolutionReason.KYC_OR_FRAGMENT_RESTRICTION: str(
            i18n_ctx.messages.admin_stars_sell_reason_kyc_or_fragment_restriction()
        ),
        StarsSellOrderResolutionReason.PAYOUT_TECHNICAL_FAILURE: str(
            i18n_ctx.messages.admin_stars_sell_reason_payout_technical_failure()
        ),
        StarsSellOrderResolutionReason.POLICY_RESTRICTION: str(
            i18n_ctx.messages.admin_stars_sell_reason_policy_restriction()
        ),
        StarsSellOrderResolutionReason.OTHER: str(
            i18n_ctx.messages.admin_stars_sell_reason_other()
        ),
    }
    return labels.get(reason, str(reason.value))


def _history_item_button_text(*, dialog_manager: DialogManager, order: Any) -> str:
    i18n_ctx = i18n(dialog_manager)
    return str(
        i18n_ctx.messages.admin_stars_sell_history_item_button(
            order_id=order.id,
            status=_status_text_for_order(dialog_manager=dialog_manager, order=order),
            stars_count=order.stars_count,
            payout_amount=price_usd_for_cents(order.payout_amount_cents),
        )
    )


def _admin_item_button_text(*, dialog_manager: DialogManager, order: Any) -> str:
    i18n_ctx = i18n(dialog_manager)
    return str(
        i18n_ctx.messages.admin_stars_sell_admin_item_button(
            order_id=order.id,
            user_id=order.user_id,
            status=_status_text_for_order(dialog_manager=dialog_manager, order=order),
            stars_count=order.stars_count,
            payout_amount=price_usd_for_cents(order.payout_amount_cents),
        )
    )


async def stars_sell_menu_getter(
    dialog_manager: DialogManager,
    **_: Any,
) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    service = stars_sell_order_service(dialog_manager)
    stats = await service.admin_stats()
    text = with_notice(
        text=str(
            i18n_ctx.messages.admin_stars_sell_menu_screen(
                total_orders=stats.total_orders,
                total_paid_stars=stats.total_paid_stars,
                ready_for_payout=stats.ready_for_payout_count,
                completed_payout=price_usd_for_cents(stats.completed_payout_cents),
            )
        ),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "banner_url": admin_banner_url(dialog_manager, "stars_sell"),
        "create_request_button_text": i18n_ctx.buttons.admin_stars_sell_create_request(),
        "history_button_text": i18n_ctx.buttons.admin_stars_sell_history(),
        "back_button_text": i18n_ctx.buttons.admin_stars_sell_back_to_admin_menu(),
    }


async def stars_sell_stars_getter(
    dialog_manager: DialogManager,
    **_: Any,
) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    service = stars_sell_order_service(dialog_manager)
    selected_count = stars_sell_count(dialog_manager)
    current_count = selected_count if selected_count is not None else service.min_stars
    hold_days_text = str(i18n_ctx.messages.admin_stars_sell_days(count=service.hold_days))
    text = with_notice(
        text=str(
            i18n_ctx.messages.admin_stars_sell_stars_screen(
                min_stars=service.min_stars,
                max_stars=service.max_stars,
                selected_stars=current_count,
                rate_usd=_decimal_to_text(service.usd_per_star),
                hold_days_text=hold_days_text,
            )
        ),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "banner_url": admin_banner_url(dialog_manager, "stars_sell"),
        "back_button_text": i18n_ctx.buttons.admin_stars_sell_back_to_admin_menu(),
    }


async def stars_sell_wallet_getter(
    dialog_manager: DialogManager,
    **_: Any,
) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    service = stars_sell_order_service(dialog_manager)
    selected_count = stars_sell_count(dialog_manager)
    quote = (
        service.build_quote(stars_count=selected_count)
        if selected_count is not None
        else service.build_quote(stars_count=service.min_stars)
    )
    current_wallet = stars_sell_wallet(dialog_manager) or "—"
    text = with_notice(
        text=str(
            i18n_ctx.messages.admin_stars_sell_wallet_screen(
                stars_count=quote.stars_count,
                payout_amount=price_usd_for_cents(quote.payout_amount_cents),
                wallet=current_wallet,
            )
        ),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "banner_url": admin_banner_url(dialog_manager, "stars_sell"),
        "change_stars_button_text": i18n_ctx.buttons.admin_stars_sell_change_stars(),
        "back_button_text": i18n_ctx.buttons.admin_stars_sell_back_to_admin_menu(),
    }


async def stars_sell_payment_getter(
    dialog_manager: DialogManager,
    **_: Any,
) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    service = stars_sell_order_service(dialog_manager)
    selected_count = stars_sell_count(dialog_manager)
    wallet = stars_sell_wallet(dialog_manager)
    quote = (
        service.build_quote(stars_count=selected_count)
        if selected_count is not None
        else service.build_quote(stars_count=service.min_stars)
    )
    wallet_text = wallet or "—"
    hold_days_text = str(i18n_ctx.messages.admin_stars_sell_days(count=quote.hold_days))

    text = with_notice(
        text=str(
            i18n_ctx.messages.admin_stars_sell_payment_screen(
                stars_count=quote.stars_count,
                payout_amount=price_usd_for_cents(quote.payout_amount_cents),
                wallet=wallet_text,
                hold_days_text=hold_days_text,
                invoice_stars=quote.invoice_total_amount,
            )
        ),
        notice=consume_notice(dialog_manager),
    )

    return {
        "text": text,
        "banner_url": admin_banner_url(dialog_manager, "stars_sell"),
        "send_invoice_button_text": i18n_ctx.buttons.admin_stars_sell_send_invoice(),
        "change_stars_button_text": i18n_ctx.buttons.admin_stars_sell_change_stars(),
        "change_wallet_button_text": i18n_ctx.buttons.admin_stars_sell_change_wallet(),
        "back_button_text": i18n_ctx.buttons.admin_stars_sell_back_to_admin_menu(),
    }


async def stars_sell_history_getter(
    dialog_manager: DialogManager,
    **_: Any,
) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
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
            "button_text": _history_item_button_text(dialog_manager=dialog_manager, order=order),
        }
        for order in orders
    ]

    text = with_notice(
        text=(
            str(i18n_ctx.messages.admin_stars_sell_history_list_screen(page=page + 1))
            if items
            else str(i18n_ctx.messages.admin_stars_sell_history_list_empty_screen())
        ),
        notice=consume_notice(dialog_manager),
    )

    return {
        "text": text,
        "banner_url": admin_banner_url(dialog_manager, "stars_sell"),
        "orders": items,
        "prev_button_text": _INVISIBLE_BUTTON_TEXT,
        "page_button_text": i18n_ctx.messages.admin_stars_sell_history_page_indicator(
            current=page + 1,
            total=total_pages,
        ),
        "next_button_text": _INVISIBLE_BUTTON_TEXT,
        "show_prev_page": page > 0,
        "show_next_page": has_next,
        "show_page_info": bool(items),
        "back_to_menu_button_text": i18n_ctx.buttons.admin_stars_sell_back_to_menu(),
        "back_button_text": i18n_ctx.buttons.admin_stars_sell_back_to_admin_menu(),
    }


async def stars_sell_history_details_getter(
    dialog_manager: DialogManager,
    **_: Any,
) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    service = stars_sell_order_service(dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    selected_id = stars_sell_history_selected_order_id(dialog_manager)

    order = None
    if selected_id is not None:
        order = await service.get_user_order(user_id=user.id, order_id=selected_id)

    if order is None:
        text_body = str(i18n_ctx.messages.admin_stars_sell_history_detail_not_found())
    else:
        paid_stars = order.paid_stars_amount if order.paid_stars_amount is not None else "—"
        text_body = str(
            i18n_ctx.messages.admin_stars_sell_history_detail_screen(
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
                resolution_reason=_resolution_reason_text(
                    dialog_manager=dialog_manager,
                    reason=order.resolution_reason,
                ),
                resolution_note=order.resolution_note or "—",
            )
        )

    text = with_notice(text=text_body, notice=consume_notice(dialog_manager))
    return {
        "text": text,
        "banner_url": admin_banner_url(dialog_manager, "stars_sell"),
        "back_to_history_button_text": i18n_ctx.buttons.admin_stars_sell_history_back_to_list(),
        "back_button_text": i18n_ctx.buttons.admin_stars_sell_back_to_admin_menu(),
    }


async def stars_sell_admin_list_getter(
    dialog_manager: DialogManager,
    **_: Any,
) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    service = stars_sell_order_service(dialog_manager)
    page = stars_sell_admin_page(dialog_manager)

    orders, has_next, total_pages = await service.list_admin_page(
        page=page,
        page_size=STARS_SELL_ADMIN_PAGE_SIZE,
    )
    if page > 0 and page >= total_pages:
        page = max(0, total_pages - 1)
        set_stars_sell_admin_page(dialog_manager, page)
        orders, has_next, total_pages = await service.list_admin_page(
            page=page,
            page_size=STARS_SELL_ADMIN_PAGE_SIZE,
        )

    items = [
        {
            "id": str(order.id),
            "button_text": _admin_item_button_text(dialog_manager=dialog_manager, order=order),
        }
        for order in orders
    ]

    text = with_notice(
        text=(
            str(i18n_ctx.messages.admin_stars_sell_admin_list_screen(page=page + 1))
            if items
            else str(i18n_ctx.messages.admin_stars_sell_admin_list_empty_screen())
        ),
        notice=consume_notice(dialog_manager),
    )

    return {
        "text": text,
        "orders": items,
        "prev_button_text": "‹",
        "page_button_text": i18n_ctx.messages.admin_stars_sell_admin_page_indicator(
            current=page + 1,
            total=total_pages,
        ),
        "next_button_text": "›",
        "show_prev_page": page > 0,
        "show_next_page": has_next,
        "show_page_info": bool(items),
        "back_to_menu_button_text": i18n_ctx.buttons.admin_stars_sell_back_to_menu(),
        "back_button_text": i18n_ctx.buttons.admin_stars_sell_back_to_admin_menu(),
    }


async def stars_sell_admin_details_getter(
    dialog_manager: DialogManager,
    **_: Any,
) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    service = stars_sell_order_service(dialog_manager)
    selected_id = stars_sell_admin_selected_order_id(dialog_manager)

    order = None
    if selected_id is not None:
        order = await service.get(order_id=selected_id)

    if order is None:
        text_body = str(i18n_ctx.messages.admin_stars_sell_admin_detail_not_found())
        show_complete_action = False
        show_reject_action = False
    else:
        paid_stars = order.paid_stars_amount if order.paid_stars_amount is not None else "—"
        text_body = str(
            i18n_ctx.messages.admin_stars_sell_admin_detail_screen(
                order_id=order.id,
                user_id=order.user_id,
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
                resolution_reason=_resolution_reason_text(
                    dialog_manager=dialog_manager,
                    reason=order.resolution_reason,
                ),
                resolution_note=order.resolution_note or "—",
            )
        )
        show_complete_action = order.status == StarsSellOrderStatus.PAID_HOLD
        show_reject_action = order.status in {
            StarsSellOrderStatus.PENDING_PAYMENT,
            StarsSellOrderStatus.PAID_HOLD,
        }

    text = with_notice(text=text_body, notice=consume_notice(dialog_manager))
    return {
        "text": text,
        "show_complete_action": show_complete_action,
        "show_reject_action": show_reject_action,
        "complete_button_text": i18n_ctx.buttons.admin_stars_sell_admin_complete(),
        "reject_button_text": i18n_ctx.buttons.admin_stars_sell_admin_reject(),
        "back_to_admin_list_button_text": i18n_ctx.buttons.admin_stars_sell_admin_back_to_list(),
        "back_button_text": i18n_ctx.buttons.admin_stars_sell_back_to_admin_menu(),
    }


__all__ = [
    "stars_sell_admin_details_getter",
    "stars_sell_admin_list_getter",
    "stars_sell_history_details_getter",
    "stars_sell_history_getter",
    "stars_sell_menu_getter",
    "stars_sell_payment_getter",
    "stars_sell_stars_getter",
    "stars_sell_wallet_getter",
]
