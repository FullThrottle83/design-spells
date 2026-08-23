#!/usr/bin/env python3
"""Parse the design-spells catalogue (README.md) and emit public/spells.js."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "README.md").read_text(encoding="utf-8")

CAT_ORDER = [
    "Interaction",
    "Navigation",
    "Cards",
    "Layout",
    "Scroll",
    "Reveal & motion",
    "Forms",
    "Overlays",
    "Typography",
    "Media",
    "Visual",
    "State",
    "Data",
    "Anchor",
    "Performance",
]

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

SUPPORT_AS_OF = "2026-08-24"

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
        "note": "@starting-style: Chrome/Edge 117+, Firefox 129+, Safari 17.5+. Popover is also supported in current browsers; both are newer Baseline features.",
    },
    "scroll-timeline": {
        "feature": "animation-timeline: scroll()",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Scroll-driven animations: Chrome/Edge 115+, Safari 26+. Firefox stable does not support them; Nightly support is preview.",
    },
    "view-timeline": {
        "feature": "animation-timeline: view()",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "view() timelines: Chrome/Edge 115+, Safari 26+. Firefox stable does not support them; Nightly support is preview.",
    },
    "anchor": {
        "feature": "CSS Anchor Positioning",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Chrome/Edge 125+, Safari 26+, Firefox 147+.",
    },
    "view-transitions-same": {
        "feature": "Same-document View Transitions",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Same-document View Transitions are available in current engines.",
    },
    "view-transitions-cross": {
        "feature": "Cross-document View Transitions",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Cross-document navigation transitions remain unavailable in Firefox.",
    },
    "interpolate-size": {
        "feature": "interpolate-size",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chrome/Edge 129+. Firefox and Safari still snap instead of interpolating.",
    },
    "field-sizing": {
        "feature": "field-sizing",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Chrome/Edge 123+, Firefox 152+, Safari 26.2+.",
    },
    "text-box-trim": {
        "feature": "text-box-trim",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Chrome/Edge 133+, Safari 18.2+. Firefox 154 support is preview; stable Firefox 153 does not support it.",
    },
    "scroll-state": {
        "feature": "scroll-state container queries",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chrome/Edge 133+. Not in Firefox or Safari as of 2026.",
    },
    "invoker-commands": {
        "feature": "Invoker Commands (commandfor)",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Chrome/Edge 135+, Firefox 144+, Safari 26.2+; Baseline newly available in late 2025.",
    },
    "interest-invokers": {
        "feature": "Interest Invokers (interestfor)",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only as of 2026. Pair with a CSS hover fallback.",
    },
    "closedby": {
        "feature": "dialog closedby",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "no",
        "note": "Chrome/Edge 134+ and Firefox 141+. Safari still needs an explicit close path.",
    },
    "open-pseudo": {
        "feature": ":open",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": ":open: Chrome/Edge 133+, Firefox 136+, Safari 26.5+. Baseline newly available in 2026.",
    },
    "scroll-initial-target": {
        "feature": "scroll-initial-target",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chrome/Edge 133+ only in stable browsers. Firefox and Safari do not support scroll-initial-target.",
    },
    "until-found": {
        "feature": 'hidden="until-found"',
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Chrome/Edge 102+, Firefox 148+, Safari 26.2+.",
    },
    "scroll-markers": {
        "feature": "::scroll-marker / ::scroll-button",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only carousel controls. Wrap them in @supports.",
    },
    "base-select": {
        "feature": "appearance: base-select",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chrome/Edge 135+ in stable browsers. Firefox has no stable support; Safari 27 support is preview.",
    },
    "select-pseudos": {
        "feature": "::checkmark / ::picker-icon",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "The pseudo-elements are Chrome/Edge 133+ and require customizable-select/base-select (Chrome/Edge 135+). Firefox has no stable support; Safari 27 is preview.",
    },
    "corner-shape": {
        "feature": "corner-shape",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chrome/Edge 139+. Falls back to regular border-radius.",
    },
    "grid-lanes": {
        "feature": "display: grid-lanes",
        "chrome": "no", "edge": "no", "firefox": "no", "safari": "yes",
        "note": "Safari 26.4+ only in stable browsers. Fallback is a regular grid.",
    },
    "sibling-index": {
        "feature": "sibling-index()",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Chrome/Edge and Safari 26.2+; Firefox has not shipped it.",
    },
    "contrast-color": {
        "feature": "contrast-color()",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Chrome/Edge 147+, Firefox 146+, Safari 26+.",
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
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Chrome/Edge 131+, Firefox 143+, Safari 18.4+.",
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
    "custom-functions": {
        "feature": "CSS Functions (@function)",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chrome/Edge 139+; Firefox and Safari unsupported.",
    },
    "css-scope": {
        "feature": "CSS Scoping (@scope)",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Baseline: Chrome/Edge 118+, Safari 17.4+, Firefox 146+.",
    },
    "gap-decorations": {
        "feature": "CSS Gap Decorations (column-rule)",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chrome/Edge 149+; Firefox and Safari unsupported.",
    },
    "css-random": {
        "feature": "CSS random()",
        "chrome": "no", "edge": "no", "firefox": "no", "safari": "yes",
        "note": "Safari 26.2+; Chromium and Firefox unsupported.",
    },
}


LEVEL_RANK = {"no": 0, "partial": 1, "yes": 2}


def detect_features(css: str, html: str, title: str, status: str) -> list[str]:
    src = f"{css}\n{html}\n{title}"
    checks = [
        (r"@function\b", "custom-functions"),
        (r"@scope\b", "css-scope"),
        (r"column-rule|row-rule", "gap-decorations"),
        (r"\brandom\(", "css-random"),
        (r"interestfor|interest-delay|:interest-source", "interest-invokers"),
        (r"commandfor|command=", "invoker-commands"),
        (r"grid-lanes", "grid-lanes"),
        (r"sibling-index\(", "sibling-index"),
        (r"contrast-color\(", "contrast-color"),
        (r"\bif\(", "if"),
        (r"attr\([^)]*type\(", "typed-attr"),
        (r"closedby", "closedby"),
        (r"scroll-initial-target", "scroll-initial-target"),
        (r":open\b", "open-pseudo"),
        (r"hidden=[\"']until-found", "until-found"),
        (r"::scroll-marker|::scroll-button", "scroll-markers"),
        (r"::checkmark|::picker-icon", "select-pseudos"),
        (r"appearance:\s*base-select", "base-select"),
        (r"corner-shape", "corner-shape"),
        (r"container-type:\s*scroll-state|@container\s+scroll-state", "scroll-state"),
        (r"animation-timeline:\s*view\(", "view-timeline"),
        (r"animation-timeline:\s*scroll\(", "scroll-timeline"),
        (r"@view-transition\s*\{[^}]*navigation\s*:\s*auto", "view-transitions-cross"),
        (r"@view-transition|view-transition-name|view-transition-class|::view-transition", "view-transitions-same"),
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
    hits = []
    for pattern, key in checks:
        if re.search(pattern, src) and key not in hits:
            hits.append(key)
    return hits or ["baseline"]


def combine_support(feature_keys: list[str]) -> dict:
    """Worst-case support across every feature a spell actually depends on,
    instead of grading it on whichever risky feature the pattern list hits
    first (that used to hide a spell's second, less-supported dependency)."""
    browsers = {"chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes"}
    for key in feature_keys:
        support = FEATURE_BROWSERS[key]
        for b in browsers:
            if LEVEL_RANK[support[b]] < LEVEL_RANK[browsers[b]]:
                browsers[b] = support[b]
    return browsers


def feature_label(feature_keys: list[str]) -> str:
    return " + ".join(FEATURE_BROWSERS[k]["feature"] for k in feature_keys)


def feature_note(feature_keys: list[str]) -> str:
    return " ".join(FEATURE_BROWSERS[k]["note"] for k in feature_keys)


def derive_status(browsers: dict) -> str:
    values = list(browsers.values())
    no_count = values.count("no")
    if no_count >= 2:
        return "Progressive"
    if no_count == 1 or "partial" in values:
        return "Newer"
    return "Baseline"


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


# The placeholder photo paths the catalogue's recipes reference. Nothing
# serves them, so both the markup and the CSS swap them for inline gradients.
LOCAL_IMG_A = r"(?:after|photo-full|hero-1|hero-bg|a|photo)\.jpg"
LOCAL_IMG_B = r"(?:before|photo-thumb|b)\.jpg"


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
    "65": '<header class="site-header"><strong class="header-logo">Brand</strong></header><p class="demo-note">Bound to the real page scroll — scroll the whole catalogue, not this box.</p>',
    "66": '<p class="demo-note">Backdrop fade applies to native dialogs and popovers.</p><button popovertarget="bd-pop">Open</button><div id="bd-pop" popover>Hello</div>',
    "72": '<ul class="stagger-list"><li>One</li><li>Two</li><li>Three</li></ul>',
    "17": '<header class="site-header">Frosted after scroll</header><p class="demo-note">Bound to the real page scroll — scroll the whole catalogue, not this box.</p>',
    "30": '<p style="min-height:4rem">Content</p><div class="sticky-cta">Continue →</div>',
    "36": '<div class="scroll-progress"></div><p class="demo-note">A 3px bar tracks root scroll.</p>',
    "43": '<header class="site-header">Auto-hide header</header><p class="demo-note">Needs the root scroll-state preset.</p>',
    "44": '<nav class="toc"><div class="toc__inner">On this page</div></nav>',
    "45": '<div class="carousel" style="max-width:20rem">' + "".join(
        f'<div class="slide"><article style="min-width:200px;padding:1.5rem;border-radius:var(--radius-lg);background:var(--color-surface);box-shadow:0 1px 2px oklch(0.2 0.01 80 / .08);text-align:center">{n}</article></div>'
        for n in ("01", "02", "03")
    ) + '</div>',
    "46": '<div class="tabs-wrap" style="max-width:20rem"><div style="display:flex;gap:1rem;white-space:nowrap;padding-inline-end:3rem;min-width:44rem">'
        + "".join(f"<span>{label}</span>" for label in ("Overview", "Getting started", "Pricing", "Documentation", "Changelog", "Support", "Community", "Careers"))
        + '</div><div class="fade-hint">→</div></div>',
    "47": '<a class="backtotop" href="#">↑</a><p class="demo-note">Wakes after the page has been scrolled.</p>',
    "55": '<div class="card-stack"><article class="card">Card A</article><article class="card">Card B</article><article class="card">Card C</article></div>',
    "69": '<div class="table-wrapper" style="max-width:20rem"><table style="min-width:44rem">'
        '<tr><th>Name</th><th>Plan</th><th>Seats</th><th>Region</th><th>Owner</th><th>Renewal date</th><th>Status</th></tr>'
        '<tr><td>Acme Corporation</td><td>Pro</td><td>24</td><td>EU-West</td><td>Jonas Andersson</td><td>2026-11-04</td><td>Active</td></tr></table>'
        '<p class="demo-note">Scroll the table sideways.</p></div>',
    "12": f'<div class="gallery"><figure><img src="{IMG}" alt=""></figure><figure><img src="{IMG_B}" alt=""></figure><figure><img src="{IMG}" alt=""></figure></div>',
    "15": '<details><summary>Open panel</summary><div class="accordion-panel"><div class="accordion-inner">Animated with 0fr → 1fr.</div></div></details>',
    "27": '<div class="scroller-wrap"><div style="display:flex;gap:1rem;overflow:auto"><span>Alpha</span><span>Bravo</span><span>Charlie</span><span>Delta</span></div></div>',
    "33": '<details><summary>True auto height</summary><div class="accordion-panel">Animates to auto.</div></details>',
    "37": f'<div class="card-container" style="resize:horizontal;overflow:auto;width:220px;min-width:180px;max-width:100%;padding:.5rem;border:1px dashed var(--color-border)"><article class="adaptive-card"><img class="card-media" src="{IMG}" alt=""><div><h3>Adaptive</h3><p>Layout follows the container.</p></div></article></div>',
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
    # See the ZERO-WIDTH note further down: full-bleed in real use, so the
    # preview has to say how wide it is.
    "52": '<div class="section-divider" style="inline-size:min(22rem, 100%)"></div>',
    "58": '<article class="premium-glow-card" style="padding:1.25rem">Breathing border</article>',
    "64": '<div class="floating-orb"></div>',
    "74": f'<div class="blend-container" style="position:relative"><img src="{IMG}" alt="" style="width:100%;display:block"><p class="contrast-text" style="position:absolute;inset:0;display:grid;place-items:center;font-size:1.6rem">Contrast</p></div>',
    "78": '<p class="text-fade-clamp">The faded mask replaces a hard line-clamp so the last visible line dissolves instead of being chopped mid-word. Extra copy keeps the fade honest.</p>',
    "13": '<div class="card-grid">' + "".join(
        f'<article class="destination-card" style="padding:1rem;border-radius:var(--radius-lg);background:var(--color-surface);box-shadow:0 1px 2px oklch(0.2 0.01 80 / .08)">{name}</article>'
        for name in ("Alpha", "Bravo", "Charlie")
    ) + '</div>',
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
    # ZERO-WIDTH: the stage centres its children on a grid, so a block whose
    # only contents are empty or absolutely positioned has nothing to derive an
    # inline size from and collapses to 0px wide — the effect renders, just
    # infinitely thin. These are full-bleed in real pages; state a width here.
    "105": '<div class="attr-meter" data-value="72" style="inline-size:min(18rem, 100%)"'
        ' aria-label="Profile complete to 72 percent"><span class="attr-meter-fill"></span></div>',
    "130": '<div class="double-slider" style="inline-size:min(20rem, 100%)">'
        '<input type="range" min="0" max="100" value="20" aria-label="Lowest price">'
        '<input type="range" min="0" max="100" value="80" aria-label="Highest price">'
        '<div class="slider-track" aria-hidden="true"></div></div>',
    "135": '<header class="plx-hero" style="inline-size:100%">'
        '<div class="plx-layer plx-bg" aria-hidden="true"></div>'
        '<div class="plx-layer plx-fg"><h1>The future of UI</h1></div></header>',
    "146": '<button commandfor="guard-modal" command="show-modal" class="btn">Open modal</button>'
        '<dialog id="guard-modal" class="guard-modal" closedby="any"><h2>Modal content</h2>'
        '<div class="guard-body">Long scrollable content…</div></dialog>',
    "67": '<div class="compare-container" style="width:100%;max-width:24rem">'
        f'<img src="{IMG_B}" alt="After" class="compare-img compare-after">'
        '<div class="compare-before-wrap">'
        f'<img src="{IMG}" alt="Before" class="compare-img compare-before">'
        '</div>'
        '<div class="compare-scroller" tabindex="0" role="region" aria-label="Compare before and after. Swipe or use the arrow keys.">'
        '<div class="scroller-spacer"></div>'
        '</div>'
        '</div>',
    "98": '<button type="button" class="icon-btn" interestfor="tip-save" aria-label="Save">★</button>'
        '<div id="tip-save" popover="hint" class="hint-tip">Save to your list</div>'
        '<p class="demo-note">The ~400ms pause before it appears is intentional (interest-delay) — it avoids flashing on every incidental hover.</p>',
    "99": '<div class="init-carousel">'
        '<article class="slide" id="q1" style="flex:0 0 9rem">Q1</article>'
        '<article class="slide is-initial" id="q2" style="flex:0 0 9rem">Q2 — current</article>'
        '<article class="slide" id="q3" style="flex:0 0 9rem">Q3</article>'
        '</div>'
        '<p class="demo-note">Notice it opens already scrolled to Q2 — scroll-initial-target places it there on first paint, no JS.</p>',
    "100": '<ul class="lanes" style="max-width:26rem">' + "".join(
        f'<li><article class="card" style="padding:1rem;border-radius:var(--radius-lg);background:var(--color-surface);box-shadow:0 1px 2px oklch(0.2 0.01 80 / .08)">{label}</article></li>'
        for label in ("Card 1", "Card 2 with more text", "Card 3", "Card 4")
    ) + '</ul><p class="demo-note">display: grid-lanes has no browser support yet — this shows the auto-fill grid fallback.</p>',
    "126": '<nav class="spy-nav"><a href="#s1" class="spy-l1">Intro</a> <a href="#s2" class="spy-l2">Features</a></nav>'
        '<main><section id="s1" style="min-height:180px;display:grid;place-items:center">Intro</section>'
        '<section id="s2" style="min-height:180px;display:grid;place-items:center">Features</section></main>',
    "134": '<ul class="swipe-list" style="max-width:20rem">'
        '<li class="swipe-item"><div class="swipe-content">Document_v1.pdf</div><button class="swipe-action">Delete</button></li>'
        '<li class="swipe-item"><div class="swipe-content">Invoice_Q3.pdf</div><button class="swipe-action">Delete</button></li>'
        '</ul>',
    "147": '<article class="fluid-rhythm-card" style="inline-size:min(22rem, 100%)">'
        '<p class="eyebrow">Quarterly report</p><h2>Spacing that scales</h2>'
        '<p>Responsive rhythm with typed @function.</p></article>',
    "148": '<article class="docs-card" style="inline-size:min(24rem, 100%)">'
        '<h2><span class="accent">Scoped</span> component guidance</h2><p>The outer accent belongs to the card.</p>'
        '<section class="example"><p><span class="accent">Embedded content</span> keeps its own theme.</p></section></article>',
    "149": '<div class="snap-products" style="max-width:22rem">'
        '<article class="snap-product"><div class="snap-product__body"><strong>Starter</strong><span>$12</span></div></article>'
        '<article class="snap-product"><div class="snap-product__body"><strong>Studio</strong><span>$28</span></div></article>'
        '<article class="snap-product"><div class="snap-product__body"><strong>Agency</strong><span>$64</span></div></article></div>',
    "150": '<dl class="metric-strip" style="inline-size:min(24rem, 100%)">'
        '<div><dt>Revenue</dt><dd>$84k</dd></div><div><dt>Retention</dt><dd>94%</dd></div><div><dt>Latency</dt><dd>82ms</dd></div></dl>',
    "151": '<ul class="avatar-cluster" style="max-width:20rem">'
        '<li aria-label="Ari">A</li><li aria-label="Bea">B</li><li aria-label="Chen">C</li><li aria-label="Dara">D</li><li aria-label="Eli">E</li></ul>',
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
            if line.startswith("---") or line.startswith("## ") or line.startswith("### "):
                # End of this spell's section — stop before absorbing the
                # next heading (or the divider right before it) into the text.
                break
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
    html = re.sub(rf'src="/{LOCAL_IMG_A}"', f'src="{IMG}"', html)
    html = re.sub(rf'src="/{LOCAL_IMG_B}"', f'src="{IMG_B}"', html)
    return html


def rewrite_preview_assets(css: str) -> str:
    """Same swap as polish_preview, but for CSS background images."""
    css = re.sub(rf"""url\(\s*['"]?/{LOCAL_IMG_A}['"]?\s*\)""", lambda _: f'url("{IMG}")', css)
    css = re.sub(rf"""url\(\s*['"]?/{LOCAL_IMG_B}['"]?\s*\)""", lambda _: f'url("{IMG_B}")', css)
    return css


_CSS_LITERAL_RE = re.compile(
    r"/\*.*?\*/|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'",
    re.S,
)


def preview_environment(css: str) -> str:
    """Select document isolation for CSS whose semantics require a document."""
    code = _CSS_LITERAL_RE.sub("", css)
    document_bound = (
        re.search(r"(?<![\w.#-])(?:html|body|:root)\b", code)
        or re.search(r"\bposition\s*:\s*fixed\b", code)
        or re.search(r":target(?!-)", code)
        or re.search(r"scroll\(\s*root\b", code)
    )
    return "document" if document_bound else "shadow"


def preview_action(css: str, html: str) -> dict:
    """Emit the interaction contract consumed by both the UI and tests."""
    src = f"{css}\n{html}"
    actions = [
        (
            r":user-invalid|:user-valid",
            "invalid-input",
            "Enter an invalid value, then leave the field",
        ),
        (
            r"commandfor|popovertarget|<dialog\b|popover(?:=|\s|>)",
            "activate-control",
            "Activate the control to preview",
        ),
        (
            r"<details\b|:open\b|\[open\]",
            "toggle-disclosure",
            "Open the disclosure to preview",
        ),
        (
            r'type=["\']range["\']',
            "adjust-range",
            "Drag the range control to preview",
        ),
        (
            r"animation-timeline|scroll-timeline|timeline-scope|container-type:\s*scroll-state",
            "scroll",
            "Scroll to preview",
        ),
        (r"@container\s+[\w-]*\s*\(", "resize", "Drag the corner to resize"),
        (r"scroll-snap-type\s*:", "swipe", "Swipe to preview"),
        (r":target(?!-)", "activate-link", "Activate the link to preview"),
        (r"::selection\b", "select-text", "Select the text to preview"),
        (r":checked\b|\[aria-pressed", "toggle-control", "Toggle the control to preview"),
        (
            r":hover\b.*:focus|:focus\b.*:hover",
            "hover-or-focus",
            "Hover or focus to preview",
        ),
        (r":hover\b", "hover", "Hover to preview"),
        (r":focus-visible\b", "keyboard-focus", "Press Tab to preview"),
        (r":focus(?:-within)?\b", "focus", "Focus to preview"),
        (r":active\b", "press", "Press and hold to preview"),
    ]
    for pattern, kind, hint in actions:
        if re.search(pattern, src, re.S):
            return {"kind": kind, "hint": hint}
    return {"kind": "none", "hint": ""}


_ROOT_SELECTOR_RE = re.compile(
    r"(?<![\w.#-])(?P<root>:root\b|\bhtml\b|\bbody\b)(?![\w-])"
)


def _skip_css_literal(css: str, start: int) -> int:
    """Return the first index after a quoted string or block comment."""
    if css.startswith("/*", start):
        end = css.find("*/", start + 2)
        return len(css) if end < 0 else end + 2
    quote = css[start]
    i = start + 1
    while i < len(css):
        if css[i] == "\\":
            i += 2
        elif css[i] == quote:
            return i + 1
        else:
            i += 1
    return len(css)


def _rewrite_root_code(code: str) -> str:
    def replace(match: re.Match) -> str:
        return ".stage" if match.group("root") == "body" else ":host"

    return _ROOT_SELECTOR_RE.sub(replace, code)


def _rewrite_prelude(prelude: str) -> str:
    """Rewrite document selectors while preserving strings and comments."""
    out: list[str] = []
    cursor = 0
    i = 0
    while i < len(prelude):
        if prelude.startswith("/*", i) or prelude[i] in {'"', "'"}:
            out.append(_rewrite_root_code(prelude[cursor:i]))
            end = _skip_css_literal(prelude, i)
            out.append(prelude[i:end])
            cursor = end
            i = end
        else:
            i += 1
    out.append(_rewrite_root_code(prelude[cursor:]))
    return "".join(out)


def _find_block_end(css: str, opening: int) -> int:
    depth = 1
    i = opening + 1
    while i < len(css):
        if css.startswith("/*", i) or css[i] in {'"', "'"}:
            i = _skip_css_literal(css, i)
            continue
        if css[i] == "{":
            depth += 1
        elif css[i] == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(css) - 1


def _rewrite_rule_list(css: str) -> str:
    out: list[str] = []
    cursor = statement = i = 0
    round_depth = square_depth = 0
    while i < len(css):
        if css.startswith("/*", i) or css[i] in {'"', "'"}:
            i = _skip_css_literal(css, i)
            continue
        char = css[i]
        if char == "(":
            round_depth += 1
        elif char == ")":
            round_depth = max(0, round_depth - 1)
        elif char == "[":
            square_depth += 1
        elif char == "]":
            square_depth = max(0, square_depth - 1)
        elif char == ";" and round_depth == square_depth == 0:
            statement = i + 1
        elif char == "{" and round_depth == square_depth == 0:
            closing = _find_block_end(css, i)
            out.append(css[cursor:statement])
            out.append(_rewrite_prelude(css[statement:i]))
            out.append("{")
            out.append(_rewrite_rule_list(css[i + 1:closing]))
            out.append("}")
            cursor = statement = closing + 1
            i = closing
        i += 1
    out.append(css[cursor:])
    return "".join(out)


def rewrite_preview_css(css: str) -> str:
    """Adapt selector preludes without touching declaration text."""
    return _rewrite_rule_list(css)


ICON_SPRITE = """<svg aria-hidden="true" style="position:absolute;width:0;height:0;overflow:hidden" xmlns="http://www.w3.org/2000/svg">
  <symbol id="ds-icon-chrome" viewBox="0 0 512 512"><path fill="#FFFFFF" d="M255.73,383.71c70.3,0,127.3-56.99,127.3-127.3s-56.99-127.3-127.3-127.3s-127.3,56.99-127.3,127.3S185.42,383.71,255.73,383.71z"/><linearGradient id="chrome-SVGID_1_" gradientUnits="userSpaceOnUse" x1="283.2852" y1="18.9008" x2="62.8264" y2="400.7473" gradientTransform="matrix(1 0 0 -1 0 514)"><stop offset="0" style="stop-color:#1E8E3E"/><stop offset="1" style="stop-color:#34A853"/></linearGradient><path fill="url(#chrome-SVGID_1_)" d="M145.48,320.08L35.26,129.17c-22.35,38.7-34.12,82.6-34.12,127.29s11.76,88.59,34.11,127.29c22.35,38.7,54.49,70.83,93.2,93.17c38.71,22.34,82.61,34.09,127.3,34.08l110.22-190.92v-0.03c-11.16,19.36-27.23,35.44-46.58,46.62c-19.35,11.18-41.3,17.07-63.65,17.07s-44.3-5.88-63.66-17.05C172.72,355.52,156.65,339.44,145.48,320.08z"/><linearGradient id="chrome-SVGID_2_" gradientUnits="userSpaceOnUse" x1="218.5901" y1="2.3333" x2="439.0491" y2="384.1796" gradientTransform="matrix(1 0 0 -1 0 514)"><stop offset="0" style="stop-color:#FCC934"/><stop offset="1" style="stop-color:#FBBC04"/></linearGradient><path fill="url(#chrome-SVGID_2_)" d="M365.96,320.08L255.74,510.99c44.69,0.01,88.59-11.75,127.29-34.1c38.7-22.34,70.84-54.48,93.18-93.18c22.34-38.7,34.1-82.61,34.09-127.3c-0.01-44.69-11.78-88.59-34.14-127.28H255.72l-0.03,0.02c22.35-0.01,44.31,5.86,63.66,17.03c19.36,11.17,35.43,27.24,46.61,46.59c11.18,19.35,17.06,41.31,17.06,63.66C383.03,278.77,377.14,300.72,365.96,320.08L365.96,320.08z"/><path fill="#1A73E8" d="M255.73,357.21c55.66,0,100.78-45.12,100.78-100.78s-45.12-100.78-100.78-100.78s-100.78,45.12-100.78,100.78S200.07,357.21,255.73,357.21z"/><linearGradient id="chrome-SVGID_3_" gradientUnits="userSpaceOnUse" x1="35.2587" y1="353.0303" x2="476.177" y2="353.0303" gradientTransform="matrix(1 0 0 -1 0 514)"><stop offset="0" style="stop-color:#D93025"/><stop offset="1" style="stop-color:#EA4335"/></linearGradient><path fill="url(#chrome-SVGID_3_)" d="M255.73,129.14h220.45C453.84,90.43,421.7,58.29,383,35.95C344.3,13.6,300.4,1.84,255.71,1.84c-44.69,0-88.59,11.77-127.29,34.12c-38.7,22.35-70.83,54.5-93.16,93.2l110.22,190.92l0.03,0.02c-11.18-19.35-17.08-41.3-17.08-63.65s5.87-44.31,17.04-63.66c11.17-19.36,27.24-35.43,46.6-46.6C211.42,135.01,233.38,129.13,255.73,129.14z"/></symbol>
  <symbol id="ds-icon-edge" viewBox="0 0 256 256"><defs><radialGradient id="edge-b" cx="161.83" cy="68.91" r="95.38" gradientTransform="matrix(1 0 0 -.95 0 248.84)" gradientUnits="userSpaceOnUse"><stop offset=".72" stop-opacity="0"/><stop offset=".95" stop-opacity=".53"/><stop offset="1"/></radialGradient><radialGradient id="edge-d" cx="-340.29" cy="62.99" r="143.24" gradientTransform="matrix(.15 -.99 -.8 -.12 176.64 -125.4)" gradientUnits="userSpaceOnUse"><stop offset=".76" stop-opacity="0"/><stop offset=".95" stop-opacity=".5"/><stop offset="1"/></radialGradient><radialGradient id="edge-e" cx="113.37" cy="570.21" r="202.43" gradientTransform="matrix(-.04 1 2.13 .08 -1179.54 -106.69)" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#35c1f1"/><stop offset=".11" stop-color="#34c1ed"/><stop offset=".23" stop-color="#2fc2df"/><stop offset=".31" stop-color="#2bc3d2"/><stop offset=".67" stop-color="#36c752"/></radialGradient><radialGradient id="edge-f" cx="376.52" cy="567.97" r="97.34" gradientTransform="matrix(.28 .96 .78 -.23 -303.76 -148.5)" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#66eb6e"/><stop offset="1" stop-color="#66eb6e" stop-opacity="0"/></radialGradient><linearGradient id="edge-a" x1="63.33" y1="84.03" x2="241.67" y2="84.03" gradientTransform="matrix(1 0 0 -1 0 266)" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#0c59a4"/><stop offset="1" stop-color="#114a8b"/></linearGradient><linearGradient id="edge-c" x1="157.35" y1="161.39" x2="45.96" y2="40.06" gradientTransform="matrix(1 0 0 -1 0 266)" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#1b9de2"/><stop offset=".16" stop-color="#1595df"/><stop offset=".67" stop-color="#0680d7"/><stop offset="1" stop-color="#0078d4"/></linearGradient></defs><path d="M235.68 195.46a93.73 93.73 0 01-10.54 4.71 101.87 101.87 0 01-35.9 6.46c-47.32 0-88.54-32.55-88.54-74.32A31.48 31.48 0 01117.13 105c-42.8 1.8-53.8 46.4-53.8 72.53 0 73.88 68.09 81.37 82.76 81.37 7.91 0 19.84-2.3 27-4.56l1.31-.44a128.34 128.34 0 0066.6-52.8 4 4 0 00-5.32-5.64z" transform="translate(-4.63 -4.92)" fill="url(#edge-a)"/><path d="M235.68 195.46a93.73 93.73 0 01-10.54 4.71 101.87 101.87 0 01-35.9 6.46c-47.32 0-88.54-32.55-88.54-74.32A31.48 31.48 0 01117.13 105c-42.8 1.8-53.8 46.4-53.8 72.53 0 73.88 68.09 81.37 82.76 81.37 7.91 0 19.84-2.3 27-4.56l1.31-.44a128.34 128.34 0 0066.6-52.8 4 4 0 00-5.32-5.64z" transform="translate(-4.63 -4.92)" style="isolation:isolate" opacity=".35" fill="url(#edge-b)"/><path d="M110.34 246.34A79.2 79.2 0 0187.6 225a80.72 80.72 0 0129.53-120c3.12-1.47 8.45-4.13 15.54-4a32.35 32.35 0 0125.69 13 31.88 31.88 0 016.36 18.66c0-.21 24.46-79.6-80-79.6-43.9 0-80 41.66-80 78.21a130.15 130.15 0 0012.11 56 128 128 0 00156.38 67.11 75.55 75.55 0 01-62.78-8z" transform="translate(-4.63 -4.92)" fill="url(#edge-c)"/><path d="M110.34 246.34A79.2 79.2 0 0187.6 225a80.72 80.72 0 0129.53-120c3.12-1.47 8.45-4.13 15.54-4a32.35 32.35 0 0125.69 13 31.88 31.88 0 016.36 18.66c0-.21 24.46-79.6-80-79.6-43.9 0-80 41.66-80 78.21a130.15 130.15 0 0012.11 56 128 128 0 00156.38 67.11 75.55 75.55 0 01-62.78-8z" transform="translate(-4.63 -4.92)" style="isolation:isolate" opacity=".41" fill="url(#edge-d)"/><path d="M156.94 153.78c-.81 1.05-3.3 2.5-3.3 5.66 0 2.61 1.7 5.12 4.72 7.23 14.38 10 41.49 8.68 41.56 8.68a59.56 59.56 0 0030.27-8.35 61.38 61.38 0 0030.43-52.88c.26-22.41-8-37.31-11.34-43.91-21.19-41.45-66.93-65.29-116.67-65.29a128 128 0 00-128 126.2c.48-36.54 36.8-66.05 80-66.05 3.5 0 23.46.34 42 10.07 16.34 8.58 24.9 18.94 30.85 29.21 6.18 10.67 7.28 24.15 7.28 29.52s-2.74 13.33-7.8 19.91z" transform="translate(-4.63 -4.92)" fill="url(#edge-e)"/><path d="M156.94 153.78c-.81 1.05-3.3 2.5-3.3 5.66 0 2.61 1.7 5.12 4.72 7.23 14.38 10 41.49 8.68 41.56 8.68a59.56 59.56 0 0030.27-8.35 61.38 61.38 0 0030.43-52.88c.26-22.41-8-37.31-11.34-43.91-21.19-41.45-66.93-65.29-116.67-65.29a128 128 0 00-128 126.2c.48-36.54 36.8-66.05 80-66.05 3.5 0 23.46.34 42 10.07 16.34 8.58 24.9 18.94 30.85 29.21 6.18 10.67 7.28 24.15 7.28 29.52s-2.74 13.33-7.8 19.91z" transform="translate(-4.63 -4.92)" fill="url(#edge-f)"/></symbol>
  <symbol id="ds-icon-firefox" viewBox="0 0 87.419 81.967"><defs><radialGradient gradientUnits="userSpaceOnUse" gradientTransform="translate(7978.7 8523.996)" r="80.797" cy="-8515.121" cx="-7907.187" id="ff-b"><stop stop-color="#ffbd4f" offset=".129"/><stop stop-color="#ffac31" offset=".186"/><stop stop-color="#ff9d17" offset=".247"/><stop stop-color="#ff980e" offset=".283"/><stop stop-color="#ff563b" offset=".403"/><stop stop-color="#ff3750" offset=".467"/><stop stop-color="#f5156c" offset=".71"/><stop stop-color="#eb0878" offset=".782"/><stop stop-color="#e50080" offset=".86"/></radialGradient><radialGradient gradientUnits="userSpaceOnUse" gradientTransform="translate(7978.7 8523.996)" r="80.797" cy="-8482.089" cx="-7936.711" id="ff-c"><stop stop-color="#960e18" offset=".3"/><stop stop-opacity=".74" stop-color="#b11927" offset=".351"/><stop stop-opacity=".343" stop-color="#db293d" offset=".435"/><stop stop-opacity=".094" stop-color="#f5334b" offset=".497"/><stop stop-opacity="0" stop-color="#ff3750" offset=".53"/></radialGradient><radialGradient gradientUnits="userSpaceOnUse" gradientTransform="translate(7978.7 8523.996)" r="58.534" cy="-8533.457" cx="-7926.97" id="ff-d"><stop stop-color="#fff44f" offset=".132"/><stop stop-color="#ffdc3e" offset=".252"/><stop stop-color="#ff9d12" offset=".506"/><stop stop-color="#ff980e" offset=".526"/></radialGradient><radialGradient gradientUnits="userSpaceOnUse" gradientTransform="translate(7978.7 8523.996)" r="38.471" cy="-8460.984" cx="-7945.648" id="ff-e"><stop stop-color="#3a8ee6" offset=".353"/><stop stop-color="#5c79f0" offset=".472"/><stop stop-color="#9059ff" offset=".669"/><stop stop-color="#c139e6" offset="1"/></radialGradient><radialGradient gradientUnits="userSpaceOnUse" gradientTransform="matrix(.972 -.235 .275 1.138 10095.002 7833.794)" r="20.397" cy="-8491.546" cx="-7935.62" id="ff-f"><stop stop-opacity="0" stop-color="#9059ff" offset=".206"/><stop stop-opacity=".064" stop-color="#8c4ff3" offset=".278"/><stop stop-opacity=".45" stop-color="#7716a8" offset=".747"/><stop stop-opacity=".6" stop-color="#6e008b" offset=".975"/></radialGradient><radialGradient gradientUnits="userSpaceOnUse" gradientTransform="translate(7978.7 8523.996)" r="27.676" cy="-8518.427" cx="-7937.731" id="ff-g"><stop stop-color="#ffe226" offset="0"/><stop stop-color="#ffdb27" offset=".121"/><stop stop-color="#ffc82a" offset=".295"/><stop stop-color="#ffa930" offset=".502"/><stop stop-color="#ff7e37" offset=".732"/><stop stop-color="#ff7139" offset=".792"/></radialGradient><radialGradient gradientUnits="userSpaceOnUse" gradientTransform="translate(7978.7 8523.996)" r="118.081" cy="-8535.981" cx="-7915.977" id="ff-h"><stop stop-color="#fff44f" offset=".113"/><stop stop-color="#ff980e" offset=".456"/><stop stop-color="#ff5634" offset=".622"/><stop stop-color="#ff3647" offset=".716"/><stop stop-color="#e31587" offset=".904"/></radialGradient><radialGradient gradientUnits="userSpaceOnUse" gradientTransform="matrix(.105 .995 -.653 .069 -4680.304 8470.187)" r="86.499" cy="-8522.859" cx="-7927.165" id="ff-i"><stop stop-color="#fff44f" offset="0"/><stop stop-color="#ffe847" offset=".06"/><stop stop-color="#ffc830" offset=".168"/><stop stop-color="#ff980e" offset=".304"/><stop stop-color="#ff8b16" offset=".356"/><stop stop-color="#ff672a" offset=".455"/><stop stop-color="#ff3647" offset=".57"/><stop stop-color="#e31587" offset=".737"/></radialGradient><radialGradient gradientUnits="userSpaceOnUse" gradientTransform="translate(7978.7 8523.996)" r="73.72" cy="-8508.176" cx="-7938.383" id="ff-j"><stop stop-color="#fff44f" offset=".137"/><stop stop-color="#ff980e" offset=".48"/><stop stop-color="#ff5634" offset=".592"/><stop stop-color="#ff3647" offset=".655"/><stop stop-color="#e31587" offset=".904"/></radialGradient><radialGradient gradientUnits="userSpaceOnUse" gradientTransform="translate(7978.7 8523.996)" r="80.686" cy="-8503.861" cx="-7918.923" id="ff-k"><stop stop-color="#fff44f" offset=".094"/><stop stop-color="#ffe141" offset=".231"/><stop stop-color="#ffaf1e" offset=".509"/><stop stop-color="#ff980e" offset=".626"/></radialGradient><linearGradient gradientTransform="translate(3.7 -.004)" gradientUnits="userSpaceOnUse" y2="74.468" x2="6.447" y1="12.393" x1="70.786" id="ff-a"><stop stop-color="#fff44f" offset=".048"/><stop stop-color="#ffe847" offset=".111"/><stop stop-color="#ffc830" offset=".225"/><stop stop-color="#ff980e" offset=".368"/><stop stop-color="#ff8b16" offset=".401"/><stop stop-color="#ff672a" offset=".462"/><stop stop-color="#ff3647" offset=".534"/><stop stop-color="#e31587" offset=".705"/></linearGradient><linearGradient gradientTransform="translate(3.7 -.004)" gradientUnits="userSpaceOnUse" y2="66.806" x2="15.267" y1="12.061" x1="70.013" id="ff-l"><stop stop-opacity=".8" stop-color="#fff44f" offset=".167"/><stop stop-opacity=".634" stop-color="#fff44f" offset=".266"/><stop stop-opacity=".217" stop-color="#fff44f" offset=".489"/><stop stop-opacity="0" stop-color="#fff44f" offset=".6"/></linearGradient></defs><path d="M79.616 26.827c-1.684-4.052-5.1-8.427-7.775-9.81a40.266 40.266 0 013.925 11.764l.007.065C71.391 17.92 63.96 13.516 57.891 3.924a47.099 47.099 0 01-.913-1.484 12.24 12.24 0 01-.427-.8 7.053 7.053 0 01-.578-1.535.1.1 0 00-.088-.1.138.138 0 00-.073 0c-.005 0-.013.009-.019.01l-.028.016.015-.026c-9.735 5.7-13.038 16.252-13.342 21.53a19.387 19.387 0 00-10.666 4.11 11.587 11.587 0 00-1-.757 17.968 17.968 0 01-.109-9.473 28.705 28.705 0 00-9.329 7.21h-.018c-1.536-1.947-1.428-8.367-1.34-9.708a6.928 6.928 0 00-1.294.687 28.225 28.225 0 00-3.788 3.245 33.845 33.845 0 00-3.623 4.347v.006-.007a32.733 32.733 0 00-5.2 11.743l-.052.256a61.89 61.89 0 00-.381 2.42c0 .029-.006.056-.009.085A36.937 36.937 0 005 41.042v.2a38.759 38.759 0 0076.954 6.554c.065-.5.118-.995.176-1.5a39.857 39.857 0 00-2.514-19.47zm-44.67 30.338c.181.087.351.18.537.264l.027.017q-.282-.135-.564-.281zm8.878-23.376zm31.952-4.934v-.037l.007.04z" fill="url(#ff-a)"/><path d="M79.616 26.827c-1.684-4.052-5.1-8.427-7.775-9.81a40.266 40.266 0 013.925 11.764v.037l.007.04a35.1 35.1 0 01-1.206 26.159c-4.442 9.53-15.194 19.3-32.024 18.825-18.185-.515-34.2-14.01-37.194-31.683-.545-2.787 0-4.2.274-6.465A28.876 28.876 0 005 41.042v.2a38.759 38.759 0 0076.954 6.554c.065-.5.118-.995.176-1.5a39.857 39.857 0 00-2.514-19.47z" fill="url(#ff-b)"/><path d="M79.616 26.827c-1.684-4.052-5.1-8.427-7.775-9.81a40.266 40.266 0 013.925 11.764v.037l.007.04a35.1 35.1 0 01-1.206 26.159c-4.442 9.53-15.194 19.3-32.024 18.825-18.185-.515-34.2-14.01-37.194-31.683-.545-2.787 0-4.2.274-6.465A28.876 28.876 0 005 41.042v.2a38.759 38.759 0 0076.954 6.554c.065-.5.118-.995.176-1.5a39.857 39.857 0 00-2.514-19.47z" fill="url(#ff-c)"/><path d="M60.782 31.383c.084.059.162.118.241.177a21.1 21.1 0 00-3.6-4.695C45.377 14.817 54.266.742 55.765.027l.015-.022c-9.735 5.7-13.038 16.252-13.342 21.53.452-.031.9-.07 1.362-.07a19.56 19.56 0 0116.982 9.918z" fill="url(#ff-d)"/><path d="M43.825 33.789c-.064.964-3.47 4.289-4.661 4.289-11.021 0-12.81 6.667-12.81 6.667.488 5.614 4.4 10.238 9.129 12.684.216.112.435.213.654.312q.569.252 1.138.466a17.235 17.235 0 005.043.973c19.317.906 23.059-23.1 9.119-30.066a13.38 13.38 0 019.345 2.269A19.56 19.56 0 0043.8 21.466c-.46 0-.91.038-1.362.069a19.387 19.387 0 00-10.666 4.11c.591.5 1.258 1.169 2.663 2.554 2.63 2.59 9.375 5.275 9.39 5.59z" fill="url(#ff-e)"/><path d="M43.825 33.789c-.064.964-3.47 4.289-4.661 4.289-11.021 0-12.81 6.667-12.81 6.667.488 5.614 4.4 10.238 9.129 12.684.216.112.435.213.654.312q.569.252 1.138.466a17.235 17.235 0 005.043.973c19.317.906 23.059-23.1 9.119-30.066a13.38 13.38 0 019.345 2.269A19.56 19.56 0 0043.8 21.466c-.46 0-.91.038-1.362.069a19.387 19.387 0 00-10.666 4.11c.591.5 1.258 1.169 2.663 2.554 2.63 2.59 9.375 5.275 9.39 5.59z" fill="url(#ff-f)"/><path d="M29.965 24.357c.314.2.573.374.8.53a17.968 17.968 0 01-.109-9.472 28.705 28.705 0 00-9.329 7.21c.189-.005 5.811-.106 8.638 1.732z" fill="url(#ff-g)"/><path d="M5.354 42.159c2.991 17.674 19.009 31.168 37.194 31.683 16.83.476 27.582-9.294 32.024-18.825a35.1 35.1 0 001.206-26.158v-.037c0-.03-.006-.046 0-.037l.007.065c1.375 8.977-3.191 17.674-10.329 23.555l-.022.05c-13.908 11.327-27.218 6.834-29.912 5q-.282-.135-.564-.281c-8.109-3.876-11.459-11.264-10.741-17.6a9.953 9.953 0 01-9.181-5.775 14.618 14.618 0 0114.249-.572 19.3 19.3 0 0014.552.572c-.015-.315-6.76-3-9.39-5.59-1.405-1.385-2.072-2.052-2.663-2.553a11.587 11.587 0 00-1-.758c-.23-.157-.489-.327-.8-.531-2.827-1.838-8.449-1.737-8.635-1.732h-.018c-1.536-1.947-1.428-8.367-1.34-9.708a6.928 6.928 0 00-1.294.687 28.225 28.225 0 00-3.788 3.245 33.845 33.845 0 00-3.638 4.337v.006-.007a32.733 32.733 0 00-5.2 11.743c-.019.079-1.396 6.099-.717 9.22z" fill="url(#ff-h)"/><path d="M57.425 26.865a21.1 21.1 0 013.6 4.7c.213.16.412.32.581.476 8.787 8.1 4.183 19.55 3.84 20.365 7.138-5.881 11.7-14.578 10.329-23.555C71.391 17.92 63.96 13.516 57.891 3.924a47.099 47.099 0 01-.913-1.484 12.24 12.24 0 01-.427-.8 7.053 7.053 0 01-.578-1.535.1.1 0 00-.088-.1.138.138 0 00-.073 0c-.005 0-.013.009-.019.01l-.028.016c-1.499.71-10.388 14.786 1.66 26.834z" fill="url(#ff-i)"/><path d="M61.6 32.036a8.083 8.083 0 00-.581-.476c-.079-.06-.157-.118-.241-.177a13.38 13.38 0 00-9.345-2.27c13.94 6.97 10.2 30.973-9.119 30.067a17.235 17.235 0 01-5.043-.973q-.569-.213-1.138-.466c-.219-.1-.438-.2-.654-.312l.027.017c2.694 1.839 16 6.332 29.912-5l.022-.05c.347-.81 4.951-12.263-3.84-20.36z" fill="url(#ff-j)"/><path d="M26.354 44.745s1.789-6.667 12.81-6.667c1.191 0 4.6-3.325 4.661-4.29a19.3 19.3 0 01-14.552-.571 14.618 14.618 0 00-14.249.572 9.953 9.953 0 009.181 5.775c-.718 6.337 2.632 13.725 10.741 17.6.181.087.351.18.537.264-4.733-2.445-8.641-7.07-9.129-12.683z" fill="url(#ff-k)"/><path d="M79.616 26.827c-1.684-4.052-5.1-8.427-7.775-9.81a40.266 40.266 0 013.925 11.764l.007.065C71.391 17.92 63.96 13.516 57.891 3.924a47.099 47.099 0 01-.913-1.484 12.24 12.24 0 01-.427-.8 7.053 7.053 0 01-.578-1.535.1.1 0 00-.088-.1.138.138 0 00-.073 0c-.005 0-.013.009-.019.01l-.028.016.015-.026c-9.735 5.7-13.038 16.252-13.342 21.53.452-.031.9-.07 1.362-.07a19.56 19.56 0 0116.982 9.918 13.38 13.38 0 00-9.345-2.27c13.94 6.97 10.2 30.973-9.119 30.067a17.235 17.235 0 01-5.043-.973q-.569-.213-1.138-.466c-.219-.1-.438-.2-.654-.312l.027.017q-.282-.135-.564-.281c.181.087.351.18.537.264-4.733-2.446-8.641-7.07-9.129-12.684 0 0 1.789-6.667 12.81-6.667 1.191 0 4.6-3.325 4.661-4.29-.015-.314-6.76-3-9.39-5.59-1.405-1.384-2.072-2.051-2.663-2.552a11.587 11.587 0 00-1-.758 17.968 17.968 0 01-.109-9.473 28.705 28.705 0 00-9.329 7.21h-.018c-1.536-1.947-1.428-8.367-1.34-9.708a6.928 6.928 0 00-1.294.687 28.225 28.225 0 00-3.788 3.245 33.845 33.845 0 00-3.623 4.347v.006-.007a32.733 32.733 0 00-5.2 11.743l-.052.256c-.073.34-.4 2.073-.447 2.445 0 .028 0-.03 0 0A45.094 45.094 0 005 41.042v.2a38.759 38.759 0 0076.954 6.554c.065-.5.118-.995.176-1.5a39.857 39.857 0 00-2.514-19.47zm-3.845 1.99l.007.042z" fill="url(#ff-l)"/></symbol>
  <symbol id="ds-icon-safari" viewBox="0 0 256 256"><defs><linearGradient x1="50%" y1="100%" x2="50%" y2="0%" id="safari-a"><stop stop-color="#DBDBDA" offset="25%"/><stop stop-color="#FFF" offset="100%"/></linearGradient><linearGradient x1="49.05%" y1="35.703%" x2="25.713%" y2="77.572%" id="safari-d"><stop stop-opacity="0" offset="0%"/><stop offset="100%"/></linearGradient><filter x="-50%" y="-50%" width="200%" height="200%" filterUnits="objectBoundingBox" id="safari-b"><feOffset dy="2" in="SourceAlpha" result="shadowOffsetOuter1"/><feGaussianBlur stdDeviation="2" in="shadowOffsetOuter1" result="shadowBlurOuter1"/><feColorMatrix values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.266007133 0" in="shadowBlurOuter1" result="shadowMatrixOuter1"/><feMerge><feMergeNode in="shadowMatrixOuter1"/><feMergeNode in="SourceGraphic"/></feMerge></filter><filter x="-50%" y="-50%" width="200%" height="200%" filterUnits="objectBoundingBox" id="safari-e"><feOffset dy="1" in="SourceAlpha" result="shadowOffsetOuter1"/><feGaussianBlur stdDeviation="2" in="shadowOffsetOuter1" result="shadowBlurOuter1"/><feColorMatrix values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 13 0" in="shadowBlurOuter1" result="shadowMatrixOuter1"/><feMerge><feMergeNode in="shadowMatrixOuter1"/><feMergeNode in="SourceGraphic"/></feMerge></filter><radialGradient cx="57.025%" cy="39.017%" fx="57.025%" fy="39.017%" r="61.032%" id="safari-c"><stop stop-color="#2ABCE1" offset="0%"/><stop stop-color="#2ABBE1" offset="11.363%"/><stop stop-color="#3375F8" offset="100%"/></radialGradient></defs><g transform="translate(4 2)"><circle fill="url(#safari-a)" filter="url(#safari-b)" cx="124" cy="124" r="124"/><circle fill="url(#safari-c)" cx="124" cy="124" r="114.7"/><g transform="translate(9.688 8.719)"><path d="M114.506 28.481c-.775 0-1.453-.581-1.453-1.356V6.878c0-.775.678-1.356 1.453-1.356s1.453.581 1.453 1.356v20.247c-.097.775-.678 1.356-1.453 1.356z" fill="#F3F3F3"/></g></g></symbol>
</svg>"""

ICONS = {
    "chrome": '<svg viewBox="0 0 512 512" aria-hidden="true"><use href="#ds-icon-chrome"></use></svg>',
    "edge": '<svg viewBox="0 0 256 256" aria-hidden="true"><use href="#ds-icon-edge"></use></svg>',
    "firefox": '<svg viewBox="0 0 87.419 81.967" aria-hidden="true"><use href="#ds-icon-firefox"></use></svg>',
    "safari": '<svg viewBox="0 0 256 256" aria-hidden="true"><use href="#ds-icon-safari"></use></svg>',
}

BROWSER_META = [
    {"key": "chrome", "label": "Chrome"},
    {"key": "edge", "label": "Edge"},
    {"key": "firefox", "label": "Firefox"},
    {"key": "safari", "label": "Safari"},
]

LEVEL_LABEL = {"yes": "Supported", "partial": "Partial", "no": "Not shipped"}

PREVIEW_TOKENS = """
  :host, :host *, :host *::before, :host *::after {
    box-sizing: border-box;
  }
  :host {
    display: block;
    color-scheme: light dark;
    --color-primary: #18181b;
    --color-bg: #fbfaf8;
    --color-text: #18181b;
    --color-text-muted: #75716a;
    --color-text-inverse: #fbfaf8;
    --color-border: #e3ddd0;
    --color-surface: #ffffff;
    --color-surface-offset: #f2efe8;
    --color-surface-dynamic: #e3ddd0;
    --color-surface-dark: #18181b;
    --color-error: #b3261e;
    --color-success: #2f7d4f;
    --color-accent: #cf4520;
    --radius-sm: 6px;
    --radius-md: 8px;
    --radius-lg: 8px;
    --space-1: .25rem;
    --space-2: .5rem;
    --space-3: .75rem;
    --space-4: 1rem;
    --space-5: 1.25rem;
    --space-6: 1.5rem;
    --space-8: 2rem;
    --header-height: 3rem;
    color: var(--color-text);
    font: 13px/1.5 var(--ds-sans, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif);
  }
  @media (prefers-color-scheme: dark) {
    :host {
      --color-primary: #f4f4f5;
      --color-bg: #18181b;
      --color-text: #f4f4f5;
      --color-text-muted: #a1a1aa;
      --color-text-inverse: #18181b;
      --color-border: #27272a;
      --color-surface: #27272a;
      --color-surface-offset: #202023;
      --color-surface-dynamic: #3f3f46;
      --color-surface-dark: #09090b;
      --color-accent: #f97316;
    }
  }
  .stage {
    position: relative;
    isolation: isolate;
    overflow: hidden;
    width: 100%;
    min-height: 180px;
    padding: 16px;
    display: grid;
    place-items: center;
    background-color: var(--color-bg);
    color: var(--color-text);
    contain: layout;
  }
  .stage > * { max-width: 100%; }
  .stage:has(details) { align-items: start; }
  img { max-width: 100%; height: auto; display: block; }
  button, .btn, a.btn {
    min-block-size: 36px;
    font: inherit;
    color: inherit;
  }
  :where(button), .btn, .btn-primary {
    padding: 0 .9rem;
    border: 1px solid var(--color-border);
    background: var(--color-surface);
    cursor: pointer;
    border-radius: var(--radius-md);
  }
  .btn-primary {
    background: var(--color-primary);
    color: var(--color-text-inverse);
    border-color: transparent;
  }
  :where(input:not([type="checkbox"]):not([type="radio"]):not([type="range"]):not([type="file"]):not([type="color"]):not([type="hidden"])),
  :where(select),
  :where(textarea) {
    font: inherit;
    color: inherit;
    padding: .45rem .65rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background: var(--color-surface);
  }
  :where(select) { padding-inline-end: 1.6rem; }
  :where(textarea) { resize: vertical; min-block-size: 5rem; }
  :where(input, select, textarea):focus-visible {
    outline: 2px solid var(--color-accent);
    outline-offset: 1px;
  }
  :where(input[type="checkbox"], input[type="radio"]) {
    inline-size: 16px;
    block-size: 16px;
  }
  :where(a) { color: var(--color-accent); text-underline-offset: 2px; }
  :where(table) { border-collapse: collapse; inline-size: 100%; }
  :where(th, td) { padding: .4rem .6rem; border-bottom: 1px solid var(--color-border); text-align: left; }
  :where(ul, ol) { padding-inline-start: 1.2rem; margin: 0; }
  .sr-only {
    position: absolute;
    inline-size: 1px; block-size: 1px;
    padding: 0; margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    clip-path: inset(50%);
    white-space: nowrap;
    border: 0;
  }
  .demo-note {
    margin: 0;
    max-inline-size: 36ch;
    text-align: center;
    color: var(--color-text-muted);
    font-size: 12px;
  }
"""

DOCUMENT_TOKENS = """
  *, *::before, *::after { box-sizing: border-box; }
  :root {
    color-scheme: light dark;
    --color-primary: light-dark(#18181b, #f4f4f5);
    --color-bg: light-dark(#fbfaf8, #18181b);
    --color-text: light-dark(#18181b, #f4f4f5);
    --color-text-muted: light-dark(#75716a, #a1a1aa);
    --color-text-inverse: light-dark(#fbfaf8, #18181b);
    --color-border: light-dark(#e3ddd0, #27272a);
    --color-surface: light-dark(#ffffff, #27272a);
    --color-surface-offset: light-dark(#f2efe8, #202023);
    --color-surface-dynamic: light-dark(#e3ddd0, #3f3f46);
    --color-surface-dark: light-dark(#18181b, #09090b);
    --color-error: #b3261e;
    --color-success: #2f7d4f;
    --color-accent: light-dark(#cf4520, #f97316);
    --radius-sm: 6px;
    --radius-md: 8px;
    --radius-lg: 8px;
    --space-1: .25rem;
    --space-2: .5rem;
    --space-3: .75rem;
    --space-4: 1rem;
    --space-5: 1.25rem;
    --space-6: 1.5rem;
    --space-8: 2rem;
    --header-height: 3rem;
  }
  html, body {
    margin: 0;
    padding: 0;
    min-height: 100%;
    background-color: var(--color-bg);
    color: var(--color-text);
    font: 13px/1.5 var(--ds-sans, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif);
  }
  body {
    padding: 16px;
    display: grid;
    place-items: center;
  }
  img { max-width: 100%; height: auto; display: block; }
  button, .btn, a.btn { min-block-size: 36px; font: inherit; color: inherit; }
  :where(button), .btn, .btn-primary {
    padding: 0 .9rem;
    border: 1px solid var(--color-border);
    background: var(--color-surface);
    cursor: pointer;
    border-radius: var(--radius-md);
  }
  .btn-primary {
    background: var(--color-primary);
    color: var(--color-text-inverse);
    border-color: transparent;
  }
  :where(input:not([type="checkbox"]):not([type="radio"]):not([type="range"]):not([type="file"]):not([type="color"]):not([type="hidden"])),
  :where(select),
  :where(textarea) {
    font: inherit;
    color: inherit;
    padding: .45rem .65rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background: var(--color-surface);
  }
  :where(select) { padding-inline-end: 1.6rem; }
  :where(textarea) { resize: vertical; min-block-size: 5rem; }
  :where(input, select, textarea):focus-visible {
    outline: 2px solid var(--color-accent);
    outline-offset: 1px;
  }
  :where(input[type="checkbox"], input[type="radio"]) {
    inline-size: 16px;
    block-size: 16px;
  }
  :where(a) { color: var(--color-accent); text-underline-offset: 2px; }
  :where(table) { border-collapse: collapse; inline-size: 100%; }
  :where(th, td) { padding: .4rem .6rem; border-bottom: 1px solid var(--color-border); text-align: left; }
  :where(ul, ol) { padding-inline-start: 1.2rem; margin: 0; }
  .sr-only {
    position: absolute;
    inline-size: 1px; block-size: 1px;
    padding: 0; margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    clip-path: inset(50%);
    white-space: nowrap;
    border: 0;
  }
  .demo-note {
    margin: 0;
    max-inline-size: 36ch;
    text-align: center;
    color: var(--color-text-muted);
    font-size: 12px;
  }
"""


def inline_md_to_html(text: str) -> str:
    """Build-time port of inlineMd(). Escapes source text before adding <code> and <strong>."""
    src = str(text or "")
    code_re = re.compile(r"`([^`]+)`")
    bold_re = re.compile(r"\*\*([^*]+(?:\*(?!\*)[^*]*)*)\*\*")
    
    def apply_bold(seg: str) -> str:
        return bold_re.sub(r"<strong>\1</strong>", seg)
        
    out = []
    last = 0
    for m in code_re.finditer(src):
        pre = html.escape(src[last:m.start()], quote=False)
        out.append(apply_bold(pre))
        out.append(f"<code>{html.escape(m.group(1), quote=False)}</code>")
        last = m.end()
    
    post = html.escape(src[last:], quote=False)
    out.append(apply_bold(post))
    return "".join(out)


def one_line(text: str) -> str:
    clean = re.sub(r"`+", "", str(text or ""))
    clean = re.sub(r"\*\*", "", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    first = re.split(r"(?<=[.!?])\s+", clean)[0] if clean else ""
    return (first[:137].rstrip() + "…") if len(first) > 140 else first


def highlight_css(src: str) -> str:
    out = []
    i = 0
    brace_depth = 0
    n = len(src)
    
    def push(cls: str | None, text: str) -> None:
        e = html.escape(text, quote=True)
        if cls:
            out.append(f'<span class="{cls}">{e}</span>')
        else:
            out.append(e)
            
    while i < n:
        c = src[i]
        
        if c == "/" and i + 1 < n and src[i + 1] == "*":
            end = src.find("*/", i + 2)
            stop = n if end < 0 else end + 2
            push("tok-com", src[i:stop])
            i = stop
            continue
            
        if c in {'"', "'"}:
            j = i + 1
            while j < n and src[j] != c:
                if src[j] == "\\":
                    j += 1
                j += 1
            j = min(j + 1, n)
            push("tok-str", src[i:j])
            i = j
            continue
            
        if c == "@":
            j = i + 1
            while j < n and (src[j].isalpha() or src[j] == "-"):
                j += 1
            push("tok-kw", src[i:j])
            i = j
            continue
            
        if c == "{":
            brace_depth += 1
            push("tok-punct", "{")
            i += 1
            continue
        if c == "}":
            brace_depth = max(0, brace_depth - 1)
            push("tok-punct", "}")
            i += 1
            continue
        if c in {";", "(", ")", ","}:
            push("tok-punct", c)
            i += 1
            continue
        if c == ":":
            push("tok-punct", ":")
            i += 1
            continue
            
        if c.isdigit() or c == "#":
            j = i
            if c == "#":
                j += 1
                while j < n and (src[j].isalnum()):
                    j += 1
                if j - i >= 4:
                    push("tok-num", src[i:j])
                    i = j
                    continue
                j = i
            if c.isdigit():
                j = i + 1
                while j < n and (src[j].isdigit() or src[j] == "."):
                    j += 1
                while j < n and (src[j].isalpha() or src[j] == "%"):
                    j += 1
                push("tok-num", src[i:j])
                i = j
                continue
                
        if c.isalpha() or c == "_" or (c == "-" and i + 1 < n and (src[i + 1].isalpha() or src[i + 1] == "-")):
            j = i
            if c == "-":
                j += 1
            while j < n and (src[j].isalnum() or src[j] in {"_", "-"}):
                j += 1
            ident = src[i:j]
            k = j
            while k < n and src[k].isspace():
                k += 1
            is_prop = brace_depth > 0 and k < n and src[k] == ":"
            push("tok-prop" if is_prop else None, ident)
            i = j
            continue
            
        push(None, c)
        i += 1
        
    return "".join(out)


def highlight_html(src: str) -> str:
    esc_html = html.escape(src, quote=True)
    tag_re = re.compile(r"&lt;(?:(!--[\s\S]*?--)|\/?)([a-zA-Z][\w-]*)((?:(?!&gt;).)*?)(\/?)&gt;")
    out = []
    last = 0
    for m in tag_re.finditer(esc_html):
        out.append(esc_html[last:m.start()])
        if m.group(1):
            out.append(f'&lt;<span class="tok-com">--{m.group(1)[:-2]}</span>--&gt;')
        else:
            name = m.group(2)
            attrs = m.group(3) or ""
            close = m.group(4) or ""
            def replace_attr(am):
                ws, an, eq, av = am.group(1), am.group(2), am.group(3), am.group(4)
                res = f'{ws}<span class="tok-attr">{an}</span>'
                if eq:
                    res += f'=<span class="tok-str">{av}</span>'
                return res
            attrs_hl = re.sub(
                r'(\s+)([a-zA-Z_:][\w:.-]*)(?:(=)(&quot;.*?&quot;|&#39;.*?&#39;|[^\s]+))?',
                replace_attr,
                attrs,
            )
            is_closing = m.group(0).startswith("&lt;/")
            out.append(f'&lt;{"/" if is_closing else ""}<span class="tok-tag">{name}</span>{attrs_hl}{close}&gt;')
        last = m.end()
    out.append(esc_html[last:])
    return "".join(out)


def tailwind_for(spell: dict) -> str:
    css = str(spell.get("css", "")).strip()
    if not css:
        return ""
    indented = "\n".join(("  " + line) if line else line for line in css.split("\n"))
    return "\n".join([
        "/* Tailwind v4 — drop into a global stylesheet processed by Tailwind. */",
        '@import "tailwindcss";',
        "",
        "@layer components {",
        indented,
        "}",
        "",
    ])


def slugify(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def browser_icon(key: str, level: str, label: str) -> str:
    icon_svg = ICONS.get(key, "")
    lvl_label = LEVEL_LABEL.get(level, level)
    return f'<span class="brow" data-level="{html.escape(level, quote=True)}" title="{html.escape(label, quote=True)}: {html.escape(lvl_label, quote=True)}">{icon_svg}</span>'


def browsers_row(spell: dict) -> str:
    return "".join(
        browser_icon(b["key"], spell.get("browsers", {}).get(b["key"], "no"), b["label"])
        for b in BROWSER_META
    )


def render_preview_box(spell: dict) -> str:
    env = spell.get("previewEnvironment", "shadow")
    raw_css = spell.get("previewCss") or spell.get("css") or ""
    raw_html = spell.get("previewHtml") or spell.get("html") or ""
    action = spell.get("previewAction", {})
    hint = action.get("hint", "")
    hint_tag = f'<span class="ds-hint" aria-hidden="true">{html.escape(hint)}</span>' if hint else ""
    
    if env == "document":
        doc_src = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    {DOCUMENT_TOKENS}
    {raw_css}
  </style>
</head>
<body>
  {raw_html}
</body>
</html>"""
        esc_doc = html.escape(doc_src, quote=True)
        return f"""<iframe class="ds-document" sandbox="allow-same-origin" srcdoc="{esc_doc}" aria-label="Live preview: {html.escape(spell['title'])}" style="width:100%;min-height:280px;border:0;display:block;background:var(--color-bg, #fbfaf8);"></iframe>{hint_tag}"""
    else:
        return f"""<template shadowrootmode="open">
  <style>
    {PREVIEW_TOKENS}
    {raw_css}
    .ds-hint {{
      position: absolute;
      right: 8px;
      bottom: 8px;
      z-index: 2;
      padding: 4px 8px;
      border-radius: 999px;
      background: var(--color-surface-dark);
      color: var(--color-text-inverse);
      font: 600 10px/1 var(--ds-sans, ui-sans-serif, system-ui, sans-serif);
      letter-spacing: .02em;
      pointer-events: none;
      opacity: .8;
    }}
    .ds-runway {{
      overflow-y: auto;
      overscroll-behavior: contain;
      scrollbar-width: thin;
    }}
    .ds-runway__pad {{ block-size: 60vh; }}
  </style>
  <div class="stage" style="min-height:280px">
    {raw_html}
    {hint_tag}
  </div>
</template>"""


def render_drawer(spell: dict) -> str:
    status_cls = "ok" if spell["status"] == "baseline" else "warn" if spell["status"] == "newer" else "muted"
    browser_items = "".join(
        f'<li><span class="bname"><span class="brow" data-level="{html.escape(spell.get("browsers", {}).get(b["key"], "no"))}">{ICONS.get(b["key"], "")}</span>{html.escape(b["label"])}</span><span class="blevel" data-level="{html.escape(spell.get("browsers", {}).get(b["key"], "no"))}">{html.escape(LEVEL_LABEL.get(spell.get("browsers", {}).get(b["key"], "no"), ""))}</span></li>'
        for b in BROWSER_META
    )
    desc_html = inline_md_to_html(spell.get("description", "")) or "A zero-JS CSS technique."
    tailwind_src = tailwind_for(spell)
    preview_box = render_preview_box(spell)
    
    return f"""
  <div class="drawer" id="drawer-{spell['id']}" popover="auto" role="dialog" aria-modal="true" aria-labelledby="drawer-title-{spell['id']}">
    <header class="drawer__head">
      <div class="drawer__head-main">
        <p class="drawer__eyebrow">
          <span>{spell['id']}</span>
          <span aria-hidden="true">·</span>
          <span>{spell['jsLabel']}</span>
        </p>
        <h2 class="drawer__title" id="drawer-title-{spell['id']}">{html.escape(spell['title'])}</h2>
        <p class="drawer__meta">
          <span class="drawer__cat">{html.escape(spell['category'])}</span>
          <span aria-hidden="true">/</span>
          <span class="label label--{status_cls}"><span class="label__dot" aria-hidden="true"></span>{html.escape(spell['statusLabel'])}</span>
        </p>
      </div>
      <button class="drawer__close" type="button" popovertarget="drawer-{spell['id']}" popovertargetaction="hide" aria-label="Close panel">×</button>
    </header>

    <div class="drawer__scroll">
      <p class="drawer__desc">{desc_html}</p>

      <section class="sect" aria-labelledby="browsers-label-{spell['id']}">
        <h3 class="sect__label" id="browsers-label-{spell['id']}">Browser support <span>{html.escape(spell['feature'])}</span></h3>
        <ul class="browser-list">{browser_items}</ul>
        <p class="support-note">{html.escape(spell['supportNote'])}</p>
      </section>

      <section class="sect" aria-labelledby="preview-label-{spell['id']}">
        <h3 class="sect__label" id="preview-label-{spell['id']}">Live preview <span>isolated sandbox</span></h3>
        <div class="preview-host preview-host--lg" id="preview-host-{spell['id']}">
          {preview_box}
        </div>
      </section>

      <section class="sect" aria-labelledby="source-label-{spell['id']}">
        <h3 class="sect__label" id="source-label-{spell['id']}">Source <span>Modern CSS / Tailwind v4 / HTML</span></h3>
        <div class="code drawer__code code__tabs">
          <details name="tabs-{spell['id']}" class="code__tab-group" open>
            <summary class="code__tab">Modern CSS</summary>
            <div class="code__view-wrap"><pre class="code__view" tabindex="0"><code>{highlight_css(spell['css'])}</code></pre></div>
          </details>
          <details name="tabs-{spell['id']}" class="code__tab-group">
            <summary class="code__tab">Tailwind v4</summary>
            <div class="code__view-wrap"><pre class="code__view" tabindex="0"><code>{highlight_css(tailwind_src)}</code></pre></div>
          </details>
          <details name="tabs-{spell['id']}" class="code__tab-group">
            <summary class="code__tab">HTML</summary>
            <div class="code__view-wrap"><pre class="code__view" tabindex="0"><code>{highlight_html(spell['previewHtml'] or spell['html'] or '<!-- CSS-only; no extra markup required. -->')}</code></pre></div>
          </details>
        </div>
      </section>
    </div>

    <footer class="drawer__foot">
      <p class="drawer__hint">Zero JS · copy and paste freely</p>
      <button class="btn btn--primary" type="button" popovertarget="drawer-{spell['id']}" popovertargetaction="hide">Close</button>
    </footer>
  </div>"""


def render_row(spell: dict) -> str:
    desc = one_line(spell.get("description", ""))
    desc_p = f'<p class="row__desc">{html.escape(desc)}</p>' if desc else ""
    browsers = browsers_row(spell)
    tags = html.escape(f"{spell['category']} {spell['status']} {spell.get('feature', '')} {spell['title']}".lower(), quote=True)
    return f"""
  <li class="row" data-id="{spell['id']}" data-cat="{html.escape(spell['category'], quote=True)}" data-status="{html.escape(spell['status'], quote=True)}" data-tags="{tags}">
    <div class="row__main">
      <h2 class="row__title">
        <button class="row__hit" type="button" popovertarget="drawer-{spell['id']}" aria-haspopup="dialog">{html.escape(spell['title'])}</button>
      </h2>
      {desc_p}
    </div>
    <div class="row__aside">
      <button class="row__id" type="button" popovertarget="drawer-{spell['id']}" aria-label="Open {spell['id']} details">{spell['id']}</button>
      <div class="row__browsers" aria-label="Browser support">{browsers}</div>
      <button class="row__copy" type="button" popovertarget="drawer-{spell['id']}" aria-label="Inspect {html.escape(spell['title'], quote=True)}">Inspect</button>
    </div>
  </li>"""


def render_index_html(catalogue: dict, out_path: Path) -> None:
    spells = catalogue["spells"]
    total = len(spells)
    
    by_cat = {}
    for s in spells:
        by_cat.setdefault(s["category"], []).append(s)
    
    order = [c for c in CAT_ORDER if c in by_cat]
    for c in by_cat:
        if c not in order:
            order.append(c)
            
    cat_radios = [f'<label class="nav-item"><input type="radio" name="cat" value="all" checked class="sr-only"><span>All</span><span class="nav-item__count" aria-hidden="true">{total}</span></label>']
    for c in order:
        cnt = len(by_cat[c])
        cat_radios.append(f'<label class="nav-item"><input type="radio" name="cat" value="{html.escape(c, quote=True)}" class="sr-only"><span>{html.escape(c)}</span><span class="nav-item__count" aria-hidden="true">{cnt}</span></label>')
    cat_nav = "\n            ".join(cat_radios)
    
    status_radios = [
        '<label class="nav-item"><input type="radio" name="status" value="all" checked class="sr-only"><span>Any status</span></label>',
        '<label class="nav-item"><input type="radio" name="status" value="baseline" class="sr-only"><span>Baseline</span></label>',
        '<label class="nav-item"><input type="radio" name="status" value="newer" class="sr-only"><span>Newer</span></label>',
        '<label class="nav-item"><input type="radio" name="status" value="progressive" class="sr-only"><span>Progressive</span></label>',
    ]
    status_nav = "\n            ".join(status_radios)
    
    browser_legend_items = "".join(
        f'<li>{browser_icon(b["key"], "yes", b["label"])}<span>{html.escape(b["label"])}</span></li>'
        for b in BROWSER_META
    )
    
    cat_blocks = []
    for c in order:
        items = by_cat[c]
        c_slug = slugify(c)
        rows_html = "".join(render_row(s) for s in items)
        cat_blocks.append(f"""
        <section class="cat-block" data-cat="{html.escape(c, quote=True)}" aria-labelledby="cat-{c_slug}">
          <div class="cat-block__head">
            <h2 class="cat-block__title" id="cat-{c_slug}">{html.escape(c)}</h2>
            <div class="cat-block__head-right">
              <span class="cat-block__count">{len(items)} spell{'s' if len(items) != 1 else ''}</span>
            </div>
          </div>
          <ul class="row-list" aria-label="{html.escape(c, quote=True)}">{rows_html}
          </ul>
        </section>""")
    catalogue_content = "\n".join(cat_blocks)
    
    drawers_html = "\n".join(render_drawer(s) for s in spells)
    
    full_html = f"""<!doctype html>
<html lang="en" dir="ltr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>Design Spells — zero-JS CSS techniques</title>
  <meta name="description" content="150 zero-JavaScript design techniques. Browse by category, preview each spell, copy the source, and see which browsers support it.">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Design Spells — zero-JS CSS techniques">
  <meta property="og:description" content="150 zero-JavaScript design techniques. Browse by category, preview each spell, copy the source, and see which browsers support it.">
  <meta property="og:url" content="https://design-spells.hultsan20.workers.dev/">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="Design Spells — zero-JS CSS techniques">
  <meta name="twitter:description" content="150 zero-JavaScript design techniques. Browse by category, preview each spell, copy the source, and see which browsers support it.">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Ctext x='1' y='13' font-size='13'%3E%E2%9C%B6%3C/text%3E%3C/svg%3E">
  <link rel="stylesheet" href="./styles.css">
  <script src="./search.js" defer></script>
</head>
<body>

  {ICON_SPRITE}

  <a class="skip-link" href="#main">Skip to content</a>

  <header class="site-head">
    <div class="site-head__row">
      <p class="brand">
        Design Spells<span class="brand__star" aria-hidden="true">*</span>
        <span class="brand__tag">Zero-JS CSS techniques</span>
      </p>
      <div class="head-meta">
        <p class="counter" id="counter" aria-live="polite">Showing {total} of {total} spells</p>
        <a class="sponsor" href="https://github.com/sponsors/FullThrottle83" target="_blank" rel="noopener">
          Sponsor on GitHub <span aria-hidden="true">↗</span>
        </a>
      </div>
    </div>
  </header>

  <main class="shell" id="main">

    <section class="intro">
      <h1>A catalogue of CSS that does the work itself.</h1>
      <p>
        {total} interaction, layout, and polish techniques. No client JavaScript.
        Click a spell to preview it, then copy the source.
      </p>
      <form class="search" id="search-form" role="search" action="#main">
        <div class="search__field">
          <input class="search__input" id="search" name="q" type="search"
                 placeholder="Search by name, category, feature, or status…"
                 aria-label="Search spells"
                 autocomplete="off" autocapitalize="off" spellcheck="false">
          <kbd class="search__kbd" aria-hidden="true">/</kbd>
        </div>
      </form>
    </section>

    <div class="browse">

      <nav class="browse__nav" aria-label="Browse spells">
        <div class="nav-group" role="group" aria-label="Categories">
          <h2 class="nav-group__label">Category</h2>
          <div class="nav-list" id="cat-list">
            {cat_nav}
          </div>
        </div>

        <div class="nav-group" role="group" aria-label="Support status">
          <h2 class="nav-group__label">Status</h2>
          <div class="nav-list" id="status-list">
            {status_nav}
          </div>
        </div>

        <div class="nav-group">
          <h2 class="nav-group__label">Browsers</h2>
          <ul class="nav-legend" id="browser-legend">
            {browser_legend_items}
          </ul>
          <p class="nav-legend__key">Green supported · amber partial · red missing</p>
        </div>
      </nav>

      <div class="browse__list" id="catalogue">
{catalogue_content}
      </div>

    </div>

    <footer class="shell-note">
      <span>Raw CSS only — no JavaScript ships with any spell</span>
      <span>Open source · contributions via pull request</span>
    </footer>
  </main>

  <!-- Pre-rendered modal drawers for all 150 spells with Declarative Shadow DOM and native code tabs -->
  <div class="drawers-layer" id="drawers-layer">
{drawers_html}
  </div>

</body>
</html>
"""
    out_path.write_text(full_html, encoding="utf-8")
    print(f"wrote {out_path.name} {out_path.stat().st_size} bytes")


def main() -> None:
    spells = parse_spells(SRC)
    print("parsed spells:", len(spells))

    payload = []
    corrected = 0
    for spell in spells:
        feature_keys = detect_features(spell["css"], spell["html"], spell["title"], spell["status"])
        browsers_support = combine_support(feature_keys)
        derived_status = derive_status(browsers_support)
        environment = preview_environment(spell["css"])
        status_label = derived_status
        status = derived_status.lower()
        if derived_status != spell["statusLabel"]:
            corrected += 1
            print(f"  status corrected {spell['id']}: {spell['statusLabel']} -> {derived_status} ({','.join(feature_keys)})")
        item = {
            **spell,
            "status": status,
            "statusLabel": status_label,
            "previewEnvironment": environment,
            "previewAction": preview_action(spell["css"], spell["html"]),
            "previewHtml": polish_preview(spell),
            "previewCss": rewrite_preview_assets(
                spell["css"]
                if environment == "document"
                else rewrite_preview_css(spell["css"])
            ),
            "featureKeys": feature_keys,
            "feature": feature_label(feature_keys),
            "browsers": browsers_support,
            "supportNote": feature_note(feature_keys),
        }
        payload.append(item)
    print(f"status labels corrected from support data: {corrected}")

    cats = {}
    for s in payload:
        cats[s["category"]] = cats.get(s["category"], 0) + 1
    print("categories:", cats)

    catalogue = {
        "supportAsOf": SUPPORT_AS_OF,
        "total": len(payload),
        "spells": payload,
    }

    # Machine-readable copy for AI agents, MCP servers, and tooling. It is
    # described by schema/spells.schema.json (and schema/spells.d.ts for
    # TypeScript consumers) — the strict contract everything else keys off.
    json_doc = {
        "$schema": "https://design-spells.hultsan20.workers.dev/spells.schema.json",
        **catalogue,
    }
    json_text = json.dumps(json_doc, ensure_ascii=False, indent=2) + "\n"
    (ROOT / "public" / "spells.json").write_text(json_text, encoding="utf-8")
    print("wrote public/spells.json", (ROOT / "public" / "spells.json").stat().st_size, "bytes")

    # Static HTML emission for the Zero-JS catalogue
    render_index_html(catalogue, ROOT / "public" / "index.html")


if __name__ == "__main__":
    main()
