#!/usr/bin/env python3
"""Parse the design-spells catalogue (README.md) and emit public/spells.js."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "README.md").read_text(encoding="utf-8")

CATEGORY_UI = {
    "Interaction": "Interaction",
    "Reveal": "Reveal & motion",
    "Scroll-driven": "Scroll",
    "Scroll-state": "Scroll",
    "Layout": "Layout",
    "Anchor": "Anchor",
    "Anchor (legacy)": "Anchor",
    "Typography": "Typography",
    "Forms": "Forms",
    "Visual": "Visual",
    "State": "State",
    "Performance": "Performance",
    "Data": "Data",
    "Navigation": "Navigation",
    "Cards": "Cards",
    "Overlays": "Overlays",
    "Media": "Media",
}

FEATURE_BROWSERS = {
    "baseline": {
        "feature": "Widely available CSS",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Works in current Chrome, Edge, Firefox, and Safari.",
    },
    "has": {
        "feature": ":has()",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": ":has() has been Baseline since late 2023.",
    },
    "light-dark": {
        "feature": "light-dark()",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "light-dark() is Baseline 2024.",
    },
    "starting-style": {
        "feature": "@starting-style / popover",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "@starting-style and the Popover API are Baseline 2024–25.",
    },
    "scroll-timeline": {
        "feature": "animation-timeline: scroll()",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Scroll-driven animations: Chrome 115+, Firefox 136+, Safari 26+.",
    },
    "view-timeline": {
        "feature": "animation-timeline: view()",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "view() timelines: Chrome 115+, Firefox 136+, Safari 26+.",
    },
    "anchor": {
        "feature": "CSS Anchor Positioning",
        "chrome": "yes", "edge": "yes", "firefox": "partial", "safari": "yes",
        "note": "Chrome 125+, Safari 26+. Firefox support is still partial.",
    },
    "view-transitions": {
        "feature": "View Transitions",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Chrome 111+, Safari 18+. Firefox has not shipped this yet.",
    },
    "interpolate-size": {
        "feature": "interpolate-size",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chrome/Edge 129+. Firefox and Safari still snap instead of interpolating.",
    },
    "field-sizing": {
        "feature": "field-sizing",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Chrome 123+, Safari 17.4+. Firefox has not shipped field-sizing.",
    },
    "text-box-trim": {
        "feature": "text-box-trim",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Chrome 133+, Safari 18.2+, Firefox 154+.",
    },
    "scroll-state": {
        "feature": "scroll-state container queries",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chrome/Edge 133+. Not in Firefox or Safari as of 2026.",
    },
    "invoker-commands": {
        "feature": "Invoker Commands (commandfor)",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Chrome 135+, Safari 26.2+, Firefox 153+.",
    },
    "interest-invokers": {
        "feature": "Interest Invokers (interestfor)",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only as of 2026. Pair with a CSS hover fallback.",
    },
    "closedby": {
        "feature": "dialog closedby",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Chrome 134+, Safari 18.4+. Firefox still needs a close button.",
    },
    "until-found": {
        "feature": 'hidden="until-found"',
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "no",
        "note": "Chrome 102+, Firefox 139+. Safari has not shipped until-found.",
    },
    "scroll-markers": {
        "feature": "::scroll-marker / ::scroll-button",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only carousel controls. Wrap them in @supports.",
    },
    "base-select": {
        "feature": "appearance: base-select",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Chrome 135+, Safari 18.4+. Firefox keeps the native picker.",
    },
    "select-pseudos": {
        "feature": "::checkmark / ::picker-icon",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Requires appearance: base-select. Chrome 135+, Safari 18.4+.",
    },
    "corner-shape": {
        "feature": "corner-shape",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chrome/Edge 139+. Falls back to regular border-radius.",
    },
    "grid-lanes": {
        "feature": "display: grid-lanes",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only masonry in 2026. Fallback is a regular grid.",
    },
    "sibling-index": {
        "feature": "sibling-index()",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only CSS Values 5 tree counting.",
    },
    "contrast-color": {
        "feature": "contrast-color()",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only. Provide an explicit color fallback.",
    },
    "if": {
        "feature": "CSS if()",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only conditional values. Other browsers ignore the declaration.",
    },
    "typed-attr": {
        "feature": "typed attr()",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only. Feature-detect with attr(x type(*)).",
    },
    "details-content": {
        "feature": "::details-content",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Chrome 131+, Safari 18.4+. Firefox still uses the older 0fr pattern.",
    },
    "reading-flow": {
        "feature": "reading-flow",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only. Tab order stays in DOM order elsewhere.",
    },
    "target-text": {
        "feature": "::target-text",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Chrome 133+, Safari 18.2+. Styles shared text fragments.",
    },
    "initial-letter": {
        "feature": "initial-letter",
        "chrome": "partial", "edge": "partial", "firefox": "no", "safari": "yes",
        "note": "Safari has full initial-letter. Chromium support is limited; a float fallback is included.",
    },
    "position-visibility": {
        "feature": "position-visibility",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Chrome 125+, Safari 26+. Overlay stays visible without support.",
    },
    "shape": {
        "feature": "clip-path: shape()",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "partial",
        "note": "shape() is newest in Chromium. Other browsers ignore the clip.",
    },
    "offset-path": {
        "feature": "offset-path",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Motion path is widely available in current browsers.",
    },
    "property": {
        "feature": "@property",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "@property is Baseline and needed for typed interpolation.",
    },
    "subgrid": {
        "feature": "CSS subgrid",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "subgrid is Baseline in current browsers.",
    },
    "container": {
        "feature": "@container size queries",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Size container queries are Baseline since 2023.",
    },
    "content-visibility": {
        "feature": "content-visibility",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "content-visibility: auto is widely available.",
    },
    "scrollbar-color": {
        "feature": "scrollbar-color",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Standard scrollbar-color / scrollbar-width are Baseline 2024+.",
    },
    "color-mix": {
        "feature": "color-mix() / oklch()",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "color-mix() and oklch() are Baseline 2023.",
    },
}


def detect_feature(css: str, html: str, title: str, status: str) -> str:
    src = f"{css}\n{html}\n{title}"
    checks = [
        (r"interestfor|interest-delay|:interest-source", "interest-invokers"),
        (r"commandfor|command=", "invoker-commands"),
        (r"grid-lanes", "grid-lanes"),
        (r"sibling-index\(", "sibling-index"),
        (r"contrast-color\(", "contrast-color"),
        (r"\bif\(", "if"),
        (r"attr\([^)]*type\(", "typed-attr"),
        (r"closedby", "closedby"),
        (r"hidden=[\"']until-found", "until-found"),
        (r"::scroll-marker|::scroll-button", "scroll-markers"),
        (r"::checkmark|::picker-icon", "select-pseudos"),
        (r"appearance:\s*base-select", "base-select"),
        (r"corner-shape", "corner-shape"),
        (r"container-type:\s*scroll-state|@container scroll-state", "scroll-state"),
        (r"animation-timeline:\s*view\(", "view-timeline"),
        (r"animation-timeline:\s*scroll\(", "scroll-timeline"),
        (r"@view-transition|view-transition-name|view-transition-class", "view-transitions"),
        (r"anchor-name|position-anchor|position-area", "anchor"),
        (r"interpolate-size", "interpolate-size"),
        (r"field-sizing", "field-sizing"),
        (r"text-box-trim", "text-box-trim"),
        (r"::details-content", "details-content"),
        (r"reading-flow", "reading-flow"),
        (r"::target-text", "target-text"),
        (r"initial-letter", "initial-letter"),
        (r"position-visibility", "position-visibility"),
        (r"clip-path:\s*shape\(", "shape"),
        (r"offset-path", "offset-path"),
        (r"@property", "property"),
        (r"subgrid", "subgrid"),
        (r"@container\b|container-type:\s*inline-size", "container"),
        (r"content-visibility", "content-visibility"),
        (r"scrollbar-color", "scrollbar-color"),
        (r"light-dark\(", "light-dark"),
        (r"@starting-style|:popover-open|popover=", "starting-style"),
        (r"color-mix\(|oklch\(", "color-mix"),
        (r":has\(", "has"),
    ]
    for pattern, key in checks:
        if re.search(pattern, src):
            return key
    return "baseline"


IMG = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 640 400'%3E"
    "%3Cdefs%3E%3ClinearGradient id='g' x1='0' x2='1' y1='0' y2='1'%3E"
    "%3Cstop stop-color='%236d5efc'/%3E%3Cstop offset='1' stop-color='%23c084fc'/%3E"
    "%3C/linearGradient%3E%3C/defs%3E"
    "%3Crect width='640' height='400' fill='url(%23g)'/%3E"
    "%3C/svg%3E"
)

IMG_B = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 640 400'%3E"
    "%3Cdefs%3E%3ClinearGradient id='g' x1='1' x2='0' y1='0' y2='1'%3E"
    "%3Cstop stop-color='%230f766e'/%3E%3Cstop offset='1' stop-color='%235eead4'/%3E"
    "%3C/linearGradient%3E%3C/defs%3E"
    "%3Crect width='640' height='400' fill='url(%23g)'/%3E"
    "%3C/svg%3E"
)


PREVIEW_HTML: dict[str, str] = {
    "1": f'<button class="btn-primary">Get started</button>',
    "2": '<button class="btn">Press me</button>',
    "3": f'<article class="destination-card"><img src="{IMG}" alt=""><h3>Lisbon</h3><p>Atlantic light.</p></article>',
    "5": '<nav><a class="nav-link" href="#">Overview</a> <a class="nav-link" href="#" aria-current="page">Pricing</a></nav>',
    "7": '<button class="icon" aria-label="Star">★</button>',
    "19": '<div class="input-group"><span aria-hidden="true">⌕</span><input type="search" placeholder="Search spells"></div>',
    "20": '<label style="display:flex;align-items:center;gap:.6rem"><input type="checkbox"> Remember me</label>',
    "22": '<details><summary>Details <span class="chevron">▾</span></summary><p>Native disclosure, no script.</p></details>',
    "24": '<a href="https://example.com" target="_blank" rel="noopener">Docs <span class="external-icon">↗</span></a>',
    "26": '<div class="segmented"><button type="button" aria-pressed="true">Day</button><button type="button">Week</button><button type="button">Month</button></div>',
    "38": '<button class="btn-primary">Mix a hover</button>',
    "39": '<label style="display:grid;gap:.4rem">Accent<input type="range" min="0" max="100" value="60"></label>',
    "8": '<h2 class="section-heading">A heading that reveals</h2>',
    "9": '<div class="hero-content"><p>Depth settles on load.</p></div>',
    "11": '<div class="skeleton" style="inline-size:16rem;block-size:4.5rem;border-radius:8px"></div>',
    "14": '<p class="demo-note">View Transitions run on real page navigations. This preview shows the CSS only.</p>',
    "31": '<button popovertarget="ph-pop" class="btn">Open menu</button><div id="ph-pop" popover class="popover-menu">Phantom entry</div>',
    "65": '<header class="site-header"><strong class="header-logo">Brand</strong></header><p style="height:8rem">Scroll the page to compress.</p>',
    "66": '<p class="demo-note">Backdrop fade applies to native dialogs and popovers.</p><button popovertarget="bd-pop">Open</button><div id="bd-pop" popover>Hello</div>',
    "72": '<ul class="stagger-list"><li>One</li><li>Two</li><li>Three</li></ul>',
    "17": '<header class="site-header">Frosted after scroll</header>',
    "30": '<p style="min-height:4rem">Content</p><div class="sticky-cta">Continue →</div>',
    "36": '<div class="scroll-progress"></div><p class="demo-note">A 3px bar tracks root scroll.</p>',
    "43": '<header class="site-header">Auto-hide header</header><p class="demo-note">Needs the root scroll-state preset.</p>',
    "44": '<nav class="toc"><div class="toc__inner">On this page</div></nav>',
    "45": '<div class="carousel"><div class="slide"><article>01</article></div><div class="slide"><article>02</article></div><div class="slide"><article>03</article></div></div>',
    "46": '<div class="tabs-wrap"><div class="fade-hint">→</div><p>Scrollable tabs live here.</p></div>',
    "47": '<a class="backtotop" href="#">↑</a><p class="demo-note">Wakes after the page has been scrolled.</p>',
    "55": '<div class="card-stack"><article class="card">Card A</article><article class="card">Card B</article><article class="card">Card C</article></div>',
    "69": '<div class="table-wrapper"><table><tr><th>Name</th><th>Plan</th><th>Seats</th></tr><tr><td>Acme</td><td>Pro</td><td>24</td></tr></table></div>',
    "12": f'<div class="gallery"><figure><img src="{IMG}" alt=""></figure><figure><img src="{IMG_B}" alt=""></figure><figure><img src="{IMG}" alt=""></figure></div>',
    "15": '<details><summary>Open panel</summary><div class="accordion-panel"><div class="accordion-inner">Animated with 0fr → 1fr.</div></div></details>',
    "27": '<div class="scroller-wrap"><div style="display:flex;gap:1rem;overflow:auto"><span>Alpha</span><span>Bravo</span><span>Charlie</span><span>Delta</span></div></div>',
    "33": '<details><summary>True auto height</summary><div class="accordion-panel">Animates to auto.</div></details>',
    "37": f'<div class="card-container"><article class="adaptive-card"><img class="card-media" src="{IMG}" alt=""><div><h3>Adaptive</h3><p>Layout follows the container.</p></div></article></div>',
    "40": '<div class="card-grid"><article class="card"><h3>One</h3><p>Short</p><button>Go</button></article><article class="card"><h3>Two</h3><p>A little more copy in this card.</p><button>Go</button></article></div>',
    "56": f'<div class="scroll-gallery" style="display:flex;gap:1rem"><img src="{IMG}" alt="" width="180"><img src="{IMG_B}" alt="" width="180"><img src="{IMG}" alt="" width="180"></div>',
    "61": '<div class="tabs-container"><details name="ui-tabs" open><summary>Overview</summary><p>First panel.</p></details><details name="ui-tabs"><summary>Details</summary><p>Second panel.</p></details></div>',
    "62": '<div class="carousel"><div class="slide">One</div><div class="slide">Two</div><div class="slide">Three</div></div>',
    "77": '<p class="demo-note">Opens as a sheet on small screens, a dialog on large ones.</p><button commandfor="sheet-demo" command="show-modal" class="btn">Open sheet</button><dialog id="sheet-demo" class="responsive-sheet" closedby="any"><p>Sheet content</p><form method="dialog"><button class="btn">Close</button></form></dialog>',
    "18": '<button data-tooltip="Copied to clipboard">Hover me</button>',
    "34": '<button class="tooltip-trigger">Trigger</button><div class="native-tooltip">Pinned tooltip</div>',
    "48": '<div class="field"><input type="email" required placeholder="you@site.com"><div class="error-bubble">Enter a valid email.</div></div>',
    "49": '<div class="filterbar"><button class="filter-trigger">Filters</button><div class="filter-panel">Sort · Date · Owner</div></div>',
    "50": '<div class="form-row"><label>API key<input></label><p class="help-rail">Keep this secret.</p></div>',
    "10": "<p>Select this sentence to see the skin.</p>",
    "bonus": "<h2 class='text-balance'>Typographic harmony on a long heading</h2><p class='text-pretty'>Pretty wrapping keeps orphans off the last line of a paragraph.</p>",
    "53": '<button class="btn">Trimmed</button> <span class="chip">Chip</span>',
    "63": "<article><p>Hyphenation keeps narrow columns from opening rivers of white space.</p></article>",
    "6": '<input type="text" placeholder="Focus me">',
    "16": '<div class="form-group"><input placeholder=" "><label>Your name</label></div>',
    "23": '<input type="email" required placeholder="you@site.com">',
    "28": '<ol class="steps"><li>Account</li><li>Address</li><li>Pay</li></ol>',
    "32": '<textarea class="auto-grow" placeholder="Type to grow…"></textarea>',
    "54": '<select class="premium-dropdown"><option>Overview</option><option>Reports</option><option>Settings</option></select>',
    "57": '<form class="checkout-form"><div class="form-group"><input required placeholder="Email"></div><button type="submit">Pay</button></form>',
    "25": f'<article class="media-card"><img src="{IMG}" alt="" style="display:block;width:100%"><h3 style="position:absolute;bottom:1rem;left:1rem;z-index:1;color:white">Stay</h3></article>',
    "35": '<article class="premium-card" style="padding:1rem">light-dark() follows the OS.</article>',
    "51": '<article class="ribbon-card" style="padding:1.5rem;background:var(--color-surface)">Ribbon cut</article>',
    "52": '<div class="section-divider"></div>',
    "58": '<article class="premium-glow-card" style="padding:1.25rem">Breathing border</article>',
    "64": '<div class="floating-orb"></div>',
    "74": f'<div class="blend-container" style="position:relative"><img src="{IMG}" alt="" style="width:100%;display:block"><p class="contrast-text" style="position:absolute;inset:0;display:grid;place-items:center;font-size:1.6rem">Contrast</p></div>',
    "78": '<p class="text-fade-clamp">The faded mask replaces a hard line-clamp so the last visible line dissolves instead of being chopped mid-word. Extra copy keeps the fade honest.</p>',
    "13": '<div class="card-grid"><article class="destination-card">Alpha</article><article class="destination-card">Bravo</article><article class="destination-card">Charlie</article></div>',
    "21": '<section id="preview-target">Deep-linked highlight</section>',
    "29": '<div class="link-cluster"><a href="#">Docs</a> <a href="#">Blog</a> <a href="#">Careers</a></div>',
    "59": '<div class="data-grid"></div>',
    "41": '<section class="lazy-section">Offscreen layout is skipped.</section>',
    "107": '<p class="demo-note">The panel hides when its anchor leaves the viewport.</p><button class="filter-trigger" style="anchor-name:--filter-btn">Filters</button><div class="filter-panel">Hidden when the trigger is gone.</div>',
    "112": "<p>Shared links that use #:~:text= highlight with ::target-text.</p>",
    "113": '<div class="pack-grid"><article>A</article><article>B</article><article>C</article></div>',
    "114": '<div class="table-scroller" style="max-height:6rem;overflow:auto"><p>Themed scrollbars on embedded panels.</p><p>More</p><p>More</p><p>More</p></div>',
    "118": '<select class="premium-dropdown"><option>One</option><option selected>Two</option><option>Three</option></select>',
    "143": '<p class="demo-note">Print rules hide chrome and append URLs. Open a print preview to see them.</p>',
    "104": '<article class="saas-card">if() tokens follow the scheme.</article>',
}


def parse_spells(md: str) -> list[dict]:
    # Slice from the Spells heading to Ready-made stacks.
    start = md.find("\n# Spells\n")
    end = md.find("\n# Ready-made stacks\n")
    if start < 0:
        raise SystemExit("Could not find # Spells")
    body = md[start:end if end > 0 else None]

    heading_re = re.compile(r"^### (.+)$", re.M)
    matches = list(heading_re.finditer(body))
    spells = []
    current_section = "Spells"
    section_re = re.compile(r"^## (.+)$", re.M)
    sections = list(section_re.finditer(body))

    def section_at(pos: int) -> str:
        name = "Spells"
        for s in sections:
            if s.start() < pos:
                name = s.group(1).strip()
            else:
                break
        return name

    for i, m in enumerate(matches):
        chunk = body[m.end(): matches[i + 1].start() if i + 1 < len(matches) else len(body)]
        raw_title = m.group(1).strip()
        ident = "bonus"
        title = raw_title
        num_m = re.match(r"^(\d+)\.\s+(.*)$", raw_title)
        if num_m:
            ident = num_m.group(1)
            title = num_m.group(2)
        elif raw_title.lower().startswith("bonus"):
            ident = "bonus"
            title = re.sub(r"^Bonus\.\s*", "", raw_title)

        meta_m = re.search(r"^\*(.+)\*\s*$", chunk, re.M)
        meta = meta_m.group(1) if meta_m else ""
        parts = [p.strip() for p in meta.split("·")]
        category = parts[0] if parts else section_at(m.start())
        status = "Baseline"
        js_need = "0 JS"
        note = ""
        for p in parts[1:]:
            if p in {"Baseline", "Newer", "Progressive"}:
                status = p
            elif p in {"0 JS", "Markup"}:
                js_need = p
            else:
                note = p

        desc_parts = []
        consumed = chunk
        if meta_m:
            consumed = chunk[meta_m.end():]
        # Strip code fences from description
        desc_src = re.sub(r"```[\s\S]*?```", "", consumed)
        for line in desc_src.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("Markup:"):
                continue
            desc_parts.append(line)
        description = " ".join(desc_parts).strip()

        html = ""
        css = ""
        for fm in re.finditer(r"```(html|css)\n([\s\S]*?)```", chunk):
            lang, code = fm.group(1), fm.group(2).rstrip() + "\n"
            if lang == "html" and not html:
                html = code
            elif lang == "css" and not css:
                css = code

        # Inline markup note like: Markup: `<div class="scroll-progress"></div>`.
        if not html:
            inline = re.search(r"Markup:\s*`([^`]+)`", chunk)
            if inline:
                html = inline.group(1) + "\n"

        spells.append({
            "id": f"ds-{ident}" if ident != "bonus" else "ds-bonus",
            "number": ident,
            "title": title,
            "section": section_at(m.start()),
            "category": CATEGORY_UI.get(category, category),
            "rawCategory": category,
            "status": status.lower(),
            "statusLabel": status,
            "jsNeed": "none" if js_need == "0 JS" else "markup",
            "jsLabel": js_need,
            "note": note,
            "description": description,
            "html": html,
            "css": css,
        })
    return spells


def polish_preview(spell: dict) -> str:
    html = PREVIEW_HTML.get(spell["number"], spell["html"]).strip()
    if not html:
        # Last-resort: a labelled sample using the first class in the CSS.
        classes = re.findall(r"(?<![:\w])\.([a-zA-Z][\w-]*)", spell["css"])
        cls = classes[0] if classes else "demo"
        html = f'<div class="{cls}">Preview · {spell["title"]}</div>'
    # Swap remote images for local gradients so previews never depend on /photo.jpg.
    html = re.sub(
        r'src="/(?:after|photo-full|hero-1|hero-bg|a|photo)\.jpg"',
        f'src="{IMG}"',
        html,
    )
    html = re.sub(
        r'src="/(?:before|photo-thumb|b)\.jpg"',
        f'src="{IMG_B}"',
        html,
    )
    return html


def rewrite_preview_css(css: str) -> str:
    css = re.sub(r":root\b", ":host", css)
    css = re.sub(r"\bhtml\b", ":host", css)
    css = re.sub(r"\bbody\b", ":host", css)
    return css


def main() -> None:
    spells = parse_spells(SRC)
    print("parsed spells:", len(spells))

    payload = []
    for spell in spells:
        feature_key = detect_feature(spell["css"], spell["html"], spell["title"], spell["status"])
        support = FEATURE_BROWSERS[feature_key]
        item = {
            **spell,
            "previewHtml": polish_preview(spell),
            "previewCss": rewrite_preview_css(spell["css"]),
            "feature": support["feature"],
            "browsers": {
                "chrome": support["chrome"],
                "edge": support["edge"],
                "firefox": support["firefox"],
                "safari": support["safari"],
            },
            "supportNote": support["note"],
        }
        payload.append(item)

    cats = {}
    for s in payload:
        cats[s["category"]] = cats.get(s["category"], 0) + 1
    print("categories:", cats)

    classic = (
        "/* generated by scripts/build.py — do not edit by hand */\n"
        "window.DESIGN_SPELLS = "
        + json.dumps({"total": len(payload), "spells": payload}, ensure_ascii=False)
        + ";\n"
    )
    (ROOT / "public" / "spells.js").write_text(classic, encoding="utf-8")
    print("wrote public/spells.js", (ROOT / "public" / "spells.js").stat().st_size, "bytes")


if __name__ == "__main__":
    main()
