from __future__ import annotations

from typing import Any, TypedDict

from pydantic import SecretStr
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.config import AppConfig
from app.services.crud import (
    CheckService,
    StarsOrderService,
    StarsSellOrderService,
    UserService,
)
from app.services.crypto_pay import CryptoPayService
from app.services.fragment_stars import FragmentStarsService
from app.services.heleket_pay import HeleketPayService
from app.services.lzt_pay import LZTPayService
from app.services.nice_pay import NicePayService
from app.services.platega_pay import PlategaPayService
from app.services.promo_codes import PromoCodeService
from app.services.redis import RedisRepository
from app.services.telegram_gifts import TelegramGiftService
from app.services.ton_pay import TonPayService
from app.services.xrocket_pay import XRocketPayService


class Services(TypedDict):
    check_service: CheckService
    crypto_pay_service: CryptoPayService
    fragment_stars_service: FragmentStarsService
    heleket_pay_service: HeleketPayService
    lzt_pay_service: LZTPayService
    nice_pay_service: NicePayService
    platega_pay_service: PlategaPayService
    promo_code_service: PromoCodeService
    redis_repository: RedisRepository
    stars_order_service: StarsOrderService
    stars_sell_order_service: StarsSellOrderService
    telegram_gift_service: TelegramGiftService
    ton_pay_service: TonPayService
    user_service: UserService
    xrocket_pay_service: XRocketPayService


def _secret_value(value: SecretStr | None) -> str | None:
    if value is None:
        return None
    return value.get_secret_value()


def _stripped_or_none(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def create_services(
    session_pool: async_sessionmaker[AsyncSession],
    redis: Redis,
    config: AppConfig,
) -> Services:
    crud_service_kwargs: dict[str, Any] = {
        "session_pool": session_pool,
        "redis": redis,
        "config": config,
    }

    redis_repository: RedisRepository = RedisRepository(client=redis, config=config)
    lzt_success_url = _stripped_or_none(config.lzt_pay.success_url) or config.server.url.strip()
    crypto_pay_service = CryptoPayService(
        api_token=_secret_value(config.crypto_pay.api_token),
        base_url=config.crypto_pay.base_url,
        currency_type=config.crypto_pay.currency_type,
        fiat=config.crypto_pay.fiat,
        accepted_assets=config.crypto_pay.accepted_assets,
        asset=config.crypto_pay.asset,
    )
    lzt_pay_service = LZTPayService(
        api_token=_secret_value(config.lzt_pay.api_token),
        base_url=config.lzt_pay.base_url,
        merchant_id=config.lzt_pay.merchant_id,
        merchant_key=_secret_value(config.lzt_pay.merchant_key),
        currency=config.lzt_pay.currency,
        success_url=lzt_success_url,
    )
    nice_pay_service = NicePayService(
        merchant_id=config.nice_pay.merchant_id,
        secret_key=_secret_value(config.nice_pay.secret_key),
        base_url=config.nice_pay.base_url,
        currency=config.nice_pay.currency_ru,
        method=config.nice_pay.method,
        success_url=config.nice_pay.success_url,
        fail_url=config.nice_pay.fail_url,
    )
    platega_pay_service = PlategaPayService(
        merchant_id=config.platega_pay.merchant_id,
        secret_key=_secret_value(config.platega_pay.secret_key),
        base_url=config.platega_pay.base_url,
        currency=config.platega_pay.currency,
        payment_method=config.platega_pay.method,
        success_url=config.platega_pay.success_url,
        fail_url=config.platega_pay.fail_url,
        usd_to_currency_rate=config.platega_pay.usd_to_currency_rate,
    )
    heleket_pay_service = HeleketPayService(
        merchant_id=config.heleket_pay.merchant_id,
        api_key=_secret_value(config.heleket_pay.api_key),
        base_url=config.heleket_pay.base_url,
        currency=config.heleket_pay.currency,
        to_currency=config.heleket_pay.to_currency,
        network=config.heleket_pay.network,
        return_url=config.heleket_pay.return_url,
        success_url=config.heleket_pay.success_url,
        callback_url=config.heleket_pay.callback_url,
        lifetime_seconds=config.heleket_pay.lifetime_seconds,
        is_payment_multiple=config.heleket_pay.is_payment_multiple,
        subtract_percent=config.heleket_pay.subtract_percent,
    )
    xrocket_pay_service = XRocketPayService(
        api_key=_secret_value(config.xrocket_pay.api_key),
        base_url=config.xrocket_pay.base_url,
        currency=config.xrocket_pay.currency,
        success_url=config.xrocket_pay.success_url,
    )
    ton_pay_service = TonPayService(
        tonapi_base_url=config.ton_pay.tonapi_base_url,
        tonapi_api_key=_secret_value(config.ton_pay.tonapi_api_key),
        invoice_api_key=_secret_value(config.ton_pay.invoice_api_key),
        invoice_base_url=config.ton_pay.invoice_base_url,
        invoice_lifetime_seconds=config.ton_pay.invoice_lifetime_seconds,
        invoice_currency=config.ton_pay.invoice_currency,
        invoice_status_cache_ttl_seconds=config.ton_pay.invoice_status_cache_ttl_seconds,
        invoice_tx_scan_limit=config.ton_pay.invoice_tx_scan_limit,
        rate_cache_ttl_seconds=config.ton_pay.rate_cache_ttl_seconds,
    )
    telegram_gift_service = TelegramGiftService(
        bot_token=config.telegram.bot_token.get_secret_value(),
        userbot_api_id=config.telegram_gifts_userbot.api_id,
        userbot_api_hash=_secret_value(config.telegram_gifts_userbot.api_hash),
        userbot_session=_secret_value(config.telegram_gifts_userbot.session),
        userbot_device_model=config.telegram_gifts_userbot.device_model,
        userbot_system_version=config.telegram_gifts_userbot.system_version,
        userbot_app_version=config.telegram_gifts_userbot.app_version,
        userbot_lang_code=config.telegram_gifts_userbot.lang_code,
        userbot_system_lang_code=config.telegram_gifts_userbot.system_lang_code,
    )
    fragment_stars_service = FragmentStarsService(
        cookies=_secret_value(config.fragment.cookies),
        fragment_hash=_secret_value(config.fragment.hash),
        wallet_api_key=_secret_value(config.fragment.wallet_api_key),
        wallet_mnemonic=_secret_value(config.fragment.wallet_mnemonic),
        wallet_version=config.fragment.wallet_version,
    )
    promo_code_service = PromoCodeService(redis=redis)
    check_service: CheckService = CheckService(
        **crud_service_kwargs,
        fragment_stars_service=fragment_stars_service,
    )
    user_service: UserService = UserService(
        **crud_service_kwargs,
        promo_code_service=promo_code_service,
    )
    stars_order_service: StarsOrderService = StarsOrderService(
        **crud_service_kwargs,
        crypto_pay_service=crypto_pay_service,
        heleket_pay_service=heleket_pay_service,
        lzt_pay_service=lzt_pay_service,
        nice_pay_service=nice_pay_service,
        platega_pay_service=platega_pay_service,
        telegram_gift_service=telegram_gift_service,
        ton_pay_service=ton_pay_service,
        xrocket_pay_service=xrocket_pay_service,
        fragment_stars_service=fragment_stars_service,
    )
    stars_sell_order_service: StarsSellOrderService = StarsSellOrderService(
        **crud_service_kwargs,
    )

    return Services(
        check_service=check_service,
        crypto_pay_service=crypto_pay_service,
        fragment_stars_service=fragment_stars_service,
        heleket_pay_service=heleket_pay_service,
        lzt_pay_service=lzt_pay_service,
        nice_pay_service=nice_pay_service,
        platega_pay_service=platega_pay_service,
        promo_code_service=promo_code_service,
        redis_repository=redis_repository,
        stars_order_service=stars_order_service,
        stars_sell_order_service=stars_sell_order_service,
        telegram_gift_service=telegram_gift_service,
        ton_pay_service=ton_pay_service,
        user_service=user_service,
        xrocket_pay_service=xrocket_pay_service,
    )
