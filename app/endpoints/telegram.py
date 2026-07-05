import asyncio
import logging
import secrets
from typing import Annotated, Any, Optional

from aiogram import Bot, Dispatcher
from aiogram.methods import TelegramMethod
from aiogram.types import Update
from aiogram_dialog.api.exceptions import UnknownIntent
from fastapi import APIRouter, Body, Header, HTTPException, status

logger = logging.getLogger(__name__)


class TelegramRequestHandler:
    dispatcher: Dispatcher
    bot: Bot
    secret_token: Optional[str]
    _feed_update_tasks: set[asyncio.Task[Any]]
    _startup_completed: bool
    _shutdown_completed: bool

    def __init__(
        self,
        dispatcher: Dispatcher,
        bot: Bot,
        path: str,
        secret_token: Optional[str] = None,
    ) -> None:
        """
        Base handler that helps to handle incoming request from aiohttp
        and propagate it to the Dispatcher
        """
        self.dispatcher = dispatcher
        self.bot = bot
        self.secret_token = secret_token
        self.router: APIRouter = APIRouter(
            on_startup=(self.startup,),
            on_shutdown=(self.shutdown,),
            include_in_schema=False,
        )
        self.router.add_api_route(path=path, endpoint=self.handle, methods=["POST"])
        self._feed_update_tasks = set()
        self._startup_completed = False
        self._shutdown_completed = False

    async def startup(self) -> None:
        if self._startup_completed:
            return
        await self.dispatcher.emit_startup(
            dispatcher=self.dispatcher,
            bot=self.bot,
            **self.dispatcher.workflow_data,
        )
        self._startup_completed = True
        self._shutdown_completed = False

    async def shutdown(self) -> None:
        if self._shutdown_completed:
            return
        await self.dispatcher.emit_shutdown(
            dispatcher=self.dispatcher,
            bot=self.bot,
            **self.dispatcher.workflow_data,
        )
        self._shutdown_completed = True
        self._startup_completed = False

    async def close(self) -> None:
        await self.bot.session.close()

    def verify_secret(self, telegram_secret_token: str) -> bool:
        if self.secret_token:
            return secrets.compare_digest(telegram_secret_token, self.secret_token)
        return True

    async def _feed_update(self, update: Update) -> None:
        try:
            result = await self.dispatcher.feed_update(
                bot=self.bot,
                update=update,
                dispatcher=self.dispatcher,
            )
            if isinstance(result, TelegramMethod):
                await self.dispatcher.silent_call_request(bot=self.bot, result=result)
        except UnknownIntent:
            callback = update.callback_query
            if callback is None:
                return
            try:
                await self.bot.answer_callback_query(
                    callback_query_id=callback.id,
                    text="Інтерфейс оновився. Відкрий /start",
                    show_alert=False,
                )
            except Exception:
                pass
            try:
                await self.bot.send_message(
                    chat_id=callback.from_user.id,
                    text="Кнопка застаріла після оновлення. Надішли /start.",
                )
            except Exception:
                pass
        except Exception:
            logger.exception("Failed to process Telegram update.")

    async def _handle_request_background(self, update: Update) -> None:
        feed_update_task: asyncio.Task[Any] = asyncio.create_task(self._feed_update(update=update))
        self._feed_update_tasks.add(feed_update_task)
        feed_update_task.add_done_callback(self._feed_update_tasks.discard)

    async def handle(
        self,
        update: Annotated[Update, Body()],
        x_telegram_bot_api_secret_token: Annotated[str, Header()],
    ) -> None:
        if not self.verify_secret(x_telegram_bot_api_secret_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid secret token",
            )
        await self._handle_request_background(update=update)
