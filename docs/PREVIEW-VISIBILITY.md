# Making subtle effects observable

This catalogue demonstrates authored CSS, rather than amplifying it in exports.
Some effects only appear on hover, keyboard focus, during an active press,
while scrolling, in a different theme, or in print preview. Their small
movement or contrast can be intentional and should not be silently rewritten.

The individual documentation pages for ds-1, ds-2, ds-5, ds-6, ds-7, ds-18,
ds-24 and ds-38 provide a **base fixture / with spell CSS** comparison with
identical markup and shared stage CSS. Both demos require the indicated native
interaction. This is an editorial pilot, not a claim that the comparison
covers or verifies all spells. The baseline pages are noindex, excluded from
the sitemap, and contain no authored spell CSS or JavaScript.

Root scroll-state demo pages ds-43 and ds-47 include the documented opt-in
root scroll-state prerequisite. Actual browser support still varies. Their
downloadable demo pages receive the same prerequisite. No such opt-in rule
is injected into other spell demos.

Verification: check that all comparison routes have the exact same fixture
markup, the effect side has the unchanged authored spell CSS, the baseline
does not, and no scripts execute. Playwright additionally checks pseudo-
element and background state changes on representative interactive spells.

Behavior claims, reduced-motion decisions and production boundaries are tracked
in [BEHAVIOR-CONTRACTS.md](BEHAVIOR-CONTRACTS.md).

## Stage-specific native walkthroughs

The hosted and downloaded demos for ds-8, ds-72, ds-125 and ds-145 now place
scroll-triggered targets after a full-height introduction, with a native jump
link and a tail runway. This makes the view-timeline state reachable rather
than showing an animation already completed on load. The source and integration
bundle remain unchanged. ds-35 exposes native light/dark controls using a
preview-only scheme override; ds-9 has a plain reload link to replay the
one-shot entrance; ds-143 tells visitors to use browser print preview rather
than faking print CSS in screen media. No preview helper requires script.

## Sticky scroll-state walkthrough (ds-44)

The ds-44 hosted and downloaded demos provide a preview-only introduction and
scroll runway so the existing sticky navigation can actually reach its top
inset. The authored CSS and integration bundle are unchanged. Chromium's
`stuck: top` transition is tested by reading the rendered `box-shadow` before,
during and after document scrolling, not by a CSS syntax probe. Firefox/WebKit
retain the native sticky positioning when scroll-state styling is unavailable.
A browser test does not replace manual keyboard, zoom or screen-reader review.

## Snapped and scrollable states (ds-45 / ds-46)

Ds-45's hosted/downloaded carousel is a labelled, keyboard-focusable scroll
region; its snap targets are unchanged, while the authored query selector now
matches the base rule's specificity. Verify a
*change of highlighted card*, not just that an overflow box has nonzero size.

Ds-46 provides a native, demo-only Fit content checkbox that changes the
content conditions from overflowing to wrapped. The authored query selector
was corrected to win the cascade and determines whether the hint becomes visible; the fixture must change
actual scrollWidth/clientWidth as well as its rendered opacity. This is a
visual scrollability example, not a fully implemented tabs component. Unsupported
browsers retain native scrolling and readable content. Manual keyboard, zoom,
screen-reader and motion review remains separate from these browser assertions.

## Observability audit (2026-10-18)

A nonzero box is not evidence that a spell demonstrates its technique. An
independent Chromium inventory of all 154 hosted demos found fixtures and
three authored snippets whose effect could not occur. Root causes, fixed here
without touching spell CSS except where the CSS itself was wrong:

- **Scroll timeline bound to a box that never scrolls (ds-91, ds-135, ds-139).**
  `animation-timeline: view()` tracks the nearest scroll container. The
  authored wrappers used `overflow: hidden`, which *is* a scroll container, so
  progress stayed pinned at 0.5 / 1 / 0.5 regardless of page scroll in every
  browser. The authored CSS now adds `overflow: clip` after the `hidden`
  fallback. The three demos also receive the existing scroll runway.
- **Authored markup and CSS disagreed (ds-105).** `attr()` reads the styled
  element, but `data-value` sat on the parent, so the fill was always 0%. The
  attribute moved onto `.attr-meter-fill` in README.md and the demo.
- **Collapsed shrink-wrapped fixture (ds-110).** Flex bars with no content in a
  centred grid stage were 0px wide; the fixture states an inline size.
- **Nothing to act on (ds-63, ds-bonus, ds-81, ds-94, ds-146).** Hyphenation
  and `text-wrap` need text that wraps, the overflow hint needs overflowing
  crumbs, the sticky header needs rows beyond the scrollport, and overscroll
  containment needs a dialog that scrolls above a page that could. Fixtures
  now supply those conditions; nothing in the spell CSS changed.
- **Keyboard path unreachable (ds-3, ds-13, ds-25, ds-68).** The hint said
  "Hover or focus", but the fixture had no focusable element for
  `:focus-within`.
- **Dead ends (ds-141, ds-112, ds-109).** The skip link pointed at a missing
  `#main-content`; `::target-text` needs a text-fragment navigation (now a
  same-page link); the ds-109 fixture was a literal ellipsis.
- **Invalid pattern (ds-50).** `pattern="[a-z0-9-]+"` is a syntax error under
  the `v` flag browsers use, so the constraint was silently ignored.

`tests/preview-observability.spec.mjs` asserts measurable state for each
(geometry, animation progress and timeline source, scroll offsets, validity,
computed style) and includes controls that fail without the fix. Chromium-only
cases skip elsewhere explicitly. Known limits: Playwright's headless Chromium
hides scrollbars, so ds-114's themed scrollbar is verified by computed style
only; ds-27 is tracked in PR #53; ds-109 still needs a ds-14-style
two-document walkthrough to show its transition.
