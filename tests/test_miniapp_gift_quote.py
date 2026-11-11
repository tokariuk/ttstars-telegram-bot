from __future__ import annotations

import unittest

from app.endpoints.miniapp.pricing import net_amount_cents_for_quote
from app.enums.stars_order import StarsOrderProductType


class MiniAppGiftQuoteTests(unittest.TestCase):
    def test_gift_quote_is_unavailable(self) -> None:
        with self.assertRaises(Exception):
            net_amount_cents_for_quote(
                product_type=StarsOrderProductType.GIFT,
                stars_count=None,
                months=None,
                amount_usd=None,
                gift_key="default_bear",
            )

    def test_gift_quote_requires_gift_key(self) -> None:
        with self.assertRaises(Exception):
            net_amount_cents_for_quote(
                product_type=StarsOrderProductType.GIFT,
                stars_count=None,
                months=None,
                amount_usd=None,
                gift_key=None,
            )


if __name__ == "__main__":
    unittest.main()
