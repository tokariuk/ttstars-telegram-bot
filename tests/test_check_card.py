from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from app.telegram.dialogs.flows.storefront.check_card import build_check_card_preview_url


class CheckCardPreviewTests(unittest.TestCase):
    def test_missing_base_url_uses_placeholder_after_local_render(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch(
                "app.telegram.dialogs.flows.storefront.check_card.render_check_card",
                return_value="/assets/checks/generated/card.jpg",
            ),
        ):
            preview_url = build_check_card_preview_url(
                stars_count=100,
                amount_usd="1.23",
                seed="check-1",
            )

        self.assertEqual(
            preview_url,
            "https://placehold.co/1600x1000/14120b/f8d85a.jpg"
            "?font=poppins&text=100+Stars%0A~1%2C23%24",
        )


if __name__ == "__main__":
    unittest.main()
