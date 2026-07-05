from pydantic import SecretStr

from .base import EnvSettings


class TelegramGiftsUserbotConfig(EnvSettings, env_prefix="TELEGRAM_GIFTS_USERBOT_"):
    api_id: int | None = None
    api_hash: SecretStr | None = None
    session: SecretStr | None = None
    device_model: str = "TTStars Gifts Userbot"
    system_version: str = "Linux"
    app_version: str = "TTStars/1.0"
    lang_code: str = "en"
    system_lang_code: str = "en"
