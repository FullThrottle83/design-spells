/**
 * Pilot 04 evidence capture for the native-overlay spells ds-79, ds-89, ds-142.
 *
 * Every recorded value comes from a live document loaded with client scripts
 * disabled: real popover state (`:popover-open`), real geometry, real focus
 * movement, real navigation results. CSS.supports strings are recorded only as
 * context, never as a success criterion.
 *
 * usage: CHROMIUM_PATH=/tmp/chromium node scripts/capture_pilot04.mjs [base] [prefix] [outDir]
 */
import { chromium } from '@playwright/test';
import fs from 'node:fs/promises';

const base = process.argv[2] || 'http://127.0.0.1:8790';
const prefix = process.argv[3] || 'before';
const out = process.argv[4] || 'docs/evidence/pilot-04';
const ids = [79, 89, 142];
const settle = (p, ms = 260) => p.waitForTimeout(ms);
// The demo documents opt into smooth scrolling; wait for real scroll rest before
// measuring or clicking so geometry reflects settled state, not mid-glide frames.
const settleScroll = async (p) => {
  // Harness-side polling with synchronous evaluates only: with client scripts
  // disabled the page never runs timers or rAF callbacks, so any evaluate that
  // returns a promise would hang forever.
  let last = -1; let still = 0;
  for (let i = 0; i < 24; i++) {
    const y = await p.evaluate(() => scrollY);
    if (y === last) { still += 1; if (still >= 2) return y; } else { still = 0; last = y; }
    await p.waitForTimeout(60);
  }
  return last;
};
const rectOf = (loc) => loc.evaluate((e) => {
  const r = e.getBoundingClientRect();
  return { x: Math.round(r.x * 100) / 100, y: Math.round(r.y * 100) / 100, width: Math.round(r.width * 100) / 100, height: Math.round(r.height * 100) / 100, right: Math.round(r.right * 100) / 100, bottom: Math.round(r.bottom * 100) / 100 };
});
const viewportOf = (loc) => loc.evaluate(() => ({ w: innerWidth, h: innerHeight }));
const contained = (r, v) => r.x >= -1 && r.y >= -1 && r.right <= v.w + 1 && r.bottom <= v.h + 1;

async function focusSequence(page, root, steps) {
  const names = [];
  for (let i = 0; i < steps; i++) {
    await page.keyboard.press('Tab');
    await page.waitForTimeout(70);
    names.push(await root.evaluate(() => {
      const a = document.activeElement;
      if (!a || a === document.body) return 'BODY';
      const label = (a.getAttribute('aria-label') || a.textContent || a.id || a.tagName).trim().replace(/\s+/g, ' ').slice(0, 34);
      return `${a.tagName.toLowerCase()}${a.id ? '#' + a.id : ''}:${label}`;
    }));
  }
  return names;
}

async function probeOverlay(page, root, trigger, popover, viewport, shotPath) {
  const result = {};
  result.triggerRect = await rectOf(trigger);
  result.command = { commandfor: await trigger.getAttribute('commandfor'), command: await trigger.getAttribute('command'), haspopup: await trigger.getAttribute('aria-haspopup') };
  // Keyboard activation: Tab until the trigger owns focus.
  let tabs = 0;
  for (; tabs < 12; tabs++) {
    if (await trigger.evaluate((e) => e === document.activeElement)) break;
    await page.keyboard.press('Tab');
    await page.waitForTimeout(70);
  }
  result.keyboardTabsToTrigger = tabs;
  result.triggerFocused = await trigger.evaluate((e) => e === document.activeElement);
  await page.keyboard.press('Enter');
  await settle(page);
  result.keyboardOpened = await popover.evaluate((e) => e.matches(':popover-open'));
  result.openRect = result.keyboardOpened ? await rectOf(popover) : null;
  result.openContained = result.openRect ? contained(result.openRect, viewport) : null;
  result.openPosition = result.keyboardOpened ? await popover.evaluate((e) => getComputedStyle(e).position) : null;
  result.focusAfterOpen = await root.evaluate(() => {
    const a = document.activeElement;
    if (!a || a === document.body) return 'BODY';
    return `${a.tagName.toLowerCase()}${a.id ? '#' + a.id : ''}:${(a.getAttribute('aria-label') || a.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 34)}`;
  });
  result.focusInsidePopover = await popover.evaluate((e) => e.contains(document.activeElement));
  if (shotPath) { await settleScroll(page); await page.screenshot({ path: shotPath }); }
  result.focusChain = await focusSequence(page, root, 4);
  await page.keyboard.press('Escape');
  await settleScroll(page);
  await settle(page);
  result.escapeClosed = await popover.evaluate((e) => !e.matches(':popover-open'));
  result.focusAfterEscape = await root.evaluate(() => {
    const a = document.activeElement;
    if (!a || a === document.body) return 'BODY';
    return `${a.tagName.toLowerCase()}${a.id ? '#' + a.id : ''}`;
  });
  // Pointer path: click open, then click far outside for light-dismiss.
  await settleScroll(page);
  await trigger.click();
  await settle(page);
  result.clickOpened = await popover.evaluate((e) => e.matches(':popover-open'));
  await page.mouse.click(4, 4);
  await settle(page, 150);
  result.lightDismissClosed = await popover.evaluate((e) => !e.matches(':popover-open'));
  return result;
}

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH });
const observations = { capturedAt: new Date().toISOString(), browserVersion: await browser.version(), base, prefix, states: [] };

for (const width of [1440, 390]) {
  const height = width === 390 ? 844 : 900;
  for (const id of ids) {
    const context = await browser.newContext({ viewport: { width, height }, javaScriptEnabled: false });
    const page = await context.newPage();
    await page.goto(`${base}/play/ds-${id}/`);
    await settle(page);
    const viewport = { w: width, h: height };
    const state = { id: `ds-${id}`, width, initial: { scripts: await page.evaluate(() => document.scripts.length), scrollWidth: await page.evaluate(() => document.documentElement.scrollWidth), innerWidth: await page.evaluate(() => innerWidth), supportsAnchor: await page.evaluate(() => CSS.supports('position-anchor: --probe')), supportsInvoker: await page.evaluate(() => 'command' in HTMLButtonElement.prototype) } };
    await page.screenshot({ path: `${out}/${prefix}-ds-${id}-${width}-initial.png` });
    const triggers = page.locator('[command="toggle-popover"]');
    const triggerCount = await triggers.count();
    state.triggerCount = triggerCount;
    state.popoverCount = await page.locator('[popover]').count();
    state.overlays = [];
    for (let i = 0; i < triggerCount; i++) {
      console.error(`[probe] ds-${id} ${width} trigger ${i}`);
      const trigger = triggers.nth(i);
      const target = await trigger.getAttribute('commandfor');
      const pop = page.locator(`#${target}`);
      state.overlays.push({ target, ...(await probeOverlay(page, page, trigger, pop, viewport, i === 0 ? `${out}/${prefix}-ds-${id}-${width}-active.png` : null)) });
    }
    console.error(`[probe] ds-${id} ${width} extras`);
    if (id === 79) {
      const links = page.locator('.mega-panel a, [popover] a');
      const hrefs = [];
      for (let i = 0; i < await links.count(); i++) hrefs.push(await links.nth(i).getAttribute('href'));
      state.panelLinks = hrefs;
      state.fragmentTargets = await page.evaluate((list) => list.map((h) => ({ href: h, exists: !!document.querySelector(h) })), hrefs.filter((h) => h && h.startsWith('#')));
      state.linkStatus = [];
      for (const href of [...new Set(hrefs.filter((h) => h && !h.startsWith('#')))]) {
        const probe = await context.newPage();
        const response = await probe.goto(href.startsWith('http') ? href : `${base}${href.startsWith('/') ? href : '/' + href}`).catch((e) => null);
        state.linkStatus.push({ href, status: response ? response.status() : 'navigation-error' });
        await probe.close();
      }
    }
    if (id === 89) {
      const trigger = triggers.first();
      await trigger.click();
      await settle(page);
      const before = await page.evaluate(() => document.body.innerHTML.length);
      const url = page.url();
      const items = page.locator('#ctx-menu button, [popover] button');
      const clicks = [];
      for (let i = 0; i < await items.count(); i++) {
        const label = (await items.nth(i).textContent() || '').trim();
        await items.nth(i).click().catch(() => {});
        await settle(page, 160);
        clicks.push({ label, stillOpen: await page.locator('[popover]').first().evaluate((e) => e.matches(':popover-open')), urlUnchanged: page.url() === url });
        if (!(await page.locator('[popover]').first().evaluate((e) => e.matches(':popover-open')))) { await trigger.click(); await settle(page); }
      }
      const after = await page.evaluate(() => document.body.innerHTML.length);
      state.menuActions = { clicks, domLengthDelta: after - before, urlUnchanged: page.url() === url };
    }
    if (id === 142) {
      state.pinCount = await page.locator('.map-pin, [class*="pin"]').count();
      state.popoverTexts = [];
      const pops = page.locator('[popover]');
      for (let i = 0; i < await pops.count(); i++) state.popoverTexts.push((await pops.nth(i).textContent() || '').trim().replace(/\s+/g, ' ').slice(0, 60));
    }
    console.error(`[probe] ds-${id} ${width} fallback`);
    // Unsupported anchor-positioning simulation: drop the @supports (position-anchor …) blocks.
    await page.evaluate(() => {
      // Recursively drop every @supports block whose condition probes anchor(),
      // including those nested inside media queries: this simulates an engine
      // without anchor positioning while leaving all other rules intact.
      const strip = (owner) => {
        for (let i = owner.cssRules.length - 1; i >= 0; i--) {
          const rule = owner.cssRules[i];
          if (rule.cssRules && rule.cssRules.length !== undefined && !(rule.conditionText || '').includes('anchor(')) { strip(rule); continue; }
          if ((rule.conditionText || '').includes('anchor(')) owner.deleteRule(i);
        }
      };
      for (const sheet of document.styleSheets) strip(sheet);
    });
    const firstTrigger = triggers.first();
    const firstTarget = await firstTrigger.getAttribute('commandfor');
    const fallbackPop = page.locator(`#${firstTarget}`);
    await page.keyboard.press('Escape');
    await settle(page, 200);
    await settleScroll(page);
    await firstTrigger.click();
    await settle(page);
    state.fallback = {
      opened: await fallbackPop.evaluate((e) => e.matches(':popover-open')),
      rect: await rectOf(fallbackPop),
      position: await fallbackPop.evaluate((e) => getComputedStyle(e).position),
      visibleText: (await fallbackPop.textContent() || '').trim().replace(/\s+/g, ' ').slice(0, 60),
    };
    state.fallback.contained = contained(state.fallback.rect, viewport);
    await page.screenshot({ path: `${out}/${prefix}-ds-${id}-${width}-fallback.png` });
    observations.states.push(state);
    await context.close();
  }
}

// Contact sheet input: also grab the catalogue preview tile state.
await fs.mkdir(out, { recursive: true });
await fs.writeFile(`${out}/${prefix}-observations.json`, JSON.stringify(observations, null, 2) + '\n');
await browser.close();
console.log(`captured ${observations.states.length} states -> ${out}/${prefix}-observations.json`);
