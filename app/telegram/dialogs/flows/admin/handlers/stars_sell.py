from __future__ import annotations

import contextlib
from re import Pattern
from re import compile as re_compile

from aiogram.enums.button_style import ButtonStyle
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Message,
)
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from app.services.crud.stars_sell_order import (
    NotReadyForPayoutError,
    OrderNotFoundError,
    StarsSellOrderResolutionReason,
    StatusConflictError,
)
from app.services.crud.stars_sell_order import (
    ValidationError as StarsSellValidationError,
)
from app.stars import price_usd_for_cents
from app.telegram.dialogs.common import get_user
from app.telegram.dialogs.common.premium_emoji import CLOSE_EMOJI_ID
from app.telegram.keyboards.callback_data.order import CDStarsSellInvoiceCancel

from ..states import AdminSG
from .shared import (
    i18n,
    set_notice,
    set_stars_sell_count,
    set_stars_sell_wallet,
    stars_sell_admin_selected_order_id,
    stars_sell_count,
    stars_sell_order_service,
    stars_sell_wallet,
)

_TON_ADDRESS_RE: Pattern[str] = re_compile(r"^(?:UQ|EQ)[A-Za-z0-9_-]{46}$")


def _normalize_wallet(value: str) -> str | None:
    wallet = value.strip()
    if not wallet:
        return None
    if not _TON_ADDRESS_RE.fullmatch(wallet):
        return None
    return wallet


async def handle_stars_sell_stars_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    raw = (message.text or "").strip()
    if not raw.isdigit():
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_stars_sell_stars_invalid()),
        )
        await dialog_manager.switch_to(AdminSG.stars_sell_stars, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    stars_value = int(raw)
    service = stars_sell_order_service(dialog_manager)
    try:
        quote = service.build_quote(stars_count=stars_value)
    except StarsSellValidationError:
        set_notice(
            dialog_manager,
            str(
                i18n_ctx.messages.admin_stars_sell_stars_out_of_range(
                    min_stars=service.min_stars,
                    max_stars=service.max_stars,
                )
            ),
        )
        await dialog_manager.switch_to(AdminSG.stars_sell_stars, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    set_stars_sell_count(dialog_manager, quote.stars_count)
    await dialog_manager.switch_to(AdminSG.stars_sell_wallet, show_mode=ShowMode.EDIT)
    with contextlib.suppress(Exception):
        await message.delete()


async def handle_stars_sell_wallet_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    normalized_wallet = _normalize_wallet((message.text or "").strip())
    if normalized_wallet is None:
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_stars_sell_wallet_invalid()),
        )
        await dialog_manager.switch_to(AdminSG.stars_sell_wallet, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    set_stars_sell_wallet(dialog_manager, normalized_wallet)
    await dialog_manager.switch_to(AdminSG.stars_sell_payment, show_mode=ShowMode.EDIT)
    with contextlib.suppress(Exception):
        await message.delete()


async def send_stars_sell_invoice(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    service = stars_sell_order_service(dialog_manager)
    user = get_user(dialog_manager=dialog_manager)

    selected_count = stars_sell_count(dialog_manager)
    if selected_count is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_stars_sell_stars_missing()))
        await dialog_manager.switch_to(AdminSG.stars_sell_stars, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await callback.answer()
        return

    wallet = stars_sell_wallet(dialog_manager)
    if wallet is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_stars_sell_wallet_missing()))
        await dialog_manager.switch_to(AdminSG.stars_sell_wallet, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await callback.answer()
        return

    try:
        create_result = await service.create_or_refresh_pending_order(
            user_id=user.id,
            stars_count=selected_count,
            payout_wallet=wallet,
        )
        order = create_result.order
    except StarsSellValidationError as error:
        set_notice(dialog_manager, str(error))
        await dialog_manager.switch_to(AdminSG.stars_sell_payment, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await callback.answer()
        return
    except Exception:
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_stars_sell_order_create_failed()),
        )
        await dialog_manager.switch_to(AdminSG.stars_sell_payment, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await callback.answer()
        return

    bot = callback.bot
    if bot is None:
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_stars_sell_invoice_send_failed()),
        )
        await dialog_manager.switch_to(AdminSG.stars_sell_payment, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await callback.answer()
        return

    try:
        invoice_message = await bot.send_invoice(
            chat_id=user.id,
            title=str(i18n_ctx.messages.admin_stars_sell_invoice_title()),
            description=str(
                i18n_ctx.messages.admin_stars_sell_invoice_description(
                    stars_count=order.stars_count,
                    payout_amount=price_usd_for_cents(order.payout_amount_cents),
                    hold_days_text=str(
                        i18n_ctx.messages.admin_stars_sell_days(count=service.hold_days)
                    ),
                )
            ),
            payload=order.invoice_payload,
            currency="XTR",
            prices=[
                LabeledPrice(
                    label=str(
                        i18n_ctx.messages.admin_stars_sell_invoice_label(
                            stars_count=order.stars_count
                        )
                    ),
                    amount=order.invoice_total_amount,
                ),
            ],
            start_parameter=f"ttstars-sell-{order.id}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=str(i18n_ctx.buttons.admin_stars_sell_invoice_pay()),
                            pay=True,
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=str(i18n_ctx.buttons.admin_stars_sell_invoice_cancel()),
                            callback_data=CDStarsSellInvoiceCancel(order_id=order.id).pack(),
                            icon_custom_emoji_id=CLOSE_EMOJI_ID,
                            style=ButtonStyle.DANGER,
                        ),
                    ],
                ],
            ),
        )
        await service.attach_invoice_message(
            order_id=order.id,
            message_id=invoice_message.message_id,
        )
    except Exception as error:
        if not create_result.reused_existing:
            await service.mark_invoice_send_failed(order_id=order.id, reason=str(error))
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_stars_sell_invoice_send_failed()),
        )
        await dialog_manager.switch_to(AdminSG.stars_sell_payment, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await callback.answer()
        return

    set_notice(
        dialog_manager,
        str(
            (
                i18n_ctx.messages.admin_stars_sell_invoice_replaced(order_id=order.id)
                if create_result.replaced_existing
                else (
                i18n_ctx.messages.admin_stars_sell_invoice_resent(order_id=order.id)
                if create_result.reused_existing
                else i18n_ctx.messages.admin_stars_sell_invoice_sent(order_id=order.id)
                )
            )
        ),
    )
    await dialog_manager.switch_to(AdminSG.stars_sell_payment, show_mode=ShowMode.EDIT)
    with contextlib.suppress(Exception):
        await callback.answer()


async def admin_mark_stars_sell_completed(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    service = stars_sell_order_service(dialog_manager)
    order_id = stars_sell_admin_selected_order_id(dialog_manager)
    if order_id is None:
        with contextlib.suppress(Exception):
            await callback.answer()
        return

    try:
        await service.mark_completed(order_id=order_id, allow_before_hold=False)
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_stars_sell_admin_action_completed(order_id=order_id)),
        )
    except NotReadyForPayoutError as error:
        available_at = (
            "—"
            if error.payout_available_at is None
            else error.payout_available_at.strftime("%Y-%m-%d %H:%M UTC")
        )
        set_notice(
            dialog_manager,
            str(
                i18n_ctx.messages.admin_stars_sell_admin_action_not_ready(
                    order_id=order_id,
                    payout_available_at=available_at,
                )
            ),
        )
    except (OrderNotFoundError, StatusConflictError):
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_stars_sell_admin_action_conflict(order_id=order_id)),
        )
    except Exception:
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_stars_sell_admin_action_failed(order_id=order_id)),
        )

    await dialog_manager.switch_to(AdminSG.stars_sell_admin_details, show_mode=ShowMode.EDIT)
    with contextlib.suppress(Exception):
        await callback.answer()


async def admin_mark_stars_sell_rejected(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    service = stars_sell_order_service(dialog_manager)
    order_id = stars_sell_admin_selected_order_id(dialog_manager)
    if order_id is None:
        with contextlib.suppress(Exception):
            await callback.answer()
        return

    try:
        await service.mark_rejected(
            order_id=order_id,
            reason=StarsSellOrderResolutionReason.OTHER,
        )
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_stars_sell_admin_action_rejected(order_id=order_id)),
        )
    except (OrderNotFoundError, StatusConflictError):
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_stars_sell_admin_action_conflict(order_id=order_id)),
        )
    except Exception:
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_stars_sell_admin_action_failed(order_id=order_id)),
        )

    await dialog_manager.switch_to(AdminSG.stars_sell_admin_details, show_mode=ShowMode.EDIT)
    with contextlib.suppress(Exception):
        await callback.answer()


__all__ = [
    "admin_mark_stars_sell_completed",
    "admin_mark_stars_sell_rejected",
    "handle_stars_sell_stars_input",
    "handle_stars_sell_wallet_input",
    "send_stars_sell_invoice",
]
