"""Pilot 05 scenery for the modal/dialog overlay spells (ds-66, ds-75, ds-77, ds-106).

The interaction markup and behavior live in README.md. This module supplies
editorial product scenes, surrounding content and original vector artwork; it
never manufactures an activated state and never overrides the canonical
overlay behavior. The one deliberate difference from canonical markup is
ds-75, whose demonstration embeds the same self-contained image in both the
thumbnail and the enlarged view so the zoom genuinely reveals more detail.
"""

import urllib.parse

HINTS = {
    "ds-66": "Open “Preview the evening programme” with pointer or keyboard, and watch the gallery page dim and blur behind the card. Escape, a backdrop click or Close dismisses it — the page behind stays scrollable throughout.",
    "ds-75": "Select the harbour image with pointer or keyboard to enlarge it. Escape, a backdrop click or Close returns to the article.",
    "ds-77": "Choose “Review booking” to open the native dialog — a bottom sheet on narrow screens, a centred modal on wider ones. Try the arrival, extras and bedding controls, then Done, Escape or a backdrop click.",
    "ds-106": "Open the dialog and try all three closings: the Close dialog button, Escape and a backdrop click. Each one only closes the dialog — nothing is sent or saved.",
}


def evening_art(kind: int) -> str:
    """Original small vector studies for the ds-66 gallery scene."""
    paths = [
        '<rect width="640" height="440" fill="#232b3a"/><circle cx="470" cy="120" r="70" fill="#e8c87e"/><path d="M0 330Q160 250 320 330T640 330V440H0Z" fill="#3d4a63"/><path d="M0 380Q160 320 320 380T640 380V440H0Z" fill="#141a28"/><path d="M120 330v-90h24v90Zm40 0v-60h24v60Zm40 0v-110h24v110Z" fill="#e8c87e"/>',
        '<rect width="640" height="440" fill="#f0e4cf"/><path d="M0 300Q160 180 320 300T640 300V440H0Z" fill="#c9704b"/><path d="M0 360Q160 260 320 360T640 360V440H0Z" fill="#5d3a36"/><circle cx="180" cy="130" r="58" fill="#c9704b"/><path d="M400 200h120v140H400Z" fill="#232b3a"/><path d="M400 200l60-40 60 40Z" fill="#141a28"/>',
        '<rect width="640" height="440" fill="#1d2b26"/><path d="M80 440V200l60-40 60 40v240Z" fill="#9ed5c4"/><path d="M260 440V140l60-40 60 40v300Z" fill="#e8c87e"/><path d="M440 440V240l60-40 60 40v200Z" fill="#c9704b"/><path d="M0 400h640v40H0Z" fill="#0f1512"/>',
        '<rect width="640" height="440" fill="#e5ddd2"/><circle cx="320" cy="200" r="110" fill="#232b3a"/><circle cx="320" cy="200" r="70" fill="#f0e4cf"/><path d="M0 340h640v100H0Z" fill="#232b3a"/><path d="M60 340v-70m80 70v-110m80 110v-60m80 60v-130m80 130v-80m80 80v-100m80 100v-50" stroke="#e8c87e" stroke-width="14"/>',
    ]
    return '<svg class="study-art" viewBox="0 0 640 440" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">' + paths[kind] + '</svg>'


def harbour_svg() -> str:
    """Original harbour-at-dusk illustration shared by the ds-75 thumbnail and zoom."""
    return (
        "<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='1500' viewBox='0 0 1200 1500'>"
        "<defs><linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'>"
        "<stop offset='0' stop-color='#1c2340'/><stop offset='.45' stop-color='#4a3a63'/>"
        "<stop offset='.68' stop-color='#c9704b'/><stop offset='.8' stop-color='#e8c87e'/>"
        "</linearGradient><linearGradient id='sea' x1='0' y1='0' x2='0' y2='1'>"
        "<stop offset='0' stop-color='#7a5a52'/><stop offset='.25' stop-color='#31445c'/>"
        "<stop offset='1' stop-color='#141d33'/>"
        "</linearGradient><linearGradient id='sunpath' x1='0' y1='0' x2='0' y2='1'>"
        "<stop offset='0' stop-color='#f2d894'/><stop offset='1' stop-color='#f2d894' stop-opacity='0'/>"
        "</linearGradient></defs>"
        "<rect width='1200' height='940' fill='url(#sky)'/>"
        "<g fill='#f2d894' opacity='.28'>"
        "<ellipse cx='260' cy='300' rx='180' ry='26'/><ellipse cx='880' cy='220' rx='220' ry='30'/>"
        "<ellipse cx='620' cy='420' rx='260' ry='24'/><ellipse cx='180' cy='520' rx='150' ry='20'/>"
        "</g>"
        "<circle cx='600' cy='880' r='150' fill='#f2d894' opacity='.35'/>"
        "<circle cx='600' cy='880' r='96' fill='#f7e3ac'/>"
        "<path d='M0 940V820l120-40 90 60 140-90 110 70 150-60 130 80 140-50 120 60 200-30v120Z' fill='#2b2a44'/>"
        "<rect x='978' y='700' width='34' height='130' fill='#e9e2d2'/>"
        "<rect x='978' y='730' width='34' height='22' fill='#b3402e'/><rect x='978' y='776' width='34' height='22' fill='#b3402e'/>"
        "<path d='M972 700h46l-8-34h-30Z' fill='#2b2a44'/>"
        "<path d='M978 688 760 640l6 26 212 40Z' fill='#f7e3ac' opacity='.5'/>"
        "<rect y='940' width='1200' height='560' fill='url(#sea)'/>"
        "<path d='M520 950h160l60 540H460Z' fill='url(#sunpath)' opacity='.55'/>"
        "<g fill='#f2d894' opacity='.7'>"
        "<rect x='540' y='990' width='120' height='10' rx='5'/><rect x='520' y='1040' width='160' height='12' rx='6'/>"
        "<rect x='552' y='1096' width='96' height='10' rx='5'/><rect x='510' y='1156' width='180' height='12' rx='6'/>"
        "<rect x='560' y='1220' width='80' height='9' rx='4'/><rect x='528' y='1290' width='144' height='11' rx='5'/>"
        "</g>"
        "<g fill='#9fb4cc' opacity='.5'>"
        "<rect x='80' y='1030' width='150' height='8' rx='4'/><rect x='900' y='1080' width='190' height='9' rx='4'/>"
        "<rect x='160' y='1200' width='170' height='9' rx='4'/><rect x='830' y='1260' width='150' height='8' rx='4'/>"
        "<rect x='340' y='1360' width='200' height='9' rx='4'/><rect x='700' y='1400' width='170' height='8' rx='4'/>"
        "</g>"
        "<g><path d='M300 1180l26 44h-52Z' fill='#e9e2d2'/><path d='M300 1180v-70' stroke='#101828' stroke-width='6'/>"
        "<path d='M306 1110l66 70h-66Z' fill='#f4ede0'/><path d='M252 1224h96l-16 26H268Z' fill='#101828'/></g>"
        "<g><path d='M880 1300l20 34h-40Z' fill='#e9e2d2'/><path d='M880 1300v-54' stroke='#101828' stroke-width='5'/>"
        "<path d='M885 1246l50 54h-50Z' fill='#e4d6bd'/><path d='M844 1334h72l-12 20h-48Z' fill='#101828'/></g>"
        "<g stroke='#101828' stroke-width='7' fill='none' stroke-linecap='round'>"
        "<path d='M420 560q22-22 44 0 22-22 44 0'/><path d='M700 480q18-18 36 0 18-18 36 0'/>"
        "<path d='M830 600q14-14 28 0 14-14 28 0'/>"
        "</g>"
        "<g fill='#0d1322'><rect x='940' y='1330' width='260' height='26'/>"
        "<rect x='980' y='1356' width='22' height='144'/><rect x='1070' y='1356' width='22' height='144'/>"
        "<rect x='940' y='1300' width='260' height='10'/><rect x='972' y='1310' width='10' height='24'/>"
        "<rect x='1030' y='1310' width='10' height='24'/><rect x='1088' y='1310' width='10' height='24'/>"
        "<rect x='1146' y='1310' width='10' height='24'/></g>"
        "<circle cx='1070' cy='1276' r='10' fill='#f7e3ac'/>"
        "<path d='M0 1500V1420l90-30 70 40 110-50 90 40 120-30 100 50 120-40 110 40 130-30 120 40 140-30v90Z' fill='#0a0f1e'/>"
        "</svg>"
    )


def harbour_uri() -> str:
    return "data:image/svg+xml," + urllib.parse.quote(harbour_svg(), safe="")


HARBOUR = harbour_uri()

HTML_66 = (
    '<main class="gallery-late"><header class="gl-top"><div class="gl-brand"><strong>Meridian</strong><span>Gallery · Est. 1987</span></div>'
    '<nav class="gl-nav" aria-label="Gallery"><a href="#gl-visit">Visit</a><a href="#gl-shows">Exhibitions</a><a href="#gl-late">Gallery late</a></nav></header>'
    '<section class="gl-hero" id="gl-late"><div><p class="scene-kicker">Gallery late · First Friday monthly</p>'
    '<h1>One evening a month, the gallery stays awake.</h1>'
    '<p>Four rooms, one courtyard bar and a print room that only opens after dark. Preview the running order — the backdrop behind the card dims and softens while it is open.</p>'
    '<button type="button" class="programme-trigger" popovertarget="bd-pop">Preview the evening programme</button></div>'
    '<dl class="gl-facts"><div><dt>Doors</dt><dd>19:00</dd></div><div><dt>First set</dt><dd>20:00</dd></div><div><dt>Entry</dt><dd>€6 · under 16 free</dd></div></dl></section>'
    '<div id="bd-pop" class="backdrop-card" popover="auto">'
    '<p class="backdrop-kicker">Gallery late · Friday</p><h2>Evening programme</h2>'
    '<ul><li><strong>19:00</strong> Doors and courtyard bar</li><li><strong>20:00</strong> First set in the atrium</li><li><strong>21:30</strong> Print room opens late</li></ul>'
    '<button type="button" popovertarget="bd-pop" popovertargetaction="hide">Close</button></div>'
    '<section class="gl-grid" id="gl-shows" aria-label="Current exhibitions">'
    + "".join(
        f'<article><div class="gl-art">{evening_art(i)}</div><p class="scene-kicker">{kicker}</p><h2>{title}</h2><p>{copy}</p></article>'
        for i, (kicker, title, copy) in enumerate([
            ("Room one · Until Oct", "Harbour light", "Twelve studies of working harbours at dusk, printed large and hung low."),
            ("Room two · Until Nov", "Night shifts", "Portraits of the people who keep the city running after midnight."),
            ("Atrium · Fridays", "First sets", "Forty-minute concerts under the glass roof. No amplification past ten."),
            ("Print room · Late only", "Open drawers", "Two hundred prints, out of storage and priced to take home."),
        ])
    )
    + '</section>'
    '<section class="gl-visit" id="gl-visit"><div><p class="scene-kicker">Plan your visit</p><h2>Find us by the water.</h2>'
    '<p>Harbour Road 4 · Open Tue–Sun 10:00–18:00 · Step-free throughout. The courtyard bar takes cards only.</p></div>'
    '<p class="gl-note">This page is a demonstration backdrop: the exhibition copy is illustrative, and the programme card above is the spell.</p></section></main>'
)

HTML_75 = (
    '<main class="harbour-article"><article><header class="ha-head"><p class="scene-kicker">Field notes · No. 12</p>'
    '<h1>The hour the harbour changes colour.</h1>'
    '<p class="ha-byline">By Mara Ellingsen · 6 min read · Tromsø, September</p></header>'
    '<p class="ha-lede">There is a twenty-minute window, just after the sun touches the breakwater, when the whole harbour seems to hold its breath. The water goes the colour of weak tea; the gulls go quiet.</p>'
    '<figure class="zoom-figure">'
    f'<button type="button" class="img-trigger" popovertarget="img-modal-1" aria-label="Enlarge: harbour at dusk"><img src="{HARBOUR}" alt="Harbour at dusk" width="640" height="800"></button>'
    '<figcaption>Harbour at dusk · Select the image to enlarge it.</figcaption></figure>'
    '<p>I have drawn this view eleven times now, and every version disagrees about the orange. The boost of colour lives mostly in the reflection path — a wavering column that the smallest ripple can erase.</p>'
    '<blockquote><p>Draw the water first. The boats will forgive you; the light will not wait.</p></blockquote>'
    '<p>The enlarged view shows the same drawing larger: count the shimmer bars in the sun path, then the gulls. Six strokes, three birds, one patient lighthouse.</p>'
    '<p class="ha-colophon">Illustration: original vector study for this catalogue. No photograph, no network request — the enlarged view is the same embedded image.</p></article>'
    '<div id="img-modal-1" class="lightbox-popover" popover="auto"><figure>'
    f'<img src="{HARBOUR}" alt="Harbour at dusk, enlarged view" width="1200" height="1500">'
    '<figcaption>Harbour at dusk · Press Escape or choose Close.</figcaption></figure>'
    '<button type="button" class="lightbox-close" popovertarget="img-modal-1" popovertargetaction="hide">Close</button></div></main>'
)

HTML_77 = (
    '<main class="cabin-booking"><section class="cb-card" aria-labelledby="cb-title"><p class="scene-kicker">Pine Hollow Cabins · Booking 2481</p>'
    '<h1 id="cb-title">The Loft Cabin, two nights.</h1>'
    '<dl class="cb-facts"><div><dt>Check-in</dt><dd>Fri 14 Nov, from 14:00</dd></div><div><dt>Check-out</dt><dd>Sun 16 Nov, by 11:00</dd></div>'
    '<div><dt>Guests</dt><dd>Two adults</dd></div><div><dt>Total</dt><dd>€240 · pay at the cabin</dd></div></dl>'
    '<button type="button" commandfor="sheet-demo" command="show-modal">Review booking</button>'
    '<p class="cb-note">The review step opens a native dialog: a bottom sheet here on phones, a centred modal on wider screens.</p></section>'
    '<section class="cb-included" aria-label="Included in your stay"><article><h2>Included</h2><ul><li>Firewood for the stove</li><li>Bed linen and towels</li><li>Rowboat on the lake</li></ul></article>'
    '<article><h2>Good to know</h2><ul><li>No card machine — cash or transfer</li><li>Dogs welcome, €15 each</li><li>Quiet hours from 22:00</li></ul></article></section>'
    '<dialog id="sheet-demo" class="responsive-sheet" closedby="any" aria-labelledby="sheet-title">'
    '<p class="sheet-kicker">Cabin booking · 2 nights</p><h2 id="sheet-title">Review your stay</h2>'
    '<p class="sheet-lede">Friday 14:00 · Two guests · Total €240. Preferences stay on this page — nothing is booked or charged here.</p>'
    '<fieldset class="sheet-field"><legend>Arrival window</legend>'
    '<label><input type="radio" name="arrival" checked> 14:00 – 16:00</label>'
    '<label><input type="radio" name="arrival"> 16:00 – 18:00</label>'
    '<label><input type="radio" name="arrival"> After 18:00</label></fieldset>'
    '<fieldset class="sheet-field"><legend>Extras</legend>'
    '<label><input type="checkbox" checked> Breakfast basket · €18</label>'
    '<label><input type="checkbox"> Sauna slot · €12</label></fieldset>'
    '<div class="sheet-field"><label for="sheet-bedding">Bedding</label>'
    '<select id="sheet-bedding"><option>Double bed made up</option><option>Two singles</option></select></div>'
    '<form method="dialog" class="sheet-actions"><button type="submit" value="done">Done</button></form></dialog></main>'
)

HTML_106 = (
    '<main class="close-options-article"><article><p class="scene-kicker">Reading room · A two-minute lesson</p>'
    '<h1>Closing is a feature, not an apology.</h1>'
    '<p>Every overlay on this page is native HTML: no script opens it, and no script closes it. The dialog below exists to teach its own dismissal — open it, then close it three different ways.</p>'
    '<button type="button" commandfor="close-options" command="show-modal">How does this dialog close?</button>'
    '<h2>Why three ways matter</h2>'
    '<p>Some readers reach for Escape; some tap outside the card; some want a labelled button. A native <code>closedby="any"</code> dialog honours all three without a line of client script, and returns focus to the button that opened it.</p>'
    '<h2>What this demo will not do</h2>'
    '<p>It will not delete, submit or save anything. “Close dialog” and “Keep reading” both dismiss the overlay; the difference is only which label you preferred.</p></article>'
    '<dialog id="close-options" class="confirm" closedby="any" aria-labelledby="close-options-title">'
    '<h2 id="close-options-title">Three ways to close</h2>'
    '<p>This native dialog dismisses three ways. Try each of them — nothing is sent or saved.</p>'
    '<ol><li>Choose <strong>Close dialog</strong> below.</li><li>Press <kbd>Escape</kbd>.</li><li>Select the dimmed backdrop around this card.</li></ol>'
    '<p class="confirm-note">Without <code>closedby</code> support the backdrop click does nothing; the close controls and Escape still work.</p>'
    '<form method="dialog" class="confirm-actions"><button type="submit" value="stay">Keep reading</button>'
    '<button type="submit" value="close" autofocus>Close dialog</button></form></dialog></main>'
)

HTML = {
    "66": HTML_66,
    "75": HTML_75,
    "77": HTML_77,
    "106": HTML_106,
}

CSS = {
    "ds-66": r'''
.showcase:has(.gallery-late){max-width:1080px}
.gallery-late{width:100%;background:light-dark(#f6f1e6,#10151d);border-radius:28px;overflow:clip;--color-primary:light-dark(#8f3b2a,#e8a37e);--color-text:light-dark(#20242e,#eef0f4);--color-text-muted:light-dark(#5d6474,#9aa3b5);--color-border:light-dark(#ddd3bf,#263041);--color-bg:light-dark(#fffdf7,#171e2a);--color-surface-offset:light-dark(#ece4d2,#222b3c);--color-accent:light-dark(#8f3b2a,#e8a37e)}
.gallery-late :where(button):focus-visible{outline:2px solid var(--color-accent);outline-offset:2px}
.gl-top{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;padding:20px clamp(20px,4vw,48px);border-bottom:1px solid var(--color-border)}
.gl-brand{display:flex;align-items:baseline;gap:10px}
.gl-brand strong{font-family:Georgia,serif;font-size:24px;letter-spacing:-.02em}
.gl-brand span{font-size:12px;color:var(--color-text-muted)}
.gl-nav{display:flex;gap:4px 20px;flex-wrap:wrap;font-size:14px}
.gl-nav a{display:inline-flex;min-block-size:44px;align-items:center}
.gl-hero{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(200px,.65fr);gap:clamp(24px,4vw,56px);align-items:center;padding:clamp(36px,6vw,84px) clamp(20px,4vw,48px);background:linear-gradient(150deg,light-dark(#e9dfc9,#1c2434),light-dark(#f6f1e6,#10151d) 72%)}
.gl-hero h1{max-width:16ch}
.gl-hero p{color:var(--color-text-muted);max-width:52ch}
.gl-facts{display:grid;gap:12px;margin:0;background:var(--color-bg);border:1px solid var(--color-border);border-radius:16px;padding:22px 24px;box-shadow:0 18px 44px #10233a14}
.gl-facts div{display:grid;gap:2px;border-top:1px solid var(--color-border);padding-top:10px}
.gl-facts div:first-child{border-top:0;padding-top:0}
.gl-facts dt{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--color-text-muted)}
.gl-facts dd{margin:0;font-family:Georgia,serif;font-size:26px}
.gl-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--color-border);border-block:1px solid var(--color-border)}
.gl-grid article{background:var(--color-bg);padding:clamp(18px,2.4vw,26px)}
.gl-grid .scene-kicker{color:var(--color-primary)}
.gl-grid h2{font:400 21px/1.2 Georgia,serif;margin:8px 0 6px}
.gl-grid p:last-child{font-size:13px;color:var(--color-text-muted);margin:0}
.gl-art{border-radius:12px;overflow:hidden;margin-bottom:14px;border:1px solid var(--color-border)}
.gl-visit{display:grid;grid-template-columns:1fr 1fr;gap:24px;padding:clamp(26px,4vw,52px)}
.gl-visit h2{font:400 24px/1.2 Georgia,serif;margin:8px 0}
.gl-visit p{font-size:14px;color:var(--color-text-muted)}
.gl-note{font-size:12px;align-self:end;margin:0}
@media(max-width:900px){.gl-grid{grid-template-columns:1fr 1fr}}
@media(max-width:640px){.gl-hero{grid-template-columns:1fr}.gl-hero h1{font-size:38px}.gl-grid{grid-template-columns:1fr}.gl-visit{grid-template-columns:1fr}}
''',
    "ds-75": r'''
.showcase:has(.harbour-article){max-width:720px}
.harbour-article{width:100%;background:light-dark(#faf6ec,#12161d);border:1px solid light-dark(#e2d8c2,#28303f);border-radius:24px;padding:clamp(26px,5vw,64px);--color-primary:light-dark(#274b63,#a9c8de);--color-text:light-dark(#232a33,#e9edf2);--color-text-muted:light-dark(#68707c,#9aa3b5);--color-border:light-dark(#ddd3bf,#28303f);--color-bg:light-dark(#fffdf7,#171e29);--color-surface-offset:light-dark(#efe7d3,#222b3c);--color-accent:light-dark(#8f3b2a,#e8a37e)}
.harbour-article :where(button):focus-visible{outline:2px solid var(--color-accent);outline-offset:3px}
.ha-head{margin-bottom:28px}
.ha-head h1{font-size:clamp(36px,5.4vw,54px)}
.ha-byline{font-size:13px;color:var(--color-text-muted);margin:0}
.ha-lede{font-family:Georgia,serif;font-size:21px;line-height:1.5}
.harbour-article article>p{color:light-dark(#3a424e,#c6cdd8)}
.harbour-article blockquote{margin:28px 0;padding:4px 0 4px 22px;border-left:4px solid var(--color-accent);font-family:Georgia,serif;font-size:22px;line-height:1.4}
.harbour-article blockquote p{margin:0}
.harbour-article .zoom-figure{inline-size:min(100%,352px);margin:30px auto}
.harbour-article .zoom-figure .img-trigger{inline-size:100%;border-radius:14px;overflow:hidden;border:1px solid var(--color-border);box-shadow:0 20px 50px #10233a1f}
.harbour-article .zoom-figure figcaption{text-align:center}
.ha-colophon{font-size:12px;border-top:1px solid var(--color-border);padding-top:16px;margin-bottom:0}
@media(max-width:640px){.harbour-article .zoom-figure{inline-size:min(100%,240px)}.ha-lede{font-size:18px}}
''',
    "ds-77": r'''
.showcase:has(.cabin-booking){max-width:760px}
.cabin-booking{width:100%;display:grid;gap:20px;--color-primary:light-dark(#3f5a36,#a9c795);--color-text:light-dark(#22271f,#e9efe5);--color-text-muted:light-dark(#5f6b58,#9aa892);--color-border:light-dark(#d4d8c8,#2b352a);--color-bg:light-dark(#fffdf6,#181f18);--color-surface-offset:light-dark(#eef0e2,#232d22);--color-accent:light-dark(#8f3b2a,#e8a37e)}
.cabin-booking :where(button,select,input):focus-visible{outline:2px solid var(--color-accent);outline-offset:2px}
.cb-card{background:linear-gradient(160deg,light-dark(#eef0e2,#1e2a1e),light-dark(#f7f5ea,#181f18) 70%);border:1px solid var(--color-border);border-radius:24px;padding:clamp(26px,5vw,52px)}
.cb-card h1{font-size:clamp(34px,5vw,50px)}
.cb-facts{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:26px 0;padding:0}
.cb-facts div{border-top:2px solid var(--color-primary);padding-top:8px}
.cb-facts dt{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--color-text-muted)}
.cb-facts dd{margin:4px 0 0;font-weight:600}
.cb-card>button{min-block-size:48px;padding:0 1.6rem;font-weight:600;cursor:pointer;border:0;border-radius:12px;background:var(--color-primary);color:light-dark(#fffdf6,#10170f)}
.cb-note{font-size:13px;color:var(--color-text-muted);margin:14px 0 0}
.cb-included{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.cb-included article{background:var(--color-bg);border:1px solid var(--color-border);border-radius:20px;padding:24px 26px}
.cb-included h2{font:400 22px/1.2 Georgia,serif;margin:0 0 10px}
.cb-included ul{margin:0;padding-inline-start:1.1rem;display:grid;gap:6px;font-size:14px;color:var(--color-text-muted)}
@media(max-width:640px){.cb-facts{grid-template-columns:1fr 1fr}.cb-included{grid-template-columns:1fr}}
''',
    "ds-106": r'''
.showcase:has(.close-options-article){max-width:680px}
.close-options-article{width:100%;background:light-dark(#f4f2ec,#131519);border:1px solid light-dark(#dcd6c6,#2a2d33);border-radius:24px;padding:clamp(26px,5vw,60px);--color-primary:light-dark(#20242e,#e8b04b);--color-text:light-dark(#20242e,#eceef2);--color-text-muted:light-dark(#5d6474,#9aa0ac);--color-border:light-dark(#d5cfbd,#2a2d33);--color-bg:light-dark(#fffdf7,#1a1d23);--color-surface-offset:light-dark(#e9e4d4,#24272e);--color-accent:light-dark(#8f3b2a,#e8a37e)}
.close-options-article :where(button):focus-visible{outline:2px solid var(--color-accent);outline-offset:2px}
.close-options-article h1{font-size:clamp(34px,5vw,50px)}
.close-options-article h2{font:400 24px/1.25 Georgia,serif;margin:30px 0 8px}
.close-options-article article>p{color:light-dark(#3a404c,#c2c7d1)}
.close-options-article article>button{min-block-size:48px;padding:0 1.6rem;font-weight:600;cursor:pointer;border:0;border-radius:12px;background:var(--color-primary);color:light-dark(#fffdf7,#141414);margin:6px 0 4px}
.close-options-article code{font-size:.85em}
''',
}
