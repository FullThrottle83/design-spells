/* Optional clipboard enhancement for static spell docs. The native link works without JS. */
(() => {
  "use strict";
  const button = document.querySelector("button[data-copy-bundle]");
  const link = document.querySelector("a[data-bundle-source]");
  const status = document.querySelector("[data-bundle-status]");
  if (!button || !link || !status || typeof navigator.clipboard?.writeText !== "function") return;
  const sid = button.dataset.copyBundle;
  if (!/^ds-(?:[1-9]\d*|bonus)$/.test(sid) || link.getAttribute("href") !== `/bundle/${sid}.txt`) return;
  button.hidden = false;
  button.addEventListener("click", async () => {
    button.disabled = true;
    status.textContent = "Copying integration source…";
    try {
      const response = await fetch(link.href, { credentials: "same-origin" });
      if (!response.ok) throw new Error("Bundle request failed");
      const source = await response.text();
      if (!source.startsWith(`<!doctype html>\n<!-- Design Spells ${sid}: integration source`)) {
        throw new Error("Unexpected bundle response");
      }
      await navigator.clipboard.writeText(source);
      status.textContent = `Integration source copied for ${sid}.`;
      button.textContent = "Copied bundle";
    } catch {
      status.textContent = "Copy failed. Use the integration source link instead.";
      button.textContent = "Copy integration bundle";
    } finally {
      button.disabled = false;
    }
  });
})();
