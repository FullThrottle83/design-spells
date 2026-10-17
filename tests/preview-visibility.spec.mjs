import { test, expect } from "@playwright/test";

test.use({ javaScriptEnabled: false, reducedMotion: "reduce" });

test("underline is perceptibly different from the identical baseline on hover", async ({ page }) => {
  await page.goto("/spells/ds-5/");
  const base = page.frameLocator('iframe[title^="Baseline without spell CSS"]')
    .locator(".nav-link").first();
  const effect = page.frameLocator('iframe[title^="Isolated demonstration"]')
    .locator(".nav-link").first();
  await expect(base).toBeVisible();
  await expect(effect).toBeVisible();
  const baseContent = await base.evaluate(el => getComputedStyle(el, "::after").content);
  expect(baseContent).toBe("none");
  await effect.hover();
  await expect.poll(async () => effect.evaluate(el =>
    parseFloat(getComputedStyle(el, "::after").width)
  )).toBeGreaterThan(10);
});

test("soft push is distinguishable from the unchanged baseline while pressed", async ({ page }) => {
  await page.goto("/spells/ds-2/");
  const base = page.frameLocator('iframe[title^="Baseline without spell CSS"]').getByRole("button", { name: "Press me" });
  const effect = page.frameLocator('iframe[title^="Isolated demonstration"]').getByRole("button", { name: "Press me" });
  await expect(base).toBeVisible();
  await expect(effect).toBeVisible();
  expect(await base.evaluate(el => getComputedStyle(el).transform)).toBe("none");
  await effect.hover();
  await page.mouse.down();
  try {
    await expect.poll(async () => effect.evaluate(el => getComputedStyle(el).transform))
      .not.toBe("none");
  } finally {
    await page.mouse.up();
  }
});

test("non-comparable document behavior retains one genuine demo", async ({ page }) => {
  await page.goto("/spells/ds-14/");
  await expect(page.locator(".demo-compare")).toHaveCount(0);
  await expect(page.getByTitle(/Isolated demonstration/)).toHaveCount(1);
});


test("ds-27 edge fade preview provides real horizontal overflow", async ({ page }) => {
  await page.goto("/play/ds-27/");
  const scroller = page.locator(".scroller-wrap > div");
  await expect(scroller).toBeVisible();
  const before = await scroller.evaluate(el => ({
    clientWidth: el.clientWidth,
    scrollWidth: el.scrollWidth,
    before: getComputedStyle(el.parentElement, "::before").content,
    after: getComputedStyle(el.parentElement, "::after").content,
  }));
  expect(before.scrollWidth).toBeGreaterThan(before.clientWidth);
  expect(before.before).not.toBe("none");
  expect(before.after).not.toBe("none");
  await scroller.evaluate(el => { el.scrollLeft = el.scrollWidth; });
  await expect.poll(() => scroller.evaluate(el => el.scrollLeft)).toBeGreaterThan(0);
});
