"""Pilot 01 editorial fixtures. No authored technique overrides live here.

HTML also supplies CSS-only bundle examples. Scenic CSS is only included by
build_pages in hosted/downloaded demos (including the ds-5 comparison).
"""

HINTS = {
    "ds-5": "Hover or Tab through the navigation. Follow a link to its section; the current page keeps its underline.",
    "ds-12": "Swipe or scroll sideways. Keyboard: Tab into the gallery, then use the arrow keys. Each print snaps into place.",
    "ds-16": "Focus a field and type. Move away, then clear it: the label stays raised only while focused or filled. Nothing is submitted.",
    "ds-21": "Choose a chapter to highlight its destination. Choose another to repeat. The outline remains after the pulse.",
    "ds-37": "Choose Sidebar or Feature to change the container, not the viewport. Above 420px the card becomes two columns.",
    "ds-95": "Hover or keyboard-focus the chart to emphasize all six bars. Open the values below for the exact data.",
}

# Small original vector studies: embedded and self-contained in downloads.
# They are editorial artwork, not representations of another spell's behavior.
def print_art(kind: int) -> str:
    paths = [
        '<rect width="640" height="440" fill="#dfd4bf"/><circle cx="420" cy="128" r="65" fill="#c15b3c"/><path d="M110 440V225a145 145 0 0 1 290 0v215Z" fill="#303c35"/><path d="M185 440V225a70 70 0 0 1 140 0v215Z" fill="#b0b39b"/><path d="M0 375h640v65H0Z" fill="#303c35"/>',
        '<rect width="640" height="440" fill="#d7e2dd"/><path d="M0 350 180 85 360 350Z" fill="#254f4b"/><path d="m230 350 170-225 220 225Z" fill="#71988a"/><circle cx="500" cy="96" r="42" fill="#e6b66c"/><path d="M0 380h640" stroke="#254f4b" stroke-width="16"/>',
        '<rect width="640" height="440" fill="#e8c6b0"/><path d="M0 280Q160 120 320 280T640 280V440H0Z" fill="#ae503b"/><path d="M0 370Q160 210 320 370T640 370V440H0Z" fill="#592f2d"/><circle cx="320" cy="115" r="64" fill="#f7e7cd"/>',
    ]
    return '<svg class="study-art" viewBox="0 0 640 440" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">' + paths[kind] + '</svg>'

HTML = {
    "5": '<div class="journal"><header class="journal-head"><strong>FORM / FIELD</strong><span>Independent design journal</span></header>'
         '<nav class="journal-nav" aria-label="Journal"><a class="nav-link" href="#overview">Overview</a><a class="nav-link" href="#field-notes">Field notes</a><a class="nav-link" href="#edition" aria-current="page">Edition 08</a></nav>'
         '<section id="edition" class="journal-feature"><p class="scene-kicker">Edition 08 · Autumn 2026</p><h1>Less, but<br>with intention.</h1><p>Objects, spaces and ideas that make room for a slower kind of living.</p></section>'
         '<div class="journal-notes"><section id="overview"><h2>01 / Overview</h2><p>A study in considered design. Start with what matters; leave room for the rest.</p></section><section id="field-notes"><h2>02 / Field notes</h2><p>From the workshop: material honesty, useful details and everyday rituals.</p></section></div></div>',
    "12": '<div class="print-gallery"><header><p class="scene-kicker">The print room / Collection 03</p><h1>Studies in stillness.</h1><p>Three architectural compositions. One continuous shelf.</p></header><div class="gallery" tabindex="0" role="region" aria-label="Three art prints">' + ''.join(
        f'<figure>{print_art(i)}<figcaption><span>0{i+1} / {name}</span><small>{note}</small></figcaption></figure>'
        for i, (name, note) in enumerate([('Archway', 'Terracotta & stone'), ('Highlands', 'Pine & morning mist'), ('Tidal forms', 'Clay & evening light')])
    ) + '</div><p class="gallery-foot">← Scroll to explore → <span>Original vector studies · 2026</span></p></div>',
    "16": '<div class="profile-sheet"><p class="scene-kicker">Member profile / Local preview</p><h1>A proper introduction.</h1><p>Your details, with labels that never lose their place.</p><div class="profile-fields">'
          '<div class="form-group"><input id="profile-name" name="name" autocomplete="name" placeholder=" "><label for="profile-name">Full name</label></div>'
          '<div class="form-group"><input id="profile-email" name="email" type="email" autocomplete="email" placeholder=" "><label for="profile-email">Email address</label></div></div><p class="profile-foot">No account created. No data sent.<br>Just a small detail that makes a form feel better.</p></div>',
    "21": '<article class="reading-guide" id="guide"><header><p class="scene-kicker">The studio handbook / 04</p><h1>Make the destination clear.</h1><p>A reading guide with native, shareable chapter links.</p></header><nav aria-label="Chapters"><a href="#materials">01 Materials ↗</a><a href="#process">02 Process ↗</a><a href="#care">03 Care ↗</a></nav>'
          '<div class="guide-chapters"><section id="materials" tabindex="-1"><small>01 / The starting point</small><h2>Material matters.</h2><p>Choose materials that age with grace: honest timber, uncoated paper and well-made textiles.</p></section><section id="process" tabindex="-1"><small>02 / The method</small><h2>Leave room to refine.</h2><p>Sketch, make, test. The most useful details often emerge on the second pass.</p></section><section id="care" tabindex="-1"><small>03 / The long view</small><h2>Built to be kept.</h2><p>Repair is part of the design. Care for the things you use, and let them tell their story.</p></section></div><a class="guide-reset" href="#guide">Clear highlight ↑</a></article>',
    "37": '<div class="container-lab"><header><p class="scene-kicker">Layout lab / One component, two contexts</p><h1>Space sets the pace.</h1></header><fieldset class="size-controls"><legend>Available container space</legend><label><input type="radio" name="card-size" id="size-compact" checked> Sidebar</label><label><input type="radio" name="card-size" id="size-wide"> Feature</label></fieldset><div class="container-boundary"><div class="card-container"><article class="adaptive-card"><div class="card-media">' + print_art(1) + '</div><div class="card-copy"><p class="scene-kicker">Field guide / 06</p><h2>The quiet route.</h2><p>A weekend among the pines. Notes on finding a little more space, closer to home.</p><span class="card-meta">6 min read · Outdoors</span></div></article></div></div><p class="container-note">The dashed line is the container. On narrow screens both choices stay stacked; widen the window to see the 420px threshold.</p><p class="container-fallback">Without container queries, this remains a readable stacked card.</p></div>',
}

# A minimal CSS-only integration fixture must not expose scene radio controls
# whose demo-only sizing CSS is intentionally absent from the bundle.
INTEGRATION_CARD_HTML = (
    '<div class="card-container" tabindex="0" role="region" aria-label="Resizable field guide card" '
    'style="resize:horizontal;overflow:auto;width:600px;min-width:180px;max-width:100%">'
    '<article class="adaptive-card"><div class="card-media">' + print_art(1) + '</div>'
    '<div><h3>The quiet route</h3><p>A weekend among the pines. Layout follows the container.</p></div></article></div>'
)

COMMON_CSS = """
/* Demo-only art direction; the spell rules above remain authoritative. */
.stage:has(.showcase) {padding:clamp(18px,4vw,56px);min-height:min(100dvh,760px);align-content:center}
.showcase {min-width:0;width:min(100%,920px);font-size:16px;line-height:1.6;--color-primary:light-dark(#254f4b,#9ed5c4)}
.showcase h1 {font-family:Georgia,serif;font-weight:400;letter-spacing:-.045em;font-size:clamp(32px,4.5vw,58px);line-height:1.08;margin:14px 0 20px;text-wrap:balance}
.showcase h2 {line-height:1.2;letter-spacing:-.025em}
.showcase p {margin:0 0 20px}
.showcase .scene-kicker {font:600 11px/1.5 ui-monospace,monospace;letter-spacing:.12em;text-transform:uppercase;margin:0}
.showcase a {color:inherit}
.showcase :where(a,input,summary,[tabindex="0"]):focus-visible {outline:2px solid var(--color-primary);outline-offset:5px}
.showcase svg {display:block;width:100%;height:auto}
.showcase .scene-instruction {border-top:1px solid var(--color-border);padding-top:18px;margin:24px 0 0;font-size:13px;max-width:70ch}
.showcase small {font-size:12px}
"""
CSS = {
    "ds-5": """
html:has(.journal) {scroll-behavior:auto}
.journal-head {display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:12px;letter-spacing:.06em;padding-bottom:24px}
.journal-head strong {font-size:18px;letter-spacing:-.03em}
.journal-head span {color:var(--color-text-muted)}
.journal-nav {display:flex;gap:clamp(18px,4vw,48px);border-block:1px solid var(--color-border);padding-block:8px;font-size:14px}
.journal-feature {padding:42px clamp(20px,5vw,56px);margin-top:30px;background:light-dark(#e8e5d9,#262e29);border-left:5px solid var(--color-primary)}
.journal-feature h1 {font-size:clamp(44px,6vw,76px)}
.journal-feature p:last-child {max-width:40ch;margin:0}
.journal-notes {display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:30px;margin-top:24px}
.journal-notes h2 {font:600 12px ui-monospace,monospace}.journal-notes p {font-size:14px;margin:0}
""",
    "ds-12": """
.print-gallery {min-width:0;width:100%}.print-gallery header {margin-bottom:30px}
.print-gallery .gallery {width:100%;padding-bottom:14px;scrollbar-width:thin}
.print-gallery figure {margin:0;min-width:0;background:var(--color-surface);border:1px solid var(--color-border)}
.print-gallery figcaption {display:grid;gap:4px;padding:18px}.print-gallery figcaption span {font-family:Georgia,serif;font-size:24px}
.print-gallery figcaption small {color:var(--color-text-muted)}
.print-gallery .gallery-foot {display:flex;flex-wrap:wrap;justify-content:space-between;gap:12px;font-size:12px;margin-top:16px}
""",
    "ds-16": """
.showcase:has(.profile-sheet) {max-width:520px}
.profile-sheet {background:var(--color-surface);border:1px solid var(--color-border);border-top:5px solid var(--color-primary);padding:clamp(22px,4vw,48px)}
.profile-sheet h1 {font-size:clamp(32px,4vw,44px)}
.profile-fields {display:grid;gap:22px;margin:32px 0}.profile-fields input {font-size:16px;border-radius:6px;min-height:62px}
.profile-sheet .profile-foot {font-size:12px;margin:0;color:var(--color-text-muted)}
""",
    "ds-21": """
html:has(.reading-guide) {scroll-behavior:auto}
.reading-guide {max-width:760px;margin:auto}.reading-guide header {max-width:540px}
.reading-guide nav {display:flex;gap:8px 24px;flex-wrap:wrap;padding-block:8px 24px;font-size:14px}
.reading-guide nav a,.guide-reset {display:inline-flex;align-items:center;min-height:44px}
.guide-chapters {display:grid;gap:24px}.guide-chapters section {padding:24px;background:var(--color-surface-offset);scroll-margin-block:24px}
.guide-chapters h2 {font:400 28px/1.2 Georgia,serif;margin:10px 0}.guide-chapters p {margin:0;max-width:60ch;font-size:15px}
.guide-chapters small {text-transform:uppercase;letter-spacing:.08em}.guide-reset {margin-top:20px;font-size:13px}
""",
    "ds-37": """
.size-controls {border:0;padding:0;display:flex;gap:12px;flex-wrap:wrap;margin:24px 0}
.size-controls legend {font-size:12px;margin-bottom:8px}.size-controls label {display:flex;gap:8px;align-items:center;min-height:44px;padding:8px 16px;border:1px solid var(--color-border);cursor:pointer}
.size-controls label:has(:checked) {background:var(--color-surface-offset);border-color:var(--color-primary)}
.container-boundary {padding:16px;border:1px dashed var(--color-text-muted)}
.container-lab .card-container {width:min(100%,240px);margin-inline:auto}
.container-lab:has(#size-wide:checked) .card-container {width:100%}
.container-lab .adaptive-card {background:var(--color-surface);border:1px solid var(--color-border)}
.card-media {overflow:hidden}.card-media svg {height:100%;object-fit:cover}.card-copy {padding:22px}.card-copy h2 {font:400 32px/1.1 Georgia,serif;margin:12px 0}.card-copy p:not(.scene-kicker) {font-size:14px}.card-meta {font:11px ui-monospace,monospace}
.container-lab .container-note,.container-fallback {font-size:12px;margin:16px 0 0;max-width:65ch}
@supports (container-type:inline-size) {.container-fallback {display:none}}
""",
    "ds-95": """
.showcase:has(.capacity-report) {max-width:620px}
.capacity-report {padding:clamp(22px,4vw,44px);border:1px solid var(--color-border);background:var(--color-surface)}
.capacity-report h1 {font:400 32px/1.1 Georgia,serif;margin-bottom:28px}
.capacity-plot {max-width:32rem}
.capacity-total {display:flex;align-items:baseline;gap:14px;margin-bottom:28px}.capacity-total strong {font-size:56px;letter-spacing:-.06em;line-height:1}.capacity-total span {font-size:13px;color:var(--color-text-muted)}
.chart-scale {display:flex;justify-content:space-between;font:11px ui-monospace,monospace;margin-bottom:10px}
.chart-months {display:flex;gap:4px;border-top:1px solid var(--color-border);padding-top:10px;margin-top:8px;font:11px ui-monospace,monospace}.chart-months span {flex:1;text-align:center}
.capacity-report details {margin-top:24px;font-size:13px}.capacity-report summary {cursor:pointer;min-height:44px;align-content:center}.capacity-report table {margin-top:8px}
""",
}


def scene_html(sid: str, raw_html: str) -> str:
    if sid == "ds-95":
        rows = ''.join(f'<tr><th scope="row">{m}</th><td>{v}%</td></tr>' for m, v in zip(['Jan','Feb','Mar','Apr','May','Jun'], [34,58,41,72,66,90]))
        raw_html = '<article class="capacity-report"><p class="scene-kicker">Studio operations / Jan—Jun 2026</p><h1>Room for good work.</h1><div class="capacity-total"><strong>90%</strong><span>June capacity booked<br>+24 points from May</span></div><div class="capacity-plot"><div class="chart-scale"><span>Booked capacity</span><span>0—100%</span></div>' + raw_html + '<div class="chart-months" aria-hidden="true">' + ''.join(f'<span>{m}</span>' for m in ['Jan','Feb','Mar','Apr','May','Jun']) + '</div></div><details><summary>View exact monthly values</summary><table><caption>Studio capacity booked · 2026</caption><thead><tr><th scope="col">Month</th><th scope="col">Capacity</th></tr></thead><tbody>' + rows + '</tbody></table></details></article>'
    return f'<div class="showcase">{raw_html}<p class="scene-instruction">{HINTS[sid]}</p></div>'

# Pilot 02 keeps its own scenery while sharing the same generation path.
try:
    from .showcase_pilot02 import HTML as P02_HTML, CSS as P02_CSS, HINTS as P02_HINTS
except ImportError:
    from showcase_pilot02 import HTML as P02_HTML, CSS as P02_CSS, HINTS as P02_HINTS
HTML.update(P02_HTML)
CSS.update(P02_CSS)
HINTS.update(P02_HINTS)

# Pilot 03: anchored interactions and their contextual product scenes.
try:
    from .showcase_pilot03 import HTML as P03_HTML, CSS as P03_CSS, HINTS as P03_HINTS
except ImportError:
    from showcase_pilot03 import HTML as P03_HTML, CSS as P03_CSS, HINTS as P03_HINTS
HTML.update(P03_HTML)
CSS.update(P03_CSS)
HINTS.update(P03_HINTS)

# Pilot 04: native overlay spells and their product scenes.
try:
    from .showcase_pilot04 import HTML as P04_HTML, CSS as P04_CSS, HINTS as P04_HINTS
except ImportError:
    from showcase_pilot04 import HTML as P04_HTML, CSS as P04_CSS, HINTS as P04_HINTS
HTML.update(P04_HTML)
CSS.update(P04_CSS)
HINTS.update(P04_HINTS)

# Pilot 05: modal and dialog overlay spells and their product scenes.
try:
    from .showcase_pilot05 import HTML as P05_HTML, CSS as P05_CSS, HINTS as P05_HINTS
except ImportError:
    from showcase_pilot05 import HTML as P05_HTML, CSS as P05_CSS, HINTS as P05_HINTS
HTML.update(P05_HTML)
CSS.update(P05_CSS)
HINTS.update(P05_HINTS)
