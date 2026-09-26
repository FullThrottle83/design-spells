"""Pilot 04 scenery for the native-overlay spells (ds-79, ds-89, ds-142).

The interaction markup and behavior live in README.md. This module supplies
editorial product scenes, real in-page destinations and original vector
artwork; it never manufactures an activated state and never overrides the
canonical overlay behavior.
"""

HINTS = {
    "ds-79": "Open Products with a click, or with Enter while the trigger has focus. Every destination in the panel is a section of this page. Nothing auto-closes on navigation — one click away or Escape clears the panel, which becomes a contained bottom sheet on narrow screens.",
    "ds-89": "Open a row’s ⋯ menu. “Open full record” and “View change history” jump to that row’s own record and history sections; “Star for review” is a real checkbox the owning row reflects. Escape or a click away closes the menu.",
    "ds-142": "Activate any numbered pin with pointer or keyboard. Its own popover opens above the pin and flips below when the pin sits near the top edge. The numbered key links to every location’s note for keyboard and no-enhancement reading.",
}


def atlas_art() -> str:
    """Original illustrated terrain for the map demo; decorative only."""
    return (
        '<svg class="map-art" viewBox="0 0 1000 560" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">'
        '<rect width="1000" height="560" fill="#cfdcd2"/>'
        '<path d="M0 0h1000v560H0z" fill="none"/>'
        '<path d="M-20 420q140-70 260-30t240 10 260-60 280-20v260H-20Z" fill="#b9cdbd"/>'
        '<path d="M120 120q90-60 200-30t150 110q-40 90-160 100T120 240Z" fill="#e6e2cf"/>'
        '<path d="M560 60q120-40 220 20t90 150q-60 80-180 70T540 190Z" fill="#efe9d6"/>'
        '<path d="M170 150q70-40 150-16t110 86q-34 62-120 70T170 210Z" fill="none" stroke="#a8b79f" stroke-width="2"/>'
        '<path d="M205 175q50-26 105-10t75 58q-26 42-84 48t-96-40Z" fill="none" stroke="#a8b79f" stroke-width="2"/>'
        '<path d="M610 100q80-26 150 14t60 100q-42 52-120 46t-100-70Z" fill="none" stroke="#b3ac93" stroke-width="2"/>'
        '<path d="M640 130q55-16 100 10t40 66q-30 34-82 30t-68-48Z" fill="none" stroke="#b3ac93" stroke-width="2"/>'
        '<path d="M420 300q60 40 90 110t40 150" fill="none" stroke="#8fb0c4" stroke-width="7" stroke-linecap="round"/>'
        '<path d="M700 330q-30 60-20 120t50 110" fill="none" stroke="#8fb0c4" stroke-width="5" stroke-linecap="round"/>'
        '<g stroke="#7d9683" stroke-width="2" fill="none">'
        '<path d="M300 430l10-18 10 18Z"/><path d="M330 452l10-18 10 18Z"/><path d="M270 460l10-18 10 18Z"/>'
        '<path d="M760 180l10-18 10 18Z"/><path d="M790 205l10-18 10 18Z"/><path d="M735 210l10-18 10 18Z"/>'
        '</g>'
        '<g stroke="#ffffff" stroke-opacity=".5" stroke-width="1">'
        '<path d="M0 140h1000M0 280h1000M0 420h1000M200 0v560M400 0v560M600 0v560M800 0v560"/>'
        '</g>'
        '<g stroke="#5f7268" stroke-width="2" fill="none"><circle cx="905" cy="80" r="30"/><path d="M905 42v76M867 80h76"/><path d="M905 58l10 22-10 22-10-22Z" fill="#5f7268"/></g>'
        '</svg>'
    )


NAV79 = (
    '<nav class="site-nav" aria-label="Primary">'
    '<a class="brand" href="#top">Fieldline</a>'
    '<button class="mega-trigger" commandfor="mega-1" command="toggle-popover">Products <span aria-hidden="true">▾</span></button>'
    '<a class="nav-link" href="#pricing">Pricing</a>'
    '<a class="nav-link" href="#field-notes">Field notes</a>'
    '</nav>'
)

PANEL79 = (
    '<div id="mega-1" popover="auto" class="mega-panel">'
    '<div class="mega-col"><h2>Observe</h2>'
    '<a class="mega-item" href="#observe"><strong>Signal dashboard</strong><span>Release metrics in one morning view.</span></a>'
    '<a class="mega-item" href="#observe-alerts"><strong>Quiet alerts</strong><span>Only the thresholds you actually set.</span></a></div>'
    '<div class="mega-col"><h2>Automate</h2>'
    '<a class="mega-item" href="#automate"><strong>Flow builder</strong><span>Plain-language steps, no scripting.</span></a>'
    '<a class="mega-item" href="#automate-schedule"><strong>Seasonal schedules</strong><span>Pause and resume whole workflows.</span></a></div>'
    '<div class="mega-col"><h2>Connect</h2>'
    '<a class="mega-item" href="#connect"><strong>Guided imports</strong><span>Bring existing records across.</span></a>'
    '<a class="mega-item" href="#connect-api"><strong>Read-only API</strong><span>Token-scoped, documented endpoints.</span></a></div>'
    '<p class="mega-foot"><a href="#changelog">Read the changelog →</a></p>'
    '</div>'
)

GRID79 = [
    ("observe", "Observe", "Signal dashboard", "One screen for yesterday’s releases: deploys, errors and the two numbers the studio actually watches."),
    ("observe-alerts", "Observe", "Quiet alerts", "Thresholds you set yourself, delivered once a day. Nothing pings at 2am unless you asked for it."),
    ("automate", "Automate", "Flow builder", "Describe a routine in plain language — weekly report, client digest — and Fieldline keeps it running."),
    ("automate-schedule", "Automate", "Seasonal schedules", "Pause a whole workflow over the quiet months and resume it with one keystroke in spring."),
    ("connect", "Connect", "Guided imports", "Bring spreadsheets and old exports across with a mapped, reviewable import. No data is moved in this demo."),
    ("connect-api", "Connect", "Read-only API", "Token-scoped endpoints for the metrics you already see, documented with copyable examples."),
]

HTML = {
    "79": (
        '<main class="fieldline-scene" id="top"><header class="fl-head">' + NAV79 + PANEL79 + '</header>'
        '<section class="fl-hero"><p class="scene-kicker">Fieldline / Studio operations</p>'
        '<h1>Know what the studio is doing this morning.</h1>'
        '<p>Fieldline keeps release metrics, routines and client records in one calm place. Open <strong>Products</strong> above to tour the range — every destination lives on this page.</p>'
        '<aside class="fl-digest"><p class="scene-kicker">This morning</p><ul>'
        '<li><strong>3</strong><span>deploys shipped before nine</span></li>'
        '<li><strong>0</strong><span>open errors across clients</span></li>'
        '<li><strong>82%</strong><span>focus time kept this week</span></li>'
        '</ul><small>Illustrative digest. Nothing pings, nothing is sent.</small></aside></section>'
        '<div class="fl-grid">' + ''.join(
            f'<section id="{sid}"><p class="scene-kicker">{group} / {i + 1:02d}</p><h2>{name}</h2><p>{copy}</p></section>'
            for i, (sid, group, name, copy) in enumerate(GRID79)
        ) + '</div>'
        '<div class="fl-tail">'
        '<section id="pricing"><p class="scene-kicker">Pricing</p><h2>One seat, one price.</h2><p>€18 per month per maker. Every feature included; no tier theatre.</p></section>'
        '<section id="field-notes"><p class="scene-kicker">Field notes</p><h2>Written by the people who build it.</h2><p>Short monthly notes on running a small studio without drowning in tooling.</p></section>'
        '<section id="changelog"><p class="scene-kicker">Changelog</p><h2>September: quieter alerts.</h2><p>Alert digests, import previews and the read-only API all shipped this month.</p></section>'
        '</div></main>'
    ),
    "89": (
        '<main class="papertrail-scene"><header class="pt-head"><div><p class="scene-kicker">Papertrail / Shared workspace</p>'
        '<h1>The reading room.</h1></div><p>Three living documents and one closed archive. Each row’s ⋯ menu offers that row’s own destinations and one real state change — nothing is deleted, sent or saved.</p></header>'
        '<div class="pt-list">'
        '<article class="doc-row" style="--ctx-anchor: --ctx-q3;"><div class="doc-copy"><h2>Q3 renewal forecast <span class="star-flag" aria-hidden="true">★</span></h2><p>Updated 2 days ago · Owned by Priya</p></div>'
        '<button class="ctx-btn" commandfor="ctx-menu" command="toggle-popover" aria-label="Actions for Q3 renewal forecast">⋯</button>'
        '<div id="ctx-menu" popover="auto" class="ctx-menu"><a class="ctx-item" href="#record-q3">Open full record</a><label class="ctx-item ctx-check"><input type="checkbox"> Star for review</label><a class="ctx-item" href="#history-q3">View change history</a></div></article>'
        '<article class="doc-row" style="--ctx-anchor: --ctx-2;"><div class="doc-copy"><h2>Studio lease — annex <span class="star-flag" aria-hidden="true">★</span></h2><p>Updated last week · Owned by Jonas</p></div>'
        '<button class="ctx-btn" commandfor="ctx-menu-2" command="toggle-popover" aria-label="Actions for Studio lease, annex">⋯</button>'
        '<div id="ctx-menu-2" popover="auto" class="ctx-menu"><a class="ctx-item" href="#record-2">Open full record</a><label class="ctx-item ctx-check"><input type="checkbox"> Star for review</label><a class="ctx-item" href="#history-2">View change history</a></div></article>'
        '<article class="doc-row" style="--ctx-anchor: --ctx-3;"><div class="doc-copy"><h2>Winter residency brief <span class="star-flag" aria-hidden="true">★</span></h2><p>Updated yesterday · Owned by Mara</p></div>'
        '<button class="ctx-btn" commandfor="ctx-menu-3" command="toggle-popover" aria-label="Actions for Winter residency brief">⋯</button>'
        '<div id="ctx-menu-3" popover="auto" class="ctx-menu"><a class="ctx-item" href="#record-3">Open full record</a><label class="ctx-item ctx-check"><input type="checkbox"> Star for review</label><a class="ctx-item" href="#history-3">View change history</a></div></article>'
        '</div>'
        '<div class="pt-records">'
        '<section id="record-q3" tabindex="-1"><p class="scene-kicker">Record / Forecast</p><h2>Q3 renewal forecast</h2><p>Eight of eleven accounts have confirmed. The remaining three are scheduled for October calls; no revenue is recognised in this demonstration.</p><a href="#top-89">Back to documents ↑</a></section>'
        '<section id="history-q3" tabindex="-1"><p class="scene-kicker">History / Forecast</p><h2>Change history</h2><p>12 Sep — Priya revised the confidence column. 04 Sep — created from the Q2 template. Every entry is illustrative.</p><a href="#top-89">Back to documents ↑</a></section>'
        '<section id="record-2" tabindex="-1"><p class="scene-kicker">Record / Lease</p><h2>Studio lease — annex</h2><p>The annex adds 40 m² from November. Terms are summarised here for reading only; no agreement is signed or stored.</p><a href="#top-89">Back to documents ↑</a></section>'
        '<section id="history-2" tabindex="-1"><p class="scene-kicker">History / Lease</p><h2>Change history</h2><p>20 Sep — Jonas attached the floor plan. 18 Sep — draft created. Illustrative entries only.</p><a href="#top-89">Back to documents ↑</a></section>'
        '<section id="record-3" tabindex="-1"><p class="scene-kicker">Record / Residency</p><h2>Winter residency brief</h2><p>Six weeks, four makers, one shared kiln. The brief describes space, stipend and application dates.</p><a href="#top-89">Back to documents ↑</a></section>'
        '<section id="history-3" tabindex="-1"><p class="scene-kicker">History / Residency</p><h2>Change history</h2><p>25 Sep — Mara opened applications. 21 Sep — brief created. Illustrative entries only.</p><a href="#top-89">Back to documents ↑</a></section>'
        '<section id="record-4" tabindex="-1"><p class="scene-kicker">Record / Archive</p><h2>Archive: spring catalogue</h2><p>Closed in June after forty printed copies. The archive record keeps the contents list and the print run for reference only; nothing is reprinted or sold here.</p><a href="#top-89">Back to documents ↑</a></section>'
        '<section id="history-4" tabindex="-1"><p class="scene-kicker">History / Archive</p><h2>Change history</h2><p>02 Jun — catalogue closed and moved to the archive. 14 Mar — spring edition created. Illustrative entries only.</p><a href="#top-89">Back to documents ↑</a></section>'
        '</div>'
        '<footer class="pt-foot" id="top-89">'
        '<article class="doc-row" style="--ctx-anchor: --ctx-4;"><div class="doc-copy"><h2>Archive: spring catalogue <span class="star-flag" aria-hidden="true">★</span></h2><p>Closed · Owned by the studio</p></div>'
        '<button class="ctx-btn" commandfor="ctx-menu-4" command="toggle-popover" aria-label="Actions for archived spring catalogue">⋯</button>'
        '<div id="ctx-menu-4" popover="auto" class="ctx-menu"><a class="ctx-item" href="#record-4">Open full record</a><label class="ctx-item ctx-check"><input type="checkbox"> Star for review</label><a class="ctx-item" href="#history-4">View change history</a></div></article>'
        '<p class="pt-foot-note">The archived row sits at the foot of the page: open its menu to see the anchored menu flip above the trigger when there is no room below.</p>'
        '</footer></main>'
    ),
    "142": (
        '<main class="atlas-scene"><header class="atlas-head"><p class="scene-kicker">Fieldline atlas / Four studios</p>'
        '<h1>Where the work happens.</h1><p>Four small studios, one shared practice. Activate a numbered pin for its details, or follow the numbered key below the map to each studio’s note.</p></header>'
        '<figure class="map-figure"><div class="map-container" role="group" aria-label="Illustrated studio map with four locations">' + atlas_art()
        + '<div class="map-stop" style="--pin-anchor: --pin-1; --pin-x: 22%; --pin-y: 46%;"><button class="map-pin" commandfor="pop-pin-1" command="toggle-popover" aria-label="Location 1, Harbour Point, Lisbon"><span aria-hidden="true"><i>1</i></span></button>'
        '<div id="pop-pin-1" popover="auto" class="pin-pop"><strong>Harbour Point</strong><span>Lisbon · 14 people · UTC+1</span><a class="pin-link" href="#note-1">Studio notes →</a><button class="pin-close" commandfor="pop-pin-1" command="hide-popover" aria-label="Close Harbour Point notes">×</button></div></div>'
        + '<div class="map-stop" style="--pin-anchor: --pin-2; --pin-x: 58%; --pin-y: 22%;"><button class="map-pin" commandfor="pop-pin-2" command="toggle-popover" aria-label="Location 2, Kiln Yard, Porto"><span aria-hidden="true"><i>2</i></span></button>'
        '<div id="pop-pin-2" popover="auto" class="pin-pop"><strong>Kiln Yard</strong><span>Porto · 6 people · UTC+1</span><a class="pin-link" href="#note-2">Studio notes →</a><button class="pin-close" commandfor="pop-pin-2" command="hide-popover" aria-label="Close Kiln Yard notes">×</button></div></div>'
        + '<div class="map-stop" style="--pin-anchor: --pin-3; --pin-x: 76%; --pin-y: 66%;"><button class="map-pin" commandfor="pop-pin-3" command="toggle-popover" aria-label="Location 3, North Light, Tromsø"><span aria-hidden="true"><i>3</i></span></button>'
        '<div id="pop-pin-3" popover="auto" class="pin-pop"><strong>North Light</strong><span>Tromsø · 3 people · UTC+2</span><a class="pin-link" href="#note-3">Studio notes →</a><button class="pin-close" commandfor="pop-pin-3" command="hide-popover" aria-label="Close North Light notes">×</button></div></div>'
        + '<div class="map-stop" style="--pin-anchor: --pin-4; --pin-x: 40%; --pin-y: 80%;"><button class="map-pin" commandfor="pop-pin-4" command="toggle-popover" aria-label="Location 4, Field Station, Azores"><span aria-hidden="true"><i>4</i></span></button>'
        '<div id="pop-pin-4" popover="auto" class="pin-pop"><strong>Field Station</strong><span>Azores · 2 people · UTC+0</span><a class="pin-link" href="#note-4">Studio notes →</a><button class="pin-close" commandfor="pop-pin-4" command="hide-popover" aria-label="Close Field Station notes">×</button></div></div>'
        + '</div><figcaption class="map-key"><ul>'
        '<li><a href="#note-1"><span aria-hidden="true">1</span>Harbour Point — Lisbon</a></li>'
        '<li><a href="#note-2"><span aria-hidden="true">2</span>Kiln Yard — Porto</a></li>'
        '<li><a href="#note-3"><span aria-hidden="true">3</span>North Light — Tromsø</a></li>'
        '<li><a href="#note-4"><span aria-hidden="true">4</span>Field Station — Azores</a></li>'
        '</ul></figcaption></figure>'
        '<div class="atlas-notes">'
        '<section id="note-1" tabindex="-1"><p class="scene-kicker">01 / Lisbon</p><h2>Harbour Point</h2><p>A converted warehouse by the water. The studio keeps its press room and the shared material library here.</p></section>'
        '<section id="note-2" tabindex="-1"><p class="scene-kicker">02 / Porto</p><h2>Kiln Yard</h2><p>Six makers share two kilns and one long table. Glaze tests line the stairwell.</p></section>'
        '<section id="note-3" tabindex="-1"><p class="scene-kicker">03 / Tromsø</p><h2>North Light</h2><p>Winter daylight is short and blue; the studio plans its photography around it.</p></section>'
        '<section id="note-4" tabindex="-1"><p class="scene-kicker">04 / Azores</p><h2>Field Station</h2><p>Two people, one field station. Soil samples and sketchbooks in equal measure.</p></section>'
        '</div></main>'
    ),
}

CSS = {
"ds-79": r'''
.fieldline-scene{width:100%;background:light-dark(#f4f1e8,#141b18);border-radius:28px;overflow:clip;--color-primary:light-dark(#1f4b43,#9ed5c4);--color-text:light-dark(#1c2422,#eef4ee);--color-text-muted:light-dark(#5f6d65,#9db2a7);--color-border:light-dark(#d9d3c3,#2a3531);--color-bg:light-dark(#fffdf6,#18211e);--color-surface-offset:light-dark(#efeadd,#222c28);--color-accent:light-dark(#c75135,#eb9075)}
.fl-head{padding:clamp(14px,2.4vw,26px) clamp(20px,4vw,54px);border-bottom:1px solid var(--color-border)}
.fl-head .brand{font-family:Georgia,serif;font-size:21px;letter-spacing:-.02em}
.fl-head .site-nav{gap:clamp(12px,2.6vw,28px)}
.fl-hero{padding:clamp(44px,7vw,104px) clamp(20px,4vw,54px);background:linear-gradient(155deg,light-dark(#e5ebdc,#1b2b26),light-dark(#f4f1e8,#141b18) 70%);display:grid;grid-template-columns:minmax(0,1.25fr) minmax(230px,.75fr);gap:clamp(24px,4vw,64px);align-items:center}.fl-digest{background:var(--color-bg);border:1px solid var(--color-border);border-radius:16px;padding:22px 24px;box-shadow:0 18px 44px #102b241f}.fl-digest ul{list-style:none;margin:14px 0 12px;padding:0;display:grid;gap:10px}.fl-digest li{display:flex;align-items:baseline;gap:12px;border-top:1px solid var(--color-border);padding-top:10px}.fl-digest strong{font:400 30px/1 Georgia,serif;min-width:2.2ch}.fl-digest span{color:var(--color-text-muted);font-size:13px}.fl-digest small{font-size:11px;color:var(--color-text-muted)}
.fl-hero h1{max-width:15ch}
.fl-hero p:last-child{max-width:52ch;color:var(--color-text-muted)}
.fl-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--color-border);border-block:1px solid var(--color-border)}
.fl-grid section{background:var(--color-bg);padding:clamp(20px,2.6vw,32px);scroll-margin-block:20px}
.fl-grid .scene-kicker{color:light-dark(#c75135,#eb9075)}
.fl-grid h2{font:400 clamp(20px,2vw,25px)/1.15 Georgia,serif;margin:6px 0 8px}
.fl-grid p:last-child{font-size:13px;color:var(--color-text-muted);margin:0}
.fl-tail{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(20px,3vw,40px);padding:clamp(26px,4vw,58px)}
.fl-tail section{scroll-margin-block:20px}
.fl-tail h2{font:400 22px/1.2 Georgia,serif;margin:6px 0 8px}
.fl-tail p:last-child{font-size:13px;color:var(--color-text-muted);margin:0}
@media(max-width:760px){.fl-grid,.fl-tail{grid-template-columns:1fr}.fl-hero{grid-template-columns:1fr}.fl-hero h1{font-size:40px}.fl-head .nav-link{display:none}}
''',
"ds-89": r'''
.papertrail-scene{width:100%;padding:clamp(22px,5vw,56px);background:light-dark(#eef0ea,#151b19);border-radius:28px;--color-primary:light-dark(#1f4b43,#9ed5c4);--color-text:light-dark(#1c2422,#eef4ee);--color-text-muted:light-dark(#5f6d65,#9db2a7);--color-border:light-dark(#d3d8cb,#2a3531);--color-bg:light-dark(#fffdf6,#18211e);--color-surface-offset:light-dark(#efece1,#222c28);--color-accent:light-dark(#c75135,#eb9075)}
.pt-head{display:flex;align-items:end;justify-content:space-between;gap:26px;margin-bottom:26px}
.pt-head h1{max-width:12ch;margin-bottom:0}
.pt-head>p{max-width:38ch;color:var(--color-text-muted);font-size:14px}
.pt-list{display:grid;gap:12px}
.papertrail-scene .doc-row h2{font:400 20px/1.2 Georgia,serif;margin:0 0 2px}
.pt-records{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:34px}
.pt-records section{padding:20px 22px;background:var(--color-bg);border:1px solid var(--color-border);border-radius:16px;scroll-margin-block:20px}
.pt-records .scene-kicker{color:light-dark(#c75135,#eb9075)}
.pt-records h2{font:400 21px/1.2 Georgia,serif;margin:6px 0 8px}
.pt-records p{font-size:13px;color:var(--color-text-muted)}
.pt-records a{display:inline-flex;min-block-size:40px;align-items:center;font-size:13px}
.pt-foot{margin-top:44px;border-top:1px solid var(--color-border);padding-top:26px}
.pt-foot .doc-row{background:light-dark(#f6f4ea,#1b2422)}
.pt-foot-note{margin:14px 0 0;font-size:12px;color:var(--color-text-muted);max-width:60ch}
@media(max-width:760px){.pt-head{display:block}.pt-head h1{font-size:38px}.pt-head>p{margin-top:10px}.pt-records{grid-template-columns:1fr}}
''',
"ds-142": r'''
.atlas-scene{width:100%;padding:clamp(22px,5vw,56px);background:light-dark(#e9ede4,#141a18);border-radius:28px;--color-primary:light-dark(#c75135,#eb9075);--color-text:light-dark(#1c2422,#eef4ee);--color-text-muted:light-dark(#5f6d65,#9db2a7);--color-border:light-dark(#ccd4c6,#2a3531);--color-bg:light-dark(#fffdf6,#18211e);--color-surface-offset:light-dark(#efece1,#222c28);--color-accent:light-dark(#1f4b43,#9ed5c4);--color-text-inverse:#fffdf6}
.atlas-head{margin-bottom:22px}
.atlas-head h1{max-width:16ch;margin-bottom:8px}
.atlas-head p:last-child{max-width:52ch;color:var(--color-text-muted)}
.atlas-scene .map-container{block-size:clamp(20rem,44vw,28rem);border-radius:20px;border-color:light-dark(#b9c4b2,#33413c)}
.atlas-scene .map-art{position:absolute;inset:0;inline-size:100%;block-size:100%}
.atlas-scene .map-key ul{gap:var(--space-2) var(--space-5);font-size:13px}
.atlas-notes{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:26px}
.atlas-notes section{padding:20px 22px;background:var(--color-bg);border:1px solid var(--color-border);border-radius:16px;scroll-margin-block:20px}
.atlas-notes .scene-kicker{color:light-dark(#c75135,#eb9075)}
.atlas-notes h2{font:400 21px/1.2 Georgia,serif;margin:6px 0 8px}
.atlas-notes p{font-size:13px;color:var(--color-text-muted);margin:0}
@media(max-width:760px){.atlas-notes{grid-template-columns:1fr}.atlas-head h1{font-size:38px}}
''',
}
