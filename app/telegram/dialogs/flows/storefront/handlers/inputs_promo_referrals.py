from __future__ import annotations

import contextlib
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput

from app.services.crud.user import UserService
from app.stars import price_usd_for_cents
from app.telegram.dialogs.common import get_i18n, get_user

from ..states import StorefrontSG
from .shared import set_notice, user_service


async def _delete_user_message(message: Message) -> None:
    with contextlib.suppress(TelegramBadRequest):
        await message.delete()


def _parse_usd_amount_to_cents(value: str) -> int | None:
    raw = value.strip().replace(" ", "").replace(",", ".")
    if not raw:
        return None
    try:
        amount = Decimal(raw)
    except InvalidOperation:
        return None
    if amount <= 0:
        return None
    cents = int((amount * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return cents if cents > 0 else None


async def handle_promo_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    service = user_service(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    code = (message.text or "").strip()
    if not code:
        set_notice(dialog_manager, str(i18n.messages.promo_invalid()))
        await dialog_manager.switch_to(StorefrontSG.promo, show_mode=ShowMode.EDIT)
        await _delete_user_message(message)
        return

    try:
        credited_cents = await service.activate_promo_code(user_id=user.id, code=code)
    except UserService.PromoCodeInvalidError:
        set_notice(dialog_manager, str(i18n.messages.promo_invalid()))
    except UserService.PromoCodeAlreadyUsedError:
        set_notice(dialog_manager, str(i18n.messages.promo_already_used()))
    except UserService.PromoCodeError:
        set_notice(dialog_manager, str(i18n.messages.promo_apply_failed()))
    else:
        set_notice(
            dialog_manager,
            str(i18n.messages.promo_applied(amount=price_usd_for_cents(credited_cents))),
        )
    await dialog_manager.switch_to(StorefrontSG.promo, show_mode=ShowMode.EDIT)
    await _delete_user_message(message)


async def handle_referral_withdraw_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    service = user_service(dialog_manager=dialog_manager)
    refreshed_user = await service.get(user_id=user.id)
    max_amount_cents = int(refreshed_user.referral_balance_cents) if refreshed_user else 0
    if max_amount_cents <= 0:
        set_notice(dialog_manager, str(i18n.messages.referral_withdraw_empty()))
        await dialog_manager.switch_to(StorefrontSG.referrals, show_mode=ShowMode.EDIT)
        await _delete_user_message(message)
        return

    amount_cents = _parse_usd_amount_to_cents(message.text or "")
    if amount_cents is None or amount_cents > max_amount_cents:
        set_notice(
            dialog_manager,
            str(
                i18n.messages.referral_withdraw_invalid_amount(
                    min_amount=price_usd_for_cents(1),
                    max_amount=price_usd_for_cents(max_amount_cents),
                )
            ),
        )
        await dialog_manager.switch_to(StorefrontSG.referrals_withdraw, show_mode=ShowMode.EDIT)
        await _delete_user_message(message)
        return

    withdrawn_cents = await service.withdraw_referral_balance_to_main(
        user_id=user.id,
        amount_cents=amount_cents,
    )
    if withdrawn_cents <= 0:
        set_notice(dialog_manager, str(i18n.messages.referral_withdraw_empty()))
    else:
        set_notice(
            dialog_manager,
            str(i18n.messages.referral_withdraw_done(amount=price_usd_for_cents(withdrawn_cents))),
        )
    await dialog_manager.switch_to(StorefrontSG.referrals, show_mode=ShowMode.EDIT)
    await _delete_user_message(message)

