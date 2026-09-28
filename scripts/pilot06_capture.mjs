/* Browser evidence reproduction. Run against a local server on port 8787; no client scripts. */
import { chromium } from '@playwright/test';
import { arenaLaunchOptions } from './arena-browser/arena-launch-options.mjs';
import { mkdirSync, writeFileSync } from 'node:fs';
const phase = process.argv[2] || 'before';
const dir = 'docs/evidence/pilot-06'; mkdirSync(dir, { recursive: true });
const browser = await chromium.launch(await arenaLaunchOptions());
const results = [];
const selectors = {97:['.nav-open','#site-drawer'],117:['.split-more','#split-menu'],131:['[command="show-popover"]','#auto-toast-1']};
for (const id of [97,117,131]) for (const [w,h] of (phase==='after-dark'?[[390,844]]:[[1440,900],[390,844]])) for (const surface of (phase==='after-dark'?['hosted']:['hosted','iframe','download'])) {
  const context = await browser.newContext({viewport:{width:w,height:h},javaScriptEnabled:false, colorScheme:phase==='after-dark'?'dark':'light',reducedMotion:'reduce',serviceWorkers:'block'});
  const page = await context.newPage();
  const path = surface === 'hosted' ? `/play/ds-${id}/` : surface === 'download' ? `/download/ds-${id}.html` : `/spells/ds-${id}/`;
  await page.goto(`http://127.0.0.1:8787${path}`);
  const root = surface === 'iframe' ? page.frameLocator('iframe').first() : page;
  const [triggerSel,overlaySel] = selectors[id];
  const trigger = root.locator(triggerSel), overlay = root.locator(overlaySel);
  const grab = async (state) => {
    const metrics = await root.locator('body').evaluate((body,{triggerSel,overlaySel,id})=>{
      const t=document.querySelector(triggerSel),o=document.querySelector(overlaySel);
      const r=e=>{const x=e.getBoundingClientRect();return {x:x.x,y:x.y,w:x.width,h:x.height,right:x.right,bottom:x.bottom}};
      return {viewport:[innerWidth,innerHeight],document:[body.scrollWidth,body.scrollHeight],trigger:r(t),overlay:r(o),open:id===97?o.matches(':modal'):o.matches(':popover-open'),active:document.activeElement?.outerHTML?.slice(0,170),links:[...document.querySelectorAll(id===97?'.nav-drawer a':id===117?'.split a, .split-menu a':'.auto-toast a')].map(a=>a.getAttribute('href')), styles:{display:getComputedStyle(o).display,position:getComputedStyle(o).position,opacity:getComputedStyle(o).opacity}};
    },{triggerSel,overlaySel,id});
    await (surface === 'iframe' ? page.locator('iframe').first() : page).screenshot({path:`${dir}/${phase}-ds-${id}-${w}-${surface}-${state}.png`});
    results.push({id,w,surface,state,...metrics});
  };
  await grab('initial');
  try {await trigger.click({timeout:2500}); await page.waitForTimeout(350); await grab('active');
    if(id===97){await page.keyboard.press('Escape');results.push({id,w,surface,probe:'escape',open:await overlay.evaluate(e=>e.matches(':modal'))});}
    if(id===117||id===131){await page.keyboard.press('Escape');results.push({id,w,surface,probe:'escape',open:await overlay.evaluate(e=>e.matches(':popover-open'))});}
  } catch(e){results.push({id,w,surface,error:String(e).slice(0,300)});}
  await context.close();
}
writeFileSync(`${dir}/${phase}-observations.json`,JSON.stringify(results,null,2)+'\n');
await browser.close();
