from __future__ import annotations

import unittest

from app.utils.routes import normalize_route_path


class NormalizeRoutePathTests(unittest.TestCase):
    def test_prefixes_relative_path(self) -> None:
        self.assertEqual(normalize_route_path("payments/webhook"), "/payments/webhook")

    def test_preserves_absolute_path(self) -> None:
        self.assertEqual(normalize_route_path("/payments/webhook"), "/payments/webhook")

    def test_preserves_repeated_leading_slashes(self) -> None:
        self.assertEqual(normalize_route_path("//payments/webhook"), "//payments/webhook")

    def test_empty_path_becomes_root_path(self) -> None:
        self.assertEqual(normalize_route_path(""), "/")


if __name__ == "__main__":
    unittest.main()
