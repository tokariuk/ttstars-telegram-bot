from __future__ import annotations

import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Callable
from unittest.mock import AsyncMock, patch

from app.enums.stars_sell_order import StarsSellOrderStatus
from app.telegram.dialogs.flows.admin.getters import stars_sell as getters


class _Messages:
    def admin_stars_sell_history_detail_screen(self, **values: object) -> str:
        required = {"order_id", "user_id", "status", "stars_count", "wallet"}
        missing = required.difference(values)
        if missing:
            raise KeyError(f"missing Fluent values: {sorted(missing)}")
        return "rendered details"

    def __getattr__(self, _name: str) -> Callable[..., str]:
        return lambda **_values: "localized"


class _Buttons:
    def __getattr__(self, _name: str) -> Callable[..., str]:
        return lambda **_values: "button"


class AdminStarsSellGetterTests(unittest.IsolatedAsyncioTestCase):
    async def test_history_details_supplies_every_required_identity_value(self) -> None:
        now = datetime.now(timezone.utc)
        order = SimpleNamespace(
            id=41,
            user_id=73,
            status=StarsSellOrderStatus.COMPLETED,
            stars_count=500,
            payout_amount_cents=725,
            payout_wallet="wallet",
            invoice_total_amount=510,
            invoice_payload="payload",
            paid_stars_amount=510,
            created_at=now,
            paid_at=now,
            payout_available_at=now,
            completed_at=now,
            rejected_at=None,
            refunded_at=None,
            failure_reason=None,
            resolution_reason=None,
            resolution_note=None,
        )
        service = SimpleNamespace(get_user_order=AsyncMock(return_value=order))
        i18n_context = SimpleNamespace(messages=_Messages(), buttons=_Buttons())
        manager = SimpleNamespace()

        with (
            patch.object(getters, "i18n", return_value=i18n_context),
            patch.object(getters, "stars_sell_order_service", return_value=service),
            patch.object(getters, "get_user", return_value=SimpleNamespace(id=73)),
            patch.object(getters, "stars_sell_history_selected_order_id", return_value=41),
            patch.object(getters, "consume_notice", return_value=None),
            patch.object(getters, "admin_banner_url", return_value=""),
        ):
            result = await getters.stars_sell_history_details_getter(manager)

        self.assertEqual(result["text"], "rendered details")


if __name__ == "__main__":
    unittest.main()
