from __future__ import annotations

import hashlib
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator

from aiogram import Bot, Dispatcher, loggers
from aiogram.methods import SetWebhook
from aiogram.types import Update
from fastapi import FastAPI

from app.endpoints.telegram import TelegramRequestHandler
from app.services.redis import RedisRepository
from app.utils import mjson

if TYPE_CHECKING:
    from app.models.config import AppConfig


_VALID_TELEGRAM_UPDATE_TYPES = frozenset(
    field_name
    for field_name in Update.model_fields
    if field_name != "update_id"
)


def _resolve_allowed_updates(dispatcher: Dispatcher) -> list[str]:
    resolved = dispatcher.resolve_used_update_types()
    allowed_updates: list[str] = []
    seen: set[str] = set()

    for update_type in resolved:
        if update_type not in _VALID_TELEGRAM_UPDATE_TYPES or update_type in seen:
            continue
        allowed_updates.append(update_type)
        seen.add(update_type)

    for required_update in ("message", "callback_query"):
        if required_update in seen:
            continue
        allowed_updates.append(required_update)
        seen.add(required_update)

    return allowed_updates


async def webhook_startup(
    dispatcher: Dispatcher,
    bot: Bot,
    config: AppConfig,
    redis_repository: RedisRepository,
) -> None:
    allowed_updates = _resolve_allowed_updates(dispatcher)
    url: str = config.server.build_url(path=config.telegram.webhook_path)
    method: SetWebhook = SetWebhook(
        url=url,
        allowed_updates=allowed_updates,
        secret_token=config.telegram.webhook_secret.get_secret_value(),
        drop_pending_updates=config.telegram.drop_pending_updates,
    )

    webhook_hash: str = hashlib.sha256(mjson.bytes_encode(method.model_dump())).hexdigest()
    has_same_hash = await redis_repository.is_webhook_set(bot_id=bot.id, webhook_hash=webhook_hash)
    webhook_info = await bot.get_webhook_info()
    has_same_url = webhook_info.url == url
    if has_same_hash and has_same_url:
        loggers.webhook.info("Skipping webhook setup, already set on url '%s'", url)
        return

    if not await bot(method):
        raise RuntimeError(f"Failed to set main bot webhook on url '{url}'")

    await redis_repository.clear_webhooks(bot_id=bot.id)
    await redis_repository.set_webhook(bot_id=bot.id, webhook_hash=webhook_hash)
    loggers.webhook.info("Main bot webhook successfully set on url '%s'", url)
    loggers.webhook.info("Webhook allowed_updates: %s", ", ".join(allowed_updates))


async def webhook_shutdown(
    bot: Bot,
    config: AppConfig,
    redis_repository: RedisRepository,
) -> None:
    if not config.telegram.reset_webhook:
        return
    if await bot.delete_webhook():
        await redis_repository.clear_webhooks(bot_id=bot.id)
        loggers.webhook.info("Dropped main bot webhook.")
    else:
        loggers.webhook.error("Failed to drop main bot webhook.")
    await bot.session.close()


@asynccontextmanager
async def webhook_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    handler: TelegramRequestHandler = app.state.tg_webhook_handler
    await handler.startup()
    yield
    await handler.shutdown()
