# Design Spells — Deep Site Audit & Improvement Plan

**Audited:** 2026-08-17 · **Commit:** `70fcf8c` · **Branch:** `arena/01a00fa0-design-spells`
**Scope:** `public/index.html`, `public/app.js` (997 lines), `public/styles.css` (859 lines), `public/spells.js` (generated, 292 KB), `scripts/build.py` (543 lines), `README.md` / `SKILL.md` (4,538 lines each), `wrangler.json`

**Method.** The site was served locally and driven programmatically through a real DOM: every category filter (16), every status filter (4), 15+ search queries, the drawer, all 3 code tabs, all 4 copy affordances, keyboard shortcuts, and the focus trap were exercised. All **145 spells were hydrated through the live preview pipeline** and their rendered shadow DOM inspected. The generated data bank was cross-analysed against spell source CSS to test the accuracy of the browser-support claims. Contrast ratios were computed from the actual token values. Everything below is an observed result, not a guess.

**Verdict.** This is a genuinely good, unusually opinionated product. There are **no crashes, no console errors, no broken filters, and no dead JS paths** — 145/145 previews hydrate without throwing, and the build is byte-for-byte reproducible. The problems are not stability problems. They are **trust problems** (the browser-support data — the site's core value claim — is wrong for at least 13 spells), **content problems** (19 descriptions have absorbed the next section's heading), and **reach problems** (no shareable URLs, no dark mode, and a third of the UI vanishes below 960 px).

---

## Table of contents

1. [Executive summary — top 12 by impact](#1-executive-summary--top-12-by-impact)
2. [Correctness bugs](#2-correctness-bugs-things-that-are-actually-wrong)
3. [Data integrity & the support matrix](#3-data-integrity--the-support-matrix-the-trust-problem)
4. [Content & copy quality](#4-content--copy-quality)
5. [Accessibility](#5-accessibility)
6. [UX & interaction design](#6-ux--interaction-design)
7. [Visual design & design system](#7-visual-design--design-system)
8. [Performance](#8-performance)
9. [The preview sandbox](#9-the-preview-sandbox-the-best-part-of-the-site)
10. [Search & findability](#10-search--findability)
11. [Code architecture](#11-code-architecture)
12. [The build pipeline](#12-the-build-pipeline-scriptsbuildpy)
13. [SEO, sharing & metadata](#13-seo-sharing--metadata)
14. [Repo hygiene, CI & deployment](#14-repo-hygiene-ci--deployment)
15. [Feature additions worth building](#15-feature-additions-worth-building)
16. [Strategic / product direction](#16-strategic--product-direction)
17. [Prioritised roadmap](#17-prioritised-roadmap)
18. [What is already excellent](#18-what-is-already-excellent-dont-regress-these)
19. [Appendix — verified test results](#appendix--verified-test-results)

---

## 1. Executive summary — top 12 by impact

| # | Issue | Severity | Effort | Where |
|---|---|---|---|---|
| 1 | Support matrix reports only **one** feature per spell — 11 spells hide a second, less-supported dependency and show all-green | 🔴 Critical | M | `build.py` |
| 2 | 19 descriptions have swallowed the next `## section heading` (`"… --- ## Reveal & motion"`) | 🔴 Critical | S | `build.py` |
| 3 | No URL state — cannot link to a spell, a filter, or a search. Kills sharing and SEO | 🔴 Critical | M | `app.js` |
| 4 | 4 "Baseline" spells are red in 2 browsers; 10 "Progressive" spells are all-green — the two systems contradict each other | 🔴 Critical | M | `build.py` |
| 5 | `rewrite_preview_css` corrupts class names: `.ticket-body` → `.ticket-:host` (2 previews silently unstyled) | 🟠 High | S | `build.py` |
| 6 | 9 spells render an **empty description line** in the list | 🟠 High | S | `build.py` |
| 7 | Muted text `#8c8778` = **3.27:1** — fails WCAG AA. Used for descriptions, counters, legends | 🟠 High | S | `styles.css` |
| 8 | Below 960 px the preview panel is `display:none`, so clicking a row does **nothing** — a dead target with `cursor:pointer` | 🟠 High | M | `styles.css` |
| 9 | Tailwind tab emits the same CSS wrapped in `@layer components` — zero added value, and 105 spells reference tokens Tailwind doesn't define | 🟠 High | M | `app.js` |
| 10 | Drawer doesn't `inert` the background; focus trap can't see shadow-DOM controls | 🟠 High | S | `app.js` |
| 11 | No dark mode, despite the catalogue teaching `light-dark()` and `color-scheme` | 🟡 Medium | M | `styles.css` |
| 12 | Full `innerHTML` rebuild of 145 rows + 580 SVG nodes on **every keystroke**, undebounced | 🟡 Medium | S | `app.js` |

---

## 2. Correctness bugs (things that are actually wrong)

### 2.1 🔴 Class-name corruption in preview CSS

`scripts/build.py` rewrites document-level selectors for the shadow DOM:

```python
css = re.sub(r":root\b", ":host", css)
css = re.sub(r"\bhtml\b", ":host", css)   # ← \b matches inside hyphenated class names
css = re.sub(r"\bbody\b", ":host", css)
```

`\b` treats `-` as a word boundary, so **any class containing `body` or `html` is destroyed**:

| Spell | Original | Becomes | Result |
|---|---|---|---|
| `ds-83` Perforated Ticket Card | `.ticket-body { padding: … }` | `.ticket-:host { … }` | rule never matches — preview renders unpadded |
| `ds-114` Themed Scrollbars | `.drawer-body { … }` | `.drawer-:host { … }` | rule dead |

**Also mangled** (cosmetic but wrong, and visible in the preview source):

- `ds-63`: `html[lang="en"] body` → `:host[lang="en"] :host` — a nonsense selector that can never match.
- `ds-74`: the comment `/* Prevents leaking to the body */` → `/* … to the :host */`.

**Fix.** Only rewrite selectors, never comments/strings, and anchor to real selector boundaries:

```python
css = re.sub(r"(?<![\w.#-]):root\b", ":host", css)
css = re.sub(r"(?<![\w.#-])\b(html|body)\b(?![\w-])", ":host", css)
```

Better still: strip comments before rewriting, and collapse `:host :host` → `:host` afterwards. Best of all: parse selectors rather than regex the whole stylesheet.

### 2.2 🟠 `oneLine()` produces empty rows

9 spells have no description at all, so the row renders `<p class="row__desc"></p>` — an empty element that still consumes layout:

`ds-6` Focus Glow · `ds-7` Icon Color Shift · `ds-10` Selection Skin · `ds-12` Scroll Snap gallery · `ds-22` Details Chevron Rotate · `ds-24` External Link Nudge · `ds-26` Pill Segmented Control Glow · `ds-35` Inline Theme Switch · `ds-bonus` Typographic Harmony

In the source Markdown these spells jump straight from the metadata line to the code fence. **Fix:** write one-line descriptions for all 9 in `README.md` (best), and have `rowTemplate` omit the `<p>` entirely when empty (defensive).

### 2.3 🟠 Category heading `id`s contain a space and an ampersand

`renderGrid()` emits `id="cat-Reveal & motion"`. It works today only because nothing links to it — but it blocks the obvious "jump to category" anchor feature and is invalid as a URL fragment. **Fix:** slugify (`cat-reveal-motion`).

### 2.4 🟡 The counter denominator ignores active filters

With *Forms + Progressive* selected the header reads **"Showing 5 of 145 spells"**. The `145` is `TOTAL_SPELLS`, never the filtered subtotal, so with two filters the sentence is misleading. **Fix:** `Showing 5 of 22 in Forms` — or `5 of 145` only when no filter is active.

### 2.5 🟡 `145` is hardcoded in five places in `index.html`

`<meta description>` ×3, the intro paragraph, and the initial counter all hardcode `145`. Add one spell and the site lies until someone hand-edits five strings. **Fix:** template them at build time from `len(payload)`.

### 2.6 🟡 Double-fire in `closeDrawer()`

Both `transitionend` and `setTimeout(finish, 380)` are registered. `finish()` is guarded by the `closing` flag so there is no visible bug, but the timer is never cleared and the `transitionend` listener leaks if the transition never fires. **Fix:** clear the timeout inside `finish()`.

### 2.7 🟡 Category nav re-render destroys focus

`renderCategoryNav()` replaces `catList.innerHTML` on every click. **Verified:** a keyboard user who activates *Forms* has focus reset to `<body>`, losing their place entirely. **Fix:** toggle `.is-on` classes in place (exactly as the status list already does correctly) instead of re-rendering.

---

## 3. Data integrity & the support matrix (the trust problem)

This is the site's headline promise — *"see which browsers support it"*. It is the area with the most defects.

### 3.1 🔴 One feature per spell, silently

`detect_feature()` returns on the **first** regex match, so a spell that uses three risky features is graded on whichever one the ordered list happens to hit. **11 spells verified affected:**

| Spell | Reported feature | Shown as | Also depends on | Truth |
|---|---|---|---|---|
| `ds-79` Anchor Mega Menu | Invoker Commands | 🟢🟢🟢🟢 | **Anchor Positioning** | FF partial |
| `ds-89` Anchor Context Menu | Invoker Commands | 🟢🟢🟢🟢 | **Anchor Positioning** | FF partial |
| `ds-117` Split Action Button | Invoker Commands | 🟢🟢🟢🟢 | **Anchor Positioning** | FF partial |
| `ds-127` Nested Cascade Popovers | Invoker Commands | 🟢🟢🟢🟢 | **Anchor Positioning** | FF partial |
| `ds-142` Map Pin Popover | Invoker Commands | 🟢🟢🟢🟢 | **Anchor Positioning** + `position-try-options` | FF partial |
| `ds-97`, `ds-106` | Invoker Commands | 🟢🟢🟢🟢 | **`closedby`** | FF ❌ |
| `ds-109` VT Cards | typed `attr()` | 🟢🟢❌❌ | **View Transitions** | FF ❌ |
| `ds-48`, `ds-121` | Anchor Positioning | — | `:has()` | ok |
| `ds-98` Interest Tooltip | Interest Invokers | 🟢🟢❌❌ | Anchor Positioning | ok-ish |

Five spells that require anchor positioning are advertised as **fully supported in Firefox**. A developer copies `ds-142`, ships it, and the popover lands in the wrong place in Firefox.

**Fix.** Collect *all* matching features and intersect their support, worst-case wins:

```python
def detect_features(css, html, title, status) -> list[str]:   # return every hit
def combine(features):                                        # min() per browser: no < partial < yes
```

Then render the drawer as a **feature list**, not a single line: *"Requires: Invoker Commands · Anchor Positioning"*, each with its own row. This is a strictly better UX as well as a correctness fix.

### 3.2 🔴 `Status` and `browsers` contradict each other

Two independent systems disagree, and both are shown side by side:

**10 "Progressive" spells show four green browsers** (`ds-8`, `ds-36`, `ds-55`, `ds-72`, `ds-91`, `ds-111`, `ds-126`, `ds-135`, `ds-139`, `ds-145`) — all scroll-driven animations. The support table says "safe everywhere"; the status chip says "wrap it in `@supports`".

**4 "Baseline" spells are red in two browsers:**

- `ds-33` True Auto-Height (`interpolate-size`) — Chromium-only ([still unsupported in Firefox and Safari](https://web-platform-dx.github.io/web-features-explorer/features/interpolate-size/)), yet labelled Baseline.
- `ds-94` Sticky Header + Zebra Table (`scroll-state`) — [Chrome/Edge 133+ only](https://www.testmuai.com/learning-hub/css-container-queries-browser-support/), labelled Baseline.
- `ds-32` `field-sizing`, `ds-146` `closedby` — no Firefox, labelled Baseline.

**Fix.** Derive `status` from the support data instead of trusting the hand-written Markdown: all-green → Baseline; one partial/`no` → Newer; two or more `no` → Progressive. Then flag any Markdown/derived mismatch as a **build error** so it can never drift again. If the author disagrees with the derivation, they change the data, not the label.

### 3.3 🟠 26 spells are graded on `oklch()` rather than what they demonstrate

The fallback probe matches any `oklch()`/`color-mix()` usage, so `ds-1 Shimmer`, `ds-3 Lift & Zoom`, `ds-82 3D Tilt`, `ds-92 Clipped Gradient Headline` etc. all report *"color-mix() / oklch()"*. That's technically true and practically useless — it tells you about the colour syntax, not about `mix-blend-mode` or `background-clip: text`. **Fix:** demote colour functions to a last-resort probe and add probes for the properties that actually carry risk (`mask-image`, `mix-blend-mode`, `background-clip:text`, `backdrop-filter`, `offset-path`, `@property`).

### 3.4 🟠 The support data is a hand-maintained snapshot with no provenance

`FEATURE_BROWSERS` is a Python dict of hardcoded verdicts with prose notes ("Chrome 135+, Safari 26.2+, Firefox 153+"). Nothing dates it, nothing verifies it, and it will silently rot. Anchor positioning in particular has moved fast — [Firefox shipped it in 147 (Jan 2026)](https://www.hurterdesignstudio.com/blog/anchor-positioning-arrives-across-browsers), and the [web-features group has debated whether it should count as Baseline at all](https://github.com/web-platform-dx/web-features/issues/3558) given the outstanding `position-try` bugs — exactly the nuance a static `"partial"` string can't express.

**Fix.** Depend on `web-features` / `caniuse-lite` at build time, key each spell to a BCD feature id, and generate the matrix. Then show real version numbers and a Baseline badge, and stamp the page with *"support data generated 2026-08-17"*. This turns the weakest part of the site into its strongest.

### 3.5 🟡 No "partial" nuance in the UI

The model supports `yes` / `partial` / `no`, but `partial` renders as 80 % opacity + slight grayscale — visually almost identical to `yes` at 16 px. The information is in the DOM (`title` attribute) but not perceivable. **Fix:** give partial a distinct mark (half-filled ring or a small dot badge), and never rely on opacity alone.

---

## 4. Content & copy quality

### 4.1 🔴 19 descriptions absorb the following section heading

The parser strips code fences but not the `---` / `## Heading` that ends a section, so the last spell in each section inherits it. Verified examples:

> **ds-90** — "…fans child actions into an arc via native CSS `cos()` / `sin()`. **--- ## Reveal & motion**"
> **ds-96** — "…screen-reader support for storage, quotas, and goals. **--- --- ## Navigation (2026)**"
> **ds-146** — "…the background moving while the modal scrolls. **---**"

Full list: `ds-41`, `ds-50`, `ds-52`(n/a), `ds-60`, `ds-63`, `ds-69`, `ds-74`, `ds-77`, `ds-78`, `ds-87`, `ds-90`, `ds-93`, `ds-96`, `ds-99`, `ds-101`, `ds-105`, `ds-107`, `ds-109`, `ds-111`, `ds-114`, `ds-126`, `ds-146`.

It's hidden in the list (`oneLine()` cuts at the first sentence) but **fully visible in the drawer**. **Fix:** stop the description scan at the first `---`, `## `, or `### ` line.

### 4.2 🟠 67 descriptions contain raw Markdown

Backticks and `**bold**` are printed literally via `textContent`: *"A microscopic scale-down on \`:active\` for tactile feedback."* and *"**Guardrails:** \`pointer-events: none\`…"*. `oneLine()` strips them for the list but the drawer shows them raw. **Fix:** render inline code and bold as real HTML (`<code>`, `<strong>`) in the drawer — a small parser or a build-time conversion. This also makes the API-name mentions scannable.

### 4.3 🟠 12 descriptions are wall-of-text (up to 466 chars)

`ds-60` (466), `ds-67` (374), `ds-74` (344), `ds-79`/`ds-107` (310) merge the intro, an a11y warning, and a cross-reference into one paragraph. **Fix:** split the model into `description` (one sentence, for the row) + `notes[]` (warnings, guardrails, cross-references) and render notes as a callout list. The `**A11y-critical:**` and `**WCAG warning:**` content in `ds-60`/`ds-74` deserves a red callout, not a run-on sentence.

### 4.4 🟡 Cross-references are plain text

Descriptions say "Combine with Spell 33" and "see Spell 17" but nothing links. **Fix:** auto-link `Spell (\d+)` → open that spell's drawer. Cheap, and it turns the catalogue into a graph.

### 4.5 🟡 The `note` field is parsed and then never displayed

`build.py` extracts a fourth metadata part into `note`, and `app.js` never reads it. Either surface it or drop it.

### 4.6 🟡 Two spells preview nothing but an apology

`ds-14` (Native Page Transitions) and `ds-143` (Print Stylesheet) render only a `demo-note` explaining that they can't be previewed. That's honest, but **`ds-143` could genuinely be demoed** by rendering the preview inside an iframe and calling `print()` — or at minimum by offering a "toggle print emulation" that applies the print rules to the stage. `ds-14` could show a before/after of the two page states.

---

## 5. Accessibility

### 5.1 🟠 Contrast failures (computed from the real tokens)

| Token | Usage | Ratio | Verdict |
|---|---|---|---|
| `--ink-2` `#8c8778` on `--bg` | row descriptions, counter, legend, category counts, hints | **3.27:1** | ❌ fails AA (4.5) |
| `--ink-2` on `--surface` | same, on hover | **3.59:1** | ❌ fails AA |
| `--warn` `#a3690a` | "Partial" status | **4.17:1** | ⚠️ borderline |
| `--accent` `#cf4520` on `--bg` | brand star, active border | **4.23:1** | ⚠️ borderline |
| `#fff6f2` on `--accent` | **primary "Copy CSS" button label** | **4.36:1** | ⚠️ fails AA for 12 px text |
| `--line` `#e2dcce` on `--bg` | all borders | **1.25:1** | ❌ fails 3:1 non-text |

`--ink-2` is the most-used secondary colour on the site and it fails. **Fix:** darken to ≈ `#6f6a5c` (≈ 4.8:1). Darken `--accent` to ≈ `#b83a17` for the button. Darken `--line` to at least `#d3cbb8` for borders that carry meaning (input outlines, focus targets).

Ironic given the catalogue ships a WCAG-quoting base layer and a `contrast-color()` spell.

### 5.2 🟠 Drawer doesn't neutralise the background

**Verified:** with the drawer open, `#main` and `.site-head` have neither `inert` nor `aria-hidden`. A screen-reader user can still arrow through all 145 rows behind a modal that claims `aria-modal="true"`. The JS Tab trap papers over keyboard nav but does nothing for virtual cursors.

**Fix:** set `inert` on `.site-head` and `#main` while open (one line, and it makes the hand-written Tab trap redundant). Better: make the drawer a real `<dialog>` with `showModal()` — free trap, free `::backdrop`, free Escape, free inertness. The catalogue *teaches* this pattern in `ds-146`; the site should eat its own cooking.

### 5.3 🟠 The focus trap can't see into the previews

The trap queries `drawer.querySelectorAll('button, a[href], [tabindex="0"]')`, which **cannot cross the shadow boundary**. Previews contain real buttons, inputs, `<details>` and `<select>`s. Tab order therefore enters the shadow tree and the wrap-around logic mis-fires. **Verified** trap list: `drawer-close, tab-tailwind, tab-modern, tab-html, copy-source, code-view, reset-preview, drawer-close-foot` — no preview controls. `inert`/`<dialog>` fixes this too.

### 5.4 🟠 Tabs are not a spec-compliant tablist

`role="tablist"` with three `role="tab"`s, but **no roving `tabindex`** (verified: all three are `null`). ARIA APG requires the selected tab to be `tabindex="0"` and the rest `-1`, so the tablist is one stop. Also missing: `Home`/`End` keys. Arrow keys work and correctly move selection with focus. **Fix:** add roving tabindex + Home/End.

### 5.5 🟡 Copy feedback is visual-only outside the drawer

The drawer's `#copy-status` is a proper `role="status"`. But the row **Copy**, **Copy all**, and the panel **Copy CSS** only swap their label to "Copied!" — no live region, so screen-reader users get nothing. **Fix:** route all four through one `announce()` live region.

### 5.6 🟡 Heading hierarchy skips and mislabels

`h1` → the three sidebar `h2`s ("Category", "Status", "Browsers") are styled as 10.5 px uppercase micro-labels but carry `h2` weight in the outline, competing with real content headings. Row titles are also `h2`, so the document has 145 `h2`s. **Fix:** sidebar group labels should be plain `<p>`/`<legend>` with the `role="group"` `aria-label` doing the work; rows are better as `h3` under the category `h2`.

### 5.7 🟡 Filters are buttons, not a filter control

Category/status filters are `<button>`s with a visual `.is-on` state and no `aria-pressed`. A screen reader announces "Forms 22, button" with no indication it's active. **Fix:** `aria-pressed="true|false"`, or model them as radio groups (they are mutually exclusive).

### 5.8 🟡 Browser support icons are decorative-only

Each icon is a `<span class="brow" title="Chrome: Supported">`. `title` is unreliable for AT and invisible on touch. The `.row__browsers` wrapper has `aria-label="Browser support"` but the *values* aren't exposed. **Fix:** add visually-hidden text (`<span class="sr-only">Chrome: supported</span>`) per icon.

### 5.9 🟡 `.row` is a click target that isn't a control

`<li class="row">` has `cursor:pointer` and a click handler but no role, no `tabindex`, no keyboard equivalent. Mouse users get "preview without opening"; keyboard users cannot. **Fix:** see §6.1 — resolve by redesigning the interaction, not by adding `tabindex` to an `li`.

### 5.10 🟢 Done well

Skip link, `:focus-visible` baseline, `aria-live` counter, `role="status"` copy feedback, focus restore to the triggering element on close, `prefers-reduced-motion` honoured both globally and in the demo shim, `aria-haspopup="dialog"` on row triggers, `dir`/`lang` set, 44 px targets in the preview tokens.

---

## 6. UX & interaction design

### 6.1 🟠 The row has two competing click behaviours — and one is invisible on mobile

Clicking the **title** opens the drawer. Clicking **anywhere else** in the row only swaps the quick-preview panel. Below 960 px that panel is `display:none`, so **the second behaviour is a no-op on every phone and small laptop** while the row still shows `cursor:pointer`. **Verified.**

**Fix — pick one model.** Recommended: the whole row opens the drawer; the preview panel follows the *keyboard-focused / hovered* row on desktop only. Or: make the panel the primary surface on desktop (row click = preview, explicit "Details" = drawer) and on mobile have row click open the drawer directly. Either way, `cursor:pointer` must only appear where a click does something.

### 6.2 🔴 No URL state (highest-leverage single fix)

**Verified:** zero uses of `history`, `location`, `URLSearchParams`, or storage. Consequences:

- You cannot link a colleague to `ds-142`.
- You cannot bookmark "Forms + Progressive".
- Refreshing loses everything.
- Google can only ever index one page — **145 pieces of content, one URL**.
- The back button doesn't close the drawer (a mobile reflex).

**Fix.** `?cat=forms&status=newer&q=anchor#ds-142`, `pushState` on drawer open, `popstate` closes it, hydrate state on load. Then add `<link rel="canonical">` per spell and prerender static `/spell/ds-142` pages at build time for real SEO.

### 6.3 🟠 The Tailwind tab doesn't earn its place

**Verified:** `tailwindFor()` takes the identical CSS, indents it, and wraps it in `@import "tailwindcss"; @layer components { … }`. No utilities, no `@apply`, no `@theme`, no `@custom-variant`. Worse — **105 of 145 spells reference custom properties that neither Tailwind nor the copied snippet defines**: `--color-primary`, `--space-4`, `--radius-md`, `--color-surface-offset`, `--header-height`, and 33 more. Paste it into a fresh Tailwind v4 project and it renders unstyled.

**Fix, in ascending value:**
1. Prepend the required `@theme` block with the tokens that snippet actually uses (computable per spell).
2. Emit real Tailwind v4: map tokens to `@theme` names, express variants as `@custom-variant`.
3. Add a **"Copy with tokens"** toggle on every tab so any snippet is self-contained. This is the single most useful change to the copy experience.

### 6.4 🟠 The site never states which tokens a spell needs

Related to the above but broader: a spell's CSS is only half the contract. **Fix:** add a "Tokens used" section in the drawer listing the custom properties, with a copy-ready `:root` block containing sensible defaults (the preview sandbox already has exactly these values in `PREVIEW_TOKENS` — reuse them).

### 6.5 🟡 No multi-select filtering, no JS-need filter

Category and status are both single-select; you can't see "Forms + Overlays", and you can't filter by `0 JS` vs `Markup` at all — even though that distinction is central to the doc's thesis and is already in the data (`jsNeed`). **Fix:** multi-select chips + a JS-need filter + a "Baseline only" quick toggle.

### 6.6 🟡 No sort control

Order is fixed (category, then source order). No way to sort by number, title, or support breadth. **Fix:** a small sort select — "Catalogue order / Best supported / Newest".

### 6.7 🟡 Nothing is saveable

No favourites, no "copied history", no stack builder. Given the README's "Ready-made stacks" concept, a **stack builder** is the obvious missing feature — see §15.1.

### 6.8 🟡 Small polish items

- **No clear (×) button** in the search field; `/` focuses but `Escape` doesn't clear.
- **`/` hint `<kbd>` is shown on touch devices** where there is no keyboard.
- **No result count per filter combination** before you apply it.
- **"Copy all" copies the filtered subset** of a category — correct, but the label doesn't say so; if a search is active you get fewer rules than "all" implies.
- **The empty state is a dead end** — "No spells match 'zzzzz'" with no "clear search" button and no suggestions.
- **The drawer has no prev/next navigation** — you must close and re-aim to compare two spells.
- **`Reset preview` is ambiguous** — its actual job (re-instantiate the shadow DOM to replay animations) would read better as "Replay".
- **Sponsor link is the only header action** and sits next to the counter, reading like part of the data.

---

## 7. Visual design & design system

The Swiss/editorial direction is confident and well-executed — sharp 2 px radii, one accent, system fonts, real typographic hierarchy. It looks like a design tool made by someone with taste. Refinements:

### 7.1 🟡 No dark mode

`color-scheme: light` is hardcoded in both CSS and a `<meta>`. For a developer-facing reference — where the code panel is *already* dark, creating a permanent light/dark clash on the page — this is the most-missed feature. It's also thematically damning: the catalogue contains `light-dark()` (`ds-35`), `color-scheme` toggles (`ds-116`), and themed scrollbars (`ds-114`), none of which the site itself uses. **Fix:** implement dark mode *using the spells*, and say so on the page.

### 7.2 🟡 The preview sandbox is always light

`PREVIEW_TOKENS` hardcodes a light palette, so dark-mode spells can't be shown in their intended context. **Fix:** a light/dark toggle **on the preview stage** — hugely valuable for judging shadows, blend modes, scrims (`ds-74`), and glass effects.

### 7.3 🟡 Row density is uniform and information-poor

Every row is title + one-line desc + 4 icons + Copy. The status (Baseline/Newer/Progressive) — arguably the most important filter dimension — **is not shown in the row at all**, only in the drawer. The `ds-NNN` id is hidden below 640 px. **Fix:** add a compact status dot to each row; consider a density toggle (comfortable/compact) and an optional grid/gallery view with live thumbnails.

### 7.4 🟡 Category colour-coding is absent

15 categories, all rendered identically. A subtle per-category hue (or just a left rule) would make the long scroll navigable.

### 7.5 🟡 The `.brow` opacity system loses meaning at 16 px

See §3.5 — grayscale-40 %/opacity-80 % for "partial" is not distinguishable from "yes" at that size, especially for colour-blind users.

### 7.6 🟡 Sticky sidebar can overflow on short viewports

`.browse__nav` is `max-height: calc(100vh - header - 40px)` with `overflow-y:auto`. With 16 categories + 4 statuses + legend at 800 px height it scrolls internally — a nested scroll region inside a page scroll, which is awkward with a trackpad. **Fix:** collapse the legend into a popover, or let the nav scroll with the page below a height threshold.

### 7.7 🟢 Nice touches worth keeping

The `code__view` dark island, tabular-nums on counters, `text-wrap: balance`/`pretty`, the `--ease` curve, the accent used *only* for the primary action and active state, borders instead of shadows.

---

## 8. Performance

Actual measured payload:

| File | Raw | Gzip |
|---|---|---|
| `index.html` | 8.4 KB | 2.4 KB |
| `styles.css` | 20 KB | 5.0 KB |
| `app.js` | 85 KB | 24.8 KB |
| **`spells.js`** | **292 KB** | **41.8 KB** |
| **Total** | **403 KB** | **~74 KB** |

### 8.1 🟠 `spells.js` is render-blocking and 292 KB

It's a **classic (non-`defer`) `<script>` in `<head>`**, so parsing blocks first paint. `app.js` is deferred and depends on it, so nothing renders until 292 KB is downloaded and evaluated. **Fix:** add `defer` to both (order is preserved among deferred scripts), or convert to JSON + `fetch`, or inline the first-screen data and lazy-load the rest.

### 8.2 🟠 ~69 KB of the payload is duplicated verbatim

**Verified:** `css === previewCss` for **132 of 145** spells, and `html === previewHtml` for 64. Every spell stores both. **Fix:** emit `previewCss` only when it differs (`previewCss: null` → fall back to `css` at runtime, which `hydratePreview` already does). Saves ~69 KB raw / ~10 KB gzip for zero behaviour change.

Also shipped and unused by the UI: `section`, `rawCategory`, `note`, `jsNeed` (partly), `number` (derivable from `id`).

### 8.3 🟡 Undebounced full re-render on every keystroke

`search` → `input` → `renderGrid()` → `catalogue.innerHTML = …` rebuilding up to **145 rows containing 580 `<use>` nodes**. Measured 233 ms for 5 keystrokes in jsdom; a real browser is far faster, but it still discards and rebuilds the entire DOM per character, throws away scroll position, and forces layout. **Fix:** 120 ms debounce + keyed DOM reconciliation (or just toggle `hidden` on existing rows — the row set is fixed at 145, so build once and filter by visibility).

### 8.4 🟡 The 87 KB icon sprite lives inside `app.js`

Four full-colour browser logos with gradient defs are embedded as a template literal, roughly **doubling** the JS bundle. They are also injected into `<body>` on every load regardless of need. **Fix:** move to an external `icons.svg` sprite (cacheable, parsed by the SVG parser rather than the JS parser) or inline it in the HTML.

### 8.5 🟡 No caching or compression story

No `_headers` file, no `Cache-Control`, no immutable hashed filenames. Cloudflare Workers Assets will do sensible defaults, but `spells.js` should be content-hashed and cached for a year. **Fix:** add `public/_headers`.

### 8.6 🟡 No `content-visibility` on the long list

The catalogue teaches `content-visibility: auto` (`ds-41`) and doesn't use it on its own 145-row list. Free win, and a nice bit of dogfooding.

### 8.7 🟡 145 shadow roots are created lazily but never disposed

Each drawer open attaches a shadow root and leaves the previous host's content in place until reopened. `clearDemoTimer` is handled correctly, but the quick-preview host's animations keep running while off-screen. **Fix:** pause demo timers when the panel isn't visible (`IntersectionObserver` or `document.visibilityState`).

---

## 9. The preview sandbox (the best part of the site)

The shadow-DOM sandbox with token injection, the `:hover`/`:focus`/`:active` demo shim, the `:target` shim, the scroll runway for timeline animations, and the spotlight ring are genuinely clever — better than most commercial component galleries. Improvements:

### 9.1 🟠 No way to see the preview at a different size

Container queries (`ds`-container spells), responsive sheets (`ds-77`), and mobile-vs-desktop behaviour can't be judged in a fixed 220/280 px box. **Fix:** width presets (320 / 768 / full) + a drag handle on the stage. High value for a layout catalogue.

### 9.2 🟠 Previews aren't editable

The single highest-value addition for a code catalogue: make the source panel a `contenteditable`/textarea that **re-hydrates the preview live**. All the machinery already exists (`hydratePreview` takes a spell object; `Reset preview` already re-instantiates). A tiny live playground would make this site a destination rather than a reference.

### 9.3 🟡 8 previews render essentially nothing

**Verified** ≤2 elements and no text: `ds-11` Skeleton Shimmer, `ds-23` Validation Whisper, `ds-32` Elastic Textarea, `ds-52` Organic Divider, `ds-59` Auto Empty State, `ds-64` Path Motion, `ds-105` Typed attr Meter, `ds-109` VT Cards (renders a literal `…`).

Several are *correct* but unconvincing (an empty skeleton box is the point). Others are weak: `ds-23` shows a bare email input with no way to discover the invalid state; `ds-59` renders an empty `<div class="data-grid">` so the "auto empty state" has nothing to contrast with; `ds-109` shows the ellipsis character. **Fix:** hand-author `PREVIEW_HTML` entries for these 8, and for `ds-23` pre-fill an invalid value so `:user-invalid` fires.

### 9.4 🟡 The demo shim can misrepresent a spell

`shimDemoCss` rewrites `:hover` → `:is(:hover, [data-ds-demo~="hover"])` and applies the attribute to **every element in the stage** (`.stage *`). For a spell with nested hover targets this fires all of them simultaneously, which is not what the CSS does in reality. **Fix:** apply the demo attribute only to the element the ring targets.

### 9.5 🟡 `@media print` and page-level spells can't work in a shadow root

`ds-143`'s rules target `.site-header`, `body`, `@page` — meaningless inside a stage div. See §4.6 for the iframe fix, which would also let `ds-14`, `ds-36` (scroll progress on `html`) and `ds-114` (scrollbar theming on `html`) preview correctly. **An iframe-based stage is the structurally correct answer** for the ~12 spells whose CSS targets `html`/`body`/`:root`, and it removes the need for the fragile `:host` rewrite entirely (§2.1).

### 9.6 🟡 No way to view the preview full-screen or open it standalone

**Fix:** "Open preview in new tab" (a generated standalone HTML page) — also gives people something to link to and makes DevTools inspection possible.

### 9.7 🟡 The hint pill is guessy

`detectTrigger()` returns a single string from a regex ladder; for spells with several interactions it names only the first. Minor, but a spell like `ds-67` (before/after slider) gets "Scroll to preview" when the real interaction is dragging.

---

## 10. Search & findability

### 10.1 🟠 The CSS body is not searchable

**Verified:** searching `backdrop-filter` — a property used by several spells — returns **0 results**. The haystack is `id, number, title, category, status, statusLabel, jsLabel, feature, description`. The one thing developers actually search for (a property or selector name) is excluded. **Fix:** include `css` and `html` in the index. Weight matches: title > feature > description > source.

### 10.2 🟠 `ds-1` matches 58 rows

Because matching is naive substring on a joined string, `ds-1` hits `ds-1`, `ds-10`…`ds-19`, `ds-100`… **Fix:** exact-match id/number when the query looks like an id, and rank exact matches first.

### 10.3 🟡 No fuzzy matching or synonyms

`SAFARI` returns 0 (case handled, but "Safari" only appears in support notes, which aren't indexed). "modal" won't find "dialog"; "dropdown" won't find "popover"; "tooltip" won't find `ds-98`. **Fix:** add a `keywords[]` field per spell, seeded with synonyms and the API names, plus a small fuzzy pass (Levenshtein ≤1 on tokens).

### 10.4 🟡 No highlighting of matches

Results don't show *why* they matched. **Fix:** `<mark>` the matched substring in title/description.

### 10.5 🟡 No empty-state recovery or suggestions

See §6.8. Add "Did you mean…", popular searches, and a clear button.

---

## 11. Code architecture

`app.js` is 997 lines of clear, well-commented, dependency-free DOM code. The comments explaining *why* (the hover-preview regression, the gradient-id collision, the `:target` shadow limitation) are genuinely excellent and rare. It is not badly written — it's just at the size where structure starts paying off.

### 11.1 🟡 One flat module, ~30 module-level `const` DOM handles

**Fix:** split into ES modules (`data.js`, `filters.js`, `render.js`, `preview.js`, `drawer.js`, `highlight.js`, `clipboard.js`). Native ESM, no build step required — consistent with the project's zero-tooling ethos.

### 11.2 🟡 No tests at all

For a project whose output is *generated data*, the absence of tests is the biggest structural risk — every bug in §2–§4 would have been caught by a cheap assertion. **Fix:** a `tests/` folder with (a) Python tests for `build.py` parsing, (b) a data-invariant suite (every spell has a non-empty description; no description contains `##`; no selector contains `:host` mid-token; status agrees with the support matrix), (c) a smoke test that hydrates all 145 previews and asserts no throw + non-trivial output. The audit harness used here is ~40 lines and found six real bugs.

### 11.3 🟡 Hand-rolled syntax highlighter

`highlightCss`/`highlightHtml` are ~150 lines. They work well, but `highlightHtml`'s regex can't handle `>` inside attribute values, and the CSS tokeniser's `tok-fn` class is defined in CSS but **never emitted** by the highlighter (dead style). **Fix:** either finish it (emit `tok-fn`, handle edge cases) or move highlighting to build time and ship pre-highlighted HTML — faster at runtime and removes 150 lines from the bundle.

### 11.4 🟡 XSS surface is currently safe but fragile

`esc()` is applied consistently, and spell content is trusted (it comes from the repo's own Markdown). But `hydratePreview` injects `spell.previewHtml` **raw** into a shadow root, so a malicious PR to `README.md` could inject script into the site. **Fix:** since this is a contribution-friendly open-source catalogue, either sanitise preview HTML at build time (allowlist tags/attrs, strip `on*` and `<script>`) or sandbox previews in an iframe with `sandbox="allow-same-origin"` (§9.5 makes this desirable anyway). Worth a build-time assertion at minimum.

### 11.5 🟡 Magic values duplicated across layers

`--header-h: 57px` in CSS vs `--header-height: 3rem` in `PREVIEW_TOKENS`; the 380 ms close timer vs the `.26s` CSS transition; `min-height` 180/280 in JS vs `.preview-host--panel/--lg` in CSS. These drift. **Fix:** derive from CSS custom properties where possible.

### 11.6 🟡 `previewPanel`, `TOTAL_SPELLS`-vs-filtered, and `state.tab` reset behaviour

`previewPanel` is queried and never used. `setTab("modern")` is forced on every drawer open, discarding the user's tab preference — if I'm working in Tailwind, I have to re-select it 145 times. **Fix:** persist `state.tab` across opens (and in the URL).

---

## 12. The build pipeline (`scripts/build.py`)

Reproducible ✅ (verified byte-identical re-run). Otherwise it's a 543-line regex pipeline doing a parser's job.

### 12.1 🟠 Regex Markdown parsing is the root cause of §2.1, §4.1, §4.2, §4.3

**Fix:** parse with `markdown-it-py`/`mistune` into an AST and walk it. Sections, headings, fences, and inline code all become structural facts instead of regex accidents. This single change eliminates four bug classes.

### 12.2 🟠 `PREVIEW_HTML` is a 100+ entry dict of hand-written demo markup living in the build script

Preview markup is *content*, not build logic, and it's invisible to anyone editing `README.md`. **Fix:** move it into the Markdown as a fenced ```` ```html preview ```` block per spell, or into a sibling `previews/ds-142.html` file. Contributors can then add a spell without touching Python.

### 12.3 🟠 No validation, no failure modes

The script prints counts and exits 0 regardless. It doesn't check that every spell has a description, that categories are known (unknown categories silently pass through `CATEGORY_UI.get(category, category)` and would create a new nav entry), that feature keys exist, or that previews are non-empty. **Fix:** a `--check` mode that fails CI on any invariant breach.

### 12.4 🟡 `README.md` and `SKILL.md` are byte-identical 4,538-line duplicates

**Verified identical.** Two copies of a 150 KB document will diverge. The build reads only `README.md`. **Fix:** keep one canonical file (`SKILL.md`, given the frontmatter is skill metadata) and make the other a short pointer — or generate `SKILL.md` from the source. Also: a 4,538-line README is a poor front door for the *repo*; a short README describing the site, the build, and how to contribute, with the catalogue in `SKILL.md`, serves both audiences.

### 12.5 🟡 The generated artifact is committed

`public/spells.js` (292 KB) is in Git, so every content change produces a large diff and the file can drift from its source. Acceptable for a zero-CI static deploy, but **fix:** either generate in CI before deploy and gitignore it, or add a CI check that regenerating produces no diff (cheap, catches stale artifacts).

### 12.6 🟡 No `python -m venv`/requirements, no `package.json`, no documented commands

Nothing tells a contributor to run `python3 scripts/build.py`. **Fix:** a `package.json` with `"build"`, `"dev"`, `"check"` scripts (even for a Python build), or a `Makefile`, plus a `CONTRIBUTING.md`.

---

## 13. SEO, sharing & metadata

### 13.1 🔴 145 pieces of content, one indexable URL

Combined with §6.2, this is the biggest growth limiter. Nobody will ever land on "CSS scroll-driven image wipe" from a search engine. **Fix:** build-time prerendered pages per spell (`/spell/ds-139/`) with real `<h1>`, description, code, and a canonical link, all hydrating into the same SPA. `build.py` already has every field needed — this is maybe 40 lines of templating and it could 10× organic traffic.

### 13.2 🟠 No `og:image`

**Verified absent.** Every share on Slack/X/LinkedIn is a grey box. **Fix:** generate a per-spell OG image at build time (title + category + support marks on the paper background). Even one static site-wide image is a large improvement.

### 13.3 🟠 Missing standard files

No `robots.txt`, no `sitemap.xml`, no `<link rel="canonical">`, no `humans.txt`. **Fix:** all four, generated.

### 13.4 🟡 `og:url` is hardcoded to `design-spells.hultsan20.workers.dev`

A deploy to any other host advertises the wrong canonical URL. **Fix:** template from an env var / `wrangler.json`.

### 13.5 🟡 No structured data

**Fix:** JSON-LD (`SoftwareSourceCode` or `TechArticle` per spell, `ItemList` for the catalogue) — realistic shot at rich results for a code catalogue.

### 13.6 🟡 No favicon beyond an inline SVG glyph

The data-URI `✶` is charming but there's no `apple-touch-icon`, no `manifest.webmanifest`, no maskable icon. **Fix:** add a small icon set + web manifest (also enables installability, which suits a reference tool).

---

## 14. Repo hygiene, CI & deployment

**Verified missing:** `.gitignore`, `LICENSE`, `.github/` (no CI), `package.json`, `CONTRIBUTING.md`, `CHANGELOG.md`, `_headers`.

### 14.1 🟠 No LICENSE

The footer says *"Open source · contributions via pull request"* and the README invites copying CSS, but **there is no license file**, so by default nobody has the legal right to reuse any of it. For a snippet library this is a direct contradiction of the product's purpose. **Fix:** MIT or CC0 for the code snippets; state it in the footer.

### 14.2 🟠 No CI

Nothing verifies the build, the data invariants, or link integrity on a PR. **Fix:** a GitHub Action running `build.py --check`, the data-invariant tests, and a diff check that the committed `spells.js` is current.

### 14.3 🟡 No `.gitignore`

`__pycache__/`, `.venv/`, `node_modules/`, `.DS_Store` will eventually get committed.

### 14.4 🟡 No contribution guide

The site says "contributions via pull request" but nothing explains the Markdown spell format, the metadata line grammar, the preview conventions, or that you must re-run the build. **Fix:** `CONTRIBUTING.md` + a spell template. This is what turns a personal project into a community one.

### 14.5 🟡 Deployment is manual and undocumented

`wrangler.json` has no build hook, so `spells.js` must be built by hand before every deploy — a stale-data footgun. **Fix:** a deploy workflow that builds, checks, then `wrangler deploy`.

### 14.6 🟡 No security headers

**Fix:** `public/_headers` with `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`. Note a strict CSP requires removing the inline `style` attribute on the sprite (§8.4) — another reason to externalise it.

### 14.7 🟡 No analytics or feedback channel

No privacy-friendly analytics, so there's no signal on which spells matter, what people search for, or what returns zero results — the exact data needed to prioritise everything in §15. **Fix:** a cookieless counter (Plausible/Cloudflare Web Analytics) tracking spell opens, copies, and zero-result queries. Plus a "report an issue with this spell" link in the drawer.

---

## 15. Feature additions worth building

Ordered by value-to-effort.

### 15.1 ⭐ Stack builder ("cart" for spells)
The README already defines *Ready-made stacks* (`Astro baseline`, `Astro marketing`, …) and *Astro mapping* per component — and **none of it is in the UI**. This is the site's best unbuilt feature and the content already exists.
Let users select spells → see them listed in a tray → **copy one combined, deduplicated stylesheet with a single `:root` token block** → share via URL (`?stack=1,2,5,19`) → export as `base.css`. Ship the six predefined stacks as one-click presets. This turns a browsable reference into a tool people return to.

### 15.2 ⭐ Prerendered per-spell pages + URL state
§6.2 + §13.1. Unlocks sharing, SEO, and the back button in one change.

### 15.3 ⭐ Dark mode, implemented with the catalogue's own spells
§7.1. Also add the preview-stage light/dark toggle (§7.2), which is a genuine reviewing tool, not a gimmick.

### 15.4 ⭐ Live-editable previews
§9.2. Highest "wow" per line of code, since `hydratePreview` already does the hard part.

### 15.5 Accurate, generated support matrix with versions
§3.4. Show "Chrome 125 · Firefox 147 · Safari 26" and a Baseline badge, sourced from `web-features`, with a generation date. Add a "works in my browser?" client-side `CSS.supports()` check — a one-line, zero-JS-philosophy-compatible feature that tells the visitor the truth about *their* browser.

### 15.6 Responsive preview sizing
§9.1. Essential for a catalogue this layout-heavy.

### 15.7 Compare mode
Select 2–3 spells and view previews + support side by side. Directly serves the README's "pick at most 1–2 dominant spells per section" guidance.

### 15.8 Framework export tabs that mean something
Replace the hollow Tailwind tab with real outputs: **Astro component** (the doc is Astro-first and even maps spells to `MainLayout.astro`, `Header.astro` — generate the component), **Tailwind v4 with `@theme`**, **CSS Module**, **styled-components**, **vanilla + tokens**. The Astro one writes itself from data already in the README.

### 15.9 Keyboard-first navigation
`j`/`k` between rows, `Enter` to open, `c` to copy, `?` for a shortcut sheet, `Cmd+K` command palette. The audience is developers; `/` alone is a tease.

### 15.10 "Random spell" / "Spell of the day"
Cheap discovery mechanic for a 145-item catalogue, and a reason to return.

### 15.11 Per-spell metadata the doc already implies
Show `jsNeed` (0 JS vs Markup) as a row badge and a filter; show "used in stacks: Marketing, Commerce"; show "related spells" from the cross-references in §4.4.

### 15.12 Copy-format options
Copy as minified, as SCSS, with/without comments, with/without the `@supports` wrapper, with a `prefers-reduced-motion` guard auto-added.

### 15.13 Offline / PWA
A service worker over 403 KB of static assets makes the whole catalogue available offline — very fitting for a reference tool, and a nice proof point for the "no runtime dependencies" ethos.

### 15.14 An RSS/JSON feed of new spells
For a catalogue that gained 50 spells in 2026, a feed gives returning users a reason to subscribe.

---

## 16. Strategic / product direction

**What this site is:** a beautifully made, opinionated, single-author reference with unusually good previews.

**What holds it back:** it behaves like a *document* (one URL, no state, no sharing, no identity per spell) while containing a *database* (145 structured records with support data, categories, and relationships).

Three moves, in order:

1. **Make every spell a first-class, addressable thing.** URL state → prerendered pages → OG images → sitemap. Everything about reach depends on this.
2. **Make the support data trustworthy and generated.** It's the differentiating claim; right now it's the least reliable part. Generated data + versions + a "does *my* browser support this" check turns the weakness into the moat.
3. **Make it a tool, not just a list.** The stack builder (§15.1) and live editing (§9.2) are what people bookmark. The README already contains the intellectual work for stacks — it just isn't wired to the UI.

One more thought on positioning: the site's premise is *zero client JS*, yet the site itself ships 377 KB of JS to browse a static catalogue. That's a fair trade for the previews — but it's an open goal for a critic, and a build-time-rendered list with progressive enhancement (server-rendered rows, JS only for previews and filtering) would let the site *demonstrate* its own thesis. Worth considering as a v2 architecture.

---

## 17. Prioritised roadmap

### Phase 1 — Correctness & trust (1–2 days)
1. Fix `\bhtml|body\b` selector corruption (§2.1)
2. Stop descriptions absorbing section headings (§4.1)
3. Write the 9 missing descriptions (§2.2)
4. Multi-feature support detection; worst-case intersection (§3.1)
5. Reconcile `status` with the support matrix; fail the build on mismatch (§3.2)
6. Darken `--ink-2`, `--accent`, `--line` to pass WCAG AA (§5.1)
7. `inert` on background when the drawer is open (§5.2)
8. Add LICENSE + `.gitignore` (§14.1, §14.3)

### Phase 2 — Reach (3–5 days)
9. URL state for spell/filters/search + back-button support (§6.2)
10. Prerendered per-spell pages, canonical, sitemap, robots (§13.1, §13.3)
11. Generated OG images (§13.2)
12. Make CSS source searchable; fix `ds-1` over-matching (§10.1, §10.2)
13. `defer` scripts; drop duplicated `previewCss`/`previewHtml` (§8.1, §8.2)
14. Fix the mobile dead-click / preview-panel gap (§6.1)

### Phase 3 — Tool-ification (1–2 weeks)
15. Stack builder with shareable URLs and the six preset stacks (§15.1)
16. Dark mode, site + preview stage (§7.1, §7.2)
17. Live-editable previews (§9.2)
18. Responsive preview sizing (§9.1)
19. Real framework exports incl. Astro components; tokens included in every copy (§6.3, §15.8)
20. `web-features`-generated support data + `CSS.supports()` self-check (§15.5)

### Phase 4 — Durability (ongoing)
21. Markdown AST parser replacing the regex pipeline (§12.1)
22. Test suite: parser, data invariants, preview smoke test (§11.2)
23. CI on PRs; deploy workflow that builds before shipping (§14.2, §14.5)
24. `CONTRIBUTING.md`, spell template, previews moved out of `build.py` (§12.2, §14.4)
25. De-duplicate `README.md`/`SKILL.md` (§12.4)
26. Split `app.js` into ES modules (§11.1)
27. Analytics on searches with zero results, to drive the next round (§14.7)

---

## 18. What is already excellent (don't regress these)

- **Zero runtime dependencies, zero webfonts, zero external requests.** Rare and admirable.
- **The shadow-DOM preview sandbox** with token injection and CSS isolation — better than most paid component galleries.
- **The auto-demo shim.** Mirroring `:hover`/`:focus`/`:active` onto a data attribute and acting out the interaction on a loop, with a spotlight ring, respecting `prefers-reduced-motion` — genuinely inventive.
- **The `:target` shim** for shadow roots, and the **scroll runway** for timeline animations. Both show real understanding of why naive previews fail.
- **The code comments explain *why*, including past regressions.** Unusually high quality.
- **The visual design.** Coherent, restrained, confident; the Swiss/editorial system is actually held to.
- **Reproducible build**, verified byte-identical.
- **No console errors, no exceptions across all 145 previews**, correct filter logic, working focus restore, honest "can't preview this" states.
- **`prefers-reduced-motion` respected in three separate places.**
- **The catalogue content itself** — 145 curated, categorised, genuinely modern techniques with Astro mappings and ready-made stacks. The hard intellectual work is done; most of this document is about surfacing it.

---

## Appendix — verified test results

**Environment:** static server on `:8080`, DOM-driven harness executing the real `app.js` + `spells.js`.

| Test | Result |
|---|---|
| Page boot, console/JS errors | ✅ 0 errors |
| Spells loaded / declared total | 145 / 145 ✅ |
| Spell numbering | 1–146, only 4 & 42 absent (documented) ✅ |
| Duplicate ids / titles | none ✅ |
| Category filters (16) | all correct ✅ |
| Status filters (4) | 86 baseline / 38 newer / 21 progressive ✅ |
| Combined filters | ✅ (counter denominator misleading, §2.4) |
| Search (15 queries) | works; source not indexed ⚠️ (§10.1) |
| Drawer open/close, Esc, backdrop, ×, footer | ✅ all paths |
| Focus restore to trigger | ✅ |
| Focus trap | ✅ within light DOM; misses shadow DOM ⚠️ (§5.3) |
| Background inert when modal open | ❌ (§5.2) |
| Tabs: click, `aria-selected`, arrows | ✅ (no roving tabindex ⚠️ §5.4) |
| Copy: row / copy-all / panel / source | ✅ all 4 write correct text |
| Copy-all payload | 16 spells, 9,198 chars ✅ |
| `/` shortcut | ✅ (correctly ignored when drawer open) |
| **All 145 previews hydrated** | ✅ 0 throws, 0 missing shadow roots |
| Near-empty previews | 8 (§9.3) |
| Corrupted selectors after `:host` rewrite | 2 (§2.1) |
| Descriptions containing section headings | 19 (§4.1) |
| Empty descriptions | 9 (§2.2) |
| Descriptions with raw Markdown | 67 (§4.2) |
| Multi-feature spells graded on one feature | 11 (§3.1) |
| Progressive-but-all-green / Baseline-but-red | 10 / 4 (§3.2) |
| `css === previewCss` duplication | 132 of 145 (~69 KB) (§8.2) |
| Spells using undefined custom properties | 105 of 145 (§6.3) |
| Build reproducibility | ✅ byte-identical |
| Contrast audit | 3 failures, 3 borderline (§5.1) |
| URL/state/storage APIs used | none (§6.2) |
| `og:image` / `robots.txt` / `sitemap.xml` / LICENSE / CI / `.gitignore` | all absent |
