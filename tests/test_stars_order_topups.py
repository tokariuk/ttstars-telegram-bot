from __future__ import annotations

import unittest

from app.services.crud.stars_order import StarsOrderService


class TopupVirtualOrderIdTests(unittest.TestCase):
    def test_round_trip_uses_existing_offset(self) -> None:
        virtual_id = StarsOrderService._encode_topup_order_id(topup_id=42)

        self.assertEqual(virtual_id, 1_000_000_042)
        self.assertEqual(StarsOrderService._decode_topup_order_id(order_id=virtual_id), 42)
        self.assertTrue(StarsOrderService._is_topup_virtual_order_id(order_id=virtual_id))

    def test_offset_and_lower_ids_are_not_topups(self) -> None:
        self.assertIsNone(StarsOrderService._decode_topup_order_id(order_id=1_000_000_000))
        self.assertFalse(StarsOrderService._is_topup_virtual_order_id(order_id=999_999_999))


class TopupProviderStatusTests(unittest.TestCase):
    def test_terminal_status_is_case_and_whitespace_insensitive(self) -> None:
        self.assertTrue(StarsOrderService._is_unpaid_terminal_provider_status(" Cancelled "))
        self.assertTrue(StarsOrderService._is_unpaid_terminal_provider_status("EXPIRED"))
        self.assertFalse(StarsOrderService._is_unpaid_terminal_provider_status("pending"))


if __name__ == "__main__":
    unittest.main()
