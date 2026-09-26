import { test, expect } from '@playwright/test';

const ids = [5, 12, 16, 21, 37, 95];
test.beforeAll(async ({ browser, browserName }) => {
  console.log(`Pilot behavior engine: ${browserName} ${browser.version()}`);
});
const css = async (el, prop, pseudo = null) => el.evaluate((e, [p, pseudo]) => getComputedStyle(e, pseudo)[p], [prop, pseudo]);
const box = el => el.boundingBox();

async function exercise(root, page, id, width, motion) {
  if (id === 5) {
    const link = root.locator('.nav-link').first();
    expect(parseFloat(await css(link, 'width', '::after'))).toBe(0);
    await link.focus();
    await page.keyboard.press('Tab');
    await page.keyboard.press('Shift+Tab');
    await expect(link).toBeFocused();
    await expect.poll(async () => parseFloat(await css(link, 'width', '::after'))).toBeGreaterThan(50);
    if (motion === 'reduce') expect(await css(link, 'transitionDuration', '::after')).toBe('0s');
    await link.click();
    await expect(root.locator('#overview')).toBeInViewport();
    await link.hover();
    await expect.poll(async () => parseFloat(await css(link, 'width', '::after'))).toBeGreaterThan(50);
  }
  if (id === 12) {
    const gallery = root.locator('.gallery');
    const figures = gallery.locator('figure');
    const geometry = () => gallery.evaluate(e => ({left: e.scrollLeft, width: e.clientWidth, max:e.scrollWidth-e.clientWidth}));
    expect((await geometry()).max).toBeGreaterThan(200);
    await gallery.focus();
    await page.keyboard.press('ArrowRight');
    await expect.poll(async () => (await geometry()).left).toBeGreaterThan(5);
    // Prove snapping at an interior item, not just clamping at a scroll edge.
    await gallery.evaluate(e => {
      e.scrollLeft = e.firstElementChild.getBoundingClientRect().width + parseFloat(getComputedStyle(e).gap) - 45;
    });
    await expect.poll(async () => Math.abs((await box(figures.nth(1))).x - (await box(gallery)).x)).toBeLessThan(2);
    // Real wheel gestures, not fake active classes or script-set final positions.
    // Firefox can settle one item per transaction even for a large delta.
    const wheelToEdge = async (direction) => {
      await gallery.hover();
      await expect(async () => {
        await page.mouse.wheel(direction * 2200, 0);
        await expect.poll(async () => {
          const g = await geometry();
          return direction < 0 ? g.left : Math.abs(g.left - g.max);
        }, {timeout: 1200}).toBeLessThan(2);
      }).toPass({timeout: 7000, intervals: [300, 500, 1000]});
    };
    await wheelToEdge(1);
    const last = await box(figures.last()), gbox = await box(gallery);
    expect(Math.abs(last.x+last.width-gbox.x-gbox.width)).toBeLessThan(3);
    await wheelToEdge(-1);
    await wheelToEdge(1);
  }
  if (id === 16) {
    const input = root.getByRole('textbox', {name:'Full name',exact:true});
    const label = root.locator('label[for="profile-name"]');
    const relativeY = async () => (await box(label)).y - (await box(input)).y;
    const initial = await relativeY();
    await input.focus();
    await expect.poll(async () => (await relativeY())).toBeLessThan(initial-4);
    await input.fill('Alex Morgan');
    await root.getByRole('textbox',{name:'Email address'}).focus();
    expect((await relativeY())).toBeLessThan(initial-4);
    await input.fill('');
    await root.getByRole('textbox',{name:'Email address'}).focus();
    await expect.poll(async () => Math.abs((await relativeY())-initial)).toBeLessThan(1);
    await input.fill('Alex Morgan');
    await root.getByRole('textbox',{name:'Email address'}).fill('alex@example.com');
    if(motion==='reduce') expect(await css(label,'transitionDuration')).toBe('0s');
  }
  if (id === 21) {
    for (const chapter of ['materials','process']) {
      await root.locator(`a[href="#${chapter}"]`).click();
      const target = root.locator(`#${chapter}`);
      await expect.poll(() => target.evaluate(e => e.matches(':target'))).toBe(true);
      expect(await css(target,'outlineStyle')).toBe('solid');
      expect(await css(target,'outlineWidth')).toBe('2px');
      if(motion==='reduce') expect(await css(target,'animationName')).toBe('none');
      else await expect.poll(() => css(target,'boxShadow')).not.toBe('none');
    }
    await root.locator('.guide-reset').click();
    expect(await root.locator('section:target').count()).toBe(0);
    await root.locator('a[href="#materials"]').click();
  }
  if (id === 37) {
    const container = root.locator('.card-container'), media=root.locator('.card-media'), copy=root.locator('.card-copy');
    const narrow = await box(container);
    expect((await box(copy)).y).toBeGreaterThan((await box(media)).y+100);
    await root.getByLabel('Feature',{exact:true}).check();
    await expect(root.getByLabel('Feature',{exact:true})).toBeChecked();
    const wide = await box(container);
    expect(wide.width).toBeGreaterThan(narrow.width);
    const supported = await container.evaluate(() => CSS.supports('container-type','inline-size'));
    if(wide.width >= 420 && supported) expect(Math.abs((await box(copy)).y-(await box(media)).y)).toBeLessThan(3);
    else expect((await box(copy)).y).toBeGreaterThan((await box(media)).y+100);
    await root.getByLabel('Sidebar',{exact:true}).check();
    expect((await box(container)).width).toBe(narrow.width);
    await root.getByLabel('Feature',{exact:true}).check();
  }
  if (id === 95) {
    const chart=root.locator('.spark'), bars=chart.locator('span');
    const c=await box(chart), values=[34,58,41,72,66,90];
    expect(c.width).toBeGreaterThan(200);
    for(let i=0;i<6;i++) { const b=await box(bars.nth(i)); expect(b.width).toBeGreaterThan(20); expect(Math.abs(b.height/c.height*100-values[i])).toBeLessThan(1); }
    const color=await css(bars.first(),'backgroundColor');
    await chart.focus(); await page.keyboard.press('Tab'); await page.keyboard.press('Shift+Tab');
    await expect(chart).toBeFocused();
    await expect.poll(()=>css(bars.first(),'backgroundColor')).not.toBe(color);
    await expect.poll(()=>css(bars.first(),'backgroundColor')).toBe(await css(bars.last(),'backgroundColor'));
    await root.locator('summary').click();
    await expect(root.locator('details')).toHaveAttribute('open','');
    await expect(root.getByRole('cell',{name:'90%',exact:true})).toBeVisible();
    await root.locator('summary').click();
    await chart.focus(); await page.keyboard.press('Tab'); await page.keyboard.press('Shift+Tab');
    await expect.poll(()=>css(bars.first(),'backgroundColor')).toBe(await css(bars.last(),'backgroundColor'));
    if(motion==='reduce') expect(await css(bars.first(),'transitionDuration')).toBe('0s');
  }
}

for (const surface of ['play','download','iframe']) {
  for (const width of [1440,390]) for (const motion of ['no-preference','reduce']) {
    for (const id of ids) test(`${surface} ds-${id} ${width} ${motion}: real reversible behavior`, async ({browser},testInfo) => {
      const context=await browser.newContext({javaScriptEnabled:false, viewport:{width,height:width===390?844:900}, reducedMotion:motion});
      const page=await context.newPage();
      const base=testInfo.project.use.baseURL || 'http://127.0.0.1:8788';
      await page.goto(`${base}/${surface==='iframe'?`spells/ds-${id}/`:surface==='download'?`download/ds-${id}.html`:`play/ds-${id}/`}`);
      const root=surface==='iframe'? page.frameLocator('iframe[title^="Isolated demonstration"]'):page;
      await expect(root.locator('.showcase')).toBeVisible();
      if(surface==='iframe') await page.locator('iframe[title^="Isolated demonstration"]').scrollIntoViewIfNeeded();
      const capture=process.env.DS_CAPTURE && surface==='play' && testInfo.project.name==='chromium';
      const dest=`docs/evidence/pilot-01/after-ds-${id}-${width}${motion==='reduce'?'-reduced':''}`;
      if(capture) await page.screenshot({fullPage:true,path:`${dest}.png`});
      // Measure the demo's own viewport, not its embedding documentation.
      const demoWidth=await root.locator('body').evaluate(e=>e.ownerDocument.documentElement.clientWidth);
      await exercise(root,page,id,demoWidth,motion);
      expect(await root.locator('body').evaluate(e=>e.ownerDocument.documentElement.scrollWidth)).toBeLessThanOrEqual(demoWidth+1);
      if(capture) await page.screenshot({fullPage:true,path:`${dest}-active.png`});
      await context.close();
    });
  }
}

for(const id of ids) test(`ds-${id}: dark mobile, touch controls, and readable degraded presentation`, async({browser},testInfo)=>{
  const context=await browser.newContext({javaScriptEnabled:false,colorScheme:'dark',hasTouch:true,isMobile:testInfo.project.name !== 'firefox',viewport:{width:390,height:844},reducedMotion:'reduce'});
  const page=await context.newPage();
  await page.goto(`${testInfo.project.use.baseURL || 'http://127.0.0.1:8788'}/play/ds-${id}/`);
  if(id===5) {await page.locator('.nav-link').first().tap();expect(new URL(page.url()).hash).toBe('#overview');}
  if(id===16) {await page.getByRole('textbox',{name:'Full name',exact:true}).tap();await expect(page.getByRole('textbox',{name:'Full name',exact:true})).toBeFocused();}
  if(id===21) {await page.locator('a[href="#process"]').tap();await expect(page.locator('#process')).toHaveCSS('outline-width','2px');}
  if(id===37) {await page.getByLabel('Feature',{exact:true}).tap();await expect(page.getByLabel('Feature',{exact:true})).toBeChecked();}
  if(id===95) {await page.locator('summary').tap();await expect(page.locator('table')).toBeVisible();}
  if(id===12) {await page.locator('.gallery').evaluate(e=>e.scrollLeft=e.scrollWidth);await expect.poll(()=>page.locator('.gallery').evaluate(e=>e.scrollLeft)).toBeGreaterThan(300);}
  expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  if(process.env.DS_CAPTURE && testInfo.project.name==='chromium') await page.screenshot({fullPage:true,path:`docs/evidence/pilot-01/after-ds-${id}-390-dark.png`});
  // Explicit fault injection, NOT evidence about a historical browser. Remove enhancement rules.
  if(id===37) {
    await page.evaluate(()=>{for(const sheet of document.styleSheets)for(let i=sheet.cssRules.length-1;i>=0;i--)if(sheet.cssRules[i].cssText.startsWith('@container'))sheet.deleteRule(i);});
    await page.setViewportSize({width:1440,height:900});
    const m=await box(page.locator('.card-media')),c=await box(page.locator('.card-copy'));
    expect(c.y).toBeGreaterThan(m.y+100);
  }
  if(id===12) {await page.evaluate(()=>{const s=document.createElement('style');s.textContent='.gallery {scroll-snap-type:none}';document.head.append(s)});await page.locator('.gallery').evaluate(e=>e.scrollLeft=150);expect(await page.locator('.gallery').evaluate(e=>e.scrollLeft)).toBe(150);}
  if(id===21) {await page.evaluate(()=>{const s=document.createElement('style');s.textContent='section:target {animation:none}';document.head.append(s)});await expect(page.locator('#process')).toHaveCSS('outline-width','2px');}
  await context.close();
});
