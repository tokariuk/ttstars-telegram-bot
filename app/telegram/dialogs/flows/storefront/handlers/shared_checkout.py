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
from app.gifts import get_gift_pack_by_id
from app.models.dto.stars_order import StarsOrderDto
from app.services.crud.stars_order import CheckoutPricing
from app.stars import normalize_recipient_username, price_usd_for_cents
from app.telegram.dialogs.common import get_i18n, get_user
from app.telegram.dialogs.common.premium_emoji import CLOSE_EMOJI_ID, WALLET_EMOJI_ID
from app.telegram.keyboards.callback_data.order import CDOrderCheckoutCancel

from .shared_constants import GIFT_NAME_MESSAGE_BY_KEY
from .shared_services import stars_order_service


def _localized_gift_name(i18n: Any, *, gift_id: str) -> str:
    gift = get_gift_pack_by_id(gift_id=gift_id)
    if gift is None:
        return gift_id
    message_key = GIFT_NAME_MESSAGE_BY_KEY.get(gift.key)
    if message_key is None:
        return gift.label
    message_getter = getattr(i18n.messages, message_key, None)
    if message_getter is None:
        return gift.label
    return str(message_getter())


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
    if order.product_type == StarsOrderProductType.GIFT:
        gift_name = (
            _localized_gift_name(i18n=i18n, gift_id=order.gift_id)
            if order.gift_id
            else "—"
        )
        recipient_display = (
            f"@{order.recipient_username}"
            if normalize_recipient_username(order.recipient_username) is not None
            else str(order.recipient_user_id or 0)
        )
        visibility = (
            str(i18n.messages.gift_sender_private_option())
            if order.gift_sender_private
            else str(i18n.messages.gift_sender_visible_option())
        )
        return str(
            i18n.messages.order_checkout_message_gift(
                recipient_id=recipient_display,
                gift=gift_name,
                amount=amount,
                fee_text=fee_text,
                pay_amount=total_with_fee,
                message=order.gift_message or "—",
                sender_visibility=visibility,
            )
        )
    if order.product_type == StarsOrderProductType.PREMIUM:
        return str(
            i18n.messages.order_checkout_message_premium(
                months=order.premium_months or 0,
                recipient=order.recipient_username,
                amount=amount,
                fee_text=fee_text,
                pay_amount=total_with_fee,
            )
        )
    return str(
        i18n.messages.order_checkout_message_stars(
            stars=order.stars_count,
            recipient=order.recipient_username,
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
