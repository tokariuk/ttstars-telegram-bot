from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

from app.enums.stars_order import StarsOrderStatus
from app.models.dto.balance_topup import BalanceTopupDto
from app.models.dto.stars_order import StarsOrderDto
from app.utils.time import datetime_now

if TYPE_CHECKING:
    from app.services.crud.stars_order import StarsOrderService

ResultT = TypeVar("ResultT")

TOPUP_ORDER_ID_OFFSET = 1_000_000_000

_UNPAID_TERMINAL_PROVIDER_STATUSES = {
    "canceled",
    "cancelled",
    "expired",
}


def encode_topup_order_id(*, topup_id: int) -> int:
    return TOPUP_ORDER_ID_OFFSET + int(topup_id)


def decode_topup_order_id(*, order_id: int) -> int | None:
    parsed = int(order_id)
    if parsed <= TOPUP_ORDER_ID_OFFSET:
        return None
    return parsed - TOPUP_ORDER_ID_OFFSET


def is_topup_virtual_order_id(*, order_id: int) -> bool:
    return decode_topup_order_id(order_id=order_id) is not None


def is_unpaid_terminal_provider_status(provider_status: str) -> bool:
    return provider_status.strip().lower() in _UNPAID_TERMINAL_PROVIDER_STATUSES


async def verify_topup(
    *,
    service: StarsOrderService,
    order_id: int,
    outcome_enum: Any,
    result_cls: Callable[..., ResultT],
) -> ResultT:
    topup_id = service._decode_topup_order_id(order_id=order_id)
    if topup_id is None:
        return result_cls(outcome=outcome_enum.NO_PENDING)
    topup = await service._get_topup(topup_id=topup_id)
    if topup is None:
        return result_cls(outcome=outcome_enum.NO_PENDING)

    terminal = _terminal_topup_result(
        service=service,
        topup=topup,
        outcome_enum=outcome_enum,
        result_cls=result_cls,
    )
    if terminal is not None:
        return terminal

    if topup.status in {StarsOrderStatus.CREATING_PAYMENT, StarsOrderStatus.PENDING_PAYMENT}:
        pending_result = await _verify_pending_topup(
            service=service,
            topup=topup,
            outcome_enum=outcome_enum,
            result_cls=result_cls,
        )
        if not isinstance(pending_result, tuple):
            return pending_result
        topup = pending_result[0]

    if topup.status in {StarsOrderStatus.PAYMENT_CONFIRMED, StarsOrderStatus.FULFILLING}:
        fulfilled = await service._fulfill_paid_topup(topup_id=topup.id)
        return _fulfilled_topup_result(
            fulfilled=fulfilled,
            outcome_enum=outcome_enum,
            result_cls=result_cls,
        )

    return result_cls(
        outcome=outcome_enum.PROCESSING,
        order=service._topup_to_order_dto(topup=topup),
    )


def _terminal_topup_result(
    *,
    service: StarsOrderService,
    topup: BalanceTopupDto,
    outcome_enum: Any,
    result_cls: Callable[..., ResultT],
) -> ResultT | None:
    outcomes = {
        StarsOrderStatus.CANCELED: outcome_enum.CANCELED,
        StarsOrderStatus.COMPLETED: outcome_enum.COMPLETED,
        StarsOrderStatus.FAILED: outcome_enum.FAILED,
    }
    outcome = outcomes.get(topup.status)
    if outcome is None:
        return None
    return result_cls(
        outcome=outcome,
        order=service._topup_to_order_dto(topup=topup),
    )


async def _verify_pending_topup(
    *,
    service: StarsOrderService,
    topup: BalanceTopupDto,
    outcome_enum: Any,
    result_cls: Callable[..., ResultT],
) -> tuple[BalanceTopupDto] | ResultT:
    is_paid, provider_status = await service._is_topup_paid(topup=topup)
    topup = (
        await service._update_topup(
            topup_id=topup.id,
            provider_status=provider_status,
        )
        or topup
    )
    if not is_paid:
        if service._is_unpaid_terminal_provider_status(provider_status):
            canceled = await service._transition_topup_status(
                topup_id=topup.id,
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
                order=service._topup_to_order_dto(topup=canceled or topup),
                provider_status=provider_status,
            )
        return result_cls(
            outcome=outcome_enum.PENDING,
            order=service._topup_to_order_dto(topup=topup),
            provider_status=provider_status,
        )
    transitioned = await service._transition_topup_status(
        topup_id=topup.id,
        from_statuses=[
            StarsOrderStatus.CREATING_PAYMENT,
            StarsOrderStatus.PENDING_PAYMENT,
        ],
        to_status=StarsOrderStatus.PAYMENT_CONFIRMED,
        provider_status=provider_status,
        paid_at=datetime_now(),
    )
    return (transitioned or topup,)


def _fulfilled_topup_result(
    *,
    fulfilled: StarsOrderDto,
    outcome_enum: Any,
    result_cls: Callable[..., ResultT],
) -> ResultT:
    outcomes = {
        StarsOrderStatus.COMPLETED: outcome_enum.COMPLETED,
        StarsOrderStatus.FAILED: outcome_enum.FAILED,
        StarsOrderStatus.CANCELED: outcome_enum.CANCELED,
    }
    return result_cls(
        outcome=outcomes.get(fulfilled.status, outcome_enum.PROCESSING),
        order=fulfilled,
    )
