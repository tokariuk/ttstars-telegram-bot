from __future__ import annotations

import unittest
from datetime import UTC, datetime
from types import SimpleNamespace

from aiogram_dialog.widgets.kbd import Button

from app.endpoints.miniapp.errors import ApiError, ErrorCode
from app.endpoints.miniapp.providers import SUPPORTED_PAYMENT_PROVIDERS, TOPUP_PAYMENT_PROVIDERS
from app.endpoints.miniapp.routes.orders import quote_order
from app.enums.stars_order import StarsOrderProductType, StarsPaymentProvider
from app.models.dto.balance_topup import BalanceTopupDto
from app.models.dto.miniapp import QuoteRequest
from app.models.dto.stars_order import StarsOrderDto
from app.services.crud.stars_order_support.constants import (
    EXTERNAL_PAYMENT_PROVIDERS,
)
from app.telegram.dialogs.flows.storefront.getters.common import provider_label
from app.telegram.dialogs.flows.storefront.windows.premium import premium_payment_window
from app.telegram.dialogs.flows.storefront.windows.stars import stars_payment_window
from app.telegram.dialogs.flows.storefront.windows.topup import topup_payment_window

HISTORICAL_PROVIDERS = (
    StarsPaymentProvider.NICE_PAY_RU,
    StarsPaymentProvider.NICE_PAY_KZ,
)


class DisabledNicePayTests(unittest.TestCase):
    def test_historical_provider_uses_archived_label_in_storefront(self) -> None:
        class Messages:
            def __getattr__(self, name: str) -> object:
                return lambda: "Archived" if name == "provider_archived" else "Current"

        i18n = SimpleNamespace(messages=Messages())
        self.assertEqual(provider_label(i18n, StarsPaymentProvider.NICE_PAY_RU), "Archived")

    def test_new_orders_and_catalog_exclude_nicepay(self) -> None:
        for provider in HISTORICAL_PROVIDERS:
            with self.subTest(provider=provider):
                self.assertNotIn(provider, EXTERNAL_PAYMENT_PROVIDERS)
                self.assertNotIn(provider, SUPPORTED_PAYMENT_PROVIDERS)
                self.assertNotIn(provider, TOPUP_PAYMENT_PROVIDERS)

    def test_storefront_payment_windows_have_no_nicepay_buttons(self) -> None:
        for window in (
            stars_payment_window,
            premium_payment_window,
            topup_payment_window,
        ):
            buttons = window.keyboard.buttons
            with self.subTest(window=window.state):
                self.assertFalse(
                    any(
                        isinstance(button, Button) and "nicepay" in button.widget_id.lower()
                        for button in buttons
                    )
                )

    def test_historical_orders_and_topups_remain_readable(self) -> None:
        now = datetime(2026, 1, 1, tzinfo=UTC)
        order = StarsOrderDto.model_validate(
            {
                "id": 1,
                "user_id": 2,
                "recipient_username": "alice",
                "stars_count": 100,
                "product_type": StarsOrderProductType.STARS,
                "amount_cents": 100,
                "payment_provider": "nice_pay_ru",
                "payment_currency": "RUB",
                "status": "canceled",
                "created_at": now,
                "updated_at": now,
            }
        )
        topup = BalanceTopupDto.model_validate(
            {
                "id": 3,
                "user_id": 2,
                "amount_cents": 100,
                "payment_provider": "nice_pay_kz",
                "payment_currency": "KZT",
                "status": "failed",
                "created_at": now,
                "updated_at": now,
            }
        )
        self.assertEqual(order.payment_provider.value, "nice_pay_ru")
        self.assertEqual(topup.payment_provider.value, "nice_pay_kz")


class DisabledNicePayQuoteTests(unittest.IsolatedAsyncioTestCase):
    async def test_quote_rejects_nicepay_before_calculating_price(self) -> None:
        for provider in HISTORICAL_PROVIDERS:
            with self.subTest(provider=provider):
                with self.assertRaises(ApiError) as caught:
                    await quote_order(
                        payload=QuoteRequest(
                            product_type=StarsOrderProductType.STARS,
                            provider=provider,
                            stars_count=100,
                        ),
                        _auth=None,  # type: ignore[arg-type]
                        stars_order_service=None,  # type: ignore[arg-type]
                    )
                self.assertEqual(caught.exception.code, ErrorCode.PROVIDER_UNAVAILABLE)


if __name__ == "__main__":
    unittest.main()
