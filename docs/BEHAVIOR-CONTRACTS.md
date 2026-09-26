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
- **ds-45 — Snapped Spotlight:** the corrected scroll-state selector matches the
  base selector's specificity so the snapped rule can win the cascade. The
  hosted/downloaded scroller has a focusable,
  named region. A snap position alone is not evidence of the authored spotlight;
  inspect the descendant article's rendered opacity and scale before/after a
  second target is snapped. Without scroll-state support, ordinary mandatory
  CSS scroll snapping remains and the cards keep their default dimmed style.
  This is a visual carousel sample, not a production carousel control system.
- **ds-46 — Real Overflow Hint:** the corrected scroll-state selector matches
  the base hint selector's specificity. A preview-only checkbox lets the same content
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

## Pilot 02 native-scroll boundaries

- **ds-111:** the KPI, not its thin track, supplies the entry timeline. Text is the accessible value; the decorative track is aria-hidden. Unsupported timelines and reduced motion retain the authored final width.
- **ds-93:** scroll-state enhancement alone hides unsnapped captions. Unsupported engines expose all captions; native horizontal scroll and the named keyboard region remain.
- **ds-134:** swipe reveals a real Open link. No deletion, undo, persistence or network operation is implemented or implied. Tab can reach the action without first swiping.
- **ds-30:** elevation is a persistent shadow, not an inferred stuck state. The demo destination is outside the sticky container. Short viewports use normal flow.
- **ds-55:** scale/dimming belongs to exit-crossing, not the moment a card first pins. Reduced motion removes the timeline animation. Short demo viewports use normal flow to preserve reading space.
- **ds-69:** the LTR demo uses `scrollable: left` to distinguish away-from-start from at-start, including reverse scrolling. This is not the most recent scroll direction. Adapt physical direction for RTL layouts before reuse.

See the Pilot 02 audit ledger for measured scope, engine results and limitations; no library-wide accessibility or support promotion follows from this pilot.

## Pilot 04 native-overlay boundaries

- **ds-79:** the mega panel is a real `[popover=auto]`; Escape, light-dismiss and focus return are native, and no static `aria-expanded` is authored. A closed panel is `display:none` outside `:popover-open` — an author `display` on `[popover]` overrides the UA hiding and leaves the closed panel hit-testable. Anchor insets resolve at compute time in Chromium, so an open panel does not travel with the document while a fragment link scrolls; do not read that persistence as broken anchoring, and do not claim `position-visibility: anchors-visible` hides it (it does not). Narrow (≤699px) and short (≤560px) viewports intentionally switch to a bottom sheet; that is the containment contract, not a failure.
- **ds-89:** zero-JS cannot implement the `role="menu"`/`role="menuitem"` interaction model (roving focus, type-ahead, arrow-key navigation), so those roles are removed and native popover semantics carry the tree. Menu items must be genuine: an in-page fragment, a reversible checkbox state and a second fragment. Edit/Duplicate/Delete copy is forbidden unless an observable action exists. Edge placement is `position-try-fallbacks`; the flip engages only when the anchored position would overflow, so tests must force the trigger near the viewport edge to observe it.
- **ds-142:** each pin is a `div.map-stop` wrapper carrying `anchor-name`, containing a `button.map-pin` that opens that stop's popover — the wrapper itself is not a link. The routes to the `#note-N` cards are plain fragment links: the in-popover "Studio notes" link and the numbered `.map-key` links, both keyboard-activatable, with the cards also present in flow below the map. The anchored note is presentation over content that already exists; without popover or anchor support the cards stay reachable through those links. Emoji or glyph pins are not acceptable scenery — they render as tofu on bare systems; the canonical pin is CSS-drawn and the atlas artwork is generator-only inline SVG.
- **All three:** canonical markup and CSS live in README.md/SKILL.md; generator files carry scene copy, layout and artwork only. Reduced motion removes open/close transitions while every open, close, dismiss and focus behaviour stays available. Documentation iframes are short (≈390px tall), so the short-viewport sheet policy is what keeps anchored panels contained there; evidence captures and specs branch on the real viewport, never on the requested test width alone. No claim is made about assistive technology, screen readers, WCAG conformance or engines other than the ones actually run.

See the Pilot 04 audit ledger for measured scope, engine results and limitations; no library-wide accessibility or support promotion follows from this pilot.
