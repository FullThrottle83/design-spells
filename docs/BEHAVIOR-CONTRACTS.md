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

## Pilot 05 modal/dialog boundaries

- **ds-66:** the programme card is a real non-modal `[popover=auto]`; no focus trap is claimed — the asserted proof is background operability (focusing the trigger and pressing Enter toggles the open card closed). Sequential Tab order past an open popover differs by engine — observed escaping in Chromium, staying inside in Firefox — so Tab escape is documented, not asserted. A bare `popovertarget` toggles, so specs must close the card before re-testing the keyboard path or Enter re-closes it. Backdrop treatment is `oklch(0 0 0/.45)` plus `blur(10px)` at opacity 1; focus stays on the invoker while open and returns to it on Escape.
- **ds-75:** thumbnail and enlarged view embed the same 1200×1500 data-URI (harbour-at-dusk original art); enlargement is 1.56× width / 2.44× area at 1440px and 1.44× / 2.08× at 390px with aspect 0.8 preserved. Enlargement factors are only asserted where the viewport has room — the 390px documentation portal height-caps the zoom below the width-sized thumbnail, so there the contract is same-source, aspect and containment. The caption is a translucent chip over the image; the Close pill meets the 44px touch target.
- **ds-77:** `closedby="any"` with `command="show-modal"`; below 640px a full-width bottom-anchored sheet with a grabber, at/above a 416px centred modal. Content fits without internal scrolling on tall viewports (`max-block-size: min(88dvh, 52rem)`); short viewports scroll internally instead — both are the containment contract. Chromium's modal Tab wrap passes through unfocused body, and in the documentation iframe the wrap-boundary Tab may continue into the outer document; the dialog stays open either way, so specs assert inside-or-body with background controls never focused, never a strict every-stop-inside trap. Radio/checkbox/select controls are natively operable and reversible; Done closes a `method="dialog"` form with `returnValue "done"`.
- **ds-106:** the dialog teaches closing, not deleting — "Delete customer / cannot be undone" copy is forbidden because zero-JS performs no deletion; the honest line is "nothing is sent or saved". Autofocus lands on the primary Close dialog control; Keep reading and Close dialog close via `method="dialog"` with returnValues `"stay"` and `"close"`; Escape and `closedby="any"` backdrop light-dismiss are the remaining paths, all returning focus to the invoker.
- **All four:** exit transitions keep `display` alive up to 300ms after close, so specs settle 550ms before asserting `display:none`. Engines without invoker commands (Safari, per the repo's support data) get an honest degraded state — the trigger advertises `command="show-modal"` and activation is a documented no-op — asserted by a behavioral probe, never by a support string. Documentation iframes admit form submission (`allow-same-origin allow-forms`) so `method="dialog"` controls work in embeds; without it Done/Close buttons are visibly dead there. `scrollIntoView()` cannot reveal fixed top-layer content by scrolling outer containers, so iframe-surface specs centre the wandered docs page first and every activation stays a real pointer event or real keypress. Reduced motion keeps every final state with `transition-duration: 0s`. No claim is made about assistive technology, screen readers, WCAG conformance or engines other than the ones actually run.

See the Pilot 05 audit ledger for measured scope, engine results and limitations; no library-wide accessibility or support promotion follows from this pilot.
