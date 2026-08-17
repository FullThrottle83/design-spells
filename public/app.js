"use strict";

/* ============================================================
   Design Spells — catalogue
   plain DOM APIs. no frameworks, no build step.
   ============================================================ */

const BANK = window.DESIGN_SPELLS;
const SPELLS = BANK?.spells ?? [];
const TOTAL_SPELLS = BANK?.total ?? SPELLS.length;

const CAT_ORDER = [
  "Interaction",
  "Navigation",
  "Cards",
  "Layout",
  "Scroll",
  "Reveal & motion",
  "Forms",
  "Overlays",
  "Typography",
  "Media",
  "Visual",
  "State",
  "Data",
  "Anchor",
  "Performance",
];

/* Small hand-drawn glyphs that read as "the four browsers" at a glance —
   evocative color/shape conventions, not traced logo artwork. Support
   level is shown via the wrapping .brow's opacity/grayscale, not color,
   so the glyphs themselves can stay true-to-brand. */
const ICONS = {
  chrome: `<svg viewBox="0 0 16 16" aria-hidden="true">
    <circle cx="8" cy="8" r="6" fill="none" stroke="#ea4335" stroke-width="3" stroke-dasharray="12.57 25.13" stroke-dashoffset="0" transform="rotate(-90 8 8)"/>
    <circle cx="8" cy="8" r="6" fill="none" stroke="#fbbc05" stroke-width="3" stroke-dasharray="12.57 25.13" stroke-dashoffset="-12.57" transform="rotate(-90 8 8)"/>
    <circle cx="8" cy="8" r="6" fill="none" stroke="#34a853" stroke-width="3" stroke-dasharray="12.57 25.13" stroke-dashoffset="-25.13" transform="rotate(-90 8 8)"/>
    <circle cx="8" cy="8" r="2.5" fill="#4285f4" stroke="#fff" stroke-width=".6"/>
  </svg>`,
  edge: `<svg viewBox="0 0 16 16" aria-hidden="true">
    <circle cx="8" cy="8" r="7.2" fill="#0f6cbd"/>
    <path d="M8 2.4c3.6 0 6.2 2.5 6.4 5.7.1 2.1-1.2 3.5-2.9 3.4-1.5-.1-2.4-1.2-2.5-2.6-.1-1.9-1.6-3.1-3.5-2.9-2.2.2-3.7 2.1-3.5 4.4.3 3.6 3.7 5.9 7.6 5.3-4.9 1.8-10-1.5-10.4-6.5C-1 4.9 3 2.4 8 2.4Z" fill="#2ec4a4"/>
    <path d="M8.4 7.6c.9-.1 1.7.3 2.1 1-.1-.9-.8-1.6-1.7-1.7-1-.1-1.9.5-2.1 1.5 0 .5.1.9.4 1.3-.6-.2-1-.7-1-1.3.1-1.4 1.2-2.5 2.6-2.6-.5-.3-1.1-.4-1.7-.3 1-1 2.5-1.3 3.9-.8-.4-.5-1-.8-1.6-.9 1.4-.3 2.9.2 3.8 1.4-.2-.1-.5-.1-.7-.1.9.7 1.4 1.8 1.3 3-.3 3.1-3.2 5.3-6.3 4.9-1.1-.1-2.1-.6-2.9-1.4 1.6.6 3.4.3 4.6-.9-1 .1-2-.3-2.6-1.1-.5-.6-.6-1.4-.4-2.1.3.4.8.7 1.3.6Z" fill="#0b5394" opacity=".55"/>
  </svg>`,
  firefox: `<svg viewBox="0 0 16 16" aria-hidden="true">
    <path d="M13.6 4.9c-.4-1-1-1.8-1.6-2.4.2.6.3 1.2.2 1.7-.6-1.3-1.6-2-2.7-2.3.5.5.8 1 1 1.5-1-.6-2.1-.8-3.2-.5-2 .5-3.5 2.3-3.6 4.4-.9-.1-1.7.2-2.3.9-.3.4-.4.9-.3 1.4-.4.3-.7.7-.8 1.2-.5 1.9.5 3.9 2.3 4.9C4 16.6 6.1 17 8 16.5c3.1-.8 5.3-3.7 5.3-7 0-1.6-.3-3.2-.9-4.6Z" fill="#f2600c"/>
    <path d="M6.4 3.9c-.6 1.1-.6 2.5.1 3.6-.5-.1-1-.4-1.3-.8-.2 1.1.2 2.3 1.1 3-1 0-1.9-.6-2.3-1.5-.3 1.5.6 3 2.1 3.5-1.2.2-2.4-.3-3.1-1.3-.1 1.7 1.1 3.2 2.8 3.5-1 .5-2.2.4-3.1-.3.9 2.7 3.9 4.1 6.5 3.2-2.6-.2-4.6-2.4-4.6-5 0-2.1 1.4-4 3.4-4.6-.4.7-.5 1.6-.2 2.4.3-.9 1-1.6 1.9-1.9-.4.6-.5 1.4-.3 2.1.4-.9 1.2-1.5 2.1-1.7-1-2.4-3.5-3.8-6-3.2.4-.3.9-.5 1.4-.6-1.4-.1-2.7.6-3.3 1.8Z" fill="#ffce54" opacity=".55"/>
  </svg>`,
  safari: `<svg viewBox="0 0 16 16" aria-hidden="true">
    <circle cx="8" cy="8" r="6.4" fill="#eaf4fc" stroke="#2f7bc7" stroke-width=".8"/>
    <path d="M8 8 4.6 11.4 6.6 6.6 11.4 4.6Z" fill="#ff4d4d"/>
    <path d="M8 8 6.6 6.6 11.4 4.6 9.4 9.4Z" fill="#c9ced3"/>
    <circle cx="8" cy="8" r="1" fill="#2f7bc7"/>
  </svg>`,
};

const BROWSER_META = [
  { key: "chrome", label: "Chrome" },
  { key: "edge", label: "Edge" },
  { key: "firefox", label: "Firefox" },
  { key: "safari", label: "Safari" },
];

const LEVEL_LABEL = { yes: "Supported", partial: "Partial", no: "Not shipped" };

const TAB_LABEL = {
  tailwind: "Tailwind v4",
  modern: "Modern CSS",
  html: "HTML",
};

/* Dark-zinc preview sandbox. The stage paints the canvas surface;
   spell markup/CSS sits on top. */
const PREVIEW_TOKENS = `
  :host, :host *, :host *::before, :host *::after {
    box-sizing: border-box;
  }
  :host {
    display: block;
    color-scheme: light;
    --color-primary: #18181b;
    --color-bg: #fbfaf8;
    --color-text: #18181b;
    --color-text-muted: #75716a;
    --color-text-inverse: #fbfaf8;
    --color-border: #e3ddd0;
    --color-surface: #ffffff;
    --color-surface-offset: #f2efe8;
    --color-surface-dynamic: #e3ddd0;
    --color-surface-dark: #18181b;
    --color-error: #b3261e;
    --color-success: #2f7d4f;
    --color-accent: #cf4520;
    --radius-sm: 6px;
    --radius-md: 8px;
    --radius-lg: 8px;
    --space-1: .25rem;
    --space-2: .5rem;
    --space-3: .75rem;
    --space-4: 1rem;
    --space-5: 1.25rem;
    --space-6: 1.5rem;
    --space-8: 2rem;
    --header-height: 3rem;
    color: var(--color-text);
    font: 13px/1.5 var(--ds-sans, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif);
  }
  .stage {
    position: relative;
    isolation: isolate;
    overflow: hidden;
    width: 100%;
    min-height: 180px;
    padding: 16px;
    display: grid;
    place-items: center;
    background-color: var(--color-bg);
    color: var(--color-text);
  }
  .stage > * { max-width: 100%; }
  img { max-width: 100%; height: auto; display: block; }
  button, .btn, a.btn {
    min-block-size: 36px;
    font: inherit;
    color: inherit;
  }
  :where(button), .btn, .btn-primary {
    padding: 0 .9rem;
    border: 1px solid var(--color-border);
    background: var(--color-surface);
    cursor: pointer;
    border-radius: var(--radius-md);
  }
  .btn-primary {
    background: var(--color-primary);
    color: var(--color-text-inverse);
    border-color: transparent;
  }
  :where(input:not([type="checkbox"]):not([type="radio"]):not([type="range"]):not([type="file"]):not([type="color"]):not([type="hidden"])),
  :where(select),
  :where(textarea) {
    font: inherit;
    color: inherit;
    padding: .45rem .65rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background: var(--color-surface);
  }
  :where(select) { padding-inline-end: 1.6rem; }
  :where(textarea) { resize: vertical; min-block-size: 5rem; }
  :where(input, select, textarea):focus-visible {
    outline: 2px solid var(--color-accent);
    outline-offset: 1px;
  }
  :where(input[type="checkbox"], input[type="radio"]) {
    inline-size: 16px;
    block-size: 16px;
  }
  :where(a) { color: var(--color-accent); text-underline-offset: 2px; }
  :where(table) { border-collapse: collapse; inline-size: 100%; }
  :where(th, td) { padding: .4rem .6rem; border-bottom: 1px solid var(--color-border); text-align: left; }
  :where(ul, ol) { padding-inline-start: 1.2rem; margin: 0; }
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
  .demo-note {
    margin: 0;
    max-inline-size: 36ch;
    text-align: center;
    color: var(--color-text-muted);
    font-size: 12px;
  }
`;

const $ = (sel, root = document) => root.querySelector(sel);

const esc = (str) =>
  String(str).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));

const catalogue    = $("#catalogue");
const catList      = $("#cat-list");
const statusList   = $("#status-list");
const browserLegend= $("#browser-legend");
const counter      = $("#counter");
const search       = $("#search");
const backdrop     = $("#backdrop");
const drawer       = $("#drawer");
const closeBtn     = $("#drawer-close");
const closeBtnFoot = $("#drawer-close-foot");
const previewHost  = $("#preview-host");

const previewPanel = $("#preview-panel");
const previewEmpty = $("#preview-empty");
const previewBody  = $("#preview-body");
const qpHost        = $("#quick-preview-host");
const qpId          = $("#qp-id");
const qpTitle       = $("#qp-title");
const qpCategory    = $("#qp-category");
const qpBrowsers    = $("#qp-browsers");
const qpCopy        = $("#qp-copy");
const qpDetails      = $("#qp-details");

const drawerId    = $("#drawer-id");
const drawerJs    = $("#drawer-js");
const drawerTitle = $("#drawer-title");
const drawerCat   = $("#drawer-category");
const drawerChip  = $("#drawer-status");
const drawerDesc  = $("#drawer-desc");
const drawerFeat  = $("#drawer-feature");
const drawerBrows = $("#drawer-browsers");
const drawerNote  = $("#drawer-support-note");

const tabBar      = $("#code-tabs");
const tabBtns     = [...tabBar.querySelectorAll('[role="tab"]')];
const codePanel   = $("#code-view");
const codeText    = $("#code-text");
const sourceLang  = $("#source-lang");
const copySource  = $("#copy-source");
const copyStatus  = $("#copy-status");

const STATUS_LINE_IDLE = "Zero JS · copy and paste freely";

const state = { query: "", category: "all", status: "all", active: null, tab: "modern", quick: null };
let lastTrigger = null;
let closing = false;
let statusTimer;

function categories() {
  const present = new Set(SPELLS.map((s) => s.category));
  const ordered = CAT_ORDER.filter((c) => present.has(c));
  for (const c of present) if (!ordered.includes(c)) ordered.push(c);
  return ordered;
}

function matches(spell) {
  if (state.category !== "all" && spell.category !== state.category) return false;
  if (state.status !== "all" && spell.status !== state.status) return false;
  if (!state.query) return true;
  const hay = [
    spell.id, spell.number, spell.title, spell.category, spell.status,
    spell.statusLabel, spell.jsLabel, spell.feature, spell.description,
  ].join(" ").toLowerCase();
  return state.query.toLowerCase().split(/\s+/).every((term) => hay.includes(term));
}

function browserIcon(key, level, label) {
  return `<span class="brow" data-level="${esc(level)}" title="${esc(label)}: ${esc(LEVEL_LABEL[level] || level)}">${ICONS[key] || ""}</span>`;
}

function browsersRow(spell) {
  return BROWSER_META.map((b) => {
    const level = spell.browsers?.[b.key] || "no";
    return browserIcon(b.key, level, b.label);
  }).join("");
}

function oneLine(text) {
  const clean = String(text || "").replace(/`+/g, "").replace(/\*\*/g, "").replace(/\s+/g, " ").trim();
  const first = clean.split(/(?<=[.!?])\s+/)[0] || clean;
  return first.length > 140 ? first.slice(0, 137).trimEnd() + "…" : first;
}

/* ---------------- rows ---------------- */

function rowTemplate(spell) {
  return `
  <li class="row" data-id="${esc(spell.id)}">
    <div class="row__main">
      <h2 class="row__title">
        <button class="row__hit" type="button" aria-haspopup="dialog">${esc(spell.title)}</button>
      </h2>
      <p class="row__desc">${esc(oneLine(spell.description))}</p>
    </div>
    <div class="row__aside">
      <span class="row__id">${esc(spell.id)}</span>
      <div class="row__browsers" aria-label="Browser support">${browsersRow(spell)}</div>
      <button class="row__copy" type="button" data-copy-row aria-label="Copy CSS for ${esc(spell.title)}">Copy</button>
    </div>
  </li>`;
}

function renderCategoryNav() {
  const rows = [`<button class="nav-item${state.category === "all" ? " is-on" : ""}" type="button" data-cat="all"><span>All</span><span class="nav-item__count" aria-hidden="true">${TOTAL_SPELLS}</span></button>`];
  for (const c of categories()) {
    const count = SPELLS.filter((s) => s.category === c).length;
    const on = state.category === c ? " is-on" : "";
    rows.push(`<button class="nav-item${on}" type="button" data-cat="${esc(c)}"><span>${esc(c)}</span><span class="nav-item__count" aria-hidden="true">${count}</span></button>`);
  }
  catList.innerHTML = rows.join("");
}

function renderBrowserLegendList() {
  browserLegend.innerHTML = BROWSER_META.map((b) =>
    `<li>${browserIcon(b.key, "yes", b.label)}<span>${esc(b.label)}</span></li>`
  ).join("");
}

function renderGrid() {
  const visible = SPELLS.filter(matches);
  const byCat = new Map();
  for (const spell of visible) {
    if (!byCat.has(spell.category)) byCat.set(spell.category, []);
    byCat.get(spell.category).push(spell);
  }

  const order = categories().filter((c) => byCat.has(c));
  if (!visible.length) {
    catalogue.innerHTML = `<p class="row-list__empty">No spells match “${esc(state.query)}”</p>`;
  } else {
    catalogue.innerHTML = order.map((cat) => {
      const items = byCat.get(cat);
      return `
        <section class="cat-block" aria-labelledby="cat-${esc(cat)}">
          <div class="cat-block__head">
            <h2 class="cat-block__title" id="cat-${esc(cat)}">${esc(cat)}</h2>
            <div class="cat-block__head-right">
              <span class="cat-block__count">${items.length} spell${items.length === 1 ? "" : "s"}</span>
              <button class="cat-block__copy-all" type="button" data-copy-cat="${esc(cat)}">Copy all</button>
            </div>
          </div>
          <ul class="row-list" aria-label="${esc(cat)}">${items.map(rowTemplate).join("")}</ul>
        </section>`;
    }).join("");
  }

  counter.textContent = `Showing ${visible.length} of ${TOTAL_SPELLS} spells`;

  if (!visible.some((s) => s.id === state.quick?.id)) {
    showQuickPreview(visible[0] || null);
  }
}

/* Most spells only change appearance on :hover/:focus/:active/etc — the
   resting state looks like plain markup, so without a hint every preview
   looks the same until you happen to interact with the right element. */
function detectTrigger(css, hasTimeline) {
  if (hasTimeline) return "Scroll to preview";
  if (/:target(?!-)/.test(css)) return "Click the link to preview";
  if (/::selection\b/.test(css)) return "Select the text";
  if (/:checked\b/.test(css)) return "Click to toggle";
  const hover = /:hover\b/.test(css);
  const focus = /:focus(-within|-visible)?\b/.test(css);
  const active = /:active\b/.test(css);
  if (hover && focus) return "Hover or focus to preview";
  if (hover) return "Hover to preview";
  if (focus) return "Focus to preview";
  if (active) return "Press to preview";
  return null;
}

/* :target only ever matches against the *document's* URL fragment, which
   can't reach into a shadow tree — so a spell's own `#anchor` link can
   never activate its `:target` rule inside this sandboxed preview. Shim it:
   mirror :target onto a plain attribute, then flip that attribute by hand
   whenever a same-shadow-root #link is clicked. */
function shimTargetCss(css) {
  return css.replace(/:target(?!-)/g, ":is(:target, [data-ds-target])");
}

/* Scroll/view-timeline animations resolve against the nearest *scrollable*
   ancestor — our stage has none, so the animation is stuck permanently at
   whatever progress its static layout happens to freeze it at (often fully
   hidden). Give it a real scroller with runway above/below the content so
   scrolling the preview itself drives the timeline, same as a real page. */
function hasScrollTimeline(css) {
  return /(animation-timeline|scroll-timeline|timeline-scope)\s*:/.test(css);
}

function hydratePreview(host, spell, compact) {
  const root = host.shadowRoot ?? host.attachShadow({ mode: "open" });
  const rawCss = spell.previewCss || spell.css || "";
  const css = shimTargetCss(rawCss);
  const html = spell.previewHtml || spell.html || "";
  const minHeight = compact ? 180 : 280;
  const timeline = hasScrollTimeline(rawCss);
  const hint = detectTrigger(rawCss, timeline);
  const stage = `
    <div class="stage" style="min-height:${minHeight}px">
      ${html}
      ${hint ? `<span class="ds-hint" aria-hidden="true">${esc(hint)}</span>` : ""}
    </div>`;
  const body = timeline
    ? `<div class="ds-runway" style="max-height:${minHeight}px">
        <div class="ds-runway__pad" aria-hidden="true"></div>
        ${stage}
        <div class="ds-runway__pad" aria-hidden="true"></div>
      </div>`
    : stage;
  root.innerHTML = `
    <style>
      ${PREVIEW_TOKENS}
      ${css}
      .ds-hint {
        position: absolute;
        right: 8px;
        bottom: 8px;
        z-index: 2;
        padding: 4px 8px;
        border-radius: 999px;
        background: var(--color-surface-dark);
        color: var(--color-text-inverse);
        font: 600 10px/1 var(--ds-sans, ui-sans-serif, system-ui, sans-serif);
        letter-spacing: .02em;
        pointer-events: none;
        opacity: .8;
      }
      .ds-runway {
        overflow-y: auto;
        overscroll-behavior: contain;
        scrollbar-width: thin;
      }
      .ds-runway__pad { block-size: 60vh; }
    </style>
    ${body}
  `;

  if (!root.__dsTargetShim) {
    root.__dsTargetShim = true;
    root.addEventListener("click", (ev) => {
      const link = ev.target.closest('a[href^="#"]');
      if (!link) return;
      ev.preventDefault();
      root.querySelectorAll("[data-ds-target]").forEach((el) => el.removeAttribute("data-ds-target"));
      const id = link.getAttribute("href").slice(1);
      const targetEl = id && root.getElementById(id);
      if (targetEl) targetEl.setAttribute("data-ds-target", "");
    });
  }
}

/* ---------------- code ---------------- */

function modernCssFor(spell) {
  return String(spell.css || "").trim() + "\n";
}

function htmlFor(spell) {
  return String(spell.previewHtml || spell.html || "").trim() ||
    "<!-- This spell is CSS-only; no extra markup is required. -->\n";
}

function tailwindFor(spell) {
  const css = modernCssFor(spell).trimEnd();
  const indented = css.split("\n").map((line) => (line ? "  " + line : line)).join("\n");
  return [
    "/* Tailwind v4 — drop into a global stylesheet processed by Tailwind. */",
    '@import "tailwindcss";',
    "",
    "@layer components {",
    indented,
    "}",
    "",
  ].join("\n");
}

function codeFor(spell, tab) {
  if (tab === "html") return htmlFor(spell);
  if (tab === "tailwind") return tailwindFor(spell);
  return modernCssFor(spell);
}

function highlightCss(src) {
  let out = "";
  let i = 0;
  let braceDepth = 0;
  const n = src.length;
  const push = (cls, text) => {
    const e = esc(text);
    out += cls ? `<span class="${cls}">${e}</span>` : e;
  };
  while (i < n) {
    const c = src[i];

    if (c === "/" && src[i + 1] === "*") {
      const end = src.indexOf("*/", i + 2);
      const stop = end < 0 ? n : end + 2;
      push("tok-com", src.slice(i, stop));
      i = stop;
      continue;
    }

    if (c === '"' || c === "'") {
      let j = i + 1;
      while (j < n && src[j] !== c) {
        if (src[j] === "\\") j++;
        j++;
      }
      j = Math.min(j + 1, n);
      push("tok-str", src.slice(i, j));
      i = j;
      continue;
    }

    if (c === "@") {
      let j = i + 1;
      while (j < n && /[a-zA-Z-]/.test(src[j])) j++;
      push("tok-kw", src.slice(i, j));
      i = j;
      continue;
    }

    if (c === "{") { braceDepth++; push("tok-punct", "{"); i++; continue; }
    if (c === "}") { braceDepth = Math.max(0, braceDepth - 1); push("tok-punct", "}"); i++; continue; }
    if (c === ";" || c === "(" || c === ")" || c === ",") {
      push("tok-punct", c); i++; continue;
    }
    if (c === ":") { push("tok-punct", ":"); i++; continue; }

    if (/[0-9#]/.test(c)) {
      let j = i;
      if (c === "#") {
        j++;
        while (j < n && /[0-9a-fA-F]/.test(src[j])) j++;
        if (j - i >= 4) { push("tok-num", src.slice(i, j)); i = j; continue; }
        j = i;
      }
      if (/[0-9]/.test(c)) {
        j = i + 1;
        while (j < n && /[0-9.]/.test(src[j])) j++;
        while (j < n && /[a-zA-Z%]/.test(src[j])) j++;
        push("tok-num", src.slice(i, j));
        i = j;
        continue;
      }
    }

    if (/[A-Za-z_]/.test(c) || (c === "-" && /[A-Za-z-]/.test(src[i + 1] || ""))) {
      let j = i;
      if (c === "-") j++;
      while (j < n && /[\w-]/.test(src[j])) j++;
      const ident = src.slice(i, j);
      let k = j;
      while (k < n && /\s/.test(src[k])) k++;
      const isProp = braceDepth > 0 && src[k] === ":";
      push(isProp ? "tok-prop" : null, ident);
      i = j;
      continue;
    }

    push(null, c);
    i++;
  }
  return out;
}

function highlightHtml(src) {
  const escHtml = esc(src);
  const tagRe = /&lt;(?:(!--[\s\S]*?--)|\/?)([a-zA-Z][\w-]*)((?:(?!&gt;).)*?)(\/?)&gt;/g;
  let out = "";
  let last = 0;
  let m;
  while ((m = tagRe.exec(escHtml)) !== null) {
    out += escHtml.slice(last, m.index);
    if (m[1]) {
      out += `&lt;<span class="tok-com">--${m[1].slice(0, -2)}</span>--&gt;`;
    } else {
      const name = m[2];
      const attrs = m[3] || "";
      const close = m[4] || "";
      const attrsHl = attrs.replace(
        /(\s+)([a-zA-Z_:][\w:.-]*)(?:(=)(&quot;.*?&quot;|&#39;.*?&#39;|[^\s]+))?/g,
        (_all, ws, an, eq, av) =>
          `${ws}<span class="tok-attr">${an}</span>` +
          (eq ? `=<span class="tok-str">${av}</span>` : "")
      );
      out += `&lt;${m[0].startsWith("&lt;/") ? "/" : ""}<span class="tok-tag">${name}</span>${attrsHl}${close}&gt;`;
    }
    last = m.index + m[0].length;
  }
  out += escHtml.slice(last);
  return out;
}

function highlight(src, tab) {
  if (tab === "html") return highlightHtml(src);
  return highlightCss(src);
}

/* ---------------- filters ---------------- */

catList.addEventListener("click", (ev) => {
  const btn = ev.target.closest("[data-cat]");
  if (!btn) return;
  state.category = btn.dataset.cat;
  renderCategoryNav();
  renderGrid();
});

statusList.addEventListener("click", (ev) => {
  const btn = ev.target.closest("[data-status]");
  if (!btn) return;
  state.status = btn.dataset.status;
  document.querySelectorAll("[data-status]").forEach((el) => {
    el.classList.toggle("is-on", el.dataset.status === state.status);
  });
  renderGrid();
});

search.addEventListener("input", () => {
  state.query = search.value.trim();
  renderGrid();
});
$("#search-form").addEventListener("submit", (ev) => ev.preventDefault());

/* ---------------- list interaction ---------------- */

function rowSpell(el) {
  const row = el?.closest?.(".row");
  return row && SPELLS.find((s) => s.id === row.dataset.id);
}

/* Preview updates on deliberate click only — hovering across the list
   used to swap the preview under the cursor as you moved past rows,
   which meant it rarely landed on the one you meant. */
catalogue.addEventListener("click", async (ev) => {
  const copyAllBtn = ev.target.closest("[data-copy-cat]");
  if (copyAllBtn) {
    ev.preventDefault();
    const cat = copyAllBtn.dataset.copyCat;
    const items = SPELLS.filter((s) => s.category === cat && matches(s));
    const combined = items.map((s) => `/* ${s.id} — ${s.title} */\n${modernCssFor(s)}`).join("\n");
    try {
      await copyText(combined);
      flashCopy(copyAllBtn, "Copied!");
    } catch {
      flashCopy(copyAllBtn, "Failed");
    }
    return;
  }

  const copyBtn = ev.target.closest("[data-copy-row]");
  if (copyBtn) {
    ev.preventDefault();
    const spell = rowSpell(copyBtn);
    if (!spell) return;
    try {
      await copyText(modernCssFor(spell));
      flashCopy(copyBtn, "Copied!");
    } catch {
      flashCopy(copyBtn, "Failed");
    }
    return;
  }

  const hit = ev.target.closest(".row__hit");
  if (hit) {
    const spell = rowSpell(hit);
    if (spell) {
      showQuickPreview(spell);
      openDrawer(spell, hit);
    }
    return;
  }

  const row = ev.target.closest(".row");
  if (row) {
    const spell = rowSpell(row);
    if (spell) showQuickPreview(spell);
  }
});

function flashCopy(btn, label) {
  const prev = btn.textContent;
  btn.textContent = label;
  btn.classList.add("is-done");
  window.setTimeout(() => {
    btn.textContent = prev;
    btn.classList.remove("is-done");
  }, 1500);
}

/* ---------------- search shortcut ---------------- */

function isEditable(el) {
  return el instanceof HTMLElement && (el.closest("input, textarea, select") !== null || el.isContentEditable);
}

document.addEventListener("keydown", (ev) => {
  if (ev.key === "/" && drawer.hidden && !isEditable(ev.target)) {
    ev.preventDefault();
    search.focus();
    return;
  }
  if (ev.key === "Escape" && !drawer.hidden) {
    ev.preventDefault();
    closeDrawer();
  }
});

/* ---------------- quick preview panel ---------------- */

function showQuickPreview(spell) {
  state.quick = spell || null;

  if (!spell) {
    previewBody.hidden = true;
    previewEmpty.hidden = false;
    if (qpHost.shadowRoot) qpHost.shadowRoot.innerHTML = "";
    return;
  }

  previewEmpty.hidden = true;
  previewBody.hidden = false;

  qpId.textContent = spell.id;
  qpTitle.textContent = spell.title;
  qpCategory.textContent = spell.category;
  qpBrowsers.innerHTML = browsersRow(spell);
  qpCopy.textContent = "Copy CSS";
  qpCopy.classList.remove("is-done");
  hydratePreview(qpHost, spell, true);
}

qpCopy.addEventListener("click", async () => {
  if (!state.quick) return;
  try {
    await copyText(modernCssFor(state.quick));
    flashCopy(qpCopy, "Copied!");
  } catch {
    flashCopy(qpCopy, "Failed");
  }
});

qpDetails.addEventListener("click", () => {
  if (state.quick) openDrawer(state.quick, qpDetails);
});

/* ---------------- drawer tabs ---------------- */

function setTab(name) {
  state.tab = name;
  for (const btn of tabBtns) {
    const on = btn.dataset.tab === name;
    btn.setAttribute("aria-selected", String(on));
    if (on) codePanel.setAttribute("aria-labelledby", btn.id);
  }
  sourceLang.textContent = TAB_LABEL[name] || name;
  const spell = state.active;
  if (!spell) {
    codeText.textContent = "";
  } else {
    const code = codeFor(spell, name);
    codeText.innerHTML = highlight(code, name);
  }
  codePanel.scrollTop = 0;
  codePanel.scrollLeft = 0;
}

tabBtns.forEach((btn) => btn.addEventListener("click", () => setTab(btn.dataset.tab)));

tabBar.addEventListener("keydown", (ev) => {
  if (ev.key !== "ArrowLeft" && ev.key !== "ArrowRight") return;
  const idx = tabBtns.indexOf(document.activeElement);
  if (idx === -1) return;
  ev.preventDefault();
  const next = tabBtns[(idx + (ev.key === "ArrowRight" ? 1 : -1) + tabBtns.length) % tabBtns.length];
  next.focus();
  setTab(next.dataset.tab);
});

/* ---------------- clipboard ---------------- */

async function copyText(text) {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      return;
    } catch {
      // Permission or focus issue — fall back to execCommand below.
    }
  }
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.setAttribute("readonly", "");
  ta.style.cssText = "position:fixed;opacity:0;";
  document.body.appendChild(ta);
  ta.select();
  try {
    document.execCommand("copy");
  } finally {
    ta.remove();
  }
}

function announce(message) {
  window.clearTimeout(statusTimer);
  copyStatus.textContent = message;
  statusTimer = window.setTimeout(() => {
    copyStatus.textContent = STATUS_LINE_IDLE;
  }, 2200);
}

copySource.addEventListener("click", async () => {
  if (!state.active) return;
  try {
    await copyText(codeFor(state.active, state.tab));
    announce(`Copied ${TAB_LABEL[state.tab]}`);
  } catch {
    announce("Copy failed — clipboard unavailable");
  }
});

$("#reset-preview").addEventListener("click", () => {
  if (!state.active) return;
  hydratePreview(previewHost, state.active, false);
  announce("Preview re-instantiated from source");
});

/* ---------------- drawer ---------------- */

function renderBrowserList(spell) {
  drawerBrows.innerHTML = BROWSER_META.map((b) => {
    const level = spell.browsers?.[b.key] || "no";
    return `<li>
      <span class="bname"><span class="brow" data-level="${esc(level)}">${ICONS[b.key] || ""}</span>${esc(b.label)}</span>
      <span class="blevel" data-level="${esc(level)}">${esc(LEVEL_LABEL[level] || level)}</span>
    </li>`;
  }).join("");
}

function openDrawer(spell, trigger) {
  state.active = spell;
  lastTrigger = trigger instanceof HTMLElement ? trigger : document.activeElement;

  drawerId.textContent = spell.id;
  drawerJs.textContent = spell.jsLabel;
  drawerTitle.textContent = spell.title;
  drawerCat.textContent = spell.category;
  drawerChip.className = `label label--${spell.status === "baseline" ? "ok" : spell.status === "newer" ? "warn" : "muted"}`;
  drawerChip.innerHTML = `<span class="label__dot" aria-hidden="true"></span>${esc(spell.statusLabel)}`;
  drawerDesc.textContent = spell.description || "A zero-JS CSS technique.";
  drawerFeat.textContent = spell.feature;
  drawerNote.textContent = spell.supportNote;
  renderBrowserList(spell);
  copyStatus.textContent = STATUS_LINE_IDLE;

  hydratePreview(previewHost, spell, false);
  setTab("modern");

  backdrop.hidden = false;
  drawer.hidden = false;
  document.body.classList.add("is-locked");

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      backdrop.classList.add("is-shown");
      drawer.classList.add("is-open");
    });
  });

  closeBtn.focus();
}

function closeDrawer() {
  if (drawer.hidden || closing) return;
  closing = true;

  drawer.classList.remove("is-open");
  backdrop.classList.remove("is-shown");
  document.body.classList.remove("is-locked");

  const finish = () => {
    if (!closing) return;
    closing = false;
    drawer.hidden = true;
    backdrop.hidden = true;
    if (previewHost.shadowRoot) previewHost.shadowRoot.innerHTML = "";
    state.active = null;
    if (lastTrigger?.isConnected) lastTrigger.focus();
  };

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    finish();
  } else {
    drawer.addEventListener("transitionend", function onEnd(ev) {
      if (ev.propertyName !== "transform") return;
      drawer.removeEventListener("transitionend", onEnd);
      finish();
    });
    window.setTimeout(finish, 380);
  }
}

closeBtn.addEventListener("click", closeDrawer);
closeBtnFoot.addEventListener("click", closeDrawer);
backdrop.addEventListener("click", closeDrawer);

drawer.addEventListener("keydown", (ev) => {
  if (ev.key !== "Tab") return;
  const items = [...drawer.querySelectorAll('button, a[href], [tabindex="0"]')]
    .filter((el) => !el.disabled && el.offsetParent !== null);
  if (!items.length) return;
  const first = items[0];
  const last = items[items.length - 1];
  if (ev.shiftKey && document.activeElement === first) {
    ev.preventDefault();
    last.focus();
  } else if (!ev.shiftKey && document.activeElement === last) {
    ev.preventDefault();
    first.focus();
  }
});

/* ---------------- init ---------------- */

if (!SPELLS.length) {
  catalogue.innerHTML = `<p class="row-list__empty">Spell data failed to load</p>`;
} else {
  renderBrowserLegendList();
  renderCategoryNav();
  renderGrid();
}
