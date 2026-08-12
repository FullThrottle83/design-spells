"use strict";

/* ============================================================
   design_spells — foundation build
   plain dom apis. no frameworks, no build step, no dependencies.
   target runtime: cloudflare workers static assets.
   ============================================================ */

const TOTAL_SPELLS = 144; // projected size of the finished catalogue

/**
 * @typedef {Object} Spell
 * @property {string} id        catalogue id, rendered monospaced
 * @property {string} title     human readable name
 * @property {string} category  grouping label (disclosure, state, scroll…)
 * @property {"stable"|"experimental"|"draft"} status
 * @property {string} jsNeed    js footprint — "none" for every spell in the bank
 * @property {string} html      markup snippet injected into the shadow preview
 * @property {string} css       source of the technique itself
 */

/** @type {Spell[]} */
const MOCK_SPELLS = [
  {
    id: "ds-001",
    title: "Exclusive accordion",
    category: "disclosure",
    status: "experimental",
    jsNeed: "none",
    html: `<div class="spell-acc">
  <details name="acc" open>
    <summary>What is a spell?</summary>
    <div class="spell-acc__body">
      <p>A single-file CSS technique that runs with zero JavaScript.</p>
    </div>
  </details>
  <details name="acc">
    <summary>Why share one <code>name</code>?</summary>
    <div class="spell-acc__body">
      <p>Native <code>&lt;details&gt;</code> elements with the same
      <code>name</code> form an exclusive group — opening one collapses the rest.</p>
    </div>
  </details>
  <details name="acc">
    <summary>Where is the js?</summary>
    <div class="spell-acc__body">
      <p>There is none. Disclosure behaviour ships with the platform.</p>
    </div>
  </details>
</div>`,
    css: `.spell-acc {
  width: min(32rem, 90%);
  border: 1px solid currentColor;
}

.spell-acc details + details {
  border-top: 1px solid currentColor;
}

.spell-acc summary {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
  padding: .65rem .9rem;
  cursor: pointer;
  list-style: none; /* hides the native marker */
  font: 600 .8rem/1.4 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}

.spell-acc summary::-webkit-details-marker { display: none; }

.spell-acc summary::after { content: "+"; font-weight: 400; }
.spell-acc details[open] > summary::after { content: "–"; }

.spell-acc summary:hover {
  background: CanvasText;
  color: Canvas;
}

.spell-acc__body {
  padding: 0 .9rem .85rem;
  font: .8rem/1.6 system-ui, sans-serif;
}`,
  },
  {
    id: "ds-002",
    title: "0-js theme switch",
    category: "state",
    status: "stable",
    jsNeed: "none",
    html: `<div class="spell-dark">
  <label class="spell-dark__toggle">
    <input type="checkbox">
    <span class="spell-dark__pill" aria-hidden="true"></span>
    invert this panel
  </label>
  <p class="spell-dark__note">The checkbox state is read by
  <code>:has()</code> on the panel root. No event listeners, no
  storage — pure cascade.</p>
</div>`,
    css: `.spell-dark {
  width: min(26rem, 88%);
  display: grid;
  gap: .8rem;
  padding: 1rem;
  border: 1px solid currentColor;
  background: Canvas;
  color: CanvasText;
}

.spell-dark__toggle {
  display: inline-flex;
  align-items: center;
  gap: .6rem;
  width: max-content;
  cursor: pointer;
  font: 600 .72rem/1.3 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  letter-spacing: .1em;
  text-transform: uppercase;
}

/* visually hidden, still focusable */
.spell-dark__toggle input {
  position: absolute;
  inline-size: 1px;
  block-size: 1px;
  opacity: 0;
}

.spell-dark__pill {
  inline-size: 2.2rem;
  block-size: 1.25rem;
  border: 1px solid currentColor;
  position: relative;
}

.spell-dark__pill::after {
  content: "";
  position: absolute;
  inset: .2rem auto .2rem .2rem;
  inline-size: .85rem;
  background: currentColor;
  transition: translate .15s ease-out;
}

.spell-dark__toggle input:checked + .spell-dark__pill::after {
  translate: .95rem 0;
}

.spell-dark__toggle input:focus-visible + .spell-dark__pill {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}

.spell-dark__note {
  margin: 0;
  max-inline-size: 42ch;
  font: .78rem/1.6 system-ui, sans-serif;
}

/* the spell: :has() flips the component — zero lines of js */
.spell-dark:has(:checked) {
  background: #0d0d12;
  color: #e6e6ec;
}`,
  },
  {
    id: "ds-003",
    title: "Scroll-snap shelf",
    category: "scroll",
    status: "stable",
    jsNeed: "none",
    html: `<div class="spell-shelf" tabindex="0" role="region"
     aria-label="Horizontally scrollable shelf">
  <article class="spell-shelf__slide"><span>01 / intro</span></article>
  <article class="spell-shelf__slide"><span>02 / rhythm</span></article>
  <article class="spell-shelf__slide"><span>03 / spacing</span></article>
  <article class="spell-shelf__slide"><span>04 / afterword</span></article>
</div>
<p class="spell-shelf__hint">scroll-x with snap — arrows, touch, wheel.
no slider library.</p>`,
    css: `.spell-shelf {
  width: min(30rem, 92%);
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 82%;
  gap: .5rem;
  overflow-x: auto;
  overscroll-behavior-inline: contain;
  scroll-snap-type: inline mandatory;
  scrollbar-width: thin;
  padding-block-end: .5rem;
}

.spell-shelf__slide {
  scroll-snap-align: center;
  aspect-ratio: 3 / 2;
  display: grid;
  place-items: center;
  border: 1px solid currentColor;
  font: 600 .7rem/1 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  letter-spacing: .14em;
  text-transform: uppercase;
}

.spell-shelf:focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}

.spell-shelf__hint {
  margin: .6rem 0 0;
  font: .75rem/1.5 system-ui, sans-serif;
  opacity: .7;
}`,
  },
];

/* ---------------- utilities ---------------- */

const $ = (sel, root = document) => root.querySelector(sel);

const esc = (str) =>
  String(str).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));

/* ---------------- dom refs ---------------- */

const grid         = $("#spell-grid");
const counter      = $("#counter");
const search       = $("#search");
const backdrop     = $("#backdrop");
const drawer       = $("#drawer");
const closeBtn     = $("#drawer-close");
const closeBtnFoot = $("#drawer-close-foot");
const previewHost  = $("#preview-host");

const drawerId    = $("#drawer-id");
const drawerJs    = $("#drawer-js");
const drawerTitle = $("#drawer-title");
const drawerCat   = $("#drawer-category");
const drawerChip  = $("#drawer-status");

const tabBar     = $("#code-tabs");
const tabBtns    = [...tabBar.querySelectorAll('[role="tab"]')];
const codePanel  = $("#code-view");
const codeText   = $("#code-text");
const sourceLang = $("#source-lang");
const copyStatus = $("#copy-status");

const STATUS_LINE_IDLE = "0-js · copy and paste freely";

/* ---------------- state ---------------- */

const state = { query: "", active: null, tab: "css" };
let lastTrigger = null;
let closing = false;
let statusTimer;

/* ---------------- grid rendering ---------------- */

function matches(spell) {
  if (!state.query) return true;
  const hay = `${spell.id} ${spell.title} ${spell.category} ${spell.status}`.toLowerCase();
  return state.query.toLowerCase().split(/\s+/).every((term) => hay.includes(term));
}

function cardTemplate(spell) {
  return `
  <li class="card" data-id="${esc(spell.id)}">
    <article class="card__inner">
      <p class="card__row">
        <span class="card__id">${esc(spell.id)}</span>
        <span class="chip chip--${esc(spell.status)}">${esc(spell.status)}</span>
      </p>
      <h2 class="card__title">
        <button class="card__hit" type="button" aria-haspopup="dialog">${esc(spell.title)}</button>
      </h2>
      <p class="card__row">
        <span class="card__cat">${esc(spell.category)}</span>
      </p>
    </article>
  </li>`;
}

function renderGrid() {
  const visible = MOCK_SPELLS.filter(matches);
  grid.innerHTML = visible.length
    ? visible.map(cardTemplate).join("")
    : `<li class="spell-grid__empty">no spells match “${esc(state.query)}” — 0 results</li>`;
  counter.textContent = `Showing ${visible.length} of ${TOTAL_SPELLS} spells`;
}

grid.addEventListener("click", (ev) => {
  const btn = ev.target.closest(".card__hit");
  if (!btn || !grid.contains(btn)) return;
  const spell = MOCK_SPELLS.find((s) => s.id === btn.closest(".card")?.dataset.id);
  if (spell) openDrawer(spell, btn);
});

/* ---------------- search ---------------- */

search.addEventListener("input", () => {
  state.query = search.value.trim();
  renderGrid();
});
$("#search-form").addEventListener("submit", (ev) => ev.preventDefault());

function isEditable(el) {
  return el instanceof HTMLElement && (el.closest("input, textarea, select") !== null || el.isContentEditable);
}

document.addEventListener("keydown", (ev) => {
  // `/` focuses search — unless already typing or the drawer owns focus
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

/* ---------------- preview engine (shadow dom) ---------------- */

function renderPreview(spell) {
  const root = previewHost.shadowRoot ?? previewHost.attachShadow({ mode: "open" });
  root.innerHTML = `
    <style>
      :host { display: block; }
      .stage {
        display: grid;
        place-items: center;
        min-height: 216px;
        padding: 20px;
        background: Canvas;
        color: CanvasText;
        color-scheme: light dark;
      }
      ${spell.css}
    </style>
    <div class="stage">${spell.html}</div>
  `;
}

/* ---------------- tabs ---------------- */

function setTab(name) {
  state.tab = name;
  for (const btn of tabBtns) {
    const on = btn.dataset.tab === name;
    btn.setAttribute("aria-selected", String(on));
    if (on) codePanel.setAttribute("aria-labelledby", btn.id);
  }
  sourceLang.textContent = name;
  codeText.textContent = !state.active ? "" : name === "css" ? state.active.css : state.active.html;
  codePanel.scrollTop = 0;
  codePanel.scrollLeft = 0;
}

tabBtns.forEach((btn) => btn.addEventListener("click", () => setTab(btn.dataset.tab)));

// roving-arrow tablist behaviour
tabBar.addEventListener("keydown", (ev) => {
  if (ev.key !== "ArrowLeft" && ev.key !== "ArrowRight") return;
  const idx = tabBtns.indexOf(document.activeElement);
  if (idx === -1) return;
  ev.preventDefault();
  const next = tabBtns[(idx + (ev.key === "ArrowRight" ? 1 : -1) + tabBtns.length) % tabBtns.length];
  next.focus();
  setTab(next.dataset.tab);
});

/* ---------------- export ---------------- */

function toAstro(spell) {
  const head = [
    `// ${spell.id} — ${spell.title}`,
    `// design-spells · category: ${spell.category} · status: ${spell.status} · js: ${spell.jsNeed}`,
  ].join("\n");
  return `---\n${head}\n---\n\n${spell.html.trim()}\n\n<style>\n${spell.css.trim()}\n</style>\n`;
}

async function copyText(text) {
  if (navigator.clipboard?.writeText) return navigator.clipboard.writeText(text);
  // fallback for insecure contexts (file://, plain http)
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

$("#copy-astro").addEventListener("click", async () => {
  if (!state.active) return;
  try {
    await copyText(toAstro(state.active));
    announce("copied .astro source — paste into any astro component");
  } catch {
    announce("copy failed — clipboard unavailable");
  }
});

$("#reset-preview").addEventListener("click", () => {
  if (!state.active) return;
  renderPreview(state.active);
  announce("preview re-instantiated from source");
});

/* ---------------- drawer lifecycle ---------------- */

function openDrawer(spell, trigger) {
  state.active = spell;
  lastTrigger = trigger instanceof HTMLElement ? trigger : document.activeElement;

  drawerId.textContent = spell.id;
  drawerJs.textContent = `js: ${spell.jsNeed}`;
  drawerTitle.textContent = spell.title;
  drawerCat.textContent = spell.category;
  drawerChip.textContent = spell.status;
  drawerChip.className = `chip chip--${spell.status}`;
  copyStatus.textContent = STATUS_LINE_IDLE;

  renderPreview(spell);
  setTab("css");

  backdrop.hidden = false;
  drawer.hidden = false;
  document.body.classList.add("is-locked");

  // two rAFs: unhide first, transition next frame
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
    window.setTimeout(finish, 380); // safety net if transitionend never fires
  }
}

closeBtn.addEventListener("click", closeDrawer);
closeBtnFoot.addEventListener("click", closeDrawer);
backdrop.addEventListener("click", closeDrawer);

// light focus trap — keep tab cycling inside the dialog
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

renderGrid();
