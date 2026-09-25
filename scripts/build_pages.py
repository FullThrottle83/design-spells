#!/usr/bin/env python3
"""Generate stable, independently navigable, zero-script spell docs and demos.

The canonical source remains README.md, parsed by scripts/build.py. Pages are
static output, not an alternative data source.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from build import DOCUMENT_TOKENS, rewrite_preview_assets

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SITE_URL = "https://design-spells.hultsan20.workers.dev"
VALID_ID = re.compile(r"ds-(?:[1-9]\d*|bonus)\Z")
SCROLL_DEMOS = {"ds-17", "ds-36", "ds-43", "ds-47", "ds-65", "ds-126"}
BROWSERS = (("chrome", "Chrome"), ("edge", "Edge"), ("firefox", "Firefox"), ("safari", "Safari"))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def write_page(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def render_doc(spell: dict) -> str:
    sid = spell["id"]
    title = esc(spell["title"])
    description = esc(spell["description"])
    css = esc(spell["css"].strip())
    authored_html = spell["html"].strip()
    example_html = esc(authored_html or spell["previewHtml"].strip())
    fixture_note = (
        "<p class='note'>This is demonstration fixture markup; the technique does not require a specific HTML structure.</p>"
        if not authored_html else ""
    )
    support = "".join(
        f"<li><strong>{name}</strong><span>{esc(spell['browsers'][key])}</span></li>"
        for key, name in BROWSERS
    )
    instruction = spell.get("previewAction", {}).get("hint", "")
    instruction_html = f"<p class='note'>{esc(instruction)}</p>" if instruction else ""
    canonical = f"{SITE_URL}/spells/{sid}/"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>{title} — Design Spells</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title} — Design Spells">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  <link rel="stylesheet" href="/spell-pages.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-head">
    <a class="brand" href="/">Design Spells</a>
    <nav aria-label="Breadcrumb"><a href="/">Catalogue</a><span aria-hidden="true">/</span><span>{esc(sid)}</span></nav>
    <a href="https://github.com/FullThrottle83/design-spells">GitHub ↗</a>
  </header>
  <main id="main" class="shell">
    <p class="eyebrow">{esc(sid)} / {esc(spell["category"])} / {esc(spell["jsLabel"])}</p>
    <h1>{title}</h1>
    <p class="lede">{description}</p>
    <p class="note">Zero JavaScript in this example. The catalogue has optional enhancements.</p>
    <section aria-labelledby="demo-title">
      <div class="section-head"><h2 id="demo-title">Live demo</h2><a class="action" href="/play/{sid}/">Open standalone demo ↗</a></div>
      {instruction_html}
      <iframe title="Isolated demonstration: {title}" src="/play/{sid}/" loading="lazy" sandbox="allow-same-origin"></iframe>
    </section>
    <section aria-labelledby="source-title">
      <h2 id="source-title">Complete source</h2>
      <p class="note">Select the source and use your browser's copy command. Shared design tokens are supplied by the demo environment, not included in these snippets.</p>
      <h3>HTML</h3>
      {fixture_note}
      <pre tabindex="0"><code>{example_html}</code></pre>
      <h3>CSS</h3>
      <pre tabindex="0"><code>{css}</code></pre>
    </section>
    <section aria-labelledby="support-title">
      <h2 id="support-title">Browser-support guidance</h2>
      <p class="note">Project category: {esc(spell["statusLabel"])}. This registry is a dated reference, not a live proof of behavior.</p>
      <ul class="browser-list">{support}</ul>
      <p class="note">{esc(spell["supportNote"])}</p>
    </section>
    <footer><a href="/">Back to catalogue</a><span>Built from canonical README.md</span></footer>
  </main>
</body>
</html>"""


def render_play(spell: dict, next_page: bool = False) -> str:
    sid = spell["id"]
    title = esc(spell["title"])
    css = rewrite_preview_assets(spell["css"])
    raw_html = spell["previewHtml"] or spell["html"] or "<p>CSS-only example.</p>"
    hint = spell.get("previewAction", {}).get("hint", "")
    hint_html = f"<p class='demo-hint'>{esc(hint)}</p>" if hint else ""
    extra = ""
    if sid == "ds-14":
        href = "../" if next_page else "next/"
        label = "Return to page A" if next_page else "Navigate to page B"
        heading = "Page B" if next_page else "Page A"
        raw_html = f'<article class="page-transition"><h1>{heading}</h1><p>Navigate between real documents to observe the transition.</p><a href="{href}">{label} →</a></article>'
    elif sid == "ds-143":
        raw_html = '<article class="print-example"><h1>A printable article</h1><p>Open your browser print preview to inspect the stylesheet.</p><p><a href="https://example.com">A sample external reference</a></p></article>'
    elif sid in SCROLL_DEMOS:
        extra = ('<div class="scroll-content"><h2>Scroll through the document</h2>'
                 '<p>Root-document scroll effects cannot be meaningfully tested in a tiny isolated card.</p></div>'
                 '<div class="scroll-content"><p>End of the scrolling demonstration.</p></div>')
    stage = raw_html + extra if sid in SCROLL_DEMOS else f'<div class="stage">{raw_html}</div>'
    page_css = """
    *,*::before,*::after {box-sizing:border-box}
    html {scroll-behavior:smooth}
    body {display:block; min-height:100dvh; padding:0}
    .stage {position:relative;display:grid;place-items:center;min-height:280px;padding:2rem;width:100%;isolation:isolate}
    .stage > * {max-width:100%}
    .stage:has(details) {align-items:start}
    .demo-hint {padding:.7rem 1rem;color:var(--color-text-muted);font-size:.875rem}
    .scroll-content {min-height:110vh;display:grid;place-items:center;align-content:center;padding:2rem}
    .page-transition {padding:clamp(2rem,7vw,6rem);max-width:60rem;margin:auto}
    .page-transition a {display:inline-block;margin-top:2rem}
    .print-example {max-width:42rem;margin:3rem auto;line-height:1.7;padding:1rem}
    @media (prefers-reduced-motion:reduce) {html {scroll-behavior:auto}}
    """
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <meta name="robots" content="noindex,follow">
  <title>Demo: {title} — Design Spells</title>
  <style>{DOCUMENT_TOKENS}\n{page_css}\n{css}</style>
</head>
<body>
  {stage}
  {hint_html}
</body>
</html>"""


def build_pages(catalogue: dict) -> None:
    sitemap = [f"{SITE_URL}/"]
    for spell in catalogue["spells"]:
        sid = spell["id"]
        if not VALID_ID.fullmatch(sid):
            raise ValueError(f"Unsafe spell ID for a file path: {sid!r}")
        write_page(PUBLIC / "spells" / sid / "index.html", render_doc(spell))
        write_page(PUBLIC / "play" / sid / "index.html", render_play(spell))
        if sid == "ds-14":
            write_page(PUBLIC / "play" / sid / "next" / "index.html", render_play(spell, next_page=True))
        sitemap.append(f"{SITE_URL}/spells/{sid}/")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += "".join(f"  <url><loc>{xml_escape(url)}</loc></url>\n" for url in sitemap)
    xml += "</urlset>\n"
    write_page(PUBLIC / "sitemap.xml", xml)
    print(f"wrote {len(catalogue['spells'])} static spell pages and isolated demos")


if __name__ == "__main__":
    build_pages(json.loads((PUBLIC / "spells.json").read_text(encoding="utf-8")))
