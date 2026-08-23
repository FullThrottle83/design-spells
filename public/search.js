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
})();
