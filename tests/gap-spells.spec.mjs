import { test, expect } from "@playwright/test";

test.use({ javaScriptEnabled: false, reducedMotion: "reduce" });

test("table crosshair exposes a distinct keyboard row/column intersection", async ({ page }) => {
  await page.goto("/play/ds-152/");
  const target = page.getByRole("button", { name: "42" });
  const sameRow = page.getByRole("button", { name: "61" });
  await target.focus();
  const targetBg = await target.locator("xpath=..").evaluate(el => getComputedStyle(el).backgroundColor);
  const rowBg = await sameRow.locator("xpath=..").evaluate(el => getComputedStyle(el).backgroundColor);
  expect(targetBg).not.toBe(rowBg);
  await expect(target).toBeFocused();
});

test("calc-size disclosure keeps a working fixed-width fallback and expands on activation", async ({ page }) => {
  await page.goto("/play/ds-153/");
  const pill = page.locator(".intrinsic-pill");
  const before = await pill.evaluate(el => el.getBoundingClientRect().width);
  await pill.click();
  await expect(page.locator("#intrinsic-more")).toBeChecked();
  const after = await pill.evaluate(el => el.getBoundingClientRect().width);
  expect(after).toBeGreaterThan(before + 80);
});

test("breakpointless switcher changes layout from row to stack without media queries", async ({ page }) => {
  await page.setViewportSize({ width: 900, height: 700 });
  await page.goto("/play/ds-154/");
  const cards = page.locator(".switcher > article");
  const wide = await cards.evaluateAll(nodes => nodes.map(el => Math.round(el.getBoundingClientRect().top)));
  expect(new Set(wide).size).toBe(1);

  await page.setViewportSize({ width: 420, height: 800 });
  const narrow = await cards.evaluateAll(nodes => nodes.map(el => Math.round(el.getBoundingClientRect().top)));
  expect(new Set(narrow).size).toBeGreaterThan(1);
});

test("round gauge resolves the 73 percent target to a 70 percent step", async ({ page }) => {
  await page.goto("/play/ds-155/");
  const ratio = await page.locator(".step-gauge").evaluate(el => {
    const track = el.querySelector(".step-gauge__track").getBoundingClientRect().width;
    const fill = el.querySelector(".step-gauge__fill").getBoundingClientRect().width;
    return fill / track;
  });
  expect(ratio).toBeGreaterThan(0.68);
  expect(ratio).toBeLessThan(0.72);
});
