// public/search.js — progressive enhancement for live search
(function () {
  "use strict";

  const searchInput = document.getElementById("search");
  const counter = document.getElementById("counter");
  if (!searchInput) return;

  const rows = Array.from(document.querySelectorAll(".row"));
  const catBlocks = Array.from(document.querySelectorAll(".cat-block"));
  const total = rows.length;

  function filter() {
    const q = searchInput.value.trim().toLowerCase();
    const terms = q ? q.split(/\s+/) : [];
    let visible = 0;

    for (const row of rows) {
      if (!terms.length) {
        row.hidden = false;
        visible++;
      } else {
        const text = (row.dataset.tags || "") + " " + (row.textContent || "").toLowerCase();
        const match = terms.every((t) => text.includes(t));
        row.hidden = !match;
        if (match) visible++;
      }
    }

    for (const block of catBlocks) {
      const hasVisible = block.querySelector(".row:not([hidden])") !== null;
      block.hidden = !hasVisible;
    }

    if (counter) {
      counter.textContent = q
        ? `Showing ${visible} of ${total} spells`
        : `Showing ${total} of ${total} spells`;
    }
  }

  searchInput.addEventListener("input", filter);

  document.addEventListener("keydown", (e) => {
    if (
      e.key === "/" &&
      document.activeElement !== searchInput &&
      !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)
    ) {
      e.preventDefault();
      searchInput.focus();
    }
  });

  // Progressive enhancement: Clipboard copy
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
})();
