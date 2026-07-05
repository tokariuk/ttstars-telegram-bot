from __future__ import annotations

from aiogram import Bot
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from aiogram_i18n import I18nContext

from app.enums.check import CheckStatus
from app.services.crud.check import CheckService
from app.services.crud.user import UserService
from app.stars import get_stars_pack, parse_stars_count, price_usd_for_cents

from .check_inline_common import (
    activate_markup,
    card_preview_url,
    inline_check_message_text,
    parse_inline_share_query,
    pending_markup,
    store_inline_draft,
)


async def handle_inline_check_query(
    inline_query: InlineQuery,
    i18n: I18nContext,
    check_service: CheckService,
    user_service: UserService,
) -> None:
    bot = inline_query.bot
    if not isinstance(bot, Bot):
        return
    share_code = parse_inline_share_query(inline_query.query)
    if share_code is not None:
        check = await check_service.get_by_code(code=share_code)
        if check is None or check.status != CheckStatus.ACTIVE:
            await inline_query.answer(
                results=[
                    InlineQueryResultArticle(
                        id="checks_not_found",
                        title=str(i18n.messages.check_inline_not_found_title()),
                        description=str(i18n.messages.check_inline_not_found_description()),
                        input_message_content=InputTextMessageContent(
                            message_text=str(i18n.messages.check_claim_not_found()),
                            parse_mode="HTML",
                        ),
                    )
                ],
                cache_time=1,
                is_personal=True,
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
        activate_link = CheckService.build_start_link(bot_username=bot_username, code=check.code)
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id=f"check:share:{check.code}",
                    title=f"📃 {i18n.messages.check_inline_share_title(stars=check.stars_count)}",
                    description=str(
                        i18n.messages.check_inline_share_description(
                            amount=price_usd_for_cents(check.amount_cents),
                        )
                    ),
                    input_message_content=InputTextMessageContent(
                        message_text=inline_check_message_text(
                            i18n=i18n,
                            image_url=image_url,
                            check=check,
                        ),
                        parse_mode="HTML",
                    ),
                    reply_markup=activate_markup(
                        i18n=i18n,
                        activate_url=activate_link,
                    ),
                )
            ],
            cache_time=1,
            is_personal=True,
        )
        return

    stars_count = parse_stars_count(inline_query.query.strip())
    if stars_count is None:
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id="checks_help",
                    title=str(i18n.messages.check_inline_help_title()),
                    description=str(i18n.messages.check_inline_help_description()),
                    input_message_content=InputTextMessageContent(
                        message_text=str(i18n.messages.check_inline_help_message()),
                        parse_mode="HTML",
                    ),
                )
            ],
            cache_time=1,
            is_personal=True,
        )
        return

    pack = get_stars_pack(str(stars_count))
    user = await user_service.get(user_id=inline_query.from_user.id)
    user_balance_cents = int(user.balance_cents) if user is not None else 0
    if user_balance_cents < pack.price_cents:
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id="checks_not_enough",
                    title=str(i18n.messages.check_inline_not_enough_title()),
                    description=str(
                        i18n.messages.check_inline_not_enough_description(
                            current=price_usd_for_cents(user_balance_cents),
                            required=price_usd_for_cents(pack.price_cents),
                        )
                    ),
                    input_message_content=InputTextMessageContent(
                        message_text=str(
                            i18n.messages.check_inline_not_enough_message(
                                current=price_usd_for_cents(user_balance_cents),
                                required=price_usd_for_cents(pack.price_cents),
                            )
                        ),
                        parse_mode="HTML",
                    ),
                )
            ],
            cache_time=1,
            is_personal=True,
        )
        return

    nonce = await store_inline_draft(
        check_service=check_service,
        creator_id=inline_query.from_user.id,
        stars_count=pack.stars_count,
        amount_cents=pack.price_cents,
    )
    amount_text = price_usd_for_cents(pack.price_cents)
    await inline_query.answer(
        results=[
            InlineQueryResultArticle(
                id=f"check:create:{nonce}",
                title=f"📃 {i18n.messages.check_inline_create_title(stars=pack.stars_count)}",
                description=str(i18n.messages.check_inline_create_description(amount=amount_text)),
                input_message_content=InputTextMessageContent(
                    message_text=str(
                        i18n.messages.check_inline_placeholder(
                            stars=pack.stars_count,
                            amount=amount_text,
                        )
                    ),
                    parse_mode="HTML",
                ),
                reply_markup=pending_markup(),
            )
        ],
        cache_time=1,
        is_personal=True,
    )

