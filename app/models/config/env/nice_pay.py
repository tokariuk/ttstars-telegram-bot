from pydantic import SecretStr

from .base import EnvSettings


class NicePayConfig(EnvSettings, env_prefix="NICE_PAY_"):
    merchant_id: str | None = None
    secret_key: SecretStr | None = None
    base_url: str = "https://nicepay.io"
    currency_ru: str = "RUB"
    currency_kz: str = "KZT"
    method: str | None = None
    webhook_path: str = "/nice-pay/webhook"
    success_url: str | None = None
    fail_url: str | None = None
    fee_percent_ru: str = "9"
    fee_percent_kz: str = "9"
    min_payment_usd_ru: str = "1"
    min_payment_usd_kz: str = "1"
    min_topup_usd_ru: str = "1"
    min_topup_usd_kz: str = "1"
    payout_fee_percent: str = "5.5"
    payout_fixed_usd: str = "0"
