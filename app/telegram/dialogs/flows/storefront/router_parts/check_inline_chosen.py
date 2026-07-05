from __future__ import annotations

import contextlib

from aiogram import Bot
from aiogram.types import ChosenInlineResult
from aiogram_i18n import I18nContext

from app.enums.check import CheckStatus
from app.services.crud.check import CheckService
from app.services.crud.check import (
    InsufficientBalanceError as CheckInsufficientBalanceError,
)
from app.services.crud.check import ValidationError as CheckValidationError
from app.stars import price_usd_for_cents

from .check_inline_common import (
    activate_markup,
    card_preview_url,
    consume_inline_draft_record,
    inline_check_message_text,
    parse_inline_create_result_id,
    parse_inline_share_result_id,
    send_inline_fallback_message,
)


async def handle_chosen_inline_check(  # noqa: C901
    event: ChosenInlineResult,
    check_service: CheckService,
    i18n: I18nContext,
) -> None:
    bot = event.bot
    if not isinstance(bot, Bot):
        return
    creator_id = event.from_user.id
    draft_nonce = parse_inline_create_result_id(event.result_id)
    if draft_nonce is not None:
        draft_record = await consume_inline_draft_record(
            check_service=check_service,
            nonce=draft_nonce,
        )
        if draft_record is None or draft_record.creator_id != creator_id:
            await send_inline_fallback_message(
                event=event,
                text=str(i18n.messages.check_inline_draft_missing()),
            )
            return

        try:
            check = await check_service.create_stars_check(
                creator_id=creator_id,
                stars_count=draft_record.stars_count,
                inline_message_id=event.inline_message_id,
            )
        except CheckInsufficientBalanceError:
            if event.inline_message_id:
                with contextlib.suppress(Exception):
                    await bot.edit_message_text(
                        text=str(i18n.messages.check_inline_unavailable()),
                        inline_message_id=event.inline_message_id,
                    )
            else:
                await send_inline_fallback_message(
                    event=event,
                    text=str(i18n.messages.check_inline_unavailable()),
                )
            return
        except CheckValidationError:
            if event.inline_message_id:
                with contextlib.suppress(Exception):
                    await bot.edit_message_text(
                        text=str(i18n.messages.check_inline_draft_missing()),
                        inline_message_id=event.inline_message_id,
                    )
            else:
                await send_inline_fallback_message(
                    event=event,
                    text=str(i18n.messages.check_inline_draft_missing()),
                )
            return

        me = await bot.get_me()
        bot_username = me.username or "unknown_bot"
        image_url = card_preview_url(
            stars_count=check.stars_count,
            amount_usd=price_usd_for_cents(check.amount_cents),
            seed=check.code,
            base_url=check_service.config.server.url,
        )
        check_link = check_service.build_start_link(bot_username=bot_username, code=check.code)
        ready_text = inline_check_message_text(
            i18n=i18n,
            image_url=image_url,
            check=check,
        )
        ready_markup = activate_markup(
            i18n=i18n,
            activate_url=check_link,
        )

        if event.inline_message_id:
            with contextlib.suppress(Exception):
                await bot.edit_message_text(
                    text=ready_text,
                    inline_message_id=event.inline_message_id,
                    reply_markup=ready_markup,
                    parse_mode="HTML",
                )
                return
        await send_inline_fallback_message(
            event=event,
            text=ready_text,
            reply_markup=ready_markup,
        )
        return

    share_code = parse_inline_share_result_id(event.result_id)
    if share_code is None:
        return
    check = await check_service.get_by_code(code=share_code)
    if check is None or check.creator_id <= 0:
        return
    if check.status == CheckStatus.ACTIVE and event.inline_message_id:
        me = await bot.get_me()
        bot_username = me.username or "unknown_bot"
        image_url = card_preview_url(
            stars_count=check.stars_count,
            amount_usd=price_usd_for_cents(check.amount_cents),
            seed=check.code,
            base_url=check_service.config.server.url,
        )
        activate_link = CheckService.build_start_link(bot_username=bot_username, code=check.code)
        with contextlib.suppress(Exception):
            await bot.edit_message_text(
                text=inline_check_message_text(
                    i18n=i18n,
                    image_url=image_url,
                    check=check,
                ),
                inline_message_id=event.inline_message_id,
                reply_markup=activate_markup(
                    i18n=i18n,
                    activate_url=activate_link,
                ),
                parse_mode="HTML",
            )
    await check_service.attach_inline_message_id(
        creator_id=check.creator_id,
        check_id=check.id,
        inline_message_id=event.inline_message_id,
    )

