from __future__ import annotations

from enum import StrEnum


class StarsSellOrderStatus(StrEnum):
    PENDING_PAYMENT = "pending_payment"
    PAID_HOLD = "paid_hold"
    COMPLETED = "completed"
    CANCELED = "canceled"
    REJECTED = "rejected"
    REFUNDED = "refunded"
    FAILED = "failed"


class StarsSellPayoutMethod(StrEnum):
    TON_USDT = "ton_usdt"


class StarsSellOrderResolutionReason(StrEnum):
    REPLACED_BY_NEW_REQUEST = "replaced_by_new_request"
    USER_REQUEST = "user_request"
    INVALID_PAYOUT_WALLET = "invalid_payout_wallet"
    STARS_REFUNDED = "stars_refunded"
    STARS_NOT_WITHDRAWABLE = "stars_not_withdrawable"
    FRAUD_SUSPECTED = "fraud_suspected"
    KYC_OR_FRAGMENT_RESTRICTION = "kyc_or_fragment_restriction"
    PAYOUT_TECHNICAL_FAILURE = "payout_technical_failure"
    POLICY_RESTRICTION = "policy_restriction"
    OTHER = "other"
