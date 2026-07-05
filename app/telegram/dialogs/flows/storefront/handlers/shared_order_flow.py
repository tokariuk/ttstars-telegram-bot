from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

from aiogram.fsm.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode

from app.enums.stars_order import StarsPaymentProvider
from app.models.dto.stars_order import StarsOrderDto
from app.services.crud.stars_order import (
    BalanceOrderInProgressError,
    InsufficientBalanceError,
    PaymentMinAmountError,
    ProviderUnavailableError,
    StarsOrderError,
    ValidationError,
)
from app.telegram.dialogs.common import get_i18n

from .shared_checkout import send_checkout_message
from .shared_constants import MAX_GIFT_MESSAGE_LENGTH
from .shared_services import set_notice

logger = logging.getLogger(__name__)


def _log_order_create_warning(
    *,
    callback: CallbackQuery,
    message: str,
    error: Exception,
) -> None:
    logger.warning(
        message,
        callback.from_user.id if callback.from_user else None,
        error,
    )


def _set_validation_notice(
    *,
    dialog_manager: DialogManager,
    i18n: Any,
    error: ValidationError,
) -> None:
    error_text = str(error).strip().lower()
    if isinstance(error, PaymentMinAmountError):
        set_notice(
            dialog_manager,
            str(
                i18n.messages.order_payment_min_amount(
                    amount=error.min_amount_text,
                    currency=error.currency,
                )
            ),
        )
        return
    if "gift recipient" in error_text:
        set_notice(dialog_manager, str(i18n.messages.gift_recipient_invalid()))
        return
    if "userbot configuration is incomplete" in error_text:
        set_notice(dialog_manager, str(i18n.messages.gift_userbot_session_required()))
        return
    if "cannot be verified without userbot session" in error_text:
        set_notice(dialog_manager, str(i18n.messages.gift_userbot_session_required()))
        return
    if "gift sender visibility" in error_text:
        set_notice(dialog_manager, str(i18n.messages.gift_sender_visibility_required()))
        return
    if "gift message is too long" in error_text:
        set_notice(
            dialog_manager,
            str(i18n.messages.gift_message_too_long(max_chars=MAX_GIFT_MESSAGE_LENGTH)),
        )
        return
    if "gift id" in error_text or "unsupported gift" in error_text:
        set_notice(dialog_manager, str(i18n.messages.gift_invalid()))
        return
    set_notice(dialog_manager, str(i18n.messages.order_validation_error()))


def _set_order_create_failure_notice(
    *,
    callback: CallbackQuery,
    dialog_manager: DialogManager,
    i18n: Any,
    error: Exception,
) -> None:
    if isinstance(error, ProviderUnavailableError):
        _log_order_create_warning(
            callback=callback,
            message="Order create failed: provider unavailable user_id=%s reason=%s",
            error=error,
        )
        set_notice(dialog_manager, str(i18n.messages.payment_provider_unavailable()))
        return
    if isinstance(error, BalanceOrderInProgressError):
        _log_order_create_warning(
            callback=callback,
            message="Order create failed: balance in progress user_id=%s reason=%s",
            error=error,
        )
        set_notice(dialog_manager, str(i18n.messages.order_balance_in_progress()))
        return
    if isinstance(error, InsufficientBalanceError):
        _log_order_create_warning(
            callback=callback,
            message="Order create failed: insufficient balance user_id=%s reason=%s",
            error=error,
        )
        set_notice(dialog_manager, str(i18n.messages.balance_not_enough()))
        return
    if isinstance(error, ValidationError):
        _log_order_create_warning(
            callback=callback,
            message="Order create failed: validation user_id=%s reason=%s",
            error=error,
        )
        _set_validation_notice(dialog_manager=dialog_manager, i18n=i18n, error=error)
        return
    if isinstance(error, StarsOrderError):
        logger.exception(
            "Order create failed: user_id=%s reason=%s",
            callback.from_user.id if callback.from_user else None,
            error,
        )
        set_notice(dialog_manager, str(i18n.messages.order_create_failed()))
        return
    raise error


async def _set_order_create_success_notice_and_checkout(
    *,
    callback: CallbackQuery,
    dialog_manager: DialogManager,
    i18n: Any,
    order: StarsOrderDto,
) -> None:
    if order.payment_provider == StarsPaymentProvider.BALANCE:
        set_notice(dialog_manager, str(i18n.messages.order_paid_from_balance()))
    else:
        set_notice(dialog_manager, str(i18n.messages.order_created()))
    if order.checkout_url:
        try:
            await send_checkout_message(
                callback=callback,
                dialog_manager=dialog_manager,
                order=order,
            )
        except Exception:
            logger.exception(
                "Checkout message send failed: user_id=%s order_id=%s",
                callback.from_user.id if callback.from_user else None,
                order.id,
            )
            set_notice(dialog_manager, str(i18n.messages.order_checkout_send_failed()))


async def create_order_with_result(
    *,
    callback: CallbackQuery,
    dialog_manager: DialogManager,
    target_state: State,
    create_order: Callable[[], Awaitable[StarsOrderDto]],
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    try:
        order = await create_order()
    except (
        ProviderUnavailableError,
        BalanceOrderInProgressError,
        InsufficientBalanceError,
        ValidationError,
        StarsOrderError,
    ) as error:
        _set_order_create_failure_notice(
            callback=callback,
            dialog_manager=dialog_manager,
            i18n=i18n,
            error=error,
        )
    else:
        await _set_order_create_success_notice_and_checkout(
            callback=callback,
            dialog_manager=dialog_manager,
            i18n=i18n,
            order=order,
        )
    await dialog_manager.switch_to(target_state, show_mode=ShowMode.EDIT)

