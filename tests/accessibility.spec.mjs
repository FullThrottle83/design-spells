import { test, expect } from '@playwright/test';

// Exercise the published HTML/CSS path as well as progressive enhancement.
for (const mode of ['disabled', 'blocked', 'enabled']) {
  test.describe(`catalogue with JavaScript ${mode}`, () => {
    test.use({ javaScriptEnabled: mode !== 'disabled', reducedMotion: 'reduce' });

    test.beforeEach(async ({ page }) => {
      if (mode === 'blocked') await page.route('**/search.js', route => route.abort());
      await page.goto('/classic/');
    });

    test('filters, source disclosures and keyboard dismissal remain usable', async ({ page }) => {
      const enhanced = mode === 'enabled';
      await expect(page.locator('#search-form')).toBeVisible({ visible: enhanced });
      await expect(page.locator('.fallback-help')).toBeVisible({ visible: !enhanced });
      await expect(page.locator('#theme-toggle')).toBeVisible({ visible: enhanced });
      await page.locator('.nav-item').filter({ has: page.locator('input[name="cat"][value="Interaction"]') }).click();
      await expect(page.locator('.cat-block[data-cat="Forms"]')).toBeHidden();
      await expect(page.locator('.row[data-id="ds-1"]')).toBeVisible();

      const trigger = page.getByRole('button', { name: 'Shimmer on primary buttons', exact: true });
      await trigger.focus();
      await page.keyboard.press('Enter');
      const panel = page.getByRole('dialog', { name: 'Shimmer on primary buttons', exact: true });
      await expect(panel).toBeVisible();
      await expect(panel).not.toHaveAttribute('aria-modal', 'true');
      await expect(panel.getByRole('button', { name: 'Close panel', exact: true })).toBeFocused();
      await expect(page.locator('#main')).not.toHaveAttribute('inert');
      await expect(panel.locator('.code__copy')).toBeVisible({ visible: enhanced });
      await expect(panel.locator('.stage-controls')).toBeVisible({ visible: enhanced });
      await panel.getByText('HTML', { exact: true }).click();
      await expect(panel.locator('details[open] summary')).toHaveText('HTML');
      await expect(panel.locator('details[open] code')).not.toBeEmpty();
      await page.keyboard.press('Escape');
      await expect(panel).toBeHidden();
      await expect(trigger).toBeFocused();
    });

    test('preview radios have names; mobile layout has no page overflow', async ({ page }) => {
      await expect(page.getByRole('radio', { name: 'Pin preview: Shimmer on primary buttons', exact: true })).toHaveCount(1);
      for (const width of [320, 390, 768, 1280]) {
        await page.setViewportSize({ width, height: 900 });
        const geometry = await page.evaluate(() => ({
          width: document.documentElement.clientWidth,
          scroll: document.documentElement.scrollWidth,
        }));
        expect(geometry.scroll, `page overflow at ${width}px`).toBeLessThanOrEqual(geometry.width);
        await expect(page.locator('#select-ds-1')).toBeVisible({ visible: width >= 960 });
      }
    });
  });
}

test('native popover toggle updates deep links and compatibility text', async ({ page }) => {
  await page.goto('/classic/');
  await page.getByRole('button', { name: 'Shimmer on primary buttons', exact: true }).click();
  await expect(page).toHaveURL(/#ds-1$/);
  await expect(page.locator('#drawer-ds-1 .feature-check')).not.toContainText('Checking');
  await page.keyboard.press('Escape');
  await expect(page.locator('#drawer-ds-1')).toBeHidden();
  await expect(page).not.toHaveURL(/#ds-1$/);
});

test('document previews retain a safe sandbox and descriptive titles', async ({ page }) => {
  await page.goto('/classic/');
  const frames = page.locator('iframe.ds-document');
  expect(await frames.count()).toBeGreaterThan(0);
  for (const frame of await frames.all()) {
    await expect(frame).toHaveAttribute('title', /^Live preview: .+/);
    await expect(frame).toHaveAttribute('loading', 'lazy');
    await expect(frame).toHaveAttribute('sandbox', 'allow-same-origin');
  }
});
