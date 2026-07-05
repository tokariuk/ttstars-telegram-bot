from __future__ import annotations

from typing import cast

from aiogram_dialog import DialogManager
from aiogram_i18n import I18nContext

from app.services.crud.stars_order import StarsOrderService
from app.services.crud.stars_sell_order import StarsSellOrderService
from app.services.crud.user import UserService
from app.services.promo_codes import PromoCodeService

from ..helpers import BroadcastPayload, payload_from_state, payload_to_state

STATE_NOTICE_KEY = "admin_notice"
BROADCAST_PAYLOAD_KEY = "admin_broadcast_payload"
PROMO_PAGE_KEY = "admin_promo_page"
PROMO_SELECTED_CODE_KEY = "admin_promo_selected_code"
PROMO_BULK_MODE_KEY = "admin_promo_bulk_mode"
PROMO_BULK_SELECTED_CODES_KEY = "admin_promo_bulk_selected_codes"
STARS_SELL_COUNT_KEY = "admin_stars_sell_count"
STARS_SELL_WALLET_KEY = "admin_stars_sell_wallet"
STARS_SELL_HISTORY_PAGE_KEY = "admin_stars_sell_history_page"
STARS_SELL_HISTORY_SELECTED_ORDER_ID_KEY = "admin_stars_sell_history_selected_order_id"
STARS_SELL_ADMIN_PAGE_KEY = "admin_stars_sell_admin_page"
STARS_SELL_ADMIN_SELECTED_ORDER_ID_KEY = "admin_stars_sell_admin_selected_order_id"


def i18n(dialog_manager: DialogManager) -> I18nContext:
    return cast(I18nContext, dialog_manager.middleware_data["i18n"])


def user_service(dialog_manager: DialogManager) -> UserService:
    return cast(UserService, dialog_manager.middleware_data["user_service"])


def promo_service(dialog_manager: DialogManager) -> PromoCodeService:
    return cast(PromoCodeService, dialog_manager.middleware_data["promo_code_service"])


def stars_order_service(dialog_manager: DialogManager) -> StarsOrderService:
    return cast(StarsOrderService, dialog_manager.middleware_data["stars_order_service"])


def stars_sell_order_service(dialog_manager: DialogManager) -> StarsSellOrderService:
    return cast(
        StarsSellOrderService,
        dialog_manager.middleware_data["stars_sell_order_service"],
    )


def set_notice(dialog_manager: DialogManager, text: str) -> None:
    dialog_manager.dialog_data[STATE_NOTICE_KEY] = text


def consume_notice(dialog_manager: DialogManager) -> str:
    value = dialog_manager.dialog_data.pop(STATE_NOTICE_KEY, "")
    return value if isinstance(value, str) else ""


def save_broadcast_payload(
    *,
    dialog_manager: DialogManager,
    payload: BroadcastPayload,
) -> None:
    dialog_manager.dialog_data[BROADCAST_PAYLOAD_KEY] = payload_to_state(payload)


def load_broadcast_payload(dialog_manager: DialogManager) -> BroadcastPayload | None:
    raw = dialog_manager.dialog_data.get(BROADCAST_PAYLOAD_KEY)
    if not isinstance(raw, dict):
        return None
    return payload_from_state(raw)


def clear_broadcast_payload(dialog_manager: DialogManager) -> None:
    dialog_manager.dialog_data.pop(BROADCAST_PAYLOAD_KEY, None)


def promo_page(dialog_manager: DialogManager) -> int:
    raw = dialog_manager.dialog_data.get(PROMO_PAGE_KEY, 0)
    if isinstance(raw, int):
        return max(raw, 0)
    if isinstance(raw, str) and raw.isdigit():
        return max(int(raw), 0)
    return 0


def set_promo_page(dialog_manager: DialogManager, page: int) -> None:
    dialog_manager.dialog_data[PROMO_PAGE_KEY] = max(page, 0)


def promo_selected_code(dialog_manager: DialogManager) -> str | None:
    raw = dialog_manager.dialog_data.get(PROMO_SELECTED_CODE_KEY)
    if isinstance(raw, str):
        value = raw.strip().upper()
        return value or None
    return None


def set_promo_selected_code(dialog_manager: DialogManager, code: str | None) -> None:
    if code is None:
        dialog_manager.dialog_data.pop(PROMO_SELECTED_CODE_KEY, None)
        return
    value = code.strip().upper()
    if not value:
        dialog_manager.dialog_data.pop(PROMO_SELECTED_CODE_KEY, None)
        return
    dialog_manager.dialog_data[PROMO_SELECTED_CODE_KEY] = value


def promo_bulk_mode(dialog_manager: DialogManager) -> bool:
    raw = dialog_manager.dialog_data.get(PROMO_BULK_MODE_KEY, False)
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        return raw.strip().lower() in {"1", "true", "yes", "on"}
    return False


def set_promo_bulk_mode(dialog_manager: DialogManager, *, enabled: bool) -> None:
    dialog_manager.dialog_data[PROMO_BULK_MODE_KEY] = enabled


def promo_bulk_selected_codes(dialog_manager: DialogManager) -> list[str]:
    raw = dialog_manager.dialog_data.get(PROMO_BULK_SELECTED_CODES_KEY, [])
    if not isinstance(raw, list):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, str):
            continue
        value = item.strip().upper()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def set_promo_bulk_selected_codes(dialog_manager: DialogManager, codes: list[str]) -> None:
    normalized: list[str] = []
    seen: set[str] = set()
    for code in codes:
        value = code.strip().upper()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    dialog_manager.dialog_data[PROMO_BULK_SELECTED_CODES_KEY] = normalized


def clear_promo_bulk_selected_codes(dialog_manager: DialogManager) -> None:
    dialog_manager.dialog_data.pop(PROMO_BULK_SELECTED_CODES_KEY, None)


def toggle_promo_bulk_selected_code(dialog_manager: DialogManager, code: str) -> bool:
    value = code.strip().upper()
    if not value:
        return False
    current = promo_bulk_selected_codes(dialog_manager)
    if value in current:
        set_promo_bulk_selected_codes(
            dialog_manager,
            [item for item in current if item != value],
        )
        return False
    current.append(value)
    set_promo_bulk_selected_codes(dialog_manager, current)
    return True


def stars_sell_count(dialog_manager: DialogManager) -> int | None:
    raw = dialog_manager.dialog_data.get(STARS_SELL_COUNT_KEY)
    if isinstance(raw, int) and raw > 0:
        return raw
    if isinstance(raw, str) and raw.isdigit():
        value = int(raw)
        if value > 0:
            return value
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


def stars_sell_admin_page(dialog_manager: DialogManager) -> int:
    raw = dialog_manager.dialog_data.get(STARS_SELL_ADMIN_PAGE_KEY)
    if isinstance(raw, int):
        return max(raw, 0)
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    return 0


def set_stars_sell_admin_page(dialog_manager: DialogManager, page: int) -> None:
    dialog_manager.dialog_data[STARS_SELL_ADMIN_PAGE_KEY] = max(page, 0)


def stars_sell_admin_selected_order_id(dialog_manager: DialogManager) -> int | None:
    raw = dialog_manager.dialog_data.get(STARS_SELL_ADMIN_SELECTED_ORDER_ID_KEY)
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    return None


def set_stars_sell_admin_selected_order_id(
    dialog_manager: DialogManager,
    order_id: int | None,
) -> None:
    if order_id is None:
        dialog_manager.dialog_data.pop(STARS_SELL_ADMIN_SELECTED_ORDER_ID_KEY, None)
        return
    dialog_manager.dialog_data[STARS_SELL_ADMIN_SELECTED_ORDER_ID_KEY] = order_id
