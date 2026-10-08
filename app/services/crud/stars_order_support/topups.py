from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import uuid4

from sqlalchemy import select

from app.enums.stars_order import (
    StarsOrderProductType,
    StarsOrderStatus,
    StarsPaymentProvider,
)
from app.models.dto.balance_topup import BalanceTopupDto
from app.models.dto.stars_order import StarsOrderDto
from app.models.sql.balance_topup import BalanceTopup
from app.models.sql.stars_order import StarsOrder
from app.models.sql.user import User
from app.services.postgres import SQLSessionContext
from app.stars import build_crypto_payload
from app.utils.time import datetime_now

if TYPE_CHECKING:
    from app.services.crud.stars_order import StarsOrderService
    from app.services.crud.stars_order_support.pricing import CheckoutPricing

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


async def create_and_attach_topup_invoice(
    *,
    service: StarsOrderService,
    topup: BalanceTopupDto,
    provider: StarsPaymentProvider,
    user_id: int,
    checkout_pricing: CheckoutPricing,
    checkout_amount_usd: str,
    description: str,
    validation_error_cls: type[Exception],
) -> BalanceTopupDto | None:
    virtual_order_id = service._encode_topup_order_id(topup_id=topup.id)
    if provider == StarsPaymentProvider.CRYPTO_BOT:
        payload = build_crypto_payload(order_id=virtual_order_id, user_id=user_id)
        crypto_invoice = await service.crypto_pay_service.create_invoice(
            amount=checkout_amount_usd,
            description=description,
            invoice_payload=payload,
        )
        return await service._update_topup(
            topup_id=topup.id,
            status=StarsOrderStatus.PENDING_PAYMENT,
            payment_payload=payload,
            provider_invoice_id=crypto_invoice.invoice_id,
            checkout_url=crypto_invoice.pay_url,
            provider_status="pending",
        )
    if provider == StarsPaymentProvider.TON_PAY:
        payment_token = f"ton-topup-{virtual_order_id}-{uuid4().hex[:12]}"
        ton_invoice = await service.ton_pay_service.create_invoice(
            order_id=virtual_order_id,
            payment_token=payment_token,
            amount_usd=checkout_amount_usd,
        )
        return await service._update_topup(
            topup_id=topup.id,
            status=StarsOrderStatus.PENDING_PAYMENT,
            payment_payload=ton_invoice.payment_token,
            provider_reference=ton_invoice.invoice_id,
            provider_amount_minor=ton_invoice.expected_amount_nano,
            checkout_url=ton_invoice.pay_url,
            provider_status=ton_invoice.status,
        )
    if provider == StarsPaymentProvider.LZT_PAY:
        payment_id = f"topup-{virtual_order_id}"
        lzt_invoice = await service.lzt_pay_service.create_invoice(
            amount=checkout_amount_usd,
            description=description,
            payment_id=payment_id,
            callback_url=service._lzt_callback_url(),
        )
        return await service._update_topup(
            topup_id=topup.id,
            status=StarsOrderStatus.PENDING_PAYMENT,
            payment_payload=lzt_invoice.payment_id,
            provider_invoice_id=lzt_invoice.invoice_id,
            checkout_url=lzt_invoice.pay_url,
            provider_status=lzt_invoice.status,
        )
    if provider == StarsPaymentProvider.HELEKET_PAY:
        heleket_order_id = service._build_heleket_order_id(local_order_id=virtual_order_id)
        heleket_invoice = await service.heleket_pay_service.create_invoice(
            amount=checkout_amount_usd,
            order_id=heleket_order_id,
            description=description,
            callback_url=service._heleket_callback_url(),
        )
        return await service._update_topup(
            topup_id=topup.id,
            status=StarsOrderStatus.PENDING_PAYMENT,
            payment_payload=heleket_invoice.invoice_uuid,
            provider_reference=heleket_invoice.order_id,
            checkout_url=heleket_invoice.pay_url,
            provider_status=heleket_invoice.status,
        )
    if provider == StarsPaymentProvider.PLATEGA_PAY:
        platega_payload = service._build_platega_payload(local_order_id=virtual_order_id)
        platega_invoice = await service.platega_pay_service.create_invoice(
            amount_usd=checkout_amount_usd,
            payment_payload=platega_payload,
            description=description,
        )
        return await service._update_topup(
            topup_id=topup.id,
            status=StarsOrderStatus.PENDING_PAYMENT,
            payment_payload=platega_invoice.payment_payload,
            provider_reference=platega_invoice.transaction_id,
            provider_amount_minor=platega_invoice.amount_minor,
            checkout_url=platega_invoice.pay_url,
            provider_status=platega_invoice.status,
        )
    if provider in {StarsPaymentProvider.NICE_PAY_RU, StarsPaymentProvider.NICE_PAY_KZ}:
        nice_order_id = service._build_nice_pay_order_id(
            provider=provider,
            local_order_id=virtual_order_id,
        )
        nice_currency = service._nice_pay_currency(provider=provider)
        nice_amount_minor = await service.nice_pay_service.invoice_amount_minor_from_usd_cents(
            usd_cents=checkout_pricing.invoice_amount_cents,
            currency=nice_currency,
        )
        nice_invoice = await service.nice_pay_service.create_invoice(
            amount_minor=nice_amount_minor,
            order_id=nice_order_id,
            customer=f"user_{user_id}",
            description=description,
            currency=nice_currency,
        )
        return await service._update_topup(
            topup_id=topup.id,
            status=StarsOrderStatus.PENDING_PAYMENT,
            payment_payload=nice_invoice.payment_id,
            provider_reference=nice_invoice.order_id,
            provider_amount_minor=nice_invoice.amount_minor,
            checkout_url=nice_invoice.pay_url,
            provider_status=nice_invoice.status,
        )
    if provider == StarsPaymentProvider.XROCKET_PAY:
        payment_payload = f"topup-{virtual_order_id}"
        xrocket_invoice = await service.xrocket_pay_service.create_invoice(
            amount=checkout_amount_usd,
            description=description,
            payment_payload=payment_payload,
            callback_url=service._xrocket_callback_url(),
        )
        return await service._update_topup(
            topup_id=topup.id,
            status=StarsOrderStatus.PENDING_PAYMENT,
            payment_payload=xrocket_invoice.payment_payload,
            provider_reference=xrocket_invoice.invoice_id,
            checkout_url=xrocket_invoice.pay_url,
            provider_status=xrocket_invoice.status,
        )
    raise validation_error_cls("Unsupported payment provider.")


async def fulfill_paid_topup(
    *,
    service: StarsOrderService,
    topup_id: int,
    error_cls: type[Exception],
) -> StarsOrderDto:
    encoded_order_id = service._encode_topup_order_id(topup_id=topup_id)
    lock_token = await service._acquire_fulfill_lock(order_id=encoded_order_id)
    if lock_token is None:
        latest = await service._get_topup(topup_id=topup_id)
        if latest is None:
            raise error_cls("Top-up not found during fulfillment.")
        return service._topup_to_order_dto(topup=latest)
    try:
        prepared = await _prepare_topup_for_credit(
            service=service,
            topup_id=topup_id,
            error_cls=error_cls,
        )
        if not isinstance(prepared, tuple):
            return prepared
        topup = prepared[0]

        stop_after_transaction, linked_order_id = await _credit_topup_transaction(
            service=service,
            topup=topup,
            error_cls=error_cls,
        )
        topup_dto = await service._get_topup(topup_id=topup.id)
        if topup_dto is None:
            raise error_cls("Top-up disappeared after fulfillment transaction.")
        if stop_after_transaction:
            return service._topup_to_order_dto(topup=topup_dto)

        await service._clear_user_cache(user_id=topup.user_id)

        if linked_order_id is not None:
            failed = await _fulfill_linked_order(
                service=service,
                topup=topup_dto,
                linked_order_id=linked_order_id,
            )
            if failed is not None:
                return failed
        refreshed = await service._get_topup(topup_id=topup_id)
        if refreshed is None:
            raise error_cls("Top-up disappeared after fulfillment.")
        return service._topup_to_order_dto(topup=refreshed)
    finally:
        await service._release_fulfill_lock(
            order_id=encoded_order_id,
            lock_token=lock_token,
        )


async def _prepare_topup_for_credit(
    *,
    service: StarsOrderService,
    topup_id: int,
    error_cls: type[Exception],
) -> tuple[BalanceTopupDto] | StarsOrderDto:
    topup = await service._get_topup(topup_id=topup_id)
    if topup is None:
        raise error_cls("Top-up not found during fulfillment.")
    if topup.status in {
        StarsOrderStatus.COMPLETED,
        StarsOrderStatus.FAILED,
        StarsOrderStatus.CANCELED,
    }:
        return service._topup_to_order_dto(topup=topup)

    if topup.status == StarsOrderStatus.PAYMENT_CONFIRMED:
        transitioned = await service._transition_topup_status(
            topup_id=topup.id,
            from_statuses=[StarsOrderStatus.PAYMENT_CONFIRMED],
            to_status=StarsOrderStatus.FULFILLING,
        )
        if transitioned is not None:
            topup = transitioned

    if topup.status != StarsOrderStatus.FULFILLING:
        return service._topup_to_order_dto(topup=topup)
    return (topup,)


async def _fulfill_linked_order(
    *,
    service: StarsOrderService,
    topup: BalanceTopupDto,
    linked_order_id: int,
) -> StarsOrderDto | None:
    try:
        await service._fulfill_paid_order(order_id=linked_order_id)
    except Exception as error:
        error_text = str(error).strip() or "Auto purchase fulfillment failed."
        failed = await service._update_topup(
            topup_id=topup.id,
            status=StarsOrderStatus.FAILED,
            failed_at=datetime_now(),
            error_message=error_text,
        )
        if failed is not None:
            return service._topup_to_order_dto(topup=failed)
    return None


async def _credit_topup_transaction(
    *,
    service: StarsOrderService,
    topup: BalanceTopupDto,
    error_cls: type[Exception],
) -> tuple[bool, int | None]:
    linked_order_id: int | None = None
    async with SQLSessionContext(session_pool=service.session_pool) as (repository, _uow):
        session = repository.session
        current = await session.scalar(
            select(BalanceTopup).where(BalanceTopup.id == topup.id).with_for_update()
        )
        if current is None:
            raise error_cls("Top-up not found during fulfillment.")
        if current.status in {
            StarsOrderStatus.COMPLETED.value,
            StarsOrderStatus.CANCELED.value,
            StarsOrderStatus.FAILED.value,
        }:
            return True, None

        user = await session.scalar(
            select(User).where(User.id == current.user_id).with_for_update()
        )
        if user is None:
            current.status = StarsOrderStatus.FAILED
            current.failed_at = datetime_now()
            current.error_message = "Top-up user not found."
            await session.commit()
            return True, None

        if int(current.amount_cents) > 0:
            user.balance_cents = int(user.balance_cents) + int(current.amount_cents)
        current.credited_at = current.credited_at or datetime_now()

        if current.auto_product_type is not None:
            product_type = StarsOrderProductType(str(current.auto_product_type))
            amount_cents = int(current.amount_cents)
            if int(user.balance_cents) < amount_cents:
                current.status = StarsOrderStatus.FAILED
                current.failed_at = datetime_now()
                current.error_message = "Insufficient balance after top-up credit."
                await session.commit()
                return True, None
            user.balance_cents = int(user.balance_cents) - amount_cents
            linked_order = StarsOrder(
                user_id=int(current.user_id),
                recipient_username=(
                    current.auto_recipient_username
                    if current.auto_recipient_username
                    else "balance"
                ),
                stars_count=int(current.auto_stars_count or 0),
                product_type=product_type.value,
                premium_months=current.auto_premium_months,
                recipient_user_id=current.auto_recipient_user_id,
                gift_id=current.auto_gift_id,
                gift_message=current.auto_gift_message,
                gift_sender_private=current.auto_gift_sender_private,
                amount_cents=amount_cents,
                payment_provider=current.payment_provider,
                payment_currency=current.payment_currency,
                status=StarsOrderStatus.PAYMENT_CONFIRMED.value,
                provider_status="paid_via_balance_topup",
                paid_at=datetime_now(),
                funding_topup_id=current.id,
                funding_provider=current.payment_provider,
            )
            session.add(linked_order)
            await session.flush()
            current.linked_order_id = linked_order.id
            linked_order_id = int(linked_order.id)

        current.status = StarsOrderStatus.COMPLETED
        current.completed_at = datetime_now()
        current.error_message = None
        await session.commit()
    return False, linked_order_id


async def find_topup_for_webhook(
    *,
    service: StarsOrderService,
    providers: Sequence[StarsPaymentProvider],
    provider_invoice_id: int | None = None,
    payment_payload: str | None = None,
    provider_reference: str | None = None,
) -> BalanceTopupDto | None:
    normalized_payload = (payment_payload or "").strip()
    normalized_reference = (provider_reference or "").strip()
    normalized_invoice = (
        int(provider_invoice_id)
        if provider_invoice_id is not None and provider_invoice_id > 0
        else None
    )
    async with SQLSessionContext(session_pool=service.session_pool) as (repository, _uow):
        if normalized_invoice is not None:
            for provider in providers:
                found = await repository.balance_topups.get_by_provider_invoice(
                    provider=provider,
                    provider_invoice_id=normalized_invoice,
                )
                if found is not None:
                    return found.dto()
        if normalized_payload:
            for provider in providers:
                found = await repository.balance_topups.get_by_provider_payload(
                    provider=provider,
                    payment_payload=normalized_payload,
                )
                if found is not None:
                    return found.dto()
        if normalized_reference:
            for provider in providers:
                found = await repository.balance_topups.get_by_provider_reference(
                    provider=provider,
                    provider_reference=normalized_reference,
                )
                if found is not None:
                    return found.dto()
    return None


async def process_topup_webhook(
    *,
    service: StarsOrderService,
    topup: BalanceTopupDto,
    provider_status: str | None = None,
    provider_invoice_id: int | None = None,
    payment_payload: str | None = None,
    provider_reference: str | None = None,
    error_cls: type[Exception],
) -> StarsOrderDto:
    normalized_status = (provider_status or "").strip().lower() or None
    normalized_payload = (payment_payload or "").strip() or None
    normalized_reference = (provider_reference or "").strip() or None
    normalized_invoice = (
        int(provider_invoice_id)
        if provider_invoice_id is not None and provider_invoice_id > 0
        else None
    )

    update_data: dict[str, Any] = {}
    if normalized_status is not None:
        update_data["provider_status"] = normalized_status
    if normalized_invoice is not None:
        update_data["provider_invoice_id"] = normalized_invoice
    if normalized_payload is not None:
        update_data["payment_payload"] = normalized_payload
    if normalized_reference is not None:
        update_data["provider_reference"] = normalized_reference

    updated_topup = (
        await service._update_topup(topup_id=topup.id, **update_data) if update_data else topup
    )
    if updated_topup is None:
        refreshed = await service._get_topup(topup_id=topup.id)
        if refreshed is None:
            raise error_cls("Top-up disappeared during webhook processing.")
        updated_topup = refreshed
    if updated_topup.status in {
        StarsOrderStatus.COMPLETED,
        StarsOrderStatus.FAILED,
        StarsOrderStatus.CANCELED,
    }:
        return service._topup_to_order_dto(topup=updated_topup)

    result = await service.verify_order(
        order_id=service._encode_topup_order_id(topup_id=updated_topup.id)
    )
    if result.order is not None:
        return result.order
    latest = await service._get_topup(topup_id=updated_topup.id)
    if latest is None:
        raise error_cls("Top-up disappeared after webhook verification.")
    return service._topup_to_order_dto(topup=latest)


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
