from __future__ import annotations

from typing import Final

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager

from app.telegram.dialogs.common import reset_stack_to
from app.telegram.dialogs.flows.storefront.states import StorefrontSG
from app.telegram.filters import ADMIN_FILTER

from .states import AdminSG

router: Final[Router] = Router(name=__name__)
router.message.filter(ADMIN_FILTER)
router.callback_query.filter(ADMIN_FILTER)


@router.message(CommandStart())
async def handle_admin_start(
    message: Message,
    dialog_manager: DialogManager,
) -> None:
    _ = message
    await reset_stack_to(dialog_manager=dialog_manager, state=StorefrontSG.menu)


@router.message(Command("admin"))
async def handle_admin_open(
    message: Message,
    dialog_manager: DialogManager,
) -> None:
    _ = message
    await reset_stack_to(dialog_manager=dialog_manager, state=AdminSG.menu)


__all__ = ["router"]
