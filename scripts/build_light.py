#!/usr/bin/env python3
"""Build the light, link-first catalogue from the same canonical spell payload.

The full interactive 2026 catalogue remains separately available at /classic/.
No spell source, highlighted code, or 150 preview documents are embedded here.
"""
from __future__ import annotations

import html
from pathlib import Path
from build import CAT_ORDER, SUPPORT_AS_OF, one_line, slugify

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "index.html"

def esc(value: object) -> str:
    return html.escape(str(value), quote=True)

def render(catalogue: dict) -> str:
    spells = catalogue["spells"]
    by_cat: dict[str, list[dict]] = {}
    for spell in spells:
        by_cat.setdefault(spell["category"], []).append(spell)
    order = [c for c in CAT_ORDER if c in by_cat]
    order.extend(c for c in by_cat if c not in order)
    links = "".join(
        f'<a href="#cat-{slugify(cat)}"><span>{esc(cat)}</span><span class="cat-link__count">{len(by_cat[cat])}</span></a>'
        for cat in order
    )
    sections = []
    for cat in order:
        rows = []
        for spell in by_cat[cat]:
            sid = esc(spell["id"])
            title = esc(spell["title"])
            status = esc(spell["status"])
            description = esc(one_line(spell.get("description", "")))
            search = esc(" ".join(str(spell.get(key, "")) for key in ("id", "title", "category", "feature", "status")).lower())
            rows.append(f"""<li class="row" data-id="{sid}" data-status="{status}" data-search="{search}">
  <span class="row__index">{esc(spell["number"]).zfill(3)}</span>
  <div class="row__body">
    <h3><a class="row__link" href="/spells/{sid}/">{title}<span aria-hidden="true"> ↗</span></a></h3>
    <p>{description}</p>
  </div>
  <span class="status-badge" data-status="{status}">{esc(spell["statusLabel"])}</span>
  <a class="row__demo" href="/play/{sid}/" aria-label="Open demo: {title}">Demo ↗</a>
</li>""")
        sections.append(f"""<section class="cat-section" id="cat-{slugify(cat)}" data-category="{esc(cat)}" aria-labelledby="heading-{slugify(cat)}">
  <div class="cat-section__head"><h2 id="heading-{slugify(cat)}">{esc(cat)}</h2><span>{len(rows)} spell{'s' if len(rows) != 1 else ''}</span></div>
  <ul class="spell-list">{"".join(rows)}</ul>
</section>""")
    total = len(spells)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>Design Spells — native HTML &amp; CSS techniques</title>
<meta name="description" content="{total} native HTML and CSS design techniques. Browse individual examples and isolated, interactive demos.">
<link rel="canonical" href="https://design-spells.hultsan20.workers.dev/">
<meta property="og:title" content="Design Spells — native HTML &amp; CSS techniques">
<meta property="og:description" content="{total} copyable HTML/CSS techniques with isolated demos and browser-support guidance.">
<meta property="og:url" content="https://design-spells.hultsan20.workers.dev/">
<link rel="stylesheet" href="/catalogue.css">
<script src="/catalogue.js" defer></script>
</head>
<body>
<a class="skip-link" href="#catalogue">Skip to catalogue</a>
<header class="site-head"><a class="brand" href="/" aria-label="Design Spells home"><span class="brand__mark" aria-hidden="true">✳</span> DESIGN SPELLS <span class="brand__tag">HTML / CSS</span></a>
<nav aria-label="Site navigation"><a href="#categories">Categories</a><a href="/classic/">Classic explorer</a><a href="https://github.com/FullThrottle83/design-spells">GitHub ↗</a></nav></header>
<main>
<section class="hero" aria-labelledby="intro-title">
<div class="hero__copy"><p class="eyebrow">THE NATIVE WEB / {total} SPELLS</p><h1 id="intro-title">A little magic.<br><em>No framework required.</em></h1>
<p class="hero__lede">Small, useful design details made with HTML and CSS. Browse the source, open a live example, and check the browser limitations before you ship.</p>
<div class="hero__actions"><a class="button button--primary" href="#catalogue">Browse all spells <span aria-hidden="true">↓</span></a><a class="button" href="/classic/">Open classic explorer ↗</a></div>
<p class="hero__fine">The spells contain no client-side JavaScript. Catalogue search is optional; all links and demos work without it.</p></div>
<div class="hero__visual"><div class="hero__visual-head"><span class="live-dot"></span> LIVE EXAMPLE <span class="hero__visual-id">DS-001</span></div>
<iframe title="Live demonstration: Shimmer on primary buttons" src="/play/ds-1/" loading="lazy" sandbox="allow-same-origin allow-forms"></iframe>
<div class="hero__visual-foot"><span>CSS, doing its thing.</span><a href="/spells/ds-1/">View source ↗</a></div></div>
</section>
<div class="catalogue-layout" id="catalogue">
<aside class="sidebar" id="categories" aria-label="Spell categories"><p class="eyebrow">DIRECTORY</p><h2>Categories</h2><nav class="category-links" aria-label="Jump to category">{links}</nav>
<div class="sidebar__note"><strong>Prefer the original layout?</strong><p>The full preview rail, popover explorer and stack builder remain available.</p><a href="/classic/">Classic explorer ↗</a></div></aside>
<div class="results"><div class="results__head"><div><p class="eyebrow">REFERENCE LIBRARY</p><h2>Explore the spells.</h2><p class="results__description">Individual pages load on demand. Browser guidance is a dated project snapshot ({SUPPORT_AS_OF}), not proof of complete behavior.</p></div>
<div class="catalogue-tools" hidden><label for="search">Find a spell</label><input id="search" type="search" placeholder="Name, feature, category…" autocomplete="off"><p id="result-count" role="status" aria-live="polite">Showing {total} spells</p></div></div>
{"".join(sections)}
<p id="no-results" hidden>No matches. Clear your search to see every spell.</p>
<footer><span>Native first. Progressive when needed.</span><a href="https://github.com/FullThrottle83/design-spells">View the source on GitHub ↗</a></footer>
</div></div>
</main></body></html>"""

def build_light(catalogue: dict) -> None:
    OUT.write_text(render(catalogue) + "\n", encoding="utf-8")
    print(f"wrote light public/index.html {OUT.stat().st_size} bytes")

if __name__ == "__main__":
    import json
    build_light(json.loads((ROOT / "public/spells.json").read_text(encoding="utf-8")))
