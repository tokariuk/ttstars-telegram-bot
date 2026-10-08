from __future__ import annotations

import unittest
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, cast
from uuid import uuid4

from alembic.config import Config
from alembic.script import ScriptDirectory
from redis.asyncio import Redis
from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.enums.stars_order import StarsOrderProductType, StarsOrderStatus, StarsPaymentProvider
from app.models.sql import BalanceTopup, StarsOrder, User
from app.services.crud.stars_order_support import topups as topup_support
from app.services.postgres.repositories.general import Repository
from app.services.redis import RedisRepository
from app.services.redis.keys import WebhookLockKey
from app.utils.key_builder import StorageKey

from .support import required_test_url


class IntegrationValueKey(StorageKey, prefix="integration"):
    identifier: str


class RepositoryIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        postgres_url = required_test_url("TEST_POSTGRES_URL")
        redis_url = required_test_url("TEST_REDIS_URL")
        self.engine = create_async_engine(postgres_url)
        self.session_pool = async_sessionmaker(self.engine, expire_on_commit=False)
        self.redis_client = Redis.from_url(redis_url)
        self.redis = RedisRepository(
            client=self.redis_client,
            config=cast(Any, object()),
        )
        suffix = uuid4().hex
        self.user_id = 1_000_000_000 + uuid4().int % 1_000_000_000
        self.redis_key = IntegrationValueKey(identifier=suffix)
        self.webhook_hashes = (f"{suffix}-first", f"{suffix}-second")

    async def asyncTearDown(self) -> None:
        await self.redis.delete(self.redis_key)
        await self.redis.clear_webhooks(bot_id=self.user_id)
        async with self.session_pool() as session:
            await session.execute(delete(StarsOrder).where(StarsOrder.user_id == self.user_id))
            await session.execute(delete(BalanceTopup).where(BalanceTopup.user_id == self.user_id))
            await session.execute(delete(User).where(User.id == self.user_id))
            await session.commit()
        await self.redis_client.aclose(close_connection_pool=True)
        await self.engine.dispose()

    async def test_database_revision_matches_alembic_head(self) -> None:
        async with self.session_pool() as session:
            revision = await session.scalar(text("SELECT version_num FROM alembic_version"))

        script = ScriptDirectory.from_config(Config("alembic.ini"))
        self.assertEqual(revision, script.get_current_head())

    async def test_redis_round_trip_and_wildcard_deletion(self) -> None:
        value = {"count": 7, "ready": True}
        await self.redis.set(self.redis_key, value)

        loaded = await self.redis.get(self.redis_key, dict[str, int | bool])

        self.assertEqual(loaded, value)
        for webhook_hash in self.webhook_hashes:
            await self.redis.set(
                WebhookLockKey(bot_id=self.user_id, webhook_hash=webhook_hash),
                True,
            )
        await self.redis.clear_webhooks(bot_id=self.user_id)
        remaining = await self.redis_client.keys(f"webhook_lock:{self.user_id}:*")
        self.assertEqual(remaining, [])

    async def test_postgres_repository_create_read_and_status_transition(self) -> None:
        async with self.session_pool() as session:
            repository = Repository(session=session)
            user = User(
                id=self.user_id,
                name="Integration User",
                language="en",
                language_code="en",
            )
            order = StarsOrder(
                user_id=self.user_id,
                recipient_username="integration_user",
                stars_count=50,
                product_type=StarsOrderProductType.STARS,
                premium_months=None,
                recipient_user_id=None,
                gift_id=None,
                gift_message=None,
                gift_sender_private=None,
                amount_cents=125,
                payment_provider=StarsPaymentProvider.CRYPTO_BOT,
                payment_currency="USDT",
                status=StarsOrderStatus.PENDING_PAYMENT,
            )
            await repository.uow.commit(user)
            await repository.uow.commit(order)

            loaded = await repository.stars_orders.get(order.id)
            transitioned = await repository.stars_orders.update_if_status(
                order_id=order.id,
                current_statuses=[StarsOrderStatus.PENDING_PAYMENT],
                status=StarsOrderStatus.PAYMENT_CONFIRMED,
                paid_at=datetime.now(UTC),
            )
            rejected = await repository.stars_orders.update_if_status(
                order_id=order.id,
                current_statuses=[StarsOrderStatus.PENDING_PAYMENT],
                status=StarsOrderStatus.FAILED,
            )

        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.user_id, self.user_id)
        self.assertIsNotNone(transitioned)
        assert transitioned is not None
        self.assertEqual(transitioned.status, StarsOrderStatus.PAYMENT_CONFIRMED)
        self.assertIsNone(rejected)

    async def test_topup_credit_transaction_updates_balance_and_status_once(self) -> None:
        async with self.session_pool() as session:
            repository = Repository(session=session)
            user = User(
                id=self.user_id,
                name="Topup Integration User",
                language="en",
                language_code="en",
            )
            await repository.uow.commit(user)
            topup = BalanceTopup(
                user_id=self.user_id,
                amount_cents=275,
                payment_provider=StarsPaymentProvider.CRYPTO_BOT,
                payment_currency="USDT",
                status=StarsOrderStatus.FULFILLING,
            )
            await repository.uow.commit(topup)
            topup_dto = topup.dto()

        stopped, linked_order_id = await topup_support._credit_topup_transaction(
            service=cast(Any, SimpleNamespace(session_pool=self.session_pool)),
            topup=topup_dto,
            error_cls=RuntimeError,
        )

        async with self.session_pool() as session:
            repository = Repository(session=session)
            updated_user = await repository.users.get(user_id=self.user_id)
            updated_topup = await repository.balance_topups.get(topup_id=topup.id)

        self.assertFalse(stopped)
        self.assertIsNone(linked_order_id)
        self.assertIsNotNone(updated_user)
        assert updated_user is not None
        self.assertEqual(updated_user.balance_cents, 275)
        self.assertIsNotNone(updated_topup)
        assert updated_topup is not None
        self.assertEqual(updated_topup.status, StarsOrderStatus.COMPLETED)
        self.assertIsNotNone(updated_topup.credited_at)
        self.assertIsNotNone(updated_topup.completed_at)


if __name__ == "__main__":
    unittest.main()
