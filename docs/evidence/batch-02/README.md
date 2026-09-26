# Batch 02 — scroll journeys and fallback evidence

2026-09-26 · Chromium **153.0.8010.0**, Playwright **1.62.1**; scripts disabled.
Before: generated pages at `6414b5a`. After: Batch 02 continuation in PR #41.

[Before overview](before-contact.png) · [After overview](after-contact.png) · [Raw baseline measurements](before-observations.json)

These are actual rendered screenshots, not design mockups. New landscape images are AI-generated editorial assets, explicitly labelled in their demo.

Before-active: attempted page scroll for ds-30/55/111, horizontal scroll for ds-69/93/134, and a click on the inert Delete button for ds-134. The old page-scroll demos had no runway, so unchanged screenshots do not imply successful activation. Ds-69's capture returns to the start after checking the attempted end state; JSON includes both observations. Ds-111's before-active image shows deliberate removal of the timeline enhancement, exposing its zero-width fallback; JSON also records the supported initial fill.

After-active: pinned session bar; three stacked route cards; scrolled project table with shadow; second snapped caption; entered metric values; revealed Details link. Tests additionally check reversals and ds-55's actual exit scale/filter, which is distinct from its pinned state.

Reproduce after captures with installed Chromium:

```sh
npm run build
DS_CAPTURE=1 npx playwright test tests/showcase-scroll.spec.mjs --workers=1
```

Viewports: desktop **1440×900**, mobile **390×844**. The dark captures deliberately remove enhancement rules as documented in the test: these are **fallback simulations**, not old-browser screenshots. Reduced-motion images use the real media preference. Physical touch gestures and screen readers remain unreviewed.

| Spell | Before desktop | After desktop | Before mobile | After mobile | Reduced motion | Dark mobile fallback |
|---|---|---|---|---|---|---|
| ds-30 | [initial](before-ds-30-1440.png) / [attempt](before-active-ds-30-1440.png) | [initial](after-ds-30-1440.png) / [active](after-ds-30-1440-active.png) | [initial](before-ds-30-390.png) / [attempt](before-active-ds-30-390.png) | [initial](after-ds-30-390.png) / [active](after-ds-30-390-active.png) | [desktop](after-ds-30-1440-reduced-active.png) / [mobile](after-ds-30-390-reduced-active.png) | [fallback](after-ds-30-390-dark.png) |
| ds-55 | [initial](before-ds-55-1440.png) / [attempt](before-active-ds-55-1440.png) | [initial](after-ds-55-1440.png) / [active](after-ds-55-1440-active.png) | [initial](before-ds-55-390.png) / [attempt](before-active-ds-55-390.png) | [initial](after-ds-55-390.png) / [active](after-ds-55-390-active.png) | [desktop](after-ds-55-1440-reduced-active.png) / [mobile](after-ds-55-390-reduced-active.png) | [fallback](after-ds-55-390-dark.png) |
| ds-69 | [initial](before-ds-69-1440.png) / [attempt](before-active-ds-69-1440.png) | [initial](after-ds-69-1440.png) / [active](after-ds-69-1440-active.png) | [initial](before-ds-69-390.png) / [attempt](before-active-ds-69-390.png) | [initial](after-ds-69-390.png) / [active](after-ds-69-390-active.png) | [desktop](after-ds-69-1440-reduced-active.png) / [mobile](after-ds-69-390-reduced-active.png) | [fallback](after-ds-69-390-dark.png) |
| ds-93 | [initial](before-ds-93-1440.png) / [attempt](before-active-ds-93-1440.png) | [initial](after-ds-93-1440.png) / [active](after-ds-93-1440-active.png) | [initial](before-ds-93-390.png) / [attempt](before-active-ds-93-390.png) | [initial](after-ds-93-390.png) / [active](after-ds-93-390-active.png) | [desktop](after-ds-93-1440-reduced-active.png) / [mobile](after-ds-93-390-reduced-active.png) | [fallback](after-ds-93-390-dark.png) |
| ds-111 | [initial](before-ds-111-1440.png) / [attempt](before-active-ds-111-1440.png) | [initial](after-ds-111-1440.png) / [active](after-ds-111-1440-active.png) | [initial](before-ds-111-390.png) / [attempt](before-active-ds-111-390.png) | [initial](after-ds-111-390.png) / [active](after-ds-111-390-active.png) | [desktop](after-ds-111-1440-reduced-active.png) / [mobile](after-ds-111-390-reduced-active.png) | [fallback](after-ds-111-390-dark.png) |
| ds-134 | [initial](before-ds-134-1440.png) / [attempt](before-active-ds-134-1440.png) | [initial](after-ds-134-1440.png) / [active](after-ds-134-1440-active.png) | [initial](before-ds-134-390.png) / [attempt](before-active-ds-134-390.png) | [initial](after-ds-134-390.png) / [active](after-ds-134-390-active.png) | [desktop](after-ds-134-1440-reduced-active.png) / [mobile](after-ds-134-390-reduced-active.png) | [fallback](after-ds-134-390-dark.png) |
