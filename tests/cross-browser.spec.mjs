import fs from "node:fs";
import { test, expect } from "@playwright/test";

const EXPECTED_TOTAL = JSON.parse(
  fs.readFileSync(new URL("../public/spells.json", import.meta.url), "utf8"),
).total;

test.use({ javaScriptEnabled: false, reducedMotion: "reduce" });

test("light catalogue keeps every spell link usable without JavaScript or horizontal overflow", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator(".row__link")).toHaveCount(EXPECTED_TOTAL);
  await expect(page.getByRole("link", { name: "Shimmer on primary buttons", exact: true })).toHaveAttribute("href", "/spells/ds-1/");
  for (const width of [320, 390, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    const geometry = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      content: document.documentElement.scrollWidth,
    }));
    expect(geometry.content, `horizontal overflow at ${width}px`).toBeLessThanOrEqual(geometry.viewport);
  }
  await page.locator('.row[data-id="ds-1"] .row__link').click();
  await expect(page).toHaveURL(/\/spells\/ds-1\/$/);
  await expect(page.getByRole("heading", { name: "Shimmer on primary buttons" })).toBeVisible();
});

test("docs expose labelled isolated demos, readable source and keyboard navigation", async ({ page }) => {
  await page.goto("/spells/ds-1/");
  await page.keyboard.press("Tab");
  await expect(page.locator(".skip-link")).toBeFocused();
  await expect(page.getByRole("heading", { name: "Live demo" })).toBeVisible();
  await expect(page.getByRole("link", { name: /Download runnable HTML/ })).toHaveAttribute("download", "ds-1.html");
  const iframe = page.getByTitle("Isolated demonstration: Shimmer on primary buttons");
  await expect(iframe).toHaveAttribute("sandbox", "allow-same-origin");
  await expect(iframe).toHaveAttribute("loading", "lazy");
  await expect(page.locator("pre code")).toHaveCount(2);
  await expect(page.getByRole("link", { name: /View integration source/ })).toHaveAttribute("href", "/bundle/ds-1.txt");
  await expect(page.locator("[data-copy-bundle]")).toBeHidden();
  await expect(page.locator('script[src="/spell-copy.js"]')).toHaveCount(1);
  await expect(page.locator("script:not([src])")).toHaveCount(0);
  await expect(page.locator("body")).toHaveCSS("overflow-x", "visible");
});

test("downloaded HTML carries its own base tokens and visible demo without scripting", async ({ page }) => {
  await page.goto("/download/ds-1.html");
  // CSS in <style> is not exposed by locator textContent consistently in Firefox/WebKit.
  // Read the actual stylesheet source instead of accessibility-derived text.
  const css = await page.locator("style").evaluate((el) => el.textContent);
  expect(css).toContain("--color-primary:");
  await expect(page.locator("script")).toHaveCount(0);
  const stage = page.locator(".stage");
  await expect(stage).toBeVisible();
  expect(await stage.evaluate((el) => el.getBoundingClientRect().width)).toBeGreaterThan(0);
});

test("integration source is served as selectable text without script dependencies", async ({ request }) => {
  const response = await request.get("/bundle/ds-120.txt");
  expect(response.status()).toBe(200);
  const source = await response.text();
  expect(source).toContain("Design Spells ds-120: integration source");
  expect(source).toContain("Authored markup from README.md");
  expect(source).not.toContain("<script");
});

test("baseline/effect comparison works without JS in both engines", async ({ page, request }) => {
  await page.goto("/spells/ds-2/");
  const frames = page.locator(".demo-compare iframe");
  await expect(frames).toHaveCount(2);
  await expect(frames.first()).toHaveAttribute("src", "/play/ds-2/before/");
  await expect(frames.last()).toHaveAttribute("src", "/play/ds-2/");
  const before = await (await request.get("/play/ds-2/before/")).text();
  const after = await (await request.get("/play/ds-2/")).text();
  expect(before).not.toContain("transform: scale(0.94)");
  expect(after).toContain("transform: scale(0.94)");
});

test("new gap-fill spells keep baseline/fallback behavior across engines", async ({ page }) => {
  await page.goto("/play/ds-153/");
  const disclosure = page.locator(".intrinsic-demo");
  const pill = page.locator(".intrinsic-pill");
  const before = await pill.evaluate(el => el.getBoundingClientRect().width);
  await pill.focus();
  await page.keyboard.press("Enter");
  await expect(disclosure).toHaveAttribute("open", "");
  // Width is transitioned; WebKit can report the pre-transition frame immediately
  // after the native <details> state changes. Check the settled rendered width.
  await expect.poll(() => pill.evaluate(el => el.getBoundingClientRect().width))
    .toBeGreaterThan(before + 10);

  await page.goto("/play/ds-152/");
  const cell = page.getByRole("button", { name: "42" });
  await cell.focus();
  await expect(cell).toBeFocused();
});

test("native cross-document navigation works with scripts disabled", async ({ page }) => {
  await page.goto("/play/ds-14/");
  await page.getByRole("link", { name: /Navigate to page B/ }).click();
  await expect(page).toHaveURL(/\/play\/ds-14\/next\/$/);
  await expect(page.getByRole("heading", { name: "Page B" })).toBeVisible();
  // WebKit may retain a cross-document transition snapshot over pointer input;
  // native keyboard activation must remain usable regardless.
  await page.getByRole("link", { name: /Return to page A/ }).focus();
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/\/play\/ds-14\/$/);
});
