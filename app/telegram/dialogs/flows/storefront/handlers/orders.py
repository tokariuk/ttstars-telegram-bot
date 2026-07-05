from __future__ import annotations

from collections.abc import Awaitable, Callable

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from app.enums.stars_order import StarsPaymentProvider
from app.models.dto.stars_order import StarsOrderDto
from app.services.crud.stars_order import StarsOrderService
from app.stars import normalize_recipient_username
from app.telegram.dialogs.common import get_i18n, get_user

from ..states import StorefrontSG
from .shared import (
    PREMIUM_RECIPIENT_USERNAME_KEY,
    STARS_RECIPIENT_USERNAME_KEY,
    create_order_with_result,
    selected_gift_key,
    selected_gift_message,
    selected_gift_recipient_user_id,
    selected_gift_recipient_username,
    selected_gift_sender_private,
    selected_premium_months,
    selected_stars_count,
    selected_topup_amount_cents,
    set_notice,
    stars_order_service,
)


def _recipient_from_dialog(dialog_manager: DialogManager, key: str) -> str:
    value = dialog_manager.dialog_data.get(key)
    return value if isinstance(value, str) else ""


async def _pay_stars_order(
    *,
    callback: CallbackQuery,
    dialog_manager: DialogManager,
    create_order: Callable[[StarsOrderService, int, str, int], Awaitable[StarsOrderDto]],
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    recipient = _recipient_from_dialog(dialog_manager, STARS_RECIPIENT_USERNAME_KEY)
    if normalize_recipient_username(recipient) is None:
        set_notice(dialog_manager, str(i18n.messages.recipient_missing()))
        await dialog_manager.switch_to(StorefrontSG.stars_recipient, show_mode=ShowMode.EDIT)
        return

    stars_count = selected_stars_count(dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    service = stars_order_service(dialog_manager=dialog_manager)
    await create_order_with_result(
        callback=callback,
        dialog_manager=dialog_manager,
        target_state=StorefrontSG.stars_payment,
        create_order=lambda: create_order(service, user.id, recipient, stars_count),
    )


async def _pay_premium_order(
    *,
    callback: CallbackQuery,
    dialog_manager: DialogManager,
    create_order: Callable[[StarsOrderService, int, str, int], Awaitable[StarsOrderDto]],
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    recipient = _recipient_from_dialog(dialog_manager, PREMIUM_RECIPIENT_USERNAME_KEY)
    if normalize_recipient_username(recipient) is None:
        set_notice(dialog_manager, str(i18n.messages.recipient_missing()))
        await dialog_manager.switch_to(StorefrontSG.premium_recipient, show_mode=ShowMode.EDIT)
        return

    months = selected_premium_months(dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    service = stars_order_service(dialog_manager=dialog_manager)
    await create_order_with_result(
        callback=callback,
        dialog_manager=dialog_manager,
        target_state=StorefrontSG.premium_payment,
        create_order=lambda: create_order(service, user.id, recipient, months),
    )


async def _pay_topup_order(
    *,
    callback: CallbackQuery,
    dialog_manager: DialogManager,
    create_order: Callable[[StarsOrderService, int, int], Awaitable[StarsOrderDto]],
) -> None:
    amount_cents = selected_topup_amount_cents(dialog_manager=dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    service = stars_order_service(dialog_manager=dialog_manager)
    await create_order_with_result(
        callback=callback,
        dialog_manager=dialog_manager,
        target_state=StorefrontSG.topup_payment,
        create_order=lambda: create_order(service, user.id, amount_cents),
    )


async def _pay_gift_order(
    *,
    callback: CallbackQuery,
    dialog_manager: DialogManager,
    create_order: Callable[
        [StarsOrderService, int, str, int | None, str, str | None, bool],
        Awaitable[StarsOrderDto],
    ],
) -> None:
    i18n = get_i18n(dialog_manager=dialog_manager)
    recipient_username = selected_gift_recipient_username(dialog_manager)
    if normalize_recipient_username(recipient_username or "") is None:
        set_notice(dialog_manager, str(i18n.messages.gift_recipient_missing()))
        await dialog_manager.switch_to(StorefrontSG.gifts_recipient, show_mode=ShowMode.EDIT)
        return
    if recipient_username is None:
        set_notice(dialog_manager, str(i18n.messages.gift_recipient_missing()))
        await dialog_manager.switch_to(StorefrontSG.gifts_recipient, show_mode=ShowMode.EDIT)
        return

    recipient_user_id = selected_gift_recipient_user_id(dialog_manager)

    gift_key = selected_gift_key(dialog_manager)
    if gift_key is None:
        set_notice(dialog_manager, str(i18n.messages.gift_invalid()))
        await dialog_manager.switch_to(StorefrontSG.gifts_catalog, show_mode=ShowMode.EDIT)
        return

    sender_private = selected_gift_sender_private(dialog_manager)
    if sender_private is None:
        set_notice(dialog_manager, str(i18n.messages.gift_sender_visibility_required()))
        await dialog_manager.switch_to(StorefrontSG.gifts_sender_privacy, show_mode=ShowMode.EDIT)
        return

    gift_message = selected_gift_message(dialog_manager)
    user = get_user(dialog_manager=dialog_manager)
    service = stars_order_service(dialog_manager=dialog_manager)
    await create_order_with_result(
        callback=callback,
        dialog_manager=dialog_manager,
        target_state=StorefrontSG.gifts_payment,
        create_order=(
            lambda: create_order(
                service,
                user.id,
                recipient_username,
                recipient_user_id,
                gift_key,
                gift_message,
                sender_private,
            )
        ),
    )


async def _pay_stars_with_provider(
    *,
    callback: CallbackQuery,
    dialog_manager: DialogManager,
    provider: StarsPaymentProvider,
) -> None:
    await _pay_stars_order(
        callback=callback,
        dialog_manager=dialog_manager,
        create_order=(
            lambda service, user_id, recipient, stars_count: service.create_stars_order(
                provider=provider,
                user_id=user_id,
                recipient_username=recipient,
                stars_count=stars_count,
            )
        ),
    )


async def _pay_premium_with_provider(
    *,
    callback: CallbackQuery,
    dialog_manager: DialogManager,
    provider: StarsPaymentProvider,
) -> None:
    await _pay_premium_order(
        callback=callback,
        dialog_manager=dialog_manager,
        create_order=(
            lambda service, user_id, recipient, months: service.create_premium_order(
                provider=provider,
                user_id=user_id,
                recipient_username=recipient,
                months=months,
            )
        ),
    )


async def _pay_topup_with_provider(
    *,
    callback: CallbackQuery,
    dialog_manager: DialogManager,
    provider: StarsPaymentProvider,
) -> None:
    await _pay_topup_order(
        callback=callback,
        dialog_manager=dialog_manager,
        create_order=(
            lambda service, user_id, amount_cents: service.create_topup_order(
                provider=provider,
                user_id=user_id,
                amount_cents=amount_cents,
            )
        ),
    )


async def _pay_gift_with_provider(
    *,
    callback: CallbackQuery,
    dialog_manager: DialogManager,
    provider: StarsPaymentProvider,
) -> None:
    await _pay_gift_order(
        callback=callback,
        dialog_manager=dialog_manager,
        create_order=(
            lambda service,
            user_id,
            recipient_username,
            recipient_user_id,
            gift_key,
            gift_message,
            sender_private: service.create_gift_order(
                provider=provider,
                user_id=user_id,
                recipient_username=recipient_username,
                recipient_user_id=recipient_user_id,
                gift_key=gift_key,
                gift_message=gift_message,
                gift_sender_private=sender_private,
            )
        ),
    )


def _bind_provider_handler(
    *,
    handler: Callable[
        ...,
        Awaitable[None],
    ],
    provider: StarsPaymentProvider,
) -> Callable[[CallbackQuery, Button, DialogManager], Awaitable[None]]:
    async def _wrapped(
        callback: CallbackQuery,
        _: Button,
        dialog_manager: DialogManager,
    ) -> None:
        await handler(
            callback=callback,
            dialog_manager=dialog_manager,
            provider=provider,
        )

    return _wrapped


pay_stars_with_balance = _bind_provider_handler(
    handler=_pay_stars_with_provider,
    provider=StarsPaymentProvider.BALANCE,
)
pay_stars_with_crypto = _bind_provider_handler(
    handler=_pay_stars_with_provider,
    provider=StarsPaymentProvider.CRYPTO_BOT,
)
pay_stars_with_ton = _bind_provider_handler(
    handler=_pay_stars_with_provider,
    provider=StarsPaymentProvider.TON_PAY,
)
pay_stars_with_lzt = _bind_provider_handler(
    handler=_pay_stars_with_provider,
    provider=StarsPaymentProvider.LZT_PAY,
)
pay_stars_with_nicepay_ru = _bind_provider_handler(
    handler=_pay_stars_with_provider,
    provider=StarsPaymentProvider.NICE_PAY_RU,
)
pay_stars_with_nicepay_kz = _bind_provider_handler(
    handler=_pay_stars_with_provider,
    provider=StarsPaymentProvider.NICE_PAY_KZ,
)
pay_stars_with_platega = _bind_provider_handler(
    handler=_pay_stars_with_provider,
    provider=StarsPaymentProvider.PLATEGA_PAY,
)
pay_stars_with_xrocket = _bind_provider_handler(
    handler=_pay_stars_with_provider,
    provider=StarsPaymentProvider.XROCKET_PAY,
)
pay_stars_with_heleket = _bind_provider_handler(
    handler=_pay_stars_with_provider,
    provider=StarsPaymentProvider.HELEKET_PAY,
)

pay_premium_with_balance = _bind_provider_handler(
    handler=_pay_premium_with_provider,
    provider=StarsPaymentProvider.BALANCE,
)
pay_premium_with_crypto = _bind_provider_handler(
    handler=_pay_premium_with_provider,
    provider=StarsPaymentProvider.CRYPTO_BOT,
)
pay_premium_with_ton = _bind_provider_handler(
    handler=_pay_premium_with_provider,
    provider=StarsPaymentProvider.TON_PAY,
)
pay_premium_with_lzt = _bind_provider_handler(
    handler=_pay_premium_with_provider,
    provider=StarsPaymentProvider.LZT_PAY,
)
pay_premium_with_nicepay_ru = _bind_provider_handler(
    handler=_pay_premium_with_provider,
    provider=StarsPaymentProvider.NICE_PAY_RU,
)
pay_premium_with_nicepay_kz = _bind_provider_handler(
    handler=_pay_premium_with_provider,
    provider=StarsPaymentProvider.NICE_PAY_KZ,
)
pay_premium_with_platega = _bind_provider_handler(
    handler=_pay_premium_with_provider,
    provider=StarsPaymentProvider.PLATEGA_PAY,
)
pay_premium_with_xrocket = _bind_provider_handler(
    handler=_pay_premium_with_provider,
    provider=StarsPaymentProvider.XROCKET_PAY,
)
pay_premium_with_heleket = _bind_provider_handler(
    handler=_pay_premium_with_provider,
    provider=StarsPaymentProvider.HELEKET_PAY,
)

pay_topup_with_crypto = _bind_provider_handler(
    handler=_pay_topup_with_provider,
    provider=StarsPaymentProvider.CRYPTO_BOT,
)
pay_topup_with_ton = _bind_provider_handler(
    handler=_pay_topup_with_provider,
    provider=StarsPaymentProvider.TON_PAY,
)
pay_topup_with_lzt = _bind_provider_handler(
    handler=_pay_topup_with_provider,
    provider=StarsPaymentProvider.LZT_PAY,
)
pay_topup_with_nicepay_ru = _bind_provider_handler(
    handler=_pay_topup_with_provider,
    provider=StarsPaymentProvider.NICE_PAY_RU,
)
pay_topup_with_nicepay_kz = _bind_provider_handler(
    handler=_pay_topup_with_provider,
    provider=StarsPaymentProvider.NICE_PAY_KZ,
)
pay_topup_with_platega = _bind_provider_handler(
    handler=_pay_topup_with_provider,
    provider=StarsPaymentProvider.PLATEGA_PAY,
)
pay_topup_with_xrocket = _bind_provider_handler(
    handler=_pay_topup_with_provider,
    provider=StarsPaymentProvider.XROCKET_PAY,
)
pay_topup_with_heleket = _bind_provider_handler(
    handler=_pay_topup_with_provider,
    provider=StarsPaymentProvider.HELEKET_PAY,
)

pay_gift_with_balance = _bind_provider_handler(
    handler=_pay_gift_with_provider,
    provider=StarsPaymentProvider.BALANCE,
)
pay_gift_with_crypto = _bind_provider_handler(
    handler=_pay_gift_with_provider,
    provider=StarsPaymentProvider.CRYPTO_BOT,
)
pay_gift_with_ton = _bind_provider_handler(
    handler=_pay_gift_with_provider,
    provider=StarsPaymentProvider.TON_PAY,
)
pay_gift_with_lzt = _bind_provider_handler(
    handler=_pay_gift_with_provider,
    provider=StarsPaymentProvider.LZT_PAY,
)
pay_gift_with_nicepay_ru = _bind_provider_handler(
    handler=_pay_gift_with_provider,
    provider=StarsPaymentProvider.NICE_PAY_RU,
)
pay_gift_with_nicepay_kz = _bind_provider_handler(
    handler=_pay_gift_with_provider,
    provider=StarsPaymentProvider.NICE_PAY_KZ,
)
pay_gift_with_platega = _bind_provider_handler(
    handler=_pay_gift_with_provider,
    provider=StarsPaymentProvider.PLATEGA_PAY,
)
pay_gift_with_xrocket = _bind_provider_handler(
    handler=_pay_gift_with_provider,
    provider=StarsPaymentProvider.XROCKET_PAY,
)
pay_gift_with_heleket = _bind_provider_handler(
    handler=_pay_gift_with_provider,
    provider=StarsPaymentProvider.HELEKET_PAY,
)


__all__ = [
    "pay_gift_with_balance",
    "pay_gift_with_crypto",
    "pay_gift_with_ton",
    "pay_gift_with_heleket",
    "pay_gift_with_lzt",
    "pay_gift_with_nicepay_ru",
    "pay_gift_with_nicepay_kz",
    "pay_gift_with_platega",
    "pay_gift_with_xrocket",
    "pay_premium_with_balance",
    "pay_premium_with_crypto",
    "pay_premium_with_ton",
    "pay_premium_with_heleket",
    "pay_premium_with_lzt",
    "pay_premium_with_nicepay_ru",
    "pay_premium_with_nicepay_kz",
    "pay_premium_with_platega",
    "pay_premium_with_xrocket",
    "pay_stars_with_balance",
    "pay_stars_with_crypto",
    "pay_stars_with_ton",
    "pay_stars_with_heleket",
    "pay_stars_with_lzt",
    "pay_stars_with_nicepay_ru",
    "pay_stars_with_nicepay_kz",
    "pay_stars_with_platega",
    "pay_stars_with_xrocket",
    "pay_topup_with_crypto",
    "pay_topup_with_ton",
    "pay_topup_with_heleket",
    "pay_topup_with_lzt",
    "pay_topup_with_nicepay_ru",
    "pay_topup_with_nicepay_kz",
    "pay_topup_with_platega",
    "pay_topup_with_xrocket",
]
