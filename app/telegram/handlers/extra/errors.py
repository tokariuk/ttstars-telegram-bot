from typing import Any, Final

from aiogram import F, Router
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent
from aiogram_i18n import I18nContext

from app.errors.base import AppError

router: Final[Router] = Router(name=__name__)


@router.error(ExceptionTypeFilter(AppError), F.update.message)
async def handle_some_error(error: ErrorEvent, i18n: I18nContext) -> Any:
    message = error.update.message
    if message is None:
        return None
    await message.answer(text=i18n.messages.errors.something_went_wrong())
    return None
