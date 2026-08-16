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

const BROWSER_META = [
  { key: "chrome", label: "Chrome", short: "C" },
  { key: "edge", label: "Edge", short: "E" },
  { key: "firefox", label: "Firefox", short: "F" },
  { key: "safari", label: "Safari", short: "S" },
];

const LEVEL_LABEL = { yes: "Supported", partial: "Partial", no: "Not shipped" };

const TAB_LABEL = {
  tailwind: "Tailwind v4",
  modern: "Modern CSS",
  html: "HTML",
};

/* Dark-zinc preview sandbox. The stage paints the canvas surface
   plus the subtle 16px dot grid; spell markup/CSS sits on top. */
const PREVIEW_TOKENS = `
  :host {
    display: block;
    color-scheme: dark;
    --color-primary: #e4e4e7;
    --color-bg: #18181b;
    --color-text: #f4f4f5;
    --color-text-muted: #a1a1aa;
    --color-text-inverse: #09090b;
    --color-border: #27272a;
    --color-surface: #121215;
    --color-surface-offset: #1f1f23;
    --color-surface-dynamic: #27272a;
    --color-surface-dark: #09090b;
    --color-error: #fca5a5;
    --color-success: #86efac;
    --color-accent: #d4d4d8;
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
  .btn, .btn-primary {
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

const catalogue   = $("#catalogue");
const catChips    = $("#cat-chips");
const counter     = $("#counter");
const search      = $("#search");
const backdrop    = $("#backdrop");
const drawer      = $("#drawer");
const closeBtn    = $("#drawer-close");
const closeBtnFoot= $("#drawer-close-foot");
const previewHost = $("#preview-host");

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

const state = { query: "", category: "all", status: "all", active: null, tab: "modern" };
let lastTrigger = null;
let closing = false;
let statusTimer;
const previewObserver = new IntersectionObserver(onPreviewIntersect, {
  rootMargin: "120px 0px",
  threshold: 0.05,
});

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

function browsersRow(spell) {
  return BROWSER_META.map((b) => {
    const level = spell.browsers?.[b.key] || "no";
    return `<span class="brow" data-level="${esc(level)}" title="${esc(b.label)}: ${esc(LEVEL_LABEL[level] || level)}">${esc(b.short)}</span>`;
  }).join("");
}

function oneLine(text) {
  const clean = String(text || "").replace(/`+/g, "").replace(/\*\*/g, "").replace(/\s+/g, " ").trim();
  const first = clean.split(/(?<=[.!?])\s+/)[0] || clean;
  return first.length > 140 ? first.slice(0, 137).trimEnd() + "…" : first;
}

function cardTemplate(spell) {
  return `
  <li class="card" data-id="${esc(spell.id)}">
    <header class="card__head">
      <h2 class="card__title">
        <button class="card__hit" type="button" aria-haspopup="dialog">${esc(spell.title)}</button>
      </h2>
      <p class="card__usecase">${esc(oneLine(spell.description))}</p>
    </header>

    <div class="card__preview" data-preview="${esc(spell.id)}" aria-hidden="true"></div>

    <div class="card__code">
      <div class="code" data-code data-id="${esc(spell.id)}" data-tab="modern">
        <div class="code__bar">
          <div class="code__tabs" role="tablist" aria-label="Source code views">
            <button class="code__tab" role="tab" data-tab="tailwind" aria-selected="false" type="button">Tailwind v4</button>
            <button class="code__tab" role="tab" data-tab="modern" aria-selected="true" type="button">Modern CSS</button>
            <button class="code__tab" role="tab" data-tab="html" aria-selected="false" type="button">HTML</button>
          </div>
        </div>
        <div class="code__view-wrap">
          <pre class="code__view" role="tabpanel" tabindex="0"><code></code></pre>
        </div>
        <button class="code__toggle" type="button" data-code-toggle>Show more</button>
      </div>
      <button class="card__copy" type="button" data-copy-code aria-label="Copy source for ${esc(spell.title)}">Copy CSS</button>
    </div>

    <div class="card__meta">
      <div class="card__cats">
        <span class="card__id">${esc(spell.id)}</span>
        <span class="card__cat-name">${esc(spell.category)}</span>
      </div>
      <div class="card__browsers" aria-label="Browser support">${browsersRow(spell)}</div>
    </div>
  </li>`;
}

function renderChips() {
  catChips.innerHTML = categories().map((c) => {
    const count = SPELLS.filter((s) => s.category === c).length;
    const on = state.category === c ? " is-on" : "";
    return `<button class="chip-btn${on}" type="button" data-cat="${esc(c)}">${esc(c)} <span aria-hidden="true">${count}</span></button>`;
  }).join("");
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
    catalogue.innerHTML = `<ul class="spell-grid"><li class="spell-grid__empty">No spells match “${esc(state.query)}”</li></ul>`;
  } else {
    catalogue.innerHTML = order.map((cat) => {
      const items = byCat.get(cat);
      return `
        <section class="cat-block" aria-labelledby="cat-${esc(cat)}">
          <div class="cat-block__head">
            <h2 class="cat-block__title" id="cat-${esc(cat)}">${esc(cat)}</h2>
            <span class="cat-block__count">${items.length} spell${items.length === 1 ? "" : "s"}</span>
          </div>
          <ul class="spell-grid" aria-label="${esc(cat)}">${items.map(cardTemplate).join("")}</ul>
        </section>`;
    }).join("");
  }

  counter.textContent = `Showing ${visible.length} of ${TOTAL_SPELLS} spells`;

  for (const host of catalogue.querySelectorAll("[data-preview]")) {
    previewObserver.observe(host);
  }
  for (const wrap of catalogue.querySelectorAll("[data-code]")) {
    renderCodeView(wrap);
  }
}

function onPreviewIntersect(entries) {
  for (const entry of entries) {
    if (!entry.isIntersecting) continue;
    const host = entry.target;
    previewObserver.unobserve(host);
    const spell = SPELLS.find((s) => s.id === host.dataset.preview);
    if (spell) hydratePreview(host, spell, true);
  }
}

function hydratePreview(host, spell, compact) {
  const root = host.shadowRoot ?? host.attachShadow({ mode: "open" });
  const css = spell.previewCss || spell.css || "";
  const html = spell.previewHtml || spell.html || "";
  const minHeight = compact ? 180 : 280;
  root.innerHTML = `
    <style>
      ${PREVIEW_TOKENS}
      ${css}
    </style>
    <div class="stage" style="min-height:${minHeight}px">${html}</div>
  `;
}

/* ---------------- code views ---------------- */

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

    // comments
    if (c === "/" && src[i + 1] === "*") {
      const end = src.indexOf("*/", i + 2);
      const stop = end < 0 ? n : end + 2;
      push("tok-com", src.slice(i, stop));
      i = stop;
      continue;
    }

    // strings
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

    // at-rules
    if (c === "@") {
      let j = i + 1;
      while (j < n && /[a-zA-Z-]/.test(src[j])) j++;
      push("tok-kw", src.slice(i, j));
      i = j;
      continue;
    }

    // braces / punctuation control declaration state
    if (c === "{") { braceDepth++; push("tok-punct", "{"); i++; continue; }
    if (c === "}") { braceDepth = Math.max(0, braceDepth - 1); push("tok-punct", "}"); i++; continue; }
    if (c === ";" || c === "(" || c === ")" || c === ",") {
      push("tok-punct", c); i++; continue;
    }
    if (c === ":") { push("tok-punct", ":"); i++; continue; }

    // numbers / hex colors / lengths
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

    // identifiers: properties inside declaration blocks, otherwise plain text
    if (/[A-Za-z_]/.test(c) || (c === "-" && /[A-Za-z-]/.test(src[i + 1] || ""))) {
      let j = i;
      if (c === "-") j++;
      while (j < n && /[\w-]/.test(src[j])) j++;
      const ident = src.slice(i, j);
      // Look ahead for a colon to decide if this is a property name.
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
  // Tokenize escaped HTML so we never accidentally highlight inside text.
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

const COPY_LABEL = { modern: "Copy CSS", html: "Copy HTML", tailwind: "Copy Tailwind" };

function renderCodeView(wrap) {
  const spell = SPELLS.find((s) => s.id === wrap.dataset.id);
  if (!spell) return;
  const tab = wrap.dataset.tab || "modern";
  const code = codeFor(spell, tab);
  const codeEl = wrap.querySelector("code");
  codeEl.innerHTML = highlight(code, tab);
  for (const btn of wrap.querySelectorAll(".code__tab")) {
    btn.setAttribute("aria-selected", String(btn.dataset.tab === tab));
  }
  const view = wrap.querySelector(".code__view");
  view.scrollTop = 0;
  requestAnimationFrame(() => updateCodeToggle(wrap));

  const copyBtn = wrap.parentElement?.querySelector(".card__copy");
  if (copyBtn && !copyBtn.classList.contains("is-done")) {
    copyBtn.textContent = COPY_LABEL[tab] || "Copy";
  }
}

function updateCodeToggle(wrap) {
  const view = wrap.querySelector(".code__view");
  const toggle = wrap.querySelector("[data-code-toggle]");
  const expanded = wrap.classList.contains("is-expanded");
  const overflow = view.scrollHeight > 190;
  toggle.classList.toggle("is-visible", overflow);
  toggle.textContent = expanded ? "Show less" : "Show more";
  view.classList.toggle("is-collapsed", overflow && !expanded);
  view.classList.toggle("is-expanded", expanded);
}

/* ---------------- filters ---------------- */

document.querySelector(".filters").addEventListener("click", (ev) => {
  const btn = ev.target.closest("[data-cat]");
  if (!btn) return;
  state.category = btn.dataset.cat;
  document.querySelectorAll("[data-cat]").forEach((el) => {
    el.classList.toggle("is-on", el.dataset.cat === state.category);
  });
  renderGrid();
});

document.querySelector(".filters--status").addEventListener("click", (ev) => {
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

/* ---------------- grid clicks ---------------- */

catalogue.addEventListener("click", async (ev) => {
  const tab = ev.target.closest(".code__tab");
  if (tab) {
    const wrap = tab.closest("[data-code]");
    wrap.dataset.tab = tab.dataset.tab;
    renderCodeView(wrap);
    return;
  }

  const toggle = ev.target.closest("[data-code-toggle]");
  if (toggle) {
    const wrap = toggle.closest("[data-code]");
    wrap.classList.toggle("is-expanded");
    updateCodeToggle(wrap);
    return;
  }

  const copyBtn = ev.target.closest("[data-copy-code]");
  if (copyBtn) {
    ev.preventDefault();
    const wrap = copyBtn.closest(".card__code")?.querySelector("[data-code]");
    const spell = wrap && SPELLS.find((s) => s.id === wrap.dataset.id);
    if (!spell) return;
    const tab = wrap.dataset.tab || "modern";
    try {
      await copyText(codeFor(spell, tab));
      flashCopy(copyBtn, "Copied!");
    } catch {
      flashCopy(copyBtn, "Failed");
    }
    return;
  }

  const hit = ev.target.closest(".card__hit");
  if (!hit) return;
  const spell = SPELLS.find((s) => s.id === hit.closest(".card")?.dataset.id);
  if (spell) openDrawer(spell, hit);
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
      <span class="bname">${esc(b.label)}</span>
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
  catalogue.innerHTML = `<ul class="spell-grid"><li class="spell-grid__empty">Spell data failed to load</li></ul>`;
} else {
  renderChips();
  renderGrid();
}
