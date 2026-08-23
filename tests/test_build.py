#!/usr/bin/env python3
"""Deterministic checks on the generated catalogue.

README.md is the source of truth; scripts/build.py parses it into
public/spells.js (the browser payload) and public/spells.json (the
machine-readable copy described by public/spells.schema.json).

Everything here is mechanical: rebuild from README in a scratch copy of the
repo and compare, then assert the invariants the site and the MCP server
rely on. No browser, no network.

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from scripts.build import rewrite_preview_css

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SPELLS_JSON = PUBLIC / "spells.json"
SPELLS_JS = PUBLIC / "spells.js"
SCHEMA_PATH = PUBLIC / "spells.schema.json"


def load_catalogue() -> dict:
    return json.loads(SPELLS_JSON.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- json schema

# public/spells.schema.json only uses a handful of draft 2020-12 keywords, so
# rather than pull in a dependency this validates exactly those. Anything it
# does not recognise is an error, not a silent skip — a schema that grows a new
# keyword must fail loudly here instead of quietly stopping being validated.
ANNOTATION_KEYWORDS = {"$schema", "$id", "title", "description"}
SUPPORTED_KEYWORDS = ANNOTATION_KEYWORDS | {
    "type", "required", "properties", "additionalProperties",
    "enum", "items", "$ref", "minimum", "$defs",
}

JSON_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}


class SchemaError(AssertionError):
    pass


def validate(instance, schema: dict, defs: dict, path: str = "$") -> None:
    unknown = set(schema) - SUPPORTED_KEYWORDS
    if unknown:
        raise SchemaError(
            f"{path}: schema uses keywords this validator does not implement: "
            f"{sorted(unknown)} — extend tests/test_build.py rather than "
            f"leaving them unchecked"
        )

    if "$ref" in schema:
        ref = schema["$ref"]
        prefix = "#/$defs/"
        if not ref.startswith(prefix):
            raise SchemaError(f"{path}: only local #/$defs/ refs are supported, got {ref!r}")
        return validate(instance, defs[ref[len(prefix):]], defs, path)

    if "type" in schema:
        expected = schema["type"]
        py = JSON_TYPES[expected]
        # bool is a subclass of int in Python; JSON does not agree.
        if isinstance(instance, bool) and expected in {"integer", "number"}:
            raise SchemaError(f"{path}: expected {expected}, got boolean")
        if not isinstance(instance, py):
            raise SchemaError(f"{path}: expected {expected}, got {type(instance).__name__}")

    if "enum" in schema and instance not in schema["enum"]:
        raise SchemaError(f"{path}: {instance!r} is not one of {schema['enum']}")

    if "minimum" in schema and instance < schema["minimum"]:
        raise SchemaError(f"{path}: {instance} is below minimum {schema['minimum']}")

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                raise SchemaError(f"{path}: missing required property {key!r}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = set(instance) - set(props)
            if extra:
                raise SchemaError(f"{path}: unexpected properties {sorted(extra)}")
        for key, value in instance.items():
            if key in props:
                validate(value, props[key], defs, f"{path}.{key}")

    if isinstance(instance, list) and "items" in schema:
        for i, item in enumerate(instance):
            validate(item, schema["items"], defs, f"{path}[{i}]")


# ------------------------------------------------------------------- helpers

def strip_css_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def class_names(css: str) -> list[str]:
    return re.findall(r"(?<![:\w.-])\.([a-zA-Z][\w-]*)", strip_css_comments(css))


def markup_classes(html: str) -> set[str]:
    groups = re.findall(r"""class=["']([^"']*)["']""", html)
    return {c for group in groups for c in group.split()}


def is_explanatory_only(html: str) -> bool:
    """True for previews that are just a `.demo-note` telling the reader why
    the effect cannot be shown on screen (print stylesheets, cross-document
    view transitions). Those have no markup to exercise, by design."""
    stripped = re.sub(r"""<p class=["']demo-note["']>.*?</p>""", "", html, flags=re.S)
    return not re.search(r"<[a-zA-Z]", stripped)


class BuildOutputTest(unittest.TestCase):
    """The committed artefacts are exactly what README.md produces."""

    def test_rebuild_from_readme_reproduces_committed_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = Path(tmp)
            shutil.copy2(ROOT / "README.md", sandbox / "README.md")
            shutil.copytree(ROOT / "scripts", sandbox / "scripts")
            (sandbox / "public").mkdir()

            result = subprocess.run(
                [sys.executable, "scripts/build.py"],
                cwd=sandbox, capture_output=True, text=True,
            )
            self.assertEqual(
                result.returncode, 0,
                f"scripts/build.py failed:\n{result.stdout}\n{result.stderr}",
            )

            for name in ("spells.js", "spells.json"):
                with self.subTest(artefact=name):
                    rebuilt = (sandbox / "public" / name).read_bytes()
                    committed = (PUBLIC / name).read_bytes()
                    self.assertEqual(
                        rebuilt, committed,
                        f"public/{name} is stale — README.md changed without "
                        f"re-running `python3 scripts/build.py`",
                    )

    def test_build_is_idempotent(self):
        """Two runs from the same README produce byte-identical output."""
        outputs = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as tmp:
                sandbox = Path(tmp)
                shutil.copy2(ROOT / "README.md", sandbox / "README.md")
                shutil.copytree(ROOT / "scripts", sandbox / "scripts")
                (sandbox / "public").mkdir()
                subprocess.run(
                    [sys.executable, "scripts/build.py"],
                    cwd=sandbox, capture_output=True, text=True, check=True,
                )
                outputs.append((sandbox / "public" / "spells.json").read_bytes())
        self.assertEqual(outputs[0], outputs[1], "build.py output is not deterministic")

    def test_spells_js_payload_matches_spells_json(self):
        js = SPELLS_JS.read_text(encoding="utf-8")
        match = re.search(r"window\.DESIGN_SPELLS = ([\s\S]+);\n$", js)
        self.assertIsNotNone(match, "public/spells.js does not assign window.DESIGN_SPELLS")
        payload = json.loads(match.group(1))

        doc = load_catalogue()
        doc.pop("$schema", None)
        self.assertEqual(
            payload, doc,
            "public/spells.js and public/spells.json describe different catalogues",
        )


class SchemaTest(unittest.TestCase):
    """public/spells.json satisfies its own published contract."""

    def setUp(self):
        self.doc = load_catalogue()
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_catalogue_validates_against_schema(self):
        validate(self.doc, self.schema, self.schema.get("$defs", {}))

    def test_schema_reference_points_at_the_published_schema(self):
        self.assertEqual(
            self.doc.get("$schema"), self.schema["$id"],
            "spells.json $schema does not match the schema's own $id",
        )

    def test_total_matches_the_number_of_spells(self):
        self.assertEqual(self.doc["total"], len(self.doc["spells"]))

    def test_typescript_and_schema_have_bidirectional_field_parity(self):
        types = (ROOT / "schema" / "spells.d.ts").read_text(encoding="utf-8")

        def interface_fields(name):
            match = re.search(
                rf"export interface {name}\s*{{([\s\S]*?)^}}",
                types,
                re.M,
            )
            self.assertIsNotNone(match, f"missing TypeScript interface {name}")
            return set(re.findall(r"^\s{2}([A-Za-z]\w*)\??\s*:", match.group(1), re.M))

        spell_schema = self.schema["$defs"]["spell"]
        self.assertEqual(
            interface_fields("Spell"),
            set(spell_schema["required"]),
            "Spell fields differ between JSON Schema and TypeScript",
        )
        self.assertEqual(
            interface_fields("BrowserSupport"),
            set(spell_schema["properties"]["browsers"]["properties"]),
            "BrowserSupport fields differ between JSON Schema and TypeScript",
        )

    def test_typescript_and_schema_have_enum_parity(self):
        types = (ROOT / "schema" / "spells.d.ts").read_text(encoding="utf-8")

        def union_values(name):
            match = re.search(rf"export type {name}\s*=([\s\S]*?);", types)
            self.assertIsNotNone(match, f"missing TypeScript union {name}")
            return set(re.findall(r'"([^"]+)"', match.group(1)))

        spell = self.schema["$defs"]["spell"]["properties"]
        self.assertEqual(union_values("Status"), set(spell["status"]["enum"]))
        self.assertEqual(union_values("StatusLabel"), set(spell["statusLabel"]["enum"]))
        self.assertEqual(union_values("JsNeed"), set(spell["jsNeed"]["enum"]))
        self.assertEqual(union_values("JsLabel"), set(spell["jsLabel"]["enum"]))
        self.assertEqual(
            union_values("PreviewActionKind"),
            set(self.schema["$defs"]["previewAction"]["properties"]["kind"]["enum"]),
        )


class SpellInvariantTest(unittest.TestCase):
    """Guarantees every consumer (site, MCP server, agents) keys off."""

    def setUp(self):
        self.spells = load_catalogue()["spells"]

    def test_ids_are_unique(self):
        dupes = [k for k, n in Counter(s["id"] for s in self.spells).items() if n > 1]
        self.assertEqual(dupes, [], f"duplicate spell ids: {dupes}")

    def test_numbers_are_unique(self):
        dupes = [k for k, n in Counter(s["number"] for s in self.spells).items() if n > 1]
        self.assertEqual(dupes, [], f"duplicate spell numbers: {dupes}")

    def test_id_is_derived_from_number(self):
        wrong = [s["id"] for s in self.spells if s["id"] != f"ds-{s['number']}"]
        self.assertEqual(wrong, [], f"ids out of sync with numbers: {wrong}")

    def test_identifying_fields_are_never_blank(self):
        # note/description/html are legitimately empty for some spells;
        # everything below is what the UI and the MCP server render directly.
        required = [
            "id", "number", "title", "section", "category", "rawCategory",
            "css", "previewHtml", "previewCss", "feature", "supportNote",
        ]
        blank = [
            f"{s['id']}.{field}"
            for s in self.spells for field in required
            if not str(s[field]).strip()
        ]
        self.assertEqual(blank, [], f"blank fields: {blank}")

    def test_status_label_agrees_with_status(self):
        wrong = [
            s["id"] for s in self.spells
            if s["status"] != s["statusLabel"].lower()
        ]
        self.assertEqual(wrong, [], f"status/statusLabel mismatch: {wrong}")

    def test_js_label_agrees_with_js_need(self):
        expected = {"none": "0 JS", "markup": "Markup"}
        wrong = [
            s["id"] for s in self.spells
            if expected[s["jsNeed"]] != s["jsLabel"]
        ]
        self.assertEqual(wrong, [], f"jsNeed/jsLabel mismatch: {wrong}")

    def test_progressive_status_matches_browser_support(self):
        """Every status is a deterministic projection of browser support."""
        for spell in self.spells:
            with self.subTest(spell=spell["id"]):
                levels = list(spell["browsers"].values())
                missing = levels.count("no")
                if missing >= 2:
                    expected = "progressive"
                elif missing == 1 or "partial" in levels:
                    expected = "newer"
                else:
                    expected = "baseline"
                self.assertEqual(
                    spell["status"],
                    expected,
                    f"{spell['id']} status disagrees with {spell['browsers']}",
                )

    def test_categories_are_known_to_the_app(self):
        app = (PUBLIC / "app.js").read_text(encoding="utf-8")
        block = re.search(r"const CAT_ORDER = \[([\s\S]*?)\];", app)
        self.assertIsNotNone(block, "could not find CAT_ORDER in public/app.js")
        known = set(re.findall(r'"([^"]+)"', block.group(1)))
        used = {s["category"] for s in self.spells}
        unknown = sorted(used - known)
        self.assertEqual(
            unknown, [],
            f"categories missing from CAT_ORDER in app.js (they sort last): {unknown}",
        )


class PreviewInvariantTest(unittest.TestCase):
    """The sandbox contract: previews are self-contained and shadow-DOM safe."""

    def setUp(self):
        self.spells = load_catalogue()["spells"]

    def test_preview_css_has_no_document_level_selectors(self):
        """rewrite_preview_css() maps :root/html/body onto the shadow :host.

        Anything left behind cannot match inside a shadow root, so the spell
        silently renders unstyled.
        """
        leaked = []
        for spell in self.spells:
            if spell.get("previewEnvironment") == "document":
                continue
            css = strip_css_comments(spell["previewCss"])
            if re.search(r"(?<![\w.#-])(:root\b|\bhtml\b|\bbody\b)(?![\w-])", css):
                leaked.append(spell["id"])
        self.assertEqual(leaked, [], f"previewCss still targets the document: {leaked}")

    def test_preview_rewriter_only_changes_selector_preludes(self):
        source = (
            '/* body :root html */\n'
            '.copy { content: "body :root html"; --label: body; }\n'
            'html > body .copy { color: red; }\n'
        )
        rewritten = rewrite_preview_css(source)
        self.assertIn('/* body :root html */', rewritten)
        self.assertIn('content: "body :root html"', rewritten)
        self.assertIn("--label: body", rewritten)
        self.assertIn(":host > .stage .copy", rewritten)
        self.assertNotIn(":host > :host", rewritten)

    def test_preview_rewriter_handles_nested_rule_lists(self):
        source = (
            "@media (width > 10px) { "
            "body > .card { color: red; } "
            ".card { content: 'body'; } }"
        )
        rewritten = rewrite_preview_css(source)
        self.assertIn(".stage > .card", rewritten)
        self.assertIn("content: 'body'", rewritten)

    def test_preview_html_has_no_remote_assets(self):
        """Previews must render offline — images are inlined as data: URIs."""
        offenders = []
        for spell in self.spells:
            for url in re.findall(r'(?:src|href)="([^"]+)"', spell["previewHtml"]):
                if url.startswith(("http://", "https://", "//")):
                    # target="_blank" demos deliberately link out; only assets
                    # (things the browser fetches to render) matter here.
                    continue
                if re.search(r"\.(jpg|jpeg|png|gif|webp|avif|svg)$", url, re.I):
                    offenders.append(f"{spell['id']} → {url}")
        self.assertEqual(offenders, [], f"previews reference local files that are not served: {offenders}")

    def test_preview_css_has_no_remote_assets(self):
        """Same rule for background images — a url('/hero-bg.jpg') 404s in the
        sandbox and the layer it paints comes out empty."""
        # Inline SVG data URIs contain url(%23gradient) references of their
        # own, so drop them whole before looking for anything fetchable.
        data_url = re.compile(r"""url\(\s*(?:"data:[^"]*"|'data:[^']*')\s*\)""")
        offenders = []
        for spell in self.spells:
            css = data_url.sub("", spell["previewCss"])
            for url in re.findall(r"""url\(\s*['"]?([^)'"]+)""", css):
                offenders.append(f"{spell['id']} → {url}")
        self.assertEqual(offenders, [], f"previewCss loads assets that are not served: {offenders}")

    def test_preview_html_is_not_empty(self):
        empty = [s["id"] for s in self.spells if not s["previewHtml"].strip()]
        self.assertEqual(empty, [], f"spells with no preview markup: {empty}")

    def test_preview_css_targets_something_in_the_preview_markup(self):
        """A preview whose markup matches none of the spell's own class
        selectors renders the sandbox default, not the spell."""
        orphans = []
        for spell in self.spells:
            classes = set(class_names(spell["previewCss"]))
            if not classes:
                continue  # element/pseudo-only spell, nothing to correlate
            if is_explanatory_only(spell["previewHtml"]):
                continue
            if not (classes & markup_classes(spell["previewHtml"])):
                orphans.append(f"{spell['id']} ({spell['title']})")
        self.assertEqual(
            orphans, [],
            f"preview markup matches none of the spell's classes: {orphans}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
