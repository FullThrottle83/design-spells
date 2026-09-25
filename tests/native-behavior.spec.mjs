/** Verify actual native spell behavior, not only that CSS parses or boxes exist.
 * Runs in Chromium, Firefox and WebKit, with client JavaScript disabled.
 * A passing test verifies only the named behavior, not WCAG conformance.
 */
import { test, expect } from "@playwright/test";

test.use({ javaScriptEnabled: false, reducedMotion: "reduce" });

test("ds-120 filters sibling cards using native checkboxes", async ({ page }) => {
  await page.goto("/play/ds-120/");
  const tech = page.locator('.matrix-card[data-cat="tech"]');
  const design = page.locator('.matrix-card[data-cat="design"]');
  const techInput = page.locator("#f-tech");
  const designInput = page.locator("#f-design");

  await expect(page.locator("script")).toHaveCount(0);
  await expect(techInput).toBeChecked();
  await expect(designInput).not.toBeChecked();
  await expect(tech).toBeVisible();
  await expect(design).toBeHidden();

  await designInput.focus();
  await page.keyboard.press("Space");
  await expect(designInput).toBeChecked();
  await expect(tech).toBeVisible();
  await expect(design).toBeVisible();

  await techInput.focus();
  await page.keyboard.press("Space");
  await expect(techInput).not.toBeChecked();
  await expect(tech).toBeHidden();
  await expect(design).toBeVisible();

  await designInput.focus();
  await page.keyboard.press("Space");
  await expect(designInput).not.toBeChecked();
  await expect(tech).toBeHidden();
  await expect(design).toBeHidden();
});

test("ds-132 named disclosures behave exclusively with keyboard activation", async ({ page }) => {
  await page.goto("/play/ds-132/");
  const first = page.locator(".faq-group details").nth(0);
  const second = page.locator(".faq-group details").nth(1);
  await expect(page.locator("script")).toHaveCount(0);
  await expect(first).not.toHaveAttribute("open", "");
  await expect(second).not.toHaveAttribute("open", "");

  await first.locator("summary").focus();
  await page.keyboard.press("Enter");
  await expect(first).toHaveAttribute("open", "");
  await expect(first.locator(".faq-content")).toBeVisible();

  await second.locator("summary").focus();
  await page.keyboard.press("Enter");
  await expect(second).toHaveAttribute("open", "");
  await expect(first).not.toHaveAttribute("open", "");
  await expect(first.locator(".faq-content")).toBeHidden();

  await page.keyboard.press("Enter");
  await expect(second).not.toHaveAttribute("open", "");
});

test("ds-128 uses native form validity for the visual meter", async ({ page }) => {
  await page.goto("/play/ds-128/");
  const input = page.locator(".pwd-input");
  const meter = page.locator(".pwd-meter span");
  const widthRatio = () => meter.evaluate(el => {
    const parentWidth = el.parentElement.getBoundingClientRect().width;
    return parentWidth ? el.getBoundingClientRect().width / parentWidth : 0;
  });
  await expect(page.locator("script")).toHaveCount(0);
  await input.fill("abc");
  expect(await input.evaluate(el => el.checkValidity())).toBe(false);
  await expect.poll(widthRatio).toBeGreaterThan(0.25);
  await expect.poll(widthRatio).toBeLessThan(0.5);

  await input.fill("Validpass1");
  expect(await input.evaluate(el => el.checkValidity())).toBe(true);
  await expect.poll(widthRatio).toBeGreaterThan(0.95);
});
