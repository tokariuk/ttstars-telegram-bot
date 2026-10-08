from __future__ import annotations

import unittest
from typing import Any, cast

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.dto.healthcheck import HealthcheckResponse
from app.services.healthcheck import check_postgres, check_redis
from app.services.redis import RedisRepository

from .support import required_test_url


class InfrastructureHealthcheckTests(unittest.IsolatedAsyncioTestCase):
    async def test_postgres_and_redis_are_reported_ready(self) -> None:
        postgres_url = required_test_url("TEST_POSTGRES_URL")
        redis_url = required_test_url("TEST_REDIS_URL")
        engine = create_async_engine(postgres_url)
        session_pool = async_sessionmaker(engine, expire_on_commit=False)
        redis_client = Redis.from_url(redis_url)
        redis_repository = RedisRepository(
            client=redis_client,
            config=cast(Any, object()),
        )
        response = HealthcheckResponse.ready(service="integration-test", ready=True)

        try:
            await check_postgres(response=response, session_pool=session_pool)
            await check_redis(response=response, redis=redis_repository)
        finally:
            await redis_client.aclose(close_connection_pool=True)
            await engine.dispose()

        results = {result.name: result for result in response.results}
        self.assertTrue(results["postgres"].ok, results["postgres"].message)
        self.assertTrue(results["redis"].ok, results["redis"].message)


if __name__ == "__main__":
    unittest.main()
