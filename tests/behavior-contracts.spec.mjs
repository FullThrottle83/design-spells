import { test, expect } from "@playwright/test";

// These are behavioral smoke checks, not an accessibility certification.
test.use({ javaScriptEnabled: false, reducedMotion: "reduce" });

test("manual toast has explicit native close and stays in the top layer until dismissed", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/play/ds-131/");
  expect(await page.evaluate(() => matchMedia("(prefers-reduced-motion: reduce)").matches)).toBe(true);
  const toast = page.locator("#auto-toast-1");
  await expect(page.locator("#auto-toast-1:popover-open")).toHaveCount(0);
  await page.getByRole("button", { name: "Show notification" }).click();
  await expect(toast).toHaveJSProperty("popover", "manual");
  await expect(toast).toHaveCSS("opacity", "1");
  await expect(page.locator("#auto-toast-1:popover-open")).toHaveCount(1);
  await expect(toast).toHaveCSS("transition-duration", "0s");
  await page.getByRole("button", { name: "Dismiss notification" }).click();
  await expect(page.locator("#auto-toast-1:popover-open")).toHaveCount(0);
});

test("wizard is a visual stepper, not an input-validation gate", async ({ page }) => {
  await page.goto("/play/ds-85/");
  await expect(page.locator(".wz-1")).toBeVisible();
  await page.locator('label[for="w-2"]').first().click();
  await expect(page.locator(".wz-2")).toBeVisible();
  await expect(page.locator(".wz-1")).toBeHidden();
  await expect(page.locator(".wz-2")).toContainText("Address");
  const source = await page.locator("style").textContent();
  expect(source).toContain(".wizard:has(#w-2:checked)");
  expect(source).not.toContain("checkValidity");
});
