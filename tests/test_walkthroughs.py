"""Native walkthroughs must remain demo-only and in sync with generated pages."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SPELLS = {spell["id"]: spell for spell in json.loads(
    (PUBLIC / "spells.json").read_text(encoding="utf-8")
)["spells"]}
ENTRY = {"ds-8", "ds-72", "ds-125", "ds-145"}


class WalkthroughTest(unittest.TestCase):
    def test_scroll_entry_stages_are_real_document_scrolling_not_script(self):
        for sid in ENTRY:
            with self.subTest(spell=sid):
                doc = (PUBLIC / "spells" / sid / "index.html").read_text(encoding="utf-8")
                self.assertIn("scroll runway", doc)
                for path in (PUBLIC / "play" / sid / "index.html",
                             PUBLIC / "download" / f"{sid}.html"):
                    source = path.read_text(encoding="utf-8")
                    self.assertIn('class="scroll-entry__intro"', source)
                    self.assertIn('href="#entry-effect"', source)
                    self.assertIn('id="entry-effect"', source)
                    self.assertIn("min-block-size:100dvh", source)
                    self.assertIn(SPELLS[sid]["css"].strip(), source)
                    self.assertIn(SPELLS[sid]["previewHtml"], source)
                    self.assertNotIn("<script", source.lower())

    def test_demo_only_theme_and_replay_never_pollute_spells(self):
        for sid, required in (
            ("ds-35", 'id="scheme-dark"'),
            ("ds-9", 'Replay entrance animation'),
        ):
            with self.subTest(spell=sid):
                for path in (PUBLIC / "play" / sid / "index.html",
                             PUBLIC / "download" / f"{sid}.html"):
                    content = path.read_text(encoding="utf-8")
                    self.assertIn(required, content)
                    self.assertIn(SPELLS[sid]["css"].strip(), content)
                    self.assertNotIn("<script", content.lower())
                self.assertNotIn(required, SPELLS[sid]["css"])
                self.assertNotIn(required, SPELLS[sid]["html"])
        for sid in ("ds-35", "ds-9", "ds-143"):
            self.assertIn(
                '<p class="note">',
                (PUBLIC / "spells" / sid / "index.html").read_text(encoding="utf-8"),
            )

    def test_print_demo_is_real_print_media_not_a_screen_replica(self):
        doc = (PUBLIC / "spells" / "ds-143" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Ctrl+P or Cmd+P", doc)
        demo = (PUBLIC / "play" / "ds-143" / "index.html").read_text(encoding="utf-8")
        self.assertIn("@media print", demo)
        self.assertNotIn("<script", demo.lower())


if __name__ == "__main__":
    unittest.main()
