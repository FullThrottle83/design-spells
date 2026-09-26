"""Batch 02 preserves source/export boundaries and runnable page parity."""
import json
import unittest
from pathlib import Path
from scripts.showcase_scroll_fixtures import HINTS

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
SPELLS = {s['id']: s for s in json.loads((PUBLIC / 'spells.json').read_text())['spells']}

class ScrollShowcaseTest(unittest.TestCase):
    def test_source_and_runnable_surfaces_match(self):
        for sid, hint in HINTS.items():
            with self.subTest(spell=sid):
                hosted = (PUBLIC / 'play' / sid / 'index.html').read_text()
                download = (PUBLIC / 'download' / f'{sid}.html').read_text()
                docs = (PUBLIC / 'spells' / sid / 'index.html').read_text()
                bundle = (PUBLIC / 'bundle' / f'{sid}.txt').read_text()
                self.assertEqual(hosted.replace('  <meta name="robots" content="noindex,follow">', ''), download)
                self.assertIn(f'src="/play/{sid}/"', docs)
                self.assertIn(hint, docs)
                self.assertIn(hint, hosted)
                self.assertIn(SPELLS[sid]['css'].strip(), hosted)
                self.assertIn(SPELLS[sid]['css'].strip(), bundle)
                self.assertNotIn('Batch 02: demo-only', bundle)
                self.assertNotIn('<script', hosted.lower())

    def test_no_fake_deletion_or_hidden_fallback_data(self):
        spell = SPELLS['ds-134']
        self.assertNotIn('<button', spell['html'])
        self.assertIn('href="#document-details"', spell['html'])
        self.assertIn('id="document-details"', spell['html'])
        self.assertNotIn('>Delete<', spell['previewHtml'])
        self.assertIn('inline-size: var(--kpi, 0%)', SPELLS['ds-111']['css'])
        self.assertIn('<strong>72%</strong>', SPELLS['ds-111']['html'])
        self.assertIn('scrollable: inline-start', SPELLS['ds-69']['css'])
        self.assertNotIn('scrolled: inline', SPELLS['ds-69']['css'])

    def test_runnable_landscapes_are_self_contained(self):
        hosted = (PUBLIC / 'play/ds-93/index.html').read_text()
        self.assertEqual(hosted.count('src="data:image/jpeg;base64,'), 2)
        self.assertIn('AI-generated landscape studies', hosted)
        self.assertNotIn('src="/a.jpg"', hosted)
        for name in ('alpine', 'coastal'):
            self.assertTrue((ROOT / 'scripts/demo-assets' / f'{name}-study.jpg').is_file())

    def test_css_only_bundle_fixtures_supply_real_conditions(self):
        self.assertIn('min-block-size:150vh', SPELLS['ds-30']['previewHtml'])
        self.assertIn('min-block-size:55vh', SPELLS['ds-55']['previewHtml'])
        self.assertIn('tabindex="0"', SPELLS['ds-69']['previewHtml'])
