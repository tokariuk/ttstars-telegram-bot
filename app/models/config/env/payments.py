from .base import EnvSettings


class PaymentsConfig(EnvSettings, env_prefix="PAYMENTS_"):
    referral_level1_percent: str = "2"
    referral_level2_percent: str = "1"
    referral_level3_percent: str = "0.5"
    poll_interval_seconds: int = 20
    poll_batch_size: int = 200
    poll_concurrency: int = 8
    stars_sell_usd_per_star: str = "0.0118"
    stars_sell_hold_days: int = 21
    stars_sell_min_stars: int = 50
    stars_sell_max_stars: int = 25_000
