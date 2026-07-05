from pydantic import SecretStr

from app.utils.custom_types import StringList

from .base import EnvSettings


class TelegramConfig(EnvSettings, env_prefix="TELEGRAM_"):
    bot_token: SecretStr
    locales: StringList
    drop_pending_updates: bool
    use_webhook: bool
    reset_webhook: bool
    webhook_path: str
    webhook_secret: SecretStr
    miniapp_auth_max_age_seconds: int = 86_400
    miniapp_session_ttl_seconds: int = 86_400
    miniapp_cors_origins: StringList = ["https://ttstars.xyz"]
