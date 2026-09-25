import { test, expect } from "@playwright/test";

test("discard untrusted URL stack identifiers before rendering", async ({ page }) => {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const injected = 'ds-1,"><img src=x onerror=alert(1)>,ds-999';
  await page.goto("/classic/?stack=" + encodeURIComponent(injected));
  await expect(page.locator("#stack-count")).toHaveText("1");
  await expect(page.locator("#stack-items .stack-item")).toHaveCount(1);
  await expect(page.locator("#stack-items img")).toHaveCount(0);
  await expect(page).toHaveURL(/stack=ds-1(?:#|$)/);
  expect(errors).toEqual([]);
});

test("discard untrusted persisted identifiers", async ({ page }) => {
  await page.goto("/classic/");
  await page.evaluate(() => localStorage.setItem("ds-stack", JSON.stringify([
    "ds-1", '"><svg onload=alert(1)>', "ds-999", 42
  ])));
  await page.reload();
  await expect(page.locator("#stack-count")).toHaveText("1");
  await expect(page.locator("#stack-items .stack-item")).toHaveCount(1);
  await expect(page.locator("#stack-items svg")).toHaveCount(0);
});

test("storage-denied browsers retain working search and filters", async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(window, "localStorage", { configurable: true, get() {
      throw new DOMException("Storage blocked", "SecurityError");
    }});
  });
  await page.goto("/classic/");
  await expect(page.locator("#search")).toBeVisible();
  await page.locator("#search").fill("shimmer");
  await expect(page.locator(".row:visible")).toHaveCount(2);
  await page.locator("#theme-toggle").click();
  await expect(page.locator("#theme-toggle")).toBeVisible();
});

test("history without filter params clears previous state", async ({ page }) => {
  await page.goto("/classic/?q=shimmer&category=Interaction&status=baseline");
  await expect(page.locator("#search")).toHaveValue("shimmer");
  await page.evaluate(() => {
    history.pushState({}, "", "/classic/");
    dispatchEvent(new PopStateEvent("popstate"));
  });
  await expect(page.locator("#search")).toHaveValue("");
  await expect(page.locator('input[name="cat"][value="all"]')).toBeChecked();
  await expect(page.locator('input[name="status"][value="all"]')).toBeChecked();
});

test("unmodified global character shortcuts do not hijack focus", async ({ page }) => {
  await page.goto("/classic/");
  await page.locator("body").focus();
  await page.keyboard.press("j");
  await expect(page.locator(".row__hit").first()).not.toBeFocused();
  await page.keyboard.press("Control+k");
  await expect(page.locator("#search")).toBeFocused();
});

test("compatibility probes never claim component behavior as verified", async ({ page }) => {
  await page.goto("/classic/");
  await page.locator('.row[data-id="ds-1"] .row__hit').click();
  const result = page.locator('#drawer-ds-1 .feature-check');
  await expect(result).toContainText("This does not verify interactive behavior");
  await expect(result).not.toContainText("Every feature this spell needs runs");
});
