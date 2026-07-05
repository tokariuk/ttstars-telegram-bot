from __future__ import annotations

import contextlib

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager

from app.telegram.dialogs.common import reset_stack_to
from app.telegram.keyboards.callback_data.menu import CDDeposit, CDMenu

from ..states import StorefrontSG
from .check_inline import CHECK_CLAIMED_NOOP_CALLBACK, CHECK_PENDING_NOOP_CALLBACK


async def ignore_claimed_check_button(callback: CallbackQuery) -> None:
    with contextlib.suppress(Exception):
        await callback.answer()


async def ignore_pending_check_button(callback: CallbackQuery) -> None:
    with contextlib.suppress(Exception):
        await callback.answer()


async def handle_help(
    _: Message,
    dialog_manager: DialogManager,
) -> None:
    await reset_stack_to(dialog_manager=dialog_manager, state=StorefrontSG.faq)


async def legacy_menu_callback(
    _: CallbackQuery,
    dialog_manager: DialogManager,
) -> None:
    await reset_stack_to(dialog_manager=dialog_manager, state=StorefrontSG.menu)


async def legacy_deposit_callback(
    _: CallbackQuery,
    dialog_manager: DialogManager,
) -> None:
    await reset_stack_to(dialog_manager=dialog_manager, state=StorefrontSG.topup_amount)


__all__ = [
    "CDDeposit",
    "CDMenu",
    "CHECK_CLAIMED_NOOP_CALLBACK",
    "CHECK_PENDING_NOOP_CALLBACK",
    "handle_help",
    "ignore_claimed_check_button",
    "ignore_pending_check_button",
    "legacy_deposit_callback",
    "legacy_menu_callback",
]

