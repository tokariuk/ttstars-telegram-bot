from __future__ import annotations

import logging
import unittest
from datetime import UTC, datetime
from typing import Any, cast

from app.enums.stars_order import (
    StarsOrderProductType,
    StarsOrderStatus,
    StarsPaymentProvider,
)
from app.models.dto.stars_order import StarsOrderDto
from app.services.crud.stars_order import StarsOrderService
from app.services.crud.stars_order_support.fulfillment import fulfill_paid_order
from app.services.crud.stars_order_support.invoices import create_and_attach_invoice
from app.services.crud.stars_order_support.pricing import CheckoutPricing
from app.services.crud.stars_order_support.runtime_ops import mark_failed_and_refund
from app.services.crud.stars_order_support.webhooks import _try_fulfill_after_paid
from app.services.crypto_pay import CryptoPayInvoice


def order_dto(**changes: Any) -> StarsOrderDto:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    values: dict[str, Any] = {
        "id": 41,
        "user_id": 7,
        "recipient_username": "alice",
        "stars_count": 100,
        "product_type": StarsOrderProductType.STARS,
        "amount_cents": 125,
        "payment_provider": StarsPaymentProvider.CRYPTO_BOT,
        "payment_currency": "USD",
        "status": StarsOrderStatus.CREATING_PAYMENT,
        "created_at": now,
        "updated_at": now,
    }
    values.update(changes)
    return StarsOrderDto.model_validate(values)


class CryptoInvoiceServiceFake:
    async def create_invoice(
        self,
        *,
        amount: str,
        description: str,
        invoice_payload: str | None = None,
    ) -> CryptoPayInvoice:
        return CryptoPayInvoice(invoice_id=91, pay_url="https://pay.test/91")


class InvoiceContextFake:
    def __init__(self, updated_order: StarsOrderDto) -> None:
        self.crypto_pay_service = CryptoInvoiceServiceFake()
        self.updated_order = updated_order
        self.update_data: dict[str, Any] | None = None

    async def _update_order(self, *, order_id: int, **data: Any) -> StarsOrderDto | None:
        self.update_data = {"order_id": order_id, **data}
        return self.updated_order


class StarsOrderInvoiceContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_crypto_invoice_is_attached_with_existing_transition_fields(self) -> None:
        initial = order_dto()
        updated = order_dto(
            status=StarsOrderStatus.PENDING_PAYMENT,
            provider_invoice_id=91,
            checkout_url="https://pay.test/91",
        )
        service = InvoiceContextFake(updated)

        result = await create_and_attach_invoice(
            service=cast(StarsOrderService, service),
            order=initial,
            provider=StarsPaymentProvider.CRYPTO_BOT,
            user_id=initial.user_id,
            checkout_pricing=CheckoutPricing(125, 125, 125, "0"),
            checkout_amount_usd="1.25",
            description="100 Stars",
            validation_error_cls=ValueError,
        )

        self.assertIs(result, updated)
        assert service.update_data is not None
        self.assertEqual(service.update_data["order_id"], 41)
        self.assertEqual(service.update_data["status"], StarsOrderStatus.PENDING_PAYMENT)
        self.assertEqual(service.update_data["provider_invoice_id"], 91)
        self.assertEqual(service.update_data["checkout_url"], "https://pay.test/91")


class CompletedFulfillmentContextFake:
    def __init__(self, order: StarsOrderDto) -> None:
        self.order = order

    async def get(self, order_id: int) -> StarsOrderDto | None:
        return self.order


class StarsOrderFulfillmentContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_completed_order_returns_without_locking_or_delivery(self) -> None:
        completed = order_dto(status=StarsOrderStatus.COMPLETED)

        result = await fulfill_paid_order(
            service=cast(StarsOrderService, CompletedFulfillmentContextFake(completed)),
            order_id=completed.id,
            order_error_cls=RuntimeError,
            logger=logging.getLogger("test.fulfillment"),
        )

        self.assertIs(result, completed)


class RefundContextFake:
    def __init__(self, failed: StarsOrderDto, refunded: StarsOrderDto) -> None:
        self.responses = [failed, refunded]
        self.credited: tuple[int, int] | None = None

    async def _update_order(self, *, order_id: int, **data: Any) -> StarsOrderDto | None:
        return self.responses.pop(0)

    async def _credit_user_balance(self, *, user_id: int, amount_cents: int) -> bool:
        self.credited = (user_id, amount_cents)
        return True


class StarsOrderRefundContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_failed_paid_order_is_refunded_and_returns_latest_order(self) -> None:
        order = order_dto(status=StarsOrderStatus.FULFILLING)
        failed = order_dto(status=StarsOrderStatus.FAILED)
        refunded = order_dto(
            status=StarsOrderStatus.FAILED,
            provider_status="delivery_failed_refunded_to_balance",
        )
        service = RefundContextFake(failed, refunded)

        result = await mark_failed_and_refund(
            service=cast(StarsOrderService, service),
            order=order,
            error_text="delivery failed",
            order_error_cls=RuntimeError,
            logger=logging.getLogger("test.refund"),
        )

        self.assertIs(result, refunded)
        self.assertEqual(service.credited, (7, 125))


class WebhookFulfillmentContextFake:
    def __init__(self, fulfilled: StarsOrderDto) -> None:
        self.fulfilled = fulfilled
        self.fulfilled_order_id: int | None = None

    async def _fulfill_paid_order(self, *, order_id: int) -> StarsOrderDto:
        self.fulfilled_order_id = order_id
        return self.fulfilled


class StarsOrderWebhookContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_confirmed_webhook_order_delegates_to_fulfillment(self) -> None:
        confirmed = order_dto(status=StarsOrderStatus.PAYMENT_CONFIRMED)
        completed = order_dto(status=StarsOrderStatus.COMPLETED)
        service = WebhookFulfillmentContextFake(completed)

        result = await _try_fulfill_after_paid(
            service=cast(StarsOrderService, service),
            order=confirmed,
        )

        self.assertIs(result, completed)
        self.assertEqual(service.fulfilled_order_id, confirmed.id)


if __name__ == "__main__":
    unittest.main()
