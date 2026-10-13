from __future__ import annotations

import unittest
from datetime import UTC, datetime
from unittest.mock import AsyncMock

from app.services.postgres.repositories.balance_topups import BalanceTopupsRepository
from app.services.postgres.repositories.stars_orders import StarsOrdersRepository


class AdminStatsRepositoryTests(unittest.IsolatedAsyncioTestCase):
    async def test_order_period_totals_only_count_completed_fulfillments(self) -> None:
        session = AsyncMock()
        session.scalar.return_value = 0
        repository = StarsOrdersRepository(session=session)

        await repository.count_completed_since(since=datetime(2026, 10, 12, tzinfo=UTC))
        await repository.sum_completed_amount_since(
            since=datetime(2026, 10, 12, tzinfo=UTC)
        )

        statements = [str(call.args[0]) for call in session.scalar.await_args_list]
        self.assertEqual(len(statements), 2)
        for statement in statements:
            self.assertIn("store_orders.status", statement)
            self.assertIn("store_orders.fulfilled_at", statement)

    async def test_topup_period_totals_exclude_linked_and_incomplete_rows(self) -> None:
        session = AsyncMock()
        session.scalar.return_value = 0
        repository = BalanceTopupsRepository(session=session)

        await repository.count_completed_since(
            since=datetime(2026, 10, 12, tzinfo=UTC), include_linked=False
        )
        await repository.sum_completed_amount_since(
            since=datetime(2026, 10, 12, tzinfo=UTC), include_linked=False
        )

        statements = [str(call.args[0]) for call in session.scalar.await_args_list]
        self.assertEqual(len(statements), 2)
        for statement in statements:
            self.assertIn("balance_topups.status", statement)
            self.assertIn("balance_topups.paid_at", statement)
            self.assertIn("balance_topups.linked_order_id IS NULL", statement)


if __name__ == "__main__":
    unittest.main()
