from pydantic import SecretStr

from .base import EnvSettings


class HeleketPayConfig(EnvSettings, env_prefix="HELEKET_PAY_"):
    merchant_id: str | None = None
    api_key: SecretStr | None = None
    base_url: str = "https://api.heleket.com"
    currency: str = "USD"
    to_currency: str | None = "USDT"
    network: str | None = None
    webhook_path: str = "/heleket-pay/webhook"
    return_url: str | None = None
    success_url: str | None = None
    callback_url: str | None = None
    webhook_trusted_ips: str | None = None
    webhook_trust_forwarded_ip: bool = False
    lifetime_seconds: int = 3600
    is_payment_multiple: bool = True
    subtract_percent: int = 0
    fee_percent: str = "2"
    min_payment_usd: str = "1"
    min_topup_usd: str = "1"
    payout_fee_percent: str = "0"
    payout_fixed_usd: str = "0"
