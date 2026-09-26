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
