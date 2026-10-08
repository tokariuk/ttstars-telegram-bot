from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import uuid4

from app.enums.stars_order import StarsOrderStatus, StarsPaymentProvider
from app.models.dto.balance_topup import BalanceTopupDto
from app.models.dto.stars_order import StarsOrderDto
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
