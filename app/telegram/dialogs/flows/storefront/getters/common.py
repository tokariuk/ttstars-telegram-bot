from __future__ import annotations

import html
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Final, Literal
from urllib.parse import quote_plus

from aiogram_dialog import DialogManager

from app.enums.stars_order import StarsOrderProductType, StarsOrderStatus, StarsPaymentProvider
from app.gifts import get_gift_pack_by_id
from app.models.config import AppConfig
from app.models.dto.stars_order import StarsOrderDto
from app.models.dto.user import UserDto
from app.services.crud import StarsOrderService
from app.services.crud.user import UserService
from app.stars import (
    DEFAULT_STARS_COUNT,
    get_stars_pack,
    normalize_recipient_username,
    premium_months_options,
    price_usd_for_cents,
)
from app.telegram.dialogs.common import get_i18n, get_user

from ..handlers import (
    DEFAULT_TOPUP_CENTS,
    GIFTS_MESSAGE_KEY,
    GIFTS_RECIPIENT_USER_ID_KEY,
    GIFTS_RECIPIENT_USERNAME_KEY,
    GIFTS_SELECTED_KEY,
    GIFTS_SENDER_PRIVATE_KEY,
    PREMIUM_RECIPIENT_USERNAME_KEY,
    SELECTED_PREMIUM_MONTHS_KEY,
    SELECTED_STARS_COUNT_KEY,
    STARS_RECIPIENT_USERNAME_KEY,
    STATE_NOTICE_KEY,
    TOPUP_AMOUNT_CENTS_KEY,
)

FAQ_SUPPORT_URL: Final[str] = "https://t.me/TTStars_support"
FAQ_NEWS_URL: Final[str] = "https://t.me/ttstars_news"
FAQ_PRIVACY_PATH: Final[str] = "/miniapp/legal/privacy"
FAQ_TERMS_PATH: Final[str] = "/miniapp/legal/terms"


def banner_link(*, text: str, bg: str, fg: str, font: str) -> str:
    return (
        f"https://placehold.co/2048x700/{bg}/{fg}.png"
        f"?font={quote_plus(font)}&text={quote_plus(text)}"
    )


BANNER_KEY = Literal[
    "menu",
    "stars",
    "premium",
    "stars_sell",
    "gifts",
    "topup",
    "calculator",
    "profile",
    "checks",
    "history",
    "referrals",
    "promo",
    "faq",
]


BANNER_FILENAMES: Final[dict[BANNER_KEY, str]] = {
    "menu": "menu.jpg",
    "stars": "stars.jpg",
    "premium": "premium.jpg",
    "stars_sell": "stars-sell.jpg",
    "gifts": "gifts.jpg",
    "topup": "topup.jpg",
    "calculator": "calculator.jpg",
    "profile": "profile.jpg",
    "checks": "checks.jpg",
    "history": "history.jpg",
    "referrals": "referrals.jpg",
    "promo": "promo.jpg",
    "faq": "faq.jpg",
}


BANNER_FALLBACKS: Final[dict[BANNER_KEY, str]] = {
    "checks": "history.jpg",
    "gifts": "premium.jpg",
}


PLACEHOLDER_BANNERS: Final[dict[BANNER_KEY, str]] = {
    "menu": banner_link(text="TTStars", bg="101826", fg="f8fafc", font="poppins"),
    "stars": banner_link(text="Stars", bg="16213e", fg="f8fafc", font="poppins"),
    "premium": banner_link(text="Premium", bg="1f2937", fg="f9fafb", font="poppins"),
    "stars_sell": banner_link(text="Sell Stars", bg="1f2937", fg="f9fafb", font="poppins"),
    "gifts": banner_link(text="Telegram Gifts", bg="3b1c32", fg="fff1f2", font="poppins"),
    "topup": banner_link(text="Top Up Balance", bg="0f766e", fg="f0fdfa", font="poppins"),
    "calculator": banner_link(text="Stars Calculator", bg="312e81", fg="eef2ff", font="poppins"),
    "profile": banner_link(text="Your Profile", bg="3f1d2e", fg="fff1f2", font="poppins"),
    "checks": banner_link(text="Gift Checks", bg="0d3b2a", fg="eafff3", font="poppins"),
    "history": banner_link(text="Orders History", bg="1f2937", fg="f9fafb", font="poppins"),
    "referrals": banner_link(text="Referral Program", bg="2b2a4c", fg="f8f7ff", font="poppins"),
    "promo": banner_link(text="Promo Codes", bg="4a044e", fg="fdf4ff", font="poppins"),
    "faq": banner_link(text="FAQ", bg="0b3b4d", fg="ecfeff", font="poppins"),
}
_GIFT_NAME_MESSAGE_BY_KEY: Final[dict[str, str]] = {
    "new_year_tree": "gift_name_new_year_tree",
    "valentine_heart": "gift_name_valentine_heart",
    "new_year_bear": "gift_name_new_year_bear",
    "bear_with_heart": "gift_name_bear_with_heart",
    "bear_with_bouquet": "gift_name_bear_with_bouquet",
    "irish_bear": "gift_name_irish_bear",
    "clown_bear": "gift_name_clown_bear",
    "easter_bear": "gift_name_easter_bear",
    "worker_bear": "gift_name_worker_bear",
    "default_bear": "gift_name_default_bear",
}


@lru_cache(maxsize=1)
def _assets_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "assets" / "banners"
        if candidate.is_dir():
            return parent / "assets"
    return current.parents[6] / "assets"


def _normalize_banner_locale(raw_locale: str | None) -> str:
    if not raw_locale:
        return "ru"
    value = raw_locale.strip().lower().replace("_", "-")
    language = value.split("-", 1)[0]
    return language if language in {"uk", "en", "ru"} else "ru"


@lru_cache(maxsize=256)
def _resolve_banner_relative_path(*, key: BANNER_KEY, locale: str) -> str | None:
    assets_root = _assets_root()
    filename = BANNER_FILENAMES[key]
    fallback_filename = BANNER_FALLBACKS.get(key)

    for locale_code in (locale, "ru"):
        path = assets_root / "banners" / locale_code / filename
        if path.is_file():
            return f"/assets/banners/{locale_code}/{filename}"
        if fallback_filename is not None:
            fallback_path = assets_root / "banners" / locale_code / fallback_filename
            if fallback_path.is_file():
                return f"/assets/banners/{locale_code}/{fallback_filename}"
    return None


def banner_url(dialog_manager: DialogManager, key: BANNER_KEY) -> str:
    user = get_user(dialog_manager=dialog_manager)
    locale = _normalize_banner_locale(user.language)
    relative_path = _resolve_banner_relative_path(key=key, locale=locale)
    if relative_path is None:
        return PLACEHOLDER_BANNERS[key]

    base_url = server_base_url(dialog_manager=dialog_manager)
    if not base_url:
        return PLACEHOLDER_BANNERS[key]
    return f"{base_url}{relative_path}"


def server_base_url(dialog_manager: DialogManager) -> str:
    raw_config = dialog_manager.middleware_data.get("config")
    if isinstance(raw_config, AppConfig):
        return raw_config.server.url.strip().rstrip("/")
    return os.getenv("SERVER_URL", "").strip().rstrip("/")


async def current_user(dialog_manager: DialogManager) -> UserDto:
    user = get_user(dialog_manager=dialog_manager)
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    updated = await user_service.get(user_id=user.id)
    return updated if updated is not None else user


_NOTICE_BADGE_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*<blockquote>.*?</blockquote>\s*",
    re.DOTALL,
)
_NOTICE_FULL_BLOCKQUOTE_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*<blockquote>(?P<inner>.*)</blockquote>\s*$",
    re.DOTALL,
)
_NOTICE_HTML_TAG_RE: Final[re.Pattern[str]] = re.compile(r"</?[^>]+>")


def _normalize_notice_for_screen(text: str) -> str:
    """Prevent duplicate badges in a single message.

    Most storefront windows already start with a section badge. Many notice
    messages also include a status badge. When appended together this creates
    two badges in one message, so we strip only the leading notice badge.
    """

    if not text:
        return ""
    normalized = text.strip()
    full_blockquote = _NOTICE_FULL_BLOCKQUOTE_RE.match(normalized)
    if full_blockquote is not None:
        content = full_blockquote.group("inner").strip()
    else:
        without_badge = _NOTICE_BADGE_RE.sub("", normalized, count=1).strip()
        content = without_badge or normalized

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        return ""

    compact = "\n".join(lines).strip()
    # Keep Telegram HTML tags (including <tg-emoji>) but ensure visible text exists.
    if not _NOTICE_HTML_TAG_RE.sub("", compact).strip():
        return ""
    return f"<blockquote>{compact}</blockquote>"


def consume_notice(dialog_manager: DialogManager) -> str:
    notice_raw = dialog_manager.dialog_data.pop(STATE_NOTICE_KEY, None)
    if isinstance(notice_raw, str):
        return _normalize_notice_for_screen(notice_raw)

    start_data_raw = dialog_manager.start_data
    if isinstance(start_data_raw, dict):
        start_notice = start_data_raw.pop(STATE_NOTICE_KEY, None)
        if isinstance(start_notice, str):
            return _normalize_notice_for_screen(start_notice)
    return ""


def selected_stars_count(dialog_manager: DialogManager) -> int:
    raw_value = dialog_manager.dialog_data.get(SELECTED_STARS_COUNT_KEY)
    if isinstance(raw_value, str):
        pack = get_stars_pack(raw_value)
        return pack.stars_count
    return get_stars_pack(str(DEFAULT_STARS_COUNT)).stars_count


def selected_premium_months(dialog_manager: DialogManager) -> int:
    raw_value = dialog_manager.dialog_data.get(SELECTED_PREMIUM_MONTHS_KEY)
    if isinstance(raw_value, int):
        return raw_value
    if isinstance(raw_value, str) and raw_value.isdigit():
        return int(raw_value)
    return premium_months_options()[0]


def selected_topup_cents(dialog_manager: DialogManager) -> int:
    raw_value = dialog_manager.dialog_data.get(TOPUP_AMOUNT_CENTS_KEY)
    if isinstance(raw_value, int):
        return raw_value
    if isinstance(raw_value, str) and raw_value.isdigit():
        return int(raw_value)
    return DEFAULT_TOPUP_CENTS


def selected_gift_recipient_user_id(dialog_manager: DialogManager) -> int | None:
    raw_value = dialog_manager.dialog_data.get(GIFTS_RECIPIENT_USER_ID_KEY)
    if isinstance(raw_value, int):
        return raw_value if raw_value > 0 else None
    if isinstance(raw_value, str) and raw_value.isdigit():
        parsed = int(raw_value)
        return parsed if parsed > 0 else None
    return None


def selected_gift_recipient_username(dialog_manager: DialogManager) -> str | None:
    raw_value = dialog_manager.dialog_data.get(GIFTS_RECIPIENT_USERNAME_KEY)
    if not isinstance(raw_value, str):
        return None
    return normalize_recipient_username(raw_value)


def selected_gift_key(dialog_manager: DialogManager) -> str | None:
    raw_value = dialog_manager.dialog_data.get(GIFTS_SELECTED_KEY)
    if not isinstance(raw_value, str):
        return None
    normalized = raw_value.strip()
    return normalized or None


def selected_gift_message(dialog_manager: DialogManager) -> str | None:
    raw_value = dialog_manager.dialog_data.get(GIFTS_MESSAGE_KEY)
    if not isinstance(raw_value, str):
        return None
    normalized = raw_value.strip()
    return normalized or None


def selected_gift_sender_private(dialog_manager: DialogManager) -> bool | None:
    raw_value = dialog_manager.dialog_data.get(GIFTS_SENDER_PRIVATE_KEY)
    if isinstance(raw_value, bool):
        return raw_value
    if isinstance(raw_value, str):
        lowered = raw_value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    return None


def secret_code_view(value: str | None, *, placeholder: str = "—") -> str:
    """Render a technical identifier (TX hash, provider ref) for a message.

    Real values are wrapped in a monospace spoiler so they stay tappable to copy
    but do not clutter the screen. Missing values fall back to a plain
    placeholder (never wrapped in a spoiler, so users do not tap blurred dashes).
    """

    if value is None:
        return placeholder
    normalized = value.strip()
    if not normalized or normalized == placeholder:
        return placeholder
    escaped = html.escape(normalized)
    return f"<code><tg-spoiler>{escaped}</tg-spoiler></code>"


def provider_label(i18n: Any, provider: StarsPaymentProvider) -> str:
    provider_getters: dict[StarsPaymentProvider, Callable[[], Any]] = {
        StarsPaymentProvider.CRYPTO_BOT: i18n.messages.provider_crypto,
        StarsPaymentProvider.TON_PAY: i18n.messages.provider_ton,
        StarsPaymentProvider.LZT_PAY: i18n.messages.provider_lzt,
        StarsPaymentProvider.HELEKET_PAY: i18n.messages.provider_heleket,
        StarsPaymentProvider.NICE_PAY_RU: i18n.messages.provider_nicepay_ru,
        StarsPaymentProvider.NICE_PAY_KZ: i18n.messages.provider_nicepay_kz,
        StarsPaymentProvider.PLATEGA_PAY: i18n.messages.provider_platega,
        StarsPaymentProvider.XROCKET_PAY: i18n.messages.provider_xrocket,
        StarsPaymentProvider.BALANCE: i18n.messages.provider_balance,
    }
    getter = provider_getters.get(provider)
    return str(getter()) if getter is not None else provider.value


def lzt_pay_configured(dialog_manager: DialogManager) -> bool:
    service_raw = dialog_manager.middleware_data.get("stars_order_service")
    if not isinstance(service_raw, StarsOrderService):
        return False
    return service_raw.lzt_pay_service.configured


def platega_pay_configured(dialog_manager: DialogManager) -> bool:
    service_raw = dialog_manager.middleware_data.get("stars_order_service")
    if not isinstance(service_raw, StarsOrderService):
        return False
    return service_raw.platega_pay_service.configured


def ton_pay_configured(dialog_manager: DialogManager) -> bool:
    service_raw = dialog_manager.middleware_data.get("stars_order_service")
    if not isinstance(service_raw, StarsOrderService):
        return False
    return service_raw.ton_pay_service.configured


def nice_pay_configured(dialog_manager: DialogManager) -> bool:
    service_raw = dialog_manager.middleware_data.get("stars_order_service")
    if not isinstance(service_raw, StarsOrderService):
        return False
    return service_raw.nice_pay_service.configured


def heleket_pay_configured(dialog_manager: DialogManager) -> bool:
    service_raw = dialog_manager.middleware_data.get("stars_order_service")
    if not isinstance(service_raw, StarsOrderService):
        return False
    return service_raw.heleket_pay_service.configured


def xrocket_pay_configured(dialog_manager: DialogManager) -> bool:
    service_raw = dialog_manager.middleware_data.get("stars_order_service")
    if not isinstance(service_raw, StarsOrderService):
        return False
    return service_raw.xrocket_pay_service.configured


def provider_fee_percent_text(
    dialog_manager: DialogManager,
    *,
    provider: StarsPaymentProvider,
    net_amount_cents: int | None = None,
    compact: bool = False,
) -> str:
    service_raw = dialog_manager.middleware_data.get("stars_order_service")
    if not isinstance(service_raw, StarsOrderService):
        return "0%"
    if net_amount_cents is not None and net_amount_cents > 0:
        return service_raw.provider_checkout_fee_display_text(
            provider=provider,
            net_amount_cents=net_amount_cents,
            compact=compact,
        )
    return f"{service_raw.provider_payment_fee_percent_text(provider=provider)}%"


def provider_meets_min_payment_amount(
    dialog_manager: DialogManager,
    *,
    provider: StarsPaymentProvider,
    amount_cents: int,
) -> bool:
    service_raw = dialog_manager.middleware_data.get("stars_order_service")
    if not isinstance(service_raw, StarsOrderService):
        return True
    return service_raw.provider_supports_payment_amount(
        provider=provider,
        amount_cents=amount_cents,
    )


def payment_button_text(
    dialog_manager: DialogManager,
    *,
    provider: StarsPaymentProvider,
    base_text: str,
    net_amount_cents: int | None = None,
) -> str:
    fee = provider_fee_percent_text(
        dialog_manager,
        provider=provider,
        net_amount_cents=net_amount_cents,
    )
    return f"{base_text} ({fee})"


def status_label(i18n: Any, status: StarsOrderStatus) -> str:
    if status == StarsOrderStatus.CREATING_PAYMENT:
        return str(i18n.messages.order_status_creating())
    if status == StarsOrderStatus.PENDING_PAYMENT:
        return str(i18n.messages.order_status_pending())
    if status == StarsOrderStatus.PAYMENT_CONFIRMED:
        return str(i18n.messages.order_status_paid())
    if status == StarsOrderStatus.FULFILLING:
        return str(i18n.messages.order_status_fulfilling())
    if status == StarsOrderStatus.COMPLETED:
        return str(i18n.messages.order_status_completed())
    if status == StarsOrderStatus.CANCELED:
        return str(i18n.messages.order_status_canceled())
    return str(i18n.messages.order_status_failed())


def _localized_gift_name(i18n: Any, *, gift_id: str) -> str:
    gift = get_gift_pack_by_id(gift_id=gift_id)
    if gift is None:
        return gift_id
    message_key = _GIFT_NAME_MESSAGE_BY_KEY.get(gift.key)
    if message_key is None:
        return gift.label
    message_getter = getattr(i18n.messages, message_key, None)
    if message_getter is None:
        return gift.label
    return str(message_getter())


def product_label(i18n: Any, order: StarsOrderDto) -> str:
    if order.product_type == StarsOrderProductType.TOPUP:
        return str(i18n.messages.order_product_topup())
    if order.product_type == StarsOrderProductType.GIFT:
        gift_name = (
            _localized_gift_name(i18n=i18n, gift_id=order.gift_id)
            if order.gift_id
            else "Gift"
        )
        return str(i18n.messages.order_product_gift(gift=gift_name))
    if order.product_type == StarsOrderProductType.PREMIUM:
        return str(i18n.messages.order_product_premium(months=order.premium_months or 0))
    return str(i18n.messages.order_product_stars(stars=order.stars_count))


__all__ = [
    "banner_url",
    "FAQ_NEWS_URL",
    "FAQ_PRIVACY_PATH",
    "FAQ_SUPPORT_URL",
    "FAQ_TERMS_PATH",
    "PREMIUM_RECIPIENT_USERNAME_KEY",
    "STARS_RECIPIENT_USERNAME_KEY",
    "consume_notice",
    "current_user",
    "get_i18n",
    "get_user",
    "heleket_pay_configured",
    "lzt_pay_configured",
    "nice_pay_configured",
    "payment_button_text",
    "provider_fee_percent_text",
    "provider_meets_min_payment_amount",
    "platega_pay_configured",
    "ton_pay_configured",
    "xrocket_pay_configured",
    "price_usd_for_cents",
    "selected_premium_months",
    "selected_stars_count",
    "selected_topup_cents",
    "selected_gift_recipient_user_id",
    "selected_gift_recipient_username",
    "selected_gift_key",
    "selected_gift_message",
    "selected_gift_sender_private",
    "secret_code_view",
    "server_base_url",
    "status_label",
]
