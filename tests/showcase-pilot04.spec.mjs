import { test, expect } from '@playwright/test';

/**
 * Pilot 04 — native overlay spells ds-79, ds-89, ds-142.
 *
 * Every assertion reads live browser state with client scripts disabled:
 * real `:popover-open`, real geometry, real focus movement, real fragment
 * navigation. CSS.supports strings are never used as a success criterion; the
 * unsupported-anchor cases delete the actual @supports rules and re-measure.
 */

const ids = [79, 89, 142];
const rect = (loc) => loc.evaluate((e) => { const r = e.getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height, right: r.right, bottom: r.bottom }; });
const viewport = (root) => root.locator('body').evaluate(() => ({ w: innerWidth, h: innerHeight }));
const style = (loc, p) => loc.evaluate((e, p) => getComputedStyle(e)[p], p);
const openState = (loc) => loc.evaluate((e) => e.matches(':popover-open'));
const settle = (p, ms = 260) => p.waitForTimeout(ms);
// Harness-side scroll rest: with client JS disabled the page runs no timers,
// so only synchronous evaluates and harness waits are safe.
async function restScroll(root) {
  // Poll the document that actually scrolls: the top page for hosted and
  // downloaded surfaces, the framed document for documentation iframes.
  const body = root.locator('body');
  const owner = body.page();
  let last = -1; let still = 0;
  for (let i = 0; i < 20; i++) {
    const y = await body.evaluate(() => scrollY);
    if (y === last) { still += 1; if (still >= 2) return y; } else { still = 0; last = y; }
    await owner.waitForTimeout(60);
  }
  return last;
}
const contained = (r, v) => r.x >= -1 && r.y >= -1 && r.right <= v.w + 1 && r.bottom <= v.h + 1;
const focusName = (root) => root.locator('body').evaluate(() => {
  const a = document.activeElement;
  if (!a || a === document.body) return 'BODY';
  return `${a.tagName.toLowerCase()}${a.className ? '.' + String(a.className).split(' ')[0] : ''}`;
});
async function tabTo(loc, page, max = 14) {
  for (let i = 0; i < max; i++) {
    if (await loc.evaluate((e) => e === document.activeElement)) return true;
    await page.keyboard.press('Tab');
    await page.waitForTimeout(60);
  }
  return loc.evaluate((e) => e === document.activeElement);
}
// Remove every @supports block probing anchor(), nested or not.
const stripAnchorSupport = (page) => page.evaluate(() => {
  const strip = (owner) => {
    for (let i = owner.cssRules.length - 1; i >= 0; i--) {
      const rule = owner.cssRules[i];
      if ((rule.conditionText || '').includes('anchor(')) { owner.deleteRule(i); continue; }
      if (rule.cssRules) strip(rule);
    }
  };
  for (const sheet of document.styleSheets) strip(sheet);
});

async function verify79(root, page, width, motion) {
  const trigger = root.locator('.mega-trigger');
  const panel = root.locator('#mega-1');
  // Closed popovers must not render or intercept anything.
  expect(await openState(panel)).toBe(false);
  expect(await style(panel, 'display')).toBe('none');
  expect(await tabTo(trigger, page)).toBe(true);
  await page.keyboard.press('Enter');
  await settle(page);
  expect(await openState(panel)).toBe(true);
  const p = await rect(panel); const t = await rect(trigger); const v = await viewport(root);
  expect(contained(p, v)).toBe(true);
  // The canonical policy serves a bottom sheet on narrow or short surfaces.
  const sheet = v.w < 700 || v.h <= 560;
  if (!sheet) {
    expect(Math.abs(p.x - t.x)).toBeLessThan(3);
    // Below the trigger, or flipped above it when the surface is short.
    expect(p.y >= t.bottom - 1 || p.bottom <= t.y + 1).toBe(true);
    expect(p.width).toBeGreaterThan(560);
  } else {
    expect(p.x).toBeLessThan(2);
    expect(Math.abs(p.bottom - v.h)).toBeLessThan(2);
    expect(Math.abs(p.width - v.w)).toBeLessThan(2);
  }
  // Focus stays on the invoker, then Tab reaches real items inside the panel.
  expect(await focusName(root)).toContain('mega-trigger');
  await page.keyboard.press('Tab');
  expect(await panel.evaluate((e) => e.contains(document.activeElement))).toBe(true);
  // Every destination is a fragment that exists in this document.
  const links = await panel.evaluate((e) => [...e.querySelectorAll('a')].map((a) => a.getAttribute('href')));
  expect(links.length).toBeGreaterThanOrEqual(6);
  for (const href of links) {
    expect(href.startsWith('#')).toBe(true);
    expect(await root.locator('body').evaluate((e, h) => !!document.querySelector(h), href)).toBe(true);
  }
  if (motion === 'reduce') expect(await style(panel, 'transitionDuration')).toBe('0s');
  // Escape closes and returns focus to the invoker (clean flow, no navigation).
  await page.keyboard.press('Escape');
  await settle(page, 150);
  expect(await openState(panel)).toBe(false);
  expect(await focusName(root)).toContain('mega-trigger');
  // Light dismiss.
  await trigger.click();
  await settle(page);
  expect(await openState(panel)).toBe(true);
  await root.locator('body').click({ position: { x: 4, y: 4 } });
  await settle(page, 150);
  expect(await openState(panel)).toBe(false);
  // Follow the last destination (page foot): real fragment navigation. The
  // native popover stays open — on wide screens it travels off-screen with its
  // trigger, on narrow screens the sheet remains until dismissed.
  await trigger.click();
  await settle(page);
  // Activate the destination from the keyboard: real navigation without
  // pointer-stability races inside short documentation iframes.
  await panel.locator('a').last().focus();
  await page.keyboard.press('Enter');
  await settle(page, 200);
  await restScroll(root);
  expect(await root.locator('body').evaluate(() => location.hash)).toBe(links[links.length - 1]);
  const target = await rect(root.locator(links[links.length - 1]));
  expect(target.y).toBeGreaterThanOrEqual(-1);
  expect(target.y).toBeLessThan(v.h);
  // Zero-JS boundary: a native popover does not auto-close on navigation, and
  // Chromium keeps the anchored panel at its viewport position while the page
  // scrolls. One outside click (light dismiss) clears it and reveals the target.
  expect(await openState(panel)).toBe(true);
  // Escape (not an outside click here: clicking would scroll the document back
  // to the click point and mask the navigation geometry we just asserted).
  await page.keyboard.press('Escape');
  await settle(page, 150);
  expect(await openState(panel)).toBe(false);
  const revealed = await rect(root.locator(links[links.length - 1]));
  expect(revealed.y).toBeGreaterThanOrEqual(-1);
  expect(revealed.y).toBeLessThan(v.h);
  await root.locator('body').evaluate(() => scrollTo(0, 0));
  await restScroll(root);
}

async function verify89(root, page, width, motion) {
  // Honest semantics: no application-menu roles the zero-JS demo cannot fulfil.
  expect(await root.locator('[role="menu"], [role="menuitem"], [aria-haspopup]').count()).toBe(0);
  // Destination identity: every row's menu points at that row's own record and
  // history sections — a valid fragment belonging to another row is a misroute.
  const rows = root.locator('.doc-row');
  expect(await rows.count()).toBe(4);
  const subjects = [];
  for (let i = 0; i < 4; i++) {
    const r = rows.nth(i);
    const title = (await r.locator('h2').innerText()).replace('★', '').trim();
    const links = r.locator('.ctx-menu a');
    expect(await links.count()).toBe(2);
    const recHref = await links.nth(0).getAttribute('href');
    const histHref = await links.nth(1).getAttribute('href');
    const rec = root.locator(recHref);
    const hist = root.locator(histHref);
    expect((await rec.locator('h2').innerText()).trim()).toBe(title);
    const recSubject = (await rec.locator('.scene-kicker').innerText()).split('/')[1].trim().toLowerCase();
    const histKind = (await hist.locator('.scene-kicker').innerText()).split('/')[0].trim().toLowerCase();
    const histSubject = (await hist.locator('.scene-kicker').innerText()).split('/')[1].trim().toLowerCase();
    expect((await rec.locator('.scene-kicker').innerText()).split('/')[0].trim().toLowerCase()).toBe('record');
    expect(histKind).toBe('history');
    expect(histSubject).toBe(recSubject);
    expect(subjects).not.toContain(recSubject);
    subjects.push(recSubject);
  }
  const row = root.locator('.doc-row').first();
  const btn = row.locator('.ctx-btn');
  const menu = root.locator('#ctx-menu');
  expect(await openState(menu)).toBe(false);
  expect(await style(menu, 'display')).toBe('none');
  expect(await tabTo(btn, page)).toBe(true);
  await page.keyboard.press('Enter');
  await settle(page);
  expect(await openState(menu)).toBe(true);
  const m = await rect(menu); const t = await rect(btn); const v = await viewport(root);
  expect(contained(m, v)).toBe(true);
  const sheet = v.w < 700 || v.h <= 560;
  if (!sheet) {
    expect(Math.abs(m.right - t.right)).toBeLessThan(3);
    expect(m.y >= t.bottom - 1 || m.bottom <= t.y + 1).toBe(true);
  } else {
    expect(m.x).toBeLessThan(2);
    expect(Math.abs(m.bottom - v.h)).toBeLessThan(2);
    expect(Math.abs(m.width - v.w)).toBeLessThan(2);
  }
  if (motion === 'reduce') expect(await style(menu, 'transitionDuration')).toBe('0s');
  // Escape closes and returns focus to the invoker (clean flow, no navigation).
  await page.keyboard.press('Escape');
  await settle(page, 150);
  expect(await openState(menu)).toBe(false);
  expect(await focusName(root)).toContain('ctx-btn');
  await btn.click();
  await settle(page);
  expect(await openState(menu)).toBe(true);
  // The checkbox is a real native state change the owning row reflects.
  const check = menu.locator('input[type="checkbox"]');
  expect(await style(row.locator('.star-flag'), 'display')).toBe('none');
  await check.check();
  expect(await check.isChecked()).toBe(true);
  expect(await style(row.locator('.star-flag'), 'display')).toBe('inline');
  await check.uncheck();
  expect(await style(row.locator('.star-flag'), 'display')).toBe('none');
  // Menu links are real local destinations.
  const hrefs = await menu.evaluate((e) => [...e.querySelectorAll('a')].map((a) => a.getAttribute('href')));
  expect(hrefs.length).toBe(2);
  for (const href of hrefs) expect(await root.locator('body').evaluate((e, h) => !!document.querySelector(h), href)).toBe(true);
  await menu.locator('a').first().focus();
  await page.keyboard.press('Enter');
  await settle(page, 200);
  await restScroll(root);
  expect(await root.locator('body').evaluate(() => location.hash)).toBe(hrefs[0]);
  const dest = await rect(root.locator(hrefs[0]));
  expect(dest.y).toBeGreaterThanOrEqual(-1);
  expect(dest.y).toBeLessThan(v.h);
  await root.locator('body').evaluate(() => scrollTo(0, 0));
  await restScroll(root);
  // The popover survives fragment navigation; dismiss explicitly.
  expect(await openState(menu)).toBe(true);
  await root.locator('body').click({ position: { x: 4, y: 4 } });
  await settle(page, 150);
  expect(await openState(menu)).toBe(false);
  // A trigger near the document end flips the anchored menu above itself.
  if (!sheet) {
    const lastBtn = root.locator('.pt-foot .ctx-btn');
    await lastBtn.evaluate((e) => e.scrollIntoView({ block: 'end' }));
    await restScroll(root);
    await lastBtn.click();
    await settle(page);
    const lm = await rect(root.locator('#ctx-menu-4'));
    const lt = await rect(lastBtn);
    expect(await openState(root.locator('#ctx-menu-4'))).toBe(true);
    expect(contained(lm, await viewport(root))).toBe(true);
    expect(lm.bottom).toBeLessThanOrEqual(lt.y + 1);
    await page.keyboard.press('Escape');
    await settle(page, 150);
  }
}

async function verify142(root, page, width, motion) {
  const pins = root.locator('.map-pin');
  expect(await pins.count()).toBe(4);
  expect(await root.locator('.map-key li').count()).toBe(4);
  for (const pop of await root.locator('[popover]').all()) {
    expect(await openState(pop)).toBe(false);
    expect(await style(pop, 'display')).toBe('none');
  }
  for (let i = 0; i < 4; i++) {
    const pin = pins.nth(i);
    const pop = root.locator(`#pop-pin-${i + 1}`);
    expect(await tabTo(pin, page)).toBe(true);
    await page.keyboard.press('Enter');
    await settle(page);
    expect(await openState(pop)).toBe(true);
    for (let j = 0; j < 4; j++) if (j !== i) expect(await openState(root.locator(`#pop-pin-${j + 1}`))).toBe(false);
    const pr = await rect(pop); const tr = await rect(pin); const v = await viewport(root);
    expect(contained(pr, v)).toBe(true);
    const above = pr.bottom <= tr.y + 1;
    const below = pr.y >= tr.bottom - 1;
    expect(above || below).toBe(true);
    if (width === 1440) expect(Math.abs((pr.x + pr.right) / 2 - (tr.x + tr.right) / 2)).toBeLessThan(4);
    // The popover holds a working link and a native close control.
    expect(await pop.locator('a').count()).toBe(1);
    expect(await root.locator('body').evaluate((e, n) => !!document.querySelector(n), `#note-${i + 1}`)).toBe(true);
    if (i === 0) {
      if (motion === 'reduce') expect(await style(pop, 'transitionDuration')).toBe('0s');
      await pop.locator('a').focus();
      await page.keyboard.press('Enter');
      await settle(page, 200);
      await restScroll(root);
      expect(await root.locator('body').evaluate(() => location.hash)).toBe('#note-1');
      // Centre the persisted popover in the scrolling document: the docs
      // iframe only shows ~390px, so a scroll-0 reset can leave the close
      // control outside the clip where no click can reach it. Top-layer
      // elements ignore scrollIntoView, so compute the offset manually.
      await root.locator('body').evaluate((e, sel) => {
        const r = document.querySelector(sel).getBoundingClientRect();
        scrollTo(0, scrollY + r.top + r.height / 2 - innerHeight / 2);
      }, '#pop-pin-1 .pin-close');
      await restScroll(root);
      // Native popovers persist across fragment navigation; close explicitly.
      expect(await openState(pop)).toBe(true);
    }
    // Explicit close control, then Escape with focus return to the pin.
    await pop.locator('.pin-close').click();
    await settle(page, 150);
    expect(await openState(pop)).toBe(false);
    await pin.click();
    await settle(page);
    expect(await openState(pop)).toBe(true);
    await page.keyboard.press('Escape');
    await settle(page, 150);
    expect(await openState(pop)).toBe(false);
    expect(await focusName(root)).toContain('map-pin');
  }
  // The numbered key is a set of real local links, keyboard-activatable.
  const keyLinks = root.locator('.map-key a');
  expect(await keyLinks.count()).toBe(4);
  for (let i = 0; i < 4; i++) {
    expect(await keyLinks.nth(i).getAttribute('href')).toBe(`#note-${i + 1}`);
  }
  const keyLink = keyLinks.nth(2);
  expect(await tabTo(keyLink, page, 20)).toBe(true);
  await page.keyboard.press('Enter');
  await settle(page, 200);
  await restScroll(root);
  expect(await root.locator('body').evaluate(() => location.hash)).toBe('#note-3');
  const noteRect = await rect(root.locator('#note-3'));
  const keyV = await viewport(root);
  expect(noteRect.y).toBeGreaterThanOrEqual(-1);
  expect(noteRect.y).toBeLessThan(keyV.h);
  await root.locator('body').evaluate(() => scrollTo(0, 0));
  await restScroll(root);
  // Light dismiss on the first pin.
  await pins.first().click();
  await settle(page);
  await root.locator('body').click({ position: { x: 4, y: 4 } });
  await settle(page, 150);
  expect(await openState(root.locator('#pop-pin-1'))).toBe(false);
}

const verify = { 79: verify79, 89: verify89, 142: verify142 };

for (const width of [1440, 390]) {
  for (const motion of ['no-preference', 'reduce']) {
    for (const surface of ['hosted', 'download', 'iframe']) {
      for (const id of ids) {
        test(`${id} ${surface} ${width} ${motion}`, async ({ browser }) => {
          const context = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 900 }, reducedMotion: motion, javaScriptEnabled: false });
          const page = await context.newPage();
          await page.goto(surface === 'iframe' ? `/spells/ds-${id}/` : surface === 'download' ? `/download/ds-${id}.html` : `/play/ds-${id}/`);
          const root = surface === 'iframe' ? page.frameLocator('iframe').first() : page;
          const doc = root.locator('body');
          expect(await doc.evaluate(() => document.scripts.length)).toBe(0);
          expect(await doc.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
          await verify[id](root, page, width, motion);
          await context.close();
        });
      }
    }
  }
}

for (const id of ids) {
  test(`${id} dark mobile touch`, async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, colorScheme: 'dark', hasTouch: true, javaScriptEnabled: false });
    const page = await context.newPage();
    await page.goto(`/play/ds-${id}/`);
    const trigger = id === 79 ? page.locator('.mega-trigger') : id === 89 ? page.locator('.ctx-btn').first() : page.locator('.map-pin').first();
    const pop = id === 79 ? page.locator('#mega-1') : id === 89 ? page.locator('#ctx-menu') : page.locator('#pop-pin-1');
    await trigger.tap();
    await settle(page);
    expect(await openState(pop)).toBe(true);
    const r = await rect(pop); const v = await viewport(page);
    expect(contained(r, v)).toBe(true);
    await page.keyboard.press('Escape');
    await settle(page, 150);
    expect(await openState(pop)).toBe(false);
    await context.close();
  });

  test(`${id} simulated no anchor positioning`, async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(`/play/ds-${id}/`);
    await stripAnchorSupport(page);
    const trigger = id === 79 ? page.locator('.mega-trigger') : id === 89 ? page.locator('.ctx-btn').first() : page.locator('.map-pin').first();
    const pop = id === 79 ? page.locator('#mega-1') : id === 89 ? page.locator('#ctx-menu') : page.locator('#pop-pin-1');
    await trigger.click();
    await settle(page);
    expect(await openState(pop)).toBe(true);
    const r = await rect(pop); const v = await viewport(page);
    expect(contained(r, v)).toBe(true);
    expect(r.width).toBeGreaterThan(120);
    // Without anchor positioning the native overlay stays centred, not pinned.
    expect(Math.abs((r.x + r.right) / 2 - v.w / 2)).toBeLessThan(60);
    expect(Math.abs((r.y + r.bottom) / 2 - v.h / 2)).toBeLessThan(90);
    await page.keyboard.press('Escape');
    await settle(page, 150);
    expect(await openState(pop)).toBe(false);
  });
}
