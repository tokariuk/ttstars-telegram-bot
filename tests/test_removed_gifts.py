from __future__ import annotations

import unittest
from datetime import UTC, datetime
from pathlib import Path

from app.enums.stars_order import StarsOrderProductType
from app.models.dto.stars_order import StarsOrderDto
from app.services.crud.stars_order_support.order_payloads import (
    prepare_balance_order_payload,
    prepare_external_order_payload,
)
from app.telegram.dialogs.flows.storefront.states import StorefrontSG


class RemovedGiftsTests(unittest.IsolatedAsyncioTestCase):
    def test_storefront_has_no_gift_purchase_states(self) -> None:
        self.assertFalse(
            any(
                state.state.split(":")[-1].startswith("gifts_")
                for state in StorefrontSG.__states__
            )
        )

    def test_historical_gift_orders_remain_readable(self) -> None:
        now = datetime(2026, 1, 1, tzinfo=UTC)
        order = StarsOrderDto.model_validate(
            {
                "id": 9,
                "user_id": 12,
                "recipient_username": "alice",
                "stars_count": 0,
                "product_type": "gift",
                "recipient_user_id": 12,
                "gift_id": "old-gift-id",
                "gift_sender_private": False,
                "amount_cents": 159,
                "payment_provider": "balance",
                "payment_currency": "USD",
                "status": "completed",
                "created_at": now,
                "updated_at": now,
            }
        )
        self.assertEqual(order.gift_id, "old-gift-id")

    async def test_old_product_cannot_create_a_new_order(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported order product type"):
            await prepare_balance_order_payload(
                service=None,
                recipient_username="alice",
                product_type=StarsOrderProductType.GIFT,
                recipient_user_id=None,
                validation_error_cls=ValueError,
            )
        with self.assertRaisesRegex(ValueError, "Unsupported order product type"):
            await prepare_external_order_payload(
                service=None,
                user_id=1,
                recipient_username="alice",
                stars_count=0,
                product_type=StarsOrderProductType.GIFT,
                premium_months=None,
                forced_amount_cents=None,
                recipient_user_id=None,
                validation_error_cls=ValueError,
            )

    def test_distribution_config_contains_no_gift_credentials(self) -> None:
        env_template = Path(__file__).resolve().parents[1] / ".env.dist"
        self.assertNotIn("TELEGRAM_GIFTS_USERBOT_", env_template.read_text())


if __name__ == "__main__":
    unittest.main()
