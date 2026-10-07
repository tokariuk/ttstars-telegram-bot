from __future__ import annotations

import unittest
from decimal import Decimal

from app.enums.stars_order import StarsPaymentProvider
from app.services.crud.stars_order import StarsOrderService, ValidationError
from app.services.crud.stars_order_support.pricing import (
    CheckoutPricing,
    build_checkout_pricing,
    checkout_fixed_component_cents,
    format_amount,
    parse_money_cents,
    parse_percent,
)


class CheckoutPricingTests(unittest.TestCase):
    def test_balance_has_no_checkout_fee(self) -> None:
        pricing = build_checkout_pricing(
            provider=StarsPaymentProvider.BALANCE,
            net_amount_cents=1_000,
            payment_fee_percents={},
            payout_fee_percents={},
            payout_fixed_cents={},
            error_type=ValidationError,
        )

        self.assertEqual(
            pricing,
            CheckoutPricing(
                net_amount_cents=1_000,
                invoice_amount_cents=1_000,
                customer_total_cents=1_000,
                fee_percent_text="0",
            ),
        )

    def test_deducted_payment_fee_is_grossed_up_with_payout_costs(self) -> None:
        pricing = build_checkout_pricing(
            provider=StarsPaymentProvider.CRYPTO_BOT,
            net_amount_cents=1_000,
            payment_fee_percents={StarsPaymentProvider.CRYPTO_BOT: Decimal("5")},
            payout_fee_percents={StarsPaymentProvider.CRYPTO_BOT: Decimal("2")},
            payout_fixed_cents={StarsPaymentProvider.CRYPTO_BOT: 50},
            error_type=ValidationError,
        )

        self.assertEqual(pricing.invoice_amount_cents, 1_128)
        self.assertEqual(pricing.customer_total_cents, 1_128)
        self.assertEqual(pricing.fee_percent_text, "7.41")

    def test_on_top_payment_fee_is_added_to_customer_total(self) -> None:
        pricing = build_checkout_pricing(
            provider=StarsPaymentProvider.PLATEGA_PAY,
            net_amount_cents=1_000,
            payment_fee_percents={StarsPaymentProvider.PLATEGA_PAY: Decimal("5")},
            payout_fee_percents={StarsPaymentProvider.PLATEGA_PAY: Decimal("2")},
            payout_fixed_cents={StarsPaymentProvider.PLATEGA_PAY: 50},
            error_type=ValidationError,
        )

        self.assertEqual(pricing.invoice_amount_cents, 1_072)
        self.assertEqual(pricing.customer_total_cents, 1_126)
        self.assertEqual(pricing.fee_percent_text, "7.14")

    def test_invalid_fee_configuration_uses_requested_error_type(self) -> None:
        with self.assertRaisesRegex(ValidationError, "Invalid payment fee configuration"):
            build_checkout_pricing(
                provider=StarsPaymentProvider.CRYPTO_BOT,
                net_amount_cents=1_000,
                payment_fee_percents={StarsPaymentProvider.CRYPTO_BOT: Decimal("100")},
                payout_fee_percents={},
                payout_fixed_cents={},
                error_type=ValidationError,
            )

    def test_service_facade_returns_shared_pricing_type(self) -> None:
        service = object.__new__(StarsOrderService)
        service.payment_fee_percents = {}
        service.payout_fee_percents = {}
        service.payout_fixed_cents = {}

        pricing = service.preview_checkout_pricing(
            provider=StarsPaymentProvider.BALANCE,
            net_amount_cents=250,
        )

        self.assertIsInstance(pricing, CheckoutPricing)
        self.assertEqual(pricing.customer_total_cents, 250)

    def test_fixed_payout_cost_is_grossed_up_by_percentage_fees(self) -> None:
        fixed_cents = checkout_fixed_component_cents(
            provider=StarsPaymentProvider.CRYPTO_BOT,
            payment_fee_percents={StarsPaymentProvider.CRYPTO_BOT: Decimal("5")},
            payout_fee_percents={StarsPaymentProvider.CRYPTO_BOT: Decimal("2")},
            payout_fixed_cents={StarsPaymentProvider.CRYPTO_BOT: 50},
        )

        self.assertEqual(fixed_cents, 54)

    def test_service_formats_compact_fee_with_fixed_component(self) -> None:
        service = object.__new__(StarsOrderService)
        service.payment_fee_percents = {StarsPaymentProvider.CRYPTO_BOT: Decimal("5")}
        service.payout_fee_percents = {StarsPaymentProvider.CRYPTO_BOT: Decimal("2")}
        service.payout_fixed_cents = {StarsPaymentProvider.CRYPTO_BOT: 50}

        text = service.provider_checkout_fee_display_text(
            provider=StarsPaymentProvider.CRYPTO_BOT,
            net_amount_cents=1_000,
            compact=True,
        )

        self.assertEqual(text, "7.41%+$0.54")


class PricingConfigurationTests(unittest.TestCase):
    def test_percent_parser_uses_default_and_clamps_range(self) -> None:
        self.assertEqual(parse_percent("", default="3"), Decimal("3"))
        self.assertEqual(parse_percent("invalid", default="3"), Decimal("3"))
        self.assertEqual(parse_percent("-2", default="3"), Decimal("0"))
        self.assertEqual(parse_percent("100", default="3"), Decimal("99.99"))

    def test_money_parser_rounds_half_up_and_rejects_negative_values(self) -> None:
        self.assertEqual(parse_money_cents("1.235", default="0"), 124)
        self.assertEqual(parse_money_cents("invalid", default="2.50"), 250)
        self.assertEqual(parse_money_cents("-1", default="2.50"), 0)

    def test_amount_formatter_removes_only_insignificant_zeroes(self) -> None:
        self.assertEqual(format_amount(Decimal("1.20")), "1.2")
        self.assertEqual(format_amount(Decimal("1.235")), "1.24")
        self.assertEqual(format_amount(Decimal("0")), "0")


if __name__ == "__main__":
    unittest.main()
