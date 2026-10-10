from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.endpoints.miniapp.routes.orders import validate_recipient
from app.enums.stars_order import StarsOrderProductType
from app.models.dto.miniapp.orders import RecipientValidateRequest
from app.services.crud.stars_order import StarsOrderService


class MiniAppRecipientValidationTests(unittest.IsolatedAsyncioTestCase):
    async def test_service_rejects_username_not_resolved_by_telegram(self) -> None:
        service = object.__new__(StarsOrderService)
        service.telegram_gift_service = SimpleNamespace(
            resolve_user_id=AsyncMock(return_value=None),
            userbot_configured=True,
        )

        result = await service.validate_gift_recipient_username(
            recipient_username="missing_user",
        )

        self.assertIsNone(result)

    async def test_service_accepts_username_resolved_by_telegram(self) -> None:
        service = object.__new__(StarsOrderService)
        service.telegram_gift_service = SimpleNamespace(
            resolve_user_id=AsyncMock(return_value=123456),
            userbot_configured=True,
        )

        result = await service.validate_gift_recipient_username(
            recipient_username="@Real_User",
        )

        self.assertEqual(result, "Real_User")

    async def test_gift_validation_rejects_unresolved_telegram_user(self) -> None:
        service = SimpleNamespace(
            validate_gift_recipient_username=AsyncMock(return_value=None),
        )
        payload = RecipientValidateRequest(
            username="@missing_user",
            product_type=StarsOrderProductType.GIFT,
        )

        result = await validate_recipient(payload, object(), service)

        self.assertFalse(result.valid)
        self.assertIsNone(result.normalized)
        service.validate_gift_recipient_username.assert_awaited_once_with(
            recipient_username="missing_user",
        )

    async def test_gift_validation_returns_resolved_normalized_username(self) -> None:
        service = SimpleNamespace(
            validate_gift_recipient_username=AsyncMock(return_value="real_user"),
        )
        payload = RecipientValidateRequest(
            username=" @Real_User ",
            product_type=StarsOrderProductType.GIFT,
        )

        result = await validate_recipient(payload, object(), service)

        self.assertTrue(result.valid)
        self.assertEqual(result.normalized, "real_user")
        service.validate_gift_recipient_username.assert_awaited_once_with(
            recipient_username="Real_User",
        )

    async def test_legacy_validation_remains_syntax_only(self) -> None:
        service = SimpleNamespace(validate_gift_recipient_username=AsyncMock())
        payload = RecipientValidateRequest(username="@valid_name")

        result = await validate_recipient(payload, object(), service)

        self.assertTrue(result.valid)
        self.assertEqual(result.normalized, "valid_name")
        service.validate_gift_recipient_username.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
