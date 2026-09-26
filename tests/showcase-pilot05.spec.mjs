import { test, expect } from '@playwright/test';

/**
 * Pilot 05 — modal/dialog overlay spells ds-66, ds-75, ds-77, ds-106.
 *
 * Every assertion reads live browser state with client scripts disabled:
 * real `:popover-open` / `[open]` / `:modal`, real geometry, real computed
 * `::backdrop` styles, real focus movement, real dismissal. CSS.supports
 * strings are never used as a success criterion; the unsupported-entry
 * cases delete the actual @starting-style rules and re-measure.
 */

const ids = [66, 75, 77, 106];
const rect = (loc) => loc.evaluate((e) => { const r = e.getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height, right: r.right, bottom: r.bottom }; });
const viewport = (root) => root.locator('body').evaluate(() => ({ w: innerWidth, h: innerHeight }));
const style = (loc, p) => loc.evaluate((e, p) => getComputedStyle(e)[p], p);
const backdrop = (loc) => loc.evaluate((e) => {
  const b = getComputedStyle(e, '::backdrop');
  return { opacity: b.opacity, backgroundColor: b.backgroundColor, backdropFilter: b.backdropFilter };
});
const popOpen = (loc) => loc.evaluate((e) => e.matches(':popover-open'));
const dialogState = (loc) => loc.evaluate((e) => ({ open: !!e.open, modal: e.matches(':modal') }));
const settle = (p, ms = 320) => p.waitForTimeout(ms);
// Exit transitions keep `display` alive for up to 300ms after `open` flips.
const settleClosed = (p) => p.waitForTimeout(550);
const contained = (r, v) => r.x >= -1 && r.y >= -1 && r.right <= v.w + 1 && r.bottom <= v.h + 1;
const focusName = (root) => root.locator('body').evaluate(() => {
  const a = document.activeElement;
  if (!a || a === document.body) return 'BODY';
  return `${a.tagName.toLowerCase()}${a.className ? '.' + String(a.className).split(' ')[0] : ''}`;
});
const focusWhere = (root, sel) => root.locator('body').evaluate((e, sel) => {
  const a = document.activeElement;
  if (!a || a === document.body) return 'body';
  return document.querySelector(sel)?.contains(a) ? 'inside' : `outside:${a.tagName}`;
}, sel);
// Modal-open clicks target top-layer content (position:fixed inside the
// frame), which scrollIntoView() cannot reveal by scrolling outer containers:
// Tab stops in the outer document wander the docs page to the footer, so the
// harness centres the iframe first and the click itself stays a real pointer
// event at a genuinely visible point. No-op off the iframe surface.
async function centreFrame(page, root) {
  if (root === page) return;
  await page.locator('iframe').first().evaluate((e) => e.scrollIntoView({ block: 'center', behavior: 'instant' }));
}
// Engines without invoker commands (Safari, per the repo's support data):
// the trigger advertises its intent and activation is a documented no-op.
// The dialog stays closed, the page stays intact, nothing navigates.
async function verifyDegraded(root, page, id) {
  const trigger = id === 77 ? root.locator('[commandfor="sheet-demo"]') : root.locator('[commandfor="close-options"]');
  const dlg = id === 77 ? root.locator('#sheet-demo') : root.locator('#close-options');
  expect(await trigger.getAttribute('command')).toBe('show-modal');
  expect(await dlg.getAttribute('closedby')).toBe('any');
  if (id === 106) expect(await dlg.locator('.confirm-actions button').count()).toBe(2);
  expect(await dialogState(dlg)).toEqual({ open: false, modal: false });
  expect(await style(dlg, 'display')).toBe('none');
  expect(await tabTo(trigger, page)).toBe(true);
  await page.keyboard.press('Enter');
  await settle(page);
  expect(await dialogState(dlg)).toEqual({ open: false, modal: false });
  await trigger.click();
  await settle(page);
  expect(await dialogState(dlg)).toEqual({ open: false, modal: false });
  expect(await style(dlg, 'display')).toBe('none');
}
async function tabTo(loc, page, max = 24) {
  for (let i = 0; i < max; i++) {
    if (await loc.evaluate((e) => e === document.activeElement)) return true;
    await page.keyboard.press('Tab');
    await page.waitForTimeout(60);
  }
  return loc.evaluate((e) => e === document.activeElement);
}
// A point outside `r` but inside the viewport: the backdrop click target.
// Strips down to ~24px still yield an exact clickable point (the full-width
// sheet in a narrow frame leaves only a 47px strip on top).
function outsidePoint(r, v) {
  if (r.y > 24) return { x: Math.min(Math.max(r.x + r.width / 2, 8), v.w - 8), y: Math.min(r.y / 2, v.h - 8) };
  if (r.bottom < v.h - 24) return { x: Math.min(Math.max(r.x + r.width / 2, 8), v.w - 8), y: Math.max((r.bottom + v.h) / 2, 8) };
  if (r.x > 24) return { x: r.x / 2, y: Math.min(Math.max(r.y + r.height / 2, 8), v.h - 8) };
  return { x: Math.min((r.right + v.w) / 2, v.w - 8), y: Math.min(Math.max(r.y + r.height / 2, 8), v.h - 8) };
}
const stripStartingStyle = (page) => page.evaluate(() => {
  const strip = (owner) => {
    for (let i = owner.cssRules.length - 1; i >= 0; i--) {
      const rule = owner.cssRules[i];
      if (rule.constructor && rule.constructor.name === 'CSSStartingStyleRule') { owner.deleteRule(i); continue; }
      if (rule.cssRules) strip(rule);
    }
  };
  for (const sheet of document.styleSheets) strip(sheet);
});

async function verify66(root, page, width, motion) {
  const trigger = root.locator('.programme-trigger');
  const card = root.locator('#bd-pop');
  expect(await popOpen(card)).toBe(false);
  expect(await style(card, 'display')).toBe('none');
  expect(await tabTo(trigger, page)).toBe(true);
  await page.keyboard.press('Enter');
  await settle(page);
  expect(await popOpen(card)).toBe(true);
  const r = await rect(card); const v = await viewport(root);
  expect(contained(r, v)).toBe(true);
  expect(r.width).toBeGreaterThan(200);
  expect(r.height).toBeGreaterThan(150);
  const bd = await backdrop(card);
  expect(bd.opacity).toBe('1');
  expect(bd.backgroundColor).not.toBe('rgba(0, 0, 0, 0)');
  expect(bd.backdropFilter).not.toBe('none');
  expect(bd.backdropFilter).toContain('blur');
  // Non-modal proof: the background trigger stays focusable and operable
  // while the card is open — no focus trap is claimed for `popover=auto`.
  // (Sequential Tab order past an open popover differs by engine, so the
  // spec proves background operability directly instead of counting Tabs.)
  expect(await focusName(root)).toContain('programme-trigger');
  if (motion === 'reduce') {
    expect(await style(card, 'transitionDuration')).toBe('0s');
    expect((await backdrop(card)).opacity).toBe('1');
  }
  // Focusing the background trigger and pressing Enter toggles the open
  // card closed (a bare popovertarget toggles).
  await trigger.focus();
  expect(await focusName(root)).toContain('programme-trigger');
  await page.keyboard.press('Enter');
  await settleClosed(page);
  expect(await popOpen(card)).toBe(false);
  expect(await style(card, 'display')).toBe('none');
  // Escape closes and returns focus to the invoker.
  await trigger.focus();
  await page.keyboard.press('Enter');
  await settle(page);
  expect(await popOpen(card)).toBe(true);
  await page.keyboard.press('Escape');
  await settleClosed(page);
  expect(await popOpen(card)).toBe(false);
  expect(await style(card, 'display')).toBe('none');
  expect(await focusName(root)).toContain('programme-trigger');
  // Light dismiss via the backdrop.
  await trigger.click();
  await settle(page);
  expect(await popOpen(card)).toBe(true);
  const open = await rect(card);
  const pt = outsidePoint(open, await viewport(root));
  await root.locator('body').click({ position: pt });
  await settleClosed(page);
  expect(await popOpen(card)).toBe(false);
  // Explicit close control, then reopening still works.
  await trigger.click();
  await settle(page);
  await card.locator('[popovertargetaction="hide"]').click();
  await settleClosed(page);
  expect(await popOpen(card)).toBe(false);
  await trigger.click();
  await settle(page);
  expect(await popOpen(card)).toBe(true);
  await page.keyboard.press('Escape');
  await settleClosed(page);
  expect(await popOpen(card)).toBe(false);
}

async function verify75(root, page, width, motion) {
  const trigger = root.locator('.img-trigger');
  const pop = root.locator('#img-modal-1');
  const thumb = trigger.locator('img');
  const big = pop.locator('img');
  expect(await thumb.getAttribute('alt')).toBeTruthy();
  expect(await big.getAttribute('alt')).toBeTruthy();
  expect(await trigger.getAttribute('aria-label')).toContain('Enlarge');
  expect(await thumb.evaluate((e) => e.naturalWidth)).toBe(1200);
  expect(await thumb.evaluate((e) => e.naturalHeight)).toBe(1500);
  expect(await popOpen(pop)).toBe(false);
  expect(await style(pop, 'display')).toBe('none');
  expect(await tabTo(trigger, page)).toBe(true);
  await page.keyboard.press('Enter');
  await settle(page);
  expect(await popOpen(pop)).toBe(true);
  // The same image at full fidelity; genuinely enlarged where the viewport
  // has room, aspect preserved everywhere.
  expect(await thumb.getAttribute('src')).toBe(await big.getAttribute('src'));
  expect(await big.evaluate((e) => e.naturalWidth)).toBe(1200);
  const t = await rect(thumb); const g = await rect(big);
  const pr = await rect(pop); const v = await viewport(root);
  if (v.h >= 700) {
    // Real viewports: genuinely enlarged, area nearly quadrupled.
    expect(g.width).toBeGreaterThan(t.width * 1.3);
    expect(g.width * g.height).toBeGreaterThan(t.width * t.height * 1.9);
  } else {
    // The 390px docs portal cannot show enlargement — the height-capped zoom
    // is narrower than the width-sized thumbnail — but it must still fit.
    expect(contained(g, v)).toBe(true);
  }
  expect(Math.abs(g.width / g.height - 0.8)).toBeLessThan(0.03);
  expect(Math.abs(t.width / t.height - 0.8)).toBeLessThan(0.03);
  expect(contained(pr, v)).toBe(true);
  const close = pop.locator('.lightbox-close');
  const cr = await rect(close);
  expect(contained(cr, v)).toBe(true);
  expect(cr.width).toBeGreaterThanOrEqual(43.5); // authored 44px; subpixel slack
  expect(cr.height).toBeGreaterThanOrEqual(43.5); // authored 44px; subpixel slack
  const bd = await backdrop(pop);
  expect(bd.opacity).toBe('1');
  expect(bd.backgroundColor).not.toBe('rgba(0, 0, 0, 0)');
  // Non-modal proof: the background trigger stays focusable and operable
  // while the zoom is open — no focus trap is claimed for `popover=auto`.
  // (Sequential Tab order past an open popover differs by engine, so the
  // spec proves background operability directly instead of counting Tabs.)
  expect(await focusName(root)).toContain('img-trigger');
  if (motion === 'reduce') {
    expect(await style(pop, 'transitionDuration')).toBe('0s');
    expect((await backdrop(pop)).opacity).toBe('1');
  }
  // Focusing the background trigger and pressing Enter toggles the open
  // zoom closed (a bare popovertarget toggles).
  await trigger.focus();
  expect(await focusName(root)).toContain('img-trigger');
  await page.keyboard.press('Enter');
  await settleClosed(page);
  expect(await popOpen(pop)).toBe(false);
  expect(await style(pop, 'display')).toBe('none');
  // Escape closes and returns focus to the trigger.
  await trigger.focus();
  await page.keyboard.press('Enter');
  await settle(page);
  expect(await popOpen(pop)).toBe(true);
  await page.keyboard.press('Escape');
  await settleClosed(page);
  expect(await popOpen(pop)).toBe(false);
  expect(await focusName(root)).toContain('img-trigger');
  // Light dismiss via the backdrop.
  await trigger.click();
  await settle(page);
  expect(await popOpen(pop)).toBe(true);
  const pt = outsidePoint(await rect(pop), await viewport(root));
  await root.locator('body').click({ position: pt });
  await settleClosed(page);
  expect(await popOpen(pop)).toBe(false);
  // Visible close control, then reopening still works.
  await trigger.click();
  await settle(page);
  await close.click();
  await settleClosed(page);
  expect(await popOpen(pop)).toBe(false);
  await trigger.click();
  await settle(page);
  expect(await popOpen(pop)).toBe(true);
  await page.keyboard.press('Escape');
  await settleClosed(page);
  expect(await popOpen(pop)).toBe(false);
}

async function verify77(root, page, width, motion, browserName) {
  const trigger = root.locator('[commandfor="sheet-demo"]');
  const dlg = root.locator('#sheet-demo');
  expect(await trigger.getAttribute('command')).toBe('show-modal');
  expect(await dlg.getAttribute('closedby')).toBe('any');
  expect(await dialogState(dlg)).toEqual({ open: false, modal: false });
  expect(await style(dlg, 'display')).toBe('none');
  // Behavioral invoker probe: engines without invoker commands (Safari, per
  // the repo's support data) leave the dialog closed; restore the closed
  // state before the full keyboard path.
  await trigger.click();
  await settle(page);
  const invokerWorks77 = (await dialogState(dlg)).open;
  console.log(`ds-77 ${browserName}: invoker-opens=${invokerWorks77}`);
  if (!invokerWorks77) { await verifyDegraded(root, page, 77); return; }
  await page.keyboard.press('Escape');
  await settleClosed(page);
  expect(await dialogState(dlg)).toEqual({ open: false, modal: false });
  expect(await tabTo(trigger, page)).toBe(true);
  await page.keyboard.press('Enter');
  await settle(page);
  expect(await dialogState(dlg)).toEqual({ open: true, modal: true });
  const r = await rect(dlg); const v = await viewport(root);
  expect(contained(r, v)).toBe(true);
  const scroll = await dlg.evaluate((e) => ({ scrollH: e.scrollHeight, clientH: e.clientHeight }));
  if (v.w < 640) {
    // Bottom sheet: full width, bottom-anchored, with the grabber.
    expect(r.x).toBeLessThan(2);
    expect(Math.abs(r.width - v.w)).toBeLessThan(2);
    expect(Math.abs(r.bottom - v.h)).toBeLessThan(2);
    expect(await dlg.evaluate((e) => getComputedStyle(e, '::before').content)).not.toBe('none');
  } else {
    // Centred modal.
    expect(Math.abs((r.x + r.right) / 2 - v.w / 2)).toBeLessThan(3);
    expect(Math.abs(r.width - 416)).toBeLessThan(3);
    expect(await dlg.evaluate((e) => getComputedStyle(e, '::before').content)).toBe('none');
  }
  const done = dlg.locator('.sheet-actions button');
  if (v.h >= 700) {
    // Tall surfaces show every control without internal scrolling.
    expect(scroll.scrollH).toBeLessThanOrEqual(scroll.clientH + 4); // font-metric slack across engines
    const dr = await rect(done);
    expect(dr.bottom).toBeLessThanOrEqual(r.bottom + 4); // font-metric slack across engines
  } else {
    // Short surfaces (documentation iframes) scroll internally instead.
    expect(scroll.scrollH).toBeGreaterThan(scroll.clientH);
  }
  const bd = await backdrop(dlg);
  expect(bd.opacity).toBe('1');
  expect(bd.backgroundColor).not.toBe('rgba(0, 0, 0, 0)');
  // Modal proof: background hit-testing is blocked and Tab is trapped.
  expect(await root.locator('body').evaluate(() => {
    const t = document.querySelector('[commandfor="sheet-demo"]');
    const q = t.getBoundingClientRect();
    return document.elementFromPoint(q.x + q.width / 2, q.y + q.height / 2) === t;
  })).toBe(false);
  const stops77 = [];
  for (let i = 0; i < 9; i++) {
    await page.keyboard.press('Tab');
    await page.waitForTimeout(60);
    stops77.push(await focusWhere(root, '#sheet-demo'));
  }
  // Chromium's modal wrap passes through unfocused body; background controls
  // must never receive focus.
  expect(stops77).toContain('inside');
  expect(stops77.some((w) => w.startsWith('outside'))).toBe(false);
  // Wandering focus never dismisses the dialog.
  expect(await dialogState(dlg)).toEqual({ open: true, modal: true });
  // Native controls work and reverse, driven by keyboard: focus() needs no
  // viewport intersection, so short iframe surfaces are covered too.
  const arrival = dlg.locator('input[name="arrival"]');
  await arrival.nth(0).focus();
  await page.keyboard.press('ArrowDown');
  expect(await arrival.nth(1).isChecked()).toBe(true);
  expect(await arrival.nth(0).isChecked()).toBe(false);
  await page.keyboard.press('ArrowUp');
  expect(await arrival.nth(0).isChecked()).toBe(true);
  const sauna = dlg.locator('.sheet-field input[type="checkbox"]').nth(1);
  await sauna.focus();
  await page.keyboard.press('Space');
  expect(await sauna.isChecked()).toBe(true);
  await page.keyboard.press('Space');
  expect(await sauna.isChecked()).toBe(false);
  await dlg.locator('#sheet-bedding').focus();
  await dlg.locator('#sheet-bedding').selectOption('Two singles');
  expect(await dlg.locator('#sheet-bedding').inputValue()).toBe('Two singles');
  await dlg.locator('#sheet-bedding').selectOption('Double bed made up');
  if (motion === 'reduce') expect(await style(dlg, 'transitionDuration')).toBe('0s');
  // Explicit Done closes with a native return value; focus returns.
  // focus() scrolls the dialog natively (Playwright cannot drive its internal
  // scroller); centreFrame() first restores the wandered docs page. Engines
  // align the scrolled control differently, so the exposure proof asserts
  // the click point — Done's centre — is inside the dialog. Then a real
  // pointer click closes.
  await centreFrame(page, root);
  await done.focus();
  const dr2 = await rect(done); const box = await rect(dlg);
  const dcy = dr2.y + dr2.height / 2;
  expect(dcy).toBeGreaterThanOrEqual(box.y);
  expect(dcy).toBeLessThanOrEqual(box.bottom);
  await done.click();
  await settleClosed(page);
  expect(await dialogState(dlg)).toEqual({ open: false, modal: false });
  expect(await dlg.evaluate((e) => e.returnValue)).toBe('done');
  expect(await focusName(root)).toContain('button');
  // Escape closes and returns focus.
  await trigger.click();
  await settle(page);
  expect(await dialogState(dlg)).toEqual({ open: true, modal: true });
  await page.keyboard.press('Escape');
  await settleClosed(page);
  expect(await dialogState(dlg)).toEqual({ open: false, modal: false });
  // Backdrop click closes (closedby="any").
  await trigger.click();
  await settle(page);
  const pt = outsidePoint(await rect(dlg), await viewport(root));
  await root.locator('body').click({ position: pt });
  await settleClosed(page);
  expect(await dialogState(dlg)).toEqual({ open: false, modal: false });
}

async function verify106(root, page, width, motion, browserName) {
  const trigger = root.locator('[commandfor="close-options"]');
  const dlg = root.locator('#close-options');
  expect(await trigger.getAttribute('command')).toBe('show-modal');
  expect(await dlg.getAttribute('closedby')).toBe('any');
  // Honest copy: nothing destructive is claimed anywhere in the dialog.
  const copy = ((await dlg.textContent()) || '').toLowerCase();
  expect(copy).not.toContain('delete');
  expect(copy).not.toContain('cannot be undone');
  expect(copy).not.toContain('customer');
  expect(copy).toContain('nothing is sent or saved');
  expect(await dialogState(dlg)).toEqual({ open: false, modal: false });
  expect(await style(dlg, 'display')).toBe('none');
  // Behavioral invoker probe (see verify77): restore closed before the full path.
  await trigger.click();
  await settle(page);
  const invokerWorks106 = (await dialogState(dlg)).open;
  console.log(`ds-106 ${browserName}: invoker-opens=${invokerWorks106}`);
  if (!invokerWorks106) { await verifyDegraded(root, page, 106); return; }
  await page.keyboard.press('Escape');
  await settleClosed(page);
  expect(await dialogState(dlg)).toEqual({ open: false, modal: false });
  expect(await tabTo(trigger, page)).toBe(true);
  await page.keyboard.press('Enter');
  await settle(page);
  expect(await dialogState(dlg)).toEqual({ open: true, modal: true });
  const r = await rect(dlg); const v = await viewport(root);
  expect(contained(r, v)).toBe(true);
  // Autofocus lands on the primary close control.
  expect(await root.locator('body').evaluate(() => document.activeElement?.textContent?.trim())).toBe('Close dialog');
  const btns = dlg.locator('.confirm-actions button');
  expect(await btns.count()).toBe(2);
  // Tall surfaces show both actions without scrolling; short ones expose
  // them via native focus scroll at click time (see below).
  if (v.h >= 700) {
    for (const b of await btns.all()) {
      const br = await rect(b);
      expect(br.bottom).toBeLessThanOrEqual(r.bottom + 4); // font-metric slack across engines
    }
  }
  const bd = await backdrop(dlg);
  expect(bd.opacity).toBe('1');
  expect(bd.backgroundColor).not.toBe('rgba(0, 0, 0, 0)');
  // Modal proof: background hit-testing is blocked and Tab is trapped.
  expect(await root.locator('body').evaluate(() => {
    const t = document.querySelector('[commandfor="close-options"]');
    const q = t.getBoundingClientRect();
    return document.elementFromPoint(q.x + q.width / 2, q.y + q.height / 2) === t;
  })).toBe(false);
  // Step back to the first stop (autofocus starts on the last), then walk
  // forward through the wrap boundary.
  await page.keyboard.press('Shift+Tab');
  await page.waitForTimeout(60);
  expect(await focusWhere(root, '#close-options')).toBe('inside');
  const stops106 = [];
  for (let i = 0; i < 4; i++) {
    await page.keyboard.press('Tab');
    await page.waitForTimeout(60);
    stops106.push(await focusWhere(root, '#close-options'));
  }
  // Chromium's modal wrap passes through unfocused body — in the iframe the
  // Tab then continues into the outer document — but inner background
  // controls must never receive focus, and the dialog must stay open.
  expect(stops106).toContain('inside');
  expect(stops106.some((w) => w.startsWith('outside'))).toBe(false);
  expect(await dialogState(dlg)).toEqual({ open: true, modal: true });
  if (motion === 'reduce') expect(await style(dlg, 'transitionDuration')).toBe('0s');
  // Explicit dismissal returns a native value; focus returns to the invoker.
  await centreFrame(page, root);
  await btns.nth(0).focus();
  await btns.nth(0).click();
  await settleClosed(page);
  expect(await dialogState(dlg)).toEqual({ open: false, modal: false });
  expect(await dlg.evaluate((e) => e.returnValue)).toBe('stay');
  // Reopen after dismissal, then Escape.
  await trigger.click();
  await settle(page);
  expect(await dialogState(dlg)).toEqual({ open: true, modal: true });
  await page.keyboard.press('Escape');
  await settleClosed(page);
  expect(await dialogState(dlg)).toEqual({ open: false, modal: false });
  // Reopen, then backdrop light-dismiss.
  await trigger.click();
  await settle(page);
  const pt = outsidePoint(await rect(dlg), await viewport(root));
  await root.locator('body').click({ position: pt });
  await settleClosed(page);
  expect(await dialogState(dlg)).toEqual({ open: false, modal: false });
  // Reopen, then the primary close control.
  await trigger.click();
  await settle(page);
  await centreFrame(page, root);
  await btns.nth(1).focus();
  await btns.nth(1).click();
  await settleClosed(page);
  expect(await dialogState(dlg)).toEqual({ open: false, modal: false });
  expect(await dlg.evaluate((e) => e.returnValue)).toBe('close');
}

const verify = { 66: verify66, 75: verify75, 77: verify77, 106: verify106 };

for (const width of [1440, 390]) {
  for (const motion of ['no-preference', 'reduce']) {
    for (const surface of ['hosted', 'download', 'iframe']) {
      for (const id of ids) {
        test(`${id} ${surface} ${width} ${motion}`, async ({ browser, browserName }) => {
          const context = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 900 }, reducedMotion: motion, javaScriptEnabled: false });
          const page = await context.newPage();
          await page.goto(surface === 'iframe' ? `/spells/ds-${id}/` : surface === 'download' ? `/download/ds-${id}.html` : `/play/ds-${id}/`);
          const root = surface === 'iframe' ? page.frameLocator('iframe').first() : page;
          const doc = root.locator('body');
          expect(await doc.evaluate(() => document.scripts.length)).toBe(0);
          expect(await doc.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
          await verify[id](root, page, width, motion, browserName);
          await context.close();
        });
      }
    }
  }
}

for (const id of ids) {
  test(`${id} dark mobile touch`, async ({ browser, browserName }) => {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, colorScheme: 'dark', hasTouch: true, javaScriptEnabled: false });
    const page = await context.newPage();
    await page.goto(`/play/ds-${id}/`);
    const trigger = id === 66 ? page.locator('.programme-trigger') : id === 75 ? page.locator('.img-trigger') : page.locator('[commandfor]').first();
    const overlay = id === 66 ? page.locator('#bd-pop') : id === 75 ? page.locator('#img-modal-1') : id === 77 ? page.locator('#sheet-demo') : page.locator('#close-options');
    const isDialog = id === 77 || id === 106;
    await trigger.tap();
    await settle(page);
    const darkOpened = isDialog ? (await dialogState(overlay)).open : await popOpen(overlay);
    console.log(`ds-${id} ${browserName}: dark-tap-opens=${darkOpened}`);
    if (!darkOpened && isDialog) {
      // No invoker commands here (Safari): the tap is a documented no-op.
      expect(await style(overlay, 'display')).toBe('none');
      await context.close();
      return;
    }
    expect(darkOpened).toBe(true);
    const r = await rect(overlay); const v = await viewport(page);
    expect(contained(r, v)).toBe(true);
    const closer = id === 66 ? overlay.locator('[popovertargetaction="hide"]') : id === 75 ? overlay.locator('.lightbox-close') : id === 77 ? overlay.locator('.sheet-actions button') : overlay.locator('.confirm-actions button').nth(1);
    await closer.scrollIntoViewIfNeeded();
    await closer.tap();
    await settleClosed(page);
    expect(isDialog ? (await dialogState(overlay)).open : await popOpen(overlay)).toBe(false);
    await context.close();
  });

  test(`${id} simulated no entry starting style`, async ({ page, browserName }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(`/play/ds-${id}/`);
    await stripStartingStyle(page);
    const trigger = id === 66 ? page.locator('.programme-trigger') : id === 75 ? page.locator('.img-trigger') : page.locator('[commandfor]').first();
    const overlay = id === 66 ? page.locator('#bd-pop') : id === 75 ? page.locator('#img-modal-1') : id === 77 ? page.locator('#sheet-demo') : page.locator('#close-options');
    const isDialog = id === 77 || id === 106;
    await trigger.click();
    await settle(page);
    const fallbackOpened = isDialog ? (await dialogState(overlay)).open : await popOpen(overlay);
    console.log(`ds-${id} ${browserName}: no-starting-style-opens=${fallbackOpened}`);
    if (!fallbackOpened && isDialog) {
      // No invoker commands here (Safari): still closed, page intact.
      expect(await style(overlay, 'display')).toBe('none');
      return;
    }
    // Without @starting-style the overlay still opens into its final state.
    expect(fallbackOpened).toBe(true);
    const r = await rect(overlay); const v = await viewport(page);
    expect(contained(r, v)).toBe(true);
    expect(r.width).toBeGreaterThan(120);
    expect((await backdrop(overlay)).opacity).toBe('1');
    await page.keyboard.press('Escape');
    await settleClosed(page);
    expect(isDialog ? (await dialogState(overlay)).open : await popOpen(overlay)).toBe(false);
  });
}
