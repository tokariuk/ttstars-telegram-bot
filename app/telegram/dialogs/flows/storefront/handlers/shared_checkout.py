from __future__ import annotations

from typing import Any

from aiogram.enums.button_style import ButtonStyle
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputRichMessage,
)
from aiogram_dialog import DialogManager

from app.enums.stars_order import StarsOrderProductType
from app.models.dto.stars_order import StarsOrderDto
from app.services.crud.stars_order import CheckoutPricing
from app.stars import price_usd_for_cents
from app.telegram.dialogs.common import get_i18n, get_user
from app.telegram.dialogs.common.premium_emoji import CLOSE_EMOJI_ID, WALLET_EMOJI_ID
from app.telegram.html import escape_text
from app.telegram.keyboards.callback_data.order import CDOrderCheckoutCancel

from .shared_services import stars_order_service


def order_checkout_message_text(
    *,
    i18n: Any,
    order: StarsOrderDto,
    pricing: CheckoutPricing,
    fee_text: str,
) -> str:
    amount = price_usd_for_cents(order.amount_cents)
    total_with_fee = price_usd_for_cents(pricing.customer_total_cents)
    if order.product_type == StarsOrderProductType.TOPUP:
        return str(
            i18n.messages.order_checkout_message_topup(
                amount=amount,
                fee_text=fee_text,
                pay_amount=total_with_fee,
            )
        )
    if order.product_type == StarsOrderProductType.PREMIUM:
        return str(
            i18n.messages.order_checkout_message_premium(
                months=order.premium_months or 0,
                recipient=escape_text(order.recipient_username),
                amount=amount,
                fee_text=fee_text,
                pay_amount=total_with_fee,
            )
        )
    return str(
        i18n.messages.order_checkout_message_stars(
            stars=order.stars_count,
            recipient=escape_text(order.recipient_username),
            amount=amount,
            fee_text=fee_text,
            pay_amount=total_with_fee,
        )
    )


async def send_checkout_message(
    *,
    callback: CallbackQuery,
    dialog_manager: DialogManager,
    order: StarsOrderDto,
) -> None:
    if not order.checkout_url:
        return
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    bot = callback.bot
    if bot is None:
        raise RuntimeError("Bot is unavailable for sending checkout message.")
    service = stars_order_service(dialog_manager=dialog_manager)
    pricing = service.checkout_pricing_for_order(order=order)
    fee_text = service.provider_checkout_fee_display_text(
        provider=order.payment_provider,
        net_amount_cents=order.amount_cents,
    )

    sent = await bot.send_rich_message(
        chat_id=user.id,
        rich_message=InputRichMessage(
            html=order_checkout_message_text(
                i18n=i18n,
                order=order,
                pricing=pricing,
                fee_text=fee_text,
            ),
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=str(i18n.buttons.open_checkout()),
                        url=order.checkout_url,
                        icon_custom_emoji_id=WALLET_EMOJI_ID,
                        style=ButtonStyle.PRIMARY,
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=str(i18n.buttons.cancel_order()),
                        callback_data=CDOrderCheckoutCancel(order_id=order.id).pack(),
                        icon_custom_emoji_id=CLOSE_EMOJI_ID,
                        style=ButtonStyle.DANGER,
                    ),
                ],
            ]
        ),
    )
    await service.set_checkout_message_id(order_id=order.id, message_id=sent.message_id)
