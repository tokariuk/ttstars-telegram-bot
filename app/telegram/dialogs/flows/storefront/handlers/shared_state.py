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
from app.telegram.dialogs.common.state import (
    clear_state_keys,
    read_non_negative_int,
    read_optional_int,
    read_positive_int,
    read_stripped_string,
    set_optional_int,
    set_positive_int,
    set_stripped_string,
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
    return read_non_negative_int(dialog_manager.dialog_data, HISTORY_PAGE_KEY)


def set_history_page(dialog_manager: DialogManager, page: int) -> None:
    dialog_manager.dialog_data[HISTORY_PAGE_KEY] = max(page, 0)


def history_selected_order_id(dialog_manager: DialogManager) -> int | None:
    return read_optional_int(dialog_manager.dialog_data, HISTORY_SELECTED_ORDER_ID_KEY)


def set_history_selected_order_id(dialog_manager: DialogManager, order_id: int | None) -> None:
    set_optional_int(dialog_manager.dialog_data, HISTORY_SELECTED_ORDER_ID_KEY, order_id)


def referrals_page(dialog_manager: DialogManager) -> int:
    return read_non_negative_int(dialog_manager.dialog_data, REFERRALS_PAGE_KEY)


def set_referrals_page(dialog_manager: DialogManager, page: int) -> None:
    dialog_manager.dialog_data[REFERRALS_PAGE_KEY] = max(page, 0)


def referrals_selected_user_id(dialog_manager: DialogManager) -> int | None:
    return read_optional_int(dialog_manager.dialog_data, REFERRALS_SELECTED_USER_ID_KEY)


def set_referrals_selected_user_id(dialog_manager: DialogManager, user_id: int | None) -> None:
    set_optional_int(dialog_manager.dialog_data, REFERRALS_SELECTED_USER_ID_KEY, user_id)


def checks_page(dialog_manager: DialogManager) -> int:
    return read_non_negative_int(dialog_manager.dialog_data, CHECKS_PAGE_KEY)


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
    set_optional_int(dialog_manager.dialog_data, CHECKS_SELECTED_CHECK_ID_KEY, check_id)


def checks_history_page(dialog_manager: DialogManager) -> int:
    return read_non_negative_int(dialog_manager.dialog_data, CHECKS_HISTORY_PAGE_KEY)


def set_checks_history_page(dialog_manager: DialogManager, page: int) -> None:
    dialog_manager.dialog_data[CHECKS_HISTORY_PAGE_KEY] = max(page, 0)


def checks_history_selected_check_id(dialog_manager: DialogManager) -> int | None:
    return read_optional_int(
        dialog_manager.dialog_data,
        CHECKS_HISTORY_SELECTED_CHECK_ID_KEY,
    )


def set_checks_history_selected_check_id(
    dialog_manager: DialogManager,
    check_id: int | None,
) -> None:
    set_optional_int(
        dialog_manager.dialog_data,
        CHECKS_HISTORY_SELECTED_CHECK_ID_KEY,
        check_id,
    )


def checks_create_stars_count(dialog_manager: DialogManager) -> int | None:
    return read_optional_int(dialog_manager.dialog_data, CHECKS_CREATE_STARS_COUNT_KEY)


def set_checks_create_stars_count(dialog_manager: DialogManager, stars_count: int | None) -> None:
    set_optional_int(dialog_manager.dialog_data, CHECKS_CREATE_STARS_COUNT_KEY, stars_count)


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
    return read_stripped_string(dialog_manager.dialog_data, CHECKS_CREATE_CLAIM_PASSWORD_KEY)


def set_checks_create_claim_password(dialog_manager: DialogManager, password: str | None) -> None:
    if password is None:
        dialog_manager.dialog_data.pop(CHECKS_CREATE_CLAIM_PASSWORD_KEY, None)
        return
    dialog_manager.dialog_data[CHECKS_CREATE_CLAIM_PASSWORD_KEY] = password


def clear_checks_create_draft(dialog_manager: DialogManager) -> None:
    clear_state_keys(
        dialog_manager.dialog_data,
        CHECKS_CREATE_STARS_COUNT_KEY,
        CHECKS_CREATE_CLAIM_USERNAME_KEY,
        CHECKS_CREATE_CLAIM_PASSWORD_KEY,
    )


def stars_sell_count(dialog_manager: DialogManager) -> int | None:
    return read_positive_int(dialog_manager.dialog_data, STARS_SELL_COUNT_KEY)


def set_stars_sell_count(dialog_manager: DialogManager, stars_count: int | None) -> None:
    set_positive_int(dialog_manager.dialog_data, STARS_SELL_COUNT_KEY, stars_count)


def stars_sell_wallet(dialog_manager: DialogManager) -> str | None:
    return read_stripped_string(dialog_manager.dialog_data, STARS_SELL_WALLET_KEY)


def set_stars_sell_wallet(dialog_manager: DialogManager, wallet: str | None) -> None:
    set_stripped_string(dialog_manager.dialog_data, STARS_SELL_WALLET_KEY, wallet)


def stars_sell_history_page(dialog_manager: DialogManager) -> int:
    return read_non_negative_int(dialog_manager.dialog_data, STARS_SELL_HISTORY_PAGE_KEY)


def set_stars_sell_history_page(dialog_manager: DialogManager, page: int) -> None:
    dialog_manager.dialog_data[STARS_SELL_HISTORY_PAGE_KEY] = max(page, 0)


def stars_sell_history_selected_order_id(dialog_manager: DialogManager) -> int | None:
    return read_optional_int(
        dialog_manager.dialog_data,
        STARS_SELL_HISTORY_SELECTED_ORDER_ID_KEY,
    )


def set_stars_sell_history_selected_order_id(
    dialog_manager: DialogManager,
    order_id: int | None,
) -> None:
    set_optional_int(
        dialog_manager.dialog_data,
        STARS_SELL_HISTORY_SELECTED_ORDER_ID_KEY,
        order_id,
    )


def clear_stars_sell_draft(dialog_manager: DialogManager) -> None:
    clear_state_keys(
        dialog_manager.dialog_data,
        STARS_SELL_COUNT_KEY,
        STARS_SELL_WALLET_KEY,
        STARS_SELL_HISTORY_SELECTED_ORDER_ID_KEY,
    )


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
    return read_positive_int(dialog_manager.dialog_data, GIFTS_RECIPIENT_USER_ID_KEY)


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
    return read_stripped_string(dialog_manager.dialog_data, GIFTS_SELECTED_KEY)


def set_selected_gift_key(dialog_manager: DialogManager, gift_key: str | None) -> None:
    set_stripped_string(dialog_manager.dialog_data, GIFTS_SELECTED_KEY, gift_key)


def selected_gift_message(dialog_manager: DialogManager) -> str | None:
    return read_stripped_string(dialog_manager.dialog_data, GIFTS_MESSAGE_KEY)


def set_selected_gift_message(dialog_manager: DialogManager, message: str | None) -> None:
    set_stripped_string(dialog_manager.dialog_data, GIFTS_MESSAGE_KEY, message)


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
    clear_state_keys(
        dialog_manager.dialog_data,
        GIFTS_RECIPIENT_USER_ID_KEY,
        GIFTS_RECIPIENT_USERNAME_KEY,
        GIFTS_SELECTED_KEY,
        GIFTS_MESSAGE_KEY,
        GIFTS_SENDER_PRIVATE_KEY,
    )


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
