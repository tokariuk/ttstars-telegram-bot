from __future__ import annotations

import asyncio
import unittest
from typing import Any, cast

from aiogram import Bot, Dispatcher
from aiogram.methods import SendMessage, TelegramMethod
from aiogram.types import Update
from fastapi import FastAPI

from app.endpoints.telegram import TelegramRequestHandler
from app.utils import mjson

from .fakes import asgi_request


class DispatcherFake:
    def __init__(self, *, result: TelegramMethod[Any] | None = None) -> None:
        self.workflow_data: dict[str, Any] = {"dependency": "available"}
        self.result = result
        self.updates: list[Update] = []
        self.api_requests: list[TelegramMethod[Any]] = []
        self.startups: list[dict[str, Any]] = []
        self.shutdowns: list[dict[str, Any]] = []

    async def feed_update(self, *, update: Update, **_: Any) -> TelegramMethod[Any] | None:
        self.updates.append(update)
        return self.result

    async def silent_call_request(self, *, result: TelegramMethod[Any], **_: Any) -> None:
        self.api_requests.append(result)

    async def emit_startup(self, **kwargs: Any) -> None:
        self.startups.append(kwargs)

    async def emit_shutdown(self, **kwargs: Any) -> None:
        self.shutdowns.append(kwargs)


class BotFake:
    pass


class TelegramWiringIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_webhook_parses_update_and_executes_returned_method(self) -> None:
        method = SendMessage(chat_id=123, text="handled locally")
        dispatcher = DispatcherFake(result=method)
        handler = TelegramRequestHandler(
            dispatcher=cast(Dispatcher, dispatcher),
            bot=cast(Bot, BotFake()),
            path="/telegram",
            secret_token="secret-token",
        )
        app = FastAPI()
        app.include_router(handler.router)

        response = await asgi_request(
            app,
            method="POST",
            path="/telegram",
            body=mjson.bytes_encode(
                {
                    "update_id": 501,
                    "message": {
                        "message_id": 601,
                        "date": 1_700_000_000,
                        "chat": {"id": 123, "type": "private"},
                        "from": {
                            "id": 123,
                            "is_bot": False,
                            "first_name": "Integration",
                        },
                        "text": "/start",
                    },
                }
            ),
            headers={"x-telegram-bot-api-secret-token": "secret-token"},
        )
        await self._drain_handler_tasks(handler)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), None)
        self.assertEqual(len(dispatcher.updates), 1)
        update = dispatcher.updates[0]
        self.assertEqual(update.update_id, 501)
        self.assertIsNotNone(update.message)
        assert update.message is not None
        self.assertEqual(update.message.text, "/start")
        self.assertEqual(dispatcher.api_requests, [method])
        self.assertEqual(dispatcher.api_requests[0].model_dump()["text"], "handled locally")

    async def test_webhook_rejects_invalid_secret_before_dispatch(self) -> None:
        dispatcher = DispatcherFake()
        handler = TelegramRequestHandler(
            dispatcher=cast(Dispatcher, dispatcher),
            bot=cast(Bot, BotFake()),
            path="/telegram",
            secret_token="secret-token",
        )
        app = FastAPI()
        app.include_router(handler.router)

        response = await asgi_request(
            app,
            method="POST",
            path="/telegram",
            body=mjson.bytes_encode({"update_id": 502}),
            headers={"x-telegram-bot-api-secret-token": "wrong-token"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid secret token"})
        self.assertEqual(dispatcher.updates, [])

    async def test_startup_and_shutdown_are_idempotent(self) -> None:
        dispatcher = DispatcherFake()
        bot = BotFake()
        handler = TelegramRequestHandler(
            dispatcher=cast(Dispatcher, dispatcher),
            bot=cast(Bot, bot),
            path="/telegram",
        )

        await handler.startup()
        await handler.startup()
        await handler.shutdown()
        await handler.shutdown()

        self.assertEqual(len(dispatcher.startups), 1)
        self.assertEqual(len(dispatcher.shutdowns), 1)
        self.assertIs(dispatcher.startups[0]["dispatcher"], dispatcher)
        self.assertIs(dispatcher.startups[0]["bot"], bot)
        self.assertEqual(dispatcher.startups[0]["dependency"], "available")

    @staticmethod
    async def _drain_handler_tasks(handler: TelegramRequestHandler) -> None:
        await asyncio.sleep(0)
        tasks = tuple(handler._feed_update_tasks)
        if tasks:
            await asyncio.gather(*tasks)


if __name__ == "__main__":
    unittest.main()
