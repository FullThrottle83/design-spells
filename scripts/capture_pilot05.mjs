/**
 * Pilot 05 evidence capture for the modal/dialog overlay spells
 * ds-66, ds-75, ds-77, ds-106.
 *
 * Every recorded value comes from a live document loaded with client scripts
 * disabled: real popover/dialog state, real geometry, real computed
 * ::backdrop styles, real focus movement. CSS.supports strings are recorded
 * only as context, never as a success criterion.
 *
 * Launch uses the repository's arena browser bootstrap (sandboxed Chromium,
 * loopback-only network boundary). No unsandboxed fallback exists.
 *
 * usage: node scripts/capture_pilot05.mjs [base] [prefix] [outDir]
 */
import { chromium } from '@playwright/test';
import fs from 'node:fs/promises';
import { arenaLaunchOptions, browserEnvironment } from './arena-browser/arena-launch-options.mjs';

const base = process.argv[2] || 'http://127.0.0.1:8791';
const prefix = process.argv[3] || 'before';
const out = process.argv[4] || 'docs/evidence/pilot-05';
const ids = [66, 75, 77, 106];
const settle = (p, ms = 300) => p.waitForTimeout(ms);
const launchOptions = await arenaLaunchOptions();

const rectOf = (loc) => loc.evaluate((e) => {
  const r = e.getBoundingClientRect();
  const round = (n) => Math.round(n * 100) / 100;
  return { x: round(r.x), y: round(r.y), width: round(r.width), height: round(r.height), right: round(r.right), bottom: round(r.bottom) };
});
const focusName = (page) => page.evaluate(() => {
  const a = document.activeElement;
  if (!a || a === document.body) return 'BODY';
  const label = (a.getAttribute('aria-label') || a.textContent || a.id || a.tagName).trim().replace(/\s+/g, ' ').slice(0, 40);
  return `${a.tagName.toLowerCase()}${a.id ? '#' + a.id : ''}:${label}`;
});
const backdropOf = (loc) => loc.evaluate((e) => {
  const b = getComputedStyle(e, '::backdrop');
  return { opacity: b.opacity, backgroundColor: b.backgroundColor, backdropFilter: b.backdropFilter, display: b.display, transitionDuration: b.transitionDuration };
});
const dialogState = (loc) => loc.evaluate((e) => ({ open: !!e.open, modal: e.matches(':modal'), display: getComputedStyle(e).display }));
const popState = (loc) => loc.evaluate((e) => ({ open: e.matches(':popover-open'), display: getComputedStyle(e).display }));

async function tabTo(page, loc, max = 16) {
  for (let i = 0; i < max; i++) {
    if (await loc.evaluate((e) => e === document.activeElement)) return i;
    await page.keyboard.press('Tab');
    await page.waitForTimeout(60);
  }
  return -1;
}

const browser = await chromium.launch({ ...launchOptions, env: browserEnvironment() });
const observations = { capturedAt: new Date().toISOString(), browserVersion: await browser.version(), base, prefix, states: [] };

for (const width of [1440, 390]) {
  const height = width === 390 ? 844 : 900;
  for (const id of ids) {
    console.error(`[probe] ds-${id} ${width} initial`);
    const context = await browser.newContext({ viewport: { width, height }, javaScriptEnabled: false });
    const page = await context.newPage();
    await page.goto(`${base}/play/ds-${id}/`);
    await settle(page);
    const state = { id: `ds-${id}`, width, initial: {} };
    state.initial.scripts = await page.evaluate(() => document.scripts.length);
    state.initial.scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    state.initial.innerWidth = await page.evaluate(() => innerWidth);
    state.initial.supportsStartingStyle = await page.evaluate(() => CSS.supports('transition: display 1s allow-discrete'));
    state.initial.supportsInvoker = await page.evaluate(() => 'command' in HTMLButtonElement.prototype);
    state.initial.supportsClosedby = await page.evaluate(() => 'closedBy' in HTMLDialogElement.prototype);
    state.initial.supportsPopover = await page.evaluate(() => 'popover' in HTMLElement.prototype);
    await page.screenshot({ path: `${out}/${prefix}-ds-${id}-${width}-initial.png` });

    if (id === 66) {
      const trigger = page.locator('[popovertarget], [commandfor]').first();
      const target = (await trigger.getAttribute('popovertarget')) || (await trigger.getAttribute('commandfor'));
      const pop = page.locator(`#${target}`);
      state.trigger = { target, text: ((await trigger.textContent()) || '').trim().slice(0, 60), rect: await rectOf(trigger) };
      state.closed = await popState(pop);
      await tabTo(page, trigger);
      state.keyboardTabsOk = await trigger.evaluate((e) => e === document.activeElement);
      await page.keyboard.press('Enter');
      await settle(page);
      state.keyboardOpened = await popState(pop);
      if (state.keyboardOpened.open) {
        state.openRect = await rectOf(pop);
        state.openBackdrop = await backdropOf(pop);
        state.focusAfterOpen = await focusName(page);
      }
      await page.screenshot({ path: `${out}/${prefix}-ds-${id}-${width}-active.png` });
      await page.keyboard.press('Escape');
      await settle(page, 200);
      state.escapeClosed = await popState(pop);
      state.focusAfterEscape = await focusName(page);
      await trigger.click();
      await settle(page);
      state.clickOpened = await popState(pop);
      await page.mouse.click(4, 4);
      await settle(page, 200);
      state.lightDismissClosed = await popState(pop);
    }

    if (id === 75) {
      const trigger = page.locator('.img-trigger, [commandfor], [popovertarget]').first();
      const target = (await trigger.getAttribute('commandfor')) || (await trigger.getAttribute('popovertarget'));
      const pop = page.locator(`#${target}`);
      const thumb = trigger.locator('img').first();
      state.trigger = { target, rect: await rectOf(trigger) };
      state.thumbnail = {
        rect: await rectOf(thumb),
        src: (await thumb.getAttribute('src') || '').slice(0, 80),
        alt: await thumb.getAttribute('alt'),
        natural: await thumb.evaluate((e) => ({ w: e.naturalWidth, h: e.naturalHeight })),
      };
      state.closed = await popState(pop);
      await tabTo(page, trigger);
      await page.keyboard.press('Enter');
      await settle(page);
      state.keyboardOpened = await popState(pop);
      const big = pop.locator('img').first();
      if (state.keyboardOpened.open && (await big.count())) {
        state.enlarged = {
          rect: await rectOf(big),
          src: (await big.getAttribute('src') || '').slice(0, 80),
          alt: await big.getAttribute('alt'),
          natural: await big.evaluate((e) => ({ w: e.naturalWidth, h: e.naturalHeight })),
        };
        state.popoverRect = await rectOf(pop);
        const t = state.thumbnail.rect, g = state.enlarged.rect;
        state.enlargement = { widthRatio: Math.round((g.width / Math.max(t.width, 1)) * 100) / 100, areaRatio: Math.round(((g.width * g.height) / Math.max(t.width * t.height, 1)) * 100) / 100 };
        state.sameSrc = state.enlarged.src === state.thumbnail.src;
      }
      state.focusAfterOpen = await focusName(page);
      await page.screenshot({ path: `${out}/${prefix}-ds-${id}-${width}-active.png` });
      await page.keyboard.press('Escape');
      await settle(page, 200);
      state.escapeClosed = await popState(pop);
      await trigger.click();
      await settle(page);
      state.clickOpened = await popState(pop);
      await page.mouse.click(4, 4);
      await settle(page, 200);
      state.lightDismissClosed = await popState(pop);
    }

    if (id === 77) {
      const trigger = page.locator('[commandfor]').first();
      const target = await trigger.getAttribute('commandfor');
      const dlg = page.locator(`#${target}`);
      state.trigger = { target, command: await trigger.getAttribute('command'), text: ((await trigger.textContent()) || '').trim().slice(0, 60), rect: await rectOf(trigger) };
      state.dialogCopy = ((await dlg.textContent()) || '').trim().replace(/\s+/g, ' ').slice(0, 200);
      state.closed = await dialogState(dlg);
      state.closedby = await dlg.getAttribute('closedby');
      await tabTo(page, trigger);
      await page.keyboard.press('Enter');
      await settle(page);
      state.keyboardOpened = await dialogState(dlg);
      if (state.keyboardOpened.open) {
        state.openRect = await rectOf(dlg);
        state.openBackdrop = await backdropOf(dlg);
        state.focusAfterOpen = await focusName(page);
        // Modality: the top-layer dialog must sit above page content.
        state.topLayerAbove = await dlg.evaluate((e) => {
          const r = e.getBoundingClientRect();
          const el = document.elementFromPoint(r.x + r.width / 2, r.y + Math.min(r.height / 2, 60));
          return e.contains(el) ? 'dialog-owns-point' : `outside:${el ? el.tagName : 'none'}`;
        });
      }
      await page.screenshot({ path: `${out}/${prefix}-ds-${id}-${width}-active.png` });
      await page.keyboard.press('Escape');
      await settle(page, 200);
      state.escapeClosed = await dialogState(dlg);
      state.focusAfterEscape = await focusName(page);
      await trigger.click();
      await settle(page);
      state.clickOpened = await dialogState(dlg);
      // Backdrop click: click well outside the dialog rect.
      const r = await rectOf(dlg);
      const bx = Math.max(4, Math.min(width - 4, r.x > 60 ? r.x - 30 : r.right + 30));
      await page.mouse.click(bx, height - 4 > r.bottom ? Math.min(height - 4, r.bottom + 20) : 4);
      await settle(page, 200);
      state.backdropClickClosed = await dialogState(dlg);
      if (state.backdropClickClosed.open) {
        // Fall back to the explicit close control for a clean end state.
        const closer = dlg.locator('button, [command]').last();
        await closer.click().catch(() => {});
        await settle(page, 200);
        state.explicitCloseClosed = await dialogState(dlg);
      }
    }

    if (id === 106) {
      const trigger = page.locator('[commandfor]').first();
      const target = await trigger.getAttribute('commandfor');
      const dlg = page.locator(`#${target}`);
      state.trigger = { target, command: await trigger.getAttribute('command'), text: ((await trigger.textContent()) || '').trim().slice(0, 60), rect: await rectOf(trigger) };
      state.dialogCopy = ((await dlg.textContent()) || '').trim().replace(/\s+/g, ' ').slice(0, 300);
      const buttons = dlg.locator('button');
      state.buttonLabels = [];
      for (let i = 0; i < (await buttons.count()); i++) state.buttonLabels.push(((await buttons.nth(i).textContent()) || '').trim());
      state.closed = await dialogState(dlg);
      await tabTo(page, trigger);
      await page.keyboard.press('Enter');
      await settle(page);
      state.keyboardOpened = await dialogState(dlg);
      if (state.keyboardOpened.open) {
        state.openRect = await rectOf(dlg);
        state.openBackdrop = await backdropOf(dlg);
        state.focusAfterOpen = await focusName(page);
      }
      await page.screenshot({ path: `${out}/${prefix}-ds-${id}-${width}-active.png` });
      // Cancel path: record whether anything observable changes besides closing.
      const urlBefore = page.url();
      const domBefore = await page.evaluate(() => document.body.innerHTML.length);
      await dlg.locator('button').first().click();
      await settle(page, 200);
      state.cancelClosed = await dialogState(dlg);
      state.cancelSideEffects = { urlChanged: page.url() !== urlBefore, domDelta: (await page.evaluate(() => document.body.innerHTML.length)) - domBefore };
      state.focusAfterCancel = await focusName(page);
      // Reopen, then the destructive-labelled path.
      await trigger.click();
      await settle(page);
      state.reopenWorks = await dialogState(dlg);
      await dlg.locator('button').last().click();
      await settle(page, 200);
      state.deleteClosed = await dialogState(dlg);
      state.deleteSideEffects = { urlChanged: page.url() !== urlBefore, domDelta: (await page.evaluate(() => document.body.innerHTML.length)) - domBefore };
      // Escape path.
      await trigger.click();
      await settle(page);
      await page.keyboard.press('Escape');
      await settle(page, 200);
      state.escapeClosed = await dialogState(dlg);
      state.focusAfterEscape = await focusName(page);
      // Backdrop light-dismiss path.
      await trigger.click();
      await settle(page);
      const dr = await rectOf(dlg);
      await page.mouse.click(4, 4);
      await settle(page, 200);
      // If the click landed inside the dialog (tiny viewport), try a corner outside it.
      let lightState = await dialogState(dlg);
      if (lightState.open && dr.x < 8 && dr.y < 8) {
        await page.mouse.click(width - 4, height - 4);
        await settle(page, 200);
        lightState = await dialogState(dlg);
      }
      state.lightDismissClosed = lightState;
    }

    // Fallback simulation: delete every @starting-style block, then reopen.
    await page.keyboard.press('Escape').catch(() => {});
    await settle(page, 150);
    await page.evaluate(() => {
      const strip = (owner) => {
        for (let i = owner.cssRules.length - 1; i >= 0; i--) {
          const rule = owner.cssRules[i];
          if (rule.constructor && rule.constructor.name === 'CSSStartingStyleRule') { owner.deleteRule(i); continue; }
          if (rule.cssRules) strip(rule);
        }
      };
      for (const sheet of document.styleSheets) { try { strip(sheet); } catch { /* cross-origin sheet */ } }
    });
    const reopenTrigger = page.locator('[commandfor], [popovertarget]').first();
    const reopenTarget = (await reopenTrigger.getAttribute('commandfor')) || (await reopenTrigger.getAttribute('popovertarget'));
    const reopenEl = page.locator(`#${reopenTarget}`);
    await reopenTrigger.click();
    await settle(page);
    const isDialog = id === 77 || id === 106;
    state.noStartingStyle = {
      opened: isDialog ? (await dialogState(reopenEl)).open : (await popState(reopenEl)).open,
      rect: await rectOf(reopenEl),
    };
    await page.screenshot({ path: `${out}/${prefix}-ds-${id}-${width}-fallback.png` });
    observations.states.push(state);
    await context.close();

    // Reduced-motion active capture in a fresh context.
    console.error(`[probe] ds-${id} ${width} reduced`);
    const rctx = await browser.newContext({ viewport: { width, height }, reducedMotion: 'reduce', javaScriptEnabled: false });
    const rpage = await rctx.newPage();
    await rpage.goto(`${base}/play/ds-${id}/`);
    await settle(rpage);
    const rentry = { id: `ds-${id}`, width, reducedMotion: true };
    const rtrigger = rpage.locator('[commandfor], [popovertarget]').first();
    const rtarget = (await rtrigger.getAttribute('commandfor')) || (await rtrigger.getAttribute('popovertarget'));
    const rel = rpage.locator(`#${rtarget}`);
    rentry.transitionDuration = await rel.evaluate((e) => getComputedStyle(e).transitionDuration);
    await rtrigger.click();
    await settle(rpage);
    rentry.opened = isDialog ? (await dialogState(rel)).open : (await popState(rel)).open;
    rentry.openRect = await rectOf(rel);
    rentry.openBackdrop = await backdropOf(rel);
    await rpage.screenshot({ path: `${out}/${prefix}-ds-${id}-${width}-reduced-active.png` });
    observations.states.push(rentry);
    await rctx.close();
  }
}

await fs.mkdir(out, { recursive: true });
await fs.writeFile(`${out}/${prefix}-observations.json`, JSON.stringify(observations, null, 2) + '\n');
await browser.close();
console.log(`captured ${observations.states.length} states -> ${out}/${prefix}-observations.json`);
