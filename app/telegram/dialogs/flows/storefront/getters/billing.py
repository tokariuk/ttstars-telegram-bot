from __future__ import annotations

from typing import Any

from aiogram_dialog import DialogManager

from app.enums.stars_order import StarsPaymentProvider

from ..handlers import MAX_TOPUP_CENTS, MIN_TOPUP_CENTS
from ..handlers.navigation import TOPUP_FROM_PROFILE_KEY
from .common import (
    banner_url,
    consume_notice,
    current_user,
    get_i18n,
    heleket_pay_configured,
    lzt_pay_configured,
    nice_pay_configured,
    payment_button_text,
    platega_pay_configured,
    price_usd_for_cents,
    provider_meets_min_payment_amount,
    selected_topup_cents,
    ton_pay_configured,
    xrocket_pay_configured,
)


async def topup_amount_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    amount_cents = selected_topup_cents(dialog_manager)
    from_profile = bool(dialog_manager.dialog_data.get(TOPUP_FROM_PROFILE_KEY))
    text = str(
        i18n.messages.topup_amount_screen(
            min_amount=price_usd_for_cents(MIN_TOPUP_CENTS),
            max_amount=price_usd_for_cents(MAX_TOPUP_CENTS),
            amount=price_usd_for_cents(amount_cents),
        )
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "topup"),
        "back_profile_text": i18n.buttons.back_to_profile(),
        "back_button_text": i18n.buttons.back_to_menu(),
        "show_back_to_profile": from_profile,
        "show_back_to_menu": not from_profile,
    }


async def topup_payment_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = await current_user(dialog_manager=dialog_manager)

    amount_cents = selected_topup_cents(dialog_manager)
    from_profile = bool(dialog_manager.dialog_data.get(TOPUP_FROM_PROFILE_KEY))

    text = str(
        i18n.messages.topup_payment_screen(
            amount=price_usd_for_cents(amount_cents),
            balance=price_usd_for_cents(user.balance_cents),
        )
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"

    can_pay_crypto = True
    can_pay_ton = ton_pay_configured(dialog_manager)
    can_pay_platega = platega_pay_configured(dialog_manager)
    can_pay_lzt = lzt_pay_configured(dialog_manager)
    can_pay_nicepay_ru = nice_pay_configured(dialog_manager)
    can_pay_nicepay_kz = nice_pay_configured(dialog_manager)
    can_pay_heleket = heleket_pay_configured(dialog_manager)
    can_pay_xrocket = xrocket_pay_configured(dialog_manager)

    can_pay_crypto_min_ok = bool(
        can_pay_crypto
        and provider_meets_min_payment_amount(
            dialog_manager,
            provider=StarsPaymentProvider.CRYPTO_BOT,
            amount_cents=amount_cents,
        )
    )
    can_pay_platega_min_ok = bool(
        can_pay_platega
        and provider_meets_min_payment_amount(
            dialog_manager,
            provider=StarsPaymentProvider.PLATEGA_PAY,
            amount_cents=amount_cents,
        )
    )
    can_pay_ton_min_ok = bool(
        can_pay_ton
        and provider_meets_min_payment_amount(
            dialog_manager,
            provider=StarsPaymentProvider.TON_PAY,
            amount_cents=amount_cents,
        )
    )
    can_pay_lzt_min_ok = bool(
        can_pay_lzt
        and provider_meets_min_payment_amount(
            dialog_manager,
            provider=StarsPaymentProvider.LZT_PAY,
            amount_cents=amount_cents,
        )
    )
    can_pay_nicepay_ru_min_ok = bool(
        can_pay_nicepay_ru
        and provider_meets_min_payment_amount(
            dialog_manager,
            provider=StarsPaymentProvider.NICE_PAY_RU,
            amount_cents=amount_cents,
        )
    )
    can_pay_nicepay_kz_min_ok = bool(
        can_pay_nicepay_kz
        and provider_meets_min_payment_amount(
            dialog_manager,
            provider=StarsPaymentProvider.NICE_PAY_KZ,
            amount_cents=amount_cents,
        )
    )
    can_pay_heleket_min_ok = bool(
        can_pay_heleket
        and provider_meets_min_payment_amount(
            dialog_manager,
            provider=StarsPaymentProvider.HELEKET_PAY,
            amount_cents=amount_cents,
        )
    )
    can_pay_xrocket_min_ok = bool(
        can_pay_xrocket
        and provider_meets_min_payment_amount(
            dialog_manager,
            provider=StarsPaymentProvider.XROCKET_PAY,
            amount_cents=amount_cents,
        )
    )

    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "topup"),
        "pay_crypto_text": payment_button_text(
            dialog_manager,
            provider=StarsPaymentProvider.CRYPTO_BOT,
            base_text=str(i18n.buttons.pay_crypto()),
            net_amount_cents=amount_cents,
        ),
        "pay_platega_text": payment_button_text(
            dialog_manager,
            provider=StarsPaymentProvider.PLATEGA_PAY,
            base_text=str(i18n.buttons.pay_platega()),
            net_amount_cents=amount_cents,
        ),
        "pay_ton_text": payment_button_text(
            dialog_manager,
            provider=StarsPaymentProvider.TON_PAY,
            base_text=str(i18n.buttons.pay_ton()),
            net_amount_cents=amount_cents,
        ),
        "pay_lzt_text": payment_button_text(
            dialog_manager,
            provider=StarsPaymentProvider.LZT_PAY,
            base_text=str(i18n.buttons.pay_lzt()),
            net_amount_cents=amount_cents,
        ),
        "pay_nicepay_ru_text": payment_button_text(
            dialog_manager,
            provider=StarsPaymentProvider.NICE_PAY_RU,
            base_text=str(i18n.buttons.pay_nicepay_ru()),
            net_amount_cents=amount_cents,
        ),
        "pay_nicepay_kz_text": payment_button_text(
            dialog_manager,
            provider=StarsPaymentProvider.NICE_PAY_KZ,
            base_text=str(i18n.buttons.pay_nicepay_kz()),
            net_amount_cents=amount_cents,
        ),
        "pay_heleket_text": payment_button_text(
            dialog_manager,
            provider=StarsPaymentProvider.HELEKET_PAY,
            base_text=str(i18n.buttons.pay_heleket()),
            net_amount_cents=amount_cents,
        ),
        "pay_xrocket_text": payment_button_text(
            dialog_manager,
            provider=StarsPaymentProvider.XROCKET_PAY,
            base_text=str(i18n.buttons.pay_xrocket()),
            net_amount_cents=amount_cents,
        ),
        "change_amount_text": i18n.buttons.change_topup_amount(),
        "back_profile_text": i18n.buttons.back_to_profile(),
        "back_button_text": i18n.buttons.back_to_menu(),
        "can_pay_crypto": can_pay_crypto,
        "can_pay_ton": can_pay_ton,
        "can_pay_platega": can_pay_platega,
        "can_pay_lzt": can_pay_lzt,
        "can_pay_nicepay_ru": can_pay_nicepay_ru,
        "can_pay_nicepay_kz": can_pay_nicepay_kz,
        "can_pay_heleket": can_pay_heleket,
        "can_pay_xrocket": can_pay_xrocket,
        "can_pay_crypto_primary": can_pay_crypto_min_ok,
        "can_pay_ton_primary": can_pay_ton_min_ok,
        "can_pay_platega_primary": can_pay_platega_min_ok,
        "can_pay_lzt_primary": can_pay_lzt_min_ok,
        "can_pay_nicepay_ru_primary": can_pay_nicepay_ru_min_ok,
        "can_pay_nicepay_kz_primary": can_pay_nicepay_kz_min_ok,
        "can_pay_heleket_primary": can_pay_heleket_min_ok,
        "can_pay_xrocket_primary": can_pay_xrocket_min_ok,
        "can_pay_crypto_danger": bool(can_pay_crypto and not can_pay_crypto_min_ok),
        "can_pay_ton_danger": bool(can_pay_ton and not can_pay_ton_min_ok),
        "can_pay_platega_danger": bool(can_pay_platega and not can_pay_platega_min_ok),
        "can_pay_lzt_danger": bool(can_pay_lzt and not can_pay_lzt_min_ok),
        "can_pay_nicepay_ru_danger": bool(
            can_pay_nicepay_ru and not can_pay_nicepay_ru_min_ok
        ),
        "can_pay_nicepay_kz_danger": bool(
            can_pay_nicepay_kz and not can_pay_nicepay_kz_min_ok
        ),
        "can_pay_heleket_danger": bool(can_pay_heleket and not can_pay_heleket_min_ok),
        "can_pay_xrocket_danger": bool(can_pay_xrocket and not can_pay_xrocket_min_ok),
        "show_back_to_profile": from_profile,
        "show_back_to_menu": not from_profile,
    }

__all__ = ["topup_amount_getter", "topup_payment_getter"]
