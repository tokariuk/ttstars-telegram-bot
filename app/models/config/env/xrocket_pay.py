from pydantic import SecretStr

from .base import EnvSettings


class XRocketPayConfig(EnvSettings, env_prefix="XROCKET_PAY_"):
    api_key: SecretStr | None = None
    base_url: str = "https://pay.xrocket.exchange"
    currency: str = "USDT"
    webhook_path: str = "/xrocket-pay/webhook"
    success_url: str | None = None
    fee_percent: str = "0"
    min_payment_usd: str = "1"
    min_topup_usd: str = "1"
    payout_fee_percent: str = "0"
    payout_fixed_usd: str = "0"
