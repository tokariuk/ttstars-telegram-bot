from __future__ import annotations

from typing import Any

from app.enums.stars_order import StarsOrderProductType, StarsOrderStatus
from app.utils.time import datetime_now

_UNPAID_TERMINAL_PROVIDER_STATUSES: set[str] = {
    "canceled",
    "cancelled",
    "expired",
}


async def force_fulfill_order(
    *,
    service: Any,
    order_id: int,
    outcome_enum: Any,
    result_cls: type,
) -> Any:
    order = await service.get(order_id=order_id)
    if order is None:
        return result_cls(outcome=outcome_enum.NO_PENDING)

    if order.status == StarsOrderStatus.CANCELED:
        return result_cls(outcome=outcome_enum.CANCELED, order=order)
    if order.status == StarsOrderStatus.COMPLETED:
        return result_cls(outcome=outcome_enum.COMPLETED, order=order)

    current = order
    topup_result = _force_topup_precheck(
        current=current,
        outcome_enum=outcome_enum,
        result_cls=result_cls,
    )
    if topup_result is not None:
        return topup_result

    if current.status == StarsOrderStatus.FAILED:
        reopen_result = await _force_reopen_failed(
            service=service,
            current=current,
            outcome_enum=outcome_enum,
            result_cls=result_cls,
        )
        if not isinstance(reopen_result, tuple):
            return reopen_result
        current = reopen_result[0]

    elif current.status in {
        StarsOrderStatus.CREATING_PAYMENT,
        StarsOrderStatus.PENDING_PAYMENT,
    }:
        forced_paid = await service._update_order(
            order_id=current.id,
            status=StarsOrderStatus.PAYMENT_CONFIRMED,
            paid_at=current.paid_at or datetime_now(),
            provider_status="force_marked_paid",
        )
        if forced_paid is not None:
            current = forced_paid

    if current.status in {
        StarsOrderStatus.PAYMENT_CONFIRMED,
        StarsOrderStatus.FULFILLING,
    }:
        fulfilled = await service._fulfill_paid_order(order_id=current.id)
        return _result_for_fulfilled(
            fulfilled=fulfilled,
            outcome_enum=outcome_enum,
            result_cls=result_cls,
        )

    return result_cls(
        outcome=outcome_enum.PROCESSING,
        order=current,
    )


async def verify_order(
    *,
    service: Any,
    order_id: int,
    outcome_enum: Any,
    result_cls: type,
) -> Any:
    order = await service.get(order_id=order_id)
    if order is None:
        return result_cls(outcome=outcome_enum.NO_PENDING)

    terminal = _terminal_result(
        order=order,
        outcome_enum=outcome_enum,
        result_cls=result_cls,
    )
    if terminal is not None:
        return terminal

    if order.status in {
        StarsOrderStatus.CREATING_PAYMENT,
        StarsOrderStatus.PENDING_PAYMENT,
    }:
        pending_result = await _verify_pending_payment(
            service=service,
            order=order,
            outcome_enum=outcome_enum,
            result_cls=result_cls,
        )
        if not isinstance(pending_result, tuple):
            return pending_result
        order = pending_result[0]

    if order.status in {
        StarsOrderStatus.PAYMENT_CONFIRMED,
        StarsOrderStatus.FULFILLING,
    }:
        fulfilled = await service._fulfill_paid_order(order_id=order.id)
        if fulfilled.status == StarsOrderStatus.COMPLETED:
            return result_cls(
                outcome=outcome_enum.COMPLETED,
                order=fulfilled,
            )
        if fulfilled.status == StarsOrderStatus.FAILED:
            return result_cls(outcome=outcome_enum.FAILED, order=fulfilled)
        return result_cls(outcome=outcome_enum.PROCESSING, order=fulfilled)

    return result_cls(outcome=outcome_enum.PROCESSING, order=order)


def _terminal_result(*, order: Any, outcome_enum: Any, result_cls: type) -> Any | None:
    if order.status == StarsOrderStatus.CANCELED:
        return result_cls(outcome=outcome_enum.CANCELED, order=order)
    if order.status == StarsOrderStatus.COMPLETED:
        return result_cls(outcome=outcome_enum.COMPLETED, order=order)
    if order.status == StarsOrderStatus.FAILED:
        return result_cls(outcome=outcome_enum.FAILED, order=order)
    return None


def _is_unpaid_terminal_provider_status(provider_status: str) -> bool:
    return provider_status.strip().lower() in _UNPAID_TERMINAL_PROVIDER_STATUSES


async def _verify_pending_payment(
    *,
    service: Any,
    order: Any,
    outcome_enum: Any,
    result_cls: type,
) -> tuple[Any] | Any:
    is_paid, provider_status = await service._is_order_paid(order=order)
    order = await service._update_order(
        order_id=order.id,
        provider_status=provider_status,
    )
    if order is None:
        return result_cls(outcome=outcome_enum.FAILED)
    if not is_paid:
        return await _pending_unpaid_result(
            service=service,
            order=order,
            provider_status=provider_status,
            outcome_enum=outcome_enum,
            result_cls=result_cls,
        )
    transitioned = await service._transition_order_status(
        order_id=order.id,
        from_statuses=[StarsOrderStatus.CREATING_PAYMENT, StarsOrderStatus.PENDING_PAYMENT],
        to_status=StarsOrderStatus.PAYMENT_CONFIRMED,
        paid_at=datetime_now(),
    )
    return (transitioned or order,)


async def _pending_unpaid_result(
    *,
    service: Any,
    order: Any,
    provider_status: str,
    outcome_enum: Any,
    result_cls: type,
) -> Any:
    canceled_result = await _cancel_if_unpaid_terminal_provider_status(
        service=service,
        order=order,
        provider_status=provider_status,
        outcome_enum=outcome_enum,
        result_cls=result_cls,
    )
    if canceled_result is not None:
        return canceled_result
    return result_cls(
        outcome=outcome_enum.PENDING,
        order=order,
        provider_status=provider_status,
    )


async def _cancel_if_unpaid_terminal_provider_status(
    *,
    service: Any,
    order: Any,
    provider_status: str,
    outcome_enum: Any,
    result_cls: type,
) -> Any | None:
    if not _is_unpaid_terminal_provider_status(provider_status):
        return None
    canceled = await service._transition_order_status(
        order_id=order.id,
        from_statuses=[
            StarsOrderStatus.CREATING_PAYMENT,
            StarsOrderStatus.PENDING_PAYMENT,
        ],
        to_status=StarsOrderStatus.CANCELED,
        provider_status=provider_status,
        canceled_at=datetime_now(),
    )
    return result_cls(
        outcome=outcome_enum.CANCELED,
        order=canceled or order,
        provider_status=provider_status,
    )


def _force_topup_precheck(*, current: Any, outcome_enum: Any, result_cls: type) -> Any | None:
    if current.product_type != StarsOrderProductType.TOPUP:
        return None
    if current.status not in {
        StarsOrderStatus.CREATING_PAYMENT,
        StarsOrderStatus.PENDING_PAYMENT,
        StarsOrderStatus.FAILED,
    }:
        return None
    if current.status == StarsOrderStatus.FAILED:
        return result_cls(outcome=outcome_enum.FAILED, order=current)
    if current.status == StarsOrderStatus.PENDING_PAYMENT:
        return result_cls(outcome=outcome_enum.PENDING, order=current)
    return result_cls(outcome=outcome_enum.PROCESSING, order=current)


async def _force_reopen_failed(
    *,
    service: Any,
    current: Any,
    outcome_enum: Any,
    result_cls: type,
) -> tuple[Any] | Any:
    if (
        current.provider_status == "delivery_failed_refunded_to_balance"
        and current.amount_cents > 0
    ):
        debited = await service._debit_user_balance_if_enough(
            user_id=current.user_id,
            amount_cents=current.amount_cents,
        )
        if not debited:
            return result_cls(
                outcome=outcome_enum.FAILED,
                order=current,
                provider_status="force_debit_failed",
            )

    reopened = await service._update_order(
        order_id=current.id,
        status=StarsOrderStatus.PAYMENT_CONFIRMED,
        paid_at=current.paid_at or datetime_now(),
        failed_at=None,
        fragment_error=None,
        provider_status="force_retry_after_failed",
    )
    if reopened is None:
        latest = await service.get(order_id=current.id)
        return result_cls(
            outcome=outcome_enum.PROCESSING,
            order=latest or current,
            provider_status="force_reopen_failed",
        )
    return (reopened,)


def _result_for_fulfilled(*, fulfilled: Any, outcome_enum: Any, result_cls: type) -> Any:
    if fulfilled.status == StarsOrderStatus.COMPLETED:
        return result_cls(
            outcome=outcome_enum.COMPLETED,
            order=fulfilled,
        )
    if fulfilled.status == StarsOrderStatus.FAILED:
        return result_cls(
            outcome=outcome_enum.FAILED,
            order=fulfilled,
        )
    if fulfilled.status == StarsOrderStatus.CANCELED:
        return result_cls(
            outcome=outcome_enum.CANCELED,
            order=fulfilled,
        )
    return result_cls(
        outcome=outcome_enum.PROCESSING,
        order=fulfilled,
    )
