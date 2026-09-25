"""Evidence contract regression tests: syntax/support lookup is not an audit."""

import json
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
