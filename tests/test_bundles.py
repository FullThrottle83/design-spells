"""Dependency-aware integration export must be deterministic and honest."""

import json
import unittest
from pathlib import Path

from scripts.build import DOCUMENT_TOKENS
from scripts.build_bundle import render_bundle, resolve_tokens

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = json.loads((ROOT / "public" / "spells.json").read_text(encoding="utf-8"))


class IntegrationBundleTest(unittest.TestCase):
    def test_token_closure_includes_dependencies_but_not_unused_registry(self):
        registry = ":root { --primary: var(--secondary); --secondary: #123; --unused: black; }"
        selected, missing = resolve_tokens(
            ".widget { color: var(--primary); border: var(--local); }"
            ".widget { --local: 1px; }",
            "<div class='widget'></div>",
            registry,
        )
        self.assertEqual(list(selected), ["--primary", "--secondary"])
        self.assertEqual(missing, [])
        self.assertNotIn("--unused", selected)

    def test_unknown_project_values_are_not_silently_resolved(self):
        source = render_bundle({
            "id": "ds-test", "title": "Test", "html": "<div class='x'></div>",
            "previewHtml": "<p>fixture</p>", "css": ".x { color: var(--brand-accent); }",
        }, DOCUMENT_TOKENS)
        self.assertIn("--brand-accent", source)
        self.assertIn("Project variables not defined", source)
        self.assertNotIn("<script", source)

    def test_all_150_generated_bundles_match_canonical_sources(self):
        for spell in CATALOGUE["spells"]:
            sid = spell["id"]
            with self.subTest(spell=sid):
                path = ROOT / "public" / "bundle" / f"{sid}.txt"
                self.assertTrue(path.is_file())
                source = path.read_text(encoding="utf-8")
                self.assertEqual(source, render_bundle(spell, DOCUMENT_TOKENS))
                self.assertIn(spell["css"].strip(), source)
                self.assertTrue(source.startswith("<!doctype html>\n"))
                self.assertNotIn("<script", source.lower())
                self.assertNotIn("*, *::before, *::after { box-sizing", source)
                if spell["html"].strip():
                    self.assertIn(spell["html"].strip(), source)
                    self.assertIn("Authored markup from README.md", source)
                else:
                    self.assertIn("Demo fixture, NOT authored component markup", source)
                selected, missing = resolve_tokens(
                    spell["css"], spell["html"] or spell["previewHtml"], DOCUMENT_TOKENS
                )
                for name in selected:
                    self.assertIn(f"  {name}: ", source)
                if missing:
                    self.assertIn("Project variables not defined", source)
                    for name in missing:
                        self.assertIn(name, source)

    def test_root_scroll_state_is_opt_in_and_document_effect_is_labelled(self):
        first = (ROOT / "public" / "bundle" / "ds-1.txt").read_text(encoding="utf-8")
        scroll = (ROOT / "public" / "bundle" / "ds-43.txt").read_text(encoding="utf-8")
        transition = (ROOT / "public" / "bundle" / "ds-14.txt").read_text(encoding="utf-8")
        self.assertNotIn("html { container-type: scroll-state; overflow: auto; }", first)
        self.assertIn("html { container-type: scroll-state; overflow: auto; }", scroll)
        self.assertIn("needs both linked HTML documents", transition)
        self.assertNotIn("--space-8:", first)


if __name__ == "__main__":
    unittest.main()
