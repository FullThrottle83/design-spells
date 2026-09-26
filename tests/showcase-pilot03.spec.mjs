import {test,expect} from '@playwright/test';

const ids=[48,49,50];
const rect=loc=>loc.evaluate(e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}});
const style=(loc,p)=>loc.evaluate((e,p)=>getComputedStyle(e)[p],p);
const settle=p=>p.waitForTimeout(240);
async function verify(root,page,id,motion,browserName){
 const doc=root.locator('body');
 expect(await doc.evaluate(()=>document.scripts.length)).toBe(0);
 expect(await doc.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
 if(id===48){
  const input=root.locator('#invite-email'),error=root.locator('#invite-email-error');
  expect(await input.getAttribute('required')).not.toBeNull();expect(await root.locator('label[for="invite-email"]')).toHaveCount(1);
  expect(await style(error,'display')).toBe('none');
  await input.fill('mara@');await input.press('Tab');await settle(page);
  expect(await input.evaluate(e=>e.matches(':user-invalid'))).toBe(true);expect(await style(error,'display')).toBe('block');
  const e=await rect(error),v=await doc.evaluate(()=>({w:innerWidth,h:innerHeight}));expect(e.x).toBeGreaterThanOrEqual(0);expect(e.right).toBeLessThanOrEqual(v.w+1);
  const next=await rect(root.locator('#invite-role'));expect(e.right<=next.x||e.x>=next.right||e.bottom<=next.y||e.y>=next.bottom).toBe(true);
  await input.fill('mara@northstar.co');await input.press('Tab');await settle(page);expect(await input.evaluate(e=>e.validity.valid)).toBe(true);expect(await style(error,'display')).toBe('none');
 }
 if(id===49){
  const details=root.locator('.filterbar'),summary=root.locator('.filter-trigger'),panel=root.locator('.filter-panel');
  expect(await details.evaluate(e=>e.open)).toBe(false);expect(await panel.isVisible()).toBe(false);
  await summary.focus();await page.keyboard.press('Enter');await settle(page);expect(await details.evaluate(e=>e.open)).toBe(true);
  const p=await rect(panel),v=await doc.evaluate(()=>({w:innerWidth,h:innerHeight}));expect(p.x).toBeGreaterThanOrEqual(-1);expect(p.right).toBeLessThanOrEqual(v.w+1);
  await root.locator('input[value="packs"]').check();await root.locator('input[value="weekend"]').check();expect(await root.locator('input[value="packs"]').isChecked()).toBe(true);
  await summary.focus();await page.keyboard.press('Enter');expect(await details.evaluate(e=>e.open)).toBe(false);expect(await panel.isVisible()).toBe(false);
 }
 if(id===50){
  const rows=root.locator('.form-row'),first=rows.first(),second=rows.nth(1),help1=first.locator('.help-rail'),help2=second.locator('.help-rail');
  expect(await style(help1,'visibility')).toBe('hidden');await first.locator('input').focus();await settle(page);expect(await style(help1,'visibility')).toBe('visible');expect(parseFloat(await style(help1,'opacity'))).toBe(1);
  const h=await rect(help1),v=await doc.evaluate(()=>({w:innerWidth,h:innerHeight}));expect(h.x).toBeGreaterThanOrEqual(-1);expect(h.right).toBeLessThanOrEqual(v.w+1);
  await page.keyboard.press('Tab');await settle(page);expect(await style(help1,'visibility')).toBe('hidden');expect(await style(help2,'visibility')).toBe('visible');
  if(motion==='reduce')expect(await style(help2,'transitionDuration')).toBe('0s');
 }
}
for(const width of [1440,390])for(const motion of ['no-preference','reduce'])for(const surface of ['hosted','download','iframe'])for(const id of ids)test(`${id} ${surface} ${width} ${motion}`,async({browser,browserName})=>{
 const context=await browser.newContext({viewport:{width,height:width===390?844:900},reducedMotion:motion,javaScriptEnabled:false});const page=await context.newPage();await page.goto(surface==='iframe'?`/spells/ds-${id}/`:surface==='download'?`/download/ds-${id}.html`:`/play/ds-${id}/`);const root=surface==='iframe'?page.frameLocator('iframe').first():page;await verify(root,page,id,motion,browserName);await context.close();
});
for(const id of ids)test(`${id} dark mobile`,async({browser,browserName})=>{const context=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark',hasTouch:true,javaScriptEnabled:false});const page=await context.newPage();await page.goto(`/play/ds-${id}/`);await verify(page,page,id,'no-preference',browserName);await context.close();});
for(const id of ids)test(`${id} simulated no anchor positioning`,async({page})=>{await page.setViewportSize({width:390,height:844});await page.goto(`/play/ds-${id}/`);await page.evaluate(()=>{for(const sheet of document.styleSheets)for(let i=sheet.cssRules.length-1;i>=0;i--)if(sheet.cssRules[i].cssText.startsWith('@supports (position-anchor'))sheet.deleteRule(i)});if(id===48){const i=page.locator('#invite-email');await i.fill('bad');await i.press('Tab');const e=await rect(page.locator('.error-bubble')),n=await rect(page.locator('#invite-role'));expect(e.bottom).toBeLessThanOrEqual(n.y+1)}if(id===49){await page.locator('.filter-trigger').click();const p=await rect(page.locator('.filter-panel'));expect(p.right).toBeLessThanOrEqual(391)}if(id===50){await page.locator('#public-name').focus();expect(await style(page.locator('#help-name'),'position')).toBe('static');expect(await style(page.locator('#help-name'),'visibility')).toBe('visible')}});
