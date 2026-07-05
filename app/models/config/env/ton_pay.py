from pydantic import SecretStr

from .base import EnvSettings


class TonPayConfig(EnvSettings, env_prefix="TON_PAY_"):
    tonapi_base_url: str = "https://tonapi.io"
    tonapi_api_key: SecretStr | None = None
    invoice_api_key: SecretStr | None = None
    invoice_base_url: str = "https://tonconsole.com"
    invoice_webhook_path: str = "/ton-pay/webhook"
    invoice_lifetime_seconds: int = 1800
    invoice_currency: str = "TON"
    invoice_status_cache_ttl_seconds: int = 5
    invoice_tx_scan_limit: int = 50
    rate_cache_ttl_seconds: int = 30
    fee_percent: str = "1"
    min_payment_usd: str = "1"
    payout_fee_percent: str = "0"
    payout_fixed_usd: str = "0"
