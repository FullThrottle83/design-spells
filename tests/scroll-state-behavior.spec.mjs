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

for (const motion of ["reduce", "no-preference"]) {
  test(`ds-45 snapped card changes its actual spotlight state (${motion})`, async ({ page, browser, browserName }) => {
    await page.emulateMedia({ reducedMotion: motion });
    await page.setViewportSize({ width: 900, height: 700 });
    await page.goto("/play/ds-45/");

    const carousel = page.getByRole("region", { name: "Snapped cards" });
    const cards = page.locator(".slide > article");
    const opacity = index => cards.nth(index).evaluate(el => Number(getComputedStyle(el).opacity));
    const transform = index => cards.nth(index).evaluate(el => getComputedStyle(el).transform);
    const scrollLeft = () => carousel.evaluate(el => el.scrollLeft);
    const supported = await page.evaluate(() => CSS.supports("container-type", "scroll-state"));

    await expect(page.locator("script")).toHaveCount(0);
    await expect(carousel).toHaveAttribute("tabindex", "0");
    await expect(carousel).toHaveCSS("scroll-snap-type", /mandatory/);
    expect(await carousel.evaluate(el => el.scrollWidth - el.clientWidth)).toBeGreaterThan(100);
    await expect(cards).toHaveCount(3);
    console.log(`ds-45 ${browserName} ${browser.version()} motion=${motion} declaration=${supported}`);

    // The named scroller can take keyboard focus without client JavaScript.
    await page.keyboard.press("Tab");
    await expect(carousel).toBeFocused();
    if (browserName === "chromium" || supported) {
      await expect.poll(() => opacity(0), { message: "first snapped card should become opaque" }).toBeGreaterThan(0.95);
      await expect.poll(() => opacity(1)).toBeLessThan(0.65);
      expect(await transform(0)).toBe("matrix(1, 0, 0, 1, 0, 0)");
    } else {
      await expect.poll(() => opacity(0)).toBeLessThan(0.65);
      await expect.poll(() => opacity(1)).toBeLessThan(0.65);
    }

    await carousel.evaluate(el => el.scrollTo({ left: el.clientWidth * 0.7, behavior: "instant" }));
    await expect.poll(scrollLeft, { message: "the carousel must actually scroll" }).toBeGreaterThan(100);
    if (browserName === "chromium" || supported) {
      await expect.poll(() => opacity(1), { message: "second snapped card should become opaque" }).toBeGreaterThan(0.95);
      await expect.poll(() => opacity(0), { message: "first card should lose spotlight" }).toBeLessThan(0.65);
      expect(await transform(1)).toBe("matrix(1, 0, 0, 1, 0, 0)");
    } else {
      await expect.poll(() => opacity(1)).toBeLessThan(0.65);
      await expect(cards.nth(1)).toBeVisible();
    }
  });

  test(`ds-46 scrollability and hint change together via native checkbox (${motion})`, async ({ page, browser, browserName }) => {
    await page.emulateMedia({ reducedMotion: motion });
    await page.setViewportSize({ width: 900, height: 700 });
    await page.goto("/play/ds-46/");

    const scroller = page.getByRole("region", { name: "Scrollable labels" });
    const checkbox = page.getByRole("checkbox", { name: "Fit content without horizontal scrolling" });
    const hint = page.locator(".fade-hint");
    const overflow = () => scroller.evaluate(el => el.scrollWidth - el.clientWidth);
    const opacity = () => hint.evaluate(el => Number(getComputedStyle(el).opacity));
    const supported = await page.evaluate(() => CSS.supports("container-type", "scroll-state"));
    console.log(`ds-46 ${browserName} ${browser.version()} motion=${motion} declaration=${supported}`);

    await expect(page.locator("script")).toHaveCount(0);
    await expect(checkbox).not.toBeChecked();
    await expect(scroller).toHaveAttribute("tabindex", "0");
    await expect.poll(overflow, { message: "the initial content must really overflow" }).toBeGreaterThan(200);
    if (browserName === "chromium" || supported) {
      await expect.poll(opacity, { message: "scrollable inline must reveal the hint" }).toBeGreaterThan(0.95);
    } else {
      await expect.poll(opacity).toBe(0);
    }

    await page.keyboard.press("Tab");
    await expect(checkbox).toBeFocused();
    await page.keyboard.press("Space");
    await expect(checkbox).toBeChecked();
    await expect.poll(overflow, { message: "wrapping must remove actual horizontal overflow" }).toBeLessThanOrEqual(1);
    await expect.poll(opacity, { message: "non-scrollable content must hide the hint" }).toBe(0);

    await page.keyboard.press("Space");
    await expect(checkbox).not.toBeChecked();
    await expect.poll(overflow).toBeGreaterThan(200);
    if (browserName === "chromium" || supported) {
      await expect.poll(opacity, { message: "restoring overflow must restore the hint" }).toBeGreaterThan(0.95);
    } else {
      await expect.poll(opacity).toBe(0);
    }
    await page.keyboard.press("Tab");
    await expect(scroller).toBeFocused();
  });
}
