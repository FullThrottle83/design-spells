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

const LEVEL_LABEL = { yes: "Yes", partial: "Partial", no: "No" };

const PREVIEW_TOKENS = `
  :host {
    display: block;
    height: 100%;
    color-scheme: light dark;
    --color-primary: light-dark(#3b35c7, #a5a1ff);
    --color-bg: light-dark(#f7f7f9, #111116);
    --color-text: light-dark(#19191f, #eaeaee);
    --color-text-muted: light-dark(#53535e, #a0a0aa);
    --color-text-inverse: light-dark(#fbfbfc, #19191f);
    --color-border: light-dark(#d8d8de, #2a2a32);
    --color-surface: light-dark(#ffffff, #18181e);
    --color-surface-offset: light-dark(#ececf0, #22222a);
    --color-surface-dynamic: light-dark(#e4e4ea, #2c2c34);
    --color-surface-dark: #141419;
    --color-error: light-dark(#c0392b, #f07167);
    --color-success: light-dark(#0b7a45, #6fd39c);
    --color-accent: light-dark(#c45c26, #e8a87c);
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 16px;
    --space-1: .25rem;
    --space-2: .5rem;
    --space-3: .75rem;
    --space-4: 1rem;
    --space-5: 1.25rem;
    --space-6: 1.5rem;
    --space-8: 2rem;
    --header-height: 3rem;
    color: var(--color-text);
    font: 12.5px/1.45 ui-sans-serif, system-ui, sans-serif;
  }
  .stage {
    position: relative;
    transform: translateZ(0);
    isolation: isolate;
    overflow: hidden;
    min-height: 100%;
    height: 100%;
    padding: 16px;
    display: grid;
    place-items: center;
    background: var(--color-bg);
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
    color: white;
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

const tabBar     = $("#code-tabs");
const tabBtns    = [...tabBar.querySelectorAll('[role="tab"]')];
const codePanel  = $("#code-view");
const codeText   = $("#code-text");
const sourceLang = $("#source-lang");
const copyStatus = $("#copy-status");

const STATUS_LINE_IDLE = "Zero JS · copy and paste freely";

const state = { query: "", category: "all", status: "all", active: null, tab: "css" };
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

function slug(name) {
  return String(name).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "cat";
}

function cardTemplate(spell) {
  return `
  <li class="card" data-id="${esc(spell.id)}">
    <div class="card__preview" data-preview="${esc(spell.id)}" aria-hidden="true"></div>
    <article class="card__inner">
      <p class="card__row">
        <span class="card__id">${esc(spell.id)}</span>
        <span class="chip chip--${esc(spell.status)}">${esc(spell.statusLabel)}</span>
      </p>
      <h2 class="card__title">
        <button class="card__hit" type="button" aria-haspopup="dialog">${esc(spell.title)}</button>
      </h2>
      <p class="card__row">
        <span class="card__cat">${esc(spell.category)}</span>
      </p>
      <div class="card__foot">
        <div class="browsers" aria-label="Browser support">${browsersRow(spell)}</div>
        <button class="copy-btn" type="button" data-copy="${esc(spell.id)}">Copy CSS</button>
      </div>
    </article>
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
  const pad = compact ? "12px" : "20px";
  root.innerHTML = `
    <style>
      ${PREVIEW_TOKENS}
      .stage { padding: ${pad}; }
      ${css}
    </style>
    <div class="stage">${html}</div>
  `;
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
  const copyBtn = ev.target.closest("[data-copy]");
  if (copyBtn) {
    ev.preventDefault();
    ev.stopPropagation();
    const spell = SPELLS.find((s) => s.id === copyBtn.dataset.copy);
    if (!spell) return;
    try {
      await copyText(spell.css.trim());
      flashCopy(copyBtn, "Copied");
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
  }, 1400);
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

/* ---------------- tabs ---------------- */

function setTab(name) {
  state.tab = name;
  for (const btn of tabBtns) {
    const on = btn.dataset.tab === name;
    btn.setAttribute("aria-selected", String(on));
    if (on) codePanel.setAttribute("aria-labelledby", btn.id);
  }
  sourceLang.textContent = name;
  const spell = state.active;
  codeText.textContent = !spell ? "" : name === "css" ? spell.css : (spell.html || "<!-- This spell is CSS-only. Preview markup is generated. -->\n");
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

function toAstro(spell) {
  const head = [
    `// ${spell.id} — ${spell.title}`,
    `// design-spells · category: ${spell.category} · status: ${spell.statusLabel} · js: ${spell.jsLabel}`,
    `// ${spell.feature} · ${spell.supportNote}`,
  ].join("\n");
  const markup = (spell.html || spell.previewHtml || "").trim();
  return `---\n${head}\n---\n\n${markup}\n\n<style>\n${spell.css.trim()}\n</style>\n`;
}

async function copyText(text) {
  if (navigator.clipboard?.writeText) return navigator.clipboard.writeText(text);
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

$("#copy-source").addEventListener("click", async () => {
  if (!state.active) return;
  const text = state.tab === "css"
    ? state.active.css.trim()
    : (state.active.html || state.active.previewHtml || "").trim();
  try {
    await copyText(text);
    announce(state.tab === "css" ? "Copied CSS" : "Copied HTML");
  } catch {
    announce("Copy failed — clipboard unavailable");
  }
});

$("#copy-astro").addEventListener("click", async () => {
  if (!state.active) return;
  try {
    await copyText(toAstro(state.active));
    announce("Copied .astro source — paste into any Astro component");
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
  drawerJs.textContent = `JS: ${spell.jsLabel}`;
  drawerTitle.textContent = spell.title;
  drawerCat.textContent = spell.category;
  drawerChip.textContent = spell.statusLabel;
  drawerChip.className = `chip chip--${spell.status}`;
  drawerDesc.textContent = spell.description || "A zero-JS CSS technique.";
  drawerFeat.textContent = spell.feature;
  drawerNote.textContent = spell.supportNote;
  renderBrowserList(spell);
  copyStatus.textContent = STATUS_LINE_IDLE;

  hydratePreview(previewHost, spell, false);
  setTab("css");

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
