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

test("ds-1 keyboard focus activates its decorative shimmer without scripting", async ({ page }) => {
  await page.goto("/play/ds-1/");
  const button = page.getByRole("button", { name: "Get started" });
  const shimmerTransform = () => button.evaluate(
    (el) => getComputedStyle(el, "::before").transform,
  );
  await expect(page.locator("script")).toHaveCount(0);
  const initial = await shimmerTransform();
  await page.keyboard.press("Tab");
  await expect(button).toBeFocused();
  await expect.poll(shimmerTransform).not.toBe(initial);
  await expect(button).toHaveCSS("min-block-size", "44px");
});

test("ds-2 press effect returns to rest on release", async ({ page }) => {
  await page.goto("/play/ds-2/");
  const button = page.getByRole("button", { name: "Press me" });
  await expect(page.locator("script")).toHaveCount(0);
  const transform = () => button.evaluate((el) => getComputedStyle(el).transform);
  const initial = await transform();
  const box = await button.boundingBox();
  expect(box).not.toBeNull();
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await page.mouse.down();
  await expect.poll(transform).not.toBe(initial);
  await page.mouse.up();
  await expect.poll(transform).toBe(initial);
});

test("ds-90 quick actions are exposed by native disclosure and keyboard", async ({ page }) => {
  await page.goto("/play/ds-90/");
  const disclosure = page.locator("details.fan");
  const summary = disclosure.locator("summary");
  const action = disclosure.getByRole("button", { name: "New post" });
  await expect(page.locator("script")).toHaveCount(0);
  await expect(disclosure).not.toHaveAttribute("open", "");
  await summary.focus();
  await page.keyboard.press("Enter");
  await expect(disclosure).toHaveAttribute("open", "");
  await expect(action).toBeVisible();
  await page.keyboard.press("Enter");
  await expect(disclosure).not.toHaveAttribute("open", "");
  await expect(action).toBeHidden();
});

test("ds-18 tooltip decoration follows hover and keyboard focus without scripting", async ({ page }) => {
  await page.goto("/play/ds-18/");
  const trigger = page.getByRole("button", { name: "Hover me" });
  const opacity = () => trigger.evaluate(el => Number(getComputedStyle(el, "::after").opacity));
  // Firefox exposes the authored attr() expression in computed content while
  // WebKit/Chromium can expose its resolved string. Validate the source data
  // and pseudo-element wiring independently of CSSOM serialization.
  const content = await trigger.evaluate(el => getComputedStyle(el, "::after").content);
  await expect(page.locator("script")).toHaveCount(0);
  await expect(trigger).toHaveAttribute("data-tooltip", "Copied to clipboard");
  expect(content === "attr(data-tooltip)" || content.includes("Copied to clipboard")).toBe(true);
  await expect.poll(opacity).toBe(0);

  await page.keyboard.press("Tab");
  await expect(trigger).toBeFocused();
  await expect.poll(opacity).toBe(1);

  // This isolated demo has one focusable control; Firefox can cycle Tab
  // back to it. Explicitly blur it and move the pointer out before checking
  // the resting state, without adding any JavaScript to the shipped page.
  await page.mouse.move(0, 0);
  await trigger.evaluate(el => el.blur());
  await expect(trigger).not.toBeFocused();
  await expect.poll(opacity).toBe(0);
  await trigger.hover();
  await expect.poll(opacity).toBe(1);
  await page.mouse.move(0, 0);
  await expect.poll(opacity).toBe(0);
});
