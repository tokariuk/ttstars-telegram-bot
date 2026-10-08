from __future__ import annotations

import unittest
from datetime import UTC, datetime
from typing import Any, cast

from app.enums.stars_order import StarsOrderStatus, StarsPaymentProvider
from app.models.dto.balance_topup import BalanceTopupDto
from app.models.dto.stars_order import StarsOrderDto
from app.services.crud.stars_order import (
    PaymentCheckOutcome,
    PaymentCheckResult,
    StarsOrderService,
)
from app.services.crud.stars_order_support.pricing import CheckoutPricing
from app.services.crud.stars_order_support.topups import (
    create_and_attach_topup_invoice,
    verify_topup,
)
from app.services.crypto_pay import CryptoPayInvoice


def make_topup(*, status: StarsOrderStatus) -> BalanceTopupDto:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return BalanceTopupDto(
        id=42,
        user_id=7,
        amount_cents=125,
        payment_provider=StarsPaymentProvider.CRYPTO_BOT,
        payment_currency="USDT",
        status=status,
        created_at=now,
        updated_at=now,
    )


class TopupServiceFake:
    def __init__(self, topup: BalanceTopupDto) -> None:
        self.topup = topup
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.order_marker = cast(StarsOrderDto, object())

    @staticmethod
    def _decode_topup_order_id(*, order_id: int) -> int | None:
        return order_id - 1_000_000_000 if order_id > 1_000_000_000 else None

    async def _get_topup(self, *, topup_id: int) -> BalanceTopupDto | None:
        self.calls.append(("get", {"topup_id": topup_id}))
        return self.topup

    def _topup_to_order_dto(self, *, topup: BalanceTopupDto) -> StarsOrderDto:
        self.calls.append(("to_order", {"status": topup.status}))
        return self.order_marker

    async def _is_topup_paid(self, *, topup: BalanceTopupDto) -> tuple[bool, str]:
        self.calls.append(("is_paid", {"topup_id": topup.id}))
        return False, " expired "

    async def _update_topup(self, *, topup_id: int, **data: Any) -> BalanceTopupDto | None:
        self.calls.append(("update", {"topup_id": topup_id, **data}))
        return self.topup

    @staticmethod
    def _is_unpaid_terminal_provider_status(provider_status: str) -> bool:
        return provider_status.strip().lower() == "expired"

    async def _transition_topup_status(
        self,
        *,
        topup_id: int,
        from_statuses: list[StarsOrderStatus],
        to_status: StarsOrderStatus,
        **data: Any,
    ) -> BalanceTopupDto | None:
        self.calls.append(
            (
                "transition",
                {
                    "topup_id": topup_id,
                    "from_statuses": from_statuses,
                    "to_status": to_status,
                    **data,
                },
            )
        )
        return self.topup.model_copy(update={"status": to_status})

    async def _fulfill_paid_topup(self, *, topup_id: int) -> StarsOrderDto:
        raise AssertionError(f"unexpected fulfillment for topup {topup_id}")


class CryptoPayServiceFake:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def create_invoice(self, **kwargs: Any) -> CryptoPayInvoice:
        self.calls.append(kwargs)
        return CryptoPayInvoice(invoice_id=314, pay_url="https://checkout.invalid/314")


class TopupInvoiceServiceFake:
    def __init__(self) -> None:
        self.crypto_pay_service = CryptoPayServiceFake()
        self.updates: list[dict[str, Any]] = []

    @staticmethod
    def _encode_topup_order_id(*, topup_id: int) -> int:
        return 1_000_000_000 + topup_id

    async def _update_topup(self, *, topup_id: int, **data: Any) -> BalanceTopupDto | None:
        self.updates.append({"topup_id": topup_id, **data})
        return make_topup(status=cast(StarsOrderStatus, data["status"]))


class TopupVirtualOrderIdTests(unittest.TestCase):
    def test_round_trip_uses_existing_offset(self) -> None:
        virtual_id = StarsOrderService._encode_topup_order_id(topup_id=42)

        self.assertEqual(virtual_id, 1_000_000_042)
        self.assertEqual(StarsOrderService._decode_topup_order_id(order_id=virtual_id), 42)
        self.assertTrue(StarsOrderService._is_topup_virtual_order_id(order_id=virtual_id))

    def test_offset_and_lower_ids_are_not_topups(self) -> None:
        self.assertIsNone(StarsOrderService._decode_topup_order_id(order_id=1_000_000_000))
        self.assertFalse(StarsOrderService._is_topup_virtual_order_id(order_id=999_999_999))


class TopupProviderStatusTests(unittest.TestCase):
    def test_terminal_status_is_case_and_whitespace_insensitive(self) -> None:
        self.assertTrue(StarsOrderService._is_unpaid_terminal_provider_status(" Cancelled "))
        self.assertTrue(StarsOrderService._is_unpaid_terminal_provider_status("EXPIRED"))
        self.assertFalse(StarsOrderService._is_unpaid_terminal_provider_status("pending"))


class TopupVerificationTests(unittest.IsolatedAsyncioTestCase):
    async def test_terminal_topup_returns_without_provider_check(self) -> None:
        service = TopupServiceFake(make_topup(status=StarsOrderStatus.CANCELED))

        result = await verify_topup(
            service=cast(Any, service),
            order_id=1_000_000_042,
            outcome_enum=PaymentCheckOutcome,
            result_cls=PaymentCheckResult,
        )

        self.assertEqual(result.outcome, PaymentCheckOutcome.CANCELED)
        self.assertIs(result.order, service.order_marker)
        self.assertEqual(
            service.calls,
            [
                ("get", {"topup_id": 42}),
                ("to_order", {"status": StarsOrderStatus.CANCELED}),
            ],
        )

    async def test_expired_pending_topup_is_canceled_after_status_update(self) -> None:
        service = TopupServiceFake(make_topup(status=StarsOrderStatus.PENDING_PAYMENT))

        result = await verify_topup(
            service=cast(Any, service),
            order_id=1_000_000_042,
            outcome_enum=PaymentCheckOutcome,
            result_cls=PaymentCheckResult,
        )

        self.assertEqual(result.outcome, PaymentCheckOutcome.CANCELED)
        self.assertEqual(result.provider_status, " expired ")
        self.assertEqual(
            [name for name, _data in service.calls],
            ["get", "is_paid", "update", "transition", "to_order"],
        )
        transition = service.calls[3][1]
        self.assertEqual(transition["to_status"], StarsOrderStatus.CANCELED)
        self.assertEqual(transition["provider_status"], " expired ")


class TopupInvoiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_crypto_invoice_uses_virtual_order_id_and_attaches_existing_fields(self) -> None:
        service = TopupInvoiceServiceFake()
        topup = make_topup(status=StarsOrderStatus.CREATING_PAYMENT)
        pricing = CheckoutPricing(
            net_amount_cents=125,
            invoice_amount_cents=130,
            customer_total_cents=130,
            fee_percent_text="4",
        )

        updated = await create_and_attach_topup_invoice(
            service=cast(Any, service),
            topup=topup,
            provider=StarsPaymentProvider.CRYPTO_BOT,
            user_id=7,
            checkout_pricing=pricing,
            checkout_amount_usd="1.30",
            description="Balance top-up",
            validation_error_cls=ValueError,
        )

        self.assertIsNotNone(updated)
        self.assertEqual(
            service.crypto_pay_service.calls,
            [
                {
                    "amount": "1.30",
                    "description": "Balance top-up",
                    "invoice_payload": "stars_crypto:1000000042:7",
                }
            ],
        )
        self.assertEqual(
            service.updates,
            [
                {
                    "topup_id": 42,
                    "status": StarsOrderStatus.PENDING_PAYMENT,
                    "payment_payload": "stars_crypto:1000000042:7",
                    "provider_invoice_id": 314,
                    "checkout_url": "https://checkout.invalid/314",
                    "provider_status": "pending",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
