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
