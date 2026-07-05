from __future__ import annotations

from typing import Any

from aiogram_dialog import DialogManager

from app.enums.stars_order import StarsPaymentProvider
from app.stars import (
    MAX_STARS_COUNT,
    MIN_STARS_COUNT,
    affordable_stars_for_balance_cents,
    get_stars_pack,
)

from .common import (
    STARS_RECIPIENT_USERNAME_KEY,
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
    selected_stars_count,
    ton_pay_configured,
    xrocket_pay_configured,
)


async def stars_amount_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = await current_user(dialog_manager=dialog_manager)
    text = str(
        i18n.messages.stars_amount_screen(
            min_stars=MIN_STARS_COUNT,
            max_stars=MAX_STARS_COUNT,
            balance=price_usd_for_cents(user.balance_cents),
            balance_for_stars_usd=price_usd_for_cents(user.balance_cents),
            balance_for_stars=affordable_stars_for_balance_cents(user.balance_cents),
        )
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "stars"),
        "change_recipient_text": i18n.buttons.change_recipient(),
        "back_button_text": i18n.buttons.back_to_menu(),
    }


async def stars_recipient_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    text = str(i18n.messages.stars_recipient_screen())
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "stars"),
        "buy_for_self_text": i18n.buttons.buy_for_self(),
        "back_amount_text": i18n.buttons.back_to_stars_amount(),
        "back_button_text": i18n.buttons.back_to_menu(),
    }


async def stars_payment_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = await current_user(dialog_manager=dialog_manager)

    stars_count = selected_stars_count(dialog_manager)
    pack = get_stars_pack(str(stars_count))
    recipient_raw = dialog_manager.dialog_data.get(STARS_RECIPIENT_USERNAME_KEY)
    recipient = recipient_raw if isinstance(recipient_raw, str) else ""

    text = str(
        i18n.messages.stars_payment_screen(
            stars=pack.stars_count,
            amount=pack.price_usd,
            recipient=(f"@{recipient}" if recipient else "—"),
            balance=price_usd_for_cents(user.balance_cents),
        )
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"

    can_pay_base = bool(recipient)
    can_pay_crypto = can_pay_base
    can_pay_ton = bool(can_pay_base and ton_pay_configured(dialog_manager))
    can_pay_platega = bool(can_pay_base and platega_pay_configured(dialog_manager))
    can_pay_lzt = bool(can_pay_base and lzt_pay_configured(dialog_manager))
    can_pay_nicepay_ru = bool(can_pay_base and nice_pay_configured(dialog_manager))
    can_pay_nicepay_kz = bool(can_pay_base and nice_pay_configured(dialog_manager))
    can_pay_heleket = bool(can_pay_base and heleket_pay_configured(dialog_manager))
    can_pay_xrocket = bool(can_pay_base and xrocket_pay_configured(dialog_manager))

    can_pay_crypto_min_ok = bool(
        can_pay_crypto
        and provider_meets_min_payment_amount(
            dialog_manager,
            provider=StarsPaymentProvider.CRYPTO_BOT,
            amount_cents=pack.price_cents,
        )
    )
    can_pay_platega_min_ok = bool(
        can_pay_platega
        and provider_meets_min_payment_amount(
            dialog_manager,
            provider=StarsPaymentProvider.PLATEGA_PAY,
            amount_cents=pack.price_cents,
        )
    )
    can_pay_ton_min_ok = bool(
        can_pay_ton
        and provider_meets_min_payment_amount(
            dialog_manager,
            provider=StarsPaymentProvider.TON_PAY,
            amount_cents=pack.price_cents,
        )
    )
    can_pay_lzt_min_ok = bool(
        can_pay_lzt
        and provider_meets_min_payment_amount(
            dialog_manager,
            provider=StarsPaymentProvider.LZT_PAY,
            amount_cents=pack.price_cents,
        )
    )
    can_pay_nicepay_ru_min_ok = bool(
        can_pay_nicepay_ru
        and provider_meets_min_payment_amount(
            dialog_manager,
            provider=StarsPaymentProvider.NICE_PAY_RU,
            amount_cents=pack.price_cents,
        )
    )
    can_pay_nicepay_kz_min_ok = bool(
        can_pay_nicepay_kz
        and provider_meets_min_payment_amount(
            dialog_manager,
            provider=StarsPaymentProvider.NICE_PAY_KZ,
            amount_cents=pack.price_cents,
        )
    )
    can_pay_heleket_min_ok = bool(
        can_pay_heleket
        and provider_meets_min_payment_amount(
            dialog_manager,
            provider=StarsPaymentProvider.HELEKET_PAY,
            amount_cents=pack.price_cents,
        )
    )
    can_pay_xrocket_min_ok = bool(
        can_pay_xrocket
        and provider_meets_min_payment_amount(
            dialog_manager,
            provider=StarsPaymentProvider.XROCKET_PAY,
            amount_cents=pack.price_cents,
        )
    )

    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "stars"),
        "pay_balance_text": i18n.buttons.pay_balance(),
        "pay_crypto_text": payment_button_text(
            dialog_manager,
            provider=StarsPaymentProvider.CRYPTO_BOT,
            base_text=str(i18n.buttons.pay_crypto()),
            net_amount_cents=pack.price_cents,
        ),
        "pay_platega_text": payment_button_text(
            dialog_manager,
            provider=StarsPaymentProvider.PLATEGA_PAY,
            base_text=str(i18n.buttons.pay_platega()),
            net_amount_cents=pack.price_cents,
        ),
        "pay_ton_text": payment_button_text(
            dialog_manager,
            provider=StarsPaymentProvider.TON_PAY,
            base_text=str(i18n.buttons.pay_ton()),
            net_amount_cents=pack.price_cents,
        ),
        "pay_lzt_text": payment_button_text(
            dialog_manager,
            provider=StarsPaymentProvider.LZT_PAY,
            base_text=str(i18n.buttons.pay_lzt()),
            net_amount_cents=pack.price_cents,
        ),
        "pay_nicepay_ru_text": payment_button_text(
            dialog_manager,
            provider=StarsPaymentProvider.NICE_PAY_RU,
            base_text=str(i18n.buttons.pay_nicepay_ru()),
            net_amount_cents=pack.price_cents,
        ),
        "pay_nicepay_kz_text": payment_button_text(
            dialog_manager,
            provider=StarsPaymentProvider.NICE_PAY_KZ,
            base_text=str(i18n.buttons.pay_nicepay_kz()),
            net_amount_cents=pack.price_cents,
        ),
        "pay_heleket_text": payment_button_text(
            dialog_manager,
            provider=StarsPaymentProvider.HELEKET_PAY,
            base_text=str(i18n.buttons.pay_heleket()),
            net_amount_cents=pack.price_cents,
        ),
        "pay_xrocket_text": payment_button_text(
            dialog_manager,
            provider=StarsPaymentProvider.XROCKET_PAY,
            base_text=str(i18n.buttons.pay_xrocket()),
            net_amount_cents=pack.price_cents,
        ),
        "change_recipient_text": i18n.buttons.change_recipient(),
        "back_amount_text": i18n.buttons.back_to_stars_amount(),
        "back_button_text": i18n.buttons.back_to_menu(),
        "can_pay_balance": bool(recipient) and user.balance_cents >= pack.price_cents,
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
    }


__all__ = ["stars_amount_getter", "stars_payment_getter", "stars_recipient_getter"]
