import { test, expect } from "@playwright/test";

test("integration bundle is a native source link when scripts are disabled", async ({ page, request }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/classic/");
  await page.getByRole("button", { name: "Shimmer on primary buttons", exact: true }).click();
  const drawer = page.locator("#drawer-ds-1");
  const link = drawer.getByRole("link", { name: "View integration source" });
  await expect(link).toHaveAttribute("href", "/bundle/ds-1.txt");
  const response = await request.get("/bundle/ds-1.txt");
  expect(response.status()).toBe(200);
  const text = await response.text();
  expect(text).toContain("Design Spells ds-1: integration source");
  expect(text).toContain(".btn-primary");
  expect(text).not.toContain("box-sizing: border-box");
});

test.describe("integration source without client JS", () => {
  test.use({ javaScriptEnabled: false, reducedMotion: "reduce" });

  test("source link is visible while copy enhancement is hidden", async ({ page }) => {
    await page.goto("/classic/");
    await page.getByRole("button", { name: "Shimmer on primary buttons", exact: true }).click();
    const drawer = page.locator("#drawer-ds-1");
    await expect(drawer.getByRole("link", { name: "View integration source" })).toBeVisible();
    await expect(drawer.locator("[data-copy-bundle]")).toBeHidden();
  });
});

test("optional copy writes exactly the generated bundle, not the raw CSS tab", async ({ page, request }) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText: async (source) => { window.__copiedBundle = source; } },
    });
  });
  await page.goto("/classic/");
  await page.getByRole("button", { name: "Shimmer on primary buttons", exact: true }).click();
  const drawer = page.locator("#drawer-ds-1");
  await drawer.getByRole("button", { name: "Copy integration bundle" }).click();
  await expect(drawer.locator("[data-bundle-status]")).toContainText("Integration source copied");
  const clipboard = await page.evaluate(() => window.__copiedBundle);
  expect(clipboard).toBe(await (await request.get("/bundle/ds-1.txt")).text());
  expect(clipboard).toContain("<html lang=");
});

test("failed fetch never claims successful copy", async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText: async () => { window.__copiedBundle = true; } },
    });
  });
  await page.route("**/bundle/ds-1.txt", route => route.fulfill({ status: 503, body: "not ready" }));
  await page.goto("/classic/");
  await page.getByRole("button", { name: "Shimmer on primary buttons", exact: true }).click();
  const drawer = page.locator("#drawer-ds-1");
  await drawer.getByRole("button", { name: "Copy integration bundle" }).click();
  await expect(drawer.locator("[data-bundle-status]")).toContainText("Copy failed");
  expect(await page.evaluate(() => window.__copiedBundle)).toBeUndefined();
});
