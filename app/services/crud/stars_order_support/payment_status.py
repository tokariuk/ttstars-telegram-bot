from __future__ import annotations

from typing import Any

from app.enums.stars_order import StarsPaymentProvider
from app.models.dto.stars_order import StarsOrderDto

from .constants import NICE_PAY_PROVIDER_VARIANTS


async def is_order_paid(  # noqa: C901
    *,
    service: Any,
    order: StarsOrderDto,
) -> tuple[bool, str]:
    if order.payment_provider == StarsPaymentProvider.CRYPTO_BOT:
        if order.provider_invoice_id is None:
            return False, "invoice_missing"
        crypto_status = await service.crypto_pay_service.get_invoice_status(
            invoice_id=order.provider_invoice_id
        )
        return crypto_status.is_paid, crypto_status.status
    if order.payment_provider == StarsPaymentProvider.TON_PAY:
        if order.provider_reference is None or not order.provider_reference.strip():
            return False, "invoice_missing"
        expected_amount_nano = int(order.provider_amount_minor or 0)
        if expected_amount_nano <= 0:
            return False, "amount_missing"
        ton_status = await service.ton_pay_service.get_invoice_status(
            invoice_id=order.provider_reference,
            expected_amount_nano=expected_amount_nano,
        )
        return ton_status.is_paid, ton_status.status
    if order.payment_provider == StarsPaymentProvider.LZT_PAY:
        if order.provider_invoice_id is None:
            return False, "invoice_missing"
        lzt_status = await service.lzt_pay_service.get_invoice_status(
            invoice_id=order.provider_invoice_id
        )
        return lzt_status.is_paid, lzt_status.status
    if order.payment_provider == StarsPaymentProvider.HELEKET_PAY:
        heleket_status = await service.heleket_pay_service.get_invoice_status(
            invoice_uuid=order.payment_payload,
            order_id=order.provider_reference,
        )
        return heleket_status.is_paid, heleket_status.status
    if order.payment_provider == StarsPaymentProvider.PLATEGA_PAY:
        if order.provider_reference is None or not order.provider_reference.strip():
            return False, "transaction_missing"
        platega_status = await service.platega_pay_service.get_invoice_status(
            transaction_id=order.provider_reference,
        )
        return platega_status.is_paid, platega_status.status
    if order.payment_provider in NICE_PAY_PROVIDER_VARIANTS:
        if order.payment_payload is None or not order.payment_payload.strip():
            return False, "payment_missing"
        nice_status = await service.nice_pay_service.get_invoice_status(
            payment_id=order.payment_payload,
        )
        return nice_status.is_paid, nice_status.status
    if order.payment_provider == StarsPaymentProvider.XROCKET_PAY:
        xrocket_status = await service.xrocket_pay_service.get_invoice_status(
            payment_payload=order.payment_payload,
            invoice_id=order.provider_reference,
        )
        return xrocket_status.is_paid, xrocket_status.status
    if order.payment_provider == StarsPaymentProvider.BALANCE:
        return True, "paid_from_balance"
    return False, "provider_unsupported"
