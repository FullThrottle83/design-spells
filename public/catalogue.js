/* Optional catalogue convenience. Browsing, links and demos never depend on this file. */
(() => {
  const input = document.getElementById("search");
  const tools = document.querySelector(".catalogue-tools");
  const rows = [...document.querySelectorAll(".spell-list .row")];
  const sections = [...document.querySelectorAll(".cat-section")];
  const count = document.getElementById("result-count");
  const empty = document.getElementById("no-results");
  if (!input || !tools || !rows.length || !count || !empty) return;

  function filter() {
    const query = input.value.trim().toLowerCase();
    const terms = query.split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const row of rows) {
      const text = row.dataset.search || "";
      const match = terms.every(term => text.includes(term));
      row.hidden = !match;
      if (match) visible++;
    }
    for (const section of sections) {
      section.hidden = !section.querySelector(".row:not([hidden])");
    }
    count.textContent = `Showing ${visible} of ${rows.length} spells`;
    empty.hidden = visible > 0;
  }

  let timer;
  input.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      filter();
      const url = new URL(location.href);
      if (input.value.trim()) url.searchParams.set("q", input.value.trim());
      else url.searchParams.delete("q");
      history.replaceState(null, "", url);
    }, 80);
  });
  window.addEventListener("popstate", () => {
    input.value = new URLSearchParams(location.search).get("q") || "";
    filter();
  });
  document.querySelectorAll(".category-links a").forEach(link => link.addEventListener("click", () => {
    if (!input.value) return;
    input.value = "";
    filter();
    const url = new URL(location.href);
    url.searchParams.delete("q");
    history.replaceState(null, "", url);
  }));
  input.value = new URLSearchParams(location.search).get("q") || "";
  filter();
  tools.hidden = false;
})();
