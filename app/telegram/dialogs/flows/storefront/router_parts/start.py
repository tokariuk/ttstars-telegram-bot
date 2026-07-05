from __future__ import annotations

from aiogram import Bot
from aiogram.filters import CommandObject
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_i18n import I18nContext

from app.models.dto.user import UserDto
from app.services.crud.check import CheckClaimOutcome, CheckService
from app.services.crud.user import UserService
from app.telegram.dialogs.common import reset_stack_to
from app.telegram.dialogs.flows.storefront.handlers.shared import (
    CHECKS_SELECTED_CHECK_ID_KEY,
    STATE_NOTICE_KEY,
)

from ..states import StorefrontSG
from .check_inline import (
    claim_notice,
    mark_inline_claimed,
    notify_creator_claimed,
)


async def handle_start(
    message: Message,
    dialog_manager: DialogManager,
    user: UserDto,
    user_service: UserService,
    check_service: CheckService,
    i18n: I18nContext,
    command: CommandObject | None = None,
    user_is_new: bool = False,
) -> None:
    claim_message: str | None = None
    if command is not None and command.args:
        check_code = check_service.parse_start_payload(command.args)
        if check_code is not None:
            owner_check = await check_service.get_by_code(code=check_code)
            if owner_check is not None and owner_check.creator_id == user.id:
                await reset_stack_to(
                    dialog_manager=dialog_manager,
                    state=StorefrontSG.checks_details,
                    data={CHECKS_SELECTED_CHECK_ID_KEY: owner_check.id},
                )
                return
            if owner_check is not None and user_is_new:
                await user_service.try_bind_referrer(
                    user_id=user.id,
                    referrer_id=owner_check.creator_id,
                )
            claim_result = await check_service.claim_check(
                code=check_code,
                recipient_user_id=user.id,
                recipient_username=message.from_user.username if message.from_user else None,
            )
            if claim_result.outcome == CheckClaimOutcome.PASSWORD_REQUIRED:
                await dialog_manager.start(
                    state=StorefrontSG.checks_claim_password,
                    mode=StartMode.RESET_STACK,
                    data={
                        "check_code": check_code,
                    },
                )
                return

            bot = message.bot
            if (
                isinstance(bot, Bot)
                and claim_result.outcome == CheckClaimOutcome.CLAIMED
                and claim_result.check is not None
            ):
                claimer_label = (
                    f"@{message.from_user.username}"
                    if message.from_user and message.from_user.username
                    else (message.from_user.full_name if message.from_user else str(user.id))
                )
                await notify_creator_claimed(
                    bot=bot,
                    i18n=i18n,
                    user_service=user_service,
                    check=claim_result.check,
                    claimer_label=claimer_label,
                )
                await mark_inline_claimed(
                    bot=bot,
                    i18n=i18n,
                    check=claim_result.check,
                )
            claim_message = claim_notice(
                i18n=i18n,
                check=claim_result.check,
                outcome=claim_result.outcome,
            )
        else:
            await user_service.try_bind_referrer_from_start_payload(
                user_id=user.id,
                payload=command.args,
            )
    await reset_stack_to(
        dialog_manager=dialog_manager,
        state=StorefrontSG.menu,
        data=({STATE_NOTICE_KEY: claim_message} if claim_message else None),
    )

