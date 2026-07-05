from __future__ import annotations

from app.models.config.env import (
    AppConfig,
    CommonConfig,
    CryptoPayConfig,
    FragmentConfig,
    HeleketPayConfig,
    LZTPayConfig,
    NicePayConfig,
    PaymentsConfig,
    PlategaPayConfig,
    PostgresConfig,
    RedisConfig,
    ServerConfig,
    SQLAlchemyConfig,
    TelegramConfig,
    TelegramGiftsUserbotConfig,
    TonPayConfig,
    XRocketPayConfig,
)


# noinspection PyArgumentList
def create_app_config() -> AppConfig:
    return AppConfig(
        telegram=TelegramConfig(),  # pyright: ignore[reportCallIssue]
        crypto_pay=CryptoPayConfig(),  # pyright: ignore[reportCallIssue]
        lzt_pay=LZTPayConfig(),  # pyright: ignore[reportCallIssue]
        nice_pay=NicePayConfig(),  # pyright: ignore[reportCallIssue]
        platega_pay=PlategaPayConfig(),  # pyright: ignore[reportCallIssue]
        heleket_pay=HeleketPayConfig(),  # pyright: ignore[reportCallIssue]
        xrocket_pay=XRocketPayConfig(),  # pyright: ignore[reportCallIssue]
        ton_pay=TonPayConfig(),  # pyright: ignore[reportCallIssue]
        payments=PaymentsConfig(),  # pyright: ignore[reportCallIssue]
        fragment=FragmentConfig(),  # pyright: ignore[reportCallIssue]
        postgres=PostgresConfig(),  # pyright: ignore[reportCallIssue]
        sql_alchemy=SQLAlchemyConfig(),
        redis=RedisConfig(),  # pyright: ignore[reportCallIssue]
        server=ServerConfig(),  # pyright: ignore[reportCallIssue]
        common=CommonConfig(),  # pyright: ignore[reportCallIssue]
        telegram_gifts_userbot=TelegramGiftsUserbotConfig(),  # pyright: ignore[reportCallIssue]
    )
