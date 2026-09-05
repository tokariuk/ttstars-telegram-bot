from __future__ import annotations

from typing import Any

from aiogram_dialog import DialogManager

from app.enums.stars_order import StarsPaymentProvider
from app.gifts import TelegramGiftPack, get_gift_pack, list_gift_packs

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
    selected_gift_key,
    selected_gift_message,
    selected_gift_recipient_user_id,
    selected_gift_recipient_username,
    selected_gift_sender_private,
    ton_pay_configured,
    xrocket_pay_configured,
)

_GIFT_PACKS: dict[str, TelegramGiftPack] = {gift.key: gift for gift in list_gift_packs()}
_GIFT_NAME_MESSAGE_BY_KEY: dict[str, str] = {
    "new_year_tree": "gift_name_new_year_tree",
    "valentine_heart": "gift_name_valentine_heart",
    "new_year_bear": "gift_name_new_year_bear",
    "bear_with_heart": "gift_name_bear_with_heart",
    "bear_with_bouquet": "gift_name_bear_with_bouquet",
    "irish_bear": "gift_name_irish_bear",
    "clown_bear": "gift_name_clown_bear",
    "easter_bear": "gift_name_easter_bear",
    "worker_bear": "gift_name_worker_bear",
    "military_bear": "gift_name_military_bear",
    "football_bear": "gift_name_football_bear",
    "default_bear": "gift_name_default_bear",
}


def _gift_pack_by_key(gift_key: str | None) -> TelegramGiftPack | None:
    if gift_key is None:
        return None
    try:
        return get_gift_pack(key=gift_key)
    except ValueError:
        return None


def _gift_label(i18n: Any, *, gift_key: str) -> str:
    message_key = _GIFT_NAME_MESSAGE_BY_KEY.get(gift_key)
    if message_key is None:
        return gift_key
    message_getter = getattr(i18n.messages, message_key, None)
    if message_getter is None:
        return gift_key
    return str(message_getter())


def _gift_button_text(i18n: Any, *, gift_key: str) -> str:
    pack = _GIFT_PACKS[gift_key]
    return str(
        i18n.buttons.gift_option(
            label=_gift_label(i18n=i18n, gift_key=gift_key),
            amount=pack.price_usd,
        )
    )


def _gift_sender_visibility_text(i18n: Any, *, sender_private: bool | None) -> str:
    if sender_private is True:
        return str(i18n.messages.gift_sender_private_option())
    if sender_private is False:
        return str(i18n.messages.gift_sender_visible_option())
    return "—"


def _gift_recipient_text(
    *,
    recipient_user_id: int | None,
    recipient_username: str | None,
) -> str:
    if recipient_username:
        return f"@{recipient_username}"
    if recipient_user_id is not None:
        return str(recipient_user_id)
    return "—"


async def gifts_recipient_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    recipient_user_id = selected_gift_recipient_user_id(dialog_manager)
    recipient_username = selected_gift_recipient_username(dialog_manager)
    recipient = _gift_recipient_text(
        recipient_user_id=recipient_user_id,
        recipient_username=recipient_username,
    )
    text = str(
        i18n.messages.gifts_recipient_screen(
            recipient_id=recipient,
            recipient=recipient,
        )
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"
    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "gifts"),
        "buy_for_self_text": i18n.buttons.buy_for_self(),
        "back_button_text": i18n.buttons.back_to_menu(),
    }


async def gifts_catalog_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    recipient_user_id = selected_gift_recipient_user_id(dialog_manager)
    recipient_username = selected_gift_recipient_username(dialog_manager)
    recipient = _gift_recipient_text(
        recipient_user_id=recipient_user_id,
        recipient_username=recipient_username,
    )
    selected_key = selected_gift_key(dialog_manager)
    selected_pack = _gift_pack_by_key(selected_key)

    text = str(
        i18n.messages.gifts_catalog_screen(
            recipient_id=recipient,
            recipient=recipient,
            selected=(
                _gift_label(i18n=i18n, gift_key=selected_pack.key)
                if selected_pack is not None
                else "—"
            ),
        )
    )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"

    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "gifts"),
        "gift_new_year_tree_text": _gift_button_text(i18n=i18n, gift_key="new_year_tree"),
        "gift_valentine_heart_text": _gift_button_text(i18n=i18n, gift_key="valentine_heart"),
        "gift_new_year_bear_text": _gift_button_text(i18n=i18n, gift_key="new_year_bear"),
        "gift_bear_with_heart_text": _gift_button_text(i18n=i18n, gift_key="bear_with_heart"),
        "gift_bear_with_bouquet_text": _gift_button_text(
            i18n=i18n,
            gift_key="bear_with_bouquet",
        ),
        "gift_irish_bear_text": _gift_button_text(i18n=i18n, gift_key="irish_bear"),
        "gift_clown_bear_text": _gift_button_text(i18n=i18n, gift_key="clown_bear"),
        "gift_easter_bear_text": _gift_button_text(i18n=i18n, gift_key="easter_bear"),
        "gift_worker_bear_text": _gift_button_text(i18n=i18n, gift_key="worker_bear"),
        "gift_military_bear_text": _gift_button_text(i18n=i18n, gift_key="military_bear"),
        "gift_football_bear_text": _gift_button_text(i18n=i18n, gift_key="football_bear"),
        "gift_default_bear_text": _gift_button_text(i18n=i18n, gift_key="default_bear"),
        "back_recipient_text": i18n.buttons.gift_back_to_recipient(),
        "back_button_text": i18n.buttons.back_to_menu(),
    }


async def gifts_message_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    recipient_user_id = selected_gift_recipient_user_id(dialog_manager)
    recipient_username = selected_gift_recipient_username(dialog_manager)
    recipient = _gift_recipient_text(
        recipient_user_id=recipient_user_id,
        recipient_username=recipient_username,
    )
    selected_pack = _gift_pack_by_key(selected_gift_key(dialog_manager))
    current_message = selected_gift_message(dialog_manager)

    if selected_pack is None:
        text = str(i18n.messages.gift_invalid())
    else:
        text = str(
            i18n.messages.gifts_message_screen(
                recipient_id=recipient,
                recipient=recipient,
                gift=_gift_label(i18n=i18n, gift_key=selected_pack.key),
                amount=selected_pack.price_usd,
                current_message=current_message or "—",
            )
        )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"

    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "gifts"),
        "skip_message_text": i18n.buttons.gift_skip_message(),
        "back_recipient_text": i18n.buttons.gift_back_to_recipient(),
        "back_catalog_text": i18n.buttons.gift_back_to_catalog(),
        "back_button_text": i18n.buttons.back_to_menu(),
    }


async def gifts_sender_privacy_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    recipient_user_id = selected_gift_recipient_user_id(dialog_manager)
    recipient_username = selected_gift_recipient_username(dialog_manager)
    recipient = _gift_recipient_text(
        recipient_user_id=recipient_user_id,
        recipient_username=recipient_username,
    )
    selected_pack = _gift_pack_by_key(selected_gift_key(dialog_manager))
    current_message = selected_gift_message(dialog_manager)

    if selected_pack is None:
        text = str(i18n.messages.gift_invalid())
    else:
        text = str(
            i18n.messages.gifts_sender_privacy_screen(
                recipient_id=recipient,
                recipient=recipient,
                gift=_gift_label(i18n=i18n, gift_key=selected_pack.key),
                amount=selected_pack.price_usd,
                message=current_message or "—",
            )
        )
    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"

    return {
        "text": text,
        "banner_url": banner_url(dialog_manager, "gifts"),
        "sender_visible_text": i18n.buttons.gift_sender_visible(),
        "sender_private_text": i18n.buttons.gift_sender_private(),
        "back_recipient_text": i18n.buttons.gift_back_to_recipient(),
        "back_catalog_text": i18n.buttons.gift_back_to_catalog(),
        "back_message_text": i18n.buttons.gift_back_to_message(),
        "back_button_text": i18n.buttons.back_to_menu(),
    }


async def gifts_payment_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n = get_i18n(dialog_manager=dialog_manager)
    user = await current_user(dialog_manager=dialog_manager)

    recipient_user_id = selected_gift_recipient_user_id(dialog_manager)
    recipient_username = selected_gift_recipient_username(dialog_manager)
    recipient = _gift_recipient_text(
        recipient_user_id=recipient_user_id,
        recipient_username=recipient_username,
    )
    selected_pack = _gift_pack_by_key(selected_gift_key(dialog_manager))
    gift_message = selected_gift_message(dialog_manager)
    sender_private = selected_gift_sender_private(dialog_manager)

    if selected_pack is None:
        text = str(i18n.messages.gift_invalid())
        amount_cents = 0
    else:
        text = str(
            i18n.messages.gifts_payment_screen(
                recipient_id=recipient,
                recipient=recipient,
                gift=_gift_label(i18n=i18n, gift_key=selected_pack.key),
                amount=selected_pack.price_usd,
                message=gift_message or "—",
                sender_visibility=_gift_sender_visibility_text(
                    i18n=i18n,
                    sender_private=sender_private,
                ),
                balance=price_usd_for_cents(user.balance_cents),
            )
        )
        amount_cents = selected_pack.price_cents

    notice = consume_notice(dialog_manager)
    if notice:
        text = f"{text}\n\n{notice}"

    can_pay = selected_pack is not None and bool(recipient_username) and sender_private is not None
    can_pay_crypto = can_pay
    can_pay_ton = bool(can_pay and ton_pay_configured(dialog_manager))
    can_pay_platega = bool(can_pay and platega_pay_configured(dialog_manager))
    can_pay_lzt = bool(can_pay and lzt_pay_configured(dialog_manager))
    can_pay_nicepay_ru = bool(can_pay and nice_pay_configured(dialog_manager))
    can_pay_nicepay_kz = bool(can_pay and nice_pay_configured(dialog_manager))
    can_pay_heleket = bool(can_pay and heleket_pay_configured(dialog_manager))
    can_pay_xrocket = bool(can_pay and xrocket_pay_configured(dialog_manager))

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
        "banner_url": banner_url(dialog_manager, "gifts"),
        "pay_balance_text": i18n.buttons.pay_balance(),
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
        "back_recipient_text": i18n.buttons.gift_back_to_recipient(),
        "back_catalog_text": i18n.buttons.gift_back_to_catalog(),
        "back_message_text": i18n.buttons.gift_back_to_message(),
        "back_sender_visibility_text": i18n.buttons.gift_back_to_sender_visibility(),
        "back_button_text": i18n.buttons.back_to_menu(),
        "can_pay_balance": bool(can_pay and user.balance_cents >= amount_cents),
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


__all__ = [
    "gifts_catalog_getter",
    "gifts_message_getter",
    "gifts_payment_getter",
    "gifts_recipient_getter",
    "gifts_sender_privacy_getter",
]
