from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final

from aiogram_dialog import DialogManager

from app.enums.stars_order import StarsOrderProductType
from app.services.crud.stars_order import StarsOrderService
from app.telegram.dialogs.flows.storefront.handlers.shared import (
    history_page,
    history_selected_order_id,
    set_history_page,
)

from .common import (
    banner_url,
    get_i18n,
    get_user,
    price_usd_for_cents,
    product_label,
    provider_label,
    secret_code_view,
    status_label,
)

HISTORY_PAGE_SIZE: Final[int] = 6
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


def _history_product_button_text(
    i18n: Any,
    *,
    order_type: StarsOrderProductType,
    amount: int,
) -> str:
    if order_type == StarsOrderProductType.TOPUP:
        return str(i18n.messages.history_product_topup_button())
    if order_type == StarsOrderProductType.GIFT:
        return str(i18n.messages.history_product_gift_button())
    if order_type == StarsOrderProductType.PREMIUM:
        return str(i18n.messages.history_product_premium_button(months=amount))
    return str(i18n.messages.history_product_stars_button(stars=amount))


async def history_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    stars_order_service: StarsOrderService = dialog_manager.middleware_data["stars_order_service"]
    page = history_page(dialog_manager)

    orders, has_next, total_pages = await stars_order_service.list_recent_page(
        user_id=user.id,
        page=page,
        page_size=HISTORY_PAGE_SIZE,
    )
    if page > 0 and page >= total_pages:
        page = max(0, total_pages - 1)
        set_history_page(dialog_manager, page)
        orders, has_next, total_pages = await stars_order_service.list_recent_page(
            user_id=user.id,
            page=page,
            page_size=HISTORY_PAGE_SIZE,
        )

    operations = [
        {
            "id": str(order.id),
            "button_text": str(
                i18n.messages.history_operation_button(
                    order_id=order.id,
                    product=_history_product_button_text(
                        i18n=i18n,
                        order_type=order.product_type,
                        amount=(
                            order.premium_months or 0
                            if order.product_type == StarsOrderProductType.PREMIUM
                            else order.stars_count
                        ),
                    ),
                    amount=price_usd_for_cents(order.amount_cents),
                )
            ),
        }
        for order in orders
    ]

    text = (
        str(i18n.messages.history_list_screen(page=page + 1))
        if operations
        else str(i18n.messages.history_list_empty_screen())
    )
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "history"),
        "operations": operations,
        "prev_button_text": _INVISIBLE_BUTTON_TEXT,
        "page_button_text": i18n.messages.history_page_indicator(
            current=page + 1,
            total=total_pages,
        ),
        "next_button_text": _INVISIBLE_BUTTON_TEXT,
        "show_prev_page": page > 0,
        "show_next_page": has_next,
        "show_page_info": bool(operations),
        "back_button_text": i18n.buttons.back_to_profile(),
    }


async def history_details_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    stars_order_service: StarsOrderService = dialog_manager.middleware_data["stars_order_service"]
    selected_order_id = history_selected_order_id(dialog_manager)
    order = None
    if selected_order_id is not None:
        order = await stars_order_service.get_user_order(
            user_id=user.id,
            order_id=selected_order_id,
        )

    if order is None:
        text = str(i18n.messages.history_detail_not_found())
    else:
        recipient = (
            "—"
            if order.product_type == StarsOrderProductType.TOPUP
            else (
                f"<code>{order.recipient_user_id}</code>"
                if order.product_type == StarsOrderProductType.GIFT
                else f"@{order.recipient_username}"
            )
        )
        tx_hash = secret_code_view(order.fragment_tx_hash)
        provider_ref_raw = order.provider_reference or (
            str(order.provider_invoice_id) if order.provider_invoice_id is not None else None
        )
        provider_ref = secret_code_view(provider_ref_raw)
        text = str(
            i18n.messages.history_detail_screen(
                order_id=order.id,
                status=status_label(i18n=i18n, status=order.status),
                provider=provider_label(i18n=i18n, provider=order.payment_provider),
                product=product_label(i18n=i18n, order=order),
                recipient=recipient,
                amount=price_usd_for_cents(order.amount_cents),
                created=_format_tg_time(order.created_at),
                paid=_format_tg_time(order.paid_at),
                fulfilled=_format_tg_time(order.fulfilled_at),
                provider_ref=provider_ref,
                tx_hash=tx_hash,
            )
        )

    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "history"),
        "back_to_history_text": i18n.buttons.history_back_to_list(),
        "back_button_text": i18n.buttons.back_to_profile(),
    }


__all__ = [
    "history_details_getter",
    "history_getter",
]
