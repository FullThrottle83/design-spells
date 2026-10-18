# Preview audit, 2026-10-18

Independent audit of whether each hosted Design Spells demo actually demonstrates
its technique. Scope: all 154 stable IDs on `origin/main` (35110d2), standalone
demos at `/play/ds-N/` (the document the documentation iframes embed).
Evidence: [`preview-audit-2026-10/inventory.json`](preview-audit-2026-10/inventory.json)
(per-spell class, evidence kind and repair) and
[`preview-audit-2026-10/before-after.png`](preview-audit-2026-10/before-after.png).

**Verdict: REPAIR.** Details at the end.

## TestSprite: not executed

The `@testsprite/testsprite-mcp` server is registered in `~/.claude.json` only
for a different project; it is not configured for this repository and its tools
were not loaded in this session. No TestSprite case was run and no credits were
spent. Credentials were neither read into this repository nor used. Findings
below come from local Playwright against the candidate build, never from the
production deployment. To run the bounded campaign the brief describes, add the
server to this project (`claude mcp add TestSprite --env API_KEY=… -- npx @testsprite/testsprite-mcp@latest`),
restart the session, and verify first that it can reach a localhost or tunnelled
build; if it cannot, test only after deployment and say so.

## Method

A Playwright harness (Chromium 151.0.7922.34, Playwright 1.62.1) loaded every demo at
1440×900, 390×844 and 900×390 (the documentation frame) and recorded:

- route status for doc, play, download and bundle pages, console errors, failed
  requests and broken images;
- every authored rule's selector matched against the fixture, with state
  pseudo-classes neutralised, to find rules that style nothing;
- zero-size elements, horizontal overflow, scrollers and scroll runway;
- real pointer and keyboard interactions (hover, Tab focus, press, checkbox,
  `:target`, `<details>`, invoker and popover buttons, wheel scroll) with a
  computed-style and pixel delta against the resting state;
- a rest-state pixel comparison against the same page generated without the
  spell's CSS (`render_play(baseline=True)`);
- scroll-timeline source and progress, via `document.getAnimations()`.

The first pass produced 61 flags. Most were harness artifacts (hidden checkbox
inputs inside labels, hidden ancestors, `[open]` not treated as state, a scroll
baseline taken after a link had already scrolled) or documented fallback
idioms, and were corrected or triaged by hand. 19 were confirmed defects.

## Counts

| | |
|---|---|
| Spells inventoried | 154 |
| PASS (observable effect verified, Chromium 151) | 146 |
| of which a state, interaction or scroll change was measured | 103 |
| of which a running animation was observed | 6 |
| of which a static effect differs from the unstyled baseline | 36 |
| of which covered by an existing two-document navigation test | 1 (ds-14) |
| Confirmed defects found | 19 |
| Repaired by this branch | 17 fully, 1 partially (ds-109) |
| Still broken | 1 (ds-27, PR #53) |
| UNSUPPORTED in Chromium 151 | 2 (ds-100 `grid-lanes`, ds-151 `random()`); both show their documented fallback |
| INCONCLUSIVE | 4 (ds-114, ds-62, ds-98, ds-54) |
| NEEDS INTERACTION not demonstrated by the hosted demo | 1 (ds-109) |
| TestSprite cases / credits | 0 / 0 |
| Interaction trials measured in the final inventory | 170 |
| Console errors, mobile horizontal overflow (final) | 0, 0 |

"PASS" means the effect is observable in the hosted demo in Chromium. It does not
mean the effect is the one intended in every engine, and it is not a
keyboard, zoom, reduced-motion, dark-scheme or assistive-technology review.
Reduced motion and dark scheme were not swept systematically here; the existing
pilot specs cover them for their spells.

## Confirmed defects and repairs

Canonical snippet defects (these affect anyone copying the spell):

| Spell | Root cause | Repair |
|---|---|---|
| ds-91, ds-135, ds-139 | `animation-timeline: view()` binds to the nearest scroll container. The wrapper's `overflow: hidden` is one, and never scrolls, so progress was pinned at 0.5 / 0.5 / 1 regardless of page scroll, in every browser. | `overflow: clip` after the `hidden` fallback, plus the existing scroll runway for the demo. |
| ds-105 | `attr()` reads the styled element, but `data-value` was on the parent: the fill was always 0%. | Attribute moved to `.attr-meter-fill` in README.md (and SKILL.md). |
| ds-50 | `pattern="[a-z0-9-]+"` is a syntax error under the `v` flag, so browsers ignored it. | Hyphen escaped. |

Demo environment defects (fixtures; spell CSS untouched):

| Spell | Root cause | Repair |
|---|---|---|
| ds-110 | Shrink-wrapped figure 20px wide, every flex bar 0px. | Stated inline size. |
| ds-63, ds-bonus | Text never wrapped, so hyphenation and `text-wrap` had nothing to act on. | Narrow column / 24rem container. |
| ds-94, ds-81 | Content never overflowed, so a sticky header and a scroll-state hint were unobservable. | 14 rows; 15rem container. |
| ds-146 | Dialog did not scroll and the page behind could not. | Long dialog content; demo-only page runway in `build_pages.py`. |
| ds-3, ds-13, ds-25, ds-68 | Hint said "Hover or focus" but the fixture had no focusable element for `:focus-within`. | Focusable links. |
| ds-141 | Skip link pointed at a missing `#main-content`. | Added target. |
| ds-112 | `::target-text` needs a text-fragment navigation. | Same-page text-fragment link. |
| ds-109 | Fixture was a literal ellipsis. | Honest card; a ds-14-style two-page walkthrough is still missing. |

A first draft of the ds-146 repair put an empty 150vh filler in the shared fixture.
The existing "every visible top-level element has a non-zero box" check caught it,
and it would have bloated the classic explorer's preview. The filler now lives in
the standalone demo only.

## Regression tests added

`tests/preview-observability.spec.mjs`, 19 cases, registered in the
cross-browser config. 18 fail on unmodified `origin/main` and pass on this branch
(the 19th is a sweep of all 154 demos for console errors, failed requests and
broken images and passes on both). Each asserts measured state: bar widths and
height ratio from typed `attr()`, meter fill ratio, wrapped line counts and
`hyphens: auto` versus `manual` (asserted only where the browser build ships a
hyphenation dictionary: a local Chromium does, CI's runner build does not), balanced versus greedy line widths, timeline
source and progress, sticky offset after `scrollTop`, hint opacity with a
widened control, validity and `patternMismatch`, Tab focus and `:target`,
`getAnimations()` play state, pixel change after a text-fragment click, and
wheel chaining with a control that proves the test can fail. Chromium-only cases
(typed `attr()`, scroll timelines, scroll-state, text fragments, modal wheel
chaining) skip explicitly elsewhere. `tests/test_walkthroughs.py` also covers
the three new scroll runways (ds-135 separately, because its demo rewrites a hosted
image and cannot meet the byte-for-byte contract).

## Verification

Run on an idle machine, from the branch, after `npm run build`:

| Check | Result |
|---|---|
| `npm run build` | clean; regenerated artifacts committed |
| `python3 -m unittest discover -s tests` | 77 tests, OK |
| `npx playwright test` (Chromium) | 580 passed (baseline on origin/main: 561) |
| `playwright test -c playwright.cross-browser.config.mjs --project=firefox` | final tree: 369 passed, 9 skipped (declared Chromium-only), 1 failed; an earlier full run of the same spec set was 370 passed, 0 failed. The failure was `showcase-pilot06` ds-117 hosted (hash after clicking the primary link), a spell this branch does not touch; it passed 5/5 repeated in isolation on this branch and 5/5 on unmodified `origin/main`, so it is an existing intermittent. |
| WebKit | **not run**: the host lacks `libevent-2.1-7t64` and `libavif16` and installing them needs sudo; CI's WebKit job is the evidence |
| `git diff --check` | clean |

An earlier run with the Chromium and cross-browser suites started concurrently
showed load-induced failures (8 Chromium tests that pass in isolation, and
Firefox pilot tests that passed on rerun); the numbers above are from
sequential runs on an otherwise idle machine.

## PR #53 (DS-27)

Inspected, not modified. It constrains the ds-27 fixture and adds a test. Its
`test` job fails at `git diff --exit-code` because `public/spells/ds-27/index.html`
(which shows the fixture HTML) was not regenerated by `npm run build`. Running the
build on that branch and committing the result should turn it green. This
branch does not touch ds-27, so the two should merge without overlap in
`scripts/build.py`; regenerate generated files after whichever lands second.

## Remaining issues, by severity

1. **ds-27 is broken on main** until PR #53 is fixed and merged.
2. **ds-109** cannot show its cross-document view transition in the hosted demo; it needs a two-page walkthrough like ds-14.
3. **WebKit was not executed locally** and Firefox only ran the existing suites plus the engine-neutral subset of the new spec. Many spells rely on features whose Safari and Firefox support was not measured here.
4. **ds-114, ds-62, ds-98, ds-54** are inconclusive: headless Chromium hides scrollbars, and scroll markers, interest-invoker delay and base-select option hover were not exercised.
5. No keyboard-only, zoom, screen-reader or systematic reduced-motion and dark-scheme review.

## GO / REPAIR / NO-GO

**REPAIR.** Not ready to publish as "every preview demonstrates its technique" until
this branch and PR #53 (with ds-27's generated page regenerated) are reviewed and
merged and WebKit has run in CI. After that, the remaining issues are ds-109 and
four inconclusive items, none of which blocks publishing. Highest user-visible
impact: ds-91, ds-135 and ds-139, whose scroll animation never ran in any browser,
followed by ds-105 and ds-110, whose bars were invisible.
