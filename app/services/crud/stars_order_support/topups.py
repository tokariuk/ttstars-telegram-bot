from __future__ import annotations

TOPUP_ORDER_ID_OFFSET = 1_000_000_000

_UNPAID_TERMINAL_PROVIDER_STATUSES = {
    "canceled",
    "cancelled",
    "expired",
}


def encode_topup_order_id(*, topup_id: int) -> int:
    return TOPUP_ORDER_ID_OFFSET + int(topup_id)


def decode_topup_order_id(*, order_id: int) -> int | None:
    parsed = int(order_id)
    if parsed <= TOPUP_ORDER_ID_OFFSET:
        return None
    return parsed - TOPUP_ORDER_ID_OFFSET


def is_topup_virtual_order_id(*, order_id: int) -> bool:
    return decode_topup_order_id(order_id=order_id) is not None


def is_unpaid_terminal_provider_status(provider_status: str) -> bool:
    return provider_status.strip().lower() in _UNPAID_TERMINAL_PROVIDER_STATUSES
