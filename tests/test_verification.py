"""Evidence contract regression tests: syntax/support lookup is not an audit."""

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from scripts.build import load_verification_overrides, verification_for_spell

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"


class VerificationContractTest(unittest.TestCase):
    def test_all_spells_disclose_unverified_baseline(self):
        catalogue = json.loads((PUBLIC / "spells.json").read_text(encoding="utf-8"))
        schema = json.loads((PUBLIC / "spells.schema.json").read_text(encoding="utf-8"))
        self.assertIn("verification", schema["$defs"]["spell"]["required"])
        self.assertEqual(catalogue["total"], len(catalogue["spells"]))
        for spell in catalogue["spells"]:
            with self.subTest(id=spell["id"]):
                state = spell["verification"]
                self.assertEqual(state["support"], "registry-estimate")
                self.assertEqual(state["behavior"], "not-individually-verified")
                self.assertEqual(state["accessibility"], "not-audited")
                self.assertEqual(state["sources"], [])
                self.assertTrue(spell["featureKeys"])
                doc = (PUBLIC / "spells" / spell["id"] / "index.html").read_text(encoding="utf-8")
                self.assertIn("registry-estimate", doc)
                self.assertIn("not-individually-verified", doc)
                self.assertIn("not-audited", doc)

    def test_schema_prevents_unsupported_verification_claims(self):
        from test_build import validate, SchemaError
        schema = json.loads((PUBLIC / "spells.schema.json").read_text(encoding="utf-8"))
        entry = schema["$defs"]["verification"]
        baseline = {
            "support": "registry-estimate",
            "behavior": "not-individually-verified",
            "accessibility": "not-audited",
            "sources": [],
        }
        validate(baseline, entry, schema["$defs"])
        with self.assertRaises(SchemaError):
            validate({**baseline, "behavior": "WCAG AA certified"}, entry, schema["$defs"])


    def test_evidence_overlay_requires_scoped_provenance(self):
        stamp = date.today().isoformat()
        record = {
            "ds-18": {
                "behavior": "browser-tested",
                "accessibility": "not-audited",
                "accessibilityNotes": "Hover dismissal has not been reviewed.",
                "dependencies": ["Native focus and hover"],
                "fallback": "Keep content available without hover.",
                "evidence": [{
                    "kind": "behavior",
                    "url": "https://github.com/FullThrottle83/design-spells/actions/runs/36175057793",
                    "checkedAt": stamp,
                    "note": "Scoped tooltip focus and hover regression.",
                    "browser": "firefox",
                    "version": "test-fixture",
                }],
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "verification.json"
            source.write_text(json.dumps(record), encoding="utf-8")
            loaded = load_verification_overrides(source)
        state = verification_for_spell("ds-18", loaded)
        self.assertEqual(state["behavior"], "browser-tested")
        self.assertEqual(state["support"], "registry-estimate")
        self.assertEqual(state["accessibility"], "not-audited")
        self.assertEqual(state["sources"], [record["ds-18"]["evidence"][0]["url"]])
        self.assertEqual(state["dependencies"], ["Native focus and hover"])
        schema = json.loads((PUBLIC / "spells.schema.json").read_text(encoding="utf-8"))
        from test_build import validate
        validate(state, schema["$defs"]["verification"], schema["$defs"])

    def test_unsupported_promotions_and_bad_evidence_are_rejected(self):
        stamp = date.today().isoformat()
        evidence = {
            "kind": "behavior",
            "url": "https://example.org/run/1",
            "checkedAt": stamp,
            "note": "A specific observed behavior.",
            "browser": "webkit",
            "version": "fixture",
        }
        bad_overrides = [
            {"support": "source-checked"},
            {"behavior": "browser-tested", "evidence": [{**evidence, "browser": ""}]},
            {"behavior": "browser-tested", "evidence": [{k: v for k, v in evidence.items() if k != "version"}]},
            {"behavior": "browser-tested", "evidence": [{**evidence, "url": "http://example.org"}]},
            {"behavior": "browser-tested", "evidence": [{**evidence, "checkedAt": "not-a-date"}]},
            {"accessibility": "reviewed", "evidence": [evidence]},
            {"accessibility": "reviewed", "evidence": [{**evidence, "kind": "accessibility"}]},
            {"sources": ["https://example.org"]},
        ]
        for override in bad_overrides:
            with self.subTest(override=override), self.assertRaises(ValueError):
                verification_for_spell("ds-18", {"ds-18": override})


if __name__ == "__main__":
    unittest.main()
