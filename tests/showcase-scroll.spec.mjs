/** Batch 02: real scroll/fragment states, not a feature-parser pass. */
import {test,expect} from '@playwright/test';
const ids=[30,55,69,93,111,134];
const rect=el=>el.evaluate(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom};});
const style=(el,key)=>el.evaluate((e,k)=>getComputedStyle(e)[k],key);
const scrollPage=(root,y)=>root.locator('body').evaluate((e,y)=>e.ownerDocument.defaultView.scrollTo({top:y,behavior:'instant'}),y);
const viewport=root=>root.locator('body').evaluate(e=>e.ownerDocument.defaultView.innerHeight);
const supports=(root,property,value)=>root.locator('body').evaluate((e,[p,v])=>e.ownerDocument.defaultView.CSS.supports(p,v),[property,value]);
const position=el=>el.evaluate(e=>e.getBoundingClientRect().top+e.ownerDocument.defaultView.scrollY);

async function check(root,page,id,motion,browserName) {
 if(id===30){
  const bar=root.locator('.sticky-cta'),h=await viewport(root);
  const original=await rect(bar);
  expect(Math.abs(original.bottom-h)).toBeLessThan(2);
  await scrollPage(root,500);
  await expect.poll(async()=>Math.abs((await rect(bar)).bottom-h)).toBeLessThan(2);
  await scrollPage(root,850);
  await expect.poll(async()=>Math.abs((await rect(bar)).bottom-h)).toBeLessThan(2);
  await root.getByRole('link',{name:'Session details'}).click();
  await expect.poll(()=>root.locator('#session-details').evaluate(e=>e.matches(':target'))).toBe(true);
  const destination=await rect(root.locator('#session-details'));
  expect(destination.y).toBeGreaterThanOrEqual(0);expect(destination.y).toBeLessThan(h);
  await root.getByRole('link',{name:'Back to the itinerary'}).click();
  await scrollPage(root,750);
 }
 if(id===55){
  const cards=root.locator('.card'),first=cards.first(),last=cards.last();
  const start=await position(first),lastStart=await position(last);
  const initial=await rect(first);const firstInset=parseFloat(await style(first,'top'));
  const lastInset=parseFloat(await style(last,'top'));
  const timeline=await supports(root,'animation-timeline','view()');
  await scrollPage(root,start-firstInset+120);
  await expect.poll(async()=>Math.abs((await rect(first)).y-firstInset)).toBeLessThan(2);
  await scrollPage(root,lastStart-lastInset);
  await expect.poll(async()=>Math.abs((await rect(first)).y-firstInset)).toBeLessThan(2);
  expect((await rect(last)).y).toBeGreaterThan((await rect(first)).y+100);
  expect((await rect(last)).y).toBeLessThan((await rect(first)).bottom);
  // Actual exit state: scale/filter are measured, not inferred from @supports.
  await scrollPage(root,lastStart+initial.h*.35);
  if(timeline&&motion!=='reduce'){
   await expect.poll(async()=>(await rect(first)).w/initial.w).toBeLessThan(.99);
   expect(await style(first,'filter')).not.toBe('brightness(1)');
  } else {
   expect(await style(first,'transform')).toBe('none');
   expect(await style(first,'filter')).toBe('none');
  }
  await scrollPage(root,0);
  await expect.poll(async()=>Math.abs((await rect(first)).w-initial.w)).toBeLessThan(1);
  await expect.poll(async()=>(await rect(first)).y).toBeGreaterThan(150);
  await scrollPage(root,lastStart-lastInset);
 }
 if(id===69){
  const scroller=root.locator('.table-wrapper'),cell=root.locator('tbody th').first();
  expect(await scroller.evaluate(e=>e.scrollWidth-e.clientWidth)).toBeGreaterThan(50);
  expect(await style(cell,'boxShadow')).toBe('none');
  await scroller.focus();await page.keyboard.press('ArrowRight');
  await expect.poll(()=>scroller.evaluate(e=>e.scrollLeft)).toBeGreaterThan(0);
  // Let the native key-scroll finish before testing an independent reversal.
  // Reduced CSS transitions do not disable the browser's own key-scroll animation.
  await expect(async()=>{
   const left=await scroller.evaluate(e=>e.scrollLeft);
   await page.waitForTimeout(200);
   expect(await scroller.evaluate(e=>e.scrollLeft)).toBe(left);
  }).toPass({timeout:3000});
  await scroller.evaluate(e=>e.scrollLeft=200);
  await expect.poll(async()=>Math.abs((await rect(cell)).x-(await rect(scroller)).x-1)).toBeLessThan(2);
  const query=await supports(root,'container-type','scroll-state');
  if(browserName==='chromium'||query)await expect.poll(()=>style(cell,'boxShadow')).not.toBe('none');
  else {expect(await style(cell,'boxShadow')).toBe('none');expect(await style(cell,'borderInlineEndWidth')).toBe('1px');}
  await scroller.evaluate(e=>e.scrollLeft=0);
  await expect.poll(()=>style(cell,'boxShadow')).toBe('none');
  await scroller.evaluate(e=>e.scrollLeft=200);
  if(query)await expect.poll(()=>style(cell,'boxShadow')).not.toBe('none');
  if(motion==='reduce')expect(await style(cell,'transitionDuration')).toBe('0s');
 }
 if(id===93){
  const carousel=root.locator('.snap-carousel'),slides=root.locator('.slide'),captions=root.locator('.caption');
  const query=await supports(root,'container-type','scroll-state');
  const enhanced=query&&motion!=='reduce';
  expect(await carousel.evaluate(e=>e.scrollWidth-e.clientWidth)).toBeGreaterThan(100);
  await expect.poll(()=>style(captions.first(),'opacity')).toBe('1');
  await expect.poll(()=>style(captions.last(),'opacity')).toBe(enhanced?'0':'1');
  await carousel.focus();await page.keyboard.press('ArrowRight');
  await expect.poll(()=>carousel.evaluate(e=>e.scrollLeft)).toBeGreaterThan(0);
  await carousel.evaluate(e=>e.scrollLeft=e.scrollWidth);
  await expect.poll(()=>style(captions.last(),'opacity')).toBe('1');
  await expect.poll(()=>style(captions.first(),'opacity')).toBe(enhanced?'0':'1');
  // Reversal, and a real focus target even without the query enhancement.
  await carousel.evaluate(e=>e.scrollLeft=0);
  await expect.poll(()=>style(captions.first(),'opacity')).toBe('1');
  await slides.last().focus();await expect(slides.last()).toBeFocused();
  await expect.poll(()=>style(captions.last(),'opacity')).toBe('1');
  await carousel.focus();await carousel.evaluate(e=>e.scrollLeft=e.scrollWidth);
  await expect.poll(()=>style(captions.last(),'opacity')).toBe('1');
  const last=await rect(slides.last()),outer=await rect(carousel);
  expect(Math.abs(last.right-outer.right)).toBeLessThan(2);
  if(motion==='reduce')expect(await style(captions.last(),'transitionDuration')).toBe('0s');
  await carousel.evaluate(e=>e.scrollIntoView({block:'center',behavior:'instant'}));
 }
 if(id===111){
  const metrics=root.locator('.kpi'),bars=root.locator('.kpi-track i');
  const timeline=await supports(root,'animation-timeline','view()');
  const ratio=i=>bars.nth(i).evaluate(e=>e.getBoundingClientRect().width/e.parentElement.getBoundingClientRect().width);
  if(timeline&&motion!=='reduce')await expect.poll(()=>ratio(0)).toBeLessThan(.01);
  else await expect.poll(()=>ratio(0)).toBeCloseTo(.72,2);
  for(const [i,value] of [72,48,91].entries()){
   await scrollPage(root,(await position(metrics.nth(i)))-40);
   await expect.poll(()=>ratio(i)).toBeCloseTo(value/100,2);
   await expect(metrics.nth(i).getByText(`${value}%`,{exact:true})).toBeVisible();
  }
  await scrollPage(root,0);
  if(timeline&&motion!=='reduce')await expect.poll(()=>ratio(0)).toBeLessThan(.01);
  else expect(await ratio(0)).toBeCloseTo(.72,2);
  await root.getByRole('link',{name:'Explore the allocation report'}).click();
  await scrollPage(root,(await position(metrics.first()))-100);
  await expect.poll(()=>ratio(0)).toBeCloseTo(.72,2);
 }
 if(id===134){
  const row=root.locator('.swipe-item').first(),action=row.locator('a');
  expect(await row.evaluate(e=>e.scrollWidth-e.clientWidth)).toBeGreaterThan(80);
  expect(await row.evaluate(e=>e.scrollLeft)).toBe(0);
  await row.focus();await page.keyboard.press('Tab');await expect(action).toBeFocused();
  await expect.poll(()=>row.evaluate(e=>e.scrollLeft)).toBeGreaterThan(80);
  await action.click();
  await expect.poll(()=>root.locator('#field-guide-details').evaluate(e=>e.matches(':target'))).toBe(true);
  await expect(root.locator('.swipe-item')).toHaveCount(2);
  await root.locator('#field-guide-details a').click();
  await row.evaluate(e=>e.scrollLeft=0);
  await expect.poll(()=>row.evaluate(e=>e.scrollLeft)).toBeLessThan(2);
  await row.focus();await page.keyboard.press('ArrowRight');
  await expect.poll(()=>row.evaluate(e=>e.scrollLeft)).toBeGreaterThan(0);
  await row.evaluate(e=>e.scrollLeft=e.scrollWidth);
  await row.evaluate(e=>e.scrollIntoView({block:'center',behavior:'instant'}));
 }
}

test.beforeAll(async({browser,browserName})=>console.log(`Batch 02 engine: ${browserName} ${browser.version()}`));
for(const surface of ['play','download','iframe'])for(const width of [1440,390])for(const motion of ['no-preference','reduce'])for(const id of ids){
 test(`${surface} ds-${id} ${width} ${motion}: observed scroll/state`,async({browser,browserName},info)=>{
  const context=await browser.newContext({javaScriptEnabled:false,viewport:{width,height:width===390?844:900},reducedMotion:motion});
  const page=await context.newPage();
  const url=surface==='iframe'?`spells/ds-${id}/`:surface==='download'?`download/ds-${id}.html`:`play/ds-${id}/`;
  await page.goto(`${info.project.use.baseURL}/${url}`);
  const root=surface==='iframe'?page.frameLocator('iframe[title^="Isolated demonstration"]'):page;
  await expect(root.locator('.journey-demo')).toBeVisible();
  await expect(root.locator('script')).toHaveCount(0);
  const capture=process.env.DS_CAPTURE&&surface==='play'&&browserName==='chromium';
  const file=`docs/evidence/batch-02/after-ds-${id}-${width}${motion==='reduce'?'-reduced':''}`;
  if(capture)await page.screenshot({path:`${file}.png`});
  await check(root,page,id,motion,browserName);
  expect(await root.locator('body').evaluate(e=>e.ownerDocument.documentElement.scrollWidth-e.ownerDocument.documentElement.clientWidth)).toBeLessThanOrEqual(1);
  if(capture)await page.screenshot({path:`${file}-active.png`});
  await context.close();
 });
}

for(const id of ids)test(`ds-${id}: dark mobile touch and explicit enhancement removal`,async({browser,browserName},info)=>{
 const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844},hasTouch:true,isMobile:browserName!=='firefox',colorScheme:'dark',reducedMotion:'reduce'});
 const page=await context.newPage();await page.goto(`${info.project.use.baseURL}/play/ds-${id}/`);
 // Delete only enhancement at-rules: fault injection, not an old-browser claim.
 await page.evaluate(()=>{for(const sheet of document.styleSheets)for(let i=sheet.cssRules.length-1;i>=0;i--)if(/^@(supports|container)/.test(sheet.cssRules[i].cssText))sheet.deleteRule(i)});
 if(id===30){await page.getByRole('link',{name:'Session details'}).tap();await expect(page.locator('#session-details')).toBeInViewport();}
 if(id===55){const first=page.locator('.card').first();await scrollPage(page,(await position(first))+100);expect(await style(first,'position')).toBe('sticky');expect(await style(first,'transform')).toBe('none');}
 if(id===69){await page.locator('.table-wrapper').evaluate(e=>e.scrollLeft=200);expect(await style(page.locator('tbody th').first(),'boxShadow')).toBe('none');expect(await style(page.locator('tbody th').first(),'borderInlineEndWidth')).toBe('1px');}
 if(id===93){for(const c of await page.locator('.caption').all())expect(await style(c,'opacity')).toBe('1');await page.locator('.snap-carousel').evaluate(e=>e.scrollLeft=e.scrollWidth);}
 if(id===111){await page.locator('.kpi').first().scrollIntoViewIfNeeded();const ratio=await page.locator('.kpi-track i').first().evaluate(e=>e.getBoundingClientRect().width/e.parentElement.getBoundingClientRect().width);expect(ratio).toBeCloseTo(.72,2);}
 if(id===134){await page.locator('.swipe-item').first().evaluate(e=>e.scrollLeft=e.scrollWidth);await page.locator('.swipe-action').first().tap();await expect(page.locator('#field-guide-details')).toBeInViewport();}
 expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(391);
 if(process.env.DS_CAPTURE&&browserName==='chromium')await page.screenshot({path:`docs/evidence/batch-02/after-ds-${id}-390-dark.png`});
 await context.close();
});
