# Behavior contracts and honest boundaries

A spell is a **CSS/HTML reference technique**, not a certified production-ready
component. The catalogue's support badges are dated registry estimates; smoke
tests do not certify complete behavior, keyboard access, accessibility or WCAG.
Keep `verification.behavior` and `verification.accessibility` unpromoted until
per-spell evidence and appropriate manual review actually exist.

## Audited examples

- **ds-131 — Dismissible Toast:** `popover="manual"` requires a native
  hide command (or application code). Animating opacity or `display` does not
  invoke the popover close algorithm. The spell now has an explicit
  `command="hide-popover"` button, a persistent visible notification, and
  opt-out of nonessential movement. Do not claim automatic timeout.
- **ds-85 — visual wizard shell:** CSS/radio state shows three panels and
  progress. It does not validate user input, guard skipped steps, submit data,
  or implement a complete keyboard/focus workflow. A production wizard needs
  explicit application design and accessibility review.
- **ds-43 / ds-47 — directional root scroll:** host and download demos need an
  opt-in root `container-type: scroll-state` preset. Their instruction is
  **scroll**, not resize. `scrolled` queries describe the most recent
  direction, not absolute distance or permanent "scrolled past" state.
- **ds-44:** The hosted/downloaded fixture supplies enough document runway for
  the unchanged `stuck: top` query to transition. A visible shadow is a
  progressive enhancement; without scroll-state support, native sticky
  positioning and text remain. The nav is demonstrative markup, not a complete
  table of contents with destination links. Individual automated observations
  do not establish screen-reader behavior or WCAG conformance.
- **ds-45 — Snapped Spotlight:** the hosted/downloaded scroller has a focusable,
  named region. A snap position alone is not evidence of the authored spotlight;
  inspect the descendant article's rendered opacity and scale before/after a
  second target is snapped. Without scroll-state support, ordinary mandatory
  CSS scroll snapping remains and the cards keep their default dimmed style.
  This is a visual carousel sample, not a production carousel control system.
- **ds-46 — Real Overflow Hint:** a preview-only checkbox lets the same content
  overflow or wrap, without changing authored CSS. Assert scrollWidth/clientWidth
  alongside the rendered hint opacity in both states. Without scroll-state
  support, the arrow stays hidden and the scrollable region remains available.
  The span labels are not functional tabs. The original 180ms/220ms transitions
  in ds-46/ds-45 do not currently opt out under reduced-motion preference;
  test the resulting state without claiming an audited motion policy.

## Reduced motion

`prefers-reduced-motion` expresses a preference to reduce nonessential motion,
not a universal ban on all visual state changes. A purposeful CSS-only
reference still needs a usable final state when motion is reduced. New and
edited motion-heavy spells must have an explicit decision: reduce, remove,
replace, or justify essential motion. Test both preference states and ensure
focus, labels, disclosure, and dismissal remain usable.

The inherited catalogue still contains unreviewed animation/transition
patterns. Do not stamp the whole library "WCAG compliant" or bulk-promote
verification data on the strength of a stylesheet policy alone.

References:
- https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/popover
- https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Conditional_rules/Container_scroll-state_queries
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion
