---
name: design-spells
description: "Curated micro-interactions, CSS animations, and UI polish patterns optimized for Astro 7, Tailwind CSS v4, and Zero-JS runtime. Use when building or refining UI components, buttons, navigation, cards, headers, and scroll effects."
risk: safe
source: internal
date_added: "2026-08-10"
---

# Design Spells — Astro Canonical (2026)

A single **canonical** reference bank of design spells for modern Astro projects whose goal is **0 client JS**. This file merges the original spell library with an Astro-first structure and **excludes every spell marked `+ JS`**.

The document therefore contains only spells marked **`0 JS`** or **`Markup`**. In the original file's terminology, `Markup` still means the spell is JS-free, but it needs a precise HTML pattern — for example `<details>`, checkbox state, `popover`, a `dialog`-compatible structure, or another native state machine.

In total there are **150 Astro-relevant spells**. Excluded `+ JS` spells: **4, 42**. Spells **97–151** are 2026 additions (Invoker Commands, Interest Invokers, Grid Lanes, `if()`, typed `attr()`, `closedby`, `hidden="until-found"`, Conic Donut, Faceted Matrix, Cart Badge, Gantt, Heatmap, SVG Draw, Section-Spy, Password Meter, Star Rating, Auto Toast, Exclusive Accordion, Swipe Action, Parallax, Datalist, Drop Cap, Image Wipe, Sticky Footer, Skip Link, Map Pin, Dynamic Counter, Animated Counter, Focus-Lock Modal, Fluid Rhythm Function, Donut-Scoped Callout, Snapped Product State, Semantic Metrics Dividers, Organic Avatar Cluster).

---

## How to use this document

### For humans

- Browse the visual catalogue in `public/` (or open the site) to preview, copy, and check browser support.
- Browse to a category that matches the problem.
- Read the metadata line directly under the heading.
- Copy the CSS block and swap in the project’s tokens where needed.
- Start with Baseline spells, then Newer, then Progressive.
- Prefer 1–2 visually dominant spells per section.

### For AI agents and editor agents

- Always refer to spells by their stable number, for example `Spell 43`.
- If several spells solve the same problem, pick the most modern sustainable one first.
- Selection priority: **Baseline → Newer → Progressive**.
- Prefer spells that drop straight into `.astro` components or layout CSS.
- Do not introduce client JS for something this document already solves with a JS-free spell.
- For programmatic access, the catalogue is also exposed as an **MCP server** (`mcp/server.mjs` — `list_categories`, `search_spells`, `get_spell`), backed by the machine-readable `public/spells.json` and its strict contract in `public/spells.schema.json` (JSON Schema) and `schema/spells.d.ts` (TypeScript).

---

## Core principles

- HTML + CSS first.
- 0 client JS by default.
- Native browser state before hand-built solutions.
- Progressive enhancement before hard dependencies.
- Astro fit before demo effect.
- Readability, focus, and layout come before decoration.
- Motion is enhancement and must respect `prefers-reduced-motion`.
- Component-local CSS is usually better than globally leaking selectors.

---

## Metadata and how to read it

The original file’s metadata is kept inside each spell section:

- **Category** = the functional type of the spell.
- **Status** = browser risk: `Baseline`, `Newer`, `Progressive`.
- **JS need** = only `0 JS` and `Markup` appear in this canonical Astro edition.

### Practical reading for Astro

- **0 JS**: ready for static Astro markup.
- **Markup**: still JS-free, but needs a more exact HTML structure.
- **Baseline**: safe to use immediately.
- **Newer**: good in modern projects; test it in critical UI flows.
- **Progressive**: wrap it in `@supports` or give it a silent fallback.

### Recommended placement in Astro

- Global spells: `base.css` or the global design layer.
- Page chrome: `MainLayout.astro`, `Header.astro`, `Shell.astro`.
- Component spells: local CSS in `.astro` components.
- New browser features: next to the component, behind `@supports`.

---

## Base safeguards

This is the foundation every spell builds on. Load it before anything else.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }

html {
  /* Prevents layout shift when a dialog/popover opens and locks the scrollbar */
  scrollbar-gutter: stable;
  /* Prevents unwanted text zoom on mobile devices */
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}

:target, :focus-visible {
  /* Prevents deep-linked content from landing under a sticky header (see Spell 17) */
  scroll-margin-block-start: max(6rem, var(--header-height, 0px));
}

/* Universal focus baseline for keyboard navigation */
:where(
  a[href],
  button,
  input,
  select,
  textarea,
  summary,
  [tabindex]:not([tabindex="-1"])
):focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 3px;
}

/* Prevents scroll from leaking to the parent/body in nested scrollers */
.scroller, .modal-body, .drawer-body {
  overscroll-behavior: contain;
}

/* WCAG 2.2 AA / mobile: minimum hit target for buttons, links, summary, labels. */
button, [type="button"], [type="submit"], [type="reset"],
summary, .btn, a.btn {
  min-block-size: 44px;
}

/* Visually hidden but still in the tab order and accessibility tree.
   Use for checkboxes/inputs that drive markup state machines (see Spell 60). */
.sr-only {
  position: absolute;
  inline-size: 1px; block-size: 1px;
  padding: 0; margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  clip-path: inset(50%);
  white-space: nowrap;
  border: 0;
}
```

## Root scroll-state preset (opt-in)

Add this **only** if you use Spell 43 (Auto-Hide Header) or Spell 47 (Scroll-Awake Back-to-Top). Spells 44, 45, and 46 set up local scroll-state containers themselves and do not need this.

```css
html {
  container-type: scroll-state;
  overflow: auto;
}
```

`container-type: scroll-state` is ignored silently in browsers without support, so the preset is safe to include even where a fallback is required. It is opinionated enough not to be the default.

---

## Selection rules

1. Pick at most 1–2 visually dominant spells per section.
2. Prefer Baseline over Newer, and Newer over Progressive.
3. Prioritize focus, contrast, spacing, and information hierarchy.
4. Place performance spells early on long pages.
5. Use native state (`:has()`, `:focus-within`, `<details>`, `scroll-snap`, `scroll-state`) before inventing your own patterns.

### Anti-patterns

- Too many hover-only spells in touch-heavy interfaces.
- Too many blur or backdrop effects in the same viewport.
- Too many reveal effects at once.
- Too much special markup without a clear payoff.
- Too much decoration before readability and state feedback work.

---

# Spells


## Interaction & feedback

### 1. Shimmer on primary buttons
*Interaction · Baseline · 0 JS*

A subtle light gleam sweeps across the button on hover.

```css
.btn-primary {
  position: relative; overflow: hidden;
  min-block-size: 44px; min-inline-size: 44px;
}
.btn-primary::before {
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  inline-size: 60%;
  background: linear-gradient(120deg, transparent, oklch(1 0 0 / 0.16), transparent);
  transform: translateX(-180%) skewX(-20deg);
  transition: transform 500ms cubic-bezier(0.16,1,0.3,1);
  pointer-events: none;
}
@media (hover: hover) {
  .btn-primary:hover::before { transform: translateX(280%) skewX(-20deg); }
}
.btn-primary:focus-visible::before { transform: translateX(280%) skewX(-20deg); }
```

### 2. Soft Push
*Interaction · Baseline · 0 JS*

A confident scale-down on `:active` for tactile feedback.

```css
.btn, .card-interactive {
  min-block-size: 44px;
  transition: transform 100ms cubic-bezier(0.16,1,0.3,1);
}
.btn:active, .card-interactive:active { transform: scale(0.94); }
```

### 3. Lift & Zoom on cards
*Interaction · Baseline · 0 JS*

The card lifts and the image zooms in slowly.

```css
.destination-card {
  overflow: hidden;
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  box-shadow: 0 1px 2px oklch(0.2 0.01 80 / 0.08);
  transition: transform 350ms cubic-bezier(0.16,1,0.3,1), box-shadow 350ms cubic-bezier(0.16,1,0.3,1);
}
.destination-card img {
  display: block; aspect-ratio: 16 / 10; object-fit: cover;
  transition: transform 600ms cubic-bezier(0.16,1,0.3,1);
}
.destination-card :is(h3, p) { margin: 0; padding-inline: 1rem; }
.destination-card h3 { padding-block-start: .85rem; }
.destination-card p { padding-block-end: 1rem; color: var(--color-text-muted); }
.destination-card:hover,
.destination-card:focus-within {
  transform: translateY(-6px);
  box-shadow: 0 12px 28px oklch(0.2 0.01 80 / 0.18);
}
.destination-card:hover img,
.destination-card:focus-within img { transform: scale(1.05); }
@media (hover: none) {
  .destination-card:hover { transform: none; box-shadow: none; }
  .destination-card:hover img { transform: none; }
}
```

### 5. Magnetic Underline
*Interaction · Baseline · 0 JS*

The underline slides in instead of blinking on.

```css
.nav-link {
  position: relative; text-decoration: none;
  min-block-size: 44px; display: inline-grid; align-items: center;
}
.nav-link::after {
  content: "";
  position: absolute;
  left: 0; bottom: -2px;
  width: 0; height: 1.5px;
  background: currentColor;
  transition: width 240ms cubic-bezier(0.16,1,0.3,1);
}
.nav-link:hover::after,
.nav-link[aria-current="page"]::after { width: 100%; }
```

### 7. Icon Color Shift
*Interaction · Baseline · 0 JS*

Icons transition smoothly through brand color tones on hover and focus.

```css
.icon {
  color: var(--color-text-muted);
  min-block-size: 44px; min-inline-size: 44px;
  display: inline-grid; place-items: center;
  transition: color 180ms cubic-bezier(0.16,1,0.3,1), transform 180ms cubic-bezier(0.16,1,0.3,1);
}
.icon:hover, .icon:focus-visible {
  color: var(--color-accent);
  transform: scale(1.12);
}
```

### 19. Focus-Within Halo
*Interaction · Baseline · 0 JS*

Wrapper-based focus feedback for composite inputs and search boxes.

```css
.input-group {
  display: flex; align-items: center; gap: .5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0 .75rem;
  transition: border-color 180ms cubic-bezier(0.16,1,0.3,1), box-shadow 180ms cubic-bezier(0.16,1,0.3,1);
}
.input-group:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px oklch(from var(--color-primary) l c h / 0.16);
}
.input-group input:focus-visible { outline: none; box-shadow: none; }
```

### 20. Spring-Loaded Checkbox
*Interaction · Baseline · 0 JS*

Animate only the properties that actually change. Never `transition: all`.

```css
input[type="checkbox"] {
  appearance: none;
  inline-size: 44px;
  block-size: 44px;
  min-inline-size: 44px;
  min-block-size: 44px;
  border: 1.5px solid var(--color-text-muted);
  border-radius: 6px;
  display: grid;
  place-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background-color 150ms ease, border-color 150ms ease;
}
input[type="checkbox"]::before {
  content: "";
  width: .7rem; height: .7rem;
  transform: scale(0);
  transition: transform 300ms cubic-bezier(0.34,1.56,0.64,1);
  background: var(--color-bg);
  clip-path: polygon(14% 44%, 0 65%, 50% 100%, 100% 16%, 80% 0%, 43% 62%);
}
input[type="checkbox"]:checked {
  background: var(--color-primary);
  border-color: var(--color-primary);
}
input[type="checkbox"]:checked::before { transform: scale(1); }
```

### 22. Details Chevron Rotate
*Interaction · Baseline · Markup*

Smooth rotation indicator for details disclosure triangles on open state.

```css
summary {
  list-style: none;
  min-block-size: 44px;
  display: flex; align-items: center; gap: .5rem;
  cursor: pointer;
}
summary::-webkit-details-marker { display: none; }
summary .chevron {
  transition: transform 220ms cubic-bezier(0.16,1,0.3,1);
}
details[open] summary .chevron { transform: rotate(180deg); }
```

### 24. External Link Nudge
*Interaction · Baseline · 0 JS*

An outbound link indicator icon that nudges outward on hover.

```css
a[target="_blank"] .external-icon {
  display: inline-block;
  opacity: .55;
  transition: transform 180ms cubic-bezier(0.16,1,0.3,1), opacity 180ms cubic-bezier(0.16,1,0.3,1);
}
a[target="_blank"]:hover .external-icon,
a[target="_blank"]:focus-visible .external-icon {
  transform: translate(.3rem, -.3rem);
  opacity: 1;
}
```

### 26. Pill Segmented Control Glow
*Interaction · Baseline · 0 JS*

Segmented pill selector with smooth active tab highlight and focus indicator.

```css
.segmented {
  display: inline-flex;
  padding: .25rem;
  border-radius: 999px;
  background: var(--color-surface-offset);
}
.segmented button {
  min-block-size: 44px; min-inline-size: 44px;
  padding-inline: 1rem; border: 0; background: transparent; cursor: pointer;
}
.segmented button[aria-pressed="true"] {
  background: var(--color-bg);
  box-shadow: 0 1px 3px oklch(0 0 0 / .08), inset 0 1px 0 oklch(1 0 0 / .3),
    0 0 0 3px color-mix(in oklch, var(--color-primary), transparent 78%);
}
```

### 38. Color-Mix Hover States
*Interaction · Baseline · 0 JS*

Build hover/active variants directly from a base color without hard-coding extra tokens.

```css
.btn-primary {
  background: var(--color-primary);
  transition: background 150ms ease;
}
.btn-primary:hover, .btn-primary:focus-visible {
  background: color-mix(in oklch, var(--color-primary), white 15%);
}
.btn-primary:active {
  background: color-mix(in oklch, var(--color-primary), black 20%);
}
```

### 39. Accent Color Forms
*Interaction · Baseline · 0 JS*

A one-liner that tints every native form control (radio, checkbox, range, progress).

```css
:root {
  accent-color: var(--color-primary);
}
```

### 67. Scroll-Driven Before/After Comparison
*Interaction · Newer · Markup*

A touch-friendly, accessible before/after image comparison with no JavaScript. The scroller exports a named `scroll-timeline` via `timeline-scope` so `clip-path` can animate on a *sibling* surface (not on the scroller itself). Supports swipe gestures and arrow keys (`tabindex="0"`). Use `role="region"` — not `slider` — because `aria-valuenow` cannot be updated without JS.

```html
<div class="compare-container">
    <img src="/after.jpg" alt="After" class="compare-img compare-after">
  <div class="compare-before-wrap">
    <img src="/before.jpg" alt="Before" class="compare-img compare-before">
  </div>
  
  <div class="compare-scroller" tabindex="0" role="region" aria-label="Compare before and after. Swipe or use the arrow keys.">
    <div class="scroller-spacer"></div>
  </div>
```

```css
.compare-container {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-md);
  aspect-ratio: 16 / 9;
  timeline-scope: --compare;
}

.compare-img {
  position: absolute;
  inset: 0;
  width: 100%; height: 100%;
  object-fit: cover;
  pointer-events: none;
}

.compare-before-wrap {
  position: absolute;
  inset: 0;
  width: 100%;
  border-right: 2px solid white;
  box-shadow: 4px 0 16px oklch(0 0 0 / 0.3);
  pointer-events: none;
}

.compare-scroller {
  position: absolute;
  inset: 0;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  overscroll-behavior-x: contain;
  scrollbar-width: none;
  z-index: 10;
  scroll-timeline: --compare inline;
}
.compare-scroller::-webkit-scrollbar { display: none; }

.scroller-spacer {
  width: 200%;
  height: 100%;
  pointer-events: none;
}

@supports (animation-timeline: scroll()) {
  .compare-before-wrap {
    animation: reveal-before linear both;
    animation-timeline: --compare;
  }

  @keyframes reveal-before {
    from { clip-path: inset(0 0% 0 0); }
    to   { clip-path: inset(0 100% 0 0); }
  }
```

### 71. Sliding Segment Indicator
*Interaction · Baseline · Markup*

A pill indicator in segmented controls/tabs that glides to the active choice with `:has()` and CSS variables (`--total-items`).

```html
<div class="segmented-nav" style="--total-items: 3;">
  <input type="radio" name="seg" id="seg-1" class="sr-only" checked style="--index: 0;">
  <label for="seg-1">Overview</label>

  <input type="radio" name="seg" id="seg-2" class="sr-only" style="--index: 1;">
  <label for="seg-2">Analytics</label>

  <input type="radio" name="seg" id="seg-3" class="sr-only" style="--index: 2;">
  <label for="seg-3">Settings</label>

  <div class="segment-pill" aria-hidden="true"></div>
</div>
```

```css
.segmented-nav {
  position: relative;
  display: inline-grid;
  grid-template-columns: repeat(var(--total-items, 3), 1fr);
  padding: 0.25rem;
  background: var(--color-surface-offset);
  border-radius: 999px;
}

.segmented-nav label {
  z-index: 2;
  min-block-size: 44px;
  display: grid; place-items: center;
  padding: 0 1rem;
  text-align: center;
  cursor: pointer;
  font-weight: 500;
  transition: color 200ms ease;
}

.segment-pill {
  position: absolute;
  top: 0.25rem; bottom: 0.25rem;
  width: calc(100% / var(--total-items, 3) - 0.166rem);
  background: var(--color-bg);
  border-radius: 999px;
  box-shadow: 0 1px 3px oklch(0 0 0 / .1);
  z-index: 1;
  transition: transform 260ms cubic-bezier(0.16, 1, 0.3, 1);
}

.segmented-nav:has(#seg-1:checked) .segment-pill { transform: translateX(0%); }
.segmented-nav:has(#seg-2:checked) .segment-pill { transform: translateX(100%); }
.segmented-nav:has(#seg-3:checked) .segment-pill { transform: translateX(200%); }
```

### 73. Expandable Speed Dial FAB
*Interaction · Baseline · Markup*

A floating action button (FAB) that expands child actions via native `<details>` and `@starting-style`. 

**Guardrails:** `pointer-events: none` on the wrapper stops invisible hit areas covering the screen. Every button meets WCAG minimum hit targets (44×44px).

```html
<details class="speed-dial">
  <summary class="fab-main" aria-label="Quick actions">+</summary>

  <div class="fab-actions">
    <button class="fab-child" title="New post" aria-label="New post">📝</button>
    <button class="fab-child" title="Upload image" aria-label="Upload image">📷</button>
    <button class="fab-child" title="Share page" aria-label="Share page">🔗</button>
  </div>
</details>
```

```css
.speed-dial {
  position: fixed;
  right: 1.5rem; bottom: 1.5rem;
  z-index: 100;
  pointer-events: none;
}

.speed-dial summary::-webkit-details-marker { display: none; }

.fab-main {
  pointer-events: auto;
  display: grid; place-items: center;
  min-width: 3.25rem; min-height: 3.25rem;
  border-radius: 999px;
  background: var(--color-primary);
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  box-shadow: 0 8px 24px oklch(0 0 0 / 0.2);
  transition: transform 240ms cubic-bezier(0.16, 1, 0.3, 1);
  touch-action: manipulation;
}

details[open] .fab-main { transform: rotate(45deg); }

.fab-actions {
  position: absolute;
  bottom: 4rem; right: 0.25rem;
  display: none; flex-direction: column; gap: 0.75rem;
  opacity: 0; transform: translateY(12px);
  transition: opacity 240ms ease, transform 240ms cubic-bezier(0.16, 1, 0.3, 1), display 240ms allow-discrete;
}

.fab-child {
  pointer-events: auto;
  min-width: 2.75rem; min-height: 2.75rem;
  border-radius: 999px;
  border: none;
  background: var(--color-bg);
  box-shadow: 0 4px 12px oklch(0 0 0 / 0.15);
  cursor: pointer;
}

details[open] .fab-actions {
  display: flex;
  opacity: 1;
  transform: translateY(0);
}

@starting-style {
  details[open] .fab-actions {
    opacity: 0;
    transform: translateY(12px);
  }
```

### 79. Anchor-Positioned Mega Menu (`[popover]`)
*Navigation · Newer · Markup*

A mega menu that opens from a nav trigger via Invoker Commands (`commandfor` + `command="toggle-popover"`) and native `[popover=auto]`, pinned with anchor positioning. Escape, light-dismiss, and focus handling come for free. Do not set a static `aria-expanded` — the native popover owns the accessibility tree.

```html
<nav class="site-nav">
  <button class="mega-trigger" commandfor="mega-1" command="toggle-popover">
    Products <span aria-hidden="true">▾</span>
  </button>
  <div id="mega-1" popover="auto" class="mega-panel">
    <ul>
      <li><a href="/analytics">Analytics</a></li>
      <li><a href="/automation">Automation</a></li>
      <li><a href="/api">API & Integrations</a></li>
    </ul>
  </div>
</nav>
```

```css
.site-nav { position: relative; anchor-scope: --mega-1; }
.mega-trigger {
  anchor-name: --mega-1;
  min-block-size: 44px;
  padding: 0 var(--space-4);
  background: none; border: 0; cursor: pointer;
  color: var(--color-text); font-weight: 500;
}
.mega-panel {
  margin: 0; inset: auto;
  position-anchor: --mega-1;
  position-area: bottom span-all;
  margin-block-start: var(--space-2);
  position-try-fallbacks: flip-block;
  min-inline-size: 22rem;
  padding: var(--space-4);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: 0 20px 50px oklch(0 0 0 / .14);
  opacity: 0; transform: translateY(-6px);
  transition: opacity 200ms cubic-bezier(.16,1,.3,1),
              transform 200ms cubic-bezier(.16,1,.3,1),
              display 200ms allow-discrete,
              overlay 200ms allow-discrete;
}
.mega-panel:popover-open { opacity: 1; transform: translateY(0); }
@starting-style { .mega-panel:popover-open { opacity: 0; transform: translateY(-6px); } }
.mega-panel a {
  display: block; padding: .65rem .75rem; min-block-size: 44px;
  border-radius: var(--radius-sm); text-decoration: none; color: var(--color-text);
}
.mega-panel a:hover, .mega-panel a:focus-visible { background: var(--color-surface-offset); }
```

### 80. Squircle Chips & Nav (`corner-shape`)
*Navigation · Progressive · 0 JS*

Pill navigation and chips with a true “squircle” silhouette (superellipse corner rounding) instead of ordinary `border-radius` arcs.

```html
<nav class="squircle-nav" aria-label="Main navigation">
  <a href="/" aria-current="page">Overview</a>
  <a href="/reports">Reports</a>
  <a href="/settings">Settings</a>
</nav>
```

```css
.squircle-nav { display: inline-flex; gap: var(--space-2); padding: .25rem;
  background: var(--color-surface-offset); border-radius: 1.25rem; }
@supports (corner-shape: squircle) {
  .squircle-nav { corner-shape: squircle; }
  .squircle-nav a { corner-shape: squircle; }
}
.squircle-nav a {
  min-block-size: 44px; display: inline-grid; place-items: center;
  padding: 0 var(--space-4); border-radius: 1rem;
  text-decoration: none; color: var(--color-text-muted); font-weight: 500;
  transition: background 160ms ease, color 160ms ease;
}
.squircle-nav a:hover { color: var(--color-text); }
.squircle-nav a[aria-current="page"] {
  background: var(--color-bg); color: var(--color-text);
  box-shadow: 0 1px 3px oklch(0 0 0 / .1), inset 0 1px 0 oklch(1 0 0 / .3);
}
```

### 81. Overflow-Aware Breadcrumbs
*Navigation · Progressive · Markup*

Breadcrumbs that show a discreet “+N” hint and edge masking only when the row is actually scrollable.

```html
<nav class="crumbs-wrap" aria-label="Breadcrumb">
  <ol class="crumbs">
    <li><a href="/">Home</a></li>
    <li><a href="/docs">Documentation</a></li>
    <li><a href="/docs/components">Components</a></li>
    <li aria-current="page">Spells</li>
  </ol>
  <span class="crumb-hint" aria-hidden="true">+2</span>
</nav>
```

```css
.crumbs-wrap {
  position: relative; overflow-x: auto; container-type: scroll-state;
  overscroll-behavior-x: contain;
  scrollbar-width: none;
  mask-image: linear-gradient(to right, black 92%, transparent);
  -webkit-mask-image: linear-gradient(to right, black 92%, transparent);
}
.crumbs-wrap::-webkit-scrollbar { display: none; }
.crumbs { display: flex; gap: var(--space-2); white-space: nowrap; list-style: none; padding: 0; }
.crumbs a, .crumbs [aria-current] {
  min-block-size: 44px; display: inline-grid; place-items: center; padding-inline: .35rem;
  color: var(--color-text-muted); text-decoration: none;
}
.crumbs a:hover { color: var(--color-text); }
.crumb-hint {
  position: absolute; right: 0; top: 50%; translate: 0 -50%;
  padding: .2rem .5rem; border-radius: 999px; font-size: .75rem;
  background: var(--color-primary); color: white;
  opacity: 0; transition: opacity 180ms ease;
}
@container scroll-state(scrollable: inline) { .crumb-hint { opacity: 1; } }
```

### 82. Fixed-Angle 3D Tilt Card
*Cards · Baseline · 0 JS*

The card tilts subtly in 3D on hover/focus for a sense of depth — no mouse tracking and no extra DOM layers.

```html
<article class="tilt-card">
  <h3>Premium plan</h3>
  <p>Everything in Pro, plus priority support and SSO.</p>
  <a href="/pricing">Choose plan</a>
</article>
```

```css
.tilt-card {
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-lg); padding: var(--space-6);
  transform: perspective(900px) rotateX(0) rotateY(0);
  transition: transform 350ms cubic-bezier(.16,1,.3,1), box-shadow 350ms cubic-bezier(.16,1,.3,1);
}
.tilt-card:hover, .tilt-card:focus-within {
  transform: perspective(900px) rotateX(3deg) rotateY(-3deg) translateY(-4px);
  box-shadow: 0 16px 40px oklch(.2 .01 80 / .16);
}
.tilt-card:focus-visible { outline: 2px solid var(--color-primary); outline-offset: 3px; }
```

### 83. Perforated Ticket Card
*Cards · Baseline · 0 JS*

A ticket/coupon card with real perforated “holes” on the edges via pseudo-elements.

```html
<article class="ticket">
  <div class="ticket-body">
    <h3>Summer offer</h3>
    <p>20% off every annual plan.</p>
  </div>
  <div class="ticket-stub">
    <strong>−20%</strong>
    <span>Code: SUMMER26</span>
  </div>
</article>
```

```css
.ticket {
  display: grid; grid-template-columns: 1fr auto;
  background: var(--color-surface); border-radius: var(--radius-md);
  position: relative; overflow: hidden;
}
.ticket::before, .ticket::after {
  content: ""; position: absolute; block-size: 1.5rem; inline-size: 1.5rem;
  border-radius: 50%; background: var(--color-bg);
  right: 34%;
}
.ticket::before { top: 0; translate: 50% -50%; }
.ticket::after  { bottom: 0; translate: 50% 50%; }
.ticket-body { padding: var(--space-5); }
.ticket-stub {
  display: grid; place-content: center; gap: .15rem; text-align: center;
  padding: var(--space-5); border-left: 2px dashed var(--color-border);
}
.ticket-stub strong { font-size: 1.5rem; color: var(--color-primary); }
```

### 84. Hover/Focus Reveal Card Actions
*Cards · Baseline · 0 JS*

Secondary card actions stay hidden until the card is hovered or focused.

```html
<article class="card-row">
  <h3>Q3 report</h3>
  <div class="card-actions">
    <button aria-label="Edit Q3 report">✏️</button>
    <button aria-label="Share Q3 report">🔗</button>
    <button aria-label="Archive Q3 report">📦</button>
  </div>
</article>
```

```css
.card-row {
  display: flex; align-items: center; justify-content: space-between; gap: var(--space-3);
  padding: var(--space-4); border: 1px solid var(--color-border); border-radius: var(--radius-md);
}
.card-actions { display: flex; gap: var(--space-1); opacity: 0; transition: opacity 180ms ease; }
.card-row:hover .card-actions,
.card-row:focus-within .card-actions { opacity: 1; }
.card-actions button {
  inline-size: 44px; block-size: 44px; border-radius: var(--radius-sm);
  border: 0; background: transparent; cursor: pointer;
}
.card-actions button:hover { background: var(--color-surface-offset); }
@media (hover: none) { .card-actions { opacity: 1; } }
```

### 88. `:target` Toast Stack
*Overlays · Baseline · 0 JS*

Confirmation toasts that appear when a link sets `#toast-…` and close via a dismiss link.

```html
<a href="#toast-saved" class="btn">Save changes</a>

<div id="toast-saved" class="toast" role="status">
  ✅ Saved! <a href="#" class="toast-close" aria-label="Dismiss notification">✕</a>
</div>
```

```css
.toast {
  position: fixed; bottom: var(--space-5); left: 50%; translate: -50% 16px;
  display: flex; align-items: center; gap: var(--space-3);
  min-block-size: 44px; padding: .6rem 1rem;
  background: var(--color-text); color: var(--color-bg);
  border-radius: 999px; box-shadow: 0 12px 32px oklch(0 0 0 / .2);
  opacity: 0; pointer-events: none; z-index: 300;
  transition: opacity 240ms cubic-bezier(.16,1,.3,1), transform 240ms cubic-bezier(.16,1,.3,1);
}
.toast:target { opacity: 1; translate: -50% 0; pointer-events: auto; }
.toast-close { color: inherit; text-decoration: none; inline-size: 44px; block-size: 44px;
  display: inline-grid; place-items: center; }
```

### 89. Anchor-Pinned Context Menu
*Overlays · Newer · Markup*

A click-driven action menu (⋯) pinned to its trigger with anchor positioning and automatic flip at the screen edges.

```html
<div class="ctx">
  <button class="ctx-btn" commandfor="ctx-menu" command="toggle-popover" aria-haspopup="menu" aria-label="More actions">⋯</button>
  <div id="ctx-menu" popover="auto" class="ctx-menu" role="menu">
    <button role="menuitem">Edit</button>
    <button role="menuitem">Duplicate</button>
    <hr>
    <button role="menuitem" class="danger">Delete</button>
  </div>
```

```css
.ctx { position: relative; anchor-scope: --ctx; }
.ctx-btn { anchor-name: --ctx; inline-size: 44px; block-size: 44px; border-radius: var(--radius-sm);
  border: 1px solid var(--color-border); background: var(--color-bg); cursor: pointer; }
.ctx-menu {
  margin: 0; inset: auto;
  position-anchor: --ctx; position-area: bottom end; margin-block-start: var(--space-2);
  position-try-fallbacks: flip-inline, flip-block;
  min-inline-size: 12rem; padding: var(--space-2);
  background: var(--color-bg); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); box-shadow: 0 20px 50px oklch(0 0 0 / .16);
  opacity: 0; transform: scale(.96); transform-origin: top right;
  transition: opacity 180ms cubic-bezier(.16,1,.3,1), transform 180ms cubic-bezier(.16,1,.3,1),
              display 180ms allow-discrete, overlay 180ms allow-discrete;
}
.ctx-menu:popover-open { opacity: 1; transform: scale(1); }
@starting-style { .ctx-menu:popover-open { opacity: 0; transform: scale(.96); } }
.ctx-menu button { display: block; inline-size: 100%; min-block-size: 44px; text-align: start;
  padding: 0 .85rem; border: 0; background: none; border-radius: var(--radius-sm); cursor: pointer; color: var(--color-text); }
.ctx-menu button:hover, .ctx-menu button:focus-visible { background: var(--color-surface-offset); }
.ctx-menu .danger { color: var(--color-error); }
.ctx-menu hr { border: 0; border-top: 1px solid var(--color-border); margin-block: var(--space-1); }
```

### 90. Sun-Fan FAB (radial)
*Overlays · Baseline · Markup*

A floating action button that fans child actions into an arc via native CSS `cos()` / `sin()`.

```html
<details class="fan">
  <summary class="fan-main" aria-label="Quick actions">＋</summary>
  <div class="fan-items">
    <button class="fan-item" style="--i:0" aria-label="New post">📝</button>
    <button class="fan-item" style="--i:1" aria-label="Upload">📷</button>
    <button class="fan-item" style="--i:2" aria-label="Share">🔗</button>
  </div>
</details>
```

```css
.fan { position: fixed; right: 1.5rem; bottom: 1.5rem; z-index: 100; pointer-events: none; }
.fan summary::-webkit-details-marker { display: none; }
.fan-main {
  pointer-events: auto; display: grid; place-items: center;
  inline-size: 3.25rem; block-size: 3.25rem; border-radius: 999px; cursor: pointer;
  background: var(--color-primary); color: white; font-size: 1.4rem;
  box-shadow: 0 8px 24px oklch(0 0 0 / .2);
  transition: transform 240ms cubic-bezier(.16,1,.3,1);
}
details[open] .fan-main { transform: rotate(45deg); }
.fan-items { position: absolute; bottom: 0; right: 0; }
.fan-item {
  pointer-events: auto; position: absolute; bottom: .35rem; right: .35rem;
  inline-size: 2.75rem; block-size: 2.75rem; border-radius: 999px; border: 0; cursor: pointer;
  background: var(--color-bg); box-shadow: 0 4px 12px oklch(0 0 0 / .18);
  --angle: calc(var(--i) * 45deg + 180deg);
  opacity: 0; transform: translate(0, 0) scale(.6);
  transition: transform 280ms cubic-bezier(.34,1.56,.64,1), opacity 200ms ease,
              display 280ms allow-discrete;
  transition-delay: calc(var(--i) * 40ms);
}
details[open] .fan-item {
  opacity: 1;
  transform: translate(calc(cos(var(--angle)) * -5.5rem), calc(sin(var(--angle)) * 5.5rem)) scale(1);
}
@starting-style { details[open] .fan-item { opacity: 0; transform: translate(0,0) scale(.6); } }
```

---

## Reveal & motion

### 8. Gradient Reveal on headings
*Reveal · Progressive · 0 JS*

A scroll-driven text reveal with `animation-timeline: view()`.

```css
@supports (animation-timeline: view()) {
  .section-heading {
    clip-path: inset(0 100% 0 0);
    animation: reveal-text linear both;
    animation-timeline: view();
    animation-range: entry 0% entry 60%;
  }
  @keyframes reveal-text { to { clip-path: inset(0 0 0 0); } }
}
```

### 9. Depth Parallax on hero
*Reveal · Baseline · 0 JS*

A light 3D settle on load.

```css
.hero-content { animation: hero-settle 0.8s cubic-bezier(0.16,1,0.3,1) both; }
@keyframes hero-settle {
  from { opacity: 0; transform: perspective(800px) rotateX(4deg) translateY(12px); }
  to   { opacity: 1; transform: perspective(800px) rotateX(0) translateY(0); }
}
```

### 11. Skeleton Shimmer
*Reveal · Baseline · 0 JS*

A CSS-driven loading surface.

```css
@keyframes shimmer {
  from { background-position: -200% 0; }
  to   { background-position: 200% 0; }
}
.skeleton {
  background: linear-gradient(90deg,
    var(--color-surface-offset) 25%,
    var(--color-surface-dynamic) 50%,
    var(--color-surface-offset) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}
```

### 14. Native Page Transitions (`@view-transition`)
*Reveal · Newer · 0 JS*

A large premium effect for multi-page sites. The browser handles MPA navigation natively.

```css
@supports (view-transition-name: none) {
  @view-transition { navigation: auto; }

  ::view-transition-old(root) {
    animation: fade-out 240ms cubic-bezier(0.16,1,0.3,1) both;
  }
  ::view-transition-new(root) {
    animation: slide-up-in 360ms cubic-bezier(0.16,1,0.3,1) both;
  }

  @keyframes fade-out { to { opacity: 0; transform: scale(0.985); } }
  @keyframes slide-up-in {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }
```

### 31. Phantom Entry (`@starting-style`)
*Reveal · Baseline · Markup*

A soft fade-in from `display: none` with no JS. Perfect for popover menus (`[popover]`) and native modals.

```css
.popover-menu {
  display: none;
  opacity: 0;
  transform: translateY(-8px) scale(0.96);
  transition: opacity 240ms cubic-bezier(0.16,1,0.3,1),
              transform 240ms cubic-bezier(0.16,1,0.3,1),
              display 240ms allow-discrete;
}
.popover-menu:popover-open,
.popover-menu.is-open {
  display: block;
  opacity: 1;
  transform: translateY(0) scale(1);
}
@starting-style {
  .popover-menu:popover-open,
  .popover-menu.is-open {
    opacity: 0;
    transform: translateY(-8px) scale(0.96);
  }
```

### 65. Scroll-Driven Header Compression
*Scroll-driven · Newer · 0 JS*

Shrinks the sticky header and scales the logo down as the user scrolls, without layout shifts.

```css
.site-header {
  position: sticky; top: 0; z-index: 100;
  padding-block: 1.25rem;
  transition: padding 150ms ease;
}

.header-logo {
  transform-origin: left center;
  transition: transform 150ms ease;
}

@supports (animation-timeline: scroll()) {
  .site-header {
    animation: shrink-header linear both;
    animation-timeline: scroll(root block);
    animation-range: 0px 120px;
  }
  
  .header-logo {
    animation: scale-logo linear both;
    animation-timeline: scroll(root block);
    animation-range: 0px 120px;
  }

  @keyframes shrink-header { to { padding-block: 0.5rem; } }
  @keyframes scale-logo { to { transform: scale(0.85); } }
}
```

### 66. Backdrop Transition (`::backdrop`)
*Reveal · Newer · Markup*

A seamless fade and blur on `::backdrop` for native `<dialog>` and `[popover]` modals, with no JS.

```css
dialog::backdrop,
[popover]::backdrop {
  background: oklch(0 0 0 / 0.4);
  backdrop-filter: blur(8px);
  opacity: 0;
  transition: opacity 280ms cubic-bezier(0.16, 1, 0.3, 1),
              backdrop-filter 280ms cubic-bezier(0.16, 1, 0.3, 1),
              display 280ms allow-discrete,
              overlay 280ms allow-discrete;
}

dialog[open]::backdrop,
[popover]:popover-open::backdrop {
  opacity: 1;
}

@starting-style {
  dialog[open]::backdrop,
  [popover]:popover-open::backdrop {
    opacity: 0;
  }
```

### 68. Infinite Logo Marquee
*Reveal · Baseline · 0 JS*

A smooth infinite logo marquee with edge fades via `mask-image`. 

**Note:** Requires duplicated HTML markup (two identical `.marquee-track` elements) to loop without a gap. Pauses automatically on `:hover` and `:focus-within` for accessibility.

```html
<div class="marquee">
  <div class="marquee-track">
    <span>Logo 1</span><span>Logo 2</span><span>Logo 3</span>
  </div>
  <!-- Duplicated track for a seamless loop -->
  <div class="marquee-track" aria-hidden="true">
    <span>Logo 1</span><span>Logo 2</span><span>Logo 3</span>
  </div>
```

```css
.marquee {
  display: flex;
  overflow: hidden;
  user-select: none;
  gap: 2rem;
  mask-image: linear-gradient(to right, transparent, black 10%, black 90%, transparent);
  -webkit-mask-image: linear-gradient(to right, transparent, black 10%, black 90%, transparent);
}

.marquee-track {
  display: flex;
  flex-shrink: 0;
  gap: 2rem;
  align-items: center;
  min-width: 100%;
  animation: marquee-scroll 25s linear infinite;
}

.marquee:hover .marquee-track,
.marquee:focus-within .marquee-track {
  animation-play-state: paused;
}

@keyframes marquee-scroll {
  from { transform: translateX(0%); }
  to   { transform: translateX(-100%); }
}
```

### 72. Scroll-Driven Staggered List
*Reveal · Progressive · 0 JS*

List and card items fade in sequence as the user scrolls, synced to viewport position.

```css
@supports (animation-timeline: view()) {
  .stagger-list > * {
    animation: list-entry linear both;
    animation-timeline: view();
    animation-range: entry 5% entry 30%;
  }

  @keyframes list-entry {
    from {
      opacity: 0;
      transform: translateY(24px) scale(0.96);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
}
```

### 75. Native Modal Image Zoom (`popovertarget`)
*Reveal · Newer · Markup*

Click an image to enlarge it to a fullscreen view with a native `popover` — no heavy lightbox library.

```html
<button commandfor="img-modal-1" command="toggle-popover" class="img-trigger">
  <img src="/photo-thumb.jpg" alt="Enlarge image">
</button>

<div id="img-modal-1" popover class="lightbox-popover">
  <img src="/photo-full.jpg" alt="Enlarged image">
</div>
```

```css
.img-trigger {
  display: block; padding: 0; border: 0; background: none; cursor: pointer;
  min-block-size: 44px; min-inline-size: 44px;
}
.img-trigger img { display: block; inline-size: 100%; }
.lightbox-popover {
  margin: auto;
  padding: 0;
  border: none;
  background: transparent;
  max-width: 90vw;
  max-height: 90vh;
  opacity: 0;
  transform: scale(0.92);
  transition: opacity 250ms ease, transform 250ms cubic-bezier(0.16, 1, 0.3, 1), display 250ms allow-discrete;
}

.lightbox-popover:popover-open {
  opacity: 1;
  transform: scale(1);
}

@starting-style {
  .lightbox-popover:popover-open {
    opacity: 0;
    transform: scale(0.92);
  }
```

### 91. Ken Burns Scroll Gallery
*Media · Progressive · 0 JS*

Images breathe slowly (scale 1.12 → 1 → 1.12) synced to their position in the viewport, with no scroll listener.

```html
<figure class="kb"><img src="/hero-1.jpg" alt="Coastal landscape"></figure>
```

```css
.kb { overflow: hidden; border-radius: var(--radius-lg); margin: 0; }
.kb img { display: block; inline-size: 100%; block-size: auto; }
@supports (animation-timeline: view()) {
  .kb img {
    animation: kb-breathe linear both;
    animation-timeline: view();
    animation-range: entry 0% exit 100%;
  }
  @keyframes kb-breathe {
    0%   { transform: scale(1.12) translateY(2%); }
    50%  { transform: scale(1)    translateY(0); }
    100% { transform: scale(1.12) translateY(-2%); }
  }
```

### 92. Image-Clipped Gradient Headline
*Media · Baseline · 0 JS*

A headline filled with an image or gradient via `background-clip: text`.

```html
<h1 class="paint-headline">Build faster. Ship prettier.</h1>
```

```css
.paint-headline {
  text-wrap: balance;
  background-image: linear-gradient(120deg, var(--color-primary), oklch(.7 .2 320));
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent; color: transparent;
}
@supports not ((-webkit-background-clip: text) or (background-clip: text)) {
  .paint-headline { color: var(--color-primary); background: none; }
}
```

### 93. Snapped Caption Reveal
*Media · Progressive · Markup*

Captions in a scroll-snap carousel fade in only once the slide is “snapped”.

```html
<div class="snap-carousel">
  <figure class="slide">
    <img src="/a.jpg" alt="">
    <figcaption class="caption">The Alps — winter 2026</figcaption>
  </figure>
  <figure class="slide">
    <img src="/b.jpg" alt="">
    <figcaption class="caption">The coast — autumn 2025</figcaption>
  </figure>
</div>
```

```css
.snap-carousel { display: flex; gap: var(--space-4); overflow-x: auto;
  scroll-snap-type: x mandatory; overscroll-behavior-x: contain; }
.slide { flex: 0 0 85%; scroll-snap-align: center; position: relative;
  container-type: scroll-state; margin: 0; }
.slide img { inline-size: 100%; border-radius: var(--radius-md); display: block; }
.caption {
  position: absolute; bottom: var(--space-3); left: var(--space-3);
  padding: .4rem .8rem; border-radius: 999px; background: oklch(0 0 0 / .6); color: white;
  opacity: 0; translate: 0 8px; transition: opacity 220ms ease, transform 220ms cubic-bezier(.16,1,.3,1);
}
@container scroll-state(snapped: inline) { .caption { opacity: 1; translate: 0 0; } }
.slide:focus-within .caption { opacity: 1; translate: 0 0; }
```

---

## Scroll-driven & scroll-state

### 17. Ambient Frost Header
*Scroll-driven · Newer · 0 JS*

The header becomes frosted glass only after the user has scrolled a little.

```css
.site-header {
  position: sticky; top: 0; z-index: 100;
  background: transparent;
  border-bottom: 1px solid transparent;
}
@supports (animation-timeline: scroll()) {
  .site-header {
    animation: frost-header linear both;
    animation-timeline: scroll(root block);
    animation-range: 0px 80px;
  }
  @keyframes frost-header {
    to {
      background: oklch(from var(--color-bg) l c h / 0.82);
      backdrop-filter: blur(12px) saturate(160%);
      -webkit-backdrop-filter: blur(12px) saturate(160%);
      border-bottom-color: var(--color-border);
      box-shadow: 0 4px 20px oklch(0 0 0 / 0.05);
    }
}
```

### 30. Sticky CTA Elevation
*Scroll-driven · Baseline · 0 JS*

A sticky bottom CTA gains more separation when it sits on top of content.

```css
.sticky-cta {
  position: sticky; bottom: 0;
  background: oklch(from var(--color-bg) l c h / .88);
  backdrop-filter: blur(10px);
  border-top: 1px solid var(--color-border);
}
```

### 36. Scroll Progress Bar
*Scroll-driven · Progressive · 0 JS*

A thin progress indicator driven entirely by scroll position.

```css
@supports (animation-timeline: scroll()) {
  .scroll-progress {
    position: fixed;
    top: 0; left: 0;
    inline-size: 100%;
    block-size: 3px;
    background: var(--color-primary);
    transform-origin: left;
    transform: scaleX(0);
    z-index: 200;
    animation: grow-progress linear both;
    animation-timeline: scroll(root block);
  }
  @keyframes grow-progress { to { transform: scaleX(1); } }
}
```

Markup: `<div class="scroll-progress"></div>`.

### 43. Auto-Hide Header
*Scroll-state · Progressive · 0 JS*

The header slides away on scroll down and returns on scroll up. **Requires the Root scroll-state preset.**

```css
.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  transition: transform 280ms cubic-bezier(0.16,1,0.3,1);
}

@container scroll-state(scrolled: bottom) {
  .site-header { transform: translateY(-100%); }
}
@container scroll-state(scrolled: top) {
  .site-header { transform: translateY(0); }
}
```

### 44. Sticky Shadow When Stuck
*Scroll-state · Progressive · 0 JS*

A sticky element gains extra shadow and border only once it is actually stuck. Much more premium than a permanent shadow.

```css
.toc {
  position: sticky;
  top: 1rem;
  container-type: scroll-state;
}

.toc__inner {
  border: 1px solid transparent;
  transition: box-shadow 220ms ease, border-color 220ms ease, background 220ms ease;
}

@container scroll-state(stuck: top) {
  .toc__inner {
    background: oklch(from var(--color-bg) l c h / .86);
    border-color: var(--color-border);
    box-shadow: 0 12px 32px oklch(0 0 0 / .10);
  }
```

### 45. Snapped Spotlight
*Scroll-state · Progressive · 0 JS*

The active slide in a scroll-snap container gets full sharpness while siblings fade down.

```css
.carousel {
  display: flex;
  gap: var(--space-4);
  overflow-x: auto;
  scroll-snap-type: inline mandatory;
  overscroll-behavior-x: contain;
}

.slide {
  scroll-snap-align: center;
  container-type: scroll-state;
}

.slide > article {
  opacity: .58;
  transform: scale(.96);
  transition: opacity 220ms ease, transform 220ms cubic-bezier(0.16,1,0.3,1);
}

@container scroll-state(snapped: inline) {
  article {
    opacity: 1;
    transform: scale(1);
  }
```

### 46. Real Overflow Hint
*Scroll-state · Progressive · 0 JS*

Show edge fades, arrows, or “swipe me” hints only when the content is actually scrollable.

```css
.tabs-wrap {
  position: relative;
  overflow-x: auto;
  container-type: scroll-state;
}

.tabs-wrap .fade-hint {
  opacity: 0;
  transition: opacity 180ms ease;
}

@container scroll-state(scrollable: inline) {
  .fade-hint { opacity: 1; }
}
```

### 47. Scroll-Awake Back-to-Top
*Scroll-state · Progressive · 0 JS*

A floating button that wakes only after the user has moved the page. **Requires the Root scroll-state preset.**

```css
.backtotop {
  position: fixed;
  right: 1rem;
  bottom: 1rem;
  inline-size: 44px; block-size: 44px;
  min-inline-size: 44px; min-block-size: 44px;
  display: grid; place-items: center;
  opacity: 0;
  transform: translateY(10px) scale(.96);
  pointer-events: none;
  transition: opacity 200ms ease, transform 240ms cubic-bezier(0.16,1,0.3,1);
}

@container scroll-state(scrolled: block) {
  .backtotop {
    opacity: 1;
    transform: none;
    pointer-events: auto;
  }
```

### 55. Sticky Card Deck
*Scroll-driven · Progressive · 0 JS*

Cards stack like a deck as the user scrolls. Scale and dimming stay synced to the exit-crossing.

```css
.card-stack { display: flex; flex-direction: column; gap: var(--space-4); }

.card-stack .card {
  position: sticky;
  top: max(2rem, var(--header-height, 0px));
  transform-origin: top center;
}

@supports (animation-timeline: view()) {
  .card-stack .card {
    animation: stack-shrink linear both;
    animation-timeline: view(block);
    animation-range: exit-crossing 0% exit-crossing 100%;
  }
  @keyframes stack-shrink {
    to {
      transform: scale(0.92) translateY(-0.5rem);
      filter: brightness(0.6);
    }
}
```

### 69. Scroll-Aware Table Boundaries (`container-type: scroll-state`)
*Scroll-state · Progressive · 0 JS*

Tables with `position: sticky` show edge shadows and dividers *only* when the content has actually been scrolled horizontally.

```css
.table-wrapper {
  overflow-x: auto;
  container-type: scroll-state;
}

.table-wrapper th:first-child,
.table-wrapper td:first-child {
  position: sticky;
  left: 0;
  background: var(--color-bg);
  transition: box-shadow 200ms ease;
}

@container scroll-state(scrolled: inline) {
  .table-wrapper th:first-child,
  .table-wrapper td:first-child {
    box-shadow: 4px 0 12px oklch(0 0 0 / 0.1);
  }
```

---

## Layout & composition

### 12. Scroll Snap gallery
*Layout · Baseline · 0 JS*

Touch-friendly horizontal scroll carousel with native CSS scroll snapping.

```css
.gallery {
  display: flex;
  overflow-x: auto;
  gap: var(--space-4);
  scroll-snap-type: x mandatory;
  overscroll-behavior-x: contain;
}
.gallery > * {
  flex: 0 0 clamp(280px, 70vw, 480px);
  scroll-snap-align: start;
}
```

### 15. 0fr Accordion
*Layout · Baseline · Markup · → 33 is more modern*

Keep this for broader browser compatibility or older projects.

```css
details .accordion-panel {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 320ms cubic-bezier(0.16,1,0.3,1);
}
details .accordion-inner { overflow: hidden; opacity: 0; transition: opacity 200ms ease; }
details[open] .accordion-panel { grid-template-rows: 1fr; }
details[open] .accordion-inner { opacity: 1; transition-delay: 80ms; }
```

### 27. Edge Fade Scroll Hint
*Layout · Baseline · 0 JS · → 56 is more modern*

Keep this only if the background is solid and static. Otherwise use Spell 56.

```css
.scroller-wrap { position: relative; }
.scroller-wrap::before,
.scroller-wrap::after {
  content: "";
  position: absolute; top: 0; bottom: 0; width: 2rem;
  pointer-events: none; z-index: 1;
}
.scroller-wrap::before {
  left: 0;
  background: linear-gradient(to right, var(--color-bg), transparent);
}
.scroller-wrap::after {
  right: 0;
  background: linear-gradient(to left, var(--color-bg), transparent);
}
```

### 33. True Auto-Height (`interpolate-size`)
*Layout · Baseline · Markup*

A modernization of Spell 15. Animates `block-size: 0` → `auto` directly.

```css
:root {
  interpolate-size: allow-keywords;
}

.accordion-panel {
  block-size: 0;
  overflow: hidden;
  transition: block-size 300ms cubic-bezier(0.16,1,0.3,1);
}

details[open] .accordion-panel {
  block-size: auto;
}
```

Bonus: `<details name="faq">` gives you an exclusive accordion automatically (siblings close when a new one opens).

### 37. Container-Aware Card (`@container`)
*Layout · Baseline · 0 JS*

A card that adapts its layout to its container, not the viewport.

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}

.adaptive-card {
  display: grid;
  gap: var(--space-3);
}

@container card (min-inline-size: 420px) {
  .adaptive-card {
    grid-template-columns: 1fr 1.6fr;
    align-items: start;
  }
  .adaptive-card .card-media {
    aspect-ratio: 1;
    border-radius: var(--radius-md) 0 0 var(--radius-md);
  }
```

### 40. Subgrid Alignment
*Layout · Baseline · 0 JS*

Cards in a grid share the exact same row tracks despite different amounts of content.

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-4);
}

.card-grid > .card {
  display: grid;
  grid-template-rows: subgrid;
  grid-row: span 3;
}
```

### 56. Seamless Edge Mask (`mask-image`)
*Layout · Baseline · 0 JS · replaces 27 in most cases*

The scroller’s own edges become literally transparent. Works regardless of the background color or pattern behind it.

```css
.scroll-gallery {
  overflow-x: auto;
  overscroll-behavior-x: contain;
  mask-image: linear-gradient(
    to right,
    transparent 0%,
    black 5%,
    black 95%,
    transparent 100%
  );
  -webkit-mask-image: linear-gradient(to right, transparent 0%, black 5%, black 95%, transparent 100%);
}
```

### 61. Native Accordion Tabs (`::details-content`)
*Layout · Newer · Markup*

Real tabs via `<details name="ui-tabs">`. No radio-button hack.

```css
details[name="ui-tabs"] summary::-webkit-details-marker { display: none; }

.tabs-container {
  display: flex; gap: var(--space-2); position: relative;
  padding-block-end: 320px;
}

details[name="ui-tabs"] summary {
  min-block-size: 44px;
  display: inline-grid; place-items: center;
  padding: var(--space-2) var(--space-4);
  cursor: pointer;
  border-bottom: 2px solid transparent;
}
details[name="ui-tabs"][open] summary { border-bottom-color: var(--color-primary); }

details[name="ui-tabs"]::details-content {
  position: absolute;
  top: 100%; left: 0; width: 100%;
  padding-block-start: var(--space-4);
  transition: opacity 300ms ease, content-visibility 300ms allow-discrete;
}
```

### 62. Native Carousel Controls (`::scroll-marker`, `::scroll-button`)
*Layout · Progressive · 0 JS*

Fully native pagination and previous/next buttons for scroll-snap carousels. Removes the last JS libraries (Swiper, Embla, Splide) for standard carousels.

```css
@supports selector(::scroll-marker) {
  .carousel {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    scroll-marker-group: after;
  }

  .carousel > .slide {
    scroll-snap-align: center;
    flex: 0 0 100%;
  }

  /* Automatically creates one button per slide */
  .carousel > .slide::scroll-marker {
    content: "";
    inline-size: .6rem;
    block-size: .6rem;
    border-radius: 999px;
    background: var(--color-text-muted);
    margin: 0 .25rem;
    transition: background 180ms ease, transform 180ms ease;
  }

  .carousel > .slide::scroll-marker:target-current {
    background: var(--color-primary);
    transform: scale(1.4);
  }

  /* Native scroll buttons */
  .carousel::scroll-button(left),
  .carousel::scroll-button(right) {
    content: "";
    inline-size: 44px;
    block-size: 44px;
    min-inline-size: 44px;
    min-block-size: 44px;
    border-radius: 999px;
    background: var(--color-bg);
    box-shadow: 0 4px 12px oklch(0 0 0 / .12);
  }
  .carousel::scroll-button(left)  { content: "←"; }
  .carousel::scroll-button(right) { content: "→"; }
}
```

### 70. Native Tree View Navigation (`<details>`)
*Layout · Baseline · Markup*

A tree view for documentation or sidebars built from nested `<details>` elements, with no JS.

```html
<nav class="tree-nav">
  <details open>
    <summary>Documentation</summary>
    <div class="tree-group">
      <a href="/docs/start">Get started</a>
      <details>
        <summary>Components</summary>
        <div class="tree-group">
          <a href="/docs/buttons">Buttons</a>
          <a href="/docs/cards">Cards</a>
        </div>
      </details>
    </div>
  </details>
</nav>
```

```css
.tree-nav details {
  padding-left: 0.75rem;
  border-left: 1px solid var(--color-border);
}

.tree-nav summary {
  cursor: pointer;
  min-block-size: 44px;
  display: flex; align-items: center;
  padding: 0.35rem 0.5rem;
  font-weight: 500;
  list-style: none;
}
.tree-nav summary::-webkit-details-marker { display: none; }

.tree-nav summary::before {
  content: "▶";
  display: inline-block;
  margin-right: 0.4rem;
  font-size: 0.7em;
  transition: transform 180ms ease;
}

.tree-nav details[open] > summary::before {
  transform: rotate(90deg);
}

.tree-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-top: 0.25rem;
}

.tree-group a {
  min-block-size: 44px;
  display: flex; align-items: center;
  padding: 0.3rem 0.5rem;
  color: var(--color-text-muted);
  text-decoration: none;
  border-radius: var(--radius-sm);
}

.tree-group a:hover {
  background: var(--color-surface-offset);
  color: var(--color-text);
}
```

### 77. Responsive Sheet Modal
*Layout · Newer · Markup*

A dialog that behaves as a bottom sheet on phones and a centered modal on larger screens.

```css
dialog.responsive-sheet {
  margin: auto auto 0 auto; /* Bottom-aligned on mobile */
  width: 100%;
  max-width: 100%;
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  border: none;
  transform: translateY(100%);
  transition: transform 300ms cubic-bezier(0.16, 1, 0.3, 1), display 300ms allow-discrete;
}

dialog.responsive-sheet[open] {
  transform: translateY(0);
}

@starting-style {
  dialog.responsive-sheet[open] {
    transform: translateY(100%);
  }

/* Centered modal on desktop */
@media (min-width: 640px) {
  dialog.responsive-sheet {
    margin: auto;
    max-width: 32rem;
    border-radius: var(--radius-lg);
    transform: scale(0.95);
  }

  @starting-style {
    dialog.responsive-sheet[open] {
      transform: scale(0.95);
    }
}
```

---

## Anchor & positioning

### 18. Micro-Tooltips (`attr(data-tooltip)`)
*Anchor (legacy) · Baseline · 0 JS · → 34 is more modern*

Keep this for simple hover text on elements where `overflow: hidden` is not a problem.

```css
[data-tooltip] { position: relative; }
[data-tooltip]::after {
  content: attr(data-tooltip);
  position: absolute;
  left: 50%; bottom: calc(100% + 8px);
  transform: translateX(-50%) translateY(4px) scale(.96);
  opacity: 0;
  white-space: nowrap;
  padding: 6px 10px;
  border-radius: var(--radius-sm);
  background: var(--color-text);
  color: var(--color-bg);
  pointer-events: none;
  transition: opacity 180ms cubic-bezier(0.16,1,0.3,1), transform 180ms cubic-bezier(0.16,1,0.3,1);
}
@media (hover: hover) {
  [data-tooltip]:hover::after {
    opacity: 1;
    transform: translateX(-50%) translateY(0) scale(1);
  }
[data-tooltip]:focus-visible::after {
  opacity: 1;
  transform: translateX(-50%) translateY(0) scale(1);
}
```

### 34. Anchor-Positioned Tooltips
*Anchor · Newer · 0 JS*

Tooltips pinned via `anchor-name` / `position-anchor`. No overflow problems.

```css
.tooltip-trigger {
  anchor-name: --info-anchor;
}

.native-tooltip {
  position: absolute;
  position-anchor: --info-anchor;
  position-area: top span-all;
  margin-bottom: var(--space-2);
  position-try-fallbacks: flip-block;
}
```

### 48. Anchored Error Bubble
*Anchor · Newer · 0 JS*

Field validation errors pin to the input without pushing the layout down.

```css
.field {
  position: relative;
}

.field input,
.field textarea,
.field select {
  anchor-name: --field-anchor;
}

.field .error-bubble {
  position: absolute;
  position-anchor: --field-anchor;
  position-area: bottom span-all;
  margin-top: .5rem;
  inline-size: max-content;
  max-inline-size: min(32ch, 90vw);
  padding: .55rem .75rem;
  border-radius: var(--radius-sm);
  background: var(--color-error);
  color: white;
  opacity: 0;
  transform: translateY(-4px);
  transition: opacity 180ms ease, transform 180ms ease;
}

.field:has(:user-invalid) .error-bubble {
  opacity: 1;
  transform: translateY(0);
}
```

### 49. Anchored Filter Panel
*Anchor · Newer · 0 JS*

Filter menus, sort panels, and account menus pinned to their trigger.

```css
.filterbar {
  position: relative;
  anchor-scope: --filter-btn;
}

.filter-trigger {
  anchor-name: --filter-btn;
}

.filter-panel {
  position: absolute;
  position-anchor: --filter-btn;
  position-area: bottom end;
  margin-top: .5rem;
  min-inline-size: 18rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg);
  box-shadow: 0 20px 50px oklch(0 0 0 / .14);
}
```

### 50. Focus Help Rail
*Anchor · Newer · 0 JS*

Contextual help appears beside a field on `:focus-within`.

```css
.form-row {
  position: relative;
  anchor-scope: --help-anchor;
}

.form-row label {
  anchor-name: --help-anchor;
}

.form-row .help-rail {
  position: absolute;
  position-anchor: --help-anchor;
  position-area: right span-all;
  margin-left: .75rem;
  inline-size: 22ch;
  opacity: 0;
  transform: translateX(-6px);
  transition: opacity 180ms ease, transform 180ms ease;
}

.form-row:focus-within .help-rail {
  opacity: 1;
  transform: translateX(0);
}
```

---

## Typography

### 10. Selection Skin
*Typography · Baseline · 0 JS*

Custom text highlight styling using `::selection` to match brand identity.

```css
::selection {
  background: oklch(from var(--color-primary) l c h / 0.25);
  color: var(--color-text);
}
```

### Bonus. Typographic Harmony (`text-wrap`)
*Typography · Baseline · 0 JS*

Prevents orphaned single words at heading line ends using text-wrap balance and pretty.

```css
h1, h2, h3, h4, .text-balance { text-wrap: balance; }
p, li, .text-pretty { text-wrap: pretty; }
```

### 53. Text-Box-Trim
*Typography · Newer · 0 JS*

Trims the font’s invisible leading above capitals and below the baseline. `padding: 1rem` is now exactly 1rem from the letter edges.

```css
.btn, .badge, .pill, .chip {
  text-box-trim: trim-both;
  text-box-edge: cap alphabetic;
  line-height: 1;
}
```

Use this relentlessly on every button, chip, and card heading. The fallback is invisible.

### 63. Smart Hyphenation
*Typography · Baseline · 0 JS*

Enables hyphenation for narrow columns and body copy for a specific language. Prevents both “rivers” and ugly orphan lines.

```css
:root { hyphens: auto; }

article p, article li {
  hyphens: auto;
  hyphenate-character: "\2010";  /* real hyphen instead of a minus */
  hyphenate-limit-chars: 8 4 4;  /* min 8 chars, 4 before the break, 4 after */
  hyphenate-limit-lines: 2;       /* max 2 hyphenated lines in a row */
  hyphenate-limit-last: always;   /* never hyphenate the last line of a paragraph */
}

html[lang="en"] body { hyphens: auto; }
```

Requires `<html lang="en">` (or the correct language) so hyphenation dictionaries can run.

---

## Forms & state

### 6. Focus Glow
*Forms · Baseline · 0 JS*

An animated halo glow on input focus that communicates active focus with soft elevation.

```css
input, textarea, select { min-block-size: 44px; }
input:focus-visible, textarea:focus-visible, select:focus-visible {
  outline: none;
  box-shadow:
    0 0 0 2px var(--color-bg),
    0 0 0 4px var(--color-primary),
    0 0 12px oklch(from var(--color-primary) l c h / 0.22);
}
```

### 16. Floating Labels
*Forms · Baseline · 0 JS*

Always use a real `<label>`. The placeholder trick never replaces the label semantically.

```css
.form-group { position: relative; }
.form-group input {
  width: 100%;
  padding: 1.4rem 1rem 0.55rem;
}
.form-group label {
  position: absolute;
  left: 1rem; top: 50%;
  transform: translateY(-50%);
  transform-origin: left top;
  pointer-events: none;
  transition: transform 220ms cubic-bezier(0.16,1,0.3,1), color 220ms cubic-bezier(0.16,1,0.3,1);
}
.form-group input:focus + label,
.form-group input:not(:placeholder-shown) + label {
  transform: translateY(-130%) scale(0.76);
  color: var(--color-primary);
}
```

### 23. Validation Whisper
*Forms · Baseline · 0 JS*

`:user-valid` / `:user-invalid` fire only after interaction, never on page load.

```css
input:user-invalid, textarea:user-invalid {
  border-color: var(--color-error);
  box-shadow: 0 0 0 3px oklch(from var(--color-error) l c h / .14);
}
input:user-valid, textarea:user-valid {
  border-color: var(--color-success);
}
```

### 28. Current Step Counter
*Forms · Baseline · 0 JS*

Wizard steps are numbered with CSS counters and no markup logic.

```css
.steps { counter-reset: step; }
.steps li::before {
  counter-increment: step;
  content: counter(step);
  inline-size: 1.75rem; block-size: 1.75rem;
  display: inline-grid; place-items: center;
  margin-right: .5rem;
  border-radius: 999px;
  background: var(--color-surface-offset);
}
```

### 32. Elastic Textarea (`field-sizing`)
*Forms · Baseline · 0 JS*

A textarea that grows with its content, with no JS listeners.

```css
textarea.auto-grow {
  field-sizing: content;
  min-block-size: 3lh;
  max-block-size: 12lh;
  resize: none;
}
```

### 54. Customizable Select (`appearance: base-select`)
*Forms · Progressive · 0 JS*

A native `<select>` becomes fully styleable, including the open menu. Retires headless libraries for standard dropdowns.

```css
@supports (appearance: base-select) {
  select.premium-dropdown {
    appearance: base-select;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: var(--space-2) var(--space-4);
  }

  select.premium-dropdown::picker(select) {
    background: oklch(from var(--color-bg) l c h / 0.92);
    backdrop-filter: blur(12px);
    border-radius: var(--radius-md);
    box-shadow: 0 12px 32px oklch(0 0 0 / 0.15);
    padding: var(--space-2);
  }

  select.premium-dropdown option:hover {
    background: var(--color-surface-offset);
    border-radius: var(--radius-sm);
  }
```

### 57. Form Gatekeeper
*Forms · Baseline · 0 JS*

A 0-JS state machine: submit stays locked until every field is valid. Invalid fields shake on blur.

```css
.checkout-form:has(input:user-invalid, textarea:user-invalid) button[type="submit"] {
  opacity: 0.5;
  pointer-events: none;
  filter: grayscale(100%);
}

.form-group:has(input:user-invalid:not(:focus)) {
  animation: error-shake 400ms cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
  color: var(--color-error);
}
@keyframes error-shake {
  20%, 80% { transform: translateX(2px); }
  40%, 60% { transform: translateX(-4px); }
}
```

### 76. Modern Wrapper Floating Label (`:has()`)
*Forms · Baseline · Markup*

A modernization of [Spell 16 (Floating Labels)](#16-floating-labels). Removes the requirement that `<label>` sit immediately after `<input>` in the DOM via the sibling combinator (`+`). Works with wrapping label containers.

```html
<div class="floating-field">
  <input id="email" type="email" placeholder=" " required>
  <label for="email">Email address</label>
</div>
```

```css
.floating-field {
  position: relative;
}

.floating-field input {
  width: 100%;
  padding: 1.4rem 1rem 0.55rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.floating-field label {
  position: absolute;
  left: 1rem; top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  transition: transform 200ms cubic-bezier(0.16, 1, 0.3, 1), color 200ms ease;
  color: var(--color-text-muted);
}

.floating-field:has(input:focus) label,
.floating-field:has(input:not(:placeholder-shown)) label {
  transform: translateY(-135%) scale(0.78);
  color: var(--color-primary);
}
```

### 85. 0-JS Multi-Step Wizard
*Forms · Baseline · Markup*

A complete multi-step wizard that switches steps, shows progress, and offers Back/Next — no script, driven by radio state and `:has()`.

```html
<form class="wizard">
  <input class="sr-only" type="radio" name="wstep" id="w-1" checked>
  <input class="sr-only" type="radio" name="wstep" id="w-2">
  <input class="sr-only" type="radio" name="wstep" id="w-3">

  <ol class="wz-steps" aria-label="Wizard steps">
    <li><label for="w-1">1 · Account</label></li>
    <li><label for="w-2">2 · Address</label></li>
    <li><label for="w-3">3 · Payment</label></li>
  </ol>

  <div class="wz-progress" aria-hidden="true"><span></span></div>

  <section class="wz-panel wz-1">
    <h2>Account</h2>
    <div class="wz-nav"><span></span><label class="btn" for="w-2">Next →</label></div>
  </section>
  <section class="wz-panel wz-2">
    <h2>Address</h2>
    <div class="wz-nav"><label class="btn ghost" for="w-1">← Back</label><label class="btn" for="w-3">Next →</label></div>
  </section>
  <section class="wz-panel wz-3">
    <h2>Payment</h2>
    <div class="wz-nav"><label class="btn ghost" for="w-2">← Back</label><button class="btn" type="submit">Finish</button></div>
  </section>
</form>
```

```css
.wizard .wz-panel { display: none; scroll-margin-block-start: max(6rem, var(--header-height, 0px)); }
.wizard:has(#w-1:checked) .wz-1,
.wizard:has(#w-2:checked) .wz-2,
.wizard:has(#w-3:checked) .wz-3 { display: block; animation: wz-in 300ms cubic-bezier(.16,1,.3,1); }
@keyframes wz-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }

.wz-steps { display: flex; gap: var(--space-2); list-style: none; padding: 0; }
.wz-steps label { display: inline-grid; place-items: center; min-block-size: 44px; padding-inline: .75rem;
  border-radius: 999px; cursor: pointer; color: var(--color-text-muted); }
.wizard:has(#w-1:checked) label[for="w-1"],
.wizard:has(#w-2:checked) label[for="w-2"],
.wizard:has(#w-3:checked) label[for="w-3"] { background: var(--color-primary); color: white; }

.wz-progress { block-size: 4px; background: var(--color-surface-offset); border-radius: 999px; margin-block: var(--space-4); overflow: hidden; }
.wz-progress span { display: block; block-size: 100%; background: var(--color-primary); inline-size: 33%;
  transition: inline-size 300ms cubic-bezier(.16,1,.3,1); }
.wizard:has(#w-2:checked) .wz-progress span { inline-size: 66%; }
.wizard:has(#w-3:checked) .wz-progress span { inline-size: 100%; }

.wz-nav { display: flex; justify-content: space-between; gap: var(--space-3); margin-block-start: var(--space-6); }
.btn { display: inline-grid; place-items: center; min-block-size: 44px; padding-inline: var(--space-4);
  border-radius: var(--radius-md); background: var(--color-primary); color: white; cursor: pointer; border: 0; text-decoration: none; }
.btn.ghost { background: transparent; color: var(--color-text); border: 1px solid var(--color-border); }
```

### 86. Themed Range Slider
*Forms · Baseline · 0 JS*

A native `<input type="range">` with a themed thumb and track — keeps built-in keyboard, step, and screen-reader semantics.

```html
<label class="range-field">
  <span>Volume</span>
  <input type="range" id="vol" min="0" max="100" value="60">
</label>
```

```css
.range-field { display: grid; gap: var(--space-2); }
:root { accent-color: var(--color-primary); }
input[type="range"] { inline-size: 100%; block-size: 44px; background: transparent; -webkit-appearance: none; appearance: none; }
input[type="range"]::-webkit-slider-runnable-track { block-size: 6px; border-radius: 999px; background: var(--color-surface-offset); }
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none; inline-size: 22px; block-size: 22px; border-radius: 50%;
  background: var(--color-primary); margin-block-start: -8px;
  box-shadow: 0 2px 6px oklch(0 0 0 / .2); transition: transform 150ms cubic-bezier(.16,1,.3,1);
}
input[type="range"]:active::-webkit-slider-thumb { transform: scale(1.15); }
input[type="range"]::-moz-range-track { block-size: 6px; border-radius: 999px; background: var(--color-surface-offset); }
input[type="range"]::-moz-range-progress { block-size: 6px; border-radius: 999px; background: var(--color-primary); }
input[type="range"]:focus-visible { outline: 2px solid var(--color-primary); outline-offset: 4px; border-radius: 999px; }
```

### 87. Group Error Summary (`:has(:user-invalid)`)
*Forms · Baseline · Markup*

An error summary at the top of a form group that appears only after a field is invalid following interaction.

```html
<fieldset class="field-group">
  <legend>Delivery</legend>
  <p class="group-error" role="alert">Some fields need fixing before you continue.</p>
  <input type="text" name="street" placeholder="Street address" required>
  <input type="text" name="zip" placeholder="Postal code" pattern="\d{5}" required>
</fieldset>
```

```css
.field-group { border: 1px solid var(--color-border); border-radius: var(--radius-md);
  padding: var(--space-4); display: grid; gap: var(--space-3); }
.group-error {
  display: none; padding: .65rem .85rem; border-radius: var(--radius-sm);
  background: oklch(from var(--color-error) l c h / .12); color: var(--color-error); font-weight: 500;
}
.field-group:has(:user-invalid) .group-error { display: block; animation: ge-in 250ms cubic-bezier(.16,1,.3,1); }
.field-group:has(:user-invalid) { border-color: var(--color-error); }
@keyframes ge-in { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: none; } }
```

---

## Shape & visual identity

### 25. Media Scrim Lift
*Visual · Baseline · 0 JS*

A media card gets a darker overlay on hover so the heading stays readable.

```css
.media-card { position: relative; overflow: hidden; }
.media-card::after {
  content: "";
  position: absolute; inset: 0;
  background: linear-gradient(to top, oklch(0 0 0 / .52), oklch(0 0 0 / .08));
  opacity: .5;
  transition: opacity 240ms cubic-bezier(0.16,1,0.3,1);
}
.media-card:hover::after,
.media-card:focus-within::after { opacity: 1; }
```

### 35. Inline Theme Switch (`light-dark()`)
*Visual · Baseline · 0 JS*

Native CSS color scheme switching without JavaScript or duplicate CSS rules.

```css
:root { color-scheme: light dark; }

.premium-card {
  background: light-dark(var(--color-surface), var(--color-surface-dark));
  color: light-dark(var(--color-text), var(--color-text-inverse));
  border: 1px solid light-dark(transparent, oklch(1 0 0 / 0.1));
}
```

### 51. Ribbon Cut Card (`shape()`)
*Visual · Newer · 0 JS*

Distinct notched or ribbon-shaped silhouettes via `shape()` in `clip-path`.

```css
.ribbon-card {
  clip-path: shape(
    from 0% 0%,
    line to 100% 0%,
    line to 100% 78%,
    line to 84% 100%,
    line to 0% 100%,
    close
  );
}
```

### 52. Organic Section Divider (`shape()`)
*Visual · Newer · 0 JS*

Responsive dividers between sections that feel editorial.

```css
.section-divider {
  block-size: 5rem;
  background: var(--color-surface);
  clip-path: shape(
    from 0% 45%,
    line to 18% 58%,
    line to 42% 32%,
    line to 68% 62%,
    line to 100% 40%,
    line to 100% 100%,
    line to 0% 100%,
    close
  );
}
```

### 58. Breathing Conic Border (`@property`)
*Visual · Baseline · 0 JS*

A color gradient that rotates along the card’s edge. Possible because `@property` allows typed interpolation of an `<angle>`.

```css
@property --border-angle {
  syntax: "<angle>";
  initial-value: 0turn;
  inherits: false;
}

.premium-glow-card {
  border: 2px solid transparent;
  background-clip: padding-box, border-box;
  background-origin: padding-box, border-box;
  background-image:
    linear-gradient(var(--color-surface), var(--color-surface)),
    conic-gradient(from var(--border-angle), transparent 60%, var(--color-primary), transparent 100%);
  animation: spin-border 4s linear infinite;
}

@keyframes spin-border {
  to { --border-angle: 1turn; }
}
```

### 64. Path Motion (`offset-path`)
*Visual · Baseline · 0 JS*

Animate an element along a curved path for decorative floating pieces (background shapes, dotted trails, orbiting icons).

```css
.floating-orb {
  inline-size: 12rem;
  block-size: 12rem;
  border-radius: 999px;
  background: radial-gradient(circle, var(--color-primary), transparent 70%);
  filter: blur(40px);
  opacity: .35;

  offset-path: path("M 0 0 C 200 100, 400 -100, 600 0 S 1000 100, 1200 0");
  offset-rotate: 0deg;
  animation: drift 18s linear infinite alternate;
}

@keyframes drift {
  to { offset-distance: 100%; }
}
```

### 74. Auto-Inverting Contrast Scrim (`mix-blend-mode`)
*Visual · Baseline · 0 JS*

Text or icons that automatically invert over the images or patterns behind them.

**WCAG warning:** Maximum contrast is guaranteed against black or white surfaces. Avoid 50% mid-grey backgrounds where a 4.5:1 contrast ratio cannot be guaranteed. Add `isolation: isolate` on the parent container so the blend mode does not leak to the whole page.

```css
.blend-container {
  isolation: isolate; /* Prevents leaking to the body */
}

.contrast-text {
  color: white;
  mix-blend-mode: difference;
  font-weight: 700;
}
```

### 78. Smooth Multiline Text Fade Mask (`mask-image`)
*Visual · Baseline · 0 JS*

Replaces the hard clip from `-webkit-line-clamp` with a soft faded alpha mask at the bottom of long text blocks.

```css
.text-fade-clamp {
  max-height: 9lh; /* Max 9 lines of text */
  overflow: hidden;
  mask-image: linear-gradient(to bottom, black 60%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, black 60%, transparent 100%);
}
```

---

## State detection with `:has`

### 13. Spotlight Focus
*State · Baseline · 0 JS*

The hovered card in a grid sharpens while its siblings recede.

```css
.card-grid { display: grid; gap: var(--space-4); }
.card-grid:has(.destination-card:hover) .destination-card:not(:hover),
.card-grid:has(.destination-card:focus-within) .destination-card:not(:focus-within) {
  opacity: 0.65;
  transform: scale(0.985);
}
.destination-card {
  transition: opacity 300ms cubic-bezier(0.16,1,0.3,1), transform 300ms cubic-bezier(0.16,1,0.3,1);
}
```

### 21. `:target` Highlight
*State · Baseline · 0 JS*

A deep-linked section gets a short highlight flash.

```css
section:target {
  animation: target-flash 1.2s ease-out;
}
@keyframes target-flash {
  0%   { box-shadow: 0 0 0 0 oklch(from var(--color-primary) l c h / .22); }
  100% { box-shadow: 0 0 0 18px oklch(from var(--color-primary) l c h / 0); }
}
```

### 29. Link Fade Neighbors
*State · Baseline · 0 JS*

In dense lists and footers the hovered link keeps focus while siblings fade.

```css
.link-cluster:has(a:hover) a:not(:hover),
.link-cluster:has(a:focus-visible) a:not(:focus-visible) { opacity: .55; }
.link-cluster a {
  min-block-size: 44px; display: inline-grid; align-items: center;
  transition: opacity 180ms ease;
}
```

### 59. Auto Empty State
*State · Baseline · 0 JS*

An empty container draws its own empty state with no JS condition.

```css
.data-grid { display: grid; gap: var(--space-4); }

.data-grid:empty::after,
.data-grid:not(:has(> *:not([hidden])))::after {
  content: "No results found.";
  display: block;
  grid-column: 1 / -1;
  padding: var(--space-8);
  text-align: center;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
}
```

### 60. Read More Toggle
*State · Baseline · Markup*

Classic “Read more” expansion with no JS, via a hidden checkbox and `:has`. Combine with Spell 33 for animated expansion.

**A11y-critical:** put the `.sr-only` class (from Base safeguards) on the checkbox — not the `hidden` attribute or `display: none`. That keeps the checkbox in the tab order and the accessibility tree so keyboard users can toggle it. The `:has(.clamp-toggle:focus-visible)` rule below paints a visible focus ring on the label.

```html
<div class="clamp-wrapper">
  <input type="checkbox" id="read-more" class="clamp-toggle sr-only">
  <p class="clamp-text">...long body copy...</p>
  <label for="read-more" class="clamp-label"></label>
</div>
```

```css
.clamp-text {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.clamp-wrapper:has(.clamp-toggle:checked) .clamp-text {
  -webkit-line-clamp: unset;
}

.clamp-label {
  cursor: pointer;
  color: var(--color-primary);
  font-weight: 600;
  min-block-size: 44px;
  display: inline-grid; align-items: center;
}
.clamp-label::after { content: " Read more →"; }
.clamp-wrapper:has(.clamp-toggle:checked) .clamp-label::after { content: " Show less"; }

/* Keyboard focus is visible on the label when the hidden checkbox is focused */
.clamp-wrapper:has(.clamp-toggle:focus-visible) .clamp-label {
  outline: 2px solid var(--color-primary);
  outline-offset: 4px;
  border-radius: var(--radius-sm);
}
```

---

## Performance

### 41. Content-Visibility Turbo
*Performance · Baseline · 0 JS*

The rendering engine skips layout for elements outside the viewport. A big win on long pages.

```css
.lazy-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 500px;
}
```

---

## Data visualization & tables

### 94. Sticky Header + Zebra Data Table
*Data · Baseline · 0 JS*

Long tables with a sticky header row, zebra stripes, and row highlight on hover/focus — the baseline for every data-dense SaaS view.

```html
<div class="table-scroller" tabindex="0" role="region" aria-label="Transactions">
  <table>
    <thead><tr><th>Date</th><th>Customer</th><th>Amount</th></tr></thead>
    <tbody>
      <tr><td>2026-08-01</td><td>Acme Inc</td><td>$12,400</td></tr>
      <tr><td>2026-08-02</td><td>Nordic Inc</td><td>$8,900</td></tr>
    </tbody>
  </table>
</div>
```

```css
.table-scroller { overflow: auto; max-block-size: 24rem; container-type: scroll-state;
  border: 1px solid var(--color-border); border-radius: var(--radius-md); }
.table-scroller table { inline-size: 100%; border-collapse: collapse; }
.table-scroller th, .table-scroller td { padding: .7rem .9rem; text-align: start; white-space: nowrap; }
.table-scroller thead th {
  position: sticky; top: 0; z-index: 2;
  background: var(--color-surface-offset); color: var(--color-text);
  box-shadow: inset 0 -1px 0 var(--color-border);
}
.table-scroller tbody tr:nth-child(even) { background: oklch(from var(--color-surface-offset) l c h / .4); }
.table-scroller tbody tr { transition: background 120ms ease; }
.table-scroller tbody tr:hover,
.table-scroller tbody tr:focus-within { background: oklch(from var(--color-primary) l c h / .08); }
```

### 95. CSS Sparkline / Bar Chart
*Data · Baseline · Markup*

A miniature bar chart driven by an inline `--v` custom property per bar — 0-JS data visualization for dashboards and KPI cards.

```html
<figure class="spark" role="img" aria-label="Sales by quarter: 34, 58, 41, 72, 66, 90 percent — rising trend">
  <span style="--v:34"></span><span style="--v:58"></span><span style="--v:41"></span>
  <span style="--v:72"></span><span style="--v:66"></span><span style="--v:90"></span>
</figure>
```

```css
.spark { display: flex; align-items: end; gap: 4px; block-size: 5rem; margin: 0; }
.spark span {
  flex: 1; min-block-size: 2px; border-radius: 3px 3px 0 0;
  background: color-mix(in oklch, var(--color-primary), transparent 25%);
  block-size: calc(var(--v, 0) * 1%);
  transition: background 160ms ease, block-size 400ms cubic-bezier(.16,1,.3,1);
}
.spark span:last-child { background: var(--color-primary); }
.spark:hover span { background: var(--color-primary); }
```

### 96. Themed `<progress>` & `<meter>`
*Data · Baseline · 0 JS*

Native `<progress>`/`<meter>` with brand colors — keeps built-in semantics, min/max logic, and screen-reader support for storage, quotas, and goals.

```html
<label class="prog-field">
  <span>Storage <output>72%</output></span>
  <progress max="100" value="72">72%</progress>
</label>
```

```css
.prog-field { display: grid; gap: var(--space-2); }
:root { accent-color: var(--color-primary); }
progress { inline-size: 100%; block-size: .6rem; border: 0; border-radius: 999px;
  background: var(--color-surface-offset); overflow: hidden; }
progress::-webkit-progress-bar { background: var(--color-surface-offset); border-radius: 999px; }
progress::-webkit-progress-value { background: var(--color-primary); border-radius: 999px;
  transition: inline-size 400ms cubic-bezier(.16,1,.3,1); }
progress::-moz-progress-bar { background: var(--color-primary); border-radius: 999px; }
```

---

## Navigation (2026)

### 97. Invoker Command Drawer (`commandfor` + `closedby`)
*Navigation · Newer · Markup*

An off-canvas menu as a native `<dialog>` — opened and closed with Invoker Commands, light-dismissed via `closedby="any"`. No `showModal()`, no click-outside listener.

```html
<button class="nav-open" commandfor="site-drawer" command="show-modal" aria-label="Open menu">
  Menu
</button>

<dialog id="site-drawer" class="nav-drawer" closedby="any">
  <form method="dialog">
    <button class="nav-close" commandfor="site-drawer" command="close" aria-label="Close menu">✕</button>
  </form>
  <nav aria-label="Mobile navigation">
    <a href="/">Home</a>
    <a href="/services">Services</a>
    <a href="/contact">Contact</a>
  </nav>
</dialog>
```

```css
.nav-open, .nav-close, .nav-drawer a {
  min-block-size: 44px; min-inline-size: 44px;
  display: inline-grid; place-items: center; align-content: center;
}
.nav-drawer {
  margin: 0; inset: 0 auto 0 0;
  inline-size: min(22rem, 92vw); block-size: 100dvh;
  border: 0; padding: var(--space-6);
  background: var(--color-bg);
  transform: translateX(-100%);
  transition: transform 280ms cubic-bezier(.16,1,.3,1),
              display 280ms allow-discrete, overlay 280ms allow-discrete;
}
.nav-drawer[open], .nav-drawer:open { transform: translateX(0); }
@starting-style { .nav-drawer[open], .nav-drawer:open { transform: translateX(-100%); } }
.nav-drawer::backdrop {
  background: oklch(0 0 0 / .4);
  opacity: 0;
  transition: opacity 280ms ease, display 280ms allow-discrete, overlay 280ms allow-discrete;
}
.nav-drawer[open]::backdrop, .nav-drawer:open::backdrop { opacity: 1; }
@starting-style { .nav-drawer[open]::backdrop, .nav-drawer:open::backdrop { opacity: 0; } }
.nav-drawer nav { display: grid; gap: .25rem; margin-block-start: var(--space-6); }
.nav-drawer a {
  justify-content: start; padding-inline: var(--space-3);
  border-radius: var(--radius-sm); color: var(--color-text); text-decoration: none;
}
.nav-drawer a:hover, .nav-drawer a:focus-visible { background: var(--color-surface-offset); }
```

### 98. Interest-Hint Tooltip (`interestfor` + `popover="hint"`)
*Navigation · Progressive · Markup · → modernizes 18 / 34*

A hover, focus, and long-press tooltip with no `mouseenter`. `popover="hint"` does not close open `auto` menus. The browser sets implicit `aria-describedby` — do not add `role="tooltip"` yourself.

```html
<button type="button" class="icon-btn" interestfor="tip-save" aria-label="Save">★</button>
<div id="tip-save" popover="hint" class="hint-tip">Save to your list</div>
```

```css
.icon-btn {
  anchor-name: --tip-save;
  interest-delay: 400ms 180ms;
  inline-size: 44px; block-size: 44px; min-inline-size: 44px; min-block-size: 44px;
  border-radius: var(--radius-sm); border: 1px solid var(--color-border);
  background: var(--color-bg); cursor: pointer;
}
.icon-btn:interest-source { border-color: var(--color-primary); }
.hint-tip {
  margin: 0; inset: auto;
  position-anchor: --tip-save;
  position-area: top;
  margin-block-end: .4rem;
  position-try-fallbacks: flip-block;
  position-visibility: anchors-visible;
  padding: .4rem .7rem; border-radius: var(--radius-sm);
  background: var(--color-text); color: var(--color-bg); font-size: .85rem;
  opacity: 0; transform: translateY(4px);
  transition: opacity 160ms ease, transform 160ms cubic-bezier(.16,1,.3,1),
              display 160ms allow-discrete, overlay 160ms allow-discrete;
}
.hint-tip:popover-open { opacity: 1; transform: none; }
@starting-style { .hint-tip:popover-open { opacity: 0; transform: translateY(4px); } }
@media (hover: none) {
  .icon-btn { interest-delay-start: 0ms; }
}
```

### 99. Scroll-Initial-Target Carousel
*Navigation · Progressive · Markup*

Deep-link a scroll-snap carousel to a specific slide on first render — no `scrollIntoView()`. The first element with `scroll-initial-target: nearest` in tree order wins.

```html
<div class="init-carousel">
  <article class="slide" id="q1">Q1</article>
  <article class="slide is-initial" id="q2">Q2 — current</article>
  <article class="slide" id="q3">Q3</article>
</div>
```

```css
.init-carousel {
  display: flex; gap: var(--space-4);
  overflow-x: auto; scroll-snap-type: x mandatory;
  overscroll-behavior-x: contain;
}
.init-carousel .slide {
  flex: 0 0 min(28rem, 88vw);
  scroll-snap-align: center;
  min-block-size: 12rem;
  border-radius: var(--radius-md);
  padding: var(--space-5);
  background: var(--color-surface);
}
.init-carousel .slide.is-initial,
.init-carousel .slide:target {
  scroll-initial-target: nearest;
}
```

---

## Cards & Grids (2026)

### 100. Grid Lanes Masonry (`display: grid-lanes`)
*Cards · Progressive · 0 JS*

Pinterest packing in CSS. `display: grid-lanes` fills the shortest column in DOM order (correct reading order, unlike `column-count`). Fallback is a regular grid.

```html
<ul class="lanes">
  <li><article class="card">Card 1</article></li>
  <li><article class="card">Card 2 with more text</article></li>
  <li><article class="card">Card 3</article></li>
</ul>
```

```css
.lanes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr));
  gap: var(--space-4);
  align-items: start;
  list-style: none; padding: 0; margin: 0;
}
@supports (display: grid-lanes) {
  .lanes {
    display: grid-lanes;
    grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr));
  }
```

### 101. Sibling-Index Stagger (`sibling-index()`)
*Cards · Progressive · 0 JS*

A staggered reveal with no `--i` custom properties. `sibling-index()` (1-based) and `sibling-count()` are CSS Values 5 tree-counting functions.

```html
<ul class="stagger">
  <li>Analytics</li><li>Automation</li><li>API</li><li>Support</li>
</ul>
```

```css
@supports (animation-delay: calc(sibling-index() * 1ms)) {
  .stagger > * {
    animation: stagger-in 420ms cubic-bezier(.16,1,.3,1) both;
    animation-delay: calc((sibling-index() - 1) * 70ms);
  }
  @keyframes stagger-in {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: none; }
  }
@media (prefers-reduced-motion: reduce) {
  .stagger > * { animation: none; }
}
```

---

## Forms (2026)

### 102. `:open` Custom Select Chrome
*Forms · Newer · 0 JS*

Style a native `<select>` while the picker is open with Baseline 2026 `:open`. Combine with Spell 54 (`appearance: base-select`).

```html
<label class="select-field">
  <span>Industry</span>
  <select class="premium-dropdown" name="industry">
    <option>Construction</option>
    <option>Plumbing</option>
    <option>Electrical</option>
  </select>
</label>
```

```css
.select-field { display: grid; gap: var(--space-2); }
.select-field select {
  min-block-size: 44px;
  inline-size: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding-inline: var(--space-3);
  background: var(--color-surface);
  transition: border-color 160ms ease, box-shadow 160ms ease;
}
select:open, select:focus-visible {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px oklch(from var(--color-primary) l c h / .16);
}
```

### 103. Contrast-Safe Chips (`contrast-color()`)
*Forms · Progressive · 0 JS*

Automatic black/white text against a dynamic background. `contrast-color()` returns black or white — wrap it in `@supports` and provide a manual fallback.

```html
<span class="chip" style="--chip-bg: var(--color-primary)">New</span>
<span class="chip" style="--chip-bg: var(--color-accent)">Sale</span>
```

```css
.chip {
  display: inline-grid; place-items: center;
  min-block-size: 44px; padding-inline: .85rem;
  border-radius: 999px;
  background: var(--chip-bg, var(--color-primary));
  color: var(--color-bg);
  font-weight: 600;
}
@supports (color: contrast-color(red)) {
  .chip { color: contrast-color(var(--chip-bg, var(--color-primary))); }
}
```

### 104. `if()` Inline Theme Tokens
*Forms · Progressive · 0 JS*

Conditional values in the property value itself — media, style query, and supports — with no extra classes. `if()` applies to the element itself (unlike `@container style()`, which queries a parent).

```css
.saas-card {
  padding: if(media(width < 40rem): var(--space-4); else: var(--space-6););
  background: if(
    style(--scheme: dark): var(--color-surface-dark);
    else: var(--color-surface);
  );
  color: if(
    style(--scheme: dark): var(--color-text-inverse);
    else: var(--color-text);
  );
  border-radius: var(--radius-md);
}
```

### 105. Typed `attr()` Field Meter
*Forms · Progressive · Markup*

Read `data-value` as a `<number>` and drive a meter with no inline `--v` or JS. Feature-detect with `attr(x type(*))`.

```html
<div class="attr-meter" data-value="72" aria-label="Profile complete to 72 percent">
  <span class="attr-meter-fill"></span>
</div>
```

```css
.attr-meter {
  block-size: .6rem; border-radius: 999px;
  background: var(--color-surface-offset); overflow: hidden;
}
.attr-meter-fill {
  display: block; block-size: 100%;
  background: var(--color-primary); border-radius: inherit;
  inline-size: 0%;
}
@supports (x: attr(x type(*))) {
  .attr-meter-fill {
    inline-size: calc(attr(data-value type(<number>), 0) * 1%);
  }
```

---

## Overlays & Modals (2026)

### 106. Light-Dismiss Confirm Dialog (`closedby="any"`)
*Overlays · Newer · Markup*

A confirm dialog that closes on Escape *and* backdrop click. Opened with `command="show-modal"`. `closedby="closerequest"` is Escape-only; `"none"` requires an explicit close button.

```html
<button class="btn" commandfor="confirm-delete" command="show-modal">Delete customer</button>

<dialog id="confirm-delete" class="confirm" closedby="any">
  <h2>Delete customer?</h2>
  <p>This cannot be undone.</p>
  <div class="confirm-actions">
    <button class="btn ghost" commandfor="confirm-delete" command="close">Cancel</button>
    <button class="btn danger" commandfor="confirm-delete" command="close">Delete</button>
  </div>
</dialog>
```

```css
.confirm {
  margin: auto; border: 0; padding: var(--space-6);
  max-inline-size: 28rem; border-radius: var(--radius-lg);
  background: var(--color-bg);
  box-shadow: 0 24px 60px oklch(0 0 0 / .22);
  opacity: 0; transform: scale(.96);
  transition: opacity 220ms cubic-bezier(.16,1,.3,1), transform 220ms cubic-bezier(.16,1,.3,1),
              display 220ms allow-discrete, overlay 220ms allow-discrete;
}
.confirm[open], .confirm:open { opacity: 1; transform: none; }
@starting-style { .confirm[open], .confirm:open { opacity: 0; transform: scale(.96); } }
.confirm-actions { display: flex; justify-content: end; gap: var(--space-3); margin-block-start: var(--space-5); }
.confirm-actions .btn, .btn { min-block-size: 44px; }
.btn.danger { background: var(--color-error); color: white; }
```

### 107. Position-Visibility Auto-Hide (`position-visibility`)
*Overlays · Newer · 0 JS*

Hide an anchor-positioned element when the trigger scrolls out of view (`anchors-visible`) or when the overlay itself overflows (`no-overflow`). Baseline 2026.

```css
.filter-panel {
  position: absolute;
  position-anchor: --filter-btn;
  position-area: bottom end;
  position-try-fallbacks: flip-inline, flip-block;
  position-visibility: anchors-visible;
}
```

Use `no-overflow` when the overlay itself must not leave the viewport. Fallback without support: the panel stays visible as usual.

---

## Media (2026)

### 108. Find-in-Page Accordion (`hidden="until-found"`)
*Media · Newer · Markup*

A collapsed FAQ that still matches the browser's Find in page and fragment links. The browser removes `hidden` and scrolls to the hit. Requires a box (not `display: none` / `contents` / `inline`).

```html
<section class="faq-item">
  <a href="#vat-answer">Jump to the VAT answer</a>
  <h2>Is VAT included?</h2>
  <div id="vat-answer" class="faq-answer" hidden="until-found">
    <p>Yes. Every price on the site includes VAT unless stated otherwise.</p>
  </div>
</section>
```

```css
.faq-answer {
  display: block;
  border-inline-start: 3px solid var(--color-primary);
  padding-inline-start: var(--space-4);
  margin-block: var(--space-3);
}
.faq-item a {
  min-block-size: 44px; display: inline-grid; align-items: center;
}
```

### 109. Named View-Transition Cards (`view-transition-class` + typed `attr()`)
*Media · Progressive · 0 JS*

A shared-element transition between a list card and a detail page. `view-transition-name` is read from `id` as a `<custom-ident>`; `view-transition-class` groups the animation.

```html
<article class="vt-card" id="case-acme">…</article>
```

```css
@supports (view-transition-name: none) {
  @view-transition { navigation: auto; }
}
@supports (x: attr(x type(*))) {
  .vt-card {
    view-transition-name: attr(id type(<custom-ident>), none);
    view-transition-class: card;
  }
::view-transition-group(*.card) {
  animation-duration: 320ms;
  animation-timing-function: cubic-bezier(.16,1,.3,1);
}
@media (prefers-reduced-motion: reduce) {
  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) { animation: none !important; }
}
```

---

## Data Visualization (2026)

### 110. Typed `attr()` Sparkline
*Data · Progressive · Markup · → modernizes 95*

The same sparkline as Spell 95, but the value lives in `data-v` — no inline `style="--v:…"`.

```html
<figure class="attr-spark" role="img" aria-label="Sales: 34, 58, 41, 72, 66, 90 percent">
  <span data-v="34"></span><span data-v="58"></span><span data-v="41"></span>
  <span data-v="72"></span><span data-v="66"></span><span data-v="90"></span>
</figure>
```

```css
.attr-spark { display: flex; align-items: end; gap: 4px; block-size: 5rem; margin: 0; }
.attr-spark span {
  flex: 1; min-block-size: 2px; border-radius: 3px 3px 0 0;
  background: color-mix(in oklch, var(--color-primary), transparent 25%);
}
@supports (x: attr(x type(*))) {
  .attr-spark span {
    block-size: calc(attr(data-v type(<number>), 0) * 1%);
  }
.attr-spark span:last-child { background: var(--color-primary); }
```

### 111. View-Timeline KPI Fill
*Data · Progressive · 0 JS*

KPI bars fill as they enter the viewport via `animation-timeline: view()` — no IntersectionObserver.

```html
<div class="kpi" style="--kpi: 72%">
  <span>Conversion</span>
  <div class="kpi-track" aria-hidden="true"><i></i></div>
</div>
```

```css
.kpi-track {
  block-size: .6rem; border-radius: 999px;
  background: var(--color-surface-offset); overflow: hidden;
}
.kpi-track i {
  display: block; block-size: 100%; inline-size: 0;
  background: var(--color-primary); border-radius: inherit;
}
@supports (animation-timeline: view()) {
  .kpi-track i {
    animation: kpi-fill linear both;
    animation-timeline: view();
    animation-range: entry 10% entry 60%;
  }
  @keyframes kpi-fill { to { inline-size: var(--kpi, 0%); } }
}
@media (prefers-reduced-motion: reduce) {
  .kpi-track i { inline-size: var(--kpi, 0%); animation: none; }
}
```

---

## Typography & Layout (2026)

### 112. `::target-text` Share Highlight
*Typography · Newer · 0 JS*

Style text-fragment highlights from shared URLs (`#:~:text=`). Visible when someone lands via a marked link.

```css
::target-text {
  background: oklch(from var(--color-primary) l c h / .28);
  color: var(--color-text);
  text-decoration: underline;
  text-decoration-thickness: 2px;
}
```

### 113. Reading-Flow Grid (`reading-flow`)
*Layout · Progressive · 0 JS*

When grid items are repacked with `dense` or explicit `order`, Tab and screen readers should follow the *visual* row order, not the DOM order.

```css
.pack-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr));
  grid-auto-flow: dense;
  gap: var(--space-4);
}
@supports (reading-flow: grid-rows) {
  .pack-grid { reading-flow: grid-rows; }
}
```

`flex-visual` / `flex-flow` for flex; `grid-columns` if column order is the semantically correct one.

### 114. Themed Scrollbars (`scrollbar-color`)
*Layout · Baseline · 0 JS*

Branded scrollbars with standard properties. Use `scrollbar-width: thin` on embedded panels; keep `auto` on `html` for discoverability.

```css
html {
  scrollbar-color: var(--color-primary) var(--color-surface-offset);
  scrollbar-width: auto;
}
.table-scroller, .drawer-body, .prose pre {
  scrollbar-color: color-mix(in oklch, var(--color-primary), transparent 35%)
                   var(--color-surface-offset);
  scrollbar-width: thin;
}
```

---

## State & Shell (2026)

### 115. File Dropzone State (`::file-selector-button`)
*Forms · Baseline · Markup*

A 0-JS dropzone around a native file input. The whole zone is the hit target; the button is 44px.

```html
<label class="dropzone">
  <input type="file" name="brief" accept=".pdf,.docx">
  <span>Drop a brief or choose a file</span>
</label>
```

```css
.dropzone {
  display: grid; place-items: center; gap: var(--space-3);
  min-block-size: 10rem;
  padding: var(--space-6);
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  cursor: pointer;
  transition: border-color 160ms ease, background 160ms ease;
}
.dropzone:focus-within,
.dropzone:has(:focus-visible) {
  border-color: var(--color-primary);
  background: oklch(from var(--color-primary) l c h / .06);
}
.dropzone input[type="file"] { inline-size: 100%; }
.dropzone input[type="file"]::file-selector-button {
  min-block-size: 44px; min-inline-size: 44px;
  margin-inline-end: var(--space-3);
  padding-inline: var(--space-4);
  border: 0; border-radius: var(--radius-md);
  background: var(--color-primary); color: white; cursor: pointer;
}
```

### 116. Checkbox Theme Switch (`:has()` + `color-scheme`)
*Visual · Baseline · Markup*

A declarative light/dark switch with no JS. The checkbox sets `color-scheme` on `:root` via `:has()`; `light-dark()` (Spell 35) follows along.

```html
<label class="theme-switch">
  <input type="checkbox" class="sr-only" name="dark" id="theme-dark">
  <span class="theme-ui" aria-hidden="true"></span>
  Dark mode
</label>
```

```css
:root:has(#theme-dark:checked) { color-scheme: dark; }
:root:not(:has(#theme-dark:checked)) { color-scheme: light; }
.theme-switch {
  display: inline-flex; align-items: center; gap: .6rem;
  min-block-size: 44px; cursor: pointer;
}
.theme-ui {
  inline-size: 44px; block-size: 24px; border-radius: 999px;
  background: var(--color-surface-offset);
  position: relative;
}
.theme-ui::after {
  content: ""; position: absolute; inset-block: 3px; inset-inline-start: 3px;
  inline-size: 18px; block-size: 18px; border-radius: 50%;
  background: var(--color-bg);
  transition: translate 180ms cubic-bezier(.16,1,.3,1);
}
:root:has(#theme-dark:checked) .theme-ui { background: var(--color-primary); }
:root:has(#theme-dark:checked) .theme-ui::after { translate: 20px 0; }
.theme-switch:has(:focus-visible) .theme-ui {
  outline: 2px solid var(--color-primary); outline-offset: 3px;
}
```

### 117. Split Action Button (`commandfor`)
*Overlays · Newer · Markup*

A primary action plus overflow menu in the same control. The menu is `[popover=auto]` pinned with anchor positioning.

```html
<div class="split">
  <a class="split-main" href="/quote">Request quote</a>
  <button class="split-more" commandfor="split-menu" command="toggle-popover" aria-label="More actions">▾</button>
  <div id="split-menu" popover="auto" class="split-menu">
    <a href="/quote?plan=pro">Pro quote</a>
    <a href="/contact">Talk to sales</a>
  </div>
```

```css
.split { display: inline-flex; position: relative; anchor-scope: --split; }
.split-main, .split-more {
  min-block-size: 44px; display: inline-grid; place-items: center;
  background: var(--color-primary); color: white; border: 0;
  text-decoration: none; cursor: pointer;
}
.split-main { padding-inline: var(--space-4); border-radius: var(--radius-md) 0 0 var(--radius-md); }
.split-more {
  anchor-name: --split;
  min-inline-size: 44px;
  border-inline-start: 1px solid oklch(1 0 0 / .25);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
}
.split-menu {
  margin: 0; inset: auto;
  position-anchor: --split; position-area: bottom end;
  margin-block-start: .35rem;
  position-try-fallbacks: flip-inline, flip-block;
  position-visibility: anchors-visible;
  min-inline-size: 12rem; padding: var(--space-2);
  background: var(--color-bg); border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: 0 16px 40px oklch(0 0 0 / .14);
}
.split-menu a {
  display: grid; align-items: center; min-block-size: 44px;
  padding-inline: .75rem; border-radius: var(--radius-sm);
  color: var(--color-text); text-decoration: none;
}
.split-menu a:hover, .split-menu a:focus-visible { background: var(--color-surface-offset); }
```

### 118. Customizable Select Checkmark (`::checkmark` + `::picker-icon`)
*Forms · Progressive · 0 JS*

Full native select chrome: a custom chevron (`::picker-icon`) and a checkmark on the selected option (`::checkmark`). Requires `appearance: base-select` (Spell 54).

```css
@supports (appearance: base-select) {
  select.premium-dropdown {
    appearance: base-select;
    min-block-size: 44px;
  }
  select.premium-dropdown::picker-icon {
    content: "▾";
    color: var(--color-text-muted);
    transition: transform 180ms cubic-bezier(.16,1,.3,1);
  }
  select.premium-dropdown:open::picker-icon { transform: rotate(180deg); }
  select.premium-dropdown option {
    min-block-size: 44px;
    display: flex; align-items: center; gap: .5rem;
    padding-inline: .75rem;
  }
  select.premium-dropdown option::checkmark {
    content: "✓";
    color: var(--color-primary);
    font-weight: 700;
  }
```


### 119. Native Donut Chart (`conic-gradient` + `mask-image`)
*Data · Baseline · 0 JS*

Draws a donut chart via `conic-gradient` with the center cut out by `mask-image`. 

```html
<div class="donut-chart" role="img" aria-label="Split: 65% Core, 20% Admin, 15% R&D" style="--p1: 65; --p2: 20;">
  <span class="donut-center">100%</span>
</div>
```

```css
.donut-chart {
  inline-size: 12rem; block-size: 12rem;
  border-radius: 50%;
  background: conic-gradient(
    var(--color-primary) 0% calc(var(--p1, 0) * 1%),
    var(--color-accent, oklch(.7 .2 50)) calc(var(--p1, 0) * 1%) calc((var(--p1, 0) + var(--p2, 0)) * 1%),
    var(--color-surface-offset) calc((var(--p1, 0) + var(--p2, 0)) * 1%) 100%
  );
  mask-image: radial-gradient(circle, transparent 58%, black 60%);
  -webkit-mask-image: radial-gradient(circle, transparent 58%, black 60%);
  display: grid; place-items: center;
}
.donut-center { font-weight: 700; font-size: 1.5rem; color: var(--color-text); }
```

### 120. Faceted Category Filter Matrix (`:has()`)
*State · Baseline · Markup*

A card gallery that filters visible items from checked boxes, with no JavaScript.

```html
<div class="filter-matrix-wrap">
  <div class="filter-controls">
    <label class="filter-chip"><input type="checkbox" id="f-tech" checked><span>Tech</span></label>
    <label class="filter-chip"><input type="checkbox" id="f-design"><span>Design</span></label>
  </div>

  <div class="card-matrix">
    <article class="matrix-card" data-cat="tech">Tech project</article>
    <article class="matrix-card" data-cat="design">Design project</article>
  </div>
```

```css
.filter-controls { display: flex; gap: var(--space-2); margin-block-end: var(--space-4); }
.filter-chip { display: inline-grid; place-items: center; min-block-size: 44px; padding-inline: 1rem; cursor: pointer; border-radius: 999px; border: 1px solid var(--color-border); }
.filter-chip input { position: absolute; opacity: 0; pointer-events: none; }
.filter-chip:has(input:checked) { background: var(--color-primary); color: white; border-color: var(--color-primary); }
.filter-chip:has(input:focus-visible) { outline: 2px solid var(--color-primary); outline-offset: 2px; }

.card-matrix:has(#f-tech:not(:checked)) .matrix-card[data-cat="tech"],
.card-matrix:has(#f-design:not(:checked)) .matrix-card[data-cat="design"] {
  display: none;
}
```

### 121. 0-JS Global Cart Counter & Badge (`counter` + Anchor)
*State · Baseline · Markup*

Increments a CSS counter when products are checked, and anchors the badge to the header icon.

```html
<header>
  <button id="cart-icon" class="cart-btn" aria-label="Cart">🛒</button>
</header>
<main class="cart-shop">
  <label class="btn"><input type="checkbox" class="add-to-cart sr-only"> Buy Product A</label>
</main>
<div class="cart-badge-wrap">
  <span class="cart-badge" aria-hidden="true"></span>
</div>
```

```css
body { counter-reset: cart-total; }
.add-to-cart:checked { counter-increment: cart-total; }

#cart-icon { anchor-name: --cart-anchor; min-block-size: 44px; min-inline-size: 44px; }
.cart-badge-wrap {
  position: absolute; position-anchor: --cart-anchor; position-area: top end;
  margin-block-start: -0.5rem; margin-inline-end: -0.5rem; pointer-events: none;
}
.cart-badge {
  display: inline-grid; place-items: center; min-inline-size: 1.5rem; block-size: 1.5rem;
  background: var(--color-error); color: white; border-radius: 999px;
  font-size: 0.75rem; font-weight: 700; opacity: 0; transform: scale(0.5);
  transition: opacity 240ms ease, transform 240ms cubic-bezier(.16,1,.3,1);
}
body:has(.add-to-cart:checked) .cart-badge { opacity: 1; transform: scale(1); }
.cart-badge::after { content: counter(cart-total); }
```

### 122. CSS Gantt Schedule Grid (`grid-template-columns`)
*Data · Baseline · Markup*

Project planning and a timeline schedule driven by CSS Grid and custom properties.

```html
<figure class="gantt" role="region" aria-label="Project timeline">
  <div class="gantt-row" style="--start: 1; --span: 3;"><span>Research</span></div>
  <div class="gantt-row" style="--start: 3; --span: 5;"><span>Development</span></div>
</figure>
```

```css
.gantt {
  display: grid; grid-template-columns: repeat(12, 1fr);
  gap: var(--space-2); padding: var(--space-4);
  background: var(--color-surface); border-radius: var(--radius-md);
}
.gantt-row {
  grid-column: var(--start, 1) / span var(--span, 1);
  min-block-size: 44px; padding-inline: .75rem;
  background: var(--color-primary); color: white;
  border-radius: var(--radius-sm); font-weight: 600;
  display: flex; align-items: center;
}
```

### 123. Matrix Heatmap (`color-mix()` + `oklch()`)
*Data · Baseline · Markup*

An activity calendar where each cell’s color intensity is computed proportionally with `color-mix()`.

```html
<div class="heatmap-grid" role="img" aria-label="Activity matrix">
  <div class="cell" style="--val: 10" title="10 events"></div>
  <div class="cell" style="--val: 85" title="85 events"></div>
</div>
```

```css
.heatmap-grid { display: flex; flex-wrap: wrap; gap: 4px; }
.cell {
  inline-size: 2.75rem; block-size: 2.75rem; border-radius: 4px;
  background: color-mix(in oklch, var(--color-primary) calc(var(--val, 0) * 1%), var(--color-surface-offset));
  transition: transform 150ms ease;
}
.cell:hover { transform: scale(1.2); z-index: 2; box-shadow: 0 4px 12px oklch(0 0 0 / .2); }
```

### 124. Stacked KPI Segment Bar (`flex` + `color-mix()`)
*Data · Baseline · Markup*

A horizontal stacked bar whose segments size themselves from their weights.

```html
<figure class="stack-bar" role="img" aria-label="Split: 40% Ops, 60% Sales">
  <div class="stack-seg" style="--v: 40; --bg: var(--color-primary)">40%</div>
  <div class="stack-seg" style="--v: 60; --bg: var(--color-accent)">60%</div>
</figure>
```

```css
.stack-bar { display: flex; block-size: 2.75rem; border-radius: 999px; overflow: hidden; gap: 2px; margin: 0; }
.stack-seg {
  flex-basis: calc(var(--v, 0) * 1%);
  display: grid; place-items: center; color: white;
  font-size: .85rem; font-weight: 700; background: var(--bg);
  min-inline-size: 2ch;
}
```

### 125. Inline SVG Line Chart (0-JS Draw & Fill)
*Data · Newer · Markup*

An SVG line chart with a scroll-driven draw animation via `stroke-dasharray`.

```html
<figure class="line-chart-wrap" role="img" aria-label="Sales trend Q1–Q4">
  <svg viewBox="0 0 300 100" class="line-chart-svg">
    <path class="line-path" d="M0,80 L75,50 L150,65 L225,20 L300,10" />
  </svg>
</figure>
```

```css
.line-chart-wrap { inline-size: 100%; block-size: 8rem; margin: 0; }
.line-chart-svg { inline-size: 100%; block-size: 100%; overflow: visible; }
.line-path {
  fill: none; stroke: var(--color-primary); stroke-width: 3;
  stroke-dasharray: 1000; stroke-dashoffset: 1000;
  stroke-linecap: round;
}
@supports (animation-timeline: view()) {
  .line-path {
    animation: draw-line linear both;
    animation-timeline: view();
    animation-range: entry 20% entry 80%;
  }
  @keyframes draw-line { to { stroke-dashoffset: 0; } }
}
```

### 126. Section-Spy Active Navigation (`timeline-scope`)
*Navigation · Progressive · 0 JS*

Sidebar links light up based on which section is in view.

```html
<nav class="spy-nav">
  <a href="#s1" class="spy-l1">Intro</a>
  <a href="#s2" class="spy-l2">Features</a>
</nav>
<main>
  <section id="s1">Intro</section>
  <section id="s2">Features</section>
</main>
```

```css
html { timeline-scope: --time-s1, --time-s2; }
#s1 { view-timeline-name: --time-s1; }
#s2 { view-timeline-name: --time-s2; }

.spy-nav a { min-block-size: 44px; display: inline-grid; place-items: center; color: var(--color-text-muted); }

@supports (animation-timeline: view()) {
  .spy-l1 { animation: spy-act linear both; animation-timeline: --time-s1; animation-range: entry 50% exit 50%; }
  .spy-l2 { animation: spy-act linear both; animation-timeline: --time-s2; animation-range: entry 50% exit 50%; }
  @keyframes spy-act { 10%, 90% { color: var(--color-primary); font-weight: 700; } }
}
```

### 127. Nested Cascade Popovers (`popover="auto"` + Anchor)
*Navigation · Newer · Markup*

Multi-level cascade menus whose light-dismiss is handled automatically by the browser.

```html
<button commandfor="m-main" command="toggle-popover" class="btn">Export ▾</button>

<div id="m-main" popover="auto" class="menu-l1">
  <button commandfor="m-sub" command="show-popover" id="b-sub" class="sub-trig">As file ▸</button>
  <div id="m-sub" popover="auto" class="menu-l2">
    <button>PDF</button>
    <button>CSV</button>
  </div>
```

```css
.menu-l1, .menu-l2 {
  margin: 0; padding: var(--space-2); background: var(--color-bg);
  border: 1px solid var(--color-border); border-radius: var(--radius-md);
  box-shadow: 0 12px 32px oklch(0 0 0 / .14);
}
.sub-trig { anchor-name: --sub-btn; inline-size: 100%; text-align: start; min-block-size: 44px; }
.menu-l2 {
  inset: auto; position-anchor: --sub-btn; position-area: right span-bottom;
  position-try-options: flip-inline, flip-block; margin-inline-start: var(--space-1);
}
.menu-l1 button, .menu-l2 button { min-block-size: 44px; inline-size: 100%; border: 0; background: none; cursor: pointer; }
```

### 128. 0-JS Password Strength Meter (`pattern` + `:valid` + `:has()`)
*Forms · Baseline · Markup*

Evaluates password strength dynamically via HTML regex and drives the meter with `:has()`.

```html
<div class="pwd-wrap">
  <input type="password" class="pwd-input" placeholder="At least 8 chars, a number & a capital" 
         pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}" required>
  <div class="pwd-meter" aria-hidden="true"><span></span></div>
</div>
```

```css
.pwd-wrap { display: grid; gap: var(--space-2); }
.pwd-input { min-block-size: 44px; padding-inline: 1rem; border: 1px solid var(--color-border); border-radius: var(--radius-md); }
.pwd-meter { block-size: 6px; background: var(--color-surface-offset); border-radius: 999px; overflow: hidden; }
.pwd-meter span { display: block; block-size: 100%; inline-size: 0; transition: inline-size 300ms ease, background 300ms ease; }

.pwd-wrap:has(input:not(:placeholder-shown):invalid) .pwd-meter span { inline-size: 33%; background: var(--color-error); }
.pwd-wrap:has(input:valid) .pwd-meter span { inline-size: 100%; background: var(--color-success); }
```

### 129. 0-JS Star Rating Input (`row-reverse` + `~`)
*Forms · Baseline · Markup*

A classic star rating that fills left to right with hidden radios and flex `row-reverse`.

```html
<fieldset class="star-rating">
  <legend class="sr-only">Rate this</legend>
  <input type="radio" id="st5" name="rate" value="5" class="sr-only"><label for="st5">★</label>
  <input type="radio" id="st4" name="rate" value="4" class="sr-only"><label for="st4">★</label>
  <input type="radio" id="st3" name="rate" value="3" class="sr-only"><label for="st3">★</label>
  <input type="radio" id="st2" name="rate" value="2" class="sr-only"><label for="st2">★</label>
  <input type="radio" id="st1" name="rate" value="1" class="sr-only"><label for="st1">★</label>
</fieldset>
```

```css
.star-rating { display: inline-flex; flex-direction: row-reverse; justify-content: flex-end; border: 0; padding: 0; }
.star-rating label { cursor: pointer; font-size: 2rem; color: var(--color-surface-offset); min-block-size: 44px; min-inline-size: 44px; display: grid; place-items: center; transition: color 150ms ease; }
.star-rating label:hover, .star-rating label:hover ~ label, .star-rating input:checked ~ label { color: oklch(0.8 0.15 80); }
.star-rating:has(input:focus-visible) label:has(+ input:focus-visible) { outline: 2px solid var(--color-primary); outline-offset: 2px; }
```

### 130. Dual-Thumb Range Slider (Overlapping inputs)
*Forms · Baseline · Markup*

A min/max range picker with two overlapping native sliders whose thumbs stay interactive.

```html
<div class="double-slider">
  <input type="range" min="0" max="100" value="20" aria-label="Lowest price">
  <input type="range" min="0" max="100" value="80" aria-label="Highest price">
  <div class="slider-track" aria-hidden="true"></div>
</div>
```

```css
.double-slider { position: relative; block-size: 44px; display: flex; align-items: center; }
.double-slider input[type="range"] {
  position: absolute; inline-size: 100%; appearance: none; background: transparent;
  pointer-events: none; z-index: 2; margin: 0; outline: none;
}
.double-slider input[type="range"]::-webkit-slider-thumb {
  pointer-events: auto; appearance: none; inline-size: 24px; block-size: 24px;
  border-radius: 50%; background: var(--color-primary); cursor: grab;
}
.double-slider input[type="range"]:focus-visible::-webkit-slider-thumb { outline: 2px solid var(--color-primary); outline-offset: 4px; }
.slider-track { position: absolute; inline-size: 100%; block-size: 6px; background: var(--color-surface-offset); border-radius: 999px; z-index: 1; }
```

### 131. Auto-Dismiss Transient Toast (`popover="manual"`)
*Overlays · Newer · Markup*

A self-dismissing transient toast driven by CSS keyframes, with no script.

```html
<button commandfor="auto-toast-1" command="show-popover" class="btn">Save changes</button>

<div id="auto-toast-1" popover="manual" class="auto-toast">
  ✅ Changes saved to the cloud
</div>
```

```css
.auto-toast {
  margin: auto auto 2rem auto; border: 0; padding: .75rem 1.25rem;
  border-radius: 999px; background: var(--color-text); color: var(--color-bg);
  box-shadow: 0 12px 32px oklch(0 0 0 / 0.15);
}
.auto-toast:popover-open {
  animation: toast-lifecycle 4s cubic-bezier(.16,1,.3,1) forwards;
}
@keyframes toast-lifecycle {
  0% { opacity: 0; transform: translateY(16px); }
  10%, 90% { opacity: 1; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(-16px); display: none; overlay: none; }
}
```

### 132. Exclusive Accordion Group (`<details name="...">`)
*Layout · Baseline · Markup*

An exclusive accordion where the browser automatically closes sibling panels when a new one opens.

```html
<div class="faq-group">
  <details name="faq">
    <summary>Is support included?</summary>
    <div class="faq-content">Yes, email support is included in every plan.</div>
  </details>
  <details name="faq">
    <summary>How does billing work?</summary>
    <div class="faq-content">Billing is monthly in advance.</div>
  </details>
</div>
```

```css
.faq-group details { border: 1px solid var(--color-border); border-radius: var(--radius-md); margin-block-end: .5rem; }
.faq-group summary { min-block-size: 44px; display: flex; align-items: center; padding-inline: 1rem; cursor: pointer; font-weight: 600; list-style: none; }
.faq-group summary::-webkit-details-marker { display: none; }
.faq-group summary::after { content: "+"; margin-inline-start: auto; transition: transform 200ms ease; }
.faq-group details[open] summary::after { transform: rotate(45deg); }
.faq-content { padding: 1rem; border-top: 1px solid var(--color-border); }
```

### 133. Billing Period Pricing Toggle (`:has()`)
*State · Baseline · Markup*

Visually switches prices between monthly and yearly billing with no JS.

```html
<div class="price-toggle-wrap">
  <fieldset class="billing-switch">
    <legend class="sr-only">Billing type</legend>
    <label><input type="radio" name="billing" id="b-m" checked> Monthly</label>
    <label><input type="radio" name="billing" id="b-y"> Yearly (−20%)</label>
  </fieldset>

  <div class="price-card">
    <p class="price-val price-monthly">$19 / mo</p>
    <p class="price-val price-yearly">$15 / mo</p>
  </div>
```

```css
.billing-switch { display: inline-flex; gap: .25rem; border: 0; padding: .25rem; background: var(--color-surface-offset); border-radius: 999px; }
.billing-switch label { min-block-size: 44px; display: inline-flex; align-items: center; padding-inline: 1rem; border-radius: 999px; cursor: pointer; }
.price-toggle-wrap:has(#b-m:checked) label:has(#b-m),
.price-toggle-wrap:has(#b-y:checked) label:has(#b-y) { background: var(--color-bg); font-weight: 600; box-shadow: 0 1px 3px oklch(0 0 0 / .1); }

.price-yearly { display: none; }
.price-toggle-wrap:has(#b-y:checked) .price-monthly { display: none; }
.price-toggle-wrap:has(#b-y:checked) .price-yearly { display: block; }
```

### 134. Mobile Swipe-to-Action List (`scroll-snap`)
*Interaction · Baseline · Markup*

A mobile-first swipe list where a delete button appears on a horizontal swipe.

```html
<ul class="swipe-list">
  <li class="swipe-item">
    <div class="swipe-content">Document_v1.pdf</div>
    <button class="swipe-action">Delete</button>
  </li>
</ul>
```

```css
.swipe-list { list-style: none; padding: 0; margin: 0; }
.swipe-item { display: flex; inline-size: 100%; overflow-x: auto; scroll-snap-type: x mandatory; overscroll-behavior-x: contain; scrollbar-width: none; }
.swipe-item::-webkit-scrollbar { display: none; }
.swipe-content { flex: 0 0 100%; scroll-snap-align: start; padding: 1rem; min-block-size: 44px; background: var(--color-surface); }
.swipe-action { flex: 0 0 80px; scroll-snap-align: end; background: var(--color-error); color: white; border: 0; cursor: pointer; font-weight: 600; }
```

### 135. Hero Parallax Lockup & Depth (`view-timeline`)
*Scroll-driven · Progressive · 0 JS*

Multi-layer parallax where background and foreground move at different speeds on scroll.

```html
<header class="plx-hero">
  <div class="plx-layer plx-bg" aria-hidden="true"></div>
  <div class="plx-layer plx-fg"><h1>The future of UI</h1></div>
</header>
```

```css
.plx-hero { position: relative; block-size: 70vh; overflow: hidden; display: grid; place-items: center; }
.plx-layer { position: absolute; inset: -10%; }
.plx-bg { background: url('/hero-bg.jpg') center/cover; }
.plx-fg { display: grid; place-items: center; z-index: 2; color: white; }

@supports (animation-timeline: view()) {
  .plx-bg { animation: plx-bg-anim linear both; animation-timeline: view(); }
  @keyframes plx-bg-anim { to { transform: translateY(15%); } }
}
```

### 136. Native Datalist Autocomplete Search
*Forms · Baseline · Markup*

A search field with a native autocomplete menu via `<datalist>`.

```html
<label for="city-search">Search city</label>
<input type="search" id="city-search" list="cities" placeholder="e.g. London">
<datalist id="cities">
  <option value="London"></option>
  <option value="Berlin"></option>
  <option value="Paris"></option>
</datalist>
```

```css
input[type="search"] {
  min-block-size: 44px; inline-size: 100%; padding-inline: 1rem;
  border: 1px solid var(--color-border); border-radius: var(--radius-md);
  background: var(--color-bg); color: var(--color-text);
}
input[type="search"]:focus-visible { outline: 2px solid var(--color-primary); outline-offset: 2px; }
```

### 137. Expandable Icon Search Field (`:focus-within`)
*Forms · Baseline · Markup*

A compact search button that expands into a full search field on click/focus.

```html
<form class="search-expand">
  <input type="search" placeholder="Search…" aria-label="Search">
  <button type="submit" aria-label="Submit search">🔍</button>
</form>
```

```css
.search-expand {
  display: flex; align-items: center; inline-size: 44px; block-size: 44px;
  border: 1px solid var(--color-border); border-radius: 999px; overflow: hidden;
  transition: inline-size 280ms cubic-bezier(.16,1,.3,1);
}
.search-expand:focus-within { inline-size: min(18rem, 80vw); }
.search-expand input { flex: 1; border: 0; background: none; padding-inline: 1rem; opacity: 0; transition: opacity 200ms ease; }
.search-expand:focus-within input { opacity: 1; }
.search-expand button { inline-size: 44px; block-size: 44px; border: 0; background: none; cursor: pointer; flex-shrink: 0; }
```

### 138. Drop Cap & Editorial Typography (`initial-letter`)
*Typography · Newer · 0 JS*

An editorial drop cap for lead paragraphs.

```html
<p class="prose-dropcap">Once upon a time there was a new standard for the web…</p>
```

```css
.prose-dropcap::first-letter {
  color: var(--color-primary); font-weight: 700;
}
@supports (initial-letter: 3 2) {
  .prose-dropcap::first-letter { initial-letter: 3 2; margin-inline-end: .5rem; }
}
@supports not (initial-letter: 3 2) {
  .prose-dropcap::first-letter { float: left; font-size: 3.2rem; line-height: .8; padding-inline-end: .4rem; }
}
```

### 139. Scroll-Driven Image Wipe (`clip-path: inset()`)
*Reveal · Progressive · 0 JS*

A tactile image reveal with `clip-path` that wipes the image in, synced to scroll.

```html
<figure class="img-wipe"><img src="/photo.jpg" alt="Description"></figure>
```

```css
.img-wipe { margin: 0; overflow: hidden; border-radius: var(--radius-lg); }
.img-wipe img { display: block; inline-size: 100%; block-size: auto; }
@supports (animation-timeline: view()) {
  .img-wipe img {
    animation: wipe-anim linear both; animation-timeline: view();
    animation-range: entry 0% entry 60%;
  }
  @keyframes wipe-anim {
    from { clip-path: inset(0 100% 0 0); transform: scale(1.05); }
    to { clip-path: inset(0 0 0 0); transform: scale(1); }
  }
```

### 140. Sticky Footer Reveal Layout
*Layout · Baseline · 0 JS*

The page footer sits at the bottom and is revealed as the main content scrolls up.

```html
<main class="main-reveal">Main content</main>
<footer class="footer-reveal">Footer</footer>
```

```css
.main-reveal {
  position: relative; z-index: 1; background: var(--color-bg);
  box-shadow: 0 20px 40px oklch(0 0 0 / .15); border-radius: 0 0 var(--radius-lg) var(--radius-lg);
}
.footer-reveal {
  position: sticky; bottom: 0; z-index: 0; padding: var(--space-8);
  background: var(--color-text); color: var(--color-bg);
}
```

### 141. Accessible Skip Link (`:focus-visible` Slide-In)
*Navigation · Baseline · 0 JS*

A keyboard-first skip link that slides in at the top of the screen on focus.

```html
<a href="#main-content" class="skip-link">Skip to content</a>
```

```css
.skip-link {
  position: fixed; top: 1rem; left: 1rem; z-index: 9999;
  min-block-size: 44px; padding-inline: 1rem; display: inline-grid; place-items: center;
  background: var(--color-text); color: var(--color-bg); font-weight: 700;
  border-radius: var(--radius-md); text-decoration: none;
  transform: translateY(-200%); transition: transform 200ms ease;
}
.skip-link:focus-visible { transform: translateY(0); outline: 2px solid var(--color-primary); outline-offset: 3px; }
```

### 142. Interactive Map Pin Popover (`anchor-name` + `position-anchor`)
*Overlays · Newer · Markup*

Map pins that open anchored popovers on click.

```html
<div class="map-container">
  <button id="pin-1" commandfor="pop-pin-1" command="toggle-popover" class="map-pin" style="top: 30%; left: 40%;">📍</button>
  <div id="pop-pin-1" popover="auto" class="pin-pop">London HQ</div>
</div>
```

```css
.map-container { position: relative; inline-size: 100%; block-size: 24rem; background: var(--color-surface-offset); }
.map-pin { position: absolute; anchor-name: --pin-1; min-block-size: 44px; min-inline-size: 44px; border: 0; background: none; font-size: 1.5rem; cursor: pointer; }
.pin-pop {
  margin: 0; inset: auto; position-anchor: --pin-1; position-area: top;
  position-try-options: flip-block, flip-inline; padding: var(--space-2) var(--space-3);
  background: var(--color-bg); border-radius: var(--radius-sm); border: 1px solid var(--color-border);
}
```

### 143. Print-Friendly Article Stylesheet (`@media print`)
*Layout · Baseline · 0 JS*

A print stylesheet that hides chrome and prints URLs in plaintext.

```css
@media print {
  .site-header, .site-footer, .skip-link, .speed-dial, .toast { display: none !important; }
  body { background: white !important; color: black !important; }
  a[href^="http"]::after { content: " (" attr(href) ")"; font-size: .85em; }
  h1, h2, h3 { page-break-after: avoid; break-after: avoid; }
  p, blockquote { orphans: 3; widows: 3; }
}
```

### 144. Dynamic Counter Summary (`counter-increment` + `:has()`)
*State · Baseline · Markup*

Counts checked boxes in a list and shows the total in a heading, with no script.

```html
<div class="count-summary-group">
  <h3>Selected services (<span class="count-output"></span>)</h3>
  <label><input type="checkbox" class="count-item"> Web design</label>
  <label><input type="checkbox" class="count-item"> SEO</label>
</div>
```

```css
.count-summary-group { counter-reset: item-sum 0; }
.count-item:checked { counter-increment: item-sum 1; }
.count-output::before { content: counter(item-sum); }
.count-summary-group label { display: flex; align-items: center; min-block-size: 44px; cursor: pointer; }
```

### 145. Animated Number Counter (`@property` + `@keyframes`)
*Typography · Progressive · 0 JS*

Counts a numeric value from 0 to a target with pure CSS.

```html
<div class="num-counter" style="--target: 98;">
  <span class="num-val"></span>%
</div>
```

```css
@property --num-count {
  syntax: "<integer>";
  initial-value: 0;
  inherits: false;
}
.num-val {
  counter-reset: num var(--num-count);
  animation: num-scroll 2s ease-out forwards;
}
.num-val::after { content: counter(num); }

@keyframes num-scroll {
  to { --num-count: var(--target, 100); }
}
@supports (animation-timeline: view()) {
  .num-val { animation-timeline: view(); animation-range: entry 10% entry 80%; }
}
```

### 146. Guardrail Focus-Lock Modal (`overscroll-behavior: contain`)
*Overlays · Baseline · Markup*

A modal dialog that prevents scroll chaining (the background moving while the modal scrolls).

```html
<dialog id="guard-modal" class="guard-modal" closedby="any">
  <h2>Modal content</h2>
  <div class="guard-body">Long scrollable content…</div>
</dialog>
```

```css
.guard-modal {
  max-block-size: 80vh; max-inline-size: min(90vw, 36rem); margin: auto;
  padding: var(--space-6); border: 0; border-radius: var(--radius-lg);
  overflow-y: auto; overscroll-behavior: contain; scrollbar-gutter: stable;
}
.guard-modal::backdrop { overscroll-behavior: none; background: oklch(0 0 0 / .4); }
```

### 147. Fluid Rhythm Function (`@function`)
*Layout · Progressive · 0 JS*

Centralize fluid spacing calculations with typed custom CSS functions. Unsupported engines fall back cleanly to the baseline `clamp()`.

```html
<article class="fluid-rhythm-card">
  <p class="eyebrow">Quarterly report</p>
  <h2>Spacing that scales</h2>
  <p>Responsive rhythm with typed @function.</p>
</article>
```

```css
.fluid-rhythm-card {
  inline-size: min(32rem, 100%);
  padding: clamp(1rem, 4cqi, 2rem);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}
@function --fluid-space(
  --minimum <length>,
  --preferred <length>,
  --maximum <length>
) returns <length> {
  result: clamp(var(--minimum), var(--preferred), var(--maximum));
}
.fluid-rhythm-card {
  padding: --fluid-space(1rem, 4cqi, 2rem);
}
.fluid-rhythm-card .eyebrow {
  color: var(--color-text-muted);
  font-size: .75rem;
  letter-spacing: .08em;
  text-transform: uppercase;
}
```

### 148. Donut-Scoped Documentation Callout (`@scope`)
*Layout · Baseline · 0 JS*

Style component guidance with `@scope` while explicitly preventing accent styles from leaking into nested demo regions.

```html
<article class="docs-card">
  <h2><span class="accent">Scoped</span> component guidance</h2>
  <p>The outer accent belongs to the card.</p>
  <section class="example" aria-label="Unstyled embedded example">
    <p><span class="accent">Embedded content</span> keeps its own theme.</p>
  </section>
</article>
```

```css
.docs-card {
  padding: 1rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
}
.docs-card > h2 .accent,
.docs-card > p .accent {
  color: var(--color-accent);
  font-weight: 750;
}
.docs-card .example {
  margin-block-start: 1rem;
  padding: .75rem;
  border-inline-start: 3px solid var(--color-border);
}
@scope (.docs-card) to (.example) {
  .accent {
    color: var(--color-accent);
    font-weight: 750;
  }
```

### 149. Snapped Product State (`scroll-state()`)
*Scroll · Progressive · 0 JS*

Highlight the active card aligned to a scroll-snap point using `@container scroll-state(snapped: inline)` without JavaScript observers.

```html
<div class="snap-products" aria-label="Featured products">
  <article class="snap-product">
    <div class="snap-product__body"><strong>Starter</strong><span>$12</span></div>
  </article>
  <article class="snap-product">
    <div class="snap-product__body"><strong>Studio</strong><span>$28</span></div>
  </article>
  <article class="snap-product">
    <div class="snap-product__body"><strong>Agency</strong><span>$64</span></div>
  </article>
</div>
```

```css
.snap-products {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: min(80%, 16rem);
  gap: .75rem;
  overflow-x: auto;
  padding: .5rem;
  scroll-snap-type: inline mandatory;
  overscroll-behavior-inline: contain;
}
.snap-product {
  container-type: scroll-state;
  scroll-snap-align: center;
}
.snap-product__body {
  min-block-size: 8rem;
  padding: 1rem;
  display: grid;
  align-content: space-between;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}
@supports (container-type: scroll-state) {
  .snap-product__body {
    opacity: .62;
    scale: .96;
    transition: opacity .2s ease, scale .2s ease, border-color .2s ease;
  }
  @container scroll-state(snapped: inline) {
    .snap-product__body {
      opacity: 1;
      scale: 1;
      border-color: var(--color-primary);
    }
}
@media (prefers-reduced-motion: reduce) {
  .snap-product__body { transition: none; }
}
```

### 150. Semantic Metrics Dividers (`column-rule`)
*Data · Progressive · 0 JS*

Draw clean separators directly in grid and flex gaps using `column-rule` without first/last-child border overrides.

```html
<dl class="metric-strip">
  <div><dt>Revenue</dt><dd>$84k</dd></div>
  <div><dt>Retention</dt><dd>94%</dd></div>
  <div><dt>Latency</dt><dd>82ms</dd></div>
</dl>
```

```css
.metric-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin: 0;
  padding: 1rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
}
.metric-strip > div {
  min-inline-size: 0;
  padding-inline-start: 1rem;
  border-inline-start: 1px solid var(--color-border);
}
.metric-strip > div:first-child {
  padding-inline-start: 0;
  border-inline-start: 0;
}
.metric-strip dt {
  color: var(--color-text-muted);
  font-size: .75rem;
}
.metric-strip dd {
  margin: .2rem 0 0;
  font-size: clamp(1.1rem, 4cqi, 1.6rem);
  font-weight: 750;
}
@supports (row-rule: 1px solid transparent) {
  .metric-strip {
    column-rule: 1px solid var(--color-border);
  }
  .metric-strip > div,
  .metric-strip > div:first-child {
    padding-inline-start: 0;
    border-inline-start: 0;
  }
```

### 151. Organic Avatar Cluster (`random()`)
*Visual · Progressive · 0 JS*

Cosmetic rotation and vertical jitter for avatar stacks using CSS `random()`, backed by deterministic `:nth-child()` fallbacks.

```html
<ul class="avatar-cluster" aria-label="Project contributors">
  <li aria-label="Ari">A</li>
  <li aria-label="Bea">B</li>
  <li aria-label="Chen">C</li>
  <li aria-label="Dara">D</li>
  <li aria-label="Eli">E</li>
</ul>
```

```css
.avatar-cluster {
  display: flex;
  align-items: center;
  gap: .4rem;
  padding: 1rem;
  margin: 0;
  list-style: none;
}
.avatar-cluster > li {
  inline-size: 2.75rem;
  block-size: 2.75rem;
  display: grid;
  place-items: center;
  border: 2px solid var(--color-bg);
  border-radius: 50%;
  background: var(--color-primary);
  color: var(--color-text-inverse);
  font-weight: 750;
}
.avatar-cluster > li:nth-child(3n + 1) { rotate: -4deg; translate: 0 -2px; }
.avatar-cluster > li:nth-child(3n + 2) { rotate:  3deg; translate: 0  2px; }
.avatar-cluster > li:nth-child(3n)     { rotate: -1deg; translate: 0  1px; }
@supports (rotate: random(-1deg, 1deg)) {
  .avatar-cluster > li {
    rotate: random(-6deg, 6deg);
    translate: 0 random(-3px, 3px);
  }
@media (prefers-reduced-motion: reduce) {
  .avatar-cluster > li {
    rotate: 0deg;
    translate: 0;
  }
```

---

# Ready-made stacks

Composed combinations for different project types. Every stack starts from Base safeguards. Stacks that include Spell 43 or 47 are marked with † and require the Root scroll-state preset.

---

## Astro mapping

### MainLayout.astro
- 14
- 17
- 36
- 41
- 43
- 47
- 112
- 114
- 116
- 121
- 126
- 135
- 140
- 141
- 143

### Header.astro
- 5
- 7
- 17
- 24
- 43
- 44
- 65
- 68
- 71
- 73
- 79
- 80
- 81
- 97
- 98
- 117
- 121
- 126
- 127
- 137
- 141

### Hero.astro
- 8
- 9
- 17
- 35
- 52
- 64
- 65
- 68
- 91
- 92
- 101
- 109
- 135
- 139

### Card.astro
- 1
- 2
- 3
- 13
- 25
- 37
- 40
- 51
- 58
- 67
- 82
- 83
- 84
- 100
- 101
- 103
- 109
- 120

### Accordion.astro
- 15
- 22
- 33
- 61
- 70
- 108
- 132

### Dialog.astro / Popover.astro
- 31
- 66
- 75
- 77
- 79
- 88
- 89
- 90
- 97
- 98
- 106
- 107
- 117
- 127
- 131
- 142
- 146

### DataViz.astro
- 94
- 95
- 96
- 110
- 111
- 114
- 119
- 122
- 123
- 124
- 125
- 145

### Table.astro
- 69
- 94
- 95
- 96
- 110
- 111
- 114
- 122

### Tooltip.astro
- 18
- 34
- 89
- 98
- 107

### Field.astro
- 6
- 16
- 19
- 20
- 23
- 32
- 38
- 48
- 50
- 54
- 57
- 76
- 85
- 86
- 87
- 96
- 102
- 104
- 105
- 115
- 118
- 128
- 129
- 130
- 131
- 136
- 144

### Carousel.astro
- 12
- 45
- 46
- 56
- 62
- 93
- 99

### Media.astro
- 11
- 25
- 67
- 74
- 75
- 91
- 92
- 93
- 108
- 109
- 139

### Prose.astro / Sidebar.astro
- 10
- 21
- 27
- 29
- 53
- 59
- 60
- 63
- 70
- 72
- 78
- 81
- 92
- 108
- 112
- 113
- 126
- 138
- 143
- 145

### Tabs.astro
- 26
- 45
- 61
- 71
- 80
- 133

### Section.astro
- 41
- 51
- 52
- 55
- 68
- 72
- 91
- 92
- 100
- 101
- 111
- 126
- 135

### Shell.astro
- 30
- 35
- 39
- 41
- 73
- 88
- 90
- 97
- 114
- 116
- 121
- 131
- 141

### ContactForm.astro / LeadWizard.astro
- 6
- 16
- 23
- 28
- 32
- 48
- 57
- 76
- 85
- 87
- 105
- 115
- 128
- 130
- 144

### Footer.astro
- 24
- 29
- 49
- 59
- 140

### SkipLink.astro
- 21
- 112
- 141

---

## Ready-made Astro stacks

### Astro baseline
`2 · 5 · 6 · 10 · 19 · 20 · 22 · 33 · 38 · 39 · 41 · 53 · 63 · 103 · 114 · 116 · 141 · 143`

### Astro marketing
`1 · 2 · 3 · 5 · 8 · 13 · 17 · 25 · 31 · 35 · 38 · 41 · 43 · 56 · 98 · 100 · 101 · 109 · 119 · 120 · 135 · 139`

### Astro docs
`5 · 10 · 19 · 21 · 22 · 33 · 36 · 41 · 43 · 44 · 47 · 53 · 60 · 63 · 97 · 108 · 112 · 113 · 126 · 132 · 138 · 141`

### Astro SaaS
`2 · 6 · 16 · 19 · 23 · 32 · 33 · 37 · 38 · 39 · 40 · 48 · 50 · 54 · 57 · 102 · 104 · 105 · 106 · 115 · 118 · 122 · 123 · 128 · 131 · 133 · 144 · 146`

### Astro commerce
`2 · 3 · 5 · 12 · 25 · 37 · 40 · 45 · 46 · 49 · 56 · 62 · 99 · 100 · 107 · 110 · 117 · 120 · 121 · 129 · 130 · 133 · 134`

### Astro editorial
`8 · 9 · 10 · 21 · 25 · 41 · 51 · 52 · 53 · 60 · 63 · 64 · 108 · 111 · 112 · 113 · 126 · 138 · 143 · 145`

---

