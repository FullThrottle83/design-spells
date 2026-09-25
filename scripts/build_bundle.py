"""Build small, honest copy/paste integration documents from canonical spell data.

This is not the hosted demo fixture or a Tailwind compilation. Do not copy the
catalogue's global styles into every component. Unknown project variables are
reported instead of being silently treated as resolved dependencies.
"""

from __future__ import annotations

import html
import re

VAR_RE = re.compile(r"var\(\s*(--[\w-]+)")
DECL_RE = re.compile(r"(?<![\w-])(--[\w-]+)\s*:\s*([^;]+);")
CSS_COMMENTS = re.compile(r"/\*.*?\*/", re.S)
ROOT_SCROLL_IDS = {"ds-43", "ds-47"}
DOCUMENT_EFFECT_IDS = {"ds-14", "ds-143"}


def resolve_tokens(css: str, markup: str, document_tokens: str) -> tuple[dict[str, str], list[str]]:
    """Select used shared tokens recursively, respecting locally authored vars."""
    shared = dict(DECL_RE.findall(document_tokens))
    authored = CSS_COMMENTS.sub("", css) + "\n" + markup
    local = {name for name, _ in DECL_RE.findall(authored)}
    required: set[str] = set()
    unresolved: set[str] = set()
    pending = list(dict.fromkeys(VAR_RE.findall(authored)))
    while pending:
        name = pending.pop(0)
        if name in local or name in required or name in unresolved:
            continue
        if name not in shared:
            unresolved.add(name)
            continue
        required.add(name)
        pending.extend(VAR_RE.findall(shared[name]))
    return ({name: value.strip() for name, value in shared.items() if name in required},
            sorted(unresolved))


def render_bundle(spell: dict, document_tokens: str) -> str:
    """Produce a copyable HTML document without the catalogue's demo stylesheet."""
    sid = spell["id"]
    authored = str(spell.get("html") or "").strip()
    markup = authored or str(spell.get("previewHtml") or "").strip()
    css = str(spell.get("css") or "").strip()
    selected, unresolved = resolve_tokens(css, markup, document_tokens)

    root = ""
    if selected:
        declarations = ["  color-scheme: light dark;"] if any(
            "light-dark(" in value for value in selected.values()
        ) else []
        declarations.extend(f"  {name}: {value};" for name, value in selected.items())
        root = ":root {\n" + "\n".join(declarations) + "\n}\n\n"

    scroll_preset = ""
    if sid in ROOT_SCROLL_IDS:
        scroll_preset = ("/* Opt-in root scroll-state required for this spell. */\n"
                         "html { container-type: scroll-state; overflow: auto; }\n\n")

    unknown_note = ""
    if unresolved:
        unknown_note = ("/* Project variables not defined in this spell or shared tokens: "
                        + ", ".join(unresolved)
                        + ". Define them in your project or verify the var() fallbacks. */\n")
    fixture_note = ("<!-- Authored markup from README.md. -->"
                    if authored else
                    "<!-- Demo fixture, NOT authored component markup. Adapt it to your project. -->")
    document_note = ""
    if sid in DOCUMENT_EFFECT_IDS:
        document_note = (
            "<!-- Document-level effect: this single example is NOT proof of the behavior. "
            "Use the runnable download; ds-14 needs both linked HTML documents. -->\n"
        )
    return (
        "<!doctype html>\n"
        f"<!-- Design Spells {sid}: integration source, not the styled catalogue demo. -->\n"
        "<!-- The effect may require modern CSS support. External media/URLs are not bundled. -->\n"
        + document_note
        + '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        + '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        + f"<title>{html.escape(str(spell['title']), quote=True)} — Design Spells</title>\n"
        + "<style>\n"
        + root + scroll_preset + unknown_note + css + "\n"
        + "</style>\n</head>\n<body>\n"
        + fixture_note + "\n" + (markup or "<!-- Supply markup matching the CSS selectors. -->")
        + "\n</body>\n</html>\n"
    )
