from __future__ import annotations

import importlib
import importlib.util
import unittest
from typing import cast

from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.style import Style

from app.telegram.dialogs.common.ttstars_interface_emoji import TELEGRAM_STAR_EMOJI_ID
from app.telegram.dialogs.flows.admin.states import AdminSG


def _buttons(widget: object) -> list[Button]:
    if isinstance(widget, Button):
        return [widget]
    return [button for child in getattr(widget, "buttons", ()) for button in _buttons(child)]


class AdminCreativeToolsTests(unittest.TestCase):
    def test_creative_tools_are_screenshot_ready_and_use_live_catalog_prices(self) -> None:
        module_name = "app.telegram.dialogs.flows.admin.getters.creatives"
        spec = importlib.util.find_spec(module_name)
        self.assertIsNotNone(spec, "admin creative tools getter module is missing")
        if spec is None:
            return

        getters = importlib.import_module(module_name)
        windows = importlib.import_module("app.telegram.dialogs.flows.admin.windows.creatives")

        self.assertTrue(hasattr(AdminSG, "creatives_menu"))
        self.assertTrue(hasattr(AdminSG, "creatives_stars"))
        self.assertTrue(hasattr(AdminSG, "creatives_premium"))
        self.assertTrue(hasattr(AdminSG, "creatives_gifts"))
        self.assertTrue(hasattr(AdminSG, "creatives_overview"))

        star_offers = getters.creative_stars_offers()
        self.assertEqual(
            [(offer.amount, offer.price_usd) for offer in star_offers],
            [
                (100, "1.62"),
                (150, "2.43"),
                (250, "4.05"),
                (350, "5.67"),
                (500, "8.1"),
                (750, "12.15"),
                (1000, "16.2"),
            ],
        )
        self.assertEqual(
            [(offer.amount, offer.price_usd) for offer in getters.creative_premium_offers()],
            [(3, "12.99"), (6, "16.99"), (12, "30.99")],
        )
        self.assertEqual(
            [(offer.amount, offer.price_usd) for offer in getters.creative_gift_offers()],
            [(1, "0.59"), (11, "1.59")],
        )

        creative_windows = (
            windows.creatives_menu_window,
            windows.creatives_stars_window,
            windows.creatives_premium_window,
            windows.creatives_gifts_window,
            windows.creatives_overview_window,
        )
        for window in creative_windows:
            with self.subTest(state=str(cast(Window, window).state)):
                self.assertIsInstance(cast(Window, window).media, DynamicMedia)

        star_buttons = [
            button
            for button in _buttons(windows.creatives_stars_window.keyboard)
            if (button.widget_id or "").startswith("admin_creatives_stars_pack_")
        ]
        self.assertEqual(len(star_buttons), 7)
        for button in star_buttons:
            with self.subTest(button=button.widget_id):
                style = cast(Style, button.style)
                self.assertIsNone(style.style, "price previews must remain neutral gray buttons")
                self.assertEqual(style.emoji_id, TELEGRAM_STAR_EMOJI_ID)


if __name__ == "__main__":
    unittest.main()
