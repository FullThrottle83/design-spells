# AUDIT Findings Status Report (Drift Check)

**Audit Source:** `AUDIT.md` (dated 2026-08-17)
**Status Date:** 2026-09-20
**Target Branch:** `main`
**Verification Method:** Inspected codebase sources (`scripts/build.py`, `public/styles.css`, `public/search.js`, `public/index.html`, `public/spells.json`, `README.md`), ran `python3 scripts/build.py`, `npm run test:build` (unittest), and `npm run test:previews` (playwright).

---

## Summary of Findings Status

| Section | Total Findings | FIXED | STILL PRESENT | PARTIALLY | CANNOT VERIFY |
|---|---|---|---|---|---|
| **Section 1 (Top 12)** | 12 | 11 | 1 | 0 | 0 |
| **Section 2 (Correctness)** | 7 | 6 | 0 | 1 | 0 |
| **Section 3 (Data Integrity)** | 5 | 2 | 0 | 3 | 0 |
| **Section 4 (Content Quality)** | 6 | 4 | 2 | 0 | 0 |
| **Section 5 (Accessibility)** | 10 | 6 | 3 | 1 | 0 |
| **Total** | **40** | **29** | **6** | **5** | **0** |

---

## 1. Executive Summary — Top 12 by Impact

### 1.1 Support matrix reports only one feature per spell
* **Original Claim:** `detect_feature()` returns on the first regex match, hiding secondary dependencies (11 spells affected).
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` line 214 implements `detect_features()` which collects all matching features (`hits`), and `combine_support()` (line 273) merges worst-case browser support across all detected features:
  ```python
  def detect_features(css: str, html: str, title: str, status: str) -> list[str]:
      ...
      hits = []
      for pattern, key in checks:
          if re.search(pattern, src) and key not in hits:
              hits.append(key)
      return hits or ["baseline"]

  def combine_support(feature_keys: list[str]) -> dict:
      browsers = {"chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes"}
      for key in feature_keys:
          support = FEATURE_BROWSERS[key]
          for b in browsers:
              if LEVEL_RANK[support[b]] < LEVEL_RANK[browsers[b]]:
                  browsers[b] = support[b]
      return browsers
  ```
  Running `python3 scripts/build.py` shows worst-case combinations: `status corrected ds-79: Newer -> Baseline (invoker-commands,anchor,starting-style,color-mix)`.

### 1.2 19 descriptions swallowed the next `## section heading`
* **Original Claim:** 19 descriptions absorbed trailing headings (`"… --- ## Reveal & motion"`).
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` lines 514-517 halts description parsing before section headers or divider lines:
  ```python
  for line in desc_src.splitlines():
      line = line.strip()
      if not line:
          continue
      if line.startswith("---") or line.startswith("## ") or line.startswith("### "):
          break
  ```
  Verified in `public/spells.json` (e.g. `ds-90` description: `"Slices a single action button into a radial menu when active or expanded, using native CSS calc(), cos(), and sin()."`).

### 1.3 No URL state
* **Original Claim:** Zero uses of `history`, `location`, `URLSearchParams`, or storage; link sharing and SEO dead.
* **Status:** **FIXED**
* **Evidence:** `public/search.js` lines 103-163 implement state synchronization using `URLSearchParams`, `history.replaceState`, `window.onpopstate`, and `#ds-...` hash deep-linking:
  ```javascript
  function updateUrlState() {
    const params = new URLSearchParams();
    const q = searchInput.value.trim();
    const cat = document.querySelector('input[name="cat"]:checked')?.value;
    const status = document.querySelector('input[name="status"]:checked')?.value;
    ...
    const newUrl = queryString ? `${location.pathname}?${queryString}${location.hash}` : location.pathname + location.hash;
    history.replaceState(null, "", newUrl);
  }
  window.addEventListener("popstate", syncFromUrl);
  ```

### 1.4 "Baseline" vs "Progressive" status contradictions
* **Original Claim:** Handwritten `Status` contradicted support data (e.g. `ds-33` Baseline but red in 2 browsers).
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` lines 288-295 automatically derives `status` from `combine_support()` browser verdicts:
  ```python
  def derive_status(browsers: dict) -> str:
      values = list(browsers.values())
      no_count = values.count("no")
      if no_count >= 2:
          return "Progressive"
      if no_count == 1 or "partial" in values:
          return "Newer"
      return "Baseline"
  ```
  `python3 scripts/build.py` output confirms: `status labels corrected from support data: 30`.

### 1.5 Class-name corruption in preview CSS
* **Original Claim:** `\bbody\b` inside `.ticket-body` gets rewritten to `.ticket-:host`.
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` lines 370-377 uses negative lookarounds in `_ROOT_SELECTOR_RE` and selector prelude parsing:
  ```python
  _ROOT_SELECTOR_RE = re.compile(
      r"(?<![\w.#-])(?P<root>:root\b|\bhtml\b|\bbody\b)(?![\w-])"
  )
  def _rewrite_root_code(code: str) -> str:
      def replace(match: re.Match) -> str:
          return ".stage" if match.group("root") == "body" else ":host"
      return _ROOT_SELECTOR_RE.sub(replace, code)
  ```
  In `public/index.html` / `public/spells.json` for `ds-83`, `.ticket-body` is preserved without corruption.

### 1.6 9 spells render an empty description line in the list
* **Original Claim:** 9 spells had no description, producing `<p class="row__desc"></p>`.
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` line 757 conditionally omits empty `<p class="row__desc">`:
  ```python
  desc = one_line(spell.get("description", ""))
  desc_p = f'<p class="row__desc">{html.escape(desc)}</p>' if desc else ""
  ```
  Descriptions were also written in `README.md` for all 9 spells (`ds-6`, `ds-7`, `ds-10`, `ds-12`, `ds-22`, `ds-24`, `ds-26`, `ds-35`, `ds-bonus`).

### 1.7 Muted text `#8c8778` fails WCAG AA contrast (3.27:1)
* **Original Claim:** `--ink-2` `#8c8778` on `--bg` = 3.27:1.
* **Status:** **FIXED**
* **Evidence:** `public/styles.css` line 25 updates `--ink-2` to darker OKLCH carbon ink:
  ```css
  --paper:          oklch(0.985 0.002 90);
  --ink-2:          oklch(0.4 0.012 260);
  ```
  Contrast against `--paper` (`oklch(0.985 0.002 90)`) increases to >6:1, passing WCAG AA.

### 1.8 Below 960 px preview panel `display:none` dead click target
* **Original Claim:** Row clicks below 960px swapped invisible preview panel.
* **Status:** **FIXED**
* **Evidence:** `public/styles.css` lines 707-710 disables pointer events on `.row__select-overlay` below 960px:
  ```css
  @media (max-width: 959px) {
    .row__select-overlay { pointer-events: none; }
  }
  ```
  Clicking row title (`.row__hit`) or number (`.row__num`) opens the drawer popover directly at all screen widths.

### 1.9 Tailwind tab emits same CSS wrapped in `@layer components`
* **Original Claim:** Tailwind tab emits raw CSS wrapped in `@layer components` without token definitions.
* **Status:** **STILL PRESENT**
* **Evidence:** `scripts/build.py` lines 695-707 (`tailwind_for`) still wraps raw spell CSS without generating `@theme` tokens:
  ```python
  def tailwind_for(spell: dict) -> str:
      css = str(spell.get("css", "")).strip()
      if not css:
          return ""
      indented = "\n".join(("  " + line) if line else line for line in css.split("\n"))
      return "\n".join([
          "/* Tailwind v4 — drop into a global stylesheet processed by Tailwind. */",
          '@import "tailwindcss";',
          "",
          "@layer components {",
          indented,
          "}",
          "",
      ])
  ```

### 1.10 Drawer doesn't `inert` background; focus trap misses shadow DOM
* **Original Claim:** Background elements remained interactive when drawer was open.
* **Status:** **FIXED**
* **Evidence:** `public/search.js` lines 212-220 sets `mainShell.inert = true` and `siteHead.inert = true` when a drawer opens:
  ```javascript
  if (e.newState === "open") {
    if (mainShell) mainShell.inert = true;
    if (siteHead) siteHead.inert = true;
    ...
  } else {
    if (mainShell) mainShell.inert = false;
    if (siteHead) siteHead.inert = false;
  }
  ```
  Drawers also use native `popover="auto"` and `role="dialog" aria-modal="true"`.

### 1.11 No dark mode
* **Original Claim:** Site hardcoded light theme with `color-scheme: light`.
* **Status:** **FIXED**
* **Evidence:** `public/styles.css` lines 112-200 provides complete dark mode tokens via `@media (prefers-color-scheme: dark)` and `:root[data-theme="dark"]`. `public/search.js` lines 38-60 implements `applyTheme()` connected to `#theme-toggle`. `styles.css` line 504 supports stage dark mode via `.preview-host[data-stage-theme="dark"]`.

### 1.12 Full `innerHTML` rebuild on every keystroke, undebounced
* **Original Claim:** `search` input triggered `innerHTML` rebuild of all 145 rows undebounced.
* **Status:** **FIXED**
* **Evidence:** `public/search.js` lines 68-98 filters pre-rendered DOM rows using `row.hidden = !isVisible` instead of `innerHTML`. Line 120 uses `debouncedFilter` with an 80ms timer:
  ```javascript
  function debouncedFilter() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(filter, 80);
  }
  searchInput.addEventListener("input", debouncedFilter);
  ```

---

## 2. Correctness Bugs

### 2.1 Class-name corruption in preview CSS
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` lines 370-377 negative lookaround regex `r"(?<![\w.#-])(?P<root>:root\b|\bhtml\b|\bbody\b)(?![\w-])"`. Verified `.ticket-body` in `ds-83` remains `.ticket-body`.

### 2.2 `oneLine()` produces empty rows
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` line 757 uses `desc_p = f'<p class="row__desc">{html.escape(desc)}</p>' if desc else ""`. `README.md` provides descriptions for all spells.

### 2.3 Category heading `id`s contain a space and an ampersand
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` line 723 defines `slugify()`, generating `id="cat-reveal-motion"` for `"Reveal & motion"` in `public/index.html`.

### 2.4 The counter denominator ignores active filters
* **Status:** **PARTIALLY**
* **Evidence:** `public/search.js` lines 104-106 appends `in ${activeCat}` to the counter string (`Showing 5 of 150 spells in Forms`), but the denominator is still `totalSpells` (150) rather than the category filtered subtotal.

### 2.5 `145` is hardcoded in five places in `index.html`
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` lines 805-890 templates all counts, meta descriptions, and intro paragraphs dynamically using `{total}` derived from `len(spells)` (currently 150).

### 2.6 Double-fire in `closeDrawer()`
* **Status:** **FIXED**
* **Evidence:** Custom JS `closeDrawer()` and transitionend/setTimeout timers were replaced with native HTML `popover="auto"` (`render_drawer`) and CSS `@starting-style` transitions in `public/styles.css`.

### 2.7 Category nav re-render destroys focus
* **Status:** **FIXED**
* **Evidence:** `public/index.html` lines 881-884 uses static `<input type="radio" name="cat">` controls. Category selection toggles state in place without replacing `catList.innerHTML`.

---

## 3. Data Integrity & the Support Matrix

### 3.1 One feature per spell, silently
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` lines 214-276 (`detect_features` returning `hits` list and `combine_support` intersecting worst-case browser support).

### 3.2 `Status` and `browsers` contradict each other
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` lines 288-295 (`derive_status`) automatically aligns status labels with browser support data.

### 3.3 26 spells are graded on `oklch()` rather than what they demonstrate
* **Status:** **PARTIALLY**
* **Evidence:** `scripts/build.py` line 261 demotes `color-mix` / `oklch()` check near the bottom of `checks` so 40+ specific modern CSS features take precedence, but explicit probes for `mix-blend-mode` or `backdrop-filter` were not added.

### 3.4 The support data is a hand-maintained snapshot with no provenance
* **Status:** **PARTIALLY**
* **Evidence:** `scripts/build.py` lines 41-205 added `SUPPORT_AS_OF = "2026-08-24"`, and `public/search.js` lines 165-223 added client-side `CSS.supports()` checks (`FEATURE_SUPPORTS`), though `FEATURE_BROWSERS` remains a static python dict in `build.py`.

### 3.5 No "partial" nuance in the UI
* **Status:** **PARTIALLY**
* **Evidence:** `public/styles.css` line 104 still uses opacity/grayscale for `.brow[data-level="partial"]`, but drawer `blevel` text labels and `.feature-check__badge.is-partial` badges now display distinct warning colors (`var(--warn)`) and text ("Partial").

---

## 4. Content & Copy Quality

### 4.1 19 descriptions absorb the following section heading
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` lines 514-517 stops description scan when encountering `---`, `## `, or `### `.

### 4.2 67 descriptions contain raw Markdown
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` lines 654-672 (`inline_md_to_html`) converts inline backticks to `<code>` and bold text to `<strong>` for drawer rendering.

### 4.3 12 descriptions are wall-of-text (up to 466 chars)
* **Status:** **FIXED**
* **Evidence:** Descriptions in `README.md` were re-written into concise single-sentence summaries (e.g. `ds-60` description in `spells.json` is 137 chars).

### 4.4 Cross-references are plain text
* **Status:** **STILL PRESENT**
* **Evidence:** `scripts/build.py` lines 654-672 (`inline_md_to_html`) only handles `<code>` and `<strong>`, without auto-linking `Spell (\d+)` mentions.

### 4.5 The `note` field is parsed and then never displayed
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` lines 532-544 removed `note` from the output dictionary generated for `spells.json` and `index.html`.

### 4.6 Two spells preview nothing but an apology
* **Status:** **STILL PRESENT**
* **Evidence:** `scripts/build.py` lines 324 & 358 (`PREVIEW_HTML`) still render `demo-note` explanatory paragraphs for `ds-14` and `ds-143`.

---

## 5. Accessibility

### 5.1 Contrast failures (computed from the real tokens)
* **Status:** **FIXED**
* **Evidence:** `public/styles.css` lines 25-29 darkened `--ink-2` to `oklch(0.4 0.012 260)` (>6:1 contrast against `--paper`) and `--accent-ink` to `oklch(0.99 0.002 90)`.

### 5.2 Drawer doesn't neutralise the background
* **Status:** **FIXED**
* **Evidence:** `public/search.js` lines 212-220 sets `mainShell.inert = true` and `siteHead.inert = true` on drawer open.

### 5.3 The focus trap can't see into the previews
* **Status:** **FIXED**
* **Evidence:** Drawers use native `popover="auto"` and background element `inert` management in `public/search.js`.

### 5.4 Tabs are not a spec-compliant tablist
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` lines 748-765 uses native HTML exclusive `<details name="tabs-{spell['id']}">` accordion groups for code tabs.

### 5.5 Copy feedback is visual-only outside the drawer
* **Status:** **STILL PRESENT**
* **Evidence:** `public/search.js` lines 375-397 updates button label to `"Copied!"` without announcing to an `aria-live` status region.

### 5.6 Heading hierarchy skips and mislabels
* **Status:** **PARTIALLY**
* **Evidence:** Sidebar group titles use `<h2 class="filters__label">`, but row titles still use `<h2 class="row__title">` inside row items nested under category `<h2 class="cat-block__title">` headers (`scripts/build.py` line 763).

### 5.7 Filters are buttons, not a filter control
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` lines 787-802 renders filters as semantic `<input type="radio">` controls inside `<label class="nav-item">`.

### 5.8 Browser support icons are decorative-only
* **Status:** **STILL PRESENT**
* **Evidence:** `scripts/build.py` line 730 `browser_icon()` relies on `title` attribute without visually-hidden `<span class="sr-only">` text.

### 5.9 `.row` is a click target that isn't a control
* **Status:** **FIXED**
* **Evidence:** `scripts/build.py` lines 752-772 uses real `<button>` elements (`row__hit` and `row__num`) with `popovertarget` for title and number interactions.

### 5.10 Done well
* **Status:** **STILL PRESENT (intact)**
* **Evidence:** Skip link (`public/styles.css` lines 201-213), `:focus-visible` outline, and `prefers-reduced-motion` rule (lines 993-1002) are maintained.
