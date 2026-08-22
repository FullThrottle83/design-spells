# Tests

Two layers, both run by `npm test`.

```bash
npm test              # both
npm run test:build    # data only, no browser, no install
npm run test:previews # live previews in Chromium
```

The browser layer is two spec files: `previews.spec.mjs` (the preview sandbox)
and `drawer.spec.mjs` (how the drawer renders description text).

## `test_build.py` — the generated data

Pure Python, stdlib only, sub-second. `python3 -m unittest discover -s tests`
works without installing anything.

- Rebuilds `public/spells.{js,json}` from `README.md` in a scratch copy of the
  repo and byte-compares against what is committed. Editing the catalogue
  without re-running `python3 scripts/build.py` fails here.
- Validates `public/spells.json` against `public/spells.schema.json`. The
  validator covers exactly the keywords that schema uses and **errors on any
  keyword it does not implement**, so extending the schema cannot silently
  turn validation off.
- Asserts the invariants every consumer keys off: unique ids, `id` derived
  from `number`, no blank fields the UI renders, `status`/`statusLabel` and
  `jsNeed`/`jsLabel` agreement, no category missing from `CAT_ORDER` in
  `app.js`, no `Baseline` claim contradicted by its own support matrix.
- Asserts the preview sandbox contract: no `:root`/`html`/`body` left
  un-rewritten (they cannot match inside a shadow root), no asset references
  that are not served, and preview markup that actually carries at least one
  of the classes the spell's CSS styles.

## `previews.spec.mjs` — the live previews

One Playwright case per spell — 145 of them, ~15s. Each selects its spell by
clicking the real catalogue row, so the whole path is covered: `spells.js` →
`hydratePreview` → shadow-root sandbox.

Per spell:

- the shadow root mounts and contains a `.stage`
- the stage and at least one descendant have a non-zero box
- **every visible top-level element has a non-zero box** — this is the check
  that catches the "renders, but 0px wide" class of bug, where the stage's
  centring grid leaves an empty or fully-absolute block with nothing to
  derive an inline size from
- no broken images
- the spell's CSS parses on its own into at least one rule
- at least one of the spell's own class selectors matches a live element
- no console errors or uncaught exceptions

Deliberately **not** asserted: colour, opacity, or anything pixel-based.
Previews animate, and several are legitimately mid-transition or hidden until
interaction, so the checks stay on geometry and structure to avoid flaking.

Two escape hatches exist because they are correct, not because they are
convenient:

- `display: none` top-level elements are skipped — closed `<dialog>`s,
  `popover`s, and `<datalist>` are supposed to be invisible.
- sizes are read with `offsetWidth`/`offsetHeight`, not the bounding box, so a
  scroll-driven `transform: scaleX(0)` (a progress bar at scroll top) reads as
  the correct state it is rather than a collapsed layout.

## `drawer.spec.mjs` — description rendering

67 of the 145 descriptions come out of the README carrying inline markdown, and
17 of those have literal HTML tags inside their backticks. `inlineMd()` in
`app.js` turns the markers into elements after escaping every source character,
so the same test covers both halves of that: the markers must become `<code>`
and `<strong>` with their text intact, and **no element may come from the source
text itself** — a description mentioning `<dialog>` that produced a `DIALOG`
node would mean the text was parsed as markup rather than escaped.

Runs under `reducedMotion: "reduce"`, which is the path `supportsViewTransition()`
in `app.js` already takes for that preference. Without it the drawer's
open/close View Transition leaves a snapshot overlay swallowing pointer events,
and 67 open/close cycles cannot outrun it.
