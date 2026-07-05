from .profile_checks import (
    checks_claim_password_window,
    checks_create_confirm_window,
    checks_create_password_window,
    checks_create_recipient_window,
    checks_create_stars_window,
    checks_details_window,
    checks_edit_password_window,
    checks_edit_recipient_window,
    checks_history_details_window,
    checks_history_window,
    checks_list_window,
    checks_settings_window,
)
from .profile_history import history_details_window, history_window
from .profile_main import profile_window
from .profile_promo import promo_window
from .profile_referrals import (
    referral_details_window,
    referral_list_window,
    referral_window,
    referral_withdraw_window,
)

__all__ = [
    "checks_claim_password_window",
    "checks_create_confirm_window",
    "checks_create_password_window",
    "checks_create_recipient_window",
    "checks_create_stars_window",
    "checks_details_window",
    "checks_edit_password_window",
    "checks_edit_recipient_window",
    "checks_history_details_window",
    "checks_history_window",
    "checks_list_window",
    "checks_settings_window",
    "history_details_window",
    "history_window",
    "profile_window",
    "promo_window",
    "referral_details_window",
    "referral_list_window",
    "referral_window",
    "referral_withdraw_window",
]
