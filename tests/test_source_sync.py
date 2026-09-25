"""Guard invariants for the canonical reference and its distributable skill."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def brace_balance(css: str) -> int:
    css = re.sub(r"/\*[\s\S]*?\*/", "", css)
    return css.count("{") - css.count("}")


class SourceSyncTest(unittest.TestCase):
    def test_skill_is_exact_copy_of_canonical_readme(self):
        self.assertEqual(
            (ROOT / "README.md").read_bytes(),
            (ROOT / "SKILL.md").read_bytes(),
            "Update SKILL.md when README.md changes.",
        )

    def test_base_safeguards_have_balanced_css(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        section = readme.split("## Base safeguards", 1)[1].split("## Root scroll-state preset", 1)[0]
        css = section.split("```css", 1)[1].split("```", 1)[0]
        self.assertEqual(brace_balance(css), 0)


if __name__ == "__main__":
    unittest.main()
