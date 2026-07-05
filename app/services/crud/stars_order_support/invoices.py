from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.enums.stars_order import StarsOrderStatus, StarsPaymentProvider
from app.models.dto.stars_order import StarsOrderDto
from app.stars import build_crypto_payload

from .constants import NICE_PAY_PROVIDER_VARIANTS


async def create_and_attach_invoice(
    *,
    service: Any,
    order: StarsOrderDto,
    provider: StarsPaymentProvider,
    user_id: int,
    checkout_pricing: Any,
    checkout_amount_usd: str,
    description: str,
    validation_error_cls: type[Exception],
) -> StarsOrderDto | None:
    if provider == StarsPaymentProvider.CRYPTO_BOT:
        payload = build_crypto_payload(order_id=order.id, user_id=user_id)
        crypto_invoice = await service.crypto_pay_service.create_invoice(
            amount=checkout_amount_usd,
            description=description,
            invoice_payload=payload,
        )
        return await service._update_order(
            order_id=order.id,
            status=StarsOrderStatus.PENDING_PAYMENT,
            payment_payload=payload,
            provider_invoice_id=crypto_invoice.invoice_id,
            checkout_url=crypto_invoice.pay_url,
            provider_status="pending",
        )
    if provider == StarsPaymentProvider.TON_PAY:
        payment_token = f"ton-order-{order.id}-{uuid4().hex[:12]}"
        ton_invoice = await service.ton_pay_service.create_invoice(
            order_id=order.id,
            payment_token=payment_token,
            amount_usd=checkout_amount_usd,
        )
        return await service._update_order(
            order_id=order.id,
            status=StarsOrderStatus.PENDING_PAYMENT,
            payment_payload=ton_invoice.payment_token,
            provider_reference=ton_invoice.invoice_id,
            provider_amount_minor=ton_invoice.expected_amount_nano,
            checkout_url=ton_invoice.pay_url,
            provider_status=ton_invoice.status,
        )
    if provider == StarsPaymentProvider.LZT_PAY:
        payment_id = f"stars-order-{order.id}"
        callback_url = service._lzt_callback_url()
        lzt_invoice = await service.lzt_pay_service.create_invoice(
            amount=checkout_amount_usd,
            description=description,
            payment_id=payment_id,
            callback_url=callback_url,
        )
        return await service._update_order(
            order_id=order.id,
            status=StarsOrderStatus.PENDING_PAYMENT,
            payment_payload=lzt_invoice.payment_id,
            provider_invoice_id=lzt_invoice.invoice_id,
            checkout_url=lzt_invoice.pay_url,
            provider_status=lzt_invoice.status,
        )
    if provider == StarsPaymentProvider.HELEKET_PAY:
        heleket_order_id = service._build_heleket_order_id(local_order_id=order.id)
        heleket_invoice = await service.heleket_pay_service.create_invoice(
            amount=checkout_amount_usd,
            order_id=heleket_order_id,
            description=description,
            callback_url=service._heleket_callback_url(),
        )
        return await service._update_order(
            order_id=order.id,
            status=StarsOrderStatus.PENDING_PAYMENT,
            payment_payload=heleket_invoice.invoice_uuid,
            provider_reference=heleket_invoice.order_id,
            checkout_url=heleket_invoice.pay_url,
            provider_status=heleket_invoice.status,
        )
    if provider == StarsPaymentProvider.PLATEGA_PAY:
        platega_payload = service._build_platega_payload(local_order_id=order.id)
        platega_invoice = await service.platega_pay_service.create_invoice(
            amount_usd=checkout_amount_usd,
            payment_payload=platega_payload,
            description=description,
        )
        return await service._update_order(
            order_id=order.id,
            status=StarsOrderStatus.PENDING_PAYMENT,
            payment_payload=platega_invoice.payment_payload,
            provider_reference=platega_invoice.transaction_id,
            provider_amount_minor=platega_invoice.amount_minor,
            checkout_url=platega_invoice.pay_url,
            provider_status=platega_invoice.status,
        )
    if provider in NICE_PAY_PROVIDER_VARIANTS:
        nice_order_id = service._build_nice_pay_order_id(
            provider=provider,
            local_order_id=order.id,
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
        return await service._update_order(
            order_id=order.id,
            status=StarsOrderStatus.PENDING_PAYMENT,
            payment_payload=nice_invoice.payment_id,
            provider_reference=nice_invoice.order_id,
            provider_amount_minor=nice_invoice.amount_minor,
            checkout_url=nice_invoice.pay_url,
            provider_status=nice_invoice.status,
        )
    if provider == StarsPaymentProvider.XROCKET_PAY:
        payment_payload = f"stars-order-{order.id}"
        xrocket_invoice = await service.xrocket_pay_service.create_invoice(
            amount=checkout_amount_usd,
            description=description,
            payment_payload=payment_payload,
            callback_url=service._xrocket_callback_url(),
        )
        return await service._update_order(
            order_id=order.id,
            status=StarsOrderStatus.PENDING_PAYMENT,
            payment_payload=xrocket_invoice.payment_payload,
            provider_reference=xrocket_invoice.invoice_id,
            checkout_url=xrocket_invoice.pay_url,
            provider_status=xrocket_invoice.status,
        )
    raise validation_error_cls("Unsupported payment provider.")
