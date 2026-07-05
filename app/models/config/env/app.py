from pydantic import BaseModel

from .common import CommonConfig
from .crypto_pay import CryptoPayConfig
from .fragment import FragmentConfig
from .heleket_pay import HeleketPayConfig
from .lzt_pay import LZTPayConfig
from .nice_pay import NicePayConfig
from .payments import PaymentsConfig
from .platega_pay import PlategaPayConfig
from .postgres import PostgresConfig
from .redis import RedisConfig
from .server import ServerConfig
from .sql_alchemy import SQLAlchemyConfig
from .telegram import TelegramConfig
from .telegram_gifts_userbot import TelegramGiftsUserbotConfig
from .ton_pay import TonPayConfig
from .xrocket_pay import XRocketPayConfig


class AppConfig(BaseModel):
    telegram: TelegramConfig
    crypto_pay: CryptoPayConfig
    lzt_pay: LZTPayConfig
    nice_pay: NicePayConfig
    platega_pay: PlategaPayConfig
    heleket_pay: HeleketPayConfig
    xrocket_pay: XRocketPayConfig
    ton_pay: TonPayConfig
    payments: PaymentsConfig
    fragment: FragmentConfig
    postgres: PostgresConfig
    sql_alchemy: SQLAlchemyConfig
    redis: RedisConfig
    server: ServerConfig
    common: CommonConfig
    telegram_gifts_userbot: TelegramGiftsUserbotConfig
