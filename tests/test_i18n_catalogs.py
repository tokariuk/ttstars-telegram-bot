from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any

from fluent.syntax import FluentParser, ast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MESSAGES_ROOT = PROJECT_ROOT / "assets" / "messages"
LOCALES = ("ru", "uk", "en")


def _walk_ast(node: Any) -> list[Any]:
    nodes = [node]
    if isinstance(node, list):
        for item in node:
            nodes.extend(_walk_ast(item))
        return nodes
    if not hasattr(node, "__dict__"):
        return nodes
    for value in vars(node).values():
        nodes.extend(_walk_ast(value))
    return nodes


def _catalog_contract(locale: str) -> dict[str, dict[str, frozenset[str]]]:
    parser = FluentParser()
    contract: dict[str, dict[str, frozenset[str]]] = {}
    locale_root = MESSAGES_ROOT / locale
    for path in sorted(locale_root.rglob("*.ftl")):
        relative_path = path.relative_to(locale_root).as_posix()
        resource = parser.parse(path.read_text(encoding="utf-8"))
        junk = [node for node in resource.body if isinstance(node, ast.Junk)]
        if junk:
            annotations = [annotation.message for node in junk for annotation in node.annotations]
            raise AssertionError(f"{locale}/{relative_path}: {annotations}")

        messages: dict[str, frozenset[str]] = {}
        for entry in resource.body:
            if not isinstance(entry, (ast.Message, ast.Term)):
                continue
            message_id = entry.id.name
            variables = frozenset(
                node.id.name
                for node in _walk_ast(entry)
                if isinstance(node, ast.VariableReference)
            )
            messages[message_id] = variables
        contract[relative_path] = messages
    return contract


class FluentCatalogContractTests(unittest.TestCase):
    def test_all_catalogs_parse_without_junk(self) -> None:
        for locale in LOCALES:
            with self.subTest(locale=locale):
                self.assertGreater(len(_catalog_contract(locale)), 0)

    def test_locales_have_matching_files_keys_and_placeholders(self) -> None:
        reference = _catalog_contract("ru")
        for locale in ("uk", "en"):
            with self.subTest(locale=locale):
                self.assertEqual(_catalog_contract(locale), reference)


if __name__ == "__main__":
    unittest.main()
