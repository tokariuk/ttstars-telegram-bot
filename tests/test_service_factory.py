from __future__ import annotations

import unittest
from types import SimpleNamespace
from typing import Any, cast

from pydantic import SecretStr

from app.factory.services import _create_application_services, _create_payment_services


def _config() -> Any:
    config = SimpleNamespace(
        server=SimpleNamespace(url="https://example.test"),
        telegram=SimpleNamespace(bot_token=SecretStr("bot-token")),
        crypto_pay=SimpleNamespace(
            api_token=SecretStr("crypto-token"),
            base_url="https://crypto.test/",
            currency_type="crypto",
            fiat="usd",
            accepted_assets="usdt",
            asset="usdt",
        ),
        lzt_pay=SimpleNamespace(
            api_token=SecretStr("lzt-token"),
            base_url="https://lzt.test/",
            merchant_id=12,
            merchant_key=SecretStr("lzt-key"),
            currency="usd",
            success_url="   ",
        ),
        nice_pay=SimpleNamespace(
            merchant_id="nice-id",
            secret_key=SecretStr("nice-key"),
            base_url="https://nice.test/",
            currency_ru="rub",
            method="card",
            success_url="https://example.test/success",
            fail_url="https://example.test/fail",
        ),
        platega_pay=SimpleNamespace(
            merchant_id="platega-id",
            secret_key=SecretStr("platega-key"),
            base_url="https://platega.test/",
            currency="rub",
            method=2,
            success_url="https://example.test/success",
            fail_url="https://example.test/fail",
            usd_to_currency_rate="90",
        ),
        heleket_pay=SimpleNamespace(
            merchant_id="heleket-id",
            api_key=SecretStr("heleket-key"),
            base_url="https://heleket.test/",
            currency="usd",
            to_currency=None,
            network=None,
            return_url=None,
            success_url=None,
            callback_url=None,
            lifetime_seconds=900,
            is_payment_multiple=False,
            subtract_percent=0,
        ),
        xrocket_pay=SimpleNamespace(
            api_key=SecretStr("xrocket-key"),
            base_url="https://xrocket.test/",
            currency="usdt",
            success_url="https://example.test/success",
        ),
        ton_pay=SimpleNamespace(
            tonapi_base_url="https://tonapi.test/",
            tonapi_api_key=SecretStr("tonapi-key"),
            invoice_api_key=SecretStr("invoice-key"),
            invoice_base_url="https://invoice.test/",
            invoice_lifetime_seconds=900,
            invoice_currency="ton",
            invoice_status_cache_ttl_seconds=30,
            invoice_tx_scan_limit=50,
            rate_cache_ttl_seconds=10,
        ),
        telegram_gifts_userbot=SimpleNamespace(
            api_id=123,
            api_hash=SecretStr("api-hash"),
            session=SecretStr("session"),
            device_model="device",
            system_version="system",
            app_version="app",
            lang_code="en",
            system_lang_code="en",
        ),
        fragment=SimpleNamespace(
            cookies=SecretStr("cookies"),
            hash=SecretStr("hash"),
            wallet_api_key=SecretStr("wallet-key"),
            wallet_mnemonic=SecretStr("one two three"),
            wallet_version="V5R1",
        ),
        payments=SimpleNamespace(
            referral_level1_percent="2",
            referral_level2_percent="1",
            referral_level3_percent="0.5",
            poll_concurrency=8,
            poll_unpaid_max_age_hours=24,
            stars_sell_min_stars=50,
            stars_sell_max_stars=25_000,
            stars_sell_hold_days=21,
            stars_sell_usd_per_star="0.0118",
        ),
    )
    for provider_name in (
        "crypto_pay",
        "lzt_pay",
        "nice_pay",
        "platega_pay",
        "heleket_pay",
        "xrocket_pay",
        "ton_pay",
    ):
        provider = getattr(config, provider_name)
        provider.fee_percent = "0"
        provider.payout_fee_percent = "0"
        provider.payout_fixed_usd = "0"
        provider.min_payment_usd = "1"
        provider.min_topup_usd = "1"
    config.nice_pay.currency_kz = "KZT"
    config.nice_pay.fee_percent_ru = "9"
    config.nice_pay.fee_percent_kz = "9"
    config.nice_pay.min_payment_usd_ru = "1"
    config.nice_pay.min_payment_usd_kz = "1"
    config.nice_pay.min_topup_usd_ru = "1"
    config.nice_pay.min_topup_usd_kz = "1"
    return config


class PaymentServiceFactoryTests(unittest.TestCase):
    def test_constructs_all_payment_services_and_applies_existing_normalization(self) -> None:
        services = _create_payment_services(cast(Any, _config()))

        self.assertEqual(
            set(services),
            {
                "crypto_pay_service",
                "fragment_stars_service",
                "heleket_pay_service",
                "lzt_pay_service",
                "nice_pay_service",
                "platega_pay_service",
                "telegram_gift_service",
                "ton_pay_service",
                "xrocket_pay_service",
            },
        )
        self.assertEqual(services["lzt_pay_service"].success_url, "https://example.test")
        self.assertEqual(services["crypto_pay_service"].asset, "USDT")
        self.assertEqual(services["xrocket_pay_service"].currency, "USDT")


class ApplicationServiceFactoryTests(unittest.TestCase):
    def test_wires_application_services_to_shared_dependencies(self) -> None:
        config = _config()
        payment_services = _create_payment_services(cast(Any, config))
        session_pool = object()
        redis = object()

        services = _create_application_services(
            session_pool=cast(Any, session_pool),
            redis=cast(Any, redis),
            config=cast(Any, config),
            payment_services=payment_services,
        )

        self.assertEqual(
            set(services),
            {
                "check_service",
                "promo_code_service",
                "redis_repository",
                "stars_order_service",
                "stars_sell_order_service",
                "user_service",
            },
        )
        self.assertIs(services["redis_repository"].client, redis)
        self.assertIs(
            services["check_service"].fragment_stars_service,
            payment_services["fragment_stars_service"],
        )
        self.assertIs(
            services["stars_order_service"].crypto_pay_service,
            payment_services["crypto_pay_service"],
        )
        self.assertIs(
            services["user_service"].promo_code_service,
            services["promo_code_service"],
        )


if __name__ == "__main__":
    unittest.main()
