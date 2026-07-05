from __future__ import annotations

from typing import Any

from aiogram_dialog import DialogManager

from app.enums.stars_order import StarsOrderProductType, StarsOrderStatus

from ..handlers.shared import i18n, stars_order_service, user_service
from .common import consume_notice, price_usd_for_cents, with_notice


async def stats_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    users_service = user_service(dialog_manager)

    users_total = await users_service.count()
    users_active = await users_service.count_active()
    users_with_balance = await users_service.count_with_positive_balance()
    users_balance_total = await users_service.sum_balances_cents()

    order_stats = await stars_order_service(dialog_manager).admin_stats()
    status_counts = order_stats.status_counts
    products = order_stats.completed_products

    completed_stars = products[StarsOrderProductType.STARS]
    completed_premium = products[StarsOrderProductType.PREMIUM]
    completed_topup = products[StarsOrderProductType.TOPUP]

    text = with_notice(
        text=str(
            i18n_ctx.messages.admin_stats_screen(
                users_total=users_total,
                users_active=users_active,
                users_with_balance=users_with_balance,
                users_balance_total=price_usd_for_cents(users_balance_total),
                orders_total=order_stats.total_orders,
                orders_new_24h=order_stats.created_last_24h,
                orders_new_7d=order_stats.created_last_7d,
                orders_paid_24h=order_stats.paid_last_24h,
                orders_paid_7d=order_stats.paid_last_7d,
                orders_paid_amount_24h=price_usd_for_cents(
                    order_stats.paid_amount_last_24h_cents
                ),
                orders_paid_amount_7d=price_usd_for_cents(order_stats.paid_amount_last_7d_cents),
                orders_completed_amount=price_usd_for_cents(order_stats.completed_amount_cents),
                completed_stars_count=completed_stars.count,
                completed_stars_units=completed_stars.stars_count,
                completed_stars_amount=price_usd_for_cents(completed_stars.amount_cents),
                completed_premium_count=completed_premium.count,
                completed_premium_amount=price_usd_for_cents(completed_premium.amount_cents),
                completed_topup_count=completed_topup.count,
                completed_topup_amount=price_usd_for_cents(completed_topup.amount_cents),
                status_creating=status_counts[StarsOrderStatus.CREATING_PAYMENT],
                status_pending=status_counts[StarsOrderStatus.PENDING_PAYMENT],
                status_paid=status_counts[StarsOrderStatus.PAYMENT_CONFIRMED],
                status_fulfilling=status_counts[StarsOrderStatus.FULFILLING],
                status_completed=status_counts[StarsOrderStatus.COMPLETED],
                status_failed=status_counts[StarsOrderStatus.FAILED],
                status_canceled=status_counts[StarsOrderStatus.CANCELED],
            )
        ),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "back_button_text": i18n_ctx.buttons.admin_back_menu(),
    }


__all__ = ["stats_getter"]
