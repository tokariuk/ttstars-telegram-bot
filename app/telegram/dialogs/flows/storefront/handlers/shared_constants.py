from __future__ import annotations

from typing import Final

from app.stars import MAX_STARS_COUNT as STARS_MAX_ALLOWED
from app.stars import MIN_STARS_COUNT as STARS_MIN_ALLOWED

MIN_STARS_COUNT: Final[int] = STARS_MIN_ALLOWED
MAX_STARS_COUNT: Final[int] = STARS_MAX_ALLOWED

SELECTED_STARS_COUNT_KEY: Final[str] = "stars_selected_count"
STARS_RECIPIENT_USERNAME_KEY: Final[str] = "stars_recipient_username"
SELECTED_PREMIUM_MONTHS_KEY: Final[str] = "premium_selected_months"
PREMIUM_RECIPIENT_USERNAME_KEY: Final[str] = "premium_recipient_username"
TOPUP_AMOUNT_CENTS_KEY: Final[str] = "topup_amount_cents"
STATE_NOTICE_KEY: Final[str] = "state_notice"
HISTORY_PAGE_KEY: Final[str] = "history_page"
HISTORY_SELECTED_ORDER_ID_KEY: Final[str] = "history_selected_order_id"
REFERRALS_PAGE_KEY: Final[str] = "referrals_page"
REFERRALS_SELECTED_USER_ID_KEY: Final[str] = "referrals_selected_user_id"
CHECKS_PAGE_KEY: Final[str] = "checks_page"
CHECKS_SELECTED_CHECK_ID_KEY: Final[str] = "checks_selected_check_id"
CHECKS_HISTORY_PAGE_KEY: Final[str] = "checks_history_page"
CHECKS_HISTORY_SELECTED_CHECK_ID_KEY: Final[str] = "checks_history_selected_check_id"
CHECKS_CREATE_STARS_COUNT_KEY: Final[str] = "checks_create_stars_count"
CHECKS_CREATE_CLAIM_USERNAME_KEY: Final[str] = "checks_create_claim_username"
CHECKS_CREATE_CLAIM_PASSWORD_KEY: Final[str] = "checks_create_claim_password"
STARS_SELL_COUNT_KEY: Final[str] = "stars_sell_count"
STARS_SELL_WALLET_KEY: Final[str] = "stars_sell_wallet"
STARS_SELL_HISTORY_PAGE_KEY: Final[str] = "stars_sell_history_page"
STARS_SELL_HISTORY_SELECTED_ORDER_ID_KEY: Final[str] = "stars_sell_history_selected_order_id"

MIN_TOPUP_CENTS: Final[int] = 100
MAX_TOPUP_CENTS: Final[int] = 500_000
DEFAULT_TOPUP_CENTS: Final[int] = 1_000
