# Pilot 02 browser evidence

Local Chromium 153.0.8010.0. Captured at 1440×900 and 390×844 with client scripts disabled. Original embedded vector artwork requires no network requests. No prior-pilot evidence is changed.

## Visual contact sheets

Each pair reads **initial, activated**; rows contain ds-111/93, ds-134/30, ds-55/69.

| Mode | Desktop | Mobile |
|---|---|---|
| Before (normal/light) | [Contact](before-1440-contact.jpg) | [Contact](before-390-contact.jpg) |
| After normal/light | [Contact](after-1440-no-preference-light-contact.jpg) | [Contact](after-390-no-preference-light-contact.jpg) |
| After reduced/light | [Contact](after-1440-reduce-light-contact.jpg) | [Contact](after-390-reduce-light-contact.jpg) |
| After normal/dark | [Contact](after-1440-no-preference-dark-contact.jpg) | [Contact](after-390-no-preference-dark-contact.jpg) |
| After reduced/dark | [Contact](after-1440-reduce-dark-contact.jpg) | [Contact](after-390-reduce-dark-contact.jpg) |

Individual captures: `before/{number}-{width}-{initial|active}.jpg`; `after/{number}-{width}-{motion}-{scheme}-{initial|active}.jpg`. KPI also includes `complete` screenshots. Before “active” means an attempted native scroll; the short placeholders for ds-30/55/111 had no meaningful journey. After KPI active means intermediate fill, not completion. Card-deck active means overlap, not a fabricated active class.

[After raw rendered measurements](after/observations.json) record scroll offsets, dimensions, opacity, transforms, filters, shadows and engine version per screenshot. [Before page text](before/observations.json) records the original fixture content. The behavior suite additionally asserts rendered outcomes in documentation iframes and downloadable HTML; screenshots here show hosted pages, not separate copies of each surface.

Reproduce after evidence: build, serve `public` on port 8787, then `node scripts/capture_pilot02.mjs after`. Optional `DS_CHROMIUM_PATH` and `DS_CAPTURE_ORIGIN` select an external runtime/server. `scripts/pilot02_contact_sheet.py` uses optional Pillow, outside the build dependency path. Reproducing before evidence requires the baseline checkout; do not overwrite it using the new source.

Limits: automated keyboard, native scrolling and emulated touch, not physical devices or assistive technology. Fallback-removal tests simulate unavailable enhancements; actual Firefox/WebKit observations are recorded separately in the audit ledger. No accessibility certification is implied.

## Simulated unsupported enhancements

[Mobile fallback contact sheet](fallback-mobile-contact.jpg) and [`fallback/observations.json`](fallback/observations.json) record the four enhancement-dependent spells after removing `@supports` and `@container` rules. Individual desktop/mobile initial and active captures live in `fallback/`. This is deliberate fault injection, not a historical browser screenshot. The filled KPI, all captions, readable native sticky deck and native table scroll remain. Reproduce with `node scripts/capture_pilot02.mjs fallback`.

## Limited next-batch triage

[ds-49 mobile](next-batch-ds49.jpg), [raw geometry](next-batch-triage.json): its Filters panel is already displayed before clicking and stays displayed; its right edge measures 396.83px in a 390px viewport. No ds-49 code is changed in this pilot.
