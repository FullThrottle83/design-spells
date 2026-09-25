import { test, expect } from "@playwright/test";

for (const enabled of [false, true]) {
  test.describe(`light homepage with scripting ${enabled ? "enabled" : "disabled"}`, () => {
    test.use({ javaScriptEnabled: enabled, reducedMotion: "reduce" });

    test("category navigation, full docs and isolated demos work", async ({ page }) => {
      await page.goto("/");
      await expect(page.locator(".row")).toHaveCount(150);
      await expect(page.locator(".row[data-id='ds-1'] .row__link")).toHaveAttribute("href", "/spells/ds-1/");
      await expect(page.locator(".row[data-id='ds-1'] .row__demo")).toHaveAttribute("href", "/play/ds-1/");
      await expect(page.locator(".catalogue-tools")).toBeVisible({ visible: enabled });
      await page.locator(".row[data-id='ds-1'] .row__link").click();
      await expect(page).toHaveURL(/\/spells\/ds-1\/$/);
      await expect(page.locator("iframe")).toHaveAttribute("sandbox", "allow-same-origin");
    });

    test("has no page-level horizontal overflow on small screens", async ({ page }) => {
      await page.goto("/");
      for (const width of [320, 390, 768, 1280]) {
        await page.setViewportSize({ width, height: 900 });
        const size = await page.evaluate(() => ({
          client: document.documentElement.clientWidth,
          scroll: document.documentElement.scrollWidth,
          offenders: [...document.querySelectorAll("body *")].map(el => ({
            node: el.tagName.toLowerCase() + "." + el.className,
            right: Math.round(el.getBoundingClientRect().right),
            width: Math.round(el.getBoundingClientRect().width),
          })).filter(el => el.right > document.documentElement.clientWidth + 1).slice(0,12),
        }));
        expect(size.scroll, `overflow at ${width}px: ${JSON.stringify(size.offenders)}`).toBeLessThanOrEqual(size.client);
      }
    });
  });
}

test("optional search filters metadata, not embedded CSS", async ({ page }) => {
  await page.goto("/?q=shimmer");
  await expect(page.locator("#search")).toHaveValue("shimmer");
  await expect(page.locator(".row:visible")).toHaveCount(2);
  await expect(page.locator("#result-count")).toContainText("2 of 150");
  await page.locator("#search").fill("");
  await expect(page.locator(".row:visible")).toHaveCount(150);
  await expect(page).not.toHaveURL(/\?q=/);
});

test("failed enhancement leaves ordinary browsing intact", async ({ page }) => {
  await page.route("**/catalogue.js", route => route.abort());
  await page.goto("/");
  await expect(page.locator(".catalogue-tools")).toBeHidden();
  await page.locator(".row[data-id='ds-1'] .row__link").click();
  await expect(page).toHaveURL(/\/spells\/ds-1\/$/);
});
