---
name: design-spells
description: "Curated micro-interactions, CSS animations, and UI polish patterns optimized for Astro 7, Tailwind CSS v4, and Zero-JS runtime. Use when building or refining UI components, buttons, navigation, cards, headers, and scroll effects."
risk: safe
source: internal
date_added: "2026-08-10"
---

# Design Spells — Astro Canonical (2026)

En enda **canonical** referensbank över design spells för moderna Astro-projekt där målet är **0 klient-JS**. Den här filen slår ihop originalets spellbibliotek med en Astro-first struktur och **utesluter alla spells märkta `+ JS`**.

Dokumentet innehåller därför endast spells märkta **`0 JS`** eller **`Markup`**. I originalfilens terminologi betyder `Markup` att spellen fortfarande är JS-fri men kräver ett tydligt HTML-mönster, till exempel `<details>`, checkbox-state, `popover`, `dialog`-kompatibel struktur eller annan native state-machine.

Totalt ingår **144 Astro-relevanta spells**. Exkluderade `+ JS`-spells: **4, 42**. Spells **97–146** är 2026-tillägg (Invoker Commands, Interest Invokers, Grid Lanes, `if()`, typed `attr()`, `closedby`, `hidden="until-found"`, Conic Donut, Faceted Matrix, Cart Badge, Gantt, Heatmap, SVG Draw, Section-Spy, Password Meter, Star Rating, Auto Toast, Exclusive Accordion, Swipe Action, Parallax, Datalist, Drop Cap, Image Wipe, Sticky Footer, Skip Link, Map Pin, Dynamic Counter, Animated Counter, Focus-Lock Modal).

---

## Hur dokumentet används

### För människor

- Bläddra till en kategori som matchar problemet.
- Läs metadata-raden direkt under rubriken.
- Kopiera CSS-blocket och byt ut projektets tokens där det behövs.
- Börja med Baseline-spells, gå vidare till Newer och sedan Progressive.
- Använd helst 1–2 visuellt dominanta spells per sektion.

### För AI-agenter och editor-agenter

- Referera alltid till spells med stabilt nummer, till exempel `Spell 43`.
- Om flera spells löser samma problem ska den modernaste hållbara väljas först.
- Prioritet för val: **Baseline → Newer → Progressive**.
- Föredra spells som passar direkt i `.astro`-komponenter eller layout-CSS.
- Introducera inte klient-JS för sådant som redan löses av dokumentets JS-fria spells.

---

## Kärnprinciper

- HTML + CSS först.
- 0 klient-JS som standard.
- Native browser state före handbyggda lösningar.
- Progressive enhancement före hårda beroenden.
- Astro-fit före demo-effekt.
- Läsbarhet, fokus och layout går före dekor.
- Motion är enhancement och ska respektera `prefers-reduced-motion`.
- Komponentlokal CSS är oftast bättre än globalt läckande selectors.

---

## Metadata och tolkning

Originalfilens metadata behålls inne i spellsektionerna:

- **Kategori** = funktionell typ av spell.
- **Status** = browserrisk: `Baseline`, `Newer`, `Progressive`.
- **JS-behov** = här förekommer bara `0 JS` och `Markup` i denna canonical Astro-utgåva.

### Praktisk tolkning för Astro

- **0 JS**: direkt lämplig i statisk Astro-markup.
- **Markup**: fortfarande JS-fri, men kräver mer exakt HTML-struktur.
- **Baseline**: trygg att använda direkt.
- **Newer**: bra i moderna projekt, testa gärna i kritiska UI-flöden.
- **Progressive**: ska kapslas i `@supports` eller få tyst fallback.

### Rekommenderad placering i Astro

- Globala spells: `base.css` eller global design layer.
- Page chrome: `MainLayout.astro`, `Header.astro`, `Shell.astro`.
- Komponentspells: lokal CSS i `.astro`-komponenter.
- Nya browserfeatures: nära komponenten bakom `@supports`.

---

## Bas-skydd

Detta är fundamentet alla spells bygger på. Ladda före allt annat.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

html {
  /* Förhindrar layout shift när dialog/popover öppnas och låser rullningslisten */
  scrollbar-gutter: stable;
  /* Förhindrar oönskat textzoombeteende på mobila enheter */
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}

:target, :focus-visible {
  /* Förhindrar att djuplänkat innehåll hamnar under sticky header (se Spell 17) */
  scroll-margin-block-start: max(6rem, var(--header-height, 0px));
}

/* Universell fokus-baslinje för tangentbordsnavigering */
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

/* Förhindrar att scroll läcker upp till parent/body i inbäddade scrollers */
.scroller, .modal-body, .drawer-body {
  overscroll-behavior: contain;
}

/* WCAG 2.2 AA / mobil: minsta tryckyta för knappar, länkar, summary, labels. */
button, [type="button"], [type="submit"], [type="reset"],
summary, .btn, a.btn {
  min-block-size: 44px;
}

/* Visuellt dold men kvar i tab-ordning och accessibility-trädet.
   Använd för checkboxar/inputs som driver markup-state-machines (se Spell 60). */
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

Lägg till detta **endast** om du använder Spell 43 (Auto-Hide Header) eller Spell 47 (Scroll-Awake Back-to-Top). Spells 44, 45 och 46 sätter upp lokala scroll-state-containers själva och behöver inte detta.

```css
html {
  container-type: scroll-state;
  overflow: auto;
}
```

`container-type: scroll-state` ignoreras tyst i browsers utan stöd, så presetet är säker att inkludera även där fallback krävs. Det är dock opinionerat nog att inte vara default.

---

## Urvalsregler

1. Välj högst 1–2 visuellt dominanta spells per sektion.
2. Välj Baseline före Newer och Newer före Progressive.
3. Prioritera fokus, kontrast, spacing och informationshierarki.
4. Lägg prestandaspells tidigt på långa sidor.
5. Använd native state (`:has()`, `:focus-within`, `<details>`, `scroll-snap`, `scroll-state`) innan du uppfinner egna mönster.

### Anti-patterns

- För många hover-only-spells i touch-tunga gränssnitt.
- För många blur- eller backdrop-effekter i samma viewport.
- För många reveal-effekter samtidigt.
- För mycket specialmarkup utan tydligt värde.
- För mycket dekoration innan läsbarhet och state-feedback fungerar.

---

# Spells


## Interaktion & feedback

### 1. Shimmer på primärknappar
*Interaktion · Baseline · 0 JS*

En subtil ljusglimt sveper över knappen vid hover.

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
*Interaktion · Baseline · 0 JS*

Mikroskopisk nedskalning på `:active` för taktil feedback.

```css
.btn, .card-interactive {
  min-block-size: 44px;
  transition: transform 100ms cubic-bezier(0.16,1,0.3,1);
}
.btn:active, .card-interactive:active { transform: scale(0.98); }
```

### 3. Lift & Zoom på kort
*Interaktion · Baseline · 0 JS*

Kortet lyfts, bilden zoomas in långsamt.

```css
.destination-card {
  overflow: hidden;
  transition: transform 350ms cubic-bezier(0.16,1,0.3,1), box-shadow 350ms cubic-bezier(0.16,1,0.3,1);
}
.destination-card:hover,
.destination-card:focus-within {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px oklch(0.2 0.01 80 / 0.12);
}
.destination-card img { transition: transform 600ms cubic-bezier(0.16,1,0.3,1); }
.destination-card:hover img,
.destination-card:focus-within img { transform: scale(1.05); }
@media (hover: none) {
  .destination-card:hover { transform: none; box-shadow: none; }
  .destination-card:hover img { transform: none; }
}
```

### 5. Magnetic Underline
*Interaktion · Baseline · 0 JS*

Underline glider in i stället för att blinka fram.

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
*Interaktion · Baseline · 0 JS*

```css
.icon {
  color: var(--color-text-muted);
  min-block-size: 44px; min-inline-size: 44px;
  display: inline-grid; place-items: center;
  transition: color 180ms cubic-bezier(0.16,1,0.3,1);
}
.icon:hover, .icon:focus-visible { color: var(--color-primary); }
```

### 19. Focus-Within Halo
*Interaktion · Baseline · 0 JS*

Wrapper-baserad fokusfeedback för sammansatta inputs och sökrutor.

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
*Interaktion · Baseline · 0 JS*

Animera bara de egenskaper som faktiskt ändras. Aldrig `transition: all`.

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
*Interaktion · Baseline · Markup*

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
*Interaktion · Baseline · 0 JS*

```css
a[target="_blank"] .external-icon {
  transition: transform 180ms cubic-bezier(0.16,1,0.3,1), opacity 180ms cubic-bezier(0.16,1,0.3,1);
}
a[target="_blank"]:hover .external-icon,
a[target="_blank"]:focus-visible .external-icon {
  transform: translate(.12rem, -.12rem);
  opacity: 1;
}
```

### 26. Pill Segmented Control Glow
*Interaktion · Baseline · 0 JS*

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
  box-shadow: 0 1px 3px oklch(0 0 0 / .08), inset 0 1px 0 oklch(1 0 0 / .3);
}
```

### 38. Color-Mix Hover States
*Interaktion · Baseline · 0 JS*

Skapa hover/active-varianter direkt från en grundfärg utan att hårdkoda extra tokens.

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
*Interaktion · Baseline · 0 JS*

One-liner som färgar alla native formulärkontroller (radio, checkbox, range, progress).

```css
:root {
  accent-color: var(--color-primary);
}
```

### 67. Scroll-Driven Before/After Comparison
*Interaktion · Newer · Markup*

Touch-vänlig och tillgänglig före/efter-bildjämförelse helt utan JS. Scroller exporterar en namngiven `scroll-timeline` via `timeline-scope` så clip-path kan animeras på en *syskon*-yta (inte på scroller-elementet själv). Stödjer svepgester och piltangenter (`tabindex="0"`). `role="region"` — inte `slider` — eftersom `aria-valuenow` inte kan uppdateras utan JS.

```html
<div class="compare-container">
  <img src="/after.jpg" alt="Efter" class="compare-img compare-after">
  <div class="compare-before-wrap">
    <img src="/before.jpg" alt="Före" class="compare-img compare-before">
  </div>
  
  <div class="compare-scroller" tabindex="0" role="region" aria-label="Jämför före och efter. Svep eller använd piltangenter.">
    <div class="scroller-spacer"></div>
  </div>
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
}
```

### 71. Sliding Segment Indicator
*Interaktion · Baseline · Markup*

Pill-indikator i segmented controls/flikar som glider sömlöst till aktivt val med `:has()` och CSS-variabler (`--total-items`).

```html
<div class="segmented-nav" style="--total-items: 3;">
  <input type="radio" name="seg" id="seg-1" class="sr-only" checked style="--index: 0;">
  <label for="seg-1">Översikt</label>

  <input type="radio" name="seg" id="seg-2" class="sr-only" style="--index: 1;">
  <label for="seg-2">Analys</label>

  <input type="radio" name="seg" id="seg-3" class="sr-only" style="--index: 2;">
  <label for="seg-3">Inställningar</label>

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
*Interaktion · Baseline · Markup*

Svävande snabbknapp (FAB) som expanderar undermenyer via nativ `<details>` och `@starting-style`. 

**Guardrails:** `pointer-events: none` på wrapper förhindrar att osynliga klickytor täcker skärmen. Alla knappar uppfyller WCAG minsta klickytor (44x44px).

```html
<details class="speed-dial">
  <summary class="fab-main" aria-label="Snabbåtgärder">+</summary>

  <div class="fab-actions">
    <button class="fab-child" title="Nytt inlägg" aria-label="Nytt inlägg">📝</button>
    <button class="fab-child" title="Ladda upp bild" aria-label="Ladda upp bild">📷</button>
    <button class="fab-child" title="Dela sida" aria-label="Dela sida">🔗</button>
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
}
```

### 79. Anchor-Positioned Mega Menu (`[popover]`)
*Navigation · Newer · Markup*

Megameny som fälls ut från en nav-trigger via Invoker Commands (`commandfor` + `command="toggle-popover"`) och nativ `[popover=auto]`, fäst med anchor positioning. Ger Esc-stängning, light-dismiss och fokus-hantering helt utan skript. Sätt inte statisk `aria-expanded` — native popover sköter tillgänglighetsträdet.

```html
<nav class="site-nav">
  <button class="mega-trigger" commandfor="mega-1" command="toggle-popover">
    Produkter <span aria-hidden="true">▾</span>
  </button>
  <div id="mega-1" popover="auto" class="mega-panel">
    <ul>
      <li><a href="/analytics">Analytics</a></li>
      <li><a href="/automation">Automation</a></li>
      <li><a href="/api">API & Integrationer</a></li>
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
*Navigation · Newer · 0 JS*

Pill-navigering och chips med äkta "squircle"-silhuett (superelliptisk hörnrundning) istället för vanliga `border-radius`-bågar.

```html
<nav class="squircle-nav" aria-label="Huvudnavigering">
  <a href="/" aria-current="page">Översikt</a>
  <a href="/reports">Rapporter</a>
  <a href="/settings">Inställningar</a>
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
*Navigation · Newer · Markup*

Brödsmulor som visar en diskret "+N"-hint och kantmaskning endast när raden faktiskt är skrollbar.

```html
<nav class="crumbs-wrap" aria-label="Brödsmulor">
  <ol class="crumbs">
    <li><a href="/">Hem</a></li>
    <li><a href="/docs">Dokumentation</a></li>
    <li><a href="/docs/components">Komponenter</a></li>
    <li aria-current="page">Spells</li>
  </ol>
  <span class="crumb-hint" aria-hidden="true">+2</span>
</nav>
```

```css
.crumbs-wrap {
  position: relative; overflow-x: auto; container-type: scroll-state;
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
*Kort · Baseline · 0 JS*

Kortet lutar sig subtilt i 3D vid hover/fokus för djupkänsla — utan mus-spårning och utan extra DOM-lager.

```html
<article class="tilt-card">
  <h3>Premium-plan</h3>
  <p>Allt i Pro, plus prioriterad support och SSO.</p>
  <a href="/pricing">Välj plan</a>
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
*Kort · Baseline · 0 JS*

Biljett-/kupongkort med äkta perforerade "hål" i kanterna via pseudo-element.

```html
<article class="ticket">
  <div class="ticket-body">
    <h3>Sommarerbjudande</h3>
    <p>20% rabatt på alla årliga planer.</p>
  </div>
  <div class="ticket-stub">
    <strong>−20%</strong>
    <span>Kod: SOMMAR26</span>
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
*Kort · Baseline · 0 JS*

Sekundära kortåtgärder döljs tills kortet hovras eller fokuseras.

```html
<article class="card-row">
  <h3>Q3-rapport</h3>
  <div class="card-actions">
    <button aria-label="Redigera Q3-rapport">✏️</button>
    <button aria-label="Dela Q3-rapport">🔗</button>
    <button aria-label="Arkivera Q3-rapport">📦</button>
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
*Overlay · Baseline · 0 JS*

Bekräftelse-toasts som visas när en länk sätter `#toast-…` och stängs via en stängningslänk.

```html
<a href="#toast-saved" class="btn">Spara ändringar</a>

<div id="toast-saved" class="toast" role="status">
  ✅ Sparat! <a href="#" class="toast-close" aria-label="Stäng notis">✕</a>
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
*Overlay · Newer · Markup*

Klickstyrd åtgärdsmeny (⋯) fäst till sin trigger med anchor positioning och automatisk flip vid skärmkanter.

```html
<div class="ctx">
  <button class="ctx-btn" commandfor="ctx-menu" command="toggle-popover" aria-haspopup="menu" aria-label="Fler åtgärder">⋯</button>
  <div id="ctx-menu" popover="auto" class="ctx-menu" role="menu">
    <button role="menuitem">Redigera</button>
    <button role="menuitem">Duplicera</button>
    <hr>
    <button role="menuitem" class="danger">Ta bort</button>
  </div>
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
*Overlay · Baseline · Markup*

Svävande snabbknapp som solfjädrar ut underliggande åtgärder i en båge via nativa CSS `cos()` / `sin()`.

```html
<details class="fan">
  <summary class="fan-main" aria-label="Snabbåtgärder">＋</summary>
  <div class="fan-items">
    <button class="fan-item" style="--i:0" aria-label="Nytt inlägg">📝</button>
    <button class="fan-item" style="--i:1" aria-label="Ladda upp">📷</button>
    <button class="fan-item" style="--i:2" aria-label="Dela">🔗</button>
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

## Reveal & rörelse

### 8. Gradient Reveal på rubriker
*Reveal · Progressive · 0 JS*

Scroll-driven text reveal med `animation-timeline: view()`.

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

### 9. Depth Parallax på hero
*Reveal · Baseline · 0 JS*

Lätt 3D-settle på load.

```css
.hero-content { animation: hero-settle 0.8s cubic-bezier(0.16,1,0.3,1) both; }
@keyframes hero-settle {
  from { opacity: 0; transform: perspective(800px) rotateX(4deg) translateY(12px); }
  to   { opacity: 1; transform: perspective(800px) rotateX(0) translateY(0); }
}
```

### 11. Skeleton Shimmer
*Reveal · Baseline · 0 JS*

CSS-driven laddningsyta.

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

Stor premiumeffekt för multipage-sajter. Browsern hanterar MPA-navigeringen nativt.

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
}
```

### 31. Phantom Entry (`@starting-style`)
*Reveal · Baseline · Markup*

Mjuk fade-in från `display: none` utan JS. Perfekt för popover-menyer (`[popover]`-attribut) och native modaler.

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
}
```

### 65. Scroll-Driven Header Compression
*Scroll-driven · Baseline · 0 JS*

Minskar sticky header-höjd och skalar ner logotypen mjukt när användaren scrollar ner på sidan utan layout shifts.

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

Sömlös mjuk toning och oskärpa på `::backdrop` för nativa `<dialog>` och `[popover]`-modaler utan JS.

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
}
```

### 68. Infinite Logo Marquee
*Reveal · Baseline · 0 JS*

Smidigt oändligt rullande logoband med kantutoning via `mask-image`. 

**Obs:** Kräver dubblerad HTML-markup (två identiska `.marquee-track`) för att snurra utan glapp. Pausas automatiskt vid `:hover` och `:focus-within` för tillgänglighet.

```html
<div class="marquee">
  <div class="marquee-track">
    <span>Logo 1</span><span>Logo 2</span><span>Logo 3</span>
  </div>
  <!-- Duplicerat spår för skarvlös loop -->
  <div class="marquee-track" aria-hidden="true">
    <span>Logo 1</span><span>Logo 2</span><span>Logo 3</span>
  </div>
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

List- och kortelement tonas fram i sekvens när användaren scrollar ner, synkat mot viewport-positionen.

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
}
```

### 75. Native Modal Image Zoom (`popovertarget`)
*Reveal · Newer · Markup*

Klicka på en bild för att förstora den till fullskärmsläge med nativ `popover` utan tunga lightbox-bibliotek.

```html
<button commandfor="img-modal-1" command="toggle-popover" class="img-trigger">
  <img src="/photo-thumb.jpg" alt="Förstora bild">
</button>

<div id="img-modal-1" popover class="lightbox-popover">
  <img src="/photo-full.jpg" alt="Förstorad bild">
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
}
```

### 91. Ken Burns Scroll Gallery
*Media · Progressive · 0 JS*

Bilder andas långsamt (scale 1.12 → 1 → 1.12) synkat med sin position i viewporten utan en enda skroll-listener.

```html
<figure class="kb"><img src="/hero-1.jpg" alt="Kustlandskap"></figure>
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
}
```

### 92. Image-Clipped Gradient Headline
*Media · Baseline · 0 JS*

Rubrik fylld med bild eller gradient via `background-clip: text`.

```html
<h1 class="paint-headline">Bygg snabbare. Leverera snyggare.</h1>
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
*Media · Newer · Markup*

Bildtexter i en scroll-snap-karusell tonas in först när slidet är "snapped".

```html
<div class="snap-carousel">
  <figure class="slide">
    <img src="/a.jpg" alt="">
    <figcaption class="caption">Alperna — vinter 2026</figcaption>
  </figure>
  <figure class="slide">
    <img src="/b.jpg" alt="">
    <figcaption class="caption">Kusten — höst 2025</figcaption>
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

Header får frostat glas först när användaren scrollat lite.

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
}
```

### 30. Sticky CTA Elevation
*Scroll-driven · Baseline · 0 JS*

Sticky bottom CTA får mer separation när den ligger ovanpå innehåll.

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

Tunn progressindikator som drivs helt av scroll-position.

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
*Scroll-state · Newer · 0 JS*

Header glider undan på scroll ned, kommer tillbaka på scroll upp. **Kräver Root scroll-state preset.**

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
*Scroll-state · Newer · 0 JS*

Sticky-element får extra skugga och border bara när det faktiskt fastnat. Mycket mer premium än permanent skugga.

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
}
```

### 45. Snapped Spotlight
*Scroll-state · Newer · 0 JS*

Aktiv slide i en scroll-snap-container får full skärpa medan syskonen tonas ned.

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
}
```

### 46. Real Overflow Hint
*Scroll-state · Newer · 0 JS*

Visa edge-fades, pilar eller "swipe me"-hintar bara när innehållet faktiskt går att skrolla.

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
*Scroll-state · Newer · 0 JS*

Floating-knapp som vaknar först när användaren rört sidan. **Kräver Root scroll-state preset.**

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
}
```

### 55. Sticky Card Deck
*Scroll-driven · Progressive · 0 JS*

Kort staplas på varandra som en kortlek när användaren scrollar. Skala och dimning synkat med exit-crossing.

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
}
```

### 69. Scroll-Aware Table Boundaries (`container-type: scroll-state`)
*Scroll-state · Newer · 0 JS*

Tabeller med `position: sticky` visar skuggor och avdelare mot kanterna *endast* när innehållet faktiskt är skrollat horisontellt.

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
}
```

---

## Layout & komposition

### 12. Scroll Snap-galleri
*Layout · Baseline · 0 JS*

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
*Layout · Baseline · Markup · → 33 är modernare*

Behåll för bredare browser-kompatibilitet eller äldre projekt.

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
*Layout · Baseline · 0 JS · → 56 är modernare*

Behåll endast om bakgrunden är solid och statisk. Annars använd Spell 56.

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

Modernisering av Spell 15. Animerar `block-size: 0` → `auto` direkt.

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

Bonus: `<details name="faq">` ger automatiskt exclusive accordion (syskon stängs när nytt öppnas).

### 37. Container-Aware Card (`@container`)
*Layout · Baseline · 0 JS*

Kort som anpassar sin layout efter sin container, inte viewporten.

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
}
```

### 40. Subgrid Alignment
*Layout · Baseline · 0 JS*

Kort i en grid delar exakt samma rad-linjal trots olika innehållsmängd.

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
*Layout · Baseline · 0 JS · ersätter 27 i de flesta fall*

Scrollerns egna kanter blir bokstavligen genomskinliga. Fungerar oavsett bakgrundsfärg eller mönster bakom.

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

Riktiga flikar via `<details name="ui-tabs">`. Inga radio-button-hack.

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

Helt native paginering och nästa/föregående-knappar för scroll-snap-karuseller. Eliminerar de sista JS-biblioteken (Swiper, Embla, Splide) för standardkaruseller.

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

  /* Skapar automatiskt en knapp per slide */
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

  /* Native scroll-knappar */
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

Trädvy för dokumentation eller sidomenyer byggd med nästlade `<details>`-element utan JS.

```html
<nav class="tree-nav">
  <details open>
    <summary>Dokumentation</summary>
    <div class="tree-group">
      <a href="/docs/start">Kom igång</a>
      <details>
        <summary>Komponenter</summary>
        <div class="tree-group">
          <a href="/docs/buttons">Knappar</a>
          <a href="/docs/cards">Kort</a>
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

Dialog som automatiskt uppför sig som en Bottom Sheet på mobiler och en centrerad modal på större skärmar.

```css
dialog.responsive-sheet {
  margin: auto auto 0 auto; /* Bottenplacerad på mobil */
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
}

/* Centrerad modal på desktop */
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
}
```

---

## Anchor & positionering

### 18. Micro-Tooltips (`attr(data-tooltip)`)
*Anchor (legacy) · Baseline · 0 JS · → 34 är modernare*

Behåll för enkel hover-text på element där `overflow: hidden` inte är ett problem.

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
}
[data-tooltip]:focus-visible::after {
  opacity: 1;
  transform: translateX(-50%) translateY(0) scale(1);
}
```

### 34. Anchor-Positioned Tooltips
*Anchor · Newer · 0 JS*

Tooltips fästa via `anchor-name` / `position-anchor`. Inga overflow-problem.

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

Fältvalideringsfel fästs till input-fältet utan att trycka ned layouten.

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

Filtermenyer, sorteringspaneler och account-menus fästa till sin trigger.

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

Kontextuellt hjälpinnehåll dyker upp bredvid ett fält vid `:focus-within`.

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

## Typografi

### 10. Selection Skin
*Typografi · Baseline · 0 JS*

```css
::selection {
  background: oklch(from var(--color-primary) l c h / 0.25);
  color: var(--color-text);
}
```

### Bonus. Typografisk Harmoni (`text-wrap`)
*Typografi · Baseline · 0 JS*

```css
h1, h2, h3, h4, .text-balance { text-wrap: balance; }
p, li, .text-pretty { text-wrap: pretty; }
```

### 53. Text-Box-Trim
*Typografi · Newer · 0 JS*

Klipper bort fontens osynliga luft (leading) ovanför versaler och under baslinje. `padding: 1rem` blir nu exakt 1rem från bokstävernas kant.

```css
.btn, .badge, .pill, .chip {
  text-box-trim: trim-both;
  text-box-edge: cap alphabetic;
  line-height: 1;
}
```

Använd stenhårt på alla knappar, brickor och kortrubriker. Fallbacken är osynlig.

### 63. Smart Hyphenation
*Typografi · Baseline · 0 JS*

Aktiverar avstavning för smala kolumner och brödtext på en specifik språkkod. Förhindrar både "ravinen" och horribla orphan-rader.

```css
:root { hyphens: auto; }

article p, article li {
  hyphens: auto;
  hyphenate-character: "\2010";  /* riktigt bindestreck istället för minus */
  hyphenate-limit-chars: 8 4 4;  /* min 8 tecken, 4 före brytning, 4 efter */
  hyphenate-limit-lines: 2;       /* max 2 avstavade rader i rad */
  hyphenate-limit-last: always;   /* aldrig avstava sista raden i ett stycke */
}

html[lang="sv"] body { hyphens: auto; }
```

Kräver att `<html lang="sv">` är korrekt satt för att svensk avstavning ska fungera.

---

## Formulär & state

### 6. Focus Glow
*Formulär · Baseline · 0 JS*

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
*Formulär · Baseline · 0 JS*

Använd alltid riktig `<label>`. Placeholder-tricket ersätter aldrig etiketten semantiskt.

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
*Formulär · Baseline · 0 JS*

`:user-valid` / `:user-invalid` triggas först efter interaktion, aldrig vid sidladdning.

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
*Formulär · Baseline · 0 JS*

Wizard-steg numreras med CSS counters utan markup-logik.

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
*Formulär · Baseline · 0 JS*

Textarea växer med innehåll utan JS-listeners.

```css
textarea.auto-grow {
  field-sizing: content;
  min-block-size: 3lh;
  max-block-size: 12lh;
  resize: none;
}
```

### 54. Customizable Select (`appearance: base-select`)
*Formulär · Progressive · 0 JS*

Native `<select>` blir fullt styleable inklusive den utfällda menyn. Dödar headless-bibliotek för standard-dropdowns.

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
}
```

### 57. Form Gatekeeper
*Formulär · Baseline · 0 JS*

0-JS state-maskin: submit låst tills alla fält är giltiga. Ogiltiga fält shake:ar vid blur.

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
*Formulär · Baseline · Markup*

Modernisering av [Spell 16 (Floating Labels)](#16-floating-labels). Tar bort kravet på att `<label>` måste ligga direkt efter `<input>` i DOM:en via sibling-selektorn (`+`). Fungerar direkt med omslutande etikett-containrar.

```html
<div class="floating-field">
  <input id="email" type="email" placeholder=" " required>
  <label for="email">E-postadress</label>
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
*Formulär · Baseline · Markup*

Fullständig flerstegsguide som växlar steg, visar progress och Tillbaka/Nästa — helt utan skript, driven av radio-tillstånd och `:has()`.

```html
<form class="wizard">
  <input class="sr-only" type="radio" name="wstep" id="w-1" checked>
  <input class="sr-only" type="radio" name="wstep" id="w-2">
  <input class="sr-only" type="radio" name="wstep" id="w-3">

  <ol class="wz-steps" aria-label="Wizard-steg">
    <li><label for="w-1">1 · Konto</label></li>
    <li><label for="w-2">2 · Adress</label></li>
    <li><label for="w-3">3 · Betalning</label></li>
  </ol>

  <div class="wz-progress" aria-hidden="true"><span></span></div>

  <section class="wz-panel wz-1">
    <h2>Konto</h2>
    <div class="wz-nav"><span></span><label class="btn" for="w-2">Nästa →</label></div>
  </section>
  <section class="wz-panel wz-2">
    <h2>Adress</h2>
    <div class="wz-nav"><label class="btn ghost" for="w-1">← Tillbaka</label><label class="btn" for="w-3">Nästa →</label></div>
  </section>
  <section class="wz-panel wz-3">
    <h2>Betalning</h2>
    <div class="wz-nav"><label class="btn ghost" for="w-2">← Tillbaka</label><button class="btn" type="submit">Slutför</button></div>
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
*Formulär · Baseline · 0 JS*

Native `<input type="range">` med temat tumme och spår — behåller inbyggd tangentbords-, steg- och skärmläsarsemantik.

```html
<label class="range-field">
  <span>Volym</span>
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
*Formulär · Baseline · Markup*

En felsammanfattning i toppen av en formulärgrupp som dyker upp först när något fält är ogiltigt efter interaktion.

```html
<fieldset class="field-group">
  <legend>Leverans</legend>
  <p class="group-error" role="alert">Vissa fält behöver rättas innan du går vidare.</p>
  <input type="text" name="street" placeholder="Gatuadress" required>
  <input type="text" name="zip" placeholder="Postnummer" pattern="\d{3}\s?\d{2}" required>
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

## Shape & visuell identitet

### 25. Media Scrim Lift
*Visuell · Baseline · 0 JS*

Bildkort får en mörkare overlay vid hover så rubriken blir läsbar.

```css
.media-card { position: relative; overflow: hidden; }
.media-card::after {
  content: "";
  position: absolute; inset: 0;
  background: linear-gradient(to top, oklch(0 0 0 / .52), oklch(0 0 0 / .08));
  transition: opacity 240ms cubic-bezier(0.16,1,0.3,1);
}
.media-card:hover::after,
.media-card:focus-within::after { opacity: .86; }
```

### 35. Inline Theme Switch (`light-dark()`)
*Visuell · Baseline · 0 JS*

```css
:root { color-scheme: light dark; }

.premium-card {
  background: light-dark(var(--color-surface), var(--color-surface-dark));
  color: light-dark(var(--color-text), var(--color-text-inverse));
  border: 1px solid light-dark(transparent, oklch(1 0 0 / 0.1));
}
```

### 51. Ribbon Cut Card (`shape()`)
*Visuell · Newer · 0 JS*

Distinkta notched eller ribbon-formade silhuetter via `shape()` i `clip-path`.

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
*Visuell · Newer · 0 JS*

Responsiva avdelare mellan sektioner som känns redaktionella.

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
*Visuell · Baseline · 0 JS*

Färggradient som roterar längs kortets kant. Möjligt eftersom `@property` tillåter typad interpolation av en `<angle>`.

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
*Visuell · Baseline · 0 JS*

Animera ett element längs en kurvad bana för dekorativa flytande element (bakgrundsformer, pricks-spår, ikon-cirkulering).

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
*Visuell · Baseline · 0 JS*

Text eller ikoner som automatiskt skiftar färg över bakomliggande bilder/mönster.

**WCAG-Varning:** Fungerar med maximal kontrast mot svarta/vita ytor. Undvik mot 50% mellan-grå bakgrunder där kontrastförhållandet 4.5:1 inte kan garanteras. Lägg till `isolation: isolate` på överordnad container för att förhindra att blend-moden läcker till hela sidan.

```css
.blend-container {
  isolation: isolate; /* Förhindrar läckage till body */
}

.contrast-text {
  color: white;
  mix-blend-mode: difference;
  font-weight: 700;
}
```

### 78. Smooth Multiline Text Fade Mask (`mask-image`)
*Visuell · Baseline · 0 JS*

Ersätter den tvära klippningen från `-webkit-line-clamp` med en mjuk tonad alfa-mask längst ner på långa textblock.

```css
.text-fade-clamp {
  max-height: 9lh; /* Max 9 rader text */
  overflow: hidden;
  mask-image: linear-gradient(to bottom, black 60%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, black 60%, transparent 100%);
}
```

---

## State-detektering med `:has`

### 13. Spotlight Focus
*State · Baseline · 0 JS*

Hovrat kort i en grid skärper sig medan syskonen dämpas.

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

Djuplänkad sektion får ett kort highlight-lager.

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

I täta listor och footers får hovrad länk fokus medan syskonen tonas ned.

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

Tom container ritar sin egen empty state utan JS-villkor.

```css
.data-grid { display: grid; gap: var(--space-4); }

.data-grid:empty::after,
.data-grid:not(:has(> *:not([hidden])))::after {
  content: "Inga resultat hittades.";
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

Klassisk "Läs mer"-expansion utan JS via dold checkbox och `:has`. Kombinera med Spell 33 för animerad expansion.

**A11y-kritiskt:** använd `.sr-only`-klassen (från Bas-skydd) på checkboxen, inte `hidden`-attributet eller `display: none`. Det behåller checkboxen i tab-ordningen och accessibility-trädet så tangentbordsanvändare kan toggla. `:has(.clamp-toggle:focus-visible)`-regeln nedan ger en synlig fokus-ring på labeln.

```html
<div class="clamp-wrapper">
  <input type="checkbox" id="read-more" class="clamp-toggle sr-only">
  <p class="clamp-text">...lång brödtext...</p>
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
.clamp-label::after { content: " Läs mer →"; }
.clamp-wrapper:has(.clamp-toggle:checked) .clamp-label::after { content: " Visa mindre"; }

/* Tangentbordsfokus syns på labeln när den dolda checkboxen får fokus */
.clamp-wrapper:has(.clamp-toggle:focus-visible) .clamp-label {
  outline: 2px solid var(--color-primary);
  outline-offset: 4px;
  border-radius: var(--radius-sm);
}
```

---

## Prestanda

### 41. Content-Visibility Turbo
*Prestanda · Baseline · 0 JS*

Renderingsmotorn hoppar över layout för element utanför viewporten. Stor vinst på långa sidor.

```css
.lazy-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 500px;
}
```

---

## Datavisualisering & Tabeller

### 94. Sticky Header + Zebra Data Table
*Data · Baseline · 0 JS*

Långa tabeller med fast rubrikrad, zebra-rader och rad-highlight vid hover/fokus — baslinjen för varje datatät SaaS-vy.

```html
<div class="table-scroller" tabindex="0" role="region" aria-label="Transaktioner">
  <table>
    <thead><tr><th>Datum</th><th>Kund</th><th>Belopp</th></tr></thead>
    <tbody>
      <tr><td>2026-08-01</td><td>Acme AB</td><td>12 400 kr</td></tr>
      <tr><td>2026-08-02</td><td>Nordic AB</td><td>8 900 kr</td></tr>
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

Miniatyr-stapeldiagram drivet av en inline `--v`-custom-property per stapel — 0-JS datavisualisering för dashboards och KPI-kort.

```html
<figure class="spark" role="img" aria-label="Försäljning per kvartal: 34, 58, 41, 72, 66, 90 procent — stigande trend">
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

Native `<progress>`/`<meter>` med varumärkesfärger — behåller inbyggd semantik, min/max-logik och skärmläsarstöd för lagring, kvoter och mål.

```html
<label class="prog-field">
  <span>Lagring <output>72%</output></span>
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


---

## Navigation (2026)

### 97. Invoker Command Drawer (`commandfor` + `closedby`)
*Navigation · Newer · Markup*

Off-canvas-meny som en nativ `<dialog>` — öppnas och stängs med Invoker Commands, light-dismiss via `closedby="any"`. Ingen `showModal()`, ingen click-outside-lyssnare.

```html
<button class="nav-open" commandfor="site-drawer" command="show-modal" aria-label="Öppna meny">
  Meny
</button>

<dialog id="site-drawer" class="nav-drawer" closedby="any">
  <form method="dialog">
    <button class="nav-close" commandfor="site-drawer" command="close" aria-label="Stäng meny">✕</button>
  </form>
  <nav aria-label="Mobilnavigering">
    <a href="/">Hem</a>
    <a href="/tjanster">Tjänster</a>
    <a href="/kontakt">Kontakt</a>
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
*Navigation · Progressive · Markup · → moderniserar 18 / 34*

Hover-, fokus- och long-press-tooltip utan `mouseenter`. `popover="hint"` stänger inte öppna `auto`-menyer. Browsern sätter implicit `aria-describedby` — lägg inte till `role="tooltip"` själv.

```html
<button type="button" class="icon-btn" interestfor="tip-save" aria-label="Spara">★</button>
<div id="tip-save" popover="hint" class="hint-tip">Spara i din lista</div>
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
*Navigation · Newer · Markup*

Djuplänka en scroll-snap-karusell till en specifik slide vid första render — utan `scrollIntoView()`. Första elementet med `scroll-initial-target: nearest` i trädordning vinner.

```html
<div class="init-carousel">
  <article class="slide" id="q1">Q1</article>
  <article class="slide is-initial" id="q2">Q2 — aktuell</article>
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
*Kort · Progressive · 0 JS*

Pinterest-packning i CSS. `display: grid-lanes` fyller kortaste kolumnen i DOM-ordning (korrekt läsordning, till skillnad från `column-count`). Fallback är vanlig grid.

```html
<ul class="lanes">
  <li><article class="card">Kort 1</article></li>
  <li><article class="card">Kort 2 med mer text</article></li>
  <li><article class="card">Kort 3</article></li>
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
}
```

### 101. Sibling-Index Stagger (`sibling-index()`)
*Kort · Progressive · 0 JS*

Staggerad reveal utan `--i`-custom properties. `sibling-index()` (1-baserat) och `sibling-count()` är CSS Values 5 tree-counting.

```html
<ul class="stagger">
  <li>Analys</li><li>Automation</li><li>API</li><li>Support</li>
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
}
@media (prefers-reduced-motion: reduce) {
  .stagger > * { animation: none; }
}
```

---

## Forms (2026)

### 102. `:open` Custom Select Chrome
*Formulär · Newer · 0 JS*

Stylea native `<select>` när pickern är öppen med Baseline 2026 `:open`. Kombinera med Spell 54 (`appearance: base-select`).

```html
<label class="select-field">
  <span>Bransch</span>
  <select class="premium-dropdown" name="industry">
    <option>Bygg</option>
    <option>VVS</option>
    <option>El</option>
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
*Formulär · Progressive · 0 JS*

Automatisk svart/vit text mot dynamisk bakgrund. `contrast-color()` returnerar svart eller vitt — kapsla i `@supports` och ge en manuell fallback.

```html
<span class="chip" style="--chip-bg: var(--color-primary)">Nyhet</span>
<span class="chip" style="--chip-bg: var(--color-accent)">Kampanj</span>
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
*Formulär · Progressive · 0 JS*

Villkorliga värden i property-värdet — media, style-query och supports — utan extra klasser. `if()` applicerar på elementet självt (till skillnad från `@container style()` som frågar en förälder).

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
*Formulär · Progressive · Markup*

Läs `data-value` som `<number>` och driv en mätare utan inline `--v` eller JS. Feature-detektera med `attr(x type(*))`.

```html
<div class="attr-meter" data-value="72" aria-label="Profil komplett till 72 procent">
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
}
```

---

## Overlays & Modals (2026)

### 106. Light-Dismiss Confirm Dialog (`closedby="any"`)
*Overlay · Newer · Markup*

Bekräftelsedialog som stängs med Esc *och* klick på backdrop. Öppnas med `command="show-modal"`. `closedby="closerequest"` är Esc-only; `"none"` kräver explicit stängknapp.

```html
<button class="btn" commandfor="confirm-delete" command="show-modal">Ta bort kund</button>

<dialog id="confirm-delete" class="confirm" closedby="any">
  <h2>Ta bort kund?</h2>
  <p>Åtgärden går inte att ångra.</p>
  <div class="confirm-actions">
    <button class="btn ghost" commandfor="confirm-delete" command="close">Avbryt</button>
    <button class="btn danger" commandfor="confirm-delete" command="close">Ta bort</button>
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
*Overlay · Newer · 0 JS*

Dölj ett ankarpositionerat element när triggern scrollat ur vyn (`anchors-visible`) eller när själva overlayt overflowar (`no-overflow`). Baseline 2026.

```css
.filter-panel {
  position: absolute;
  position-anchor: --filter-btn;
  position-area: bottom end;
  position-try-fallbacks: flip-inline, flip-block;
  position-visibility: anchors-visible;
}
```

Använd `no-overflow` när overlayt självt inte får hamna utanför viewporten. Fallback utan stöd: panelen syns som vanligt.

---

## Media (2026)

### 108. Find-in-Page Accordion (`hidden="until-found"`)
*Media · Newer · Markup*

Ihopfälld FAQ som fortfarande matchar webbläsarens Sök på sidan och fragment-länkar. Browsern tar bort `hidden` och scrollar till träffen. Kräver en box (inte `display: none` / `contents` / `inline`).

```html
<section class="faq-item">
  <a href="#moms-svar">Hoppa till svaret om moms</a>
  <h2>Ingår moms?</h2>
  <div id="moms-svar" class="faq-answer" hidden="until-found">
    <p>Ja. Alla priser på sajten anges inklusive moms om inget annat sägs.</p>
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

Delad element-transition mellan listkort och detaljsida. `view-transition-name` läses från `id` som `<custom-ident>`; `view-transition-class` grupperar animationen.

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
*Data · Progressive · Markup · → moderniserar 95*

Samma sparkline som Spell 95 men värdet bor i `data-v` — ingen inline `style="--v:…"`.

```html
<figure class="attr-spark" role="img" aria-label="Försäljning: 34, 58, 41, 72, 66, 90 procent">
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
}
.attr-spark span:last-child { background: var(--color-primary); }
```

### 111. View-Timeline KPI Fill
*Data · Progressive · 0 JS*

KPI-staplar fylls när de kommer in i viewporten via `animation-timeline: view()` — ingen IntersectionObserver.

```html
<div class="kpi" style="--kpi: 72%">
  <span>Konvertering</span>
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
*Typografi · Newer · 0 JS*

Stylea text-fragment-highlights från delade URL:er (`#:~:text=`). Syns när någon landar via en markerad länk.

```css
::target-text {
  background: oklch(from var(--color-primary) l c h / .28);
  color: var(--color-text);
  text-decoration: underline;
  text-decoration-thickness: 2px;
}
```

### 113. Reading-Flow Grid (`reading-flow`)
*Layout · Newer · 0 JS*

När grid-objekt packas om med `dense` eller explicit `order` ska Tab och skärmläsare följa den *visuella* radordningen, inte DOM-ordningen.

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

`flex-visual` / `flex-flow` för flex; `grid-columns` om kolumnordning är den semantiskt rätta.

### 114. Themed Scrollbars (`scrollbar-color`)
*Layout · Baseline · 0 JS*

Varumärkta scrollbars med standard-properties. `scrollbar-width: thin` på inbäddade paneler; behåll `auto` på `html` för discoverability.

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
*Formulär · Baseline · Markup*

0-JS dropzone-yta kring native file input. Stor klickytan är hela zonen; knappen är 44px.

```html
<label class="dropzone">
  <input type="file" name="brief" accept=".pdf,.docx">
  <span>Släpp brief eller välj fil</span>
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
*Visuell · Baseline · Markup*

Deklarativ ljus/mörk-växel utan JS. Checkboxen sätter `color-scheme` på `:root` via `:has()`; `light-dark()` (Spell 35) följer med.

```html
<label class="theme-switch">
  <input type="checkbox" class="sr-only" name="dark" id="theme-dark">
  <span class="theme-ui" aria-hidden="true"></span>
  Mörkt läge
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
*Overlay · Newer · Markup*

Primär åtgärd + overflow-meny i samma kontroll. Menyn är `[popover=auto]` fäst med anchor positioning.

```html
<div class="split">
  <a class="split-main" href="/offert">Begär offert</a>
  <button class="split-more" commandfor="split-menu" command="toggle-popover" aria-label="Fler åtgärder">▾</button>
  <div id="split-menu" popover="auto" class="split-menu">
    <a href="/offert?plan=pro">Pro-offert</a>
    <a href="/kontakt">Prata med sälj</a>
  </div>
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
*Formulär · Progressive · 0 JS*

Full native select-krom: egen chevron (`::picker-icon`) och bock i vald option (`::checkmark`). Kräver `appearance: base-select` (Spell 54).

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
}
```


### 119. Native Donut Chart (`conic-gradient` + `mask-image`)
*Data · Baseline · 0 JS*

Ritar ett donut-diagram via `conic-gradient` där centrum klipps ut med `mask-image`. 

```html
<div class="donut-chart" role="img" aria-label="Fördelning: 65% Kärnverksamhet, 20% Admin, 15% R&D" style="--p1: 65; --p2: 20;">
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

Kortgalleri som filtrerar visade objekt baserat på valda kryssrutor helt utan JavaScript.

```html
<div class="filter-matrix-wrap">
  <div class="filter-controls">
    <label class="filter-chip"><input type="checkbox" id="f-tech" checked><span>Tech</span></label>
    <label class="filter-chip"><input type="checkbox" id="f-design"><span>Design</span></label>
  </div>

  <div class="card-matrix">
    <article class="matrix-card" data-cat="tech">Tech-projekt</article>
    <article class="matrix-card" data-cat="design">Design-projekt</article>
  </div>
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

Inkrementerar en CSS-räknare när produkter bockas i, och ankrar badgen upp till headerns ikon.

```html
<header>
  <button id="cart-icon" class="cart-btn" aria-label="Varukorg">🛒</button>
</header>
<main class="cart-shop">
  <label class="btn"><input type="checkbox" class="add-to-cart sr-only"> Köp Produkt A</label>
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

Projektplanering och tidslinjeschema drivet av CSS Grid och custom properties.

```html
<figure class="gantt" role="region" aria-label="Projekt tidslinje">
  <div class="gantt-row" style="--start: 1; --span: 3;"><span>Research</span></div>
  <div class="gantt-row" style="--start: 3; --span: 5;"><span>Utveckling</span></div>
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

Aktivitetskalender där cellens färgintensitet beräknas proportionellt med `color-mix()`.

```html
<div class="heatmap-grid" role="img" aria-label="Aktivitetsmatris">
  <div class="cell" style="--val: 10" title="10 händelser"></div>
  <div class="cell" style="--val: 85" title="85 händelser"></div>
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

Horisontellt ytdiagram där segmenten storleksätts automatiskt utifrån viktning.

```html
<figure class="stack-bar" role="img" aria-label="Fördelning: 40% Drift, 60% Sälj">
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
*Data · Baseline · Markup*

SVG-linjediagram med scroll-driven ritningsanimation via `stroke-dasharray`.

```html
<figure class="line-chart-wrap" role="img" aria-label="Försäljningstrend Q1-Q4">
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

Länkar i sidonavigeringen lyser upp baserat på vilken sektion som befinner sig iyn.

```html
<nav class="spy-nav">
  <a href="#s1" class="spy-l1">Intro</a>
  <a href="#s2" class="spy-l2">Funktioner</a>
</nav>
<main>
  <section id="s1">Intro</section>
  <section id="s2">Funktioner</section>
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

Kaskadmenyer i flera nivåer där light-dismiss hanteras automatiskt av webbläsaren.

```html
<button commandfor="m-main" command="toggle-popover" class="btn">Exportera ▾</button>

<div id="m-main" popover="auto" class="menu-l1">
  <button commandfor="m-sub" command="show-popover" id="b-sub" class="sub-trig">Som fil ▸</button>
  <div id="m-sub" popover="auto" class="menu-l2">
    <button>PDF</button>
    <button>CSV</button>
  </div>
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
*Formulär · Baseline · Markup*

Utvärderar lösenordsstyrka dynamiskt via HTML-regex och kör mätaren via `:has()`.

```html
<div class="pwd-wrap">
  <input type="password" class="pwd-input" placeholder="Minst 8 tkn, siffra & versal" 
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
*Formulär · Baseline · Markup*

Klassiskt stjärnbetyg fyllt från vänster till höger med dolda radios och flex `row-reverse`.

```html
<fieldset class="star-rating">
  <legend class="sr-only">Betygsätt</legend>
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
*Formulär · Baseline · Markup*

Min/Max-intervallväljare med två överlappande native sliders där tummarna förblir interaktiva.

```html
<div class="double-slider">
  <input type="range" min="0" max="100" value="20" aria-label="Lägsta pris">
  <input type="range" min="0" max="100" value="80" aria-label="Högsta pris">
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
*Overlay · Newer · Markup*

Självstängande transient toast driven av CSS Keyframes utan skript.

```html
<button commandfor="auto-toast-1" command="show-popover" class="btn">Spara ändringar</button>

<div id="auto-toast-1" popover="manual" class="auto-toast">
  ✅ Ändringar sparades i molnet
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

Exklusiv accordion där webbläsaren automatiskt stänger syskonpaneler när en ny öppnas.

```html
<div class="faq-group">
  <details name="faq">
    <summary>Ingår fri support?</summary>
    <div class="faq-content">Ja, e-postsupport ingår i alla planer.</div>
  </details>
  <details name="faq">
    <summary>Hur fungerar fakturering?</summary>
    <div class="faq-content">Fakturering sker månadsvis i förskott.</div>
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

Växlar priser mellan månads- och årsdebitering visuellt utan JS.

```html
<div class="price-toggle-wrap">
  <fieldset class="billing-switch">
    <legend class="sr-only">Debiteringstyp</legend>
    <label><input type="radio" name="billing" id="b-m" checked> Månad</label>
    <label><input type="radio" name="billing" id="b-y"> År (−20%)</label>
  </fieldset>

  <div class="price-card">
    <p class="price-val price-monthly">199 kr / mån</p>
    <p class="price-val price-yearly">159 kr / mån</p>
  </div>
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
*Interaktion · Baseline · Markup*

Mobiloptimerad sveplista där en radera-knapp uppenbarar sig vid horisontell svepning.

```html
<ul class="swipe-list">
  <li class="swipe-item">
    <div class="swipe-content">Dokument_v1.pdf</div>
    <button class="swipe-action">Radera</button>
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

Flerlagers-parallax där bakgrunds- och förgrundselement rör sig i asynkrona hastigheter vid scroll.

```html
<header class="plx-hero">
  <div class="plx-layer plx-bg" aria-hidden="true"></div>
  <div class="plx-layer plx-fg"><h1>Framtidens UI</h1></div>
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
*Formulär · Baseline · Markup*

Sökfält med native autokompletteringsmeny via `<datalist>`.

```html
<label for="city-search">Sök stad</label>
<input type="search" id="city-search" list="cities" placeholder="T.ex. Stockholm">
<datalist id="cities">
  <option value="Stockholm"></option>
  <option value="Göteborg"></option>
  <option value="Malmö"></option>
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
*Formulär · Baseline · Markup*

Kompakt söknapp som expanderar till ett fullskaligt sökfält vid klick/fokus.

```html
<form class="search-expand">
  <input type="search" placeholder="Sök..." aria-label="Sök">
  <button type="submit" aria-label="Genomför sökning">🔍</button>
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
*Typografi · Newer · 0 JS*

Redaktionell anfangen/drop cap för ingressparagrafer.

```html
<p class="prose-dropcap">Det var en gång en ny standard för webben...</p>
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

Taktil bildavslöjning med `clip-path` som torkar in bilden synkat med scroll.

```html
<figure class="img-wipe"><img src="/photo.jpg" alt="Beskrivning"></figure>
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
}
```

### 140. Sticky Footer Reveal Layout
*Layout · Baseline · 0 JS*

Sidans footer ligger placerad i botten och avtäcks när det huvudsakliga innehållet rullar uppåt.

```html
<main class="main-reveal">Huvudinnehåll</main>
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

Tangentbordsanpassad hopplänk som glider in överst på skärmen vid fokus.

```html
<a href="#main-content" class="skip-link">Hoppa till innehåll</a>
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
*Overlay · Newer · Markup*

Kartnålar som öppnar förankrade popovers vid klick.

```html
<div class="map-container">
  <button id="pin-1" commandfor="pop-pin-1" command="toggle-popover" class="map-pin" style="top: 30%; left: 40%;">📍</button>
  <div id="pop-pin-1" popover="auto" class="pin-pop">Stockholm HK</div>
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

Regelsett för utskrifter som döljer krom och skriver ut URL:er i klartext.

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

Räknar antalet valda checkboxes i en lista och visar summan i en rubrik utan skript.

```html
<div class="count-summary-group">
  <h3>Valda tjänster (<span class="count-output"></span>)</h3>
  <label><input type="checkbox" class="count-item"> Webbdesign</label>
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
*Typografi · Progressive · 0 JS*

Räknar upp ett numeriskt värde från 0 till ett målvärde med ren CSS.

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
*Overlay · Baseline · Markup*

Modal-dialog som förhindrar Scroll Chaining (att bakgrunden rör sig vid scroll i modalen).

```html
<dialog id="guard-modal" class="guard-modal" closedby="any">
  <h2>Modalinnehåll</h2>
  <div class="guard-body">Långt skrollbart innehåll...</div>
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

---

# Färdiga stacks

Komponerade kombinationer för olika projekttyper. Alla använder Bas-skydd som bas. Stacks som innehåller Spell 43 eller 47 markeras med † och kräver Root scroll-state preset.

---

## Astro-mappning

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

## Färdiga Astro-stacks

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
