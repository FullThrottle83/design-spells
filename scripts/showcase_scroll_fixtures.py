"""Batch 02: scene-only scroll journeys. Actual techniques stay in README.md.

The two AI-generated landscape studies are deliberately embedded in runnable
pages so hosted/iframe/download have identical, offline-capable image content.
"""
from base64 import b64encode
from functools import lru_cache
from pathlib import Path

HINTS = {
    'ds-30': 'Scroll through the workshop itinerary. The session bar stays at the bottom; Session details takes you to the visit information.',
    'ds-55': 'Scroll slowly through the three stops. Cards pin and overlap; supporting browsers shrink and dim the deck as it exits. Return to the start to replay.',
    'ds-69': 'Scroll the table sideways, or focus it and use arrow keys. The first column stays pinned. Supporting browsers add a shadow while content is hidden to its left.',
    'ds-93': 'Swipe or scroll sideways to the next landscape. Its caption appears when it snaps. Tab to a slide to reveal its caption directly.',
    'ds-111': 'Scroll down to the allocation report. Bars fill as each metric enters; scroll back up to replay. Unsupported browsers and reduced motion show the final values.',
    'ds-134': 'Swipe a document to the left, or focus its row and use the right arrow. Tab also reveals Details. Follow the link to the real document information below.',
}

@lru_cache(maxsize=2)
def photo(name):
    return 'data:image/jpeg;base64,' + b64encode((Path(__file__).parent / 'demo-assets' / f'{name}-study.jpg').read_bytes()).decode('ascii')


def heading(kicker, title, copy):
    return f'<header class="journey-head"><p class="journey-kicker">{kicker}</p><h1>{title}</h1><p class="journey-lede">{copy}</p></header>'


def instruction(sid):
    return f'<p class="journey-instruction">{HINTS[sid]}</p>'


def render(sid):
    if sid == 'ds-30':
        markup = '<div class="workshop-journey" id="workshop-start">' + heading('PAPER / PRACTICE · Saturday sessions', 'Make something<br>worth keeping.', 'A slow afternoon of paper, thread and simple tools. Learn to bind a notebook you will actually use.') + instruction(sid)
        markup += '''<div class="workshop-cover" aria-hidden="true"><span class="book book-one">PAPER<br>NOTES<span>VOL. 01 / HAND BOUND</span></span><span class="book book-two">Field<br>notes.</span><span class="cover-caption">A simple object. Made by you.</span></div>
        <div class="workshop-story"><section><p class="journey-kicker">01 / Find your materials</p><h2>Start with the feel of it.</h2><p>Compare soft cotton sheets and warm, textured covers. Choose your paper, fold a signature and learn why the grain matters.</p><dl><div><dt>Materials</dt><dd>Recycled paper &amp; linen thread</dd></div><div><dt>Experience</dt><dd>Curiosity is enough</dd></div></dl></section>
        <section><p class="journey-kicker">02 / Learn the rhythm</p><h2>One stitch at a time.</h2><p>A guided demonstration, then time to find your own pace. We use a simple exposed stitch so you can see exactly how the book holds together.</p><p class="workshop-pullquote">“The best tools are the ones<br>you learn to trust.”</p></section>
        <section><p class="journey-kicker">03 / Take it with you</p><h2>A notebook, not a souvenir.</h2><p>Trim the edges, add a title and take home a finished notebook, a printed binding guide and the confidence to make another.</p></section></div>
        <aside class="sticky-cta" aria-label="Workshop information"><div><strong>Paper &amp; Practice</strong><span>Saturday · 14:00–17:00 · €48</span></div><a href="#session-details">Session details ↓</a></aside></div>
        <section class="session-details" id="session-details" tabindex="-1"><p class="journey-kicker">Plan your visit</p><h2>A seat at the workbench.</h2><p>This is an illustrative workshop itinerary, not a booking service.</p><dl><div><dt>Duration</dt><dd>3 hours, including a tea break</dd></div><div><dt>Included</dt><dd>All materials and a take-home guide</dd></div><div><dt>Group size</dt><dd>Up to 8 participants</dd></div></dl><a href="#workshop-start">Back to the itinerary ↑</a></section>'''
    elif sid == 'ds-55':
        markup = '<div id="route-start">' + heading('FIELD ATLAS / Route 03', 'A day, in<br>three chapters.', 'A short walking route from the treeline to open water. Scroll to stack the stops, one over the next.') + instruction(sid) + '</div>'
        cards = [
            ('01', 'The treeline', '09:00 · 2.4 km', 'A quiet start beneath the pines. Follow the path until the canopy gives way to the first open view.', 'Switch off. Look up.', 'forest'),
            ('02', 'The ridgeline', '11:30 · 3.1 km', 'The trail narrows, the horizon opens. Stop at the crest for lunch and a little space to think.', 'Take the longer view.', 'ridge'),
            ('03', 'The shoreline', '14:00 · 1.8 km', 'An easy descent to the water. Find a flat stone, loosen your boots and let the afternoon slow down.', 'Leave time for nothing.', 'shore'),
        ]
        markup += '<div class="card-stack">'
        for i,(n,title,meta,copy,quote,kind) in enumerate(cards):
            markup += f'<article class="card route-{kind}" style="--stack-offset:{i*64}px"><div class="route-label"><span>STOP {n} / 03</span><span>{meta}</span></div><div class="route-illustration" aria-hidden="true"><span></span><span></span><span></span></div><div class="route-copy"><h2>{title}</h2><p>{copy}</p><strong>{quote}</strong></div></article>'
        markup += '</div><footer class="route-end"><p class="journey-kicker">7.3 km / One unhurried day</p><h2>Good places<br>stay with you.</h2><a href="#route-start">Return to the first chapter ↑</a><p class="journey-note">Illustrative itinerary. Sticky stacking remains without view timelines; reduced motion removes shrinking and dimming.</p></footer>'
    elif sid == 'ds-69':
        markup = heading('STUDIO OPERATIONS / September 2026', 'Keep your bearings.', 'A project ledger with a first column that stays put while the rest of the data moves.') + instruction(sid)
        projects = [('Field journal','Editorial','Mina Rao','Sep 30','12','€8,400','On track'),('Orchard identity','Brand','Theo Kim','Oct 07','18','€12,600','In review'),('Harbour site','Digital','Ari Soto','Oct 12','24','€19,200','On track'),('Archive annual','Print','Lea Berg','Oct 20','16','€11,200','Planning'),('Sunday objects','Packaging','Noor Ali','Nov 02','21','€14,700','In review')]
        markup += '<div class="ledger-summary"><span><strong>5</strong> active projects</span><span>All amounts in EUR · Sample data</span></div><div class="table-wrapper" tabindex="0" role="region" aria-label="Project ledger, scroll horizontally"><table><caption>Studio project ledger · autumn delivery schedule</caption><thead><tr>' + ''.join(f'<th scope="col">{x}</th>' for x in ['Project','Discipline','Lead','Delivery','Days','Budget','Status']) + '</tr></thead><tbody>'
        for row in projects:
            markup += '<tr><th scope="row">'+row[0]+'</th>'+''.join(f'<td>{x}</td>' for x in row[1:])+'</tr>'
        markup += '</tbody></table></div><p class="table-foot">← Scroll to compare delivery, budget and status →</p><p class="journey-note">Without scroll-state queries, the pinned column and its divider remain; only the conditional shadow is absent.</p>'
    elif sid == 'ds-93':
        markup = heading('LANDSCAPE STUDIES / Two ways to pause', 'Stay for the view.', 'Two places to let your eyes wander. A caption waits for the moment the frame settles.') + instruction(sid)
        markup += '<div class="snap-carousel" role="region" aria-label="Landscape studies" tabindex="0">'
        for name,title,note in [('alpine','Alpine stillness','01 / Morning light'),('coastal','The long way home','02 / Evening tide')]:
            markup += f'<figure class="slide" tabindex="0"><img src="{photo(name)}" width="1100" height="733" alt="{title}: '+('rocky mountains reflected in a turquoise lake' if name=='alpine' else 'a grassy coastal path above the sea')+f'"><figcaption class="caption"><small>{note}</small><strong>{title}</strong></figcaption></figure>'
        markup += '</div><p class="gallery-credit">AI-generated landscape studies · Native scroll, no carousel script</p><p class="journey-note">Without scroll-state support, or with reduced motion, both captions stay visible. Keyboard focus reveals a caption even before snapping.</p>'
    elif sid == 'ds-111':
        markup = '<section class="report-intro" id="report-start">' + heading('COMMON GROUND / 2026 impact report', 'Small grants.<br>Lasting change.', 'Community-led spaces, funded one practical idea at a time. Scroll to see this year’s allocation take shape.') + instruction(sid) + '''<div class="report-seal" aria-hidden="true"><span>CG</span><small>LOCAL IDEAS<br>SHARED PROGRESS</small></div><a href="#allocation-report">Explore the allocation report ↓</a></section>
        <section class="allocation-report" id="allocation-report"><p class="journey-kicker">The allocation report / Q3</p><h2>Where support<br>takes root.</h2><p>Percentage of each annual fund committed to approved local projects. Sample figures, not live fundraising data.</p>'''
        for value,title,note in [(72,'Neighbourhood gardens','€144,000 of €200,000 committed'),(48,'Shared workshops','€72,000 of €150,000 committed'),(91,'Community kitchens','€91,000 of €100,000 committed')]:
            markup += f'<div class="kpi" style="--kpi:{value}%"><div class="metric-label"><h3>{title}</h3><strong>{value}%</strong></div><div class="kpi-track" aria-hidden="true"><i></i></div><p>{note}</p></div>'
        markup += '</section><footer class="report-end"><p class="journey-kicker">Figures before flourish</p><h2>Every number<br>stays readable.</h2><p>Without view timelines, these bars show their final values. Reduced motion does the same. The numeric labels never depend on animation.</p><a href="#report-start">Back to the report introduction ↑</a></footer>'
    elif sid == 'ds-134':
        markup = '<div id="files-start">' + heading('PROJECT LIBRARY / Your reference shelf', 'A little more<br>within reach.', 'Document information, tucked beside each row rather than crowded into it.') + instruction(sid) + '<ul class="swipe-list">'
        for name,file,meta in [('field-guide','Field guide','PDF · 2.4 MB · Updated Sep 18'),('materials','Material notes','PDF · 860 KB · Updated Sep 22')]:
            markup += f'<li class="swipe-item" tabindex="0" aria-label="{file}, scroll for details"><div class="swipe-content"><span class="file-icon" aria-hidden="true">PDF</span><div><strong>{file}</strong><small>{meta}</small></div><span aria-hidden="true">←</span></div><a class="swipe-action" href="#{name}-details" aria-label="Details for {file}">Details ↗</a></li>'
        markup += '</ul><p class="journey-note">The action navigates to information. CSS does not delete a file, download it or save application state.</p></div><div class="document-notes">'
        for name,file,desc in [('field-guide','Field guide','A concise guide to observation, sketching and collecting useful references on a walk.'),('materials','Material notes','An annotated list of papers, threads and cover stocks for the studio’s next workshop.')]:
            markup += f'<section id="{name}-details" tabindex="-1"><p class="journey-kicker">Document information</p><h2>{file}</h2><p>{desc}</p><p class="journey-note">Illustrative document record. No actual file operation is performed.</p><a href="#files-start">Return to documents ↑</a></section>'
        markup += '</div>'
    else:
        raise ValueError(sid)
    return f'<main class="journey-demo journey-{sid}" id="demo-main">{markup}</main>'

COMMON_CSS = '''
/* Batch 02: demo-only composition, never overrides a spell's activated state. */
html:has(.journey-demo) {scroll-behavior:auto}
.journey-demo {width:100%;min-width:0;max-width:1020px;margin-inline:auto;padding:clamp(22px,5vw,64px);font:16px/1.65 ui-sans-serif,system-ui,sans-serif;--color-primary:light-dark(#245b50,#a2d9be);--color-bg:light-dark(#faf9f5,#151918);--color-border:light-dark(#dadbd1,#3a453e)}
body:has(.journey-demo) {background:light-dark(#faf9f5,#151918)}
.journey-demo * {min-width:0}
.journey-head {max-width:720px;margin-bottom:24px}
.journey-demo h1,.journey-demo h2 {font-family:Georgia,serif;font-weight:400;letter-spacing:-.045em;line-height:1.04;text-wrap:balance}
.journey-demo h1 {font-size:clamp(40px,6vw,76px);margin:18px 0 24px}.journey-demo h2 {font-size:clamp(32px,4vw,54px);margin:18px 0 24px}
.journey-demo p {margin:0 0 20px}.journey-demo a {color:inherit;text-underline-offset:5px}
.journey-kicker {font:600 11px/1.6 ui-monospace,monospace;letter-spacing:.13em;text-transform:uppercase}
.journey-lede {max-width:56ch}.journey-demo .journey-instruction {font-size:13px;border-inline-start:2px solid var(--color-primary);padding-inline-start:16px;max-width:65ch;margin:24px 0 32px}
.journey-demo .journey-note {font-size:12px;max-width:65ch;margin:24px 0}
.journey-demo :where(a,[tabindex="0"]):focus-visible {outline:2px solid var(--color-primary);outline-offset:4px}
.journey-demo :where(a) {min-height:44px;display:inline-flex;align-items:center}
.journey-demo :where(section) {scroll-margin-top:24px}
.journey-demo dl {font-size:14px}.journey-demo dl div {padding-block:14px;border-top:1px solid var(--color-border)}.journey-demo dt {font-size:11px;text-transform:uppercase;letter-spacing:.08em}.journey-demo dd {margin:6px 0 0}
'''
CSS = {
'ds-30': '''
.workshop-cover {background:light-dark(#e4dacc,#302a23);min-height:clamp(320px,48vw,480px);position:relative;display:flex;justify-content:center;align-items:center;gap:24px;overflow:hidden}
.book {display:flex;flex-direction:column;justify-content:space-between;width:clamp(110px,21vw,210px);height:clamp(180px,29vw,300px);padding:20px;font:clamp(18px,3vw,28px)/1.05 Georgia,serif;box-shadow:10px 15px 0 #0001;border-inline-start:6px double #ffffff70;transform:rotate(-7deg)}
.book-one {background:#285a4d;color:#f3ebda}.book-two {background:#b65d3e;color:#ffeddb;transform:rotate(8deg)}.book span {font:9px/1.4 ui-monospace,monospace}.cover-caption {position:absolute;bottom:16px;font:11px ui-monospace,monospace}
.workshop-story {max-width:640px;margin:auto}.workshop-story section {padding-block:clamp(64px,12vh,140px);min-height:70dvh;border-bottom:1px solid var(--color-border)}
.workshop-pullquote {font:italic clamp(24px,3vw,36px)/1.3 Georgia,serif;padding-block:32px;color:var(--color-primary)}
.journey-ds-30 .sticky-cta {z-index:2;display:flex;justify-content:space-between;align-items:center;gap:16px;padding:18px 12px;margin-inline:-12px;font-size:14px}
.sticky-cta strong,.sticky-cta span {display:block}.sticky-cta span {font-size:11px}.sticky-cta a {text-align:center;padding:8px 16px;background:var(--color-primary);color:var(--color-text-inverse);text-decoration:none;line-height:1.4}
.session-details {padding-block:70px;min-height:90dvh;max-width:640px;margin:auto}
''',
'ds-55': '''
.journey-ds-55 {max-width:1060px}.journey-ds-55 .card-stack {gap:28dvh;padding-bottom:70dvh;margin-top:60px}
.journey-ds-55 .card {min-height:68dvh;border:1px solid var(--color-border);padding:clamp(20px,4vw,44px);display:flex;flex-direction:column;background:var(--color-bg)}
.route-label {display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;font:11px/1.4 ui-monospace,monospace;text-transform:uppercase}
.route-illustration {height:clamp(100px,20vh,200px);position:relative;overflow:hidden;margin-block:24px;background:#d6dcd2;isolation:isolate}
.route-illustration span {position:absolute;bottom:-1px;width:65%;height:90%;background:#3c5d4d;clip-path:polygon(0 100%,50% 0,100% 100%)}.route-illustration span:nth-child(2) {left:35%;height:65%;background:#8e9e82}.route-illustration span:nth-child(3) {width:50px;height:50px;top:15px;left:72%;border-radius:50%;clip-path:none;background:#e5b46c;z-index:-1}
.route-ridge .route-illustration {background:#e2d5c8}.route-ridge .route-illustration span {background:#976a53}.route-ridge .route-illustration span:nth-child(2) {background:#c2977a}
.route-shore .route-illustration {background:#cadcde}.route-shore .route-illustration span:not(:nth-child(3)) {clip-path:ellipse(65% 50% at 50% 90%);background:#4f7977}.route-shore .route-illustration span:nth-child(2) {background:#89aaa2}
.route-copy p {max-width:54ch}.route-copy strong {font:italic 18px Georgia,serif;color:var(--color-primary)}
.route-end {min-height:100dvh;display:flex;flex-direction:column;justify-content:center;padding-block:70px}
''',
'ds-69': '''
.journey-ds-69 {max-width:1140px}.ledger-summary {display:flex;justify-content:space-between;flex-wrap:wrap;gap:14px;font-size:12px;padding-block:18px;border-top:1px solid var(--color-border)}.ledger-summary strong {font-size:20px;margin-right:6px}
.journey-ds-69 .table-wrapper {width:100%;border:1px solid var(--color-border);scrollbar-width:thin}
.journey-ds-69 table {min-width:1120px;width:100%;border-collapse:separate;border-spacing:0;font-size:14px;font-variant-numeric:tabular-nums}
.journey-ds-69 caption {text-align:left;padding:14px 18px;font-size:12px}.journey-ds-69 th,.journey-ds-69 td {padding:20px 18px;text-align:left;white-space:nowrap;border-bottom:1px solid var(--color-border)}
.journey-ds-69 thead th {font:600 10px ui-monospace,monospace;text-transform:uppercase;letter-spacing:.09em}.journey-ds-69 th:first-child {width:190px}
.journey-ds-69 tbody th {font-weight:600}.journey-ds-69 tbody tr:nth-child(even) {background:light-dark(#f0f1e9,#1b231f)}.table-foot {font:12px ui-monospace,monospace;padding-top:18px}
''',
'ds-93': '''
.journey-ds-93 {max-width:1140px}.journey-ds-93 .snap-carousel {width:100%;padding-bottom:14px;scrollbar-width:thin}
.journey-ds-93 .slide {min-width:0}.journey-ds-93 .slide img {object-fit:cover;height:clamp(220px,45dvh,420px)}
.journey-ds-93 .caption {font-size:clamp(14px,2vw,22px);line-height:1.3}.caption small,.caption strong {display:block}.caption small {font:10px/1.5 ui-monospace,monospace;text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px}.caption strong {font-family:Georgia,serif;font-weight:400}
.gallery-credit {font-size:11px;margin-top:18px!important}
''',
'ds-111': '''
.journey-ds-111 {max-width:1000px}.report-intro {min-height:108dvh;display:flex;flex-direction:column;align-items:flex-start;justify-content:center;padding-bottom:64px}
.report-seal {display:flex;gap:24px;align-items:center;border-block:1px solid var(--color-border);padding-block:24px;margin-bottom:24px;width:100%;max-width:560px}.report-seal span {font:italic 72px/1 Georgia,serif;color:var(--color-primary)}.report-seal small {font:11px/1.7 ui-monospace,monospace;letter-spacing:.12em}
.allocation-report {max-width:660px;margin-inline:auto;padding-block:50px}.allocation-report>p:not(.journey-kicker) {font-size:14px;max-width:54ch}
.allocation-report .kpi {padding-block:40px;margin-bottom:22px;border-bottom:1px solid var(--color-border)}.metric-label {display:flex;align-items:baseline;justify-content:space-between;gap:20px;margin-bottom:20px}.metric-label h3 {font-size:clamp(16px,2vw,22px);font-weight:500;margin:0}.metric-label strong {font:40px/1 Georgia,serif}.kpi p {font-size:12px;margin:14px 0 0}
.report-end {min-height:100dvh;display:flex;flex-direction:column;align-items:flex-start;justify-content:center;max-width:620px;margin:auto}.report-end p {max-width:50ch}
''',
'ds-134': '''
.journey-ds-134 {max-width:800px}.journey-ds-134 .swipe-list {margin-top:40px;border-top:1px solid var(--color-border)}
.journey-ds-134 .swipe-item {border-bottom:1px solid var(--color-border)}.journey-ds-134 .swipe-content {display:flex;align-items:center;gap:16px;padding:24px 12px}.swipe-content div {flex:1}.swipe-content strong {display:block;font-size:16px}.swipe-content small {display:block;font-size:11px;margin-top:4px}.file-icon {padding:10px 6px;font:10px ui-monospace,monospace;border:1px solid var(--color-border);border-radius:2px;background:var(--color-bg)}
.journey-ds-134 .swipe-action {display:grid;color:var(--color-text-inverse);font-size:13px}
.document-notes {padding-top:120px}.document-notes section {padding:30px 0;min-height:55dvh;border-top:1px solid var(--color-border)}.document-notes section:target {outline:2px solid var(--color-primary);outline-offset:12px}
''',
}

# Small functional fixtures for CSS-only integration bundles and legacy previews.
# Scene-only controls/art direction above are intentionally not exported here.
INTEGRATION_HTML = {
    '30': '<article style="inline-size:min(100%,36rem)"><div style="min-block-size:150vh"><h2>Paper &amp; Practice</h2><p>Scroll through a workshop itinerary.</p></div><aside class="sticky-cta"><a href="#visit-info">Session details ↓</a></aside></article><section id="visit-info" tabindex="-1"><h2>Visit information</h2><p>A three-hour paper-binding workshop. Illustrative itinerary, not a booking service.</p></section>',
    '55': '<div class="card-stack" style="inline-size:min(100%,36rem);padding-block-end:60vh">' + ''.join(
        f'<article class="card" style="min-block-size:55vh;margin-block-end:20vh;--stack-offset:{i*64}px;background:var(--color-bg);border:1px solid var(--color-border);padding:1rem"><h2>{title}</h2><p>{copy}</p></article>'
        for i,(title,copy) in enumerate([('01 / The treeline','Start beneath the pines.'),('02 / The ridgeline','Take the longer view.'),('03 / The shoreline','Leave time for nothing.')])
    ) + '</div>',
    '69': '<div class="table-wrapper" style="inline-size:min(100%,32rem)" tabindex="0" role="region" aria-label="Project ledger, scroll horizontally"><table style="min-inline-size:54rem"><caption>Studio project ledger</caption><thead><tr>' + ''.join(f'<th scope="col">{x}</th>' for x in ['Project','Discipline','Lead','Delivery','Days','Budget','Status']) + '</tr></thead><tbody>' + ''.join(
        '<tr><th scope="row">'+r[0]+'</th>'+''.join(f'<td>{x}</td>' for x in r[1:])+'</tr>'
        for r in [('Field journal','Editorial','Mina Rao','Sep 30','12','€8,400','On track'),('Orchard identity','Brand','Theo Kim','Oct 07','18','€12,600','In review'),('Harbour site','Digital','Ari Soto','Oct 12','24','€19,200','On track')]
    ) + '</tbody></table></div>',
}
