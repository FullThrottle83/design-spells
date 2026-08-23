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

    classic = (
        "/* generated by scripts/build.py — do not edit by hand */\n"
        "window.DESIGN_SPELLS = "
        + json.dumps(catalogue, ensure_ascii=False)
        + ";\n"
    )
    (ROOT / "public" / "spells.js").write_text(classic, encoding="utf-8")
    print("wrote public/spells.js", (ROOT / "public" / "spells.js").stat().st_size, "bytes")

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


if __name__ == "__main__":
    main()
