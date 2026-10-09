from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, cast

from aiogram.enums.button_style import ButtonStyle
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog.widgets.style import Style
from fluent.runtime import FluentBundle, FluentResource
from fluent.syntax import FluentParser, ast

from app.telegram.dialogs.common import premium_emoji
from app.telegram.dialogs.flows.admin import windows as admin_windows
from app.telegram.dialogs.flows.admin.windows.orders import orders_menu_window
from app.telegram.dialogs.flows.storefront import windows as storefront_windows
from app.telegram.dialogs.flows.storefront.windows.gifts import gifts_payment_window
from app.telegram.dialogs.flows.storefront.windows.premium import premium_payment_window
from app.telegram.dialogs.flows.storefront.windows.stars import stars_payment_window
from app.telegram.dialogs.flows.storefront.windows.topup import topup_payment_window
from app.telegram.html import DIAGNOSTIC_TEXT_LIMIT, visible_text_length
from app.telegram.keyboards.callback_data.menu import CDDeposit, CDMenu
from app.telegram.keyboards.callback_data.order import (
    CDOrderCheckoutCancel,
    CDStarsSellInvoiceCancel,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CUSTOM_EMOJI_RE = re.compile(
    r'<tg-emoji\s+emoji-id="(?P<emoji_id>\d+)">(?P<fallback>.*?)</tg-emoji>',
    re.DOTALL,
)
SUPPORTED_TELEGRAM_TAGS = {
    "a",
    "b",
    "blockquote",
    "code",
    "mark",
    "table",
    "td",
    "tg-emoji",
    "tg-spoiler",
    "th",
    "tr",
}
CAPTION_BOUNDARY_KEYS = {
    "messages-admin_stars_sell_admin_detail_screen",
    "messages-admin_stars_sell_history_detail_screen",
    "messages-check_history_detail_screen",
    "messages-history_detail_screen",
    "messages-referral_screen",
    "messages-stars_sell_history_detail_screen",
}


class _TelegramMarkupParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag not in SUPPORTED_TELEGRAM_TAGS:
            self.errors.append(f"unsupported <{tag}>")
        self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unbalanced </{tag}>")
            return
        self.stack.pop()

    def finish(self) -> list[str]:
        self.close()
        return [*self.errors, *(f"unclosed <{tag}>" for tag in reversed(self.stack))]


def _fluent_bundle(locale: str) -> FluentBundle:
    bundle = FluentBundle([locale], use_isolating=False)
    for path in sorted((PROJECT_ROOT / "assets" / "messages" / locale).rglob("*.ftl")):
        bundle.add_resource(FluentResource(path.read_text(encoding="utf-8")))
    return bundle


def _walk_ast(node: Any) -> list[Any]:
    nodes = [node]
    if isinstance(node, list):
        for item in node:
            nodes.extend(_walk_ast(item))
        return nodes
    if hasattr(node, "__dict__"):
        for value in vars(node).values():
            nodes.extend(_walk_ast(value))
    return nodes


def _catalog_variables(locale: str) -> dict[str, frozenset[str]]:
    parser = FluentParser()
    variables: dict[str, frozenset[str]] = {}
    for path in sorted((PROJECT_ROOT / "assets" / "messages" / locale).rglob("*.ftl")):
        resource = parser.parse(path.read_text(encoding="utf-8"))
        for entry in resource.body:
            if isinstance(entry, (ast.Message, ast.Term)):
                variables[entry.id.name] = frozenset(
                    node.id.name
                    for node in _walk_ast(entry)
                    if isinstance(node, ast.VariableReference)
                )
    return variables


def _has_keyboard_action(widget: object) -> bool:
    children = getattr(widget, "buttons", None)
    if children is None:
        return True
    return any(_has_keyboard_action(child) for child in children)


class TelegramUiContractTests(unittest.TestCase):
    def test_legacy_emoji_catalog_keeps_public_provider_and_gift_exports(self) -> None:
        expected_exports = {
            "CRYPTOBOT_PAY_EMOJI_ID",
            "GIFT_DEFAULT_BEAR_EMOJI_ID",
            "LEFT_CIRCLE_2_EMOJI_ID",
            "TELEGRAM_STAR_EMOJI_ID",
            "TTSTARS_EMOJI_ID",
        }

        self.assertIsNone(getattr(premium_emoji, "__all__", None))
        for name in expected_exports:
            with self.subTest(name=name):
                self.assertTrue(hasattr(premium_emoji, name))

    def test_all_exported_dialog_windows_have_an_action_or_message_input(self) -> None:
        for module in (storefront_windows, admin_windows):
            windows = {
                name: value for name, value in vars(module).items() if isinstance(value, Window)
            }
            self.assertTrue(windows)
            for name, window in windows.items():
                with self.subTest(module=module.__name__, window=name):
                    self.assertTrue(
                        _has_keyboard_action(window.keyboard) or bool(window.on_message)
                    )

    def test_force_delivery_entry_point_is_styled_as_dangerous(self) -> None:
        force_button = cast(
            Button,
            next(
                button
                for button in cast(Group, orders_menu_window.keyboard).buttons
                if button.widget_id == "admin_orders_force"
            ),
        )

        self.assertEqual(cast(Style, force_button.style).style, ButtonStyle.DANGER)

    def test_unavailable_payment_choices_are_not_styled_as_destructive(self) -> None:
        payment_windows = (
            stars_payment_window,
            premium_payment_window,
            topup_payment_window,
            gifts_payment_window,
        )

        for window in payment_windows:
            for button in cast(Group, window.keyboard).buttons:
                if button.widget_id and button.widget_id.endswith("_danger"):
                    with self.subTest(state=str(window.state), button=button.widget_id):
                        style = cast(Style, cast(Button, button).style)
                        self.assertNotEqual(style.style, ButtonStyle.DANGER)

    def test_callback_payloads_fit_telegram_sixty_four_byte_limit(self) -> None:
        payloads = (
            CDDeposit().pack(),
            CDMenu().pack(),
            CDOrderCheckoutCancel(order_id=9_223_372_036_854_775_807).pack(),
            CDStarsSellInvoiceCancel(order_id=9_223_372_036_854_775_807).pack(),
        )

        for payload in payloads:
            with self.subTest(payload=payload):
                self.assertLessEqual(len(payload.encode("utf-8")), 64)

    def test_custom_emoji_markup_has_numeric_id_and_visible_fallback(self) -> None:
        files = sorted((PROJECT_ROOT / "assets" / "messages").rglob("*.ftl"))
        match_count = 0
        for path in files:
            text = path.read_text(encoding="utf-8")
            for match in CUSTOM_EMOJI_RE.finditer(text):
                match_count += 1
                with self.subTest(path=path, emoji_id=match.group("emoji_id")):
                    fallback = re.sub(r"<[^>]+>", "", match.group("fallback")).strip()
                    self.assertTrue(fallback)
        self.assertGreater(match_count, 0)

    def test_fluent_markup_uses_supported_balanced_telegram_tags(self) -> None:
        for path in sorted((PROJECT_ROOT / "assets" / "messages").rglob("*.ftl")):
            parser = _TelegramMarkupParser()
            parser.feed(path.read_text(encoding="utf-8"))
            with self.subTest(path=path):
                self.assertEqual(parser.finish(), [])

    def test_rendered_messages_and_media_captions_fit_telegram_limits(self) -> None:
        for locale in ("ru", "uk", "en"):
            bundle = _fluent_bundle(locale)
            variables_by_key = _catalog_variables(locale)
            for key, variables in variables_by_key.items():
                message = bundle.get_message(key)
                if message is None or message.value is None:
                    continue
                arguments = dict.fromkeys(variables, "X" * 20)
                for name in {
                    "error",
                    "failure_reason",
                    "invoice_payload",
                    "last_error",
                    "resolution_note",
                } & variables:
                    arguments[name] = "X" * DIAGNOSTIC_TEXT_LIMIT
                rendered, errors = bundle.format_pattern(message.value, arguments)
                with self.subTest(locale=locale, key=key):
                    self.assertEqual(errors, [])
                    if not isinstance(rendered, str):
                        self.fail("Fluent message did not render to text")
                    self.assertLessEqual(visible_text_length(rendered), 4096)
                    if key in CAPTION_BOUNDARY_KEYS:
                        self.assertLessEqual(visible_text_length(rendered), 1024)

    def test_localized_button_labels_remain_practical_on_mobile(self) -> None:
        for locale in ("ru", "uk", "en"):
            bundle = _fluent_bundle(locale)
            variables_by_key = _catalog_variables(locale)
            for key, variables in variables_by_key.items():
                if not key.startswith("buttons-"):
                    continue
                message = bundle.get_message(key)
                if message is None or message.value is None:
                    continue
                rendered, errors = bundle.format_pattern(
                    message.value,
                    dict.fromkeys(variables, "9999"),
                )
                with self.subTest(locale=locale, key=key):
                    self.assertEqual(errors, [])
                    if not isinstance(rendered, str):
                        self.fail("Fluent button did not render to text")
                    self.assertLessEqual(visible_text_length(rendered), 32)


if __name__ == "__main__":
    unittest.main()
