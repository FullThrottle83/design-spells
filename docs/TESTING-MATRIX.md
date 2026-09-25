# Browser and accessibility verification boundaries

The default suite runs the generated-data invariants and Chromium previews. The
separate `playwright.cross-browser.config.mjs` suite checks **Firefox** and
**WebKit** against the light catalogue, standalone docs, downloaded HTML and a
real two-document navigation, with JavaScript disabled and reduced motion on.

These smoke tests do not establish individual browser support for every modern
CSS feature. In particular, a page rendering does **not** imply an animation,
anchor, CSS function or invoker behavior works in that engine.

## Run

```sh
npm ci
npx playwright install --with-deps chromium firefox webkit
npm test
npx playwright test -c playwright.cross-browser.config.mjs
```

## Manual checks still required

- Keyboard-only operation in Firefox and Safari, including any popup/dialog,
  disclosure, tooltip and interaction-specific state; test Escape/focus return.
- VoiceOver on macOS/iOS and NVDA with a compatible browser: name, role, state,
  announcements, visible focus and DOM order of representative spell demos.
- Browser-specific CSS behavior under default and reduced motion; ensure
  unsupported progressive features have usable fallbacks.
- 200% text resize and 400% zoom/reflow; touch targets, hover/focus content,
  contrast across both color schemes and all states.
- For each individually reviewed spell, attach source URLs, browser versions,
  test date and observed result before promoting the `verification` fields.

No global WCAG 2.2 AA or cross-engine conformance claim is made by CI.
