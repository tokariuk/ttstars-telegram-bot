from __future__ import annotations

import unittest

from app.endpoints.miniapp.errors import ApiError, ErrorCode
from app.endpoints.miniapp.pricing import net_amount_cents_for_quote
from app.enums.stars_order import StarsOrderProductType
from app.models.dto.miniapp import CatalogResponse, QuoteRequest


class MiniAppGiftQuoteTests(unittest.TestCase):
    def test_gift_quote_is_unavailable(self) -> None:
        with self.assertRaises(ApiError) as raised:
            net_amount_cents_for_quote(
                product_type=StarsOrderProductType.GIFT,
                stars_count=None,
                months=None,
                amount_usd=None,
            )
        self.assertEqual(raised.exception.code, ErrorCode.VALIDATION_ERROR)

    def test_catalog_and_quote_contracts_expose_no_gift_purchase_fields(self) -> None:
        self.assertNotIn("gift_key", QuoteRequest.model_fields)
        self.assertNotIn("gifts", CatalogResponse.model_fields)


if __name__ == "__main__":
    unittest.main()
