from __future__ import annotations

import unittest
from types import SimpleNamespace

from app.endpoints.miniapp.routes.orders import validate_recipient
from app.enums.stars_order import StarsOrderProductType
from app.models.dto.miniapp.orders import RecipientValidateRequest


class MiniAppRecipientValidationTests(unittest.IsolatedAsyncioTestCase):
    async def test_gift_recipient_is_unavailable(self) -> None:
        payload = RecipientValidateRequest(
            username="@valid_name", product_type=StarsOrderProductType.GIFT
        )
        result = await validate_recipient(
            payload, SimpleNamespace(), SimpleNamespace(), SimpleNamespace()
        )
        self.assertFalse(result.valid)

    async def test_other_recipient_remains_syntax_validated(self) -> None:
        payload = RecipientValidateRequest(username="@valid_name")
        result = await validate_recipient(
            payload, SimpleNamespace(), SimpleNamespace(), SimpleNamespace()
        )
        self.assertTrue(result.valid)
        self.assertEqual(result.normalized, "valid_name")


if __name__ == "__main__":
    unittest.main()
