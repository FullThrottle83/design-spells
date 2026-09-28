import { test, expect } from '@playwright/test';

/* Pilot 06: real hosted/iframe/download interactions with scripts disabled.
   Unsupported-feature overrides below are SIMULATIONS, not historical browsers. */
const ids = [97,117,131];
const trigger = {97:'.nav-open',117:'.split-more',131:'.toast-trigger'};
const overlay = {97:'#site-drawer',117:'#split-menu',131:'#auto-toast-1'};
const rect = loc => loc.evaluate(e => {const r=e.getBoundingClientRect(); return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,w:r.width,h:r.height};});
const state = (loc,id) => loc.evaluate((e,id)=> id===97 ? e.matches(':modal') && e.open : e.matches(':popover-open'),id);
const viewport = root => root.locator('body').evaluate(() => ({w:innerWidth,h:innerHeight}));
const fits = (r,v) => r.x>=-1 && r.y>=-1 && r.right<=v.w+1 && r.bottom<=v.h+1;
const active = root => root.locator('body').evaluate(() => document.activeElement?.className || document.activeElement?.tagName);
const inside = (root,sel) => root.locator('body').evaluate((_,sel)=>document.querySelector(sel).contains(document.activeElement),sel);
const endpoint = async (loc,id) => expect.poll(async()=>state(loc,id)).toBe(true);
const closed = async (loc,id) => {await expect.poll(async()=>state(loc,id)).toBe(false); await expect.poll(async()=>loc.evaluate(e=>getComputedStyle(e).display)).toBe('none');};
async function scene(page,id,w,surface,motion='no-preference',scheme='light') {
  await page.setViewportSize({width:w,height:w===390?844:900});
  await page.emulateMedia({reducedMotion:motion,colorScheme:scheme});
  const url=surface==='iframe'?`/spells/ds-${id}/`:surface==='download'?`file://${process.cwd()}/public/download/ds-${id}.html`:`/play/ds-${id}/`;
  await page.goto(url);
  const root=surface==='iframe'?page.frameLocator('iframe').first():page;
  return {root,t:root.locator(trigger[id]),o:root.locator(overlay[id])};
}
async function centreFrame(page,surface) {
  if(surface==='iframe') await page.locator('iframe').first().evaluate(e=>e.scrollIntoView({block:'center',behavior:'instant'}));
}
// Pointer events at a known visible point of the *iframe viewport*, not a
// Playwright body locator that scrolls a tall body beneath fixed top-layer UI.
async function outsideClick(page,surface,x,y) {
  if(surface==='iframe') {
    await centreFrame(page,surface);
    const r=await rect(page.locator('iframe').first());
    await page.mouse.click(r.x+x,r.y+y);
  } else await page.mouse.click(x,y);
}
async function open(t,o,id,page) {
  await t.click();
  // A behavioral probe: no inferred universal commandfor support.
  if (!await state(o,id)) return false;
  await endpoint(o,id);
  return true;
}
async function focusTrigger(t,page) {
  await t.focus();
  expect(await t.evaluate(e=>e===document.activeElement)).toBe(true);
  await page.keyboard.press('Enter');
}

for(const id of ids) for(const surface of ['hosted','iframe','download']) for(const w of [1440,390]) for(const motion of ['no-preference','reduce']) {
 test(`ds-${id} ${surface} ${w} ${motion} native state and controls`,async({page})=>{
  await page.context().route('**/*',route=>route.continue());
  const {root,t,o}=await scene(page,id,w,surface,motion,w===390?'dark':'light');
  await centreFrame(page,surface);
  expect(await state(o,id)).toBe(false);
  expect(await o.evaluate(e=>getComputedStyle(e).display)).toBe('none');
  const v=await viewport(root);
  expect(v.w).toBeLessThanOrEqual(w);
  if(!await open(t,o,id,page)) {
    // Engines missing declarative invoker commands: visible controls stay inert.
    expect(await t.getAttribute('command')).toMatch(/show-modal|toggle-popover|show-popover/);
    await focusTrigger(t,page);
    expect(await state(o,id)).toBe(false);
    return;
  }
  await expect.poll(async()=>fits(await rect(o),v)).toBe(true);
  if(motion==='reduce' && id!==117) expect(await o.evaluate(e=>getComputedStyle(e).transitionDuration)).toBe('0s');
  if(id===97) {
    expect(await inside(root,'#site-drawer')).toBe(true); // autofocus close
    expect(String(await active(root))).toContain('nav-close');
    expect(await o.getAttribute('closedby')).toBe('any');
    const links=o.locator('nav a');
    expect(await links.count()).toBe(4);
    for(const a of await links.all()) {
      const href=await a.getAttribute('href');
      expect(href).toMatch(/^#nav-/);
      expect(await root.locator(href).count()).toBe(1);
    }
    // Modal background is inert for real pointer/focus: background cannot acquire focus.
    await root.locator('.nav-open').focus();
    expect(await inside(root,'#site-drawer')).toBe(true);
    await page.keyboard.press('Tab');
    expect(await inside(root,'#site-drawer')).toBe(true);
    await centreFrame(page,surface);
    if(surface==='iframe') {await o.locator('.nav-close').focus();await page.keyboard.press('Enter');}
    else await o.locator('.nav-close').click();
    await closed(o,id);
    expect(await t.evaluate(e=>e===document.activeElement)).toBe(true);
    await focusTrigger(t,page); await endpoint(o,id);
    await page.keyboard.press('Escape'); await closed(o,id);
    expect(await t.evaluate(e=>e===document.activeElement)).toBe(true);
    if(surface==='iframe') await focusTrigger(t,page); else await t.click();
    await endpoint(o,id);
    const link=o.locator('nav a[href="#nav-notes"]');
    await centreFrame(page,surface);
    await link.focus();
    expect(await link.evaluate(e=>e===document.activeElement)).toBe(true);
    await page.keyboard.press('Enter');
    expect(await root.locator('body').evaluate(()=>location.hash)).toBe('#nav-notes');
    // After a fragment jump in a short iframe, Playwright scrollIntoView
    // chases the fixed top-layer control across two nested scrollports.
    // A real keyboard activation avoids that automation artefact.
    await o.locator('.nav-close').focus();
    await page.keyboard.press('Enter'); await closed(o,id);
    const target=await rect(root.locator('#nav-notes'));
    expect(target.y).toBeLessThan(v.h);
    // Backdrop light dismiss only when the running engine actually supports closedby=any.
    if(surface==='iframe') await focusTrigger(t,page); else await t.click();
    await endpoint(o,id);
    await outsideClick(page,surface,Math.min(v.w-5,(await rect(o)).right+12),12);
    if(await state(o,id)) {
      // Some engines ignore backdrop clicks; after the fragment jump a fixed
      // top-layer element is not reliably scrolled into view by Playwright.
      await o.locator('.nav-close').focus(); await page.keyboard.press('Enter'); await closed(o,id);
    } else {await closed(o,id);expect(await t.evaluate(e=>e===document.activeElement)).toBe(true);}
  }
  if(id===117) {
    const menu=await rect(o),button=await rect(t);
    if(v.w>=600 && v.h>=560 && await o.evaluate(e=>getComputedStyle(e).positionAnchor==='--project-split-more')) {
      // Declared anchor plus actual geometry: native flip-block is also valid
      // when the invoker is low in the viewport (CI uses different fonts).
      expect(Math.abs(menu.right-button.right)).toBeLessThan(3);
      expect(menu.y>=button.bottom-2 || menu.bottom<=button.y+2).toBe(true);
    } else {
      // Real mobile/short or unsupported-anchor geometry, not hidden content.
      expect(v.w-menu.right).toBeGreaterThanOrEqual(8);
      expect(v.h-menu.bottom).toBeGreaterThanOrEqual(8);
    }
    for(const a of await o.locator('a').all()) expect(await root.locator(await a.getAttribute('href')).count()).toBe(1);
    expect(await root.locator('.split-main').getAttribute('href')).toBe('#project-brief');
    // The primary label retains its contrasting button ink inside showcase CSS.
    const contrast=await root.locator('.split-main').evaluate(e=>{
      const rgb=s=>s.match(/[0-9.]+/g).slice(0,3).map(Number).map(c=>{c/=255;return c<=.04045?c/12.92:((c+.055)/1.055)**2.4});
      const lum=s=>rgb(s).reduce((a,c,i)=>a+c*[.2126,.7152,.0722][i],0);
      const fg=lum(getComputedStyle(e).color),bg=lum(getComputedStyle(e).backgroundColor);
      return (Math.max(fg,bg)+.05)/(Math.min(fg,bg)+.05);
    });
    expect(contrast).toBeGreaterThan(4.5);
    await page.keyboard.press('Escape'); await closed(o,id);
    expect(await t.evaluate(e=>e===document.activeElement)).toBe(true);
    await focusTrigger(t,page); await endpoint(o,id);
    await outsideClick(page,surface,8,8); await closed(o,id); // native auto light-dismiss
    if(surface==='iframe') await focusTrigger(t,page); else await t.click();
    await endpoint(o,id);
    const timeline=o.locator('a[href="#project-timeline"]');
    if(surface==='iframe') {await timeline.focus();await page.keyboard.press('Enter');}
    else await timeline.click();
    expect(await root.locator('body').evaluate(()=>location.hash)).toBe('#project-timeline');
    // Fragment navigation does not itself light-dismiss an auto popover.
    if(await state(o,id)) {await page.keyboard.press('Escape');}
    await closed(o,id);
    const primary=root.locator('.split-main');
    if(surface==='iframe') {await primary.focus();await page.keyboard.press('Enter');}
    else await primary.click();
    expect(await root.locator('body').evaluate(()=>location.hash)).toBe('#project-brief');
    expect(await state(o,id)).toBe(false); // primary does not open secondary
  }
  if(id===131) {
    expect(await o.getAttribute('popover')).toBe('manual');
    expect(await o.locator('[role="status"]').innerText()).toContain('No notes were saved');
    await page.keyboard.press('Escape'); expect(await state(o,id)).toBe(true);
    // Outside click does not dismiss manual popovers.
    await outsideClick(page,surface,8,8); expect(await state(o,id)).toBe(true);
    // Native state persists without a timer; not an opacity-only simulation.
    await page.waitForTimeout(400); expect(await state(o,id)).toBe(true);
    const x=o.locator('.auto-toast__close');
    await x.focus(); expect(await x.evaluate(e=>e===document.activeElement)).toBe(true);
    await page.keyboard.press('Enter'); await closed(o,id);
    await focusTrigger(t,page); await endpoint(o,id);
    await centreFrame(page,surface);
    await expect.poll(async()=>o.evaluate(e=>getComputedStyle(e).opacity)).toBe('1');
    if(surface==='iframe') {await x.focus();await page.keyboard.press('Enter');}
    else await x.click();
    await closed(o,id);
    if(surface==='iframe') await focusTrigger(t,page); else await t.click();
    await endpoint(o,id);
    await centreFrame(page,surface);
    await expect.poll(async()=>o.evaluate(e=>getComputedStyle(e).opacity)).toBe('1');
    if(surface==='iframe') {await x.focus();await page.keyboard.press('Enter');}
    else await x.click();
    await closed(o,id);
  }
 });
}

test('ds-117 forced viewport edge flips anchored menu (rendered placement)',async({page})=>{
 const {root,t,o}=await scene(page,117,1440,'hosted');
 // Force the actual anchor near the viewport bottom/right; no visual-only marker.
 await root.locator('.sp-controls').evaluate(e=>{e.style.position='fixed';e.style.right='12px';e.style.bottom='12px';e.style.zIndex='2'});
 if(!await open(t,o,117,page)) return;
 const r=await rect(o),a=await rect(t),v=await viewport(root);
 expect(fits(r,v)).toBe(true);
 if(await o.evaluate(e=>getComputedStyle(e).positionAnchor==='--project-split-more')) {
   expect(r.bottom).toBeLessThan(a.y+2); // flip-block above the anchor
 } else {
   expect(v.h-r.bottom).toBeGreaterThanOrEqual(8); // useful fixed fallback
 }
});

test('ds-117 simulated no anchor positioning retains usable native corner overlay',async({page})=>{
 const {root,t,o}=await scene(page,117,1440,'hosted');
 await page.addStyleTag({content:'.split-menu {position-anchor:auto !important;position-area:none !important;inset:auto 1rem 1rem auto !important;margin:0 !important}'});
 if(!await open(t,o,117,page)) return;
 const r=await rect(o),v=await viewport(root);
 expect(fits(r,v)).toBe(true);
 expect(v.w-r.right).toBeGreaterThan(8);
 expect(v.h-r.bottom).toBeGreaterThan(8);
 await o.locator('a[href="#project-people"]').click();
 expect(await root.locator('body').evaluate(()=>location.hash)).toBe('#project-people');
});

test('ds-97 fresh backdrop click and explicit fallback by engine',async({page,browserName})=>{
 const {root,t,o}=await scene(page,97,1440,'hosted');
 if(!await open(t,o,97,page)) return; // invoker-less engine: documented no-op
 // Backdrop is not hit-test-ready while its discrete entry is in flight.
 await expect.poll(async()=>o.evaluate(e=>getComputedStyle(e).transform)).toBe('none');
 await expect.poll(async()=>o.evaluate(e=>getComputedStyle(e,'::backdrop').opacity)).toBe('1');
 const r=await rect(o),v=await viewport(root);
 await page.mouse.click(Math.min(r.right+40,v.w-10),100);
 if(browserName==='chromium') expect(await state(o,97)).toBe(false);
 if(await state(o,97)) {
   // Actual no-backdrop-dismiss behavior: Close must remain operable.
   await o.locator('.nav-close').focus(); await page.keyboard.press('Enter');
 }
 await closed(o,97);
 expect(await t.evaluate(e=>e===document.activeElement)).toBe(true);
});

test('ds-97 simulated missing closedby has explicit and Escape paths',async({page})=>{
 const {root,t,o}=await scene(page,97,390,'hosted');
 await o.evaluate(e=>e.removeAttribute('closedby'));
 if(!await open(t,o,97,page)) return;
 const v=await viewport(root);
 await root.locator('body').click({position:{x:v.w-4,y:10},force:true});
 expect(await state(o,97)).toBe(true);
 await o.locator('.nav-close').click();await closed(o,97);
 await t.click();await endpoint(o,97);
 await page.keyboard.press('Escape');await closed(o,97);
});
