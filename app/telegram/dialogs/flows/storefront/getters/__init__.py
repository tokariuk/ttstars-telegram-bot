from .billing import topup_amount_getter, topup_payment_getter
from .calculator import calculator_getter
from .checks import (
    checks_claim_password_getter,
    checks_create_confirm_getter,
    checks_create_password_getter,
    checks_create_recipient_getter,
    checks_create_stars_getter,
    checks_details_getter,
    checks_edit_password_getter,
    checks_edit_recipient_getter,
    checks_history_details_getter,
    checks_history_getter,
    checks_list_getter,
    checks_settings_getter,
)
from .faq import faq_getter
from .gifts import (
    gifts_catalog_getter,
    gifts_message_getter,
    gifts_payment_getter,
    gifts_recipient_getter,
    gifts_sender_privacy_getter,
)
from .history import history_details_getter, history_getter
from .menu import menu_getter
from .premium import premium_payment_getter, premium_plans_getter, premium_recipient_getter
from .profile import (
    profile_getter,
    promo_getter,
)
from .referrals import (
    referral_details_getter,
    referral_getter,
    referral_list_getter,
    referral_withdraw_getter,
)
from .stars import stars_amount_getter, stars_payment_getter, stars_recipient_getter
from .stars_sell import (
    stars_sell_history_details_getter,
    stars_sell_history_getter,
    stars_sell_menu_getter,
    stars_sell_payment_getter,
    stars_sell_stars_getter,
    stars_sell_wallet_getter,
)

__all__ = [
    "calculator_getter",
    "checks_claim_password_getter",
    "checks_create_password_getter",
    "checks_create_confirm_getter",
    "checks_create_recipient_getter",
    "checks_create_stars_getter",
    "checks_details_getter",
    "checks_edit_password_getter",
    "checks_edit_recipient_getter",
    "checks_history_details_getter",
    "checks_history_getter",
    "checks_list_getter",
    "checks_settings_getter",
    "faq_getter",
    "gifts_catalog_getter",
    "gifts_message_getter",
    "gifts_payment_getter",
    "gifts_recipient_getter",
    "gifts_sender_privacy_getter",
    "history_details_getter",
    "history_getter",
    "menu_getter",
    "premium_payment_getter",
    "premium_plans_getter",
    "premium_recipient_getter",
    "profile_getter",
    "promo_getter",
    "referral_details_getter",
    "referral_getter",
    "referral_list_getter",
    "referral_withdraw_getter",
    "stars_amount_getter",
    "stars_payment_getter",
    "stars_recipient_getter",
    "stars_sell_history_details_getter",
    "stars_sell_history_getter",
    "stars_sell_menu_getter",
    "stars_sell_payment_getter",
    "stars_sell_stars_getter",
    "stars_sell_wallet_getter",
    "topup_amount_getter",
    "topup_payment_getter",
]
