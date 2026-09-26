# Pilot 01 — captured browser evidence

2026-09-26 · Chromium **153.0.8010.0** (external sandbox binary), Playwright 1.62.1.
No client scripts. These are actual rendered captures, not generated mockups.
Before: generated pages at `ac626cf`. After: Pilot 01 changes on this PR.

[Before overview](before-contact.png) · [After overview](after-contact.png)

`before-active` means the attempted action: hover ds-5/95, scroll ds-12,
fill ds-16. Ds-21 had no link and ds-37 had no keyboard/touch size controls;
their before-active files are unchanged, not fabricated active states.
Raw before geometry: [JSON](before-observations.json).

After capture regeneration (installed Playwright Chromium required):

```sh
npm run build
DS_CAPTURE=1 npx playwright test tests/showcase-pilot.spec.mjs --workers=1
```

Tests assert live changes before capturing. After screenshots are full-page so
longer content and instructions are not hidden. Before screenshots use the
requested viewport; these initial fixtures fit above the fold. File names record
viewport width; heights are 900 desktop and 844 mobile. Reduced-motion suffix
means `prefers-reduced-motion: reduce`; dark images use a dark mobile context.
No claim of physical touch or assistive-technology testing.

| Spell | Before desktop | After desktop | Before mobile | After mobile | Reduced motion | Dark mobile |
|---|---|---|---|---|---|---|
| ds-5 | [initial](before-ds-5-1440.png) / [attempted action](before-active-ds-5-1440.png) | [initial](after-ds-5-1440.png) / [active](after-ds-5-1440-active.png) | [initial](before-ds-5-390.png) / [attempted action](before-active-ds-5-390.png) | [initial](after-ds-5-390.png) / [active](after-ds-5-390-active.png) | [desktop](after-ds-5-1440-reduced-active.png) / [mobile](after-ds-5-390-reduced-active.png) | [active](after-ds-5-390-dark.png) |
| ds-12 | [initial](before-ds-12-1440.png) / [attempted action](before-active-ds-12-1440.png) | [initial](after-ds-12-1440.png) / [active](after-ds-12-1440-active.png) | [initial](before-ds-12-390.png) / [attempted action](before-active-ds-12-390.png) | [initial](after-ds-12-390.png) / [active](after-ds-12-390-active.png) | [desktop](after-ds-12-1440-reduced-active.png) / [mobile](after-ds-12-390-reduced-active.png) | [active](after-ds-12-390-dark.png) |
| ds-16 | [initial](before-ds-16-1440.png) / [attempted action](before-active-ds-16-1440.png) | [initial](after-ds-16-1440.png) / [active](after-ds-16-1440-active.png) | [initial](before-ds-16-390.png) / [attempted action](before-active-ds-16-390.png) | [initial](after-ds-16-390.png) / [active](after-ds-16-390-active.png) | [desktop](after-ds-16-1440-reduced-active.png) / [mobile](after-ds-16-390-reduced-active.png) | [active](after-ds-16-390-dark.png) |
| ds-21 | [initial](before-ds-21-1440.png) / [attempted action](before-active-ds-21-1440.png) | [initial](after-ds-21-1440.png) / [active](after-ds-21-1440-active.png) | [initial](before-ds-21-390.png) / [attempted action](before-active-ds-21-390.png) | [initial](after-ds-21-390.png) / [active](after-ds-21-390-active.png) | [desktop](after-ds-21-1440-reduced-active.png) / [mobile](after-ds-21-390-reduced-active.png) | [active](after-ds-21-390-dark.png) |
| ds-37 | [initial](before-ds-37-1440.png) / [attempted action](before-active-ds-37-1440.png) | [initial](after-ds-37-1440.png) / [active](after-ds-37-1440-active.png) | [initial](before-ds-37-390.png) / [attempted action](before-active-ds-37-390.png) | [initial](after-ds-37-390.png) / [active](after-ds-37-390-active.png) | [desktop](after-ds-37-1440-reduced-active.png) / [mobile](after-ds-37-390-reduced-active.png) | [active](after-ds-37-390-dark.png) |
| ds-95 | [initial](before-ds-95-1440.png) / [attempted action](before-active-ds-95-1440.png) | [initial](after-ds-95-1440.png) / [active](after-ds-95-1440-active.png) | [initial](before-ds-95-390.png) / [attempted action](before-active-ds-95-390.png) | [initial](after-ds-95-390.png) / [active](after-ds-95-390-active.png) | [desktop](after-ds-95-1440-reduced-active.png) / [mobile](after-ds-95-390-reduced-active.png) | [active](after-ds-95-390-dark.png) |
