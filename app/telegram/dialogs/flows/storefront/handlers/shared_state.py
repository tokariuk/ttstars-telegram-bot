from __future__ import annotations

import contextlib
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from aiogram_dialog import DialogManager

from app.stars import (
    get_premium_pack,
    get_stars_pack,
    normalize_recipient_username,
    parse_stars_count,
    premium_months_options,
)

from .shared_constants import (
    CHECKS_CREATE_CLAIM_PASSWORD_KEY,
    CHECKS_CREATE_CLAIM_USERNAME_KEY,
    CHECKS_CREATE_STARS_COUNT_KEY,
    CHECKS_HISTORY_PAGE_KEY,
    CHECKS_HISTORY_SELECTED_CHECK_ID_KEY,
    CHECKS_PAGE_KEY,
    CHECKS_SELECTED_CHECK_ID_KEY,
    DEFAULT_TOPUP_CENTS,
    GIFTS_MESSAGE_KEY,
    GIFTS_RECIPIENT_USER_ID_KEY,
    GIFTS_RECIPIENT_USERNAME_KEY,
    GIFTS_SELECTED_KEY,
    GIFTS_SENDER_PRIVATE_KEY,
    HISTORY_PAGE_KEY,
    HISTORY_SELECTED_ORDER_ID_KEY,
    MAX_TOPUP_CENTS,
    MIN_TOPUP_CENTS,
    REFERRALS_PAGE_KEY,
    REFERRALS_SELECTED_USER_ID_KEY,
    SELECTED_PREMIUM_MONTHS_KEY,
    SELECTED_STARS_COUNT_KEY,
    STARS_SELL_COUNT_KEY,
    STARS_SELL_HISTORY_PAGE_KEY,
    STARS_SELL_HISTORY_SELECTED_ORDER_ID_KEY,
    STARS_SELL_WALLET_KEY,
    TOPUP_AMOUNT_CENTS_KEY,
)


def history_page(dialog_manager: DialogManager) -> int:
    raw = dialog_manager.dialog_data.get(HISTORY_PAGE_KEY)
    if isinstance(raw, int):
        return max(raw, 0)
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    return 0


def set_history_page(dialog_manager: DialogManager, page: int) -> None:
    dialog_manager.dialog_data[HISTORY_PAGE_KEY] = max(page, 0)


def history_selected_order_id(dialog_manager: DialogManager) -> int | None:
    raw = dialog_manager.dialog_data.get(HISTORY_SELECTED_ORDER_ID_KEY)
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    return None


def set_history_selected_order_id(dialog_manager: DialogManager, order_id: int | None) -> None:
    if order_id is None:
        dialog_manager.dialog_data.pop(HISTORY_SELECTED_ORDER_ID_KEY, None)
        return
    dialog_manager.dialog_data[HISTORY_SELECTED_ORDER_ID_KEY] = order_id


def referrals_page(dialog_manager: DialogManager) -> int:
    raw = dialog_manager.dialog_data.get(REFERRALS_PAGE_KEY)
    if isinstance(raw, int):
        return max(raw, 0)
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    return 0


def set_referrals_page(dialog_manager: DialogManager, page: int) -> None:
    dialog_manager.dialog_data[REFERRALS_PAGE_KEY] = max(page, 0)


def referrals_selected_user_id(dialog_manager: DialogManager) -> int | None:
    raw = dialog_manager.dialog_data.get(REFERRALS_SELECTED_USER_ID_KEY)
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    return None


def set_referrals_selected_user_id(dialog_manager: DialogManager, user_id: int | None) -> None:
    if user_id is None:
        dialog_manager.dialog_data.pop(REFERRALS_SELECTED_USER_ID_KEY, None)
        return
    dialog_manager.dialog_data[REFERRALS_SELECTED_USER_ID_KEY] = user_id


def checks_page(dialog_manager: DialogManager) -> int:
    raw = dialog_manager.dialog_data.get(CHECKS_PAGE_KEY)
    if isinstance(raw, int):
        return max(raw, 0)
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    return 0


def set_checks_page(dialog_manager: DialogManager, page: int) -> None:
    dialog_manager.dialog_data[CHECKS_PAGE_KEY] = max(page, 0)


def selected_check_id(dialog_manager: DialogManager) -> int | None:
    raw = dialog_manager.dialog_data.get(CHECKS_SELECTED_CHECK_ID_KEY)
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    start_data = dialog_manager.start_data
    if isinstance(start_data, dict):
        raw_from_start = start_data.get(CHECKS_SELECTED_CHECK_ID_KEY)
        if isinstance(raw_from_start, int):
            dialog_manager.dialog_data[CHECKS_SELECTED_CHECK_ID_KEY] = raw_from_start
            return raw_from_start
        if isinstance(raw_from_start, str) and raw_from_start.isdigit():
            parsed = int(raw_from_start)
            dialog_manager.dialog_data[CHECKS_SELECTED_CHECK_ID_KEY] = parsed
            return parsed
    return None


def set_selected_check_id(dialog_manager: DialogManager, check_id: int | None) -> None:
    if check_id is None:
        dialog_manager.dialog_data.pop(CHECKS_SELECTED_CHECK_ID_KEY, None)
        return
    dialog_manager.dialog_data[CHECKS_SELECTED_CHECK_ID_KEY] = check_id


def checks_history_page(dialog_manager: DialogManager) -> int:
    raw = dialog_manager.dialog_data.get(CHECKS_HISTORY_PAGE_KEY)
    if isinstance(raw, int):
        return max(raw, 0)
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    return 0


def set_checks_history_page(dialog_manager: DialogManager, page: int) -> None:
    dialog_manager.dialog_data[CHECKS_HISTORY_PAGE_KEY] = max(page, 0)


def checks_history_selected_check_id(dialog_manager: DialogManager) -> int | None:
    raw = dialog_manager.dialog_data.get(CHECKS_HISTORY_SELECTED_CHECK_ID_KEY)
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    return None


def set_checks_history_selected_check_id(
    dialog_manager: DialogManager,
    check_id: int | None,
) -> None:
    if check_id is None:
        dialog_manager.dialog_data.pop(CHECKS_HISTORY_SELECTED_CHECK_ID_KEY, None)
        return
    dialog_manager.dialog_data[CHECKS_HISTORY_SELECTED_CHECK_ID_KEY] = check_id


def checks_create_stars_count(dialog_manager: DialogManager) -> int | None:
    raw = dialog_manager.dialog_data.get(CHECKS_CREATE_STARS_COUNT_KEY)
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    return None


def set_checks_create_stars_count(dialog_manager: DialogManager, stars_count: int | None) -> None:
    if stars_count is None:
        dialog_manager.dialog_data.pop(CHECKS_CREATE_STARS_COUNT_KEY, None)
        return
    dialog_manager.dialog_data[CHECKS_CREATE_STARS_COUNT_KEY] = stars_count


def checks_create_claim_username(dialog_manager: DialogManager) -> str | None:
    raw = dialog_manager.dialog_data.get(CHECKS_CREATE_CLAIM_USERNAME_KEY)
    if not isinstance(raw, str):
        return None
    normalized = raw.strip().lstrip("@")
    return normalized or None


def set_checks_create_claim_username(dialog_manager: DialogManager, username: str | None) -> None:
    if username is None:
        dialog_manager.dialog_data.pop(CHECKS_CREATE_CLAIM_USERNAME_KEY, None)
        return
    dialog_manager.dialog_data[CHECKS_CREATE_CLAIM_USERNAME_KEY] = username


def checks_create_claim_password(dialog_manager: DialogManager) -> str | None:
    raw = dialog_manager.dialog_data.get(CHECKS_CREATE_CLAIM_PASSWORD_KEY)
    if not isinstance(raw, str):
        return None
    normalized = raw.strip()
    return normalized or None


def set_checks_create_claim_password(dialog_manager: DialogManager, password: str | None) -> None:
    if password is None:
        dialog_manager.dialog_data.pop(CHECKS_CREATE_CLAIM_PASSWORD_KEY, None)
        return
    dialog_manager.dialog_data[CHECKS_CREATE_CLAIM_PASSWORD_KEY] = password


def clear_checks_create_draft(dialog_manager: DialogManager) -> None:
    dialog_manager.dialog_data.pop(CHECKS_CREATE_STARS_COUNT_KEY, None)
    dialog_manager.dialog_data.pop(CHECKS_CREATE_CLAIM_USERNAME_KEY, None)
    dialog_manager.dialog_data.pop(CHECKS_CREATE_CLAIM_PASSWORD_KEY, None)


def stars_sell_count(dialog_manager: DialogManager) -> int | None:
    raw = dialog_manager.dialog_data.get(STARS_SELL_COUNT_KEY)
    if isinstance(raw, int) and raw > 0:
        return raw
    if isinstance(raw, str) and raw.isdigit():
        value = int(raw)
        return value if value > 0 else None
    return None


def set_stars_sell_count(dialog_manager: DialogManager, stars_count: int | None) -> None:
    if stars_count is None:
        dialog_manager.dialog_data.pop(STARS_SELL_COUNT_KEY, None)
        return
    value = int(stars_count)
    if value <= 0:
        dialog_manager.dialog_data.pop(STARS_SELL_COUNT_KEY, None)
        return
    dialog_manager.dialog_data[STARS_SELL_COUNT_KEY] = value


def stars_sell_wallet(dialog_manager: DialogManager) -> str | None:
    raw = dialog_manager.dialog_data.get(STARS_SELL_WALLET_KEY)
    if not isinstance(raw, str):
        return None
    value = raw.strip()
    return value or None


def set_stars_sell_wallet(dialog_manager: DialogManager, wallet: str | None) -> None:
    if wallet is None:
        dialog_manager.dialog_data.pop(STARS_SELL_WALLET_KEY, None)
        return
    value = wallet.strip()
    if not value:
        dialog_manager.dialog_data.pop(STARS_SELL_WALLET_KEY, None)
        return
    dialog_manager.dialog_data[STARS_SELL_WALLET_KEY] = value


def stars_sell_history_page(dialog_manager: DialogManager) -> int:
    raw = dialog_manager.dialog_data.get(STARS_SELL_HISTORY_PAGE_KEY)
    if isinstance(raw, int):
        return max(raw, 0)
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    return 0


def set_stars_sell_history_page(dialog_manager: DialogManager, page: int) -> None:
    dialog_manager.dialog_data[STARS_SELL_HISTORY_PAGE_KEY] = max(page, 0)


def stars_sell_history_selected_order_id(dialog_manager: DialogManager) -> int | None:
    raw = dialog_manager.dialog_data.get(STARS_SELL_HISTORY_SELECTED_ORDER_ID_KEY)
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    return None


def set_stars_sell_history_selected_order_id(
    dialog_manager: DialogManager,
    order_id: int | None,
) -> None:
    if order_id is None:
        dialog_manager.dialog_data.pop(STARS_SELL_HISTORY_SELECTED_ORDER_ID_KEY, None)
        return
    dialog_manager.dialog_data[STARS_SELL_HISTORY_SELECTED_ORDER_ID_KEY] = order_id


def clear_stars_sell_draft(dialog_manager: DialogManager) -> None:
    dialog_manager.dialog_data.pop(STARS_SELL_COUNT_KEY, None)
    dialog_manager.dialog_data.pop(STARS_SELL_WALLET_KEY, None)
    dialog_manager.dialog_data.pop(STARS_SELL_HISTORY_SELECTED_ORDER_ID_KEY, None)


def selected_stars_count(dialog_manager: DialogManager) -> int:
    raw_value = dialog_manager.dialog_data.get(SELECTED_STARS_COUNT_KEY)
    if isinstance(raw_value, str):
        parsed = parse_stars_count(raw_value)
        if parsed is not None:
            return parsed
    return get_stars_pack(None).stars_count


def selected_premium_months(dialog_manager: DialogManager) -> int:
    raw_value = dialog_manager.dialog_data.get(SELECTED_PREMIUM_MONTHS_KEY)
    if isinstance(raw_value, int):
        with contextlib.suppress(ValueError):
            return get_premium_pack(months=raw_value).months
    if isinstance(raw_value, str) and raw_value.isdigit():
        with contextlib.suppress(ValueError):
            return get_premium_pack(months=int(raw_value)).months
    return premium_months_options()[0]


def selected_topup_amount_cents(dialog_manager: DialogManager) -> int:
    raw_value = dialog_manager.dialog_data.get(TOPUP_AMOUNT_CENTS_KEY)
    if isinstance(raw_value, int):
        if MIN_TOPUP_CENTS <= raw_value <= MAX_TOPUP_CENTS:
            return raw_value
    if isinstance(raw_value, str) and raw_value.isdigit():
        parsed = int(raw_value)
        if MIN_TOPUP_CENTS <= parsed <= MAX_TOPUP_CENTS:
            return parsed
    return DEFAULT_TOPUP_CENTS


def selected_gift_recipient_user_id(dialog_manager: DialogManager) -> int | None:
    raw_value = dialog_manager.dialog_data.get(GIFTS_RECIPIENT_USER_ID_KEY)
    if isinstance(raw_value, int):
        return raw_value if raw_value > 0 else None
    if isinstance(raw_value, str) and raw_value.isdigit():
        parsed = int(raw_value)
        return parsed if parsed > 0 else None
    return None


def set_selected_gift_recipient_user_id(
    dialog_manager: DialogManager,
    recipient_user_id: int | None,
) -> None:
    if recipient_user_id is None or recipient_user_id <= 0:
        dialog_manager.dialog_data.pop(GIFTS_RECIPIENT_USER_ID_KEY, None)
        return
    dialog_manager.dialog_data[GIFTS_RECIPIENT_USER_ID_KEY] = recipient_user_id


def selected_gift_recipient_username(dialog_manager: DialogManager) -> str | None:
    raw_value = dialog_manager.dialog_data.get(GIFTS_RECIPIENT_USERNAME_KEY)
    if not isinstance(raw_value, str):
        return None
    return normalize_recipient_username(raw_value)


def set_selected_gift_recipient_username(
    dialog_manager: DialogManager,
    recipient_username: str | None,
) -> None:
    if recipient_username is None:
        dialog_manager.dialog_data.pop(GIFTS_RECIPIENT_USERNAME_KEY, None)
        return
    normalized = normalize_recipient_username(recipient_username)
    if normalized is None:
        dialog_manager.dialog_data.pop(GIFTS_RECIPIENT_USERNAME_KEY, None)
        return
    dialog_manager.dialog_data[GIFTS_RECIPIENT_USERNAME_KEY] = normalized


def selected_gift_key(dialog_manager: DialogManager) -> str | None:
    raw_value = dialog_manager.dialog_data.get(GIFTS_SELECTED_KEY)
    if not isinstance(raw_value, str):
        return None
    normalized = raw_value.strip()
    return normalized or None


def set_selected_gift_key(dialog_manager: DialogManager, gift_key: str | None) -> None:
    if gift_key is None:
        dialog_manager.dialog_data.pop(GIFTS_SELECTED_KEY, None)
        return
    normalized = gift_key.strip()
    if not normalized:
        dialog_manager.dialog_data.pop(GIFTS_SELECTED_KEY, None)
        return
    dialog_manager.dialog_data[GIFTS_SELECTED_KEY] = normalized


def selected_gift_message(dialog_manager: DialogManager) -> str | None:
    raw_value = dialog_manager.dialog_data.get(GIFTS_MESSAGE_KEY)
    if not isinstance(raw_value, str):
        return None
    normalized = raw_value.strip()
    return normalized or None


def set_selected_gift_message(dialog_manager: DialogManager, message: str | None) -> None:
    if message is None:
        dialog_manager.dialog_data.pop(GIFTS_MESSAGE_KEY, None)
        return
    normalized = message.strip()
    if not normalized:
        dialog_manager.dialog_data.pop(GIFTS_MESSAGE_KEY, None)
        return
    dialog_manager.dialog_data[GIFTS_MESSAGE_KEY] = normalized


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


def set_selected_gift_sender_private(
    dialog_manager: DialogManager,
    sender_private: bool | None,
) -> None:
    if sender_private is None:
        dialog_manager.dialog_data.pop(GIFTS_SENDER_PRIVATE_KEY, None)
        return
    dialog_manager.dialog_data[GIFTS_SENDER_PRIVATE_KEY] = bool(sender_private)


def clear_gift_draft(dialog_manager: DialogManager) -> None:
    dialog_manager.dialog_data.pop(GIFTS_RECIPIENT_USER_ID_KEY, None)
    dialog_manager.dialog_data.pop(GIFTS_RECIPIENT_USERNAME_KEY, None)
    dialog_manager.dialog_data.pop(GIFTS_SELECTED_KEY, None)
    dialog_manager.dialog_data.pop(GIFTS_MESSAGE_KEY, None)
    dialog_manager.dialog_data.pop(GIFTS_SENDER_PRIVATE_KEY, None)


def parse_topup_amount_cents(value: str) -> int | None:
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
    if cents < MIN_TOPUP_CENTS or cents > MAX_TOPUP_CENTS:
        return None
    return cents
