from __future__ import annotations

from typing import Final

from aiogram import F, Router
from aiogram.filters import Command, CommandStart

from .router_parts import (
    CHECK_CLAIMED_NOOP_CALLBACK,
    CHECK_PENDING_NOOP_CALLBACK,
    CDDeposit,
    CDMenu,
    handle_chosen_inline_check,
    handle_help,
    handle_inline_check_query,
    handle_start,
    ignore_claimed_check_button,
    ignore_pending_check_button,
    legacy_deposit_callback,
    legacy_menu_callback,
)

router: Final[Router] = Router(name=__name__)

router.message.register(handle_start, CommandStart())
router.message.register(handle_start, Command("menu"))
router.inline_query.register(handle_inline_check_query)
router.chosen_inline_result.register(handle_chosen_inline_check)
router.callback_query.register(ignore_claimed_check_button, F.data == CHECK_CLAIMED_NOOP_CALLBACK)
router.callback_query.register(ignore_pending_check_button, F.data == CHECK_PENDING_NOOP_CALLBACK)
router.message.register(handle_help, Command("help"))
router.callback_query.register(legacy_menu_callback, CDMenu.filter())
router.callback_query.register(legacy_deposit_callback, CDDeposit.filter())

