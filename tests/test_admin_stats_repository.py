from __future__ import annotations

import unittest
from datetime import UTC, date, datetime
from unittest.mock import AsyncMock, Mock

from app.services.crud.stars_order import _build_admin_activity_series
from app.services.postgres.repositories.balance_topups import BalanceTopupsRepository
from app.services.postgres.repositories.stars_orders import StarsOrdersRepository


class AdminStatsRepositoryTests(unittest.IsolatedAsyncioTestCase):
    async def test_order_activity_uses_each_event_timestamp(self) -> None:
        session = AsyncMock()
        session.execute.return_value.all = Mock(return_value=[])
        repository = StarsOrdersRepository(session=session)

        await repository.activity_by_day_since(
            since=datetime(2026, 9, 15, tzinfo=UTC)
        )

        statement = str(session.execute.await_args.args[0])
        for column in (
            "store_orders.created_at",
            "store_orders.paid_at",
            "store_orders.fulfilled_at",
            "store_orders.canceled_at",
            "store_orders.failed_at",
        ):
            self.assertIn(column, statement)

    async def test_topup_activity_excludes_linked_rows(self) -> None:
        session = AsyncMock()
        session.execute.return_value.all = Mock(return_value=[])
        repository = BalanceTopupsRepository(session=session)

        await repository.activity_by_day_since(
            since=datetime(2026, 9, 15, tzinfo=UTC),
            include_linked=False,
        )

        statement = str(session.execute.await_args.args[0])
        self.assertIn("balance_topups.linked_order_id IS NULL", statement)
        for column in (
            "balance_topups.created_at",
            "balance_topups.paid_at",
            "balance_topups.completed_at",
            "balance_topups.canceled_at",
            "balance_topups.failed_at",
        ):
            self.assertIn(column, statement)

    def test_activity_series_merges_sources_and_fills_missing_days(self) -> None:
        points = _build_admin_activity_series(
            end_date=date(2026, 10, 14),
            days=3,
            sources=(
                {
                    date(2026, 10, 12): {
                        "created": 2,
                        "paid": 1,
                        "completed": 1,
                        "canceled": 0,
                        "failed": 0,
                        "revenue_cents": 125,
                    }
                },
                {
                    date(2026, 10, 12): {
                        "created": 1,
                        "paid": 1,
                        "completed": 1,
                        "canceled": 0,
                        "failed": 0,
                        "revenue_cents": 75,
                    },
                    date(2026, 10, 14): {
                        "created": 1,
                        "paid": 0,
                        "completed": 0,
                        "canceled": 1,
                        "failed": 0,
                        "revenue_cents": 0,
                    },
                },
            ),
        )

        self.assertEqual([point.date.isoformat() for point in points], [
            "2026-10-12",
            "2026-10-13",
            "2026-10-14",
        ])
        self.assertEqual(points[0].created, 3)
        self.assertEqual(points[0].completed, 2)
        self.assertEqual(points[0].revenue_cents, 200)
        self.assertEqual(points[1].created, 0)
        self.assertEqual(points[2].canceled, 1)

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
