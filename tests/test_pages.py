"""Contracts for generated, independently navigable zero-script pages."""

import html
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CATALOGUE = json.loads((PUBLIC / "spells.json").read_text(encoding="utf-8"))


class StaticPagesTest(unittest.TestCase):
    def test_every_spell_has_documentation_and_standalone_demo(self):
        for spell in CATALOGUE["spells"]:
            sid = spell["id"]
            with self.subTest(spell=sid):
                doc = (PUBLIC / "spells" / sid / "index.html").read_text(encoding="utf-8")
                play = (PUBLIC / "play" / sid / "index.html").read_text(encoding="utf-8")
                self.assertIn(f"/play/{sid}/", doc)
                if sid in {"ds-1", "ds-2", "ds-5", "ds-6", "ds-7", "ds-18", "ds-24", "ds-38"}:
                    self.assertIn(f'/play/{sid}/before/', doc)
                    self.assertIn(f'Baseline without spell CSS: {html.escape(spell["title"], quote=True)}', doc)
                    baseline = (PUBLIC / "play" / sid / "before" / "index.html").read_text(encoding="utf-8")
                    self.assertIn("<!doctype html>", baseline.lower())
                    self.assertNotIn(spell["css"].strip(), baseline)
                    self.assertIn(spell["previewHtml"], baseline)
                    self.assertNotIn("<script", baseline.lower())
                    self.assertIn(spell["previewHtml"], play)
                else:
                    self.assertNotIn('class="demo-compare"', doc)
                self.assertIn(f'/download/{sid}.html', doc)
                self.assertIn(f'href="/bundle/{sid}.txt"', doc)
                self.assertIn('data-bundle-source', doc)
                self.assertIn('src="/spell-copy.js" defer', doc)
                if sid in {"ds-14", "ds-143"}:
                    self.assertNotIn('data-copy-bundle', doc)
                else:
                    self.assertIn(f'data-copy-bundle="{sid}" hidden', doc)
                exported = (PUBLIC / "download" / f"{sid}.html").read_text(encoding="utf-8")
                self.assertIn("<!doctype html>", exported.lower())
                self.assertIn("<style>", exported)
                self.assertIn("--color-primary:", exported)
                self.assertIn(spell["css"].strip().splitlines()[0], exported)
                self.assertNotIn("<script", exported.lower())
                self.assertNotIn('name="robots" content="noindex', exported)
                self.assertNotIn('href="/spell-pages.css"', exported)
                self.assertIn(f"/spells/{sid}/", doc)
                self.assertIn('sandbox="allow-same-origin"', doc)
                self.assertIn('name="robots" content="noindex,follow"', play)
                self.assertEqual(doc.count("<script"), 1)
                self.assertNotIn("<script", play.lower())
                self.assertIn(f"<h1>{html.escape(spell['title'], quote=True)}</h1>", doc)

    def test_sitemap_only_indexes_docs_and_catalogue(self):
        xml = (PUBLIC / "sitemap.xml").read_text(encoding="utf-8")
        self.assertEqual(xml.count("<url>"), CATALOGUE["total"] + 1)
        self.assertNotIn("/play/", xml)

    def test_root_scroll_state_demo_prerequisite_is_opt_in(self):
        for sid in ("ds-43", "ds-47"):
            with self.subTest(spell=sid):
                for path in (PUBLIC / "play" / sid / "index.html",
                             PUBLIC / "download" / f"{sid}.html"):
                    self.assertIn(
                        "html { container-type: scroll-state; overflow: auto; }",
                        path.read_text(encoding="utf-8"),
                    )
        self.assertNotIn(
            "html { container-type: scroll-state; overflow: auto; }",
            (PUBLIC / "play" / "ds-1" / "index.html").read_text(encoding="utf-8"),
        )

    def test_directional_scroll_demos_request_scroll_not_resize(self):
        for sid in ("ds-43", "ds-47"):
            with self.subTest(spell=sid):
                spell = next(s for s in CATALOGUE["spells"] if s["id"] == sid)
                self.assertEqual(spell["previewAction"]["kind"], "scroll")
                doc = (PUBLIC / "spells" / sid / "index.html").read_text(encoding="utf-8")
                self.assertIn("Scroll to preview", doc)
                self.assertNotIn("Drag the corner to resize", doc)

    def test_view_transition_uses_two_real_documents(self):
        first = (PUBLIC / "play" / "ds-14" / "index.html").read_text(encoding="utf-8")
        second = (PUBLIC / "play" / "ds-14" / "next" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Navigate to page B", first)
        self.assertIn("Return to page A", second)
        self.assertIn("@view-transition", first)
        self.assertIn("@view-transition", second)
        export_a = (PUBLIC / "download" / "ds-14.html").read_text(encoding="utf-8")
        export_b = (PUBLIC / "download" / "ds-14-next.html").read_text(encoding="utf-8")
        self.assertIn('href="ds-14-next.html"', export_a)
        self.assertIn('href="ds-14.html"', export_b)
        self.assertIn('download="ds-14-next.html"', (PUBLIC / "spells" / "ds-14" / "index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
