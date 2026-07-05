from pydantic import SecretStr

from .base import EnvSettings


class PlategaPayConfig(EnvSettings, env_prefix="PLATEGA_PAY_"):
    merchant_id: str | None = None
    secret_key: SecretStr | None = None
    base_url: str = "https://app.platega.io"
    currency: str = "RUB"
    method: int = 2
    usd_to_currency_rate: str | None = None
    webhook_path: str = "/platega-pay/webhook"
    success_url: str | None = None
    fail_url: str | None = None
    fee_percent: str = "0"
    min_payment_usd: str = "1"
    min_topup_usd: str = "1"
    payout_fee_percent: str = "0"
    payout_fixed_usd: str = "0"
