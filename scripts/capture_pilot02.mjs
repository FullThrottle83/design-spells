// Browser evidence only; never shipped in a demonstration.
// npm run build && python3 -m http.server 8787 --directory public
// node scripts/capture_pilot02.mjs [before|after|fallback]
import {chromium} from 'playwright';
import fs from 'node:fs';
const phase=process.argv[2]||'after';
const browser=await chromium.launch(process.env.DS_CHROMIUM_PATH?{executablePath:process.env.DS_CHROMIUM_PATH,args:['--no-sandbox','--disable-dev-shm-usage']}:{});
const out=`docs/evidence/pilot-02/${phase}`;fs.mkdirSync(out,{recursive:true});const observations=[];
const variants=phase!=='after'?[['no-preference','light']]:[['no-preference','light'],['reduce','light'],['no-preference','dark'],['reduce','dark']];
for(const width of [1440,390]) for(const [motion,scheme] of variants) for(const id of (phase==='fallback'?[111,93,55,69]:[111,93,134,30,55,69])){
 const page=await browser.newPage({viewport:{width,height:width===390?844:900},javaScriptEnabled:false,reducedMotion:motion,colorScheme:scheme,hasTouch:width===390});
 await page.goto(`${process.env.DS_CAPTURE_ORIGIN||'http://localhost:8787'}/play/ds-${id}/`);await page.waitForTimeout(350);
 if(phase==='fallback'){await page.evaluate(()=>{for(const sheet of document.styleSheets)for(let i=sheet.cssRules.length-1;i>=0;i--){const text=sheet.cssRules[i].cssText;if(text.startsWith('@supports')||text.startsWith('@container'))sheet.deleteRule(i);}});await page.waitForTimeout(350);}
 const prefix=`${out}/${id}-${width}-${motion}-${scheme}`;
 const record=async(state)=>{await page.screenshot({path:`${prefix}-${state}.jpg`,quality:85});observations.push({id,width,motion,scheme,state,version:browser.version(),metrics:await page.evaluate(()=>({scrollY,viewport:[innerWidth,innerHeight],pageWidth:document.documentElement.scrollWidth,elements:[...document.querySelectorAll('.kpi-track i,.caption,.swipe-item,.sticky-cta,.card-stack .card,.table-wrapper,tbody th:first-child')].map(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {class:e.className,x:r.x,y:r.y,width:r.width,height:r.height,scrollLeft:e.scrollLeft,scrollWidth:e.scrollWidth,clientWidth:e.clientWidth,opacity:s.opacity,transform:s.transform,filter:s.filter,shadow:s.boxShadow,position:s.position}})}))});};
 await record('initial');
 await page.evaluate(({id,phase})=>{
  const scroller=document.querySelector(({93:'.snap-carousel',134:'.swipe-item',69:'.table-wrapper'})[id]);
  if(scroller){scroller.scrollLeft=id===93?scroller.children[1].offsetLeft-scroller.offsetLeft-(scroller.clientWidth-scroller.children[1].clientWidth)/2-30:scroller.scrollWidth;return;}
  const target=document.querySelector(({111:'.kpi',30:'.guide-body section:nth-child(2)',55:'.card-stack .card:nth-child(3)'})[id]);
  if(phase!=='before'&&target)scrollTo(0,target.getBoundingClientRect().top+scrollY-(id===111?innerHeight*.45:60));else scrollTo(0,document.body.scrollHeight/2);
 },{id,phase});
 await page.waitForTimeout(500);await record('active');
 if(phase==='after'&&id===111){await page.locator('.kpi').first().evaluate(e=>scrollTo(0,e.getBoundingClientRect().top+scrollY-20));await page.waitForTimeout(200);await record('complete');}
 await page.close();
}
fs.writeFileSync(`${out}/observations.json`,JSON.stringify(observations,null,2));await browser.close();
