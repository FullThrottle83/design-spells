/** A real stuck transition, not a syntax or geometry-only smoke test.
 * The demo contains no client JavaScript; page.evaluate only drives/observes
 * browser state from Playwright. This is not a WCAG audit.
 */
import { test, expect } from "@playwright/test";

test.use({ javaScriptEnabled: false, reducedMotion: "reduce" });

test("ds-44 sticky navigation reaches the inset and its supported shadow toggles", async ({ page, browser, browserName }) => {
  await page.setViewportSize({ width: 900, height: 700 });
  await page.goto("/play/ds-44/");
  const nav = page.locator(".toc");
  const inner = page.locator(".toc__inner");
  const shadow = () => inner.evaluate(el => getComputedStyle(el).boxShadow);
  const top = () => nav.evaluate(el => el.getBoundingClientRect().top);

  await expect(page.locator("script")).toHaveCount(0);
  await expect(nav).toHaveCSS("position", "sticky");
  await expect(page.getByText("On this page")).toBeVisible();
  const initialTop = await top();
  expect(initialTop, "fixture must start before the sticky threshold").toBeGreaterThan(70);
  expect(await shadow(), "the unstuck state must not have a shadow").toBe("none");
  const runway = await page.evaluate(() => document.documentElement.scrollHeight - innerHeight);
  expect(runway, "document must provide a real scrolling runway").toBeGreaterThan(300);

  await page.evaluate(() => window.scrollTo({ top: 240, behavior: "instant" }));
  await expect.poll(() => page.evaluate(() => scrollY)).toBeGreaterThan(120);
  await expect.poll(top).toBeGreaterThan(12);
  await expect.poll(top).toBeLessThan(20);

  // Syntax support alone is never promoted to behavior verification.
  // Chromium must show an observed shadow; other engines either demonstrate
  // the same transition or retain usable native sticky positioning.
  const declaresContainer = await page.evaluate(() => CSS.supports("container-type", "scroll-state"));
  console.log(`ds-44 ${browserName} ${browser.version()} scroll-state declaration=${declaresContainer}`);
  if (browserName === "chromium" || declaresContainer) {
    await expect.poll(shadow, { message: "stuck: top must change the rendered shadow" }).not.toBe("none");
    await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
    await expect.poll(top).toBeGreaterThan(70);
    await expect.poll(shadow, { message: "unsticking must remove the rendered shadow" }).toBe("none");
  } else {
    await expect(inner).toBeVisible();
    await expect.poll(shadow).toBe("none");
    await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
    await expect.poll(top).toBeGreaterThan(70);
  }
});
