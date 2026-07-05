from pydantic import SecretStr

from .base import EnvSettings


class LZTPayConfig(EnvSettings, env_prefix="LZT_PAY_"):
    api_token: SecretStr | None = None
    base_url: str = "https://prod-api.lzt.market"
    merchant_id: int | None = None
    merchant_key: SecretStr | None = None
    currency: str = "usd"
    webhook_path: str = "/lzt-pay/webhook"
    success_url: str | None = None
    fee_percent: str = "0"
    min_payment_usd: str = "1"
    min_topup_usd: str = "1"
    payout_fee_percent: str = "0"
    payout_fixed_usd: str = "0"
