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
from build_bundle import ROOT_SCROLL_IDS, render_bundle
from showcase_fixtures import HTML as SCENE_HTML, HINTS, CSS as SCENE_CSS, COMMON_CSS, scene_html

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SITE_URL = "https://design-spells.hultsan20.workers.dev"
VALID_ID = re.compile(r"ds-(?:[1-9]\d*|bonus)\Z")
SCROLL_DEMOS = {"ds-17", "ds-36", "ds-43", "ds-47", "ds-65", "ds-126"}
SCROLL_ENTRY_DEMOS = {"ds-8", "ds-72", "ds-125", "ds-145"}
# A curated comparison, not a claim that all 150 CSS features have a
# meaningful single-frame before/after state. Keep authored spell CSS intact.
COMPARE_NOTES = {
    "ds-1": "Hover or keyboard-focus both buttons. The right button gains a moving highlight.",
    "ds-2": "Press and hold each button. Only the right button shrinks while pressed.",
    "ds-5": "Hover Overview in both previews. The right underline grows across the link.",
    "ds-6": "Use Tab to focus each input. The right input gets a layered focus glow.",
    "ds-7": "Hover or keyboard-focus each star. The right star changes color and grows.",
    "ds-18": "Hover or focus each button. The right one reveals a tooltip above it.",
    "ds-24": "Hover or focus each Docs link. The right arrow moves up and right.",
    "ds-38": "Hover, then press each button. The right button changes its background.",
}
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
        if not authored_html else ("<!-- Canonical authored markup. -->" if sid in {"ds-48", "ds-49", "ds-50"} else "")
    )
    support = "".join(
        f"<li><strong>{name}</strong><span>{esc(spell['browsers'][key])}</span></li>"
        for key, name in BROWSERS
    )
    instruction = HINTS.get(sid, spell.get("previewAction", {}).get("hint", ""))
    instruction_html = f"<p class='note'>{esc(instruction)}</p>" if instruction else ""
    if sid in SCROLL_ENTRY_DEMOS:
        instruction_html += '<p class="note">This entry animation needs a scroll runway. Scroll inside the iframe or open the full-page demo, then move down to the effect. The spell CSS has not been accelerated.</p>'
    elif sid == "ds-44":
        instruction_html += "<p class=\"note\">Scroll inside the iframe or open the full-page demo. The preview-only runway lets the sticky navigation reach its top inset; supporting browsers then apply the authored shadow. Other browsers retain the sticky navigation without that enhancement.</p>"
    elif sid == "ds-45":
        instruction_html += "<p class=\"note\">Scroll horizontally in the carousel or use the arrow keys after focusing it. On supporting browsers the snapped card becomes fully opaque and returns to its original scale. Other browsers retain native scroll snapping without spotlight styling.</p>"
    elif sid == "ds-46":
        instruction_html += "<p class=\"note\">Use the native Fit content checkbox to compare an overflowing row with one that wraps. The overflow arrow follows actual scrollability in supporting browsers; horizontal scrolling and readable labels remain available without the enhancement. These labels are a visual fixture, not working tab controls.</p>"
    elif sid == "ds-35":
        instruction_html += '<p class="note">Use the native Light / Dark controls inside the demo to compare both color schemes without changing the spell CSS.</p>'
    elif sid == "ds-9":
        instruction_html += '<p class="note">This animation happens on page load. Use Replay in the standalone demo to reload it without JavaScript.</p>'
    elif sid == "ds-143":
        instruction_html += '<p class="note">Print styles are visible only in print media. Open the standalone demo, then use your browser’s Print preview (Ctrl+P or Cmd+P).</p>'
    download_note = '<p class="note">This cross-document transition also needs <a href="/download/ds-14-next.html" download="ds-14-next.html">page B (HTML) ↓</a>; save both files together.</p>' if sid == "ds-14" else ""
    effect_iframe = f'<iframe title="Isolated demonstration: {title}" src="/play/{sid}/" loading="lazy" sandbox="allow-same-origin"></iframe>'
    if sid in COMPARE_NOTES:
        demo_preview = (
            '<div class="demo-compare">'
            f'<div class="demo-compare__item"><h3>Base fixture</h3><iframe title="Baseline without spell CSS: {title}" src="/play/{sid}/before/" loading="lazy" sandbox="allow-same-origin"></iframe></div>'
            f'<div class="demo-compare__item"><h3>With spell CSS</h3>{effect_iframe}</div>'
            '</div>'
            f'<p class="note demo-compare__guide">{esc(COMPARE_NOTES[sid])} Both use identical markup and shared demo styling; only the right includes this spell’s CSS.</p>'
        )
    else:
        demo_preview = effect_iframe
    evidence = spell["verification"]
    evidence_note = (
        f"Support: {esc(evidence['support'])}; "
        f"behavior: {esc(evidence['behavior'])}; "
        f"accessibility: {esc(evidence['accessibility'])}."
    )
    evidence_details = ""
    if evidence.get("evidence"):
        observations = "".join(
            f'<li>{esc(item["kind"])} ({esc(item["checkedAt"])}'
            f'{", " + esc(item["browser"]) + " " + esc(item["version"]) if "browser" in item else ""}): '
            f'{esc(item["note"])} — <a href="{esc(item["url"])}">Source</a></li>'
            for item in evidence["evidence"]
        )
        evidence_details += f'<h3>Verification evidence</h3><ul>{observations}</ul>'
    if evidence.get("dependencies"):
        evidence_details += '<p class="note">Dependencies: ' + esc(", ".join(evidence["dependencies"])) + '</p>'
    if evidence.get("fallback"):
        evidence_details += '<p class="note">Fallback: ' + esc(evidence["fallback"]) + '</p>'
    if evidence.get("accessibilityNotes"):
        evidence_details += '<p class="note">Accessibility review: ' + esc(evidence["accessibilityNotes"]) + '</p>'
    bundle_copy = (
        f'<button class="action bundle-copy" type="button" data-copy-bundle="{sid}" hidden>Copy integration bundle</button>'
        if sid not in {"ds-14", "ds-143"} else ""
    )
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
    <p class="note">The spell and its demo use zero JavaScript. Optional copy controls do not affect the example.</p>
    <section aria-labelledby="demo-title">
      <div class="section-head"><h2 id="demo-title">Live demo</h2><a class="action" href="/play/{sid}/">Open standalone demo ↗</a><a class="action" href="/download/{sid}.html" download="{sid}.html">Download runnable HTML ↓</a></div>
      {instruction_html}
      {download_note}
      {demo_preview}
    </section>
    <section aria-labelledby="source-title">
      <h2 id="source-title">Complete source</h2>
      <div class="bundle-actions">
        <a class="action" href="/bundle/{sid}.txt" data-bundle-source>View integration source ↗</a>
        {bundle_copy}
        <span class="bundle-status" role="status" aria-live="polite" data-bundle-status></span>
      </div>
      <p class="note">Integration source includes only referenced shared tokens and authored HTML (or a labelled demo fixture); project variables and external media may need attention. Raw snippets below omit shared base tokens. Download runnable HTML above for the complete styled demo.</p>
      <h3>HTML</h3>
      {fixture_note}
      <pre tabindex="0"><code>{example_html}</code></pre>
      <h3>CSS</h3>
      <pre tabindex="0"><code>{css}</code></pre>
    </section>
    <section aria-labelledby="support-title">
      <h2 id="support-title">Browser-support guidance</h2>
      <p class="note">Project category: {esc(spell["statusLabel"])}. This hand-maintained registry is a dated estimate, not proof of browser behavior.</p>
      <p class="note">{evidence_note}</p>{evidence_details}
      <ul class="browser-list">{support}</ul>
      <p class="note">{esc(spell["supportNote"])}</p>
    </section>
    <footer><a href="/">Back to catalogue</a><span>Built from canonical README.md</span></footer>
  </main>
  <script src="/spell-copy.js" defer></script>
</body>
</html>"""


def render_play(spell: dict, next_page: bool = False, baseline: bool = False) -> str:
    sid = spell["id"]
    title = esc(spell["title"])
    css = "" if baseline else rewrite_preview_assets(spell["css"])
    if sid in ROOT_SCROLL_IDS and not baseline:
        # The hosted root-scroll demos need the same opt-in prerequisite
        # as their integration bundles; it must not leak into other spells.
        css = "html { container-type: scroll-state; overflow: auto; }\n" + css
    raw_html = spell["previewHtml"] or spell["html"] or "<p>CSS-only example.</p>"
    if sid == "ds-37":
        raw_html = SCENE_HTML["37"]
    if sid == "ds-35":
        # Preview-only scheme controls: keep the source CSS and integration bundle unchanged.
        css += """
html:has(#scheme-light:checked) { color-scheme: light; }
html:has(#scheme-dark:checked) { color-scheme: dark; }
.demo-theme {display:flex;flex-wrap:wrap;gap:1rem;align-items:center;border:0;margin:1rem;padding:.75rem 1rem}
.demo-theme legend {font-weight:650}
.demo-theme label {display:inline-flex;gap:.4rem;min-block-size:44px;align-items:center;cursor:pointer}
"""
    elif sid in SCROLL_ENTRY_DEMOS:
        css += """
.scroll-entry__intro {min-block-size:100dvh;display:grid;place-content:center;justify-items:center;gap:1rem;text-align:center;padding:2rem;background:var(--color-bg)}
.scroll-entry__intro h1 {font-size:clamp(1.5rem,5vw,2.5rem);margin:0}
.scroll-entry__intro p {max-width:46ch;margin:0;color:var(--color-text-muted)}
.scroll-entry__intro a {display:inline-flex;min-block-size:44px;align-items:center}
.scroll-entry__tail {min-block-size:65dvh;display:grid;place-items:center;padding:2rem}
"""
    elif sid == "ds-44":
        # Demo-only scroll runway: never rewrite authored sticky CSS or its bundle.
        css += """
.sticky-demo { display: block; min-block-size: 190dvh; padding: 2rem; }
.sticky-demo__intro { margin: 0 0 6rem; max-inline-size: 36ch; color: var(--color-text-muted); }
.sticky-demo .toc { z-index: 1; max-inline-size: 28rem; margin-inline: auto; }
.sticky-demo .toc__inner { padding: 1rem; border-radius: var(--radius-md); }
.sticky-demo__runway { min-block-size: 150dvh; max-inline-size: 28rem; margin-inline: auto;
  padding-block-start: 3rem; color: var(--color-text-muted); }
"""
    elif sid == "ds-45":
        css += """
/* The scroller itself is keyboard-focusable in the hosted/downloaded fixture. */
.carousel:focus-visible { outline: 2px solid var(--color-primary); outline-offset: 2px; }
"""
        raw_html = raw_html.replace('class="carousel"', 'class="carousel" role="region" aria-label="Snapped cards" tabindex="0"', 1)
    elif sid == "ds-46":
        css += """
/* Demo-only conditions: the authored scroll-state rule above is unchanged. */
.overflow-demo { inline-size: 100%; max-inline-size: 32rem; }
.overflow-demo__toggle { display: inline-flex; align-items: center; gap: .6rem; min-block-size: 44px; margin-block-end: 1rem; cursor: pointer; }
.overflow-demo .tabs-wrap { inline-size: 100%; }
.overflow-demo:has(#overflow-fit:checked) .tabs-wrap > div:first-child {
  min-width: 0 !important;
  white-space: normal !important;
  flex-wrap: wrap;
  padding-inline-end: 0 !important;
}
.overflow-demo .fade-hint { position: sticky; inset-inline-end: 0; inline-size: 2rem; margin-inline-start: auto; text-align: center; }
"""
        raw_html = raw_html.replace('class="tabs-wrap"', 'class="tabs-wrap" role="region" aria-label="Scrollable labels" tabindex="0"', 1)
    elif sid == "ds-9":
        css += ".demo-replay {padding:1rem;text-align:center}\n.demo-replay a {display:inline-flex;min-block-size:44px;align-items:center}\n"
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
    if sid in SCROLL_ENTRY_DEMOS:
        stage = (
            '<section class="scroll-entry__intro">'
            '<h1>Scroll to see this effect</h1>'
            '<p>The target starts below the fold so its view timeline has room to run.</p>'
            '<a href="#entry-effect">Jump to the effect ↓</a>'
            '</section>'
            f'<div class="stage scroll-entry__stage" id="entry-effect">{raw_html}</div>'
            '<div class="scroll-entry__tail">Continue scrolling to finish the animation.</div>'
        )
    elif sid == "ds-44":
        stage = (
            '<div class="stage sticky-demo">'
            '<p class="sticky-demo__intro">Scroll down until the navigation reaches the top edge.</p>'
            f"{raw_html}"
            '<div class="sticky-demo__runway"><p>Keep scrolling to see the navigation remain pinned.</p></div>'
            '</div>'
        )
    elif sid == "ds-46":
        stage = (
            '<div class="stage"><div class="overflow-demo">'
            '<label class="overflow-demo__toggle">'
            '<input type="checkbox" id="overflow-fit"> Fit content without horizontal scrolling'
            '</label>'
            f"{raw_html}"
            '</div></div>'
        )
    else:
        stage = raw_html + extra if sid in SCROLL_DEMOS else f'<div class="stage">{raw_html}</div>'
    if sid == "ds-35":
        stage = (
            '<fieldset class="demo-theme"><legend>Preview color scheme</legend>'
            '<label><input type="radio" id="scheme-light" name="demo-scheme" checked> Light</label>'
            '<label><input type="radio" id="scheme-dark" name="demo-scheme"> Dark</label>'
            '</fieldset>' + stage
        )
    elif sid == "ds-9":
        stage += '<p class="demo-replay"><a href="/play/ds-9/">Replay entrance animation ↻</a></p>'
    if sid in HINTS:
        stage = f'<div class="stage">{scene_html(sid, raw_html)}</div>'
        css += COMMON_CSS + SCENE_CSS[sid]
        hint_html = ""  # The contextual instruction lives inside the scene.
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
{"" if sid in HINTS else "  " + hint_html}
</body>
</html>"""


def render_download(spell: dict, next_page: bool = False) -> str:
    """The actual runnable demo, plus its required base tokens, in one HTML file.

    Unlike the raw CSS tab, this includes the demo fixture and the same document
    scaffolding the hosted demo uses. Remote media may still require a network.
    """
    page = render_play(spell, next_page=next_page)
    page = page.replace('  <meta name="robots" content="noindex,follow">', "")
    if spell["id"] == "ds-14":
        # Two real files are necessary for a cross-document transition offline.
        href = 'href="ds-14.html"' if next_page else 'href="ds-14-next.html"'
        page = page.replace('href="../"' if next_page else 'href="next/"', href)
    return page


def build_pages(catalogue: dict) -> None:
    sitemap = [f"{SITE_URL}/"]
    for spell in catalogue["spells"]:
        sid = spell["id"]
        if not VALID_ID.fullmatch(sid):
            raise ValueError(f"Unsafe spell ID for a file path: {sid!r}")
        write_page(PUBLIC / "spells" / sid / "index.html", render_doc(spell))
        write_page(PUBLIC / "play" / sid / "index.html", render_play(spell))
        if sid in COMPARE_NOTES:
            write_page(PUBLIC / "play" / sid / "before" / "index.html", render_play(spell, baseline=True))
        write_page(PUBLIC / "download" / f"{sid}.html", render_download(spell))
        write_page(PUBLIC / "bundle" / f"{sid}.txt", render_bundle(spell, DOCUMENT_TOKENS))
        if sid == "ds-14":
            write_page(PUBLIC / "play" / sid / "next" / "index.html", render_play(spell, next_page=True))
            write_page(PUBLIC / "download" / "ds-14-next.html", render_download(spell, next_page=True))
        sitemap.append(f"{SITE_URL}/spells/{sid}/")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += "".join(f"  <url><loc>{xml_escape(url)}</loc></url>\n" for url in sitemap)
    xml += "</urlset>\n"
    write_page(PUBLIC / "sitemap.xml", xml)
    print(f"wrote {len(catalogue['spells'])} static spell pages and isolated demos")


if __name__ == "__main__":
    build_pages(json.loads((PUBLIC / "spells.json").read_text(encoding="utf-8")))
