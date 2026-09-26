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
region; its snap targets and authored spotlight styles are unchanged. Verify a
*change of highlighted card*, not just that an overflow box has nonzero size.

Ds-46 provides a native, demo-only Fit content checkbox that changes the
content conditions from overflowing to wrapped. The authored scroll-state CSS
still determines whether the hint becomes visible; the fixture must change
actual scrollWidth/clientWidth as well as its rendered opacity. This is a
visual scrollability example, not a fully implemented tabs component. Unsupported
browsers retain native scrolling and readable content. Manual keyboard, zoom,
screen-reader and motion review remains separate from these browser assertions.
