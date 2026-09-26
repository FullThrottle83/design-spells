"""Pilot source/export parity and honest, complete inventory coverage."""
import json
import re
import unittest
from pathlib import Path
from scripts.showcase_fixtures import HINTS

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
SPELLS = {s['id']: s for s in json.loads((PUBLIC / 'spells.json').read_text())['spells']}

class ShowcaseTest(unittest.TestCase):
    def test_ledger_enumerates_every_stable_id_once(self):
        ledger = (ROOT / 'docs/DEMO-QUALITY-AUDIT.md').read_text()
        ids = re.findall(r'^\| (ds-(?:\d+|bonus)) —', ledger, re.M)
        self.assertEqual(len(ids), 154)
        self.assertEqual(len(set(ids)), 154)
        self.assertEqual(set(ids), set(SPELLS))
        self.assertIn('NOT a completed 154-spell visual audit', ledger)

    def test_hosted_download_and_iframe_share_one_fixture_and_source(self):
        for sid, hint in HINTS.items():
            with self.subTest(spell=sid):
                hosted = (PUBLIC / 'play' / sid / 'index.html').read_text()
                download = (PUBLIC / 'download' / f'{sid}.html').read_text()
                docs = (PUBLIC / 'spells' / sid / 'index.html').read_text()
                self.assertEqual(hosted.replace('  <meta name="robots" content="noindex,follow">', ''), download)
                self.assertIn(f'src="/play/{sid}/"', docs)
                self.assertIn(hint, hosted)
                self.assertIn(SPELLS[sid]['css'].strip(), hosted)
                self.assertNotIn('<script', hosted.lower())
                bundle = (PUBLIC / 'bundle' / f'{sid}.txt').read_text()
                self.assertIn(SPELLS[sid]['css'].strip(), bundle)
                self.assertNotIn('Demo-only art direction', bundle)
                self.assertNotIn('scene-instruction', bundle)

    def test_comparison_is_identical_except_authored_css(self):
        hosted = (PUBLIC / 'play/ds-5/index.html').read_text()
        base = (PUBLIC / 'play/ds-5/before/index.html').read_text()
        self.assertEqual(hosted.replace(SPELLS['ds-5']['css'], '', 1), base)
