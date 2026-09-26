import { test, expect } from "@playwright/test";

test.use({ javaScriptEnabled: false, reducedMotion: "reduce" });

test("view-timeline reveal has a full-height entry runway and native jump link", async ({ page }) => {
  await page.goto("/play/ds-8/");
  const target = page.locator("#entry-effect");
  await expect(page.getByRole("heading", { name: "Scroll to see this effect" })).toBeVisible();
  await expect(target).not.toBeInViewport();
  await page.getByRole("link", { name: "Jump to the effect" }).click();
  await expect(target).toBeInViewport();
  await expect(target.locator(".section-heading")).toBeVisible();
  await expect(page.locator("script")).toHaveCount(0);
});

test("SVG chart demo preserves the original drawing CSS below the fold", async ({ page }) => {
  await page.goto("/play/ds-125/");
  await expect(page.locator("#entry-effect")).not.toBeInViewport();
  await page.getByRole("link", { name: "Jump to the effect" }).click();
  await expect(page.locator("#entry-effect .line-path")).toBeInViewport();
  const source = await page.locator("style").textContent();
  expect(source).toContain("stroke-dashoffset: 1000");
  expect(source).toContain("animation-timeline: view()");
});

test("native theme controls switch the document scheme without scripting", async ({ page }) => {
  await page.goto("/play/ds-35/");
  await expect(page.locator("html")).toHaveCSS("color-scheme", "light");
  const card = page.locator(".premium-card");
  const light = await card.evaluate(el => getComputedStyle(el).backgroundColor);
  await page.getByRole("radio", { name: "Dark" }).check();
  await expect(page.locator("html")).toHaveCSS("color-scheme", "dark");
  const dark = await card.evaluate(el => getComputedStyle(el).backgroundColor);
  expect(dark).not.toBe(light);
  await expect(page.locator("script")).toHaveCount(0);
});

test("one-shot animation offers native replay and print media is explained", async ({ page }) => {
  await page.goto("/play/ds-9/");
  await expect(page.getByRole("link", { name: "Replay entrance animation" })).toHaveAttribute("href", "/play/ds-9/");
  await page.goto("/spells/ds-143/");
  await expect(page.getByText(/Ctrl\+P or Cmd\+P/)).toBeVisible();
  await expect(page.locator(".demo-compare")).toHaveCount(0);
});
