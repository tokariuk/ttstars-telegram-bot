from __future__ import annotations

from enum import StrEnum


class CheckStatus(StrEnum):
    ACTIVE = "active"
    PROCESSING = "processing"
    REDEEMED = "redeemed"
    CLOSED = "closed"
