from __future__ import annotations

import unittest
from typing import Any, cast

from redis.asyncio import Redis

from app.services.redis.repository import RedisRepository


class RedisKeysFake:
    def __init__(self, keys: list[bytes | str]) -> None:
        self.keys_result = keys
        self.deleted: tuple[bytes | str, ...] | None = None

    async def keys(self, _: str) -> list[bytes | str]:
        return self.keys_result

    async def delete(self, *keys: bytes | str) -> int:
        self.deleted = keys
        return len(keys)


class RedisRepositoryTests(unittest.IsolatedAsyncioTestCase):
    async def test_clear_webhooks_deletes_byte_and_string_keys_unchanged(self) -> None:
        client = RedisKeysFake([b"webhook:7:first", "webhook:7:second"])
        repository = RedisRepository(
            client=cast(Redis, client),
            config=cast(Any, object()),
        )

        await repository.clear_webhooks(bot_id=7)

        self.assertEqual(client.deleted, (b"webhook:7:first", "webhook:7:second"))

    async def test_clear_webhooks_skips_delete_for_empty_result(self) -> None:
        client = RedisKeysFake([])
        repository = RedisRepository(
            client=cast(Redis, client),
            config=cast(Any, object()),
        )

        await repository.clear_webhooks(bot_id=7)

        self.assertIsNone(client.deleted)


if __name__ == "__main__":
    unittest.main()
