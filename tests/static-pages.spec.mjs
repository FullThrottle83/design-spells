import { test, expect } from "@playwright/test";

test.describe("static spell pages without scripting", () => {
  test.use({ javaScriptEnabled: false, reducedMotion: "reduce" });

  test("standalone docs expose accessible source and an isolated demo", async ({ page }) => {
    await page.goto("/spells/ds-1/");
    await expect(page.getByRole("heading", { name: "Shimmer on primary buttons" })).toBeVisible();
    const demo = page.getByTitle("Isolated demonstration: Shimmer on primary buttons");
    await expect(demo).toHaveAttribute("sandbox", "allow-same-origin");
    await expect(page.getByRole("link", { name: /Open standalone demo/ })).toHaveAttribute("href", "/play/ds-1/");
    await expect(page.locator("pre code")).toHaveCount(2);
    await expect(page.locator('script[src="/spell-copy.js"]')).toHaveCount(1);
    await expect(page.locator("script:not([src])")).toHaveCount(0);
  });

  test("catalogue provides direct links to independent pages without scripting", async ({ page }) => {
    await page.goto("/");
    const link = page.locator('.row[data-id="ds-1"] .row__link');
    await expect(link).toHaveAttribute("href", "/spells/ds-1/");
    await link.click();
    await expect(page).toHaveURL(/\/spells\/ds-1\/$/);
    await expect(page.getByRole("heading", { name: "Shimmer on primary buttons" })).toBeVisible();
  });

  test("cross-document transition uses actual page navigation", async ({ page }) => {
    await page.goto("/play/ds-14/");
    await expect(page.getByRole("heading", { name: "Page A" })).toBeVisible();
    await page.getByRole("link", { name: /Navigate to page B/ }).click();
    await expect(page).toHaveURL(/\/play\/ds-14\/next\/$/);
    await expect(page.getByRole("heading", { name: "Page B" })).toBeVisible();
    await expect(page.locator("script")).toHaveCount(0);
  });

  test("print example is a real document with print rules", async ({ page }) => {
    await page.goto("/play/ds-143/");
    await expect(page.getByRole("heading", { name: "A printable article" })).toBeVisible();
    await page.emulateMedia({ media: "print" });
    expect(await page.locator("style").allTextContents()).toEqual(expect.arrayContaining([expect.stringContaining("@media print")]));
  });
});
