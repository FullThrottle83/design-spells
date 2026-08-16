#!/usr/bin/env python3
"""Translate the design-spells catalogue and emit public/spells.js."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "README.md").read_text(encoding="utf-8")

# Longest-first phrase replacements covering prose, headings, HTML, and comments.
REPLACEMENTS: list[tuple[str, str]] = [
    (
        "En enda **canonical** referensbank över design spells för moderna Astro-projekt där målet är **0 klient-JS**. Den här filen slår ihop originalets spellbibliotek med en Astro-first struktur och **utesluter alla spells märkta `+ JS`**.",
        "A single **canonical** reference bank of design spells for modern Astro projects whose goal is **0 client JS**. This file merges the original spell library with an Astro-first structure and **excludes every spell marked `+ JS`**.",
    ),
    (
        "Dokumentet innehåller därför endast spells märkta **`0 JS`** eller **`Markup`**. I originalfilens terminologi betyder `Markup` att spellen fortfarande är JS-fri men kräver ett tydligt HTML-mönster, till exempel `<details>`, checkbox-state, `popover`, `dialog`-kompatibel struktur eller annan native state-machine.",
        "The document therefore contains only spells marked **`0 JS`** or **`Markup`**. In the original file's terminology, `Markup` still means the spell is JS-free, but it needs a precise HTML pattern — for example `<details>`, checkbox state, `popover`, a `dialog`-compatible structure, or another native state machine.",
    ),
    (
        "Totalt ingår **144 Astro-relevanta spells**. Exkluderade `+ JS`-spells: **4, 42**. Spells **97–146** är 2026-tillägg (Invoker Commands, Interest Invokers, Grid Lanes, `if()`, typed `attr()`, `closedby`, `hidden=\"until-found\"`, Conic Donut, Faceted Matrix, Cart Badge, Gantt, Heatmap, SVG Draw, Section-Spy, Password Meter, Star Rating, Auto Toast, Exclusive Accordion, Swipe Action, Parallax, Datalist, Drop Cap, Image Wipe, Sticky Footer, Skip Link, Map Pin, Dynamic Counter, Animated Counter, Focus-Lock Modal).",
        "In total there are **144 Astro-relevant spells**. Excluded `+ JS` spells: **4, 42**. Spells **97–146** are 2026 additions (Invoker Commands, Interest Invokers, Grid Lanes, `if()`, typed `attr()`, `closedby`, `hidden=\"until-found\"`, Conic Donut, Faceted Matrix, Cart Badge, Gantt, Heatmap, SVG Draw, Section-Spy, Password Meter, Star Rating, Auto Toast, Exclusive Accordion, Swipe Action, Parallax, Datalist, Drop Cap, Image Wipe, Sticky Footer, Skip Link, Map Pin, Dynamic Counter, Animated Counter, Focus-Lock Modal).",
    ),
    (
        "Touch-vänlig och tillgänglig före/efter-bildjämförelse helt utan JS. Scroller exporterar en namngiven `scroll-timeline` via `timeline-scope` så clip-path kan animeras på en *syskon*-yta (inte på scroller-elementet själv). Stödjer svepgester och piltangenter (`tabindex=\"0\"`). `role=\"region\"` — inte `slider` — eftersom `aria-valuenow` inte kan uppdateras utan JS.",
        "A touch-friendly, accessible before/after image comparison with no JavaScript. The scroller exports a named `scroll-timeline` via `timeline-scope` so `clip-path` can animate on a *sibling* surface (not on the scroller itself). Supports swipe gestures and arrow keys (`tabindex=\"0\"`). Use `role=\"region\"` — not `slider` — because `aria-valuenow` cannot be updated without JS.",
    ),
    (
        "Megameny som fälls ut från en nav-trigger via Invoker Commands (`commandfor` + `command=\"toggle-popover\"`) och nativ `[popover=auto]`, fäst med anchor positioning. Ger Esc-stängning, light-dismiss och fokus-hantering helt utan skript. Sätt inte statisk `aria-expanded` — native popover sköter tillgänglighetsträdet.",
        "A mega menu that opens from a nav trigger via Invoker Commands (`commandfor` + `command=\"toggle-popover\"`) and native `[popover=auto]`, pinned with anchor positioning. Escape, light-dismiss, and focus handling come for free. Do not set a static `aria-expanded` — the native popover owns the accessibility tree.",
    ),
    (
        "**A11y-kritiskt:** använd `.sr-only`-klassen (från Bas-skydd) på checkboxen, inte `hidden`-attributet eller `display: none`. Det behåller checkboxen i tab-ordningen och accessibility-trädet så tangentbordsanvändare kan toggla. `:has(.clamp-toggle:focus-visible)`-regeln nedan ger en synlig fokus-ring på labeln.",
        "**A11y-critical:** put the `.sr-only` class (from Base safeguards) on the checkbox — not the `hidden` attribute or `display: none`. That keeps the checkbox in the tab order and the accessibility tree so keyboard users can toggle it. The `:has(.clamp-toggle:focus-visible)` rule below paints a visible focus ring on the label.",
    ),
    (
        "Modernisering av [Spell 16 (Floating Labels)](#16-floating-labels). Tar bort kravet på att `<label>` måste ligga direkt efter `<input>` i DOM:en via sibling-selektorn (`+`). Fungerar direkt med omslutande etikett-containrar.",
        "A modernization of [Spell 16 (Floating Labels)](#16-floating-labels). Removes the requirement that `<label>` sit immediately after `<input>` in the DOM via the sibling combinator (`+`). Works with wrapping label containers.",
    ),
    (
        "**WCAG-Varning:** Fungerar med maximal kontrast mot svarta/vita ytor. Undvik mot 50% mellan-grå bakgrunder där kontrastförhållandet 4.5:1 inte kan garanteras. Lägg till `isolation: isolate` på överordnad container för att förhindra att blend-moden läcker till hela sidan.",
        "**WCAG warning:** Maximum contrast is guaranteed against black or white surfaces. Avoid 50% mid-grey backgrounds where a 4.5:1 contrast ratio cannot be guaranteed. Add `isolation: isolate` on the parent container so the blend mode does not leak to the whole page.",
    ),
    (
        "Lägg till detta **endast** om du använder Spell 43 (Auto-Hide Header) eller Spell 47 (Scroll-Awake Back-to-Top). Spells 44, 45 och 46 sätter upp lokala scroll-state-containers själva och behöver inte detta.",
        "Add this **only** if you use Spell 43 (Auto-Hide Header) or Spell 47 (Scroll-Awake Back-to-Top). Spells 44, 45, and 46 set up local scroll-state containers themselves and do not need this.",
    ),
    (
        "`container-type: scroll-state` ignoreras tyst i browsers utan stöd, så presetet är säker att inkludera även där fallback krävs. Det är dock opinionerat nog att inte vara default.",
        "`container-type: scroll-state` is ignored silently in browsers without support, so the preset is safe to include even where a fallback is required. It is opinionated enough not to be the default.",
    ),
    (
        "Komponerade kombinationer för olika projekttyper. Alla använder Bas-skydd som bas. Stacks som innehåller Spell 43 eller 47 markeras med † och kräver Root scroll-state preset.",
        "Composed combinations for different project types. Every stack starts from Base safeguards. Stacks that include Spell 43 or 47 are marked with † and require the Root scroll-state preset.",
    ),
    (
        "Fullständig flerstegsguide som växlar steg, visar progress och Tillbaka/Nästa — helt utan skript, driven av radio-tillstånd och `:has()`.",
        "A complete multi-step wizard that switches steps, shows progress, and offers Back/Next — no script, driven by radio state and `:has()`.",
    ),
    (
        "Hover-, fokus- och long-press-tooltip utan `mouseenter`. `popover=\"hint\"` stänger inte öppna `auto`-menyer. Browsern sätter implicit `aria-describedby` — lägg inte till `role=\"tooltip\"` själv.",
        "A hover, focus, and long-press tooltip with no `mouseenter`. `popover=\"hint\"` does not close open `auto` menus. The browser sets implicit `aria-describedby` — do not add `role=\"tooltip\"` yourself.",
    ),
    (
        "Pinterest-packning i CSS. `display: grid-lanes` fyller kortaste kolumnen i DOM-ordning (korrekt läsordning, till skillnad från `column-count`). Fallback är vanlig grid.",
        "Pinterest packing in CSS. `display: grid-lanes` fills the shortest column in DOM order (correct reading order, unlike `column-count`). Fallback is a regular grid.",
    ),
    (
        "Ihopfälld FAQ som fortfarande matchar webbläsarens Sök på sidan och fragment-länkar. Browsern tar bort `hidden` och scrollar till träffen. Kräver en box (inte `display: none` / `contents` / `inline`).",
        "A collapsed FAQ that still matches the browser's Find in page and fragment links. The browser removes `hidden` and scrolls to the hit. Requires a box (not `display: none` / `contents` / `inline`).",
    ),
    (
        "Villkorliga värden i property-värdet — media, style-query och supports — utan extra klasser. `if()` applicerar på elementet självt (till skillnad från `@container style()` som frågar en förälder).",
        "Conditional values in the property value itself — media, style query, and supports — with no extra classes. `if()` applies to the element itself (unlike `@container style()`, which queries a parent).",
    ),
    (
        "Off-canvas-meny som en nativ `<dialog>` — öppnas och stängs med Invoker Commands, light-dismiss via `closedby=\"any\"`. Ingen `showModal()`, ingen click-outside-lyssnare.",
        "An off-canvas menu as a native `<dialog>` — opened and closed with Invoker Commands, light-dismissed via `closedby=\"any\"`. No `showModal()`, no click-outside listener.",
    ),
    (
        "Bekräftelsedialog som stängs med Esc *och* klick på backdrop. Öppnas med `command=\"show-modal\"`. `closedby=\"closerequest\"` är Esc-only; `\"none\"` kräver explicit stängknapp.",
        "A confirm dialog that closes on Escape *and* backdrop click. Opened with `command=\"show-modal\"`. `closedby=\"closerequest\"` is Escape-only; `\"none\"` requires an explicit close button.",
    ),
    (
        "Dölj ett ankarpositionerat element när triggern scrollat ur vyn (`anchors-visible`) eller när själva overlayt overflowar (`no-overflow`). Baseline 2026.",
        "Hide an anchor-positioned element when the trigger scrolls out of view (`anchors-visible`) or when the overlay itself overflows (`no-overflow`). Baseline 2026.",
    ),
    (
        "Native `<input type=\"range\">` med temat tumme och spår — behåller inbyggd tangentbords-, steg- och skärmläsarsemantik.",
        "A native `<input type=\"range\">` with a themed thumb and track — keeps built-in keyboard, step, and screen-reader semantics.",
    ),
    (
        "Miniatyr-stapeldiagram drivet av en inline `--v`-custom-property per stapel — 0-JS datavisualisering för dashboards och KPI-kort.",
        "A miniature bar chart driven by an inline `--v` custom property per bar — 0-JS data visualization for dashboards and KPI cards.",
    ),
    (
        "Native `<progress>`/`<meter>` med varumärkesfärger — behåller inbyggd semantik, min/max-logik och skärmläsarstöd för lagring, kvoter och mål.",
        "Native `<progress>`/`<meter>` with brand colors — keeps built-in semantics, min/max logic, and screen-reader support for storage, quotas, and goals.",
    ),
    (
        "Långa tabeller med fast rubrikrad, zebra-rader och rad-highlight vid hover/fokus — baslinjen för varje datatät SaaS-vy.",
        "Long tables with a sticky header row, zebra stripes, and row highlight on hover/focus — the baseline for every data-dense SaaS view.",
    ),
    (
        "Helt native paginering och nästa/föregående-knappar för scroll-snap-karuseller. Eliminerar de sista JS-biblioteken (Swiper, Embla, Splide) för standardkaruseller.",
        "Fully native pagination and previous/next buttons for scroll-snap carousels. Removes the last JS libraries (Swiper, Embla, Splide) for standard carousels.",
    ),
    (
        "Pill-indikator i segmented controls/flikar som glider sömlöst till aktivt val med `:has()` och CSS-variabler (`--total-items`).",
        "A pill indicator in segmented controls/tabs that glides to the active choice with `:has()` and CSS variables (`--total-items`).",
    ),
    (
        "Djuplänka en scroll-snap-karusell till en specifik slide vid första render — utan `scrollIntoView()`. Första elementet med `scroll-initial-target: nearest` i trädordning vinner.",
        "Deep-link a scroll-snap carousel to a specific slide on first render — no `scrollIntoView()`. The first element with `scroll-initial-target: nearest` in tree order wins.",
    ),
    (
        "Staggerad reveal utan `--i`-custom properties. `sibling-index()` (1-baserat) och `sibling-count()` är CSS Values 5 tree-counting.",
        "A staggered reveal with no `--i` custom properties. `sibling-index()` (1-based) and `sibling-count()` are CSS Values 5 tree-counting functions.",
    ),
    (
        "Stylea native `<select>` när pickern är öppen med Baseline 2026 `:open`. Kombinera med Spell 54 (`appearance: base-select`).",
        "Style a native `<select>` while the picker is open with Baseline 2026 `:open`. Combine with Spell 54 (`appearance: base-select`).",
    ),
    (
        "Automatisk svart/vit text mot dynamisk bakgrund. `contrast-color()` returnerar svart eller vitt — kapsla i `@supports` och ge en manuell fallback.",
        "Automatic black/white text against a dynamic background. `contrast-color()` returns black or white — wrap it in `@supports` and provide a manual fallback.",
    ),
    (
        "Läs `data-value` som `<number>` och driv en mätare utan inline `--v` eller JS. Feature-detektera med `attr(x type(*))`.",
        "Read `data-value` as a `<number>` and drive a meter with no inline `--v` or JS. Feature-detect with `attr(x type(*))`.",
    ),
    (
        "Delad element-transition mellan listkort och detaljsida. `view-transition-name` läses från `id` som `<custom-ident>`; `view-transition-class` grupperar animationen.",
        "A shared-element transition between a list card and a detail page. `view-transition-name` is read from `id` as a `<custom-ident>`; `view-transition-class` groups the animation.",
    ),
    (
        "När grid-objekt packas om med `dense` eller explicit `order` ska Tab och skärmläsare följa den *visuella* radordningen, inte DOM-ordningen.",
        "When grid items are repacked with `dense` or explicit `order`, Tab and screen readers should follow the *visual* row order, not the DOM order.",
    ),
    (
        "Varumärkta scrollbars med standard-properties. `scrollbar-width: thin` på inbäddade paneler; behåll `auto` på `html` för discoverability.",
        "Branded scrollbars with standard properties. Use `scrollbar-width: thin` on embedded panels; keep `auto` on `html` for discoverability.",
    ),
    (
        "Full native select-krom: egen chevron (`::picker-icon`) och bock i vald option (`::checkmark`). Kräver `appearance: base-select` (Spell 54).",
        "Full native select chrome: a custom chevron (`::picker-icon`) and a checkmark on the selected option (`::checkmark`). Requires `appearance: base-select` (Spell 54).",
    ),
    (
        "Deklarativ ljus/mörk-växel utan JS. Checkboxen sätter `color-scheme` på `:root` via `:has()`; `light-dark()` (Spell 35) följer med.",
        "A declarative light/dark switch with no JS. The checkbox sets `color-scheme` on `:root` via `:has()`; `light-dark()` (Spell 35) follows along.",
    ),
    (
        "Använd `no-overflow` när overlayt självt inte får hamna utanför viewporten. Fallback utan stöd: panelen syns som vanligt.",
        "Use `no-overflow` when the overlay itself must not leave the viewport. Fallback without support: the panel stays visible as usual.",
    ),
    (
        "`flex-visual` / `flex-flow` för flex; `grid-columns` om kolumnordning är den semantiskt rätta.",
        "`flex-visual` / `flex-flow` for flex; `grid-columns` if column order is the semantically correct one.",
    ),
    (
        "Samma sparkline som Spell 95 men värdet bor i `data-v` — ingen inline `style=\"--v:…\"`.",
        "The same sparkline as Spell 95, but the value lives in `data-v` — no inline `style=\"--v:…\"`.",
    ),
    (
        "KPI-staplar fylls när de kommer in i viewporten via `animation-timeline: view()` — ingen IntersectionObserver.",
        "KPI bars fill as they enter the viewport via `animation-timeline: view()` — no IntersectionObserver.",
    ),
    (
        "Stylea text-fragment-highlights från delade URL:er (`#:~:text=`). Syns när någon landar via en markerad länk.",
        "Style text-fragment highlights from shared URLs (`#:~:text=`). Visible when someone lands via a marked link.",
    ),
    (
        "0-JS dropzone-yta kring native file input. Stor klickytan är hela zonen; knappen är 44px.",
        "A 0-JS dropzone around a native file input. The whole zone is the hit target; the button is 44px.",
    ),
    (
        "Primär åtgärd + overflow-meny i samma kontroll. Menyn är `[popover=auto]` fäst med anchor positioning.",
        "A primary action plus overflow menu in the same control. The menu is `[popover=auto]` pinned with anchor positioning.",
    ),
    (
        "Klassisk \"Läs mer\"-expansion utan JS via dold checkbox och `:has`. Kombinera med Spell 33 för animerad expansion.",
        "Classic “Read more” expansion with no JS, via a hidden checkbox and `:has`. Combine with Spell 33 for animated expansion.",
    ),
    (
        "En felsammanfattning i toppen av en formulärgrupp som dyker upp först när något fält är ogiltigt efter interaktion.",
        "An error summary at the top of a form group that appears only after a field is invalid following interaction.",
    ),
    (
        "Native `<select>` blir fullt styleable inklusive den utfällda menyn. Dödar headless-bibliotek för standard-dropdowns.",
        "A native `<select>` becomes fully styleable, including the open menu. Retires headless libraries for standard dropdowns.",
    ),
    (
        "Tabeller med `position: sticky` visar skuggor och avdelare mot kanterna *endast* när innehållet faktiskt är skrollat horisontellt.",
        "Tables with `position: sticky` show edge shadows and dividers *only* when the content has actually been scrolled horizontally.",
    ),
    (
        "Bilder andas långsamt (scale 1.12 → 1 → 1.12) synkat med sin position i viewporten utan en enda skroll-listener.",
        "Images breathe slowly (scale 1.12 → 1 → 1.12) synced to their position in the viewport, with no scroll listener.",
    ),
    (
        "**Obs:** Kräver dubblerad HTML-markup (två identiska `.marquee-track`) för att snurra utan glapp. Pausas automatiskt vid `:hover` och `:focus-within` för tillgänglighet.",
        "**Note:** Requires duplicated HTML markup (two identical `.marquee-track` elements) to loop without a gap. Pauses automatically on `:hover` and `:focus-within` for accessibility.",
    ),
    (
        "Svävande snabbknapp (FAB) som expanderar undermenyer via nativ `<details>` och `@starting-style`.",
        "A floating action button (FAB) that expands child actions via native `<details>` and `@starting-style`.",
    ),
    (
        "**Guardrails:** `pointer-events: none` på wrapper förhindrar att osynliga klickytor täcker skärmen. Alla knappar uppfyller WCAG minsta klickytor (44x44px).",
        "**Guardrails:** `pointer-events: none` on the wrapper stops invisible hit areas covering the screen. Every button meets WCAG minimum hit targets (44×44px).",
    ),
    (
        "Pill-navigering och chips med äkta \"squircle\"-silhuett (superelliptisk hörnrundning) istället för vanliga `border-radius`-bågar.",
        "Pill navigation and chips with a true “squircle” silhouette (superellipse corner rounding) instead of ordinary `border-radius` arcs.",
    ),
    (
        "Brödsmulor som visar en diskret \"+N\"-hint och kantmaskning endast när raden faktiskt är skrollbar.",
        "Breadcrumbs that show a discreet “+N” hint and edge masking only when the row is actually scrollable.",
    ),
    (
        "Kortet lutar sig subtilt i 3D vid hover/fokus för djupkänsla — utan mus-spårning och utan extra DOM-lager.",
        "The card tilts subtly in 3D on hover/focus for a sense of depth — no mouse tracking and no extra DOM layers.",
    ),
    (
        "Svävande snabbknapp som solfjädrar ut underliggande åtgärder i en båge via nativa CSS `cos()` / `sin()`.",
        "A floating action button that fans child actions into an arc via native CSS `cos()` / `sin()`.",
    ),
    (
        "Minskar sticky header-höjd och skalar ner logotypen mjukt när användaren scrollar ner på sidan utan layout shifts.",
        "Shrinks the sticky header and scales the logo down as the user scrolls, without layout shifts.",
    ),
    (
        "Sömlös mjuk toning och oskärpa på `::backdrop` för nativa `<dialog>` och `[popover]`-modaler utan JS.",
        "A seamless fade and blur on `::backdrop` for native `<dialog>` and `[popover]` modals, with no JS.",
    ),
    (
        "List- och kortelement tonas fram i sekvens när användaren scrollar ner, synkat mot viewport-positionen.",
        "List and card items fade in sequence as the user scrolls, synced to viewport position.",
    ),
    (
        "Klicka på en bild för att förstora den till fullskärmsläge med nativ `popover` utan tunga lightbox-bibliotek.",
        "Click an image to enlarge it to a fullscreen view with a native `popover` — no heavy lightbox library.",
    ),
    (
        "Bildtexter i en scroll-snap-karusell tonas in först när slidet är \"snapped\".",
        "Captions in a scroll-snap carousel fade in only once the slide is “snapped”.",
    ),
    (
        "Header glider undan på scroll ned, kommer tillbaka på scroll upp. **Kräver Root scroll-state preset.**",
        "The header slides away on scroll down and returns on scroll up. **Requires the Root scroll-state preset.**",
    ),
    (
        "Sticky-element får extra skugga och border bara när det faktiskt fastnat. Mycket mer premium än permanent skugga.",
        "A sticky element gains extra shadow and border only once it is actually stuck. Much more premium than a permanent shadow.",
    ),
    (
        "Aktiv slide i en scroll-snap-container får full skärpa medan syskonen tonas ned.",
        "The active slide in a scroll-snap container gets full sharpness while siblings fade down.",
    ),
    (
        "Visa edge-fades, pilar eller \"swipe me\"-hintar bara när innehållet faktiskt går att skrolla.",
        "Show edge fades, arrows, or “swipe me” hints only when the content is actually scrollable.",
    ),
    (
        "Floating-knapp som vaknar först när användaren rört sidan. **Kräver Root scroll-state preset.**",
        "A floating button that wakes only after the user has moved the page. **Requires the Root scroll-state preset.**",
    ),
    (
        "Kort staplas på varandra som en kortlek när användaren scrollar. Skala och dimning synkat med exit-crossing.",
        "Cards stack like a deck as the user scrolls. Scale and dimming stay synced to the exit-crossing.",
    ),
    (
        "Scrollerns egna kanter blir bokstavligen genomskinliga. Fungerar oavsett bakgrundsfärg eller mönster bakom.",
        "The scroller’s own edges become literally transparent. Works regardless of the background color or pattern behind it.",
    ),
    (
        "Trädvy för dokumentation eller sidomenyer byggd med nästlade `<details>`-element utan JS.",
        "A tree view for documentation or sidebars built from nested `<details>` elements, with no JS.",
    ),
    (
        "Dialog som automatiskt uppför sig som en Bottom Sheet på mobiler och en centrerad modal på större skärmar.",
        "A dialog that behaves as a bottom sheet on phones and a centered modal on larger screens.",
    ),
    (
        "Behåll för enkel hover-text på element där `overflow: hidden` inte är ett problem.",
        "Keep this for simple hover text on elements where `overflow: hidden` is not a problem.",
    ),
    (
        "Klipper bort fontens osynliga luft (leading) ovanför versaler och under baslinje. `padding: 1rem` blir nu exakt 1rem från bokstävernas kant.",
        "Trims the font’s invisible leading above capitals and below the baseline. `padding: 1rem` is now exactly 1rem from the letter edges.",
    ),
    (
        "Aktiverar avstavning för smala kolumner och brödtext på en specifik språkkod. Förhindrar både \"ravinen\" och horribla orphan-rader.",
        "Enables hyphenation for narrow columns and body copy for a specific language. Prevents both “rivers” and ugly orphan lines.",
    ),
    (
        "Kräver att `<html lang=\"sv\">` är korrekt satt för att svensk avstavning ska fungera.",
        "Requires `<html lang=\"en\">` (or the correct language) so hyphenation dictionaries can run.",
    ),
    (
        "0-JS state-maskin: submit låst tills alla fält är giltiga. Ogiltiga fält shake:ar vid blur.",
        "A 0-JS state machine: submit stays locked until every field is valid. Invalid fields shake on blur.",
    ),
    (
        "Animera ett element längs en kurvad bana för dekorativa flytande element (bakgrundsformer, pricks-spår, ikon-cirkulering).",
        "Animate an element along a curved path for decorative floating pieces (background shapes, dotted trails, orbiting icons).",
    ),
    (
        "Ersätter den tvära klippningen från `-webkit-line-clamp` med en mjuk tonad alfa-mask längst ner på långa textblock.",
        "Replaces the hard clip from `-webkit-line-clamp` with a soft faded alpha mask at the bottom of long text blocks.",
    ),
    (
        "Renderingsmotorn hoppar över layout för element utanför viewporten. Stor vinst på långa sidor.",
        "The rendering engine skips layout for elements outside the viewport. A big win on long pages.",
    ),
    (
        "Kortgalleri som filtrerar visade objekt baserat på valda kryssrutor helt utan JavaScript.",
        "A card gallery that filters visible items from checked boxes, with no JavaScript.",
    ),
    (
        "Inkrementerar en CSS-räknare när produkter bockas i, och ankrar badgen upp till headerns ikon.",
        "Increments a CSS counter when products are checked, and anchors the badge to the header icon.",
    ),
    (
        "Projektplanering och tidslinjeschema drivet av CSS Grid och custom properties.",
        "Project planning and a timeline schedule driven by CSS Grid and custom properties.",
    ),
    (
        "Aktivitetskalender där cellens färgintensitet beräknas proportionellt med `color-mix()`.",
        "An activity calendar where each cell’s color intensity is computed proportionally with `color-mix()`.",
    ),
    (
        "Horisontellt ytdiagram där segmenten storleksätts automatiskt utifrån viktning.",
        "A horizontal stacked bar whose segments size themselves from their weights.",
    ),
    (
        "SVG-linjediagram med scroll-driven ritningsanimation via `stroke-dasharray`.",
        "An SVG line chart with a scroll-driven draw animation via `stroke-dasharray`.",
    ),
    (
        "Länkar i sidonavigeringen lyser upp baserat på vilken sektion som befinner sig iyn.",
        "Sidebar links light up based on which section is in view.",
    ),
    (
        "Kaskadmenyer i flera nivåer där light-dismiss hanteras automatiskt av webbläsaren.",
        "Multi-level cascade menus whose light-dismiss is handled automatically by the browser.",
    ),
    (
        "Utvärderar lösenordsstyrka dynamiskt via HTML-regex och kör mätaren via `:has()`.",
        "Evaluates password strength dynamically via HTML regex and drives the meter with `:has()`.",
    ),
    (
        "Klassiskt stjärnbetyg fyllt från vänster till höger med dolda radios och flex `row-reverse`.",
        "A classic star rating that fills left to right with hidden radios and flex `row-reverse`.",
    ),
    (
        "Min/Max-intervallväljare med två överlappande native sliders där tummarna förblir interaktiva.",
        "A min/max range picker with two overlapping native sliders whose thumbs stay interactive.",
    ),
    (
        "Självstängande transient toast driven av CSS Keyframes utan skript.",
        "A self-dismissing transient toast driven by CSS keyframes, with no script.",
    ),
    (
        "Exklusiv accordion där webbläsaren automatiskt stänger syskonpaneler när en ny öppnas.",
        "An exclusive accordion where the browser automatically closes sibling panels when a new one opens.",
    ),
    (
        "Växlar priser mellan månads- och årsdebitering visuellt utan JS.",
        "Visually switches prices between monthly and yearly billing with no JS.",
    ),
    (
        "Mobiloptimerad sveplista där en radera-knapp uppenbarar sig vid horisontell svepning.",
        "A mobile-first swipe list where a delete button appears on a horizontal swipe.",
    ),
    (
        "Flerlagers-parallax där bakgrunds- och förgrundselement rör sig i asynkrona hastigheter vid scroll.",
        "Multi-layer parallax where background and foreground move at different speeds on scroll.",
    ),
    (
        "Sökfält med native autokompletteringsmeny via `<datalist>`.",
        "A search field with a native autocomplete menu via `<datalist>`.",
    ),
    (
        "Kompakt söknapp som expanderar till ett fullskaligt sökfält vid klick/fokus.",
        "A compact search button that expands into a full search field on click/focus.",
    ),
    (
        "Redaktionell anfangen/drop cap för ingressparagrafer.",
        "An editorial drop cap for lead paragraphs.",
    ),
    (
        "Taktil bildavslöjning med `clip-path` som torkar in bilden synkat med scroll.",
        "A tactile image reveal with `clip-path` that wipes the image in, synced to scroll.",
    ),
    (
        "Sidans footer ligger placerad i botten och avtäcks när det huvudsakliga innehållet rullar uppåt.",
        "The page footer sits at the bottom and is revealed as the main content scrolls up.",
    ),
    (
        "Tangentbordsanpassad hopplänk som glider in överst på skärmen vid fokus.",
        "A keyboard-first skip link that slides in at the top of the screen on focus.",
    ),
    (
        "Kartnålar som öppnar förankrade popovers vid klick.",
        "Map pins that open anchored popovers on click.",
    ),
    (
        "Regelsett för utskrifter som döljer krom och skriver ut URL:er i klartext.",
        "A print stylesheet that hides chrome and prints URLs in plaintext.",
    ),
    (
        "Räknar antalet valda checkboxes i en lista och visar summan i en rubrik utan skript.",
        "Counts checked boxes in a list and shows the total in a heading, with no script.",
    ),
    (
        "Räknar upp ett numeriskt värde från 0 till ett målvärde med ren CSS.",
        "Counts a numeric value from 0 to a target with pure CSS.",
    ),
    (
        "Modal-dialog som förhindrar Scroll Chaining (att bakgrunden rör sig vid scroll i modalen).",
        "A modal dialog that prevents scroll chaining (the background moving while the modal scrolls).",
    ),
    (
        "Ritar ett donut-diagram via `conic-gradient` där centrum klipps ut med `mask-image`.",
        "Draws a donut chart via `conic-gradient` with the center cut out by `mask-image`.",
    ),
    (
        "Skapa hover/active-varianter direkt från en grundfärg utan att hårdkoda extra tokens.",
        "Build hover/active variants directly from a base color without hard-coding extra tokens.",
    ),
    (
        "One-liner som färgar alla native formulärkontroller (radio, checkbox, range, progress).",
        "A one-liner that tints every native form control (radio, checkbox, range, progress).",
    ),
    (
        "Wrapper-baserad fokusfeedback för sammansatta inputs och sökrutor.",
        "Wrapper-based focus feedback for composite inputs and search boxes.",
    ),
    (
        "Animera bara de egenskaper som faktiskt ändras. Aldrig `transition: all`.",
        "Animate only the properties that actually change. Never `transition: all`.",
    ),
    (
        "Stor premiumeffekt för multipage-sajter. Browsern hanterar MPA-navigeringen nativt.",
        "A large premium effect for multi-page sites. The browser handles MPA navigation natively.",
    ),
    (
        "Mjuk fade-in från `display: none` utan JS. Perfekt för popover-menyer (`[popover]`-attribut) och native modaler.",
        "A soft fade-in from `display: none` with no JS. Perfect for popover menus (`[popover]`) and native modals.",
    ),
    (
        "Smidigt oändligt rullande logoband med kantutoning via `mask-image`.",
        "A smooth infinite logo marquee with edge fades via `mask-image`.",
    ),
    (
        "Rubrik fylld med bild eller gradient via `background-clip: text`.",
        "A headline filled with an image or gradient via `background-clip: text`.",
    ),
    (
        "Header får frostat glas först när användaren scrollat lite.",
        "The header becomes frosted glass only after the user has scrolled a little.",
    ),
    (
        "Sticky bottom CTA får mer separation när den ligger ovanpå innehåll.",
        "A sticky bottom CTA gains more separation when it sits on top of content.",
    ),
    (
        "Tunn progressindikator som drivs helt av scroll-position.",
        "A thin progress indicator driven entirely by scroll position.",
    ),
    (
        "Behåll för bredare browser-kompatibilitet eller äldre projekt.",
        "Keep this for broader browser compatibility or older projects.",
    ),
    (
        "Behåll endast om bakgrunden är solid och statisk. Annars använd Spell 56.",
        "Keep this only if the background is solid and static. Otherwise use Spell 56.",
    ),
    (
        "Modernisering av Spell 15. Animerar `block-size: 0` → `auto` direkt.",
        "A modernization of Spell 15. Animates `block-size: 0` → `auto` directly.",
    ),
    (
        "Bonus: `<details name=\"faq\">` ger automatiskt exclusive accordion (syskon stängs när nytt öppnas).",
        "Bonus: `<details name=\"faq\">` gives you an exclusive accordion automatically (siblings close when a new one opens).",
    ),
    (
        "Kort som anpassar sin layout efter sin container, inte viewporten.",
        "A card that adapts its layout to its container, not the viewport.",
    ),
    (
        "Kort i en grid delar exakt samma rad-linjal trots olika innehållsmängd.",
        "Cards in a grid share the exact same row tracks despite different amounts of content.",
    ),
    (
        "Riktiga flikar via `<details name=\"ui-tabs\">`. Inga radio-button-hack.",
        "Real tabs via `<details name=\"ui-tabs\">`. No radio-button hack.",
    ),
    (
        "Tooltips fästa via `anchor-name` / `position-anchor`. Inga overflow-problem.",
        "Tooltips pinned via `anchor-name` / `position-anchor`. No overflow problems.",
    ),
    (
        "Fältvalideringsfel fästs till input-fältet utan att trycka ned layouten.",
        "Field validation errors pin to the input without pushing the layout down.",
    ),
    (
        "Filtermenyer, sorteringspaneler och account-menus fästa till sin trigger.",
        "Filter menus, sort panels, and account menus pinned to their trigger.",
    ),
    (
        "Kontextuellt hjälpinnehåll dyker upp bredvid ett fält vid `:focus-within`.",
        "Contextual help appears beside a field on `:focus-within`.",
    ),
    (
        "Använd stenhårt på alla knappar, brickor och kortrubriker. Fallbacken är osynlig.",
        "Use this relentlessly on every button, chip, and card heading. The fallback is invisible.",
    ),
    (
        "Använd alltid riktig `<label>`. Placeholder-tricket ersätter aldrig etiketten semantiskt.",
        "Always use a real `<label>`. The placeholder trick never replaces the label semantically.",
    ),
    (
        "`:user-valid` / `:user-invalid` triggas först efter interaktion, aldrig vid sidladdning.",
        "`:user-valid` / `:user-invalid` fire only after interaction, never on page load.",
    ),
    (
        "Wizard-steg numreras med CSS counters utan markup-logik.",
        "Wizard steps are numbered with CSS counters and no markup logic.",
    ),
    (
        "Textarea växer med innehåll utan JS-listeners.",
        "A textarea that grows with its content, with no JS listeners.",
    ),
    (
        "Bildkort får en mörkare overlay vid hover så rubriken blir läsbar.",
        "A media card gets a darker overlay on hover so the heading stays readable.",
    ),
    (
        "Distinkta notched eller ribbon-formade silhuetter via `shape()` i `clip-path`.",
        "Distinct notched or ribbon-shaped silhouettes via `shape()` in `clip-path`.",
    ),
    (
        "Responsiva avdelare mellan sektioner som känns redaktionella.",
        "Responsive dividers between sections that feel editorial.",
    ),
    (
        "Färggradient som roterar längs kortets kant. Möjligt eftersom `@property` tillåter typad interpolation av en `<angle>`.",
        "A color gradient that rotates along the card’s edge. Possible because `@property` allows typed interpolation of an `<angle>`.",
    ),
    (
        "Text eller ikoner som automatiskt skiftar färg över bakomliggande bilder/mönster.",
        "Text or icons that automatically invert over the images or patterns behind them.",
    ),
    (
        "Hovrat kort i en grid skärper sig medan syskonen dämpas.",
        "The hovered card in a grid sharpens while its siblings recede.",
    ),
    (
        "Djuplänkad sektion får ett kort highlight-lager.",
        "A deep-linked section gets a short highlight flash.",
    ),
    (
        "I täta listor och footers får hovrad länk fokus medan syskonen tonas ned.",
        "In dense lists and footers the hovered link keeps focus while siblings fade.",
    ),
    (
        "Tom container ritar sin egen empty state utan JS-villkor.",
        "An empty container draws its own empty state with no JS condition.",
    ),
    (
        "Biljett-/kupongkort med äkta perforerade \"hål\" i kanterna via pseudo-element.",
        "A ticket/coupon card with real perforated “holes” on the edges via pseudo-elements.",
    ),
    (
        "Sekundära kortåtgärder döljs tills kortet hovras eller fokuseras.",
        "Secondary card actions stay hidden until the card is hovered or focused.",
    ),
    (
        "Bekräftelse-toasts som visas när en länk sätter `#toast-…` och stängs via en stängningslänk.",
        "Confirmation toasts that appear when a link sets `#toast-…` and close via a dismiss link.",
    ),
    (
        "Klickstyrd åtgärdsmeny (⋯) fäst till sin trigger med anchor positioning och automatisk flip vid skärmkanter.",
        "A click-driven action menu (⋯) pinned to its trigger with anchor positioning and automatic flip at the screen edges.",
    ),
    (
        "En subtil ljusglimt sveper över knappen vid hover.",
        "A subtle light gleam sweeps across the button on hover.",
    ),
    (
        "Mikroskopisk nedskalning på `:active` för taktil feedback.",
        "A microscopic scale-down on `:active` for tactile feedback.",
    ),
    (
        "Kortet lyfts, bilden zoomas in långsamt.",
        "The card lifts and the image zooms in slowly.",
    ),
    (
        "Underline glider in i stället för att blinka fram.",
        "The underline slides in instead of blinking on.",
    ),
    (
        "Scroll-driven text reveal med `animation-timeline: view()`.",
        "A scroll-driven text reveal with `animation-timeline: view()`.",
    ),
    (
        "Lätt 3D-settle på load.",
        "A light 3D settle on load.",
    ),
    (
        "CSS-driven laddningsyta.",
        "A CSS-driven loading surface.",
    ),
    (
        "Originalfilens metadata behålls inne i spellsektionerna:",
        "The original file’s metadata is kept inside each spell section:",
    ),
    (
        "Detta är fundamentet alla spells bygger på. Ladda före allt annat.",
        "This is the foundation every spell builds on. Load it before anything else.",
    ),
    (
        "- Introducera inte klient-JS för sådant som redan löses av dokumentets JS-fria spells.",
        "- Do not introduce client JS for something this document already solves with a JS-free spell.",
    ),
    (
        "- Föredra spells som passar direkt i `.astro`-komponenter eller layout-CSS.",
        "- Prefer spells that drop straight into `.astro` components or layout CSS.",
    ),
    (
        "- Om flera spells löser samma problem ska den modernaste hållbara väljas först.",
        "- If several spells solve the same problem, pick the most modern sustainable one first.",
    ),
    (
        "- Referera alltid till spells med stabilt nummer, till exempel `Spell 43`.",
        "- Always refer to spells by their stable number, for example `Spell 43`.",
    ),
    (
        "- Använd helst 1–2 visuellt dominanta spells per sektion.",
        "- Prefer 1–2 visually dominant spells per section.",
    ),
    (
        "- Börja med Baseline-spells, gå vidare till Newer och sedan Progressive.",
        "- Start with Baseline spells, then Newer, then Progressive.",
    ),
    (
        "- Kopiera CSS-blocket och byt ut projektets tokens där det behövs.",
        "- Copy the CSS block and swap in the project’s tokens where needed.",
    ),
    (
        "- Läs metadata-raden direkt under rubriken.",
        "- Read the metadata line directly under the heading.",
    ),
    (
        "- Bläddra till en kategori som matchar problemet.",
        "- Browse to a category that matches the problem.",
    ),
    (
        "- Komponentlokal CSS är oftast bättre än globalt läckande selectors.",
        "- Component-local CSS is usually better than globally leaking selectors.",
    ),
    (
        "- Motion är enhancement och ska respektera `prefers-reduced-motion`.",
        "- Motion is enhancement and must respect `prefers-reduced-motion`.",
    ),
    (
        "- Läsbarhet, fokus och layout går före dekor.",
        "- Readability, focus, and layout come before decoration.",
    ),
    (
        "- Astro-fit före demo-effekt.",
        "- Astro fit before demo effect.",
    ),
    (
        "- Progressive enhancement före hårda beroenden.",
        "- Progressive enhancement before hard dependencies.",
    ),
    (
        "- Native browser state före handbyggda lösningar.",
        "- Native browser state before hand-built solutions.",
    ),
    (
        "- 0 klient-JS som standard.",
        "- 0 client JS by default.",
    ),
    (
        "- HTML + CSS först.",
        "- HTML + CSS first.",
    ),
    (
        "- **Kategori** = funktionell typ av spell.",
        "- **Category** = the functional type of the spell.",
    ),
    (
        "- **Status** = browserrisk: `Baseline`, `Newer`, `Progressive`.",
        "- **Status** = browser risk: `Baseline`, `Newer`, `Progressive`.",
    ),
    (
        "- **JS-behov** = här förekommer bara `0 JS` och `Markup` i denna canonical Astro-utgåva.",
        "- **JS need** = only `0 JS` and `Markup` appear in this canonical Astro edition.",
    ),
    (
        "- **0 JS**: direkt lämplig i statisk Astro-markup.",
        "- **0 JS**: ready for static Astro markup.",
    ),
    (
        "- **Markup**: fortfarande JS-fri, men kräver mer exakt HTML-struktur.",
        "- **Markup**: still JS-free, but needs a more exact HTML structure.",
    ),
    (
        "- **Baseline**: trygg att använda direkt.",
        "- **Baseline**: safe to use immediately.",
    ),
    (
        "- **Newer**: bra i moderna projekt, testa gärna i kritiska UI-flöden.",
        "- **Newer**: good in modern projects; test it in critical UI flows.",
    ),
    (
        "- **Progressive**: ska kapslas i `@supports` eller få tyst fallback.",
        "- **Progressive**: wrap it in `@supports` or give it a silent fallback.",
    ),
    (
        "- Globala spells: `base.css` eller global design layer.",
        "- Global spells: `base.css` or the global design layer.",
    ),
    (
        "- Nya browserfeatures: nära komponenten bakom `@supports`.",
        "- New browser features: next to the component, behind `@supports`.",
    ),
    (
        "1. Välj högst 1–2 visuellt dominanta spells per sektion.",
        "1. Pick at most 1–2 visually dominant spells per section.",
    ),
    (
        "2. Välj Baseline före Newer och Newer före Progressive.",
        "2. Prefer Baseline over Newer, and Newer over Progressive.",
    ),
    (
        "3. Prioritera fokus, kontrast, spacing och informationshierarki.",
        "3. Prioritize focus, contrast, spacing, and information hierarchy.",
    ),
    (
        "4. Lägg prestandaspells tidigt på långa sidor.",
        "4. Place performance spells early on long pages.",
    ),
    (
        "5. Använd native state (`:has()`, `:focus-within`, `<details>`, `scroll-snap`, `scroll-state`) innan du uppfinner egna mönster.",
        "5. Use native state (`:has()`, `:focus-within`, `<details>`, `scroll-snap`, `scroll-state`) before inventing your own patterns.",
    ),
    (
        "- För många hover-only-spells i touch-tunga gränssnitt.",
        "- Too many hover-only spells in touch-heavy interfaces.",
    ),
    (
        "- För många blur- eller backdrop-effekter i samma viewport.",
        "- Too many blur or backdrop effects in the same viewport.",
    ),
    (
        "- För många reveal-effekter samtidigt.",
        "- Too many reveal effects at once.",
    ),
    (
        "- För mycket specialmarkup utan tydligt värde.",
        "- Too much special markup without a clear payoff.",
    ),
    (
        "- För mycket dekoration innan läsbarhet och state-feedback fungerar.",
        "- Too much decoration before readability and state feedback work.",
    ),
    ("### Rekommenderad placering i Astro", "### Recommended placement in Astro"),
    ("### Praktisk tolkning för Astro", "### Practical reading for Astro"),
    ("### För AI-agenter och editor-agenter", "### For AI agents and editor agents"),
    ("### För människor", "### For humans"),
    ("## Hur dokumentet används", "## How to use this document"),
    ("## Kärnprinciper", "## Core principles"),
    ("## Metadata och tolkning", "## Metadata and how to read it"),
    ("## Bas-skydd", "## Base safeguards"),
    ("## Urvalsregler", "## Selection rules"),
    ("## Interaktion & feedback", "## Interaction & feedback"),
    ("## Reveal & rörelse", "## Reveal & motion"),
    ("## Layout & komposition", "## Layout & composition"),
    ("## Anchor & positionering", "## Anchor & positioning"),
    ("## Typografi", "## Typography"),
    ("## Formulär & state", "## Forms & state"),
    ("## Shape & visuell identitet", "## Shape & visual identity"),
    ("## State-detektering med `:has`", "## State detection with `:has`"),
    ("## Prestanda", "## Performance"),
    ("## Datavisualisering & Tabeller", "## Data visualization & tables"),
    ("# Färdiga stacks", "# Ready-made stacks"),
    ("## Astro-mappning", "## Astro mapping"),
    ("## Färdiga Astro-stacks", "## Ready-made Astro stacks"),
    ("### 1. Shimmer på primärknappar", "### 1. Shimmer on primary buttons"),
    ("### 3. Lift & Zoom på kort", "### 3. Lift & Zoom on cards"),
    ("### 8. Gradient Reveal på rubriker", "### 8. Gradient Reveal on headings"),
    ("### 9. Depth Parallax på hero", "### 9. Depth Parallax on hero"),
    ("### 12. Scroll Snap-galleri", "### 12. Scroll Snap gallery"),
    ("### Bonus. Typografisk Harmoni (`text-wrap`)", "### Bonus. Typographic Harmony (`text-wrap`)"),
    ("*Interaktion · Baseline · 0 JS*", "*Interaction · Baseline · 0 JS*"),
    ("*Interaktion · Newer · Markup*", "*Interaction · Newer · Markup*"),
    ("*Interaktion · Baseline · Markup*", "*Interaction · Baseline · Markup*"),
    ("*Navigation · Newer · Markup*", "*Navigation · Newer · Markup*"),
    ("*Navigation · Newer · 0 JS*", "*Navigation · Newer · 0 JS*"),
    ("*Navigation · Progressive · Markup · → moderniserar 18 / 34*", "*Navigation · Progressive · Markup · → modernizes 18 / 34*"),
    ("*Navigation · Progressive · 0 JS*", "*Navigation · Progressive · 0 JS*"),
    ("*Navigation · Baseline · 0 JS*", "*Navigation · Baseline · 0 JS*"),
    ("*Kort · Baseline · 0 JS*", "*Cards · Baseline · 0 JS*"),
    ("*Kort · Progressive · 0 JS*", "*Cards · Progressive · 0 JS*"),
    ("*Overlay · Baseline · 0 JS*", "*Overlays · Baseline · 0 JS*"),
    ("*Overlay · Newer · Markup*", "*Overlays · Newer · Markup*"),
    ("*Overlay · Baseline · Markup*", "*Overlays · Baseline · Markup*"),
    ("*Overlay · Newer · 0 JS*", "*Overlays · Newer · 0 JS*"),
    ("*Reveal · Progressive · 0 JS*", "*Reveal · Progressive · 0 JS*"),
    ("*Reveal · Baseline · 0 JS*", "*Reveal · Baseline · 0 JS*"),
    ("*Reveal · Newer · 0 JS*", "*Reveal · Newer · 0 JS*"),
    ("*Reveal · Baseline · Markup*", "*Reveal · Baseline · Markup*"),
    ("*Reveal · Newer · Markup*", "*Reveal · Newer · Markup*"),
    ("*Media · Progressive · 0 JS*", "*Media · Progressive · 0 JS*"),
    ("*Media · Baseline · 0 JS*", "*Media · Baseline · 0 JS*"),
    ("*Media · Newer · Markup*", "*Media · Newer · Markup*"),
    ("*Media · Newer · 0 JS*", "*Media · Newer · 0 JS*"),
    ("*Media · Progressive · Markup*", "*Media · Progressive · Markup*"),
    ("*Scroll-driven · Newer · 0 JS*", "*Scroll-driven · Newer · 0 JS*"),
    ("*Scroll-driven · Baseline · 0 JS*", "*Scroll-driven · Baseline · 0 JS*"),
    ("*Scroll-driven · Progressive · 0 JS*", "*Scroll-driven · Progressive · 0 JS*"),
    ("*Scroll-state · Newer · 0 JS*", "*Scroll-state · Newer · 0 JS*"),
    ("*Layout · Baseline · Markup · → 33 är modernare*", "*Layout · Baseline · Markup · → 33 is more modern*"),
    ("*Layout · Baseline · 0 JS · → 56 är modernare*", "*Layout · Baseline · 0 JS · → 56 is more modern*"),
    ("*Layout · Baseline · 0 JS · ersätter 27 i de flesta fall*", "*Layout · Baseline · 0 JS · replaces 27 in most cases*"),
    ("*Layout · Baseline · Markup*", "*Layout · Baseline · Markup*"),
    ("*Layout · Baseline · 0 JS*", "*Layout · Baseline · 0 JS*"),
    ("*Layout · Newer · Markup*", "*Layout · Newer · Markup*"),
    ("*Layout · Progressive · 0 JS*", "*Layout · Progressive · 0 JS*"),
    ("*Layout · Newer · 0 JS*", "*Layout · Newer · 0 JS*"),
    ("*Anchor (legacy) · Baseline · 0 JS · → 34 är modernare*", "*Anchor (legacy) · Baseline · 0 JS · → 34 is more modern*"),
    ("*Anchor · Newer · 0 JS*", "*Anchor · Newer · 0 JS*"),
    ("*Typografi · Baseline · 0 JS*", "*Typography · Baseline · 0 JS*"),
    ("*Typografi · Newer · 0 JS*", "*Typography · Newer · 0 JS*"),
    ("*Typografi · Progressive · 0 JS*", "*Typography · Progressive · 0 JS*"),
    ("*Formulär · Baseline · 0 JS*", "*Forms · Baseline · 0 JS*"),
    ("*Formulär · Progressive · 0 JS*", "*Forms · Progressive · 0 JS*"),
    ("*Formulär · Baseline · Markup*", "*Forms · Baseline · Markup*"),
    ("*Formulär · Newer · 0 JS*", "*Forms · Newer · 0 JS*"),
    ("*Formulär · Progressive · Markup*", "*Forms · Progressive · Markup*"),
    ("*Visuell · Baseline · 0 JS*", "*Visual · Baseline · 0 JS*"),
    ("*Visuell · Newer · 0 JS*", "*Visual · Newer · 0 JS*"),
    ("*Visuell · Baseline · Markup*", "*Visual · Baseline · Markup*"),
    ("*State · Baseline · 0 JS*", "*State · Baseline · 0 JS*"),
    ("*State · Baseline · Markup*", "*State · Baseline · Markup*"),
    ("*Prestanda · Baseline · 0 JS*", "*Performance · Baseline · 0 JS*"),
    ("*Data · Baseline · 0 JS*", "*Data · Baseline · 0 JS*"),
    ("*Data · Baseline · Markup*", "*Data · Baseline · Markup*"),
    ("*Data · Progressive · Markup · → moderniserar 95*", "*Data · Progressive · Markup · → modernizes 95*"),
    ("*Data · Progressive · 0 JS*", "*Data · Progressive · 0 JS*"),
    ("*Data · Progressive · Markup*", "*Data · Progressive · Markup*"),
    ("- Page chrome: `MainLayout.astro`, `Header.astro`, `Shell.astro`.", "- Page chrome: `MainLayout.astro`, `Header.astro`, `Shell.astro`."),
    ("- Komponentspells: lokal CSS i `.astro`-komponenter.", "- Component spells: local CSS in `.astro` components."),
    ("Prioritet för val: **Baseline → Newer → Progressive**.", "Selection priority: **Baseline → Newer → Progressive**."),
    ("  /* Förhindrar layout shift när dialog/popover öppnas och låser rullningslisten */", "  /* Prevents layout shift when a dialog/popover opens and locks the scrollbar */"),
    ("  /* Förhindrar oönskat textzoombeteende på mobila enheter */", "  /* Prevents unwanted text zoom on mobile devices */"),
    ("  /* Förhindrar att djuplänkat innehåll hamnar under sticky header (se Spell 17) */", "  /* Prevents deep-linked content from landing under a sticky header (see Spell 17) */"),
    ("/* Universell fokus-baslinje för tangentbordsnavigering */", "/* Universal focus baseline for keyboard navigation */"),
    ("/* Förhindrar att scroll läcker upp till parent/body i inbäddade scrollers */", "/* Prevents scroll from leaking to the parent/body in nested scrollers */"),
    ("/* WCAG 2.2 AA / mobil: minsta tryckyta för knappar, länkar, summary, labels. */", "/* WCAG 2.2 AA / mobile: minimum hit target for buttons, links, summary, labels. */"),
    (
        "/* Visuellt dold men kvar i tab-ordning och accessibility-trädet.\n   Använd för checkboxar/inputs som driver markup-state-machines (se Spell 60). */",
        "/* Visually hidden but still in the tab order and accessibility tree.\n   Use for checkboxes/inputs that drive markup state machines (see Spell 60). */",
    ),
    ('    <img src="/after.jpg" alt="Efter" class="compare-img compare-after">', '    <img src="/after.jpg" alt="After" class="compare-img compare-after">'),
    ('    <img src="/before.jpg" alt="Före" class="compare-img compare-before">', '    <img src="/before.jpg" alt="Before" class="compare-img compare-before">'),
    (
        '  <div class="compare-scroller" tabindex="0" role="region" aria-label="Jämför före och efter. Svep eller använd piltangenter.">',
        '  <div class="compare-scroller" tabindex="0" role="region" aria-label="Compare before and after. Swipe or use the arrow keys.">',
    ),
    ('  <label for="seg-1">Översikt</label>', '  <label for="seg-1">Overview</label>'),
    ("  <label for=\"seg-2\">Analys</label>", '  <label for="seg-2">Analytics</label>'),
    ('  <label for="seg-3">Inställningar</label>', '  <label for="seg-3">Settings</label>'),
    ('  <summary class="fab-main" aria-label="Snabbåtgärder">+</summary>', '  <summary class="fab-main" aria-label="Quick actions">+</summary>'),
    (
        '    <button class="fab-child" title="Nytt inlägg" aria-label="Nytt inlägg">📝</button>',
        '    <button class="fab-child" title="New post" aria-label="New post">📝</button>',
    ),
    (
        '    <button class="fab-child" title="Ladda upp bild" aria-label="Ladda upp bild">📷</button>',
        '    <button class="fab-child" title="Upload image" aria-label="Upload image">📷</button>',
    ),
    (
        '    <button class="fab-child" title="Dela sida" aria-label="Dela sida">🔗</button>',
        '    <button class="fab-child" title="Share page" aria-label="Share page">🔗</button>',
    ),
    ("    Produkter <span aria-hidden=\"true\">▾</span>", "    Products <span aria-hidden=\"true\">▾</span>"),
    ('      <li><a href="/api">API & Integrationer</a></li>', '      <li><a href="/api">API & Integrations</a></li>'),
    ('<nav class="squircle-nav" aria-label="Huvudnavigering">', '<nav class="squircle-nav" aria-label="Main navigation">'),
    ('  <a href="/" aria-current="page">Översikt</a>', '  <a href="/" aria-current="page">Overview</a>'),
    ('  <a href="/reports">Rapporter</a>', '  <a href="/reports">Reports</a>'),
    ('  <a href="/settings">Inställningar</a>', '  <a href="/settings">Settings</a>'),
    ('<nav class="crumbs-wrap" aria-label="Brödsmulor">', '<nav class="crumbs-wrap" aria-label="Breadcrumb">'),
    ("    <li><a href=\"/\">Hem</a></li>", '    <li><a href="/">Home</a></li>'),
    ('    <li><a href="/docs">Dokumentation</a></li>', '    <li><a href="/docs">Documentation</a></li>'),
    ('    <li><a href="/docs/components">Komponenter</a></li>', '    <li><a href="/docs/components">Components</a></li>'),
    ("    <h3>Premium-plan</h3>", "    <h3>Premium plan</h3>"),
    ("    <p>Allt i Pro, plus prioriterad support och SSO.</p>", "    <p>Everything in Pro, plus priority support and SSO.</p>"),
    ('  <a href="/pricing">Välj plan</a>', '  <a href="/pricing">Choose plan</a>'),
    ("    <h3>Sommarerbjudande</h3>", "    <h3>Summer offer</h3>"),
    ("    <p>20% rabatt på alla årliga planer.</p>", "    <p>20% off every annual plan.</p>"),
    ("    <span>Kod: SOMMAR26</span>", "    <span>Code: SUMMER26</span>"),
    ("    <h3>Q3-rapport</h3>", "    <h3>Q3 report</h3>"),
    ('    <button aria-label="Redigera Q3-rapport">✏️</button>', '    <button aria-label="Edit Q3 report">✏️</button>'),
    ('    <button aria-label="Dela Q3-rapport">🔗</button>', '    <button aria-label="Share Q3 report">🔗</button>'),
    ('    <button aria-label="Arkivera Q3-rapport">📦</button>', '    <button aria-label="Archive Q3 report">📦</button>'),
    ('<a href="#toast-saved" class="btn">Spara ändringar</a>', '<a href="#toast-saved" class="btn">Save changes</a>'),
    (
        '  ✅ Sparat! <a href="#" class="toast-close" aria-label="Stäng notis">✕</a>',
        '  ✅ Saved! <a href="#" class="toast-close" aria-label="Dismiss notification">✕</a>',
    ),
    (
        '  <button class="ctx-btn" commandfor="ctx-menu" command="toggle-popover" aria-haspopup="menu" aria-label="Fler åtgärder">⋯</button>',
        '  <button class="ctx-btn" commandfor="ctx-menu" command="toggle-popover" aria-haspopup="menu" aria-label="More actions">⋯</button>',
    ),
    ('    <button role="menuitem">Redigera</button>', '    <button role="menuitem">Edit</button>'),
    ('    <button role="menuitem">Duplicera</button>', '    <button role="menuitem">Duplicate</button>'),
    ('    <button role="menuitem" class="danger">Ta bort</button>', '    <button role="menuitem" class="danger">Delete</button>'),
    ('  <summary class="fan-main" aria-label="Snabbåtgärder">＋</summary>', '  <summary class="fan-main" aria-label="Quick actions">＋</summary>'),
    (
        '    <button class="fan-item" style="--i:0" aria-label="Nytt inlägg">📝</button>',
        '    <button class="fan-item" style="--i:0" aria-label="New post">📝</button>',
    ),
    (
        '    <button class="fan-item" style="--i:1" aria-label="Ladda upp">📷</button>',
        '    <button class="fan-item" style="--i:1" aria-label="Upload">📷</button>',
    ),
    (
        '    <button class="fan-item" style="--i:2" aria-label="Dela">🔗</button>',
        '    <button class="fan-item" style="--i:2" aria-label="Share">🔗</button>',
    ),
    ("  <!-- Duplicerat spår för skarvlös loop -->", "  <!-- Duplicated track for a seamless loop -->"),
    ('  <img src="/photo-thumb.jpg" alt="Förstora bild">', '  <img src="/photo-thumb.jpg" alt="Enlarge image">'),
    ('  <img src="/photo-full.jpg" alt="Förstorad bild">', '  <img src="/photo-full.jpg" alt="Enlarged image">'),
    ('<figure class="kb"><img src="/hero-1.jpg" alt="Kustlandskap"></figure>', '<figure class="kb"><img src="/hero-1.jpg" alt="Coastal landscape"></figure>'),
    ("<h1 class=\"paint-headline\">Bygg snabbare. Leverera snyggare.</h1>", '<h1 class="paint-headline">Build faster. Ship prettier.</h1>'),
    ("    <figcaption class=\"caption\">Alperna — vinter 2026</figcaption>", '    <figcaption class="caption">The Alps — winter 2026</figcaption>'),
    ("    <figcaption class=\"caption\">Kusten — höst 2025</figcaption>", '    <figcaption class="caption">The coast — autumn 2025</figcaption>'),
    ("  /* Skapar automatiskt en knapp per slide */", "  /* Automatically creates one button per slide */"),
    ("  /* Native scroll-knappar */", "  /* Native scroll buttons */"),
    ("    <summary>Dokumentation</summary>", "    <summary>Documentation</summary>"),
    ('      <a href="/docs/start">Kom igång</a>', '      <a href="/docs/start">Get started</a>'),
    ("        <summary>Komponenter</summary>", "        <summary>Components</summary>"),
    ('          <a href="/docs/buttons">Knappar</a>', '          <a href="/docs/buttons">Buttons</a>'),
    ('          <a href="/docs/cards">Kort</a>', '          <a href="/docs/cards">Cards</a>'),
    ("  margin: auto auto 0 auto; /* Bottenplacerad på mobil */", "  margin: auto auto 0 auto; /* Bottom-aligned on mobile */"),
    ("/* Centrerad modal på desktop */", "/* Centered modal on desktop */"),
    ('  hyphenate-character: "\\2010";  /* riktigt bindestreck istället för minus */', '  hyphenate-character: "\\2010";  /* real hyphen instead of a minus */'),
    ("  hyphenate-limit-chars: 8 4 4;  /* min 8 tecken, 4 före brytning, 4 efter */", "  hyphenate-limit-chars: 8 4 4;  /* min 8 chars, 4 before the break, 4 after */"),
    ("  hyphenate-limit-lines: 2;       /* max 2 avstavade rader i rad */", "  hyphenate-limit-lines: 2;       /* max 2 hyphenated lines in a row */"),
    ("  hyphenate-limit-last: always;   /* aldrig avstava sista raden i ett stycke */", "  hyphenate-limit-last: always;   /* never hyphenate the last line of a paragraph */"),
    ('html[lang="sv"] body { hyphens: auto; }', 'html[lang="en"] body { hyphens: auto; }'),
    ('  <label for="email">E-postadress</label>', '  <label for="email">Email address</label>'),
    ('  <ol class="wz-steps" aria-label="Wizard-steg">', '  <ol class="wz-steps" aria-label="Wizard steps">'),
    ('    <li><label for="w-1">1 · Konto</label></li>', '    <li><label for="w-1">1 · Account</label></li>'),
    ('    <li><label for="w-2">2 · Adress</label></li>', '    <li><label for="w-2">2 · Address</label></li>'),
    ('    <li><label for="w-3">3 · Betalning</label></li>', '    <li><label for="w-3">3 · Payment</label></li>'),
    ("    <h2>Konto</h2>", "    <h2>Account</h2>"),
    ("    <h2>Adress</h2>", "    <h2>Address</h2>"),
    ("    <h2>Betalning</h2>", "    <h2>Payment</h2>"),
    (
        '    <div class="wz-nav"><span></span><label class="btn" for="w-2">Nästa →</label></div>',
        '    <div class="wz-nav"><span></span><label class="btn" for="w-2">Next →</label></div>',
    ),
    (
        '    <div class="wz-nav"><label class="btn ghost" for="w-1">← Tillbaka</label><label class="btn" for="w-3">Nästa →</label></div>',
        '    <div class="wz-nav"><label class="btn ghost" for="w-1">← Back</label><label class="btn" for="w-3">Next →</label></div>',
    ),
    (
        '    <div class="wz-nav"><label class="btn ghost" for="w-2">← Tillbaka</label><button class="btn" type="submit">Slutför</button></div>',
        '    <div class="wz-nav"><label class="btn ghost" for="w-2">← Back</label><button class="btn" type="submit">Finish</button></div>',
    ),
    ("    <span>Volym</span>", "    <span>Volume</span>"),
    ("  <legend>Leverans</legend>", "  <legend>Delivery</legend>"),
    (
        '  <p class="group-error" role="alert">Vissa fält behöver rättas innan du går vidare.</p>',
        '  <p class="group-error" role="alert">Some fields need fixing before you continue.</p>',
    ),
    ('  <input type="text" name="street" placeholder="Gatuadress" required>', '  <input type="text" name="street" placeholder="Street address" required>'),
    (
        r'  <input type="text" name="zip" placeholder="Postnummer" pattern="\d{3}\s?\d{2}" required>',
        '  <input type="text" name="zip" placeholder="Postal code" pattern="\\d{5}" required>',
    ),
    ("  isolation: isolate; /* Förhindrar läckage till body */", "  isolation: isolate; /* Prevents leaking to the body */"),
    ('  <p class="clamp-text">...lång brödtext...</p>', '  <p class="clamp-text">...long body copy...</p>'),
    ('.clamp-label::after { content: " Läs mer →"; }', '.clamp-label::after { content: " Read more →"; }'),
    ('.clamp-wrapper:has(.clamp-toggle:checked) .clamp-label::after { content: " Visa mindre"; }', '.clamp-wrapper:has(.clamp-toggle:checked) .clamp-label::after { content: " Show less"; }'),
    ("/* Tangentbordsfokus syns på labeln när den dolda checkboxen får fokus */", "/* Keyboard focus is visible on the label when the hidden checkbox is focused */"),
    ('  content: "Inga resultat hittades.";', '  content: "No results found.";'),
    (
        '<div class="table-scroller" tabindex="0" role="region" aria-label="Transaktioner">',
        '<div class="table-scroller" tabindex="0" role="region" aria-label="Transactions">',
    ),
    ("    <thead><tr><th>Datum</th><th>Kund</th><th>Belopp</th></tr></thead>", "    <thead><tr><th>Date</th><th>Customer</th><th>Amount</th></tr></thead>"),
    ("      <tr><td>2026-08-01</td><td>Acme AB</td><td>12 400 kr</td></tr>", "      <tr><td>2026-08-01</td><td>Acme Inc</td><td>$12,400</td></tr>"),
    ("      <tr><td>2026-08-02</td><td>Nordic AB</td><td>8 900 kr</td></tr>", "      <tr><td>2026-08-02</td><td>Nordic Inc</td><td>$8,900</td></tr>"),
    (
        '<figure class="spark" role="img" aria-label="Försäljning per kvartal: 34, 58, 41, 72, 66, 90 procent — stigande trend">',
        '<figure class="spark" role="img" aria-label="Sales by quarter: 34, 58, 41, 72, 66, 90 percent — rising trend">',
    ),
    ("  <span>Lagring <output>72%</output></span>", "  <span>Storage <output>72%</output></span>"),
    (
        '<button class="nav-open" commandfor="site-drawer" command="show-modal" aria-label="Öppna meny">',
        '<button class="nav-open" commandfor="site-drawer" command="show-modal" aria-label="Open menu">',
    ),
    ("  Meny", "  Menu"),
    (
        '    <button class="nav-close" commandfor="site-drawer" command="close" aria-label="Stäng meny">✕</button>',
        '    <button class="nav-close" commandfor="site-drawer" command="close" aria-label="Close menu">✕</button>',
    ),
    ('  <nav aria-label="Mobilnavigering">', '  <nav aria-label="Mobile navigation">'),
    ('    <a href="/">Hem</a>', '    <a href="/">Home</a>'),
    ('    <a href="/tjanster">Tjänster</a>', '    <a href="/services">Services</a>'),
    ('    <a href="/kontakt">Kontakt</a>', '    <a href="/contact">Contact</a>'),
    (
        '<button type="button" class="icon-btn" interestfor="tip-save" aria-label="Spara">★</button>',
        '<button type="button" class="icon-btn" interestfor="tip-save" aria-label="Save">★</button>',
    ),
    ('<div id="tip-save" popover="hint" class="hint-tip">Spara i din lista</div>', '<div id="tip-save" popover="hint" class="hint-tip">Save to your list</div>'),
    ('  <article class="slide" id="q2">Q2 — aktuell</article>', '  <article class="slide is-initial" id="q2">Q2 — current</article>'),
    ("    <li><article class=\"card\">Kort 1</article></li>", '    <li><article class="card">Card 1</article></li>'),
    ('    <li><article class="card">Kort 2 med mer text</article></li>', '    <li><article class="card">Card 2 with more text</article></li>'),
    ('    <li><article class="card">Kort 3</article></li>', '    <li><article class="card">Card 3</article></li>'),
    ("  <li>Analys</li><li>Automation</li><li>API</li><li>Support</li>", "  <li>Analytics</li><li>Automation</li><li>API</li><li>Support</li>"),
    ("    <span>Bransch</span>", "    <span>Industry</span>"),
    ("    <option>Bygg</option>", "    <option>Construction</option>"),
    ("    <option>VVS</option>", "    <option>Plumbing</option>"),
    ("    <option>El</option>", "    <option>Electrical</option>"),
    ('<span class="chip" style="--chip-bg: var(--color-primary)">Nyhet</span>', '<span class="chip" style="--chip-bg: var(--color-primary)">New</span>'),
    ('<span class="chip" style="--chip-bg: var(--color-accent)">Kampanj</span>', '<span class="chip" style="--chip-bg: var(--color-accent)">Sale</span>'),
    (
        '<div class="attr-meter" data-value="72" aria-label="Profil komplett till 72 procent">',
        '<div class="attr-meter" data-value="72" aria-label="Profile complete to 72 percent">',
    ),
    (
        '<button class="btn" commandfor="confirm-delete" command="show-modal">Ta bort kund</button>',
        '<button class="btn" commandfor="confirm-delete" command="show-modal">Delete customer</button>',
    ),
    ("  <h2>Ta bort kund?</h2>", "  <h2>Delete customer?</h2>"),
    ("  <p>Åtgärden går inte att ångra.</p>", "  <p>This cannot be undone.</p>"),
    (
        '    <button class="btn ghost" commandfor="confirm-delete" command="close">Avbryt</button>',
        '    <button class="btn ghost" commandfor="confirm-delete" command="close">Cancel</button>',
    ),
    (
        '    <button class="btn danger" commandfor="confirm-delete" command="close">Ta bort</button>',
        '    <button class="btn danger" commandfor="confirm-delete" command="close">Delete</button>',
    ),
    ('  <a href="#moms-svar">Hoppa till svaret om moms</a>', '  <a href="#vat-answer">Jump to the VAT answer</a>'),
    ("  <h2>Ingår moms?</h2>", "  <h2>Is VAT included?</h2>"),
    (
        '  <div id="moms-svar" class="faq-answer" hidden="until-found">',
        '  <div id="vat-answer" class="faq-answer" hidden="until-found">',
    ),
    (
        "    <p>Ja. Alla priser på sajten anges inklusive moms om inget annat sägs.</p>",
        "    <p>Yes. Every price on the site includes VAT unless stated otherwise.</p>",
    ),
    (
        '<figure class="attr-spark" role="img" aria-label="Försäljning: 34, 58, 41, 72, 66, 90 procent">',
        '<figure class="attr-spark" role="img" aria-label="Sales: 34, 58, 41, 72, 66, 90 percent">',
    ),
    ("  <span>Konvertering</span>", "  <span>Conversion</span>"),
    ("  <span>Släpp brief eller välj fil</span>", "  <span>Drop a brief or choose a file</span>"),
    ("  Mörkt läge", "  Dark mode"),
    ('  <a class="split-main" href="/offert">Begär offert</a>', '  <a class="split-main" href="/quote">Request quote</a>'),
    (
        '  <button class="split-more" commandfor="split-menu" command="toggle-popover" aria-label="Fler åtgärder">▾</button>',
        '  <button class="split-more" commandfor="split-menu" command="toggle-popover" aria-label="More actions">▾</button>',
    ),
    ('    <a href="/offert?plan=pro">Pro-offert</a>', '    <a href="/quote?plan=pro">Pro quote</a>'),
    ('    <a href="/kontakt">Prata med sälj</a>', '    <a href="/contact">Talk to sales</a>'),
    (
        '<div class="donut-chart" role="img" aria-label="Fördelning: 65% Kärnverksamhet, 20% Admin, 15% R&D" style="--p1: 65; --p2: 20;">',
        '<div class="donut-chart" role="img" aria-label="Split: 65% Core, 20% Admin, 15% R&D" style="--p1: 65; --p2: 20;">',
    ),
    ('    <label class="filter-chip"><input type="checkbox" id="f-tech" checked><span>Tech</span></label>',
     '    <label class="filter-chip"><input type="checkbox" id="f-tech" checked><span>Tech</span></label>'),
    ('    <article class="matrix-card" data-cat="tech">Tech-projekt</article>',
     '    <article class="matrix-card" data-cat="tech">Tech project</article>'),
    ('    <article class="matrix-card" data-cat="design">Design-projekt</article>',
     '    <article class="matrix-card" data-cat="design">Design project</article>'),
    ('  <button id="cart-icon" class="cart-btn" aria-label="Varukorg">🛒</button>',
     '  <button id="cart-icon" class="cart-btn" aria-label="Cart">🛒</button>'),
    (
        '  <label class="btn"><input type="checkbox" class="add-to-cart sr-only"> Köp Produkt A</label>',
        '  <label class="btn"><input type="checkbox" class="add-to-cart sr-only"> Buy Product A</label>',
    ),
    (
        '<figure class="gantt" role="region" aria-label="Projekt tidslinje">',
        '<figure class="gantt" role="region" aria-label="Project timeline">',
    ),
    (
        '  <div class="gantt-row" style="--start: 3; --span: 5;"><span>Utveckling</span></div>',
        '  <div class="gantt-row" style="--start: 3; --span: 5;"><span>Development</span></div>',
    ),
    (
        '<div class="heatmap-grid" role="img" aria-label="Aktivitetsmatris">',
        '<div class="heatmap-grid" role="img" aria-label="Activity matrix">',
    ),
    ('  <div class="cell" style="--val: 10" title="10 händelser"></div>', '  <div class="cell" style="--val: 10" title="10 events"></div>'),
    ('  <div class="cell" style="--val: 85" title="85 händelser"></div>', '  <div class="cell" style="--val: 85" title="85 events"></div>'),
    (
        '<figure class="stack-bar" role="img" aria-label="Fördelning: 40% Drift, 60% Sälj">',
        '<figure class="stack-bar" role="img" aria-label="Split: 40% Ops, 60% Sales">',
    ),
    (
        '<figure class="line-chart-wrap" role="img" aria-label="Försäljningstrend Q1-Q4">',
        '<figure class="line-chart-wrap" role="img" aria-label="Sales trend Q1–Q4">',
    ),
    ('  <a href="#s1" class="spy-l1">Intro</a>', '  <a href="#s1" class="spy-l1">Intro</a>'),
    ('  <a href="#s2" class="spy-l2">Funktioner</a>', '  <a href="#s2" class="spy-l2">Features</a>'),
    ("  <section id=\"s2\">Funktioner</section>", "  <section id=\"s2\">Features</section>"),
    ('<button commandfor="m-main" command="toggle-popover" class="btn">Exportera ▾</button>',
     '<button commandfor="m-main" command="toggle-popover" class="btn">Export ▾</button>'),
    (
        '  <button commandfor="m-sub" command="show-popover" id="b-sub" class="sub-trig">Som fil ▸</button>',
        '  <button commandfor="m-sub" command="show-popover" id="b-sub" class="sub-trig">As file ▸</button>',
    ),
    (
        '         pattern="(?=.*\\d)(?=.*[a-z])(?=.*[A-Z]).{8,}" required>',
        '         pattern="(?=.*\\d)(?=.*[a-z])(?=.*[A-Z]).{8,}" required>',
    ),
    (
        '  <input type="password" class="pwd-input" placeholder="Minst 8 tkn, siffra & versal"',
        '  <input type="password" class="pwd-input" placeholder="At least 8 chars, a number & a capital"',
    ),
    ('  <legend class="sr-only">Betygsätt</legend>', '  <legend class="sr-only">Rate this</legend>'),
    ('  <input type="range" min="0" max="100" value="20" aria-label="Lägsta pris">',
     '  <input type="range" min="0" max="100" value="20" aria-label="Lowest price">'),
    ('  <input type="range" min="0" max="100" value="80" aria-label="Högsta pris">',
     '  <input type="range" min="0" max="100" value="80" aria-label="Highest price">'),
    (
        '<button commandfor="auto-toast-1" command="show-popover" class="btn">Spara ändringar</button>',
        '<button commandfor="auto-toast-1" command="show-popover" class="btn">Save changes</button>',
    ),
    ("  ✅ Ändringar sparades i molnet", "  ✅ Changes saved to the cloud"),
    ("    <summary>Ingår fri support?</summary>", "    <summary>Is support included?</summary>"),
    ("    <div class=\"faq-content\">Ja, e-postsupport ingår i alla planer.</div>",
     '    <div class="faq-content">Yes, email support is included in every plan.</div>'),
    ("    <summary>Hur fungerar fakturering?</summary>", "    <summary>How does billing work?</summary>"),
    ("    <div class=\"faq-content\">Fakturering sker månadsvis i förskott.</div>",
     '    <div class="faq-content">Billing is monthly in advance.</div>'),
    ("    <legend class=\"sr-only\">Debiteringstyp</legend>", '    <legend class="sr-only">Billing type</legend>'),
    ('    <label><input type="radio" name="billing" id="b-m" checked> Månad</label>',
     '    <label><input type="radio" name="billing" id="b-m" checked> Monthly</label>'),
    ('    <label><input type="radio" name="billing" id="b-y"> År (−20%)</label>',
     '    <label><input type="radio" name="billing" id="b-y"> Yearly (−20%)</label>'),
    ('    <p class="price-val price-monthly">199 kr / mån</p>', '    <p class="price-val price-monthly">$19 / mo</p>'),
    ('    <p class="price-val price-yearly">159 kr / mån</p>', '    <p class="price-val price-yearly">$15 / mo</p>'),
    ('    <div class="swipe-content">Dokument_v1.pdf</div>', '    <div class="swipe-content">Document_v1.pdf</div>'),
    ('    <button class="swipe-action">Radera</button>', '    <button class="swipe-action">Delete</button>'),
    ('  <div class="plx-layer plx-fg"><h1>Framtidens UI</h1></div>', '  <div class="plx-layer plx-fg"><h1>The future of UI</h1></div>'),
    ('<label for="city-search">Sök stad</label>', '<label for="city-search">Search city</label>'),
    ('<input type="search" id="city-search" list="cities" placeholder="T.ex. Stockholm">',
     '<input type="search" id="city-search" list="cities" placeholder="e.g. London">'),
    ('  <option value="Stockholm"></option>', '  <option value="London"></option>'),
    ('  <option value="Göteborg"></option>', '  <option value="Berlin"></option>'),
    ('  <option value="Malmö"></option>', '  <option value="Paris"></option>'),
    ('  <input type="search" placeholder="Sök..." aria-label="Sök">',
     '  <input type="search" placeholder="Search…" aria-label="Search">'),
    ('  <button type="submit" aria-label="Genomför sökning">🔍</button>',
     '  <button type="submit" aria-label="Submit search">🔍</button>'),
    (
        '<p class="prose-dropcap">Det var en gång en ny standard för webben...</p>',
        '<p class="prose-dropcap">Once upon a time there was a new standard for the web…</p>',
    ),
    ('<figure class="img-wipe"><img src="/photo.jpg" alt="Beskrivning"></figure>',
     '<figure class="img-wipe"><img src="/photo.jpg" alt="Description"></figure>'),
    ('<main class="main-reveal">Huvudinnehåll</main>', '<main class="main-reveal">Main content</main>'),
    ('<a href="#main-content" class="skip-link">Hoppa till innehåll</a>',
     '<a href="#main-content" class="skip-link">Skip to content</a>'),
    (
        '  <button id="pin-1" commandfor="pop-pin-1" command="toggle-popover" class="map-pin" style="top: 30%; left: 40%;">📍</button>',
        '  <button id="pin-1" commandfor="pop-pin-1" command="toggle-popover" class="map-pin" style="top: 30%; left: 40%;">📍</button>',
    ),
    ('  <div id="pop-pin-1" popover="auto" class="pin-pop">Stockholm HK</div>',
     '  <div id="pop-pin-1" popover="auto" class="pin-pop">London HQ</div>'),
    ("  <h3>Valda tjänster (<span class=\"count-output\"></span>)</h3>",
     '  <h3>Selected services (<span class="count-output"></span>)</h3>'),
    ('  <label><input type="checkbox" class="count-item"> Webbdesign</label>',
     '  <label><input type="checkbox" class="count-item"> Web design</label>'),
    ("  <h2>Modalinnehåll</h2>", "  <h2>Modal content</h2>"),
    ('  <div class="guard-body">Långt skrollbart innehåll...</div>',
     '  <div class="guard-body">Long scrollable content…</div>'),
    ("max-height: 9lh; /* Max 9 rader text */", "max-height: 9lh; /* Max 9 lines of text */"),
    ("Page chrome: `MainLayout.astro`, `Header.astro`, `Shell.astro`.", "Page chrome: `MainLayout.astro`, `Header.astro`, `Shell.astro`."),
]

# Sort replacements longest-first so longer phrases win.
REPLACEMENTS.sort(key=lambda pair: len(pair[0]), reverse=True)

CATEGORY_UI = {
    "Interaction": "Interaction",
    "Reveal": "Reveal & motion",
    "Scroll-driven": "Scroll",
    "Scroll-state": "Scroll",
    "Layout": "Layout",
    "Anchor": "Anchor",
    "Anchor (legacy)": "Anchor",
    "Typography": "Typography",
    "Forms": "Forms",
    "Visual": "Visual",
    "State": "State",
    "Performance": "Performance",
    "Data": "Data",
    "Navigation": "Navigation",
    "Cards": "Cards",
    "Overlays": "Overlays",
    "Media": "Media",
}

FEATURE_BROWSERS = {
    "baseline": {
        "feature": "Widely available CSS",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Works in current Chrome, Edge, Firefox, and Safari.",
    },
    "has": {
        "feature": ":has()",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": ":has() has been Baseline since late 2023.",
    },
    "light-dark": {
        "feature": "light-dark()",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "light-dark() is Baseline 2024.",
    },
    "starting-style": {
        "feature": "@starting-style / popover",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "@starting-style and the Popover API are Baseline 2024–25.",
    },
    "scroll-timeline": {
        "feature": "animation-timeline: scroll()",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Scroll-driven animations: Chrome 115+, Firefox 136+, Safari 26+.",
    },
    "view-timeline": {
        "feature": "animation-timeline: view()",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "view() timelines: Chrome 115+, Firefox 136+, Safari 26+.",
    },
    "anchor": {
        "feature": "CSS Anchor Positioning",
        "chrome": "yes", "edge": "yes", "firefox": "partial", "safari": "yes",
        "note": "Chrome 125+, Safari 26+. Firefox support is still partial.",
    },
    "view-transitions": {
        "feature": "View Transitions",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Chrome 111+, Safari 18+. Firefox has not shipped this yet.",
    },
    "interpolate-size": {
        "feature": "interpolate-size",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chrome/Edge 129+. Firefox and Safari still snap instead of interpolating.",
    },
    "field-sizing": {
        "feature": "field-sizing",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Chrome 123+, Safari 17.4+. Firefox has not shipped field-sizing.",
    },
    "text-box-trim": {
        "feature": "text-box-trim",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Chrome 133+, Safari 18.2+, Firefox 154+.",
    },
    "scroll-state": {
        "feature": "scroll-state container queries",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chrome/Edge 133+. Not in Firefox or Safari as of 2026.",
    },
    "invoker-commands": {
        "feature": "Invoker Commands (commandfor)",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Chrome 135+, Safari 26.2+, Firefox 153+.",
    },
    "interest-invokers": {
        "feature": "Interest Invokers (interestfor)",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only as of 2026. Pair with a CSS hover fallback.",
    },
    "closedby": {
        "feature": "dialog closedby",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Chrome 134+, Safari 18.4+. Firefox still needs a close button.",
    },
    "until-found": {
        "feature": 'hidden="until-found"',
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "no",
        "note": "Chrome 102+, Firefox 139+. Safari has not shipped until-found.",
    },
    "scroll-markers": {
        "feature": "::scroll-marker / ::scroll-button",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only carousel controls. Wrap them in @supports.",
    },
    "base-select": {
        "feature": "appearance: base-select",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Chrome 135+, Safari 18.4+. Firefox keeps the native picker.",
    },
    "select-pseudos": {
        "feature": "::checkmark / ::picker-icon",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Requires appearance: base-select. Chrome 135+, Safari 18.4+.",
    },
    "corner-shape": {
        "feature": "corner-shape",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chrome/Edge 139+. Falls back to regular border-radius.",
    },
    "grid-lanes": {
        "feature": "display: grid-lanes",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only masonry in 2026. Fallback is a regular grid.",
    },
    "sibling-index": {
        "feature": "sibling-index()",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only CSS Values 5 tree counting.",
    },
    "contrast-color": {
        "feature": "contrast-color()",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only. Provide an explicit color fallback.",
    },
    "if": {
        "feature": "CSS if()",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only conditional values. Other browsers ignore the declaration.",
    },
    "typed-attr": {
        "feature": "typed attr()",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only. Feature-detect with attr(x type(*)).",
    },
    "details-content": {
        "feature": "::details-content",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Chrome 131+, Safari 18.4+. Firefox still uses the older 0fr pattern.",
    },
    "reading-flow": {
        "feature": "reading-flow",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "no",
        "note": "Chromium-only. Tab order stays in DOM order elsewhere.",
    },
    "target-text": {
        "feature": "::target-text",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Chrome 133+, Safari 18.2+. Styles shared text fragments.",
    },
    "initial-letter": {
        "feature": "initial-letter",
        "chrome": "partial", "edge": "partial", "firefox": "no", "safari": "yes",
        "note": "Safari has full initial-letter. Chromium support is limited; a float fallback is included.",
    },
    "position-visibility": {
        "feature": "position-visibility",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "yes",
        "note": "Chrome 125+, Safari 26+. Overlay stays visible without support.",
    },
    "shape": {
        "feature": "clip-path: shape()",
        "chrome": "yes", "edge": "yes", "firefox": "no", "safari": "partial",
        "note": "shape() is newest in Chromium. Other browsers ignore the clip.",
    },
    "offset-path": {
        "feature": "offset-path",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Motion path is widely available in current browsers.",
    },
    "property": {
        "feature": "@property",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "@property is Baseline and needed for typed interpolation.",
    },
    "subgrid": {
        "feature": "CSS subgrid",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "subgrid is Baseline in current browsers.",
    },
    "container": {
        "feature": "@container size queries",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Size container queries are Baseline since 2023.",
    },
    "content-visibility": {
        "feature": "content-visibility",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "content-visibility: auto is widely available.",
    },
    "scrollbar-color": {
        "feature": "scrollbar-color",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "Standard scrollbar-color / scrollbar-width are Baseline 2024+.",
    },
    "color-mix": {
        "feature": "color-mix() / oklch()",
        "chrome": "yes", "edge": "yes", "firefox": "yes", "safari": "yes",
        "note": "color-mix() and oklch() are Baseline 2023.",
    },
}


def detect_feature(css: str, html: str, title: str, status: str) -> str:
    src = f"{css}\n{html}\n{title}"
    checks = [
        (r"interestfor|interest-delay|:interest-source", "interest-invokers"),
        (r"commandfor|command=", "invoker-commands"),
        (r"grid-lanes", "grid-lanes"),
        (r"sibling-index\(", "sibling-index"),
        (r"contrast-color\(", "contrast-color"),
        (r"\bif\(", "if"),
        (r"attr\([^)]*type\(", "typed-attr"),
        (r"closedby", "closedby"),
        (r"hidden=[\"']until-found", "until-found"),
        (r"::scroll-marker|::scroll-button", "scroll-markers"),
        (r"::checkmark|::picker-icon", "select-pseudos"),
        (r"appearance:\s*base-select", "base-select"),
        (r"corner-shape", "corner-shape"),
        (r"container-type:\s*scroll-state|@container scroll-state", "scroll-state"),
        (r"animation-timeline:\s*view\(", "view-timeline"),
        (r"animation-timeline:\s*scroll\(", "scroll-timeline"),
        (r"@view-transition|view-transition-name|view-transition-class", "view-transitions"),
        (r"anchor-name|position-anchor|position-area", "anchor"),
        (r"interpolate-size", "interpolate-size"),
        (r"field-sizing", "field-sizing"),
        (r"text-box-trim", "text-box-trim"),
        (r"::details-content", "details-content"),
        (r"reading-flow", "reading-flow"),
        (r"::target-text", "target-text"),
        (r"initial-letter", "initial-letter"),
        (r"position-visibility", "position-visibility"),
        (r"clip-path:\s*shape\(", "shape"),
        (r"offset-path", "offset-path"),
        (r"@property", "property"),
        (r"subgrid", "subgrid"),
        (r"@container\b|container-type:\s*inline-size", "container"),
        (r"content-visibility", "content-visibility"),
        (r"scrollbar-color", "scrollbar-color"),
        (r"light-dark\(", "light-dark"),
        (r"@starting-style|:popover-open|popover=", "starting-style"),
        (r"color-mix\(|oklch\(", "color-mix"),
        (r":has\(", "has"),
    ]
    for pattern, key in checks:
        if re.search(pattern, src):
            return key
    return "baseline"


IMG = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 640 400'%3E"
    "%3Cdefs%3E%3ClinearGradient id='g' x1='0' x2='1' y1='0' y2='1'%3E"
    "%3Cstop stop-color='%236d5efc'/%3E%3Cstop offset='1' stop-color='%23c084fc'/%3E"
    "%3C/linearGradient%3E%3C/defs%3E"
    "%3Crect width='640' height='400' fill='url(%23g)'/%3E"
    "%3C/svg%3E"
)

IMG_B = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 640 400'%3E"
    "%3Cdefs%3E%3ClinearGradient id='g' x1='1' x2='0' y1='0' y2='1'%3E"
    "%3Cstop stop-color='%230f766e'/%3E%3Cstop offset='1' stop-color='%235eead4'/%3E"
    "%3C/linearGradient%3E%3C/defs%3E"
    "%3Crect width='640' height='400' fill='url(%23g)'/%3E"
    "%3C/svg%3E"
)


PREVIEW_HTML: dict[str, str] = {
    "1": f'<button class="btn-primary">Get started</button>',
    "2": '<button class="btn">Press me</button>',
    "3": f'<article class="destination-card"><img src="{IMG}" alt=""><h3>Lisbon</h3><p>Atlantic light.</p></article>',
    "5": '<nav><a class="nav-link" href="#">Overview</a> <a class="nav-link" href="#" aria-current="page">Pricing</a></nav>',
    "7": '<button class="icon" aria-label="Star">★</button>',
    "19": '<div class="input-group"><span aria-hidden="true">⌕</span><input type="search" placeholder="Search spells"></div>',
    "20": '<label style="display:flex;align-items:center;gap:.6rem"><input type="checkbox"> Remember me</label>',
    "22": '<details><summary>Details <span class="chevron">▾</span></summary><p>Native disclosure, no script.</p></details>',
    "24": '<a href="https://example.com" target="_blank" rel="noopener">Docs <span class="external-icon">↗</span></a>',
    "26": '<div class="segmented"><button type="button" aria-pressed="true">Day</button><button type="button">Week</button><button type="button">Month</button></div>',
    "38": '<button class="btn-primary">Mix a hover</button>',
    "39": '<label style="display:grid;gap:.4rem">Accent<input type="range" min="0" max="100" value="60"></label>',
    "8": '<h2 class="section-heading">A heading that reveals</h2>',
    "9": '<div class="hero-content"><p>Depth settles on load.</p></div>',
    "11": '<div class="skeleton" style="inline-size:16rem;block-size:4.5rem;border-radius:8px"></div>',
    "14": '<p class="demo-note">View Transitions run on real page navigations. This preview shows the CSS only.</p>',
    "31": '<button popovertarget="ph-pop" class="btn">Open menu</button><div id="ph-pop" popover class="popover-menu">Phantom entry</div>',
    "65": '<header class="site-header"><strong class="header-logo">Brand</strong></header><p style="height:8rem">Scroll the page to compress.</p>',
    "66": '<p class="demo-note">Backdrop fade applies to native dialogs and popovers.</p><button popovertarget="bd-pop">Open</button><div id="bd-pop" popover>Hello</div>',
    "72": '<ul class="stagger-list"><li>One</li><li>Two</li><li>Three</li></ul>',
    "17": '<header class="site-header">Frosted after scroll</header>',
    "30": '<p style="min-height:4rem">Content</p><div class="sticky-cta">Continue →</div>',
    "36": '<div class="scroll-progress"></div><p class="demo-note">A 3px bar tracks root scroll.</p>',
    "43": '<header class="site-header">Auto-hide header</header><p class="demo-note">Needs the root scroll-state preset.</p>',
    "44": '<nav class="toc"><div class="toc__inner">On this page</div></nav>',
    "45": '<div class="carousel"><div class="slide"><article>01</article></div><div class="slide"><article>02</article></div><div class="slide"><article>03</article></div></div>',
    "46": '<div class="tabs-wrap"><div class="fade-hint">→</div><p>Scrollable tabs live here.</p></div>',
    "47": '<a class="backtotop" href="#">↑</a><p class="demo-note">Wakes after the page has been scrolled.</p>',
    "55": '<div class="card-stack"><article class="card">Card A</article><article class="card">Card B</article><article class="card">Card C</article></div>',
    "69": '<div class="table-wrapper"><table><tr><th>Name</th><th>Plan</th><th>Seats</th></tr><tr><td>Acme</td><td>Pro</td><td>24</td></tr></table></div>',
    "12": f'<div class="gallery"><figure><img src="{IMG}" alt=""></figure><figure><img src="{IMG_B}" alt=""></figure><figure><img src="{IMG}" alt=""></figure></div>',
    "15": '<details><summary>Open panel</summary><div class="accordion-panel"><div class="accordion-inner">Animated with 0fr → 1fr.</div></div></details>',
    "27": '<div class="scroller-wrap"><div style="display:flex;gap:1rem;overflow:auto"><span>Alpha</span><span>Bravo</span><span>Charlie</span><span>Delta</span></div></div>',
    "33": '<details><summary>True auto height</summary><div class="accordion-panel">Animates to auto.</div></details>',
    "37": f'<div class="card-container"><article class="adaptive-card"><img class="card-media" src="{IMG}" alt=""><div><h3>Adaptive</h3><p>Layout follows the container.</p></div></article></div>',
    "40": '<div class="card-grid"><article class="card"><h3>One</h3><p>Short</p><button>Go</button></article><article class="card"><h3>Two</h3><p>A little more copy in this card.</p><button>Go</button></article></div>',
    "56": f'<div class="scroll-gallery" style="display:flex;gap:1rem"><img src="{IMG}" alt="" width="180"><img src="{IMG_B}" alt="" width="180"><img src="{IMG}" alt="" width="180"></div>',
    "61": '<div class="tabs-container"><details name="ui-tabs" open><summary>Overview</summary><p>First panel.</p></details><details name="ui-tabs"><summary>Details</summary><p>Second panel.</p></details></div>',
    "62": '<div class="carousel"><div class="slide">One</div><div class="slide">Two</div><div class="slide">Three</div></div>',
    "77": '<p class="demo-note">Opens as a sheet on small screens, a dialog on large ones.</p><button commandfor="sheet-demo" command="show-modal" class="btn">Open sheet</button><dialog id="sheet-demo" class="responsive-sheet" closedby="any"><p>Sheet content</p><form method="dialog"><button class="btn">Close</button></form></dialog>',
    "18": '<button data-tooltip="Copied to clipboard">Hover me</button>',
    "34": '<button class="tooltip-trigger">Trigger</button><div class="native-tooltip">Pinned tooltip</div>',
    "48": '<div class="field"><input type="email" required placeholder="you@site.com"><div class="error-bubble">Enter a valid email.</div></div>',
    "49": '<div class="filterbar"><button class="filter-trigger">Filters</button><div class="filter-panel">Sort · Date · Owner</div></div>',
    "50": '<div class="form-row"><label>API key<input></label><p class="help-rail">Keep this secret.</p></div>',
    "10": "<p>Select this sentence to see the skin.</p>",
    "bonus": "<h2 class='text-balance'>Typographic harmony on a long heading</h2><p class='text-pretty'>Pretty wrapping keeps orphans off the last line of a paragraph.</p>",
    "53": '<button class="btn">Trimmed</button> <span class="chip">Chip</span>',
    "63": "<article><p>Hyphenation keeps narrow columns from opening rivers of white space.</p></article>",
    "6": '<input type="text" placeholder="Focus me">',
    "16": '<div class="form-group"><input placeholder=" "><label>Your name</label></div>',
    "23": '<input type="email" required placeholder="you@site.com">',
    "28": '<ol class="steps"><li>Account</li><li>Address</li><li>Pay</li></ol>',
    "32": '<textarea class="auto-grow" placeholder="Type to grow…"></textarea>',
    "54": '<select class="premium-dropdown"><option>Overview</option><option>Reports</option><option>Settings</option></select>',
    "57": '<form class="checkout-form"><div class="form-group"><input required placeholder="Email"></div><button type="submit">Pay</button></form>',
    "25": f'<article class="media-card"><img src="{IMG}" alt="" style="display:block;width:100%"><h3 style="position:absolute;bottom:1rem;left:1rem;z-index:1;color:white">Stay</h3></article>',
    "35": '<article class="premium-card" style="padding:1rem">light-dark() follows the OS.</article>',
    "51": '<article class="ribbon-card" style="padding:1.5rem;background:var(--color-surface)">Ribbon cut</article>',
    "52": '<div class="section-divider"></div>',
    "58": '<article class="premium-glow-card" style="padding:1.25rem">Breathing border</article>',
    "64": '<div class="floating-orb"></div>',
    "74": f'<div class="blend-container" style="position:relative"><img src="{IMG}" alt="" style="width:100%;display:block"><p class="contrast-text" style="position:absolute;inset:0;display:grid;place-items:center;font-size:1.6rem">Contrast</p></div>',
    "78": '<p class="text-fade-clamp">The faded mask replaces a hard line-clamp so the last visible line dissolves instead of being chopped mid-word. Extra copy keeps the fade honest.</p>',
    "13": '<div class="card-grid"><article class="destination-card">Alpha</article><article class="destination-card">Bravo</article><article class="destination-card">Charlie</article></div>',
    "21": '<section id="preview-target">Deep-linked highlight</section>',
    "29": '<div class="link-cluster"><a href="#">Docs</a> <a href="#">Blog</a> <a href="#">Careers</a></div>',
    "59": '<div class="data-grid"></div>',
    "41": '<section class="lazy-section">Offscreen layout is skipped.</section>',
    "107": '<p class="demo-note">The panel hides when its anchor leaves the viewport.</p><button class="filter-trigger" style="anchor-name:--filter-btn">Filters</button><div class="filter-panel">Hidden when the trigger is gone.</div>',
    "112": "<p>Shared links that use #:~:text= highlight with ::target-text.</p>",
    "113": '<div class="pack-grid"><article>A</article><article>B</article><article>C</article></div>',
    "114": '<div class="table-scroller" style="max-height:6rem;overflow:auto"><p>Themed scrollbars on embedded panels.</p><p>More</p><p>More</p><p>More</p></div>',
    "118": '<select class="premium-dropdown"><option>One</option><option selected>Two</option><option>Three</option></select>',
    "143": '<p class="demo-note">Print rules hide chrome and append URLs. Open a print preview to see them.</p>',
    "104": '<article class="saas-card">if() tokens follow the scheme.</article>',
}


def translate(text: str) -> str:
    out = text
    for src, dst in REPLACEMENTS:
        if src in out:
            out = out.replace(src, dst)
    return out


def parse_spells(md: str) -> list[dict]:
    # Slice from the Spells heading to Ready-made stacks.
    start = md.find("\n# Spells\n")
    end = md.find("\n# Ready-made stacks\n")
    if start < 0:
        raise SystemExit("Could not find # Spells")
    body = md[start:end if end > 0 else None]

    heading_re = re.compile(r"^### (.+)$", re.M)
    matches = list(heading_re.finditer(body))
    spells = []
    current_section = "Spells"
    section_re = re.compile(r"^## (.+)$", re.M)
    sections = list(section_re.finditer(body))

    def section_at(pos: int) -> str:
        name = "Spells"
        for s in sections:
            if s.start() < pos:
                name = s.group(1).strip()
            else:
                break
        return name

    for i, m in enumerate(matches):
        chunk = body[m.end(): matches[i + 1].start() if i + 1 < len(matches) else len(body)]
        raw_title = m.group(1).strip()
        ident = "bonus"
        title = raw_title
        num_m = re.match(r"^(\d+)\.\s+(.*)$", raw_title)
        if num_m:
            ident = num_m.group(1)
            title = num_m.group(2)
        elif raw_title.lower().startswith("bonus"):
            ident = "bonus"
            title = re.sub(r"^Bonus\.\s*", "", raw_title)

        meta_m = re.search(r"^\*(.+)\*\s*$", chunk, re.M)
        meta = meta_m.group(1) if meta_m else ""
        parts = [p.strip() for p in meta.split("·")]
        category = parts[0] if parts else section_at(m.start())
        status = "Baseline"
        js_need = "0 JS"
        note = ""
        for p in parts[1:]:
            if p in {"Baseline", "Newer", "Progressive"}:
                status = p
            elif p in {"0 JS", "Markup"}:
                js_need = p
            else:
                note = p

        desc_parts = []
        consumed = chunk
        if meta_m:
            consumed = chunk[meta_m.end():]
        # Strip code fences from description
        desc_src = re.sub(r"```[\s\S]*?```", "", consumed)
        for line in desc_src.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("Markup:"):
                continue
            desc_parts.append(line)
        description = " ".join(desc_parts).strip()

        html = ""
        css = ""
        for fm in re.finditer(r"```(html|css)\n([\s\S]*?)```", chunk):
            lang, code = fm.group(1), fm.group(2).rstrip() + "\n"
            if lang == "html" and not html:
                html = code
            elif lang == "css" and not css:
                css = code

        # Inline markup note like: Markup: `<div class="scroll-progress"></div>`.
        if not html:
            inline = re.search(r"Markup:\s*`([^`]+)`", chunk)
            if inline:
                html = inline.group(1) + "\n"

        spells.append({
            "id": f"ds-{ident}" if ident != "bonus" else "ds-bonus",
            "number": ident,
            "title": title,
            "section": section_at(m.start()),
            "category": CATEGORY_UI.get(category, category),
            "rawCategory": category,
            "status": status.lower(),
            "statusLabel": status,
            "jsNeed": "none" if js_need == "0 JS" else "markup",
            "jsLabel": js_need,
            "note": note,
            "description": description,
            "html": html,
            "css": css,
        })
    return spells


def polish_preview(spell: dict) -> str:
    html = PREVIEW_HTML.get(spell["number"], spell["html"]).strip()
    if not html:
        # Last-resort: a labelled sample using the first class in the CSS.
        classes = re.findall(r"(?<![:\w])\.([a-zA-Z][\w-]*)", spell["css"])
        cls = classes[0] if classes else "demo"
        html = f'<div class="{cls}">Preview · {spell["title"]}</div>'
    # Swap remote images for local gradients so previews never depend on /photo.jpg.
    html = re.sub(
        r'src="/(?:after|photo-full|hero-1|hero-bg|a|photo)\.jpg"',
        f'src="{IMG}"',
        html,
    )
    html = re.sub(
        r'src="/(?:before|photo-thumb|b)\.jpg"',
        f'src="{IMG_B}"',
        html,
    )
    return html


def rewrite_preview_css(css: str) -> str:
    css = re.sub(r":root\b", ":host", css)
    css = re.sub(r"\bhtml\b", ":host", css)
    css = re.sub(r"\bbody\b", ":host", css)
    return css


def main() -> None:
    english = translate(SRC)
    leftover = sorted({
        w for w in re.findall(r"[A-Za-zÅÄÖåäöÉé]{3,}", english)
        if re.search(r"[åäöÅÄÖ]", w)
    })
    print("leftover swedish tokens:", leftover)

    (ROOT / "README.md").write_text(english, encoding="utf-8")
    (ROOT / "SKILL.md").write_text(english, encoding="utf-8")

    spells = parse_spells(english)
    print("parsed spells:", len(spells))

    payload = []
    for spell in spells:
        feature_key = detect_feature(spell["css"], spell["html"], spell["title"], spell["status"])
        support = FEATURE_BROWSERS[feature_key]
        item = {
            **spell,
            "previewHtml": polish_preview(spell),
            "previewCss": rewrite_preview_css(spell["css"]),
            "feature": support["feature"],
            "browsers": {
                "chrome": support["chrome"],
                "edge": support["edge"],
                "firefox": support["firefox"],
                "safari": support["safari"],
            },
            "supportNote": support["note"],
        }
        payload.append(item)

    cats = {}
    for s in payload:
        cats[s["category"]] = cats.get(s["category"], 0) + 1
    print("categories:", cats)

    js = (
        "/* generated by scripts/build.py — do not edit by hand */\n"
        "export const TOTAL_SPELLS = "
        + str(len(payload))
        + ";\n"
        "export const SPELLS = "
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + ";\n"
    )
    # The UI is classic scripts, not modules. Emit a global instead.
    classic = (
        "/* generated by scripts/build.py — do not edit by hand */\n"
        "window.DESIGN_SPELLS = "
        + json.dumps({"total": len(payload), "spells": payload}, ensure_ascii=False)
        + ";\n"
    )
    (ROOT / "public" / "spells.js").write_text(classic, encoding="utf-8")
    print("wrote public/spells.js", (ROOT / "public" / "spells.js").stat().st_size, "bytes")


if __name__ == "__main__":
    main()
