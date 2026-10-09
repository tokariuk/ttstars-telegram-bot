from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.endpoints.miniapp.routes.admin import execute_sell_stars_refund
from app.enums.stars_sell_order import StarsSellOrderStatus


class AdminSellRefundTests(unittest.IsolatedAsyncioTestCase):
    async def test_refund_calls_telegram_before_marking_order_refunded(self) -> None:
        order = SimpleNamespace(
            id=42,
            user_id=101,
            status=StarsSellOrderStatus.PAID_HOLD,
            telegram_payment_charge_id="charge-123",
        )
        bot = SimpleNamespace(refund_star_payment=AsyncMock(return_value=True))
        service = SimpleNamespace(mark_refunded=AsyncMock(return_value=order))

        result = await execute_sell_stars_refund(
            order=order,
            bot=bot,
            service=service,
            note="user request",
        )

        bot.refund_star_payment.assert_awaited_once_with(
            user_id=101,
            telegram_payment_charge_id="charge-123",
        )
        service.mark_refunded.assert_awaited_once_with(order_id=42, note="user request")
        self.assertIs(result, order)


if __name__ == "__main__":
    unittest.main()
