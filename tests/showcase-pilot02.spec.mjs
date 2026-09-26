import {test,expect} from '@playwright/test';
const ids=[111,93,134,30,55,69];
const style=(el,p)=>el.evaluate((e,p)=>getComputedStyle(e)[p],p);
const rect=el=>el.evaluate(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};});
const settle=page=>page.waitForTimeout(350);
test.beforeAll(async({browser,browserName})=>console.log(`${process.env.CI ? "::notice::" : ""}Pilot 02: ${browserName} ${browser.version()}`));
async function scrollDocument(root,selector,y){
 await root.locator(selector).first().evaluate((e,y)=>window.scrollTo(0,e.getBoundingClientRect().top+scrollY-y),y);
}
async function verify(root,page,id,motion,browserName){
 const doc=root.locator('body');
 expect(await doc.evaluate(e=>e.scrollWidth<=innerWidth+1)).toBe(true);
 if(id===111){
  const k=root.locator('.kpi').first(),fill=k.locator('i'),track=k.locator('.kpi-track');
  const ratio=async()=>(await rect(fill)).width/(await rect(track)).width;
  expect(await k.innerText()).toContain('72%');
  const enhanced=await k.evaluate(()=>CSS.supports('animation-timeline: view()'));
  const height=await doc.evaluate(()=>innerHeight);
  await scrollDocument(root,'.kpi',height-50);await settle(page);
  const early=await ratio();
  if(enhanced&&motion!=='reduce') expect(early).toBeLessThan(.2); else expect(early).toBeCloseTo(.72,2);
  await scrollDocument(root,'.kpi',height*.45);await settle(page);
  const mid=await ratio();
  if(enhanced&&motion!=='reduce'){expect(mid).toBeGreaterThan(early+.1);expect(mid).toBeLessThan(.72);}
  await scrollDocument(root,'.kpi',20);await settle(page);
  expect(await ratio()).toBeCloseTo(.72,2);
  await scrollDocument(root,'.kpi',height-50);await settle(page);
  expect(await ratio()).toBeCloseTo(early,2);
  if(motion==='reduce') expect(await style(fill,'animationName')).toBe('none');
 }
 if(id===93){
  const scroller=root.locator('.snap-carousel'),slides=scroller.locator('.slide'),captions=scroller.locator('.caption');
  expect(await scroller.evaluate(e=>e.scrollWidth-e.clientWidth)).toBeGreaterThan(200);
  await scroller.focus();await page.keyboard.press('ArrowRight');
  await expect.poll(()=>scroller.evaluate(e=>e.scrollLeft)).toBeGreaterThan(5);
  // Set an off-grid position: the UA, not the test, chooses the snapped position.
  await scroller.evaluate(e=>{const s=e.children[1];e.scrollLeft=s.offsetLeft-e.offsetLeft-(e.clientWidth-s.clientWidth)/2-30;});
  await expect.poll(async()=>Math.abs((await rect(slides.nth(1))).x+(await rect(slides.nth(1))).width/2-(await rect(scroller)).x-(await rect(scroller)).width/2)).toBeLessThan(2);
  await expect.poll(()=>style(captions.nth(1),'opacity')).toBe('1');
  if(browserName==='chromium') await expect.poll(()=>style(captions.first(),'opacity')).toBe('0');
  else expect(await style(captions.first(),'opacity')).toBe('1');
  await scroller.evaluate(e=>e.scrollLeft=0);
  await expect.poll(()=>style(captions.first(),'opacity')).toBe('1');
  if(browserName==='chromium') await expect.poll(()=>style(captions.nth(1),'opacity')).toBe('0');
  if(motion==='reduce') expect(await style(captions.first(),'transitionDuration')).toBe('0s');
 }
 if(id===134){
  const row=root.locator('.swipe-item').first(),link=row.locator('a');
  expect(await row.evaluate(e=>e.scrollWidth-e.clientWidth)).toBeGreaterThanOrEqual(79);
  expect(await row.evaluate(e=>e.scrollLeft)).toBe(0);
  await row.focus();await page.keyboard.press('Tab');await expect(link).toBeFocused();
  await expect.poll(()=>row.evaluate(e=>e.scrollLeft)).toBeGreaterThan(60);
  const l=await rect(link),r=await rect(row);expect(l.x+l.width).toBeLessThanOrEqual(r.x+r.width+1);
  await page.keyboard.press('Enter');await expect(root.locator('#doc-0')).toBeInViewport();
  expect(await root.locator('#doc-0').evaluate(e=>e.matches(':target'))).toBe(true);
  await row.evaluate(e=>e.scrollLeft=0);await expect.poll(()=>row.evaluate(e=>e.scrollLeft)).toBeLessThan(1);
 }
 if(id===30){
  const cta=root.locator('.sticky-cta'),link=cta.locator('a');
  const short=await doc.evaluate(()=>innerHeight<=480);expect(await style(cta,'position')).toBe(short?'static':'sticky');expect(await style(cta,'boxShadow')).not.toBe('none');
  await scrollDocument(root,'.guide-body section:nth-child(2)',40);await settle(page);
  const r=await rect(cta),h=await doc.evaluate(()=>innerHeight);if(!short) expect(Math.abs(r.y+r.height-h)).toBeLessThan(2); else expect(r.y).toBeGreaterThan(h);
  await link.focus();await page.keyboard.press('Enter');
  await expect(root.locator('#checklist')).toBeInViewport();
  await root.locator('#checklist input').first().check();await expect(root.locator('#checklist input').first()).toBeChecked();
  const target=await rect(root.locator('#checklist'));const c=await rect(cta);expect(c.y+c.height).toBeLessThanOrEqual(target.y+1);
 }
 if(id===55){
  const cards=root.locator('.card-stack .card'),first=cards.first();
  const inset=parseFloat(await style(first,'top'));
  const short=await doc.evaluate(()=>innerHeight<=550);
  const initial=await rect(first);expect(initial.y).toBeGreaterThan(inset);
  await scrollDocument(root,'.card-stack',-80);await settle(page);
  if(!short) expect(Math.abs((await rect(first)).y-inset)).toBeLessThan(2); else expect(await style(first,'position')).toBe('static');
  await scrollDocument(root,'.card-stack',-160);await settle(page);
  if(!short) expect(Math.abs((await rect(first)).y-inset)).toBeLessThan(2); else expect(await style(first,'position')).toBe('static');
  // The authored exit-crossing timeline is measured near the stack's exit.
  await cards.last().evaluate(e=>window.scrollTo(0,e.getBoundingClientRect().top+scrollY-32));await settle(page);
  const enhanced=await first.evaluate(()=>CSS.supports('animation-timeline: view()'));
  if(enhanced&&motion!=='reduce') {
   expect(await style(first,'animationName')).toBe('stack-shrink');
  } else expect(await style(first,'transform')).toBe('none');
  const a=await rect(first),b=await rect(cards.last());if(!short) expect(a.y+a.height).toBeGreaterThan(b.y); else expect(a.y+a.height).toBeLessThan(b.y);
  if(enhanced&&motion!=='reduce'){
   await root.locator('.card-stack').evaluate(e=>window.scrollTo(0,e.getBoundingClientRect().bottom+scrollY-innerHeight/3));await settle(page);
   expect(await first.evaluate(e=>new DOMMatrix(getComputedStyle(e).transform).a)).toBeLessThan(.99);
   expect(parseFloat((await style(first,'filter')).match(/[\d.]+/)[0])).toBeLessThan(.95);
  }
  await doc.evaluate(()=>window.scrollTo(0,0));await settle(page);expect((await rect(first)).y).toBeCloseTo(initial.y,0);
 }
 if(id===69){
  const scroller=root.locator('.table-wrapper'),cell=scroller.locator('tbody th').first();
  const x=(await rect(cell)).x;
  expect(await scroller.evaluate(e=>e.scrollWidth-e.clientWidth)).toBeGreaterThan(100);
  expect(await style(cell,'boxShadow')).toBe('none');
  await scroller.focus();await page.keyboard.press('ArrowRight');await expect.poll(()=>scroller.evaluate(e=>e.scrollLeft)).toBeGreaterThan(5);
  await scroller.evaluate(e=>e.scrollLeft=150);await settle(page);
  expect((await rect(cell)).x).toBeCloseTo(x,0);
  if(browserName==='chromium') await expect.poll(()=>style(cell,'boxShadow')).not.toBe('none');
  else expect(await style(cell,'boxShadow')).toBe('none');
  await scroller.evaluate(e=>e.scrollLeft=80);await settle(page);
  if(browserName==='chromium') expect(await style(cell,'boxShadow')).not.toBe('none');
  await scroller.evaluate(e=>e.scrollLeft=0);await expect.poll(()=>style(cell,'boxShadow')).toBe('none');
  expect((await rect(cell)).x).toBeCloseTo(x,0);
 }
}
for(const width of [1440,390])for(const motion of ['no-preference','reduce'])for(const surface of ['hosted','download','iframe'])for(const id of ids){
 test(`${id} ${surface} ${width} ${motion}`,async({browser,browserName})=>{
  const context=await browser.newContext({viewport:{width,height:width===390?844:900},reducedMotion:motion,javaScriptEnabled:false});
  const page=await context.newPage();
  await page.goto(surface==='iframe'?`/spells/ds-${id}/`:surface==='download'?`/download/ds-${id}.html`:`/play/ds-${id}/`);
  const root=surface==='iframe'?page.frameLocator('iframe').first():page;
  await verify(root,page,id,motion,browserName);await context.close();
 });
}
for(const id of ids)test(`${id} dark touch-emulated mobile`,async({browser,browserName})=>{
 const context=await browser.newContext({viewport:{width:390,height:844},hasTouch:true,colorScheme:'dark',javaScriptEnabled:false});const page=await context.newPage();await page.goto(`/play/ds-${id}/`);await verify(page,page,id,'no-preference',browserName);if(id===134){await page.locator('.swipe-action').first().tap();await expect(page.locator('#doc-0')).toBeInViewport();}if(id===30){await page.locator('.sticky-cta a').tap();await expect(page.locator('#checklist')).toBeInViewport();}await context.close();
});
for(const id of [111,93,55,69])test(`${id} simulated unsupported enhancement`,async({page})=>{
 await page.goto(`/play/ds-${id}/`);
 // Remove enhancement blocks, not base CSS: an explicit degradation simulation.
 await page.evaluate(()=>{for(const sheet of document.styleSheets){for(let i=sheet.cssRules.length-1;i>=0;i--){const r=sheet.cssRules[i];if(r.cssText.startsWith('@supports')||r.cssText.startsWith('@container'))sheet.deleteRule(i);}}});
 if(id===111)expect(await page.locator('.kpi-track i').first().evaluate(e=>e.clientWidth/e.parentElement.clientWidth)).toBeCloseTo(.72,2);
 if(id===93)for(const c of await page.locator('.caption').all())await expect.poll(()=>style(c,'opacity')).toBe('1');
 if(id===55){expect(await style(page.locator('.card').first(),'position')).toBe('sticky');expect(await style(page.locator('.card').first(),'transform')).toBe('none');}
 if(id===69){const e=page.locator('.table-wrapper');await e.evaluate(e=>e.scrollLeft=120);expect(await e.evaluate(e=>e.scrollLeft)).toBe(120);expect(await style(e.locator('th').first(),'boxShadow')).toBe('none');}
});
test('30 short zoom-equivalent viewport leaves CTA in flow',async({page})=>{await page.setViewportSize({width:360,height:450});await page.goto('/play/ds-30/');expect(await style(page.locator('.sticky-cta'),'position')).toBe('static');await page.locator('.sticky-cta a').click();await expect(page.locator('#checklist')).toBeInViewport();});
