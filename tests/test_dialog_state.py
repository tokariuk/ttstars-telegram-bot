from __future__ import annotations

import unittest

from app.telegram.dialogs.common.state import (
    clear_state_keys,
    read_non_negative_int,
    read_optional_int,
    read_positive_int,
    read_stripped_string,
    set_optional_int,
    set_positive_int,
    set_stripped_string,
)


class DialogStateReadTests(unittest.TestCase):
    def test_reads_non_negative_page_from_integer_or_numeric_string(self) -> None:
        self.assertEqual(read_non_negative_int({"page": 4}, "page"), 4)
        self.assertEqual(read_non_negative_int({"page": "5"}, "page"), 5)

    def test_non_negative_page_clamps_negative_integer_and_rejects_invalid_string(self) -> None:
        self.assertEqual(read_non_negative_int({"page": -2}, "page"), 0)
        self.assertEqual(read_non_negative_int({"page": "-2"}, "page"), 0)

    def test_reads_optional_identifier_without_changing_integer_sign(self) -> None:
        self.assertEqual(read_optional_int({"id": -3}, "id"), -3)
        self.assertEqual(read_optional_int({"id": "3"}, "id"), 3)
        self.assertIsNone(read_optional_int({"id": "3.0"}, "id"))

    def test_reads_only_positive_count(self) -> None:
        self.assertEqual(read_positive_int({"count": "3"}, "count"), 3)
        self.assertIsNone(read_positive_int({"count": 0}, "count"))
        self.assertIsNone(read_positive_int({"count": -1}, "count"))

    def test_reads_stripped_non_empty_string(self) -> None:
        self.assertEqual(read_stripped_string({"wallet": "  abc  "}, "wallet"), "abc")
        self.assertIsNone(read_stripped_string({"wallet": "   "}, "wallet"))
        self.assertIsNone(read_stripped_string({"wallet": 123}, "wallet"))


class DialogStateWriteTests(unittest.TestCase):
    def test_optional_identifier_is_stored_or_removed(self) -> None:
        data: dict[str, object] = {}
        set_optional_int(data, "id", -2)
        self.assertEqual(data, {"id": -2})
        set_optional_int(data, "id", None)
        self.assertEqual(data, {})

    def test_non_positive_count_removes_existing_value(self) -> None:
        data: dict[str, object] = {"count": 5}
        set_positive_int(data, "count", 0)
        self.assertEqual(data, {})

    def test_positive_count_preserves_integer_coercion(self) -> None:
        data: dict[str, object] = {}
        set_positive_int(data, "count", "7")  # type: ignore[arg-type]
        self.assertEqual(data, {"count": 7})

    def test_string_is_stripped_when_stored_and_removed_when_empty(self) -> None:
        data: dict[str, object] = {}
        set_stripped_string(data, "wallet", "  abc  ")
        self.assertEqual(data, {"wallet": "abc"})
        set_stripped_string(data, "wallet", "   ")
        self.assertEqual(data, {})

    def test_clear_removes_only_requested_keys(self) -> None:
        data: dict[str, object] = {"count": 5, "wallet": "abc", "other": True}
        clear_state_keys(data, "count", "wallet")
        self.assertEqual(data, {"other": True})


if __name__ == "__main__":
    unittest.main()
