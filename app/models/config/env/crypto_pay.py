from pydantic import SecretStr

from .base import EnvSettings


class CryptoPayConfig(EnvSettings, env_prefix="CRYPTO_PAY_"):
    api_token: SecretStr | None = None
    base_url: str = "https://pay.crypt.bot/api"
    currency_type: str = "fiat"
    fiat: str = "USD"
    accepted_assets: str | None = None
    asset: str = "USDT"
    webhook_path: str = "/crypto-pay/webhook"
    fee_percent: str = "3"
    min_payment_usd: str = "1"
    min_topup_usd: str = "1"
    payout_fee_percent: str = "0"
    payout_fixed_usd: str = "0"
