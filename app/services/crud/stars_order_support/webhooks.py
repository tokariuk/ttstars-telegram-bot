from __future__ import annotations

import logging
from typing import Any

from app.enums.stars_order import StarsOrderStatus, StarsPaymentProvider
from app.models.dto.stars_order import StarsOrderDto
from app.models.sql.stars_order import StarsOrder
from app.services.postgres import SQLSessionContext
from app.utils.time import datetime_now

from .constants import NICE_PAY_PROVIDER_VARIANTS

logger = logging.getLogger(__name__)


async def _try_fulfill_after_paid(
    *,
    service: Any,
    order: StarsOrderDto,
) -> StarsOrderDto:
    if order.status not in {
        StarsOrderStatus.PAYMENT_CONFIRMED,
        StarsOrderStatus.FULFILLING,
    }:
        return order
    try:
        return await service._fulfill_paid_order(order_id=order.id)
    except Exception:
        logger.exception(
            "Immediate fulfillment after webhook failed for order %s.",
            order.id,
        )
        return order


async def process_crypto_webhook_invoice(
    *,
    service: Any,
    invoice_id: int,
) -> StarsOrderDto | None:
    async with SQLSessionContext(session_pool=service.session_pool) as (repository, _uow):
        order = await repository.stars_orders.get_by_provider_invoice(
            provider=StarsPaymentProvider.CRYPTO_BOT,
            provider_invoice_id=invoice_id,
        )
    if order is None:
        return None
    dto = order.dto()
    if dto.status in {
        StarsOrderStatus.COMPLETED,
        StarsOrderStatus.FAILED,
        StarsOrderStatus.CANCELED,
    }:
        return dto

    transitioned = await service._transition_order_status(
        order_id=dto.id,
        from_statuses=[
            StarsOrderStatus.PENDING_PAYMENT,
            StarsOrderStatus.CREATING_PAYMENT,
        ],
        to_status=StarsOrderStatus.PAYMENT_CONFIRMED,
        provider_status="paid",
        paid_at=datetime_now(),
    )
    if transitioned is not None:
        dto = transitioned

    return await _try_fulfill_after_paid(service=service, order=dto)


async def process_lzt_webhook_invoice(
    *,
    service: Any,
    invoice_id: int | None = None,
    payment_id: str | None = None,
) -> StarsOrderDto | None:
    order: StarsOrder | None = None
    normalized_payment_id = payment_id.strip() if isinstance(payment_id, str) else ""

    async with SQLSessionContext(session_pool=service.session_pool) as (repository, _uow):
        if invoice_id is not None and invoice_id > 0:
            order = await repository.stars_orders.get_by_provider_invoice(
                provider=StarsPaymentProvider.LZT_PAY,
                provider_invoice_id=invoice_id,
            )
        if order is None and normalized_payment_id:
            order = await repository.stars_orders.get_by_provider_payload(
                provider=StarsPaymentProvider.LZT_PAY,
                payment_payload=normalized_payment_id,
            )

    if order is None:
        return None

    dto = order.dto()
    if dto.status in {
        StarsOrderStatus.COMPLETED,
        StarsOrderStatus.FAILED,
        StarsOrderStatus.CANCELED,
    }:
        return dto

    is_paid, provider_status = await service._is_order_paid(order=dto)
    dto = (
        await service._update_order(
            order_id=dto.id,
            provider_status=provider_status,
        )
        or dto
    )
    if not is_paid:
        return dto

    transitioned = await service._transition_order_status(
        order_id=dto.id,
        from_statuses=[
            StarsOrderStatus.PENDING_PAYMENT,
            StarsOrderStatus.CREATING_PAYMENT,
        ],
        to_status=StarsOrderStatus.PAYMENT_CONFIRMED,
        provider_status=provider_status,
        paid_at=datetime_now(),
    )
    return await _try_fulfill_after_paid(service=service, order=transitioned or dto)


async def process_platega_webhook_payment(
    *,
    service: Any,
    transaction_id: str | None = None,
    payment_payload: str | None = None,
    webhook_status: str | None = None,
) -> StarsOrderDto | None:
    order: StarsOrder | None = None
    normalized_transaction_id = (
        transaction_id.strip() if isinstance(transaction_id, str) else ""
    )
    normalized_payment_payload = (
        payment_payload.strip() if isinstance(payment_payload, str) else ""
    )

    async with SQLSessionContext(session_pool=service.session_pool) as (repository, _uow):
        if normalized_transaction_id:
            order = await repository.stars_orders.get_by_provider_reference(
                provider=StarsPaymentProvider.PLATEGA_PAY,
                provider_reference=normalized_transaction_id,
            )
        if order is None and normalized_payment_payload:
            order = await repository.stars_orders.get_by_provider_payload(
                provider=StarsPaymentProvider.PLATEGA_PAY,
                payment_payload=normalized_payment_payload,
            )

    if order is None:
        return None

    dto = order.dto()
    if dto.status in {
        StarsOrderStatus.COMPLETED,
        StarsOrderStatus.FAILED,
        StarsOrderStatus.CANCELED,
    }:
        return dto

    provider_status = (
        webhook_status.strip().lower()
        if isinstance(webhook_status, str) and webhook_status.strip()
        else dto.provider_status
    )
    dto = (
        await service._update_order(
            order_id=dto.id,
            provider_status=provider_status,
            payment_payload=normalized_payment_payload or dto.payment_payload,
            provider_reference=normalized_transaction_id or dto.provider_reference,
        )
        or dto
    )

    is_paid, verified_status = await service._is_order_paid(order=dto)
    dto = (
        await service._update_order(
            order_id=dto.id,
            provider_status=verified_status,
            payment_payload=normalized_payment_payload or dto.payment_payload,
            provider_reference=normalized_transaction_id or dto.provider_reference,
        )
        or dto
    )
    if not is_paid:
        return dto

    transitioned = await service._transition_order_status(
        order_id=dto.id,
        from_statuses=[
            StarsOrderStatus.PENDING_PAYMENT,
            StarsOrderStatus.CREATING_PAYMENT,
        ],
        to_status=StarsOrderStatus.PAYMENT_CONFIRMED,
        provider_status=verified_status,
        paid_at=datetime_now(),
        payment_payload=normalized_payment_payload or dto.payment_payload,
        provider_reference=normalized_transaction_id or dto.provider_reference,
    )
    return await _try_fulfill_after_paid(service=service, order=transitioned or dto)


async def find_nice_pay_webhook_order(
    *,
    service: Any,
    payment_id: str,
    order_id: str,
) -> StarsOrder | None:
    order: StarsOrder | None = None
    async with SQLSessionContext(session_pool=service.session_pool) as (repository, _uow):
        if payment_id:
            for provider in NICE_PAY_PROVIDER_VARIANTS:
                order = await repository.stars_orders.get_by_provider_payload(
                    provider=provider,
                    payment_payload=payment_id,
                )
                if order is not None:
                    return order
        if order_id:
            for provider in NICE_PAY_PROVIDER_VARIANTS:
                order = await repository.stars_orders.get_by_provider_reference(
                    provider=provider,
                    provider_reference=order_id,
                )
                if order is not None:
                    return order
    return None


def nice_pay_provider_status(
    *,
    webhook_result: str | None,
    current_status: str | None,
) -> str | None:
    if isinstance(webhook_result, str) and webhook_result.strip():
        return webhook_result.strip().lower()
    return current_status


async def process_nice_pay_webhook_payment(
    *,
    service: Any,
    payment_id: str | None = None,
    order_id: str | None = None,
    webhook_result: str | None = None,
) -> StarsOrderDto | None:
    normalized_payment_id = payment_id.strip() if isinstance(payment_id, str) else ""
    normalized_order_id = order_id.strip() if isinstance(order_id, str) else ""
    order = await find_nice_pay_webhook_order(
        service=service,
        payment_id=normalized_payment_id,
        order_id=normalized_order_id,
    )

    if order is None:
        return None

    dto = order.dto()
    if dto.status in {
        StarsOrderStatus.COMPLETED,
        StarsOrderStatus.FAILED,
        StarsOrderStatus.CANCELED,
    }:
        return dto

    provider_status = nice_pay_provider_status(
        webhook_result=webhook_result,
        current_status=dto.provider_status,
    )
    dto = (
        await service._update_order(
            order_id=dto.id,
            provider_status=provider_status,
            provider_reference=normalized_order_id or dto.provider_reference,
        )
        or dto
    )

    if provider_status != "success":
        return dto

    is_paid, verified_status = await service._is_order_paid(order=dto)
    dto = (
        await service._update_order(
            order_id=dto.id,
            provider_status=verified_status,
            provider_reference=normalized_order_id or dto.provider_reference,
        )
        or dto
    )
    if not is_paid:
        return dto

    transitioned = await service._transition_order_status(
        order_id=dto.id,
        from_statuses=[
            StarsOrderStatus.PENDING_PAYMENT,
            StarsOrderStatus.CREATING_PAYMENT,
        ],
        to_status=StarsOrderStatus.PAYMENT_CONFIRMED,
        provider_status=verified_status,
        paid_at=datetime_now(),
        provider_reference=normalized_order_id or dto.provider_reference,
    )
    return await _try_fulfill_after_paid(service=service, order=transitioned or dto)


async def process_heleket_webhook_invoice(
    *,
    service: Any,
    invoice_uuid: str | None = None,
    order_id: str | None = None,
    webhook_status: str | None = None,
) -> StarsOrderDto | None:
    order: StarsOrder | None = None
    normalized_invoice_uuid = invoice_uuid.strip() if isinstance(invoice_uuid, str) else ""
    normalized_order_id = order_id.strip() if isinstance(order_id, str) else ""

    async with SQLSessionContext(session_pool=service.session_pool) as (repository, _uow):
        if normalized_invoice_uuid:
            order = await repository.stars_orders.get_by_provider_payload(
                provider=StarsPaymentProvider.HELEKET_PAY,
                payment_payload=normalized_invoice_uuid,
            )
        if order is None and normalized_order_id:
            order = await repository.stars_orders.get_by_provider_reference(
                provider=StarsPaymentProvider.HELEKET_PAY,
                provider_reference=normalized_order_id,
            )

    if order is None:
        return None

    dto = order.dto()
    if dto.status in {
        StarsOrderStatus.COMPLETED,
        StarsOrderStatus.FAILED,
        StarsOrderStatus.CANCELED,
    }:
        return dto

    provider_status = (
        webhook_status.strip().lower()
        if isinstance(webhook_status, str) and webhook_status.strip()
        else dto.provider_status
    )
    dto = (
        await service._update_order(
            order_id=dto.id,
            provider_status=provider_status,
            payment_payload=normalized_invoice_uuid or dto.payment_payload,
            provider_reference=normalized_order_id or dto.provider_reference,
        )
        or dto
    )

    is_paid, verified_status = await service._is_order_paid(order=dto)
    dto = (
        await service._update_order(
            order_id=dto.id,
            provider_status=verified_status,
            payment_payload=normalized_invoice_uuid or dto.payment_payload,
            provider_reference=normalized_order_id or dto.provider_reference,
        )
        or dto
    )
    if not is_paid:
        return dto

    transitioned = await service._transition_order_status(
        order_id=dto.id,
        from_statuses=[
            StarsOrderStatus.PENDING_PAYMENT,
            StarsOrderStatus.CREATING_PAYMENT,
        ],
        to_status=StarsOrderStatus.PAYMENT_CONFIRMED,
        provider_status=verified_status,
        paid_at=datetime_now(),
        payment_payload=normalized_invoice_uuid or dto.payment_payload,
        provider_reference=normalized_order_id or dto.provider_reference,
    )
    return await _try_fulfill_after_paid(service=service, order=transitioned or dto)


async def process_xrocket_webhook_invoice(
    *,
    service: Any,
    payment_payload: str | None = None,
    invoice_id: str | None = None,
    webhook_status: str | None = None,
) -> StarsOrderDto | None:
    order: StarsOrder | None = None
    normalized_payment_payload = (
        payment_payload.strip() if isinstance(payment_payload, str) else ""
    )
    normalized_invoice_id = invoice_id.strip() if isinstance(invoice_id, str) else ""

    async with SQLSessionContext(session_pool=service.session_pool) as (repository, _uow):
        if normalized_payment_payload:
            order = await repository.stars_orders.get_by_provider_payload(
                provider=StarsPaymentProvider.XROCKET_PAY,
                payment_payload=normalized_payment_payload,
            )
        if order is None and normalized_invoice_id:
            order = await repository.stars_orders.get_by_provider_reference(
                provider=StarsPaymentProvider.XROCKET_PAY,
                provider_reference=normalized_invoice_id,
            )

    if order is None:
        return None

    dto = order.dto()
    if dto.status in {
        StarsOrderStatus.COMPLETED,
        StarsOrderStatus.FAILED,
        StarsOrderStatus.CANCELED,
    }:
        return dto

    provider_status = (
        webhook_status.strip().lower()
        if isinstance(webhook_status, str) and webhook_status.strip()
        else dto.provider_status
    )
    dto = (
        await service._update_order(
            order_id=dto.id,
            provider_status=provider_status,
            provider_reference=normalized_invoice_id or dto.provider_reference,
        )
        or dto
    )

    is_paid, verified_status = await service._is_order_paid(order=dto)
    dto = (
        await service._update_order(
            order_id=dto.id,
            provider_status=verified_status,
            provider_reference=normalized_invoice_id or dto.provider_reference,
        )
        or dto
    )
    if not is_paid:
        return dto

    transitioned = await service._transition_order_status(
        order_id=dto.id,
        from_statuses=[
            StarsOrderStatus.PENDING_PAYMENT,
            StarsOrderStatus.CREATING_PAYMENT,
        ],
        to_status=StarsOrderStatus.PAYMENT_CONFIRMED,
        provider_status=verified_status,
        paid_at=datetime_now(),
        provider_reference=normalized_invoice_id or dto.provider_reference,
    )
    return await _try_fulfill_after_paid(service=service, order=transitioned or dto)
