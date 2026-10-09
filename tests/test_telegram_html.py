from __future__ import annotations

import unittest

from app.telegram.html import (
    code,
    escape_attribute,
    escape_text,
    link,
    safe_diagnostic,
    spoiler_code,
    truncate_plain_text,
    username,
    visible_text_length,
)


class TelegramHtmlTests(unittest.TestCase):
    def test_plain_text_cannot_create_or_break_html_entities(self) -> None:
        hostile = '<b title="x">Tom & Jerry</b> \'unfinished'

        self.assertEqual(
            escape_text(hostile),
            "&lt;b title=&quot;x&quot;&gt;Tom &amp; Jerry&lt;/b&gt; &#x27;unfinished",
        )

    def test_attributes_escape_quotes_and_markup(self) -> None:
        self.assertEqual(
            escape_attribute('https://example.test/?q="<x>&'),
            "https://example.test/?q=&quot;&lt;x&gt;&amp;",
        )

    def test_link_escapes_label_and_attribute_and_rejects_unsafe_scheme(self) -> None:
        self.assertEqual(
            link("<Admin & Co>", 'tg://user?id=1&x="bad"'),
            '<a href="tg://user?id=1&amp;x=&quot;bad&quot;">&lt;Admin &amp; Co&gt;</a>',
        )
        self.assertEqual(link("<Admin>", "javascript:alert(1)"), "&lt;Admin&gt;")

    def test_copyable_identifiers_escape_the_value_once(self) -> None:
        self.assertEqual(code("tx<&>"), "<code>tx&lt;&amp;&gt;</code>")
        self.assertEqual(
            spoiler_code("tx<&>"),
            "<code><tg-spoiler>tx&lt;&amp;&gt;</tg-spoiler></code>",
        )

    def test_missing_identifier_uses_plain_placeholder(self) -> None:
        self.assertEqual(spoiler_code(None), "—")
        self.assertEqual(spoiler_code("  "), "—")

    def test_username_is_escaped_and_has_one_at_prefix(self) -> None:
        self.assertEqual(username("@name<&>"), "@name&lt;&amp;&gt;")
        self.assertEqual(username(None), "—")

    def test_visible_length_counts_rendered_text_not_tags_or_entities(self) -> None:
        rendered = '<blockquote><b>A &amp; B</b> <tg-emoji emoji-id="1">⭐</tg-emoji></blockquote>'

        self.assertEqual(visible_text_length(rendered), len("A & B ⭐"))

    def test_truncation_keeps_the_result_inside_the_requested_limit(self) -> None:
        self.assertEqual(truncate_plain_text("0123456789abcdef", max_length=10), "012345678…")
        self.assertEqual(truncate_plain_text("short", max_length=10), "short")

    def test_diagnostic_is_truncated_before_it_is_escaped(self) -> None:
        self.assertEqual(safe_diagnostic("123456789<b>", max_length=10), "123456789…")
        self.assertEqual(safe_diagnostic(None, max_length=10), "—")


if __name__ == "__main__":
    unittest.main()
