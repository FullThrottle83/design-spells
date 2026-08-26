// public/search.js — Design Spells v2026 progressive enhancement & state engine
(function () {
  "use strict";

  // Elements
  const searchInput = document.getElementById("search");
  const counter = document.getElementById("counter");
  const themeToggle = document.getElementById("theme-toggle");
  const stackBar = document.getElementById("stack-bar");
  const stackCountEl = document.getElementById("stack-count");
  const stackItemsEl = document.getElementById("stack-items");
  const stackCopyBtn = document.getElementById("stack-copy-css");
  const stackDownloadBtn = document.getElementById("stack-download-css");
  const stackShareBtn = document.getElementById("stack-share-url");
  const stackClearBtn = document.getElementById("stack-clear");
  const catRadios = document.querySelectorAll('input[name="cat"]');
  const statusRadios = document.querySelectorAll('input[name="status"]');

  if (!searchInput) return;

  const rows = Array.from(document.querySelectorAll(".row"));
  const catBlocks = Array.from(document.querySelectorAll(".cat-block"));
  const totalSpells = rows.length;

  // Stacks presets
  const STACK_PRESETS = {
    baseline: ["ds-1", "ds-2", "ds-3", "ds-5", "ds-12", "ds-15", "ds-19", "ds-20"],
    marketing: ["ds-8", "ds-9", "ds-11", "ds-14", "ds-25", "ds-31", "ds-68", "ds-135"],
    forms: ["ds-6", "ds-16", "ds-23", "ds-32", "ds-76", "ds-85", "ds-128", "ds-129"],
    data: ["ds-95", "ds-96", "ds-110", "ds-111", "ds-119", "ds-122", "ds-123", "ds-124"],
    micro: ["ds-1", "ds-5", "ds-7", "ds-20", "ds-22", "ds-24", "ds-26", "ds-38"]
  };

  // State
  let stackSet = new Set();
  let highlightedIndex = -1;
  let debounceTimer = null;

  // ------------------------------------------------------------- 1. Theme
  function initTheme() {
    const saved = localStorage.getItem("ds-theme") || "auto";
    applyTheme(saved);
  }

  function applyTheme(mode) {
    if (mode === "dark") {
      document.documentElement.dataset.theme = "dark";
      if (themeToggle) themeToggle.querySelector(".theme-btn__icon").textContent = "🌙";
      if (themeToggle) themeToggle.querySelector(".theme-btn__label").textContent = "Dark";
    } else if (mode === "light") {
      document.documentElement.dataset.theme = "light";
      if (themeToggle) themeToggle.querySelector(".theme-btn__icon").textContent = "☀️";
      if (themeToggle) themeToggle.querySelector(".theme-btn__label").textContent = "Light";
    } else {
      delete document.documentElement.dataset.theme;
      if (themeToggle) themeToggle.querySelector(".theme-btn__icon").textContent = "💻";
      if (themeToggle) themeToggle.querySelector(".theme-btn__label").textContent = "Auto";
    }
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const current = localStorage.getItem("ds-theme") || "auto";
      const next = current === "auto" ? "dark" : current === "dark" ? "light" : "auto";
      localStorage.setItem("ds-theme", next);
      applyTheme(next);
    });
  }

  // ------------------------------------------------------------- 2. Filtering
  function filter() {
    const q = searchInput.value.trim().toLowerCase();
    const terms = q ? q.split(/\s+/) : [];
    const activeCat = document.querySelector('input[name="cat"]:checked')?.value || "all";
    const activeStatus = document.querySelector('input[name="status"]:checked')?.value || "all";

    let visibleCount = 0;
    let categoryVisibleCounts = {};

    for (const row of rows) {
      const rowCat = row.dataset.cat;
      const rowStatus = row.dataset.status;

      // Category filter
      const catMatch = activeCat === "all" || rowCat === activeCat;
      // Status filter
      const statusMatch = activeStatus === "all" || rowStatus === activeStatus;
      // Query search
      let searchMatch = true;
      if (terms.length > 0) {
        const text = (row.dataset.tags || "") + " " + (row.textContent || "").toLowerCase();
        searchMatch = terms.every((t) => text.includes(t));
      }

      const isVisible = catMatch && statusMatch && searchMatch;
      row.hidden = !isVisible;

      if (isVisible) {
        visibleCount++;
        categoryVisibleCounts[rowCat] = (categoryVisibleCounts[rowCat] || 0) + 1;
      }
    }

    // Hide empty category blocks
    for (const block of catBlocks) {
      const blockCat = block.dataset.cat;
      const hasVisible = categoryVisibleCounts[blockCat] > 0;
      block.hidden = !hasVisible;
    }

    // Update counter
    if (counter) {
      if (activeCat !== "all" || activeStatus !== "all" || q) {
        let text = `Showing ${visibleCount} of ${totalSpells} spells`;
        if (activeCat !== "all") text += ` in ${activeCat}`;
        counter.textContent = text;
      } else {
        counter.textContent = `Showing ${totalSpells} of ${totalSpells} spells`;
      }
    }

    updateUrlState();
  }

  function debouncedFilter() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(filter, 80);
  }

  searchInput.addEventListener("input", debouncedFilter);

  catRadios.forEach((r) => r.addEventListener("change", filter));
  statusRadios.forEach((r) => r.addEventListener("change", filter));

  // ------------------------------------------------------------- 3. URL State & Deep Link
  function updateUrlState() {
    const params = new URLSearchParams();
    const q = searchInput.value.trim();
    const cat = document.querySelector('input[name="cat"]:checked')?.value;
    const status = document.querySelector('input[name="status"]:checked')?.value;

    if (q) params.set("q", q);
    if (cat && cat !== "all") params.set("category", cat);
    if (status && status !== "all") params.set("status", status);
    if (stackSet.size > 0) params.set("stack", Array.from(stackSet).join(","));

    const queryString = params.toString();
    const newUrl = queryString ? `${location.pathname}?${queryString}${location.hash}` : location.pathname + location.hash;
    history.replaceState(null, "", newUrl);
  }

  function syncFromUrl() {
    const params = new URLSearchParams(location.search);
    const q = params.get("q");
    const cat = params.get("category");
    const status = params.get("status");
    const stack = params.get("stack");

    if (q) searchInput.value = q;

    if (cat) {
      const radio = document.querySelector(`input[name="cat"][value="${CSS.escape(cat)}"]`);
      if (radio) radio.checked = true;
    }
    if (status) {
      const radio = document.querySelector(`input[name="status"][value="${CSS.escape(status)}"]`);
      if (radio) radio.checked = true;
    }

    if (stack) {
      stackSet = new Set(stack.split(",").map((s) => s.trim()).filter(Boolean));
      saveStack();
      renderStack();
    }

    filter();

    // Check hash for direct spell modal deep-linking
    const hash = location.hash.replace("#", "");
    if (hash && hash.startsWith("ds-")) {
      const drawer = document.getElementById(`drawer-${hash}`);
      if (drawer && typeof drawer.showPopover === "function") {
        setTimeout(() => drawer.showPopover(), 100);
      }
      const radio = document.getElementById(`select-${hash}`);
      if (radio) radio.checked = true;
    }
  }

  window.addEventListener("popstate", syncFromUrl);

  // ------------------------------------------------------------- 4. Live Browser Feature Check (CSS.supports)
  const FEATURE_SUPPORTS = {
    "custom-functions": "CSS.supports('@function --f() {}')",
    "css-scope": "CSS.supports('@scope')",
    "gap-decorations": "CSS.supports('column-rule: 1px solid red')",
    "css-random": "CSS.supports('width: random(1px, 10px)')",
    "interest-invokers": "'interestfor' in HTMLButtonElement.prototype",
    "invoker-commands": "'commandfor' in HTMLButtonElement.prototype",
    "grid-lanes": "CSS.supports('display: grid-lanes')",
    "sibling-index": "CSS.supports('top: sibling-index()')",
    "contrast-color": "CSS.supports('color: contrast-color(red)')",
    "if": "CSS.supports('color: if(style(--x: 1): red)')",
    "typed-attr": "CSS.supports('width: attr(data-w type(<length>))')",
    "closedby": "'closedBy' in HTMLDialogElement.prototype || 'closedby' in HTMLElement.prototype",
    "scroll-initial-target": "CSS.supports('scroll-initial-target: nearest')",
    "open-pseudo": "CSS.supports('selector(:open)')",
    "until-found": "'onbeforematch' in window",
    "scroll-markers": "CSS.supports('selector(::scroll-marker)')",
    "select-pseudos": "CSS.supports('selector(::checkmark)')",
    "base-select": "CSS.supports('appearance: base-select')",
    "corner-shape": "CSS.supports('corner-shape: round')",
    "scroll-state": "CSS.supports('container-type: scroll-state')",
    "view-timeline": "CSS.supports('animation-timeline: view()')",
    "scroll-timeline": "CSS.supports('animation-timeline: scroll()')",
    "view-transitions-cross": "CSS.supports('@view-transition { navigation: auto; }')",
    "view-transitions-same": "CSS.supports('view-transition-name: test')",
    "anchor": "CSS.supports('anchor-name: --a')",
    "interpolate-size": "CSS.supports('interpolate-size: allow-keywords')",
    "field-sizing": "CSS.supports('field-sizing: content')",
    "text-box-trim": "CSS.supports('text-box-trim: both')",
    "details-content": "CSS.supports('selector(::details-content)')",
    "reading-flow": "CSS.supports('reading-flow: grid-rows')",
    "target-text": "CSS.supports('selector(::target-text)')",
    "initial-letter": "CSS.supports('initial-letter: 2')",
    "position-visibility": "CSS.supports('position-visibility: anchors-visible')",
    "shape": "CSS.supports('clip-path: shape()')",
    "offset-path": "CSS.supports('offset-path: path(\"M0 0\")')",
    "property": "CSS.supports('@property --p { syntax: \"<number>\"; inherits: false; initial-value: 0; }')",
    "subgrid": "CSS.supports('grid-template-columns: subgrid')",
    "container": "CSS.supports('container-type: inline-size')",
    "content-visibility": "CSS.supports('content-visibility: auto')",
    "scrollbar-color": "CSS.supports('scrollbar-color: auto')",
    "light-dark": "CSS.supports('color: light-dark(#fff, #000)')",
    "starting-style": "CSS.supports('@starting-style {}')",
    "color-mix": "CSS.supports('color: color-mix(in srgb, red 50%, blue)')",
    "has": "CSS.supports('selector(:has(*))')"
  };

  function checkFeatureSupport(featureKeys) {
    if (!featureKeys || !featureKeys.length) return { status: "yes", text: "100% supported in your browser" };

    let supportedCount = 0;
    for (const key of featureKeys) {
      const expr = FEATURE_SUPPORTS[key];
      if (!expr) {
        supportedCount++;
        continue;
      }
      try {
        const res = eval(expr);
        if (res) supportedCount++;
      } catch (e) {
        // Feature check failed
      }
    }

    if (supportedCount === featureKeys.length) {
      return { status: "yes", text: "✓ Fully supported in your current browser" };
    } else if (supportedCount > 0) {
      return { status: "partial", text: "⚠️ Partial support in your current browser" };
    } else {
      return { status: "no", text: "❌ Modern feature — requires fallback or browser update" };
    }
  }

  function updateDrawerFeatureChecks(drawerEl) {
    const checkEl = drawerEl.querySelector(".feature-check");
    if (!checkEl) return;
    try {
      const keys = JSON.parse(checkEl.dataset.features || "[]");
      const res = checkFeatureSupport(keys);
      checkEl.innerHTML = `
        <span class="feature-check__badge is-${res.status === 'yes' ? 'supported' : res.status === 'partial' ? 'partial' : 'unsupported'}">
          ${res.status === 'yes' ? 'Supported' : res.status === 'partial' ? 'Partial' : 'No native support'}
        </span>
        <span class="feature-check__text">${res.text}</span>
      `;
    } catch (e) {
      // Ignore JSON parse error
    }
  }

  // Listen for popover toggle events
  document.addEventListener("toggle", (e) => {
    if (e.target.classList.contains("drawer")) {
      const mainShell = document.getElementById("main");
      const siteHead = document.querySelector(".site-head");

      if (e.newState === "open") {
        if (mainShell) mainShell.inert = true;
        if (siteHead) siteHead.inert = true;
        updateDrawerFeatureChecks(e.target);
        location.hash = e.target.id.replace("drawer-", "");
      } else {
        if (mainShell) mainShell.inert = false;
        if (siteHead) siteHead.inert = false;
        if (location.hash && location.hash.startsWith("#ds-")) {
          history.replaceState(null, "", location.pathname + location.search);
        }
      }
      updateUrlState();
    }
  });

  // ------------------------------------------------------------- 5. Stage Controls (Width & Theme)
  document.addEventListener("click", (e) => {
    // Width controls
    const stageWidthBtn = e.target.closest("[data-stage-width]");
    if (stageWidthBtn) {
      const width = stageWidthBtn.dataset.stageWidth;
      const host = stageWidthBtn.closest(".sect")?.querySelector(".preview-host");
      if (host) {
        const stage = host.querySelector(".stage") || host.querySelector("iframe");
        if (stage) stage.style.maxWidth = width;
      }
      stageWidthBtn.parentElement.querySelectorAll("[data-stage-width]").forEach((b) => b.classList.remove("is-active"));
      stageWidthBtn.classList.add("is-active");
      return;
    }

    // Stage theme toggle
    const stageThemeBtn = e.target.closest("[data-stage-theme-toggle]");
    if (stageThemeBtn) {
      const host = stageThemeBtn.closest(".sect")?.querySelector(".preview-host");
      if (host) {
        const currentTheme = host.dataset.stageTheme || "light";
        const nextTheme = currentTheme === "light" ? "dark" : "light";
        host.dataset.stageTheme = nextTheme;
        if (nextTheme === "dark") {
          host.style.background = "oklch(0.18 0.01 285.9)";
          host.style.color = "#fff";
        } else {
          host.style.background = "var(--color-bg, #fbfaf8)";
          host.style.color = "inherit";
        }
      }
      return;
    }

    // Preset buttons
    const presetBtn = e.target.closest("[data-preset]");
    if (presetBtn) {
      const key = presetBtn.dataset.preset;
      const list = STACK_PRESETS[key];
      if (list) {
        list.forEach((id) => stackSet.add(id));
        saveStack();
        renderStack();
        const stackDrawer = document.getElementById("stack-drawer");
        if (stackDrawer && typeof stackDrawer.showPopover === "function") {
          stackDrawer.showPopover();
        }
      }
      return;
    }
  });

  // ------------------------------------------------------------- 6. Stack Builder Engine
  function loadStack() {
    const saved = localStorage.getItem("ds-stack");
    if (saved) {
      try {
        stackSet = new Set(JSON.parse(saved));
      } catch (e) {}
    }
  }

  function saveStack() {
    localStorage.setItem("ds-stack", JSON.stringify(Array.from(stackSet)));
    updateUrlState();
  }

  function renderStack() {
    const count = stackSet.size;
    if (stackCountEl) stackCountEl.textContent = count;
    if (stackBar) stackBar.hidden = count === 0;

    // Update row & drawer buttons
    document.querySelectorAll("[data-stack-add]").forEach((btn) => {
      const sid = btn.dataset.stackAdd;
      if (stackSet.has(sid)) {
        btn.classList.add("is-stacked");
        btn.textContent = btn.classList.contains("btn-row-stack") ? "✓" : "✓ In Stack";
      } else {
        btn.classList.remove("is-stacked");
        btn.textContent = btn.classList.contains("btn-row-stack") ? "+" : "+ Add to Stack";
      }
    });

    // Render stack drawer items
    if (!stackItemsEl) return;

    if (count === 0) {
      stackItemsEl.innerHTML = `<p class="stack-empty">Your stack is currently empty. Click <strong>+ Add to Stack</strong> on any spell or preset above to build your bundle.</p>`;
      return;
    }

    let itemsHtml = "";
    stackSet.forEach((sid) => {
      const row = document.querySelector(`.row[data-id="${sid}"]`);
      const title = row ? row.querySelector(".row__hit")?.textContent || sid : sid;
      itemsHtml += `
        <div class="stack-item" data-id="${sid}">
          <span><strong class="stack-item__id">${sid}</strong> ${escapeHtml(title)}</span>
          <button type="button" class="stack-item__remove" data-stack-remove="${sid}" aria-label="Remove ${sid}">✕</button>
        </div>
      `;
    });
    stackItemsEl.innerHTML = itemsHtml;
  }

  function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  document.addEventListener("click", (e) => {
    // Add to stack
    const addBtn = e.target.closest("[data-stack-add]");
    if (addBtn) {
      const sid = addBtn.dataset.stackAdd;
      if (stackSet.has(sid)) {
        stackSet.delete(sid);
      } else {
        stackSet.add(sid);
      }
      saveStack();
      renderStack();
      return;
    }

    // Remove from stack
    const removeBtn = e.target.closest("[data-stack-remove]");
    if (removeBtn) {
      const sid = removeBtn.dataset.stackRemove;
      stackSet.delete(sid);
      saveStack();
      renderStack();
      return;
    }
  });

  if (stackClearBtn) {
    stackClearBtn.addEventListener("click", () => {
      stackSet.clear();
      saveStack();
      renderStack();
    });
  }

  if (stackCopyBtn) {
    stackCopyBtn.addEventListener("click", async () => {
      if (stackSet.size === 0) return;
      const combinedCss = generateCombinedCss();
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(combinedCss);
        const orig = stackCopyBtn.textContent;
        stackCopyBtn.textContent = "Copied Stack CSS!";
        setTimeout(() => (stackCopyBtn.textContent = orig), 1500);
      }
    });
  }

  if (stackDownloadBtn) {
    stackDownloadBtn.addEventListener("click", () => {
      if (stackSet.size === 0) return;
      const combinedCss = generateCombinedCss();
      const blob = new Blob([combinedCss], { type: "text/css" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "design-spells-stack.css";
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  if (stackShareBtn) {
    stackShareBtn.addEventListener("click", async () => {
      updateUrlState();
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(location.href);
        const orig = stackShareBtn.textContent;
        stackShareBtn.textContent = "Link Copied!";
        setTimeout(() => (stackShareBtn.textContent = orig), 1500);
      }
    });
  }

  function generateCombinedCss() {
    let cssBlocks = [];
    cssBlocks.push(`/* ============================================================`);
    cssBlocks.push(`   Design Spells — Combined Bundle (${stackSet.size} spells)`);
    cssBlocks.push(`   Generated: ${new Date().toISOString().slice(0, 10)}`);
    cssBlocks.push(`   Zero Client JS · Astro 7 & Modern CSS Ready`);
    cssBlocks.push(`   ============================================================ */\n`);

    stackSet.forEach((sid) => {
      const drawerCode = document.querySelector(`#drawer-${sid} .code__view code`);
      if (drawerCode) {
        cssBlocks.push(`/* --- ${sid} --- */`);
        cssBlocks.push(drawerCode.textContent.trim());
        cssBlocks.push("");
      }
    });

    return cssBlocks.join("\n");
  }

  // ------------------------------------------------------------- 7. Progressive Copy
  document.addEventListener("click", async (e) => {
    const copyBtn = e.target.closest("[data-copy-row], .code__copy");
    if (!copyBtn) return;

    let textToCopy = "";
    const spellId = copyBtn.dataset.spellId;
    if (spellId) {
      const drawerCode = document.querySelector(`#drawer-${spellId} .code__view code`);
      if (drawerCode) textToCopy = drawerCode.textContent;
    } else if (copyBtn.closest(".code")) {
      const openCode = copyBtn.closest(".code").querySelector(".code__tab-group[open] .code__view code")
        || copyBtn.closest(".code").querySelector(".code__view code");
      if (openCode) textToCopy = openCode.textContent;
    }

    if (textToCopy && navigator.clipboard) {
      try {
        await navigator.clipboard.writeText(textToCopy);
        const orig = copyBtn.textContent;
        copyBtn.textContent = "Copied!";
        copyBtn.classList.add("is-done");
        setTimeout(() => {
          copyBtn.textContent = orig;
          copyBtn.classList.remove("is-done");
        }, 1500);
      } catch (err) {
        console.error("Copy failed", err);
      }
    }
  });

  // ------------------------------------------------------------- 8. Keyboard Navigation
  document.addEventListener("keydown", (e) => {
    // '/' or 'Cmd+K' search focus
    if (
      (e.key === "/" || (e.key === "k" && (e.metaKey || e.ctrlKey))) &&
      document.activeElement !== searchInput &&
      !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)
    ) {
      e.preventDefault();
      searchInput.focus();
      return;
    }

    // Row navigation with 'j' and 'k' when search is not focused
    if (
      !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName) &&
      !document.querySelector(".drawer[popover]:not([hidden]):popover-open")
    ) {
      const visibleRows = rows.filter((r) => !r.hidden);
      if (!visibleRows.length) return;

      if (e.key === "j") {
        e.preventDefault();
        highlightedIndex = Math.min(highlightedIndex + 1, visibleRows.length - 1);
        focusRow(visibleRows[highlightedIndex]);
      } else if (e.key === "k") {
        e.preventDefault();
        highlightedIndex = Math.max(highlightedIndex - 1, 0);
        focusRow(visibleRows[highlightedIndex]);
      } else if (e.key === "Enter" && highlightedIndex >= 0 && visibleRows[highlightedIndex]) {
        const btn = visibleRows[highlightedIndex].querySelector(".row__hit");
        if (btn) btn.click();
      }
    }
  });

  function focusRow(rowEl) {
    if (!rowEl) return;
    const hitBtn = rowEl.querySelector(".row__hit");
    if (hitBtn) hitBtn.focus();
    rowEl.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  // ------------------------------------------------------------- Init
  initTheme();
  loadStack();
  syncFromUrl();
  renderStack();
})();
