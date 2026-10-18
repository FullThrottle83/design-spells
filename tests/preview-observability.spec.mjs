import fs from "node:fs";
import { test, expect } from "@playwright/test";

// A rendered element is not evidence that a spell works. Each case below
// asserts a measurable state (geometry, animation progress, scroll offset,
// validity, computed style) that was previously unreachable or empty in the
// hosted demo. Chromium only: several of the features are not shipped
// elsewhere, and no support claim is derived from these runs.
test.use({ javaScriptEnabled: false });

const spells = JSON.parse(fs.readFileSync(new URL("../public/spells.json", import.meta.url), "utf8")).spells;

// Rendered row widths of a text node, one entry per visual line.
const lineWidths = el => {
  const range = document.createRange();
  range.selectNodeContents(el);
  const rows = new Map();
  for (const r of range.getClientRects()) {
    const key = Math.round(r.top);
    const row = rows.get(key) ?? { l: Infinity, r: -Infinity };
    row.l = Math.min(row.l, r.left);
    row.r = Math.max(row.r, r.right);
    rows.set(key, row);
  }
  return [...rows.values()].map(r => Math.round(r.r - r.l));
};

// Visual signature of everything under <body>, including generated content.
const styleSignature = () => [...document.body.querySelectorAll("*")].flatMap(el =>
  [null, "::before", "::after"].map(pe => {
    const cs = getComputedStyle(el, pe);
    return ["opacity", "transform", "box-shadow", "filter", "background-color", "outline-style", "color"]
      .map(p => cs.getPropertyValue(p)).join("|");
  })).join("\n");

test("ds-110 sparkline bars have real, proportional heights", async ({ page, browserName }) => {
  test.skip(browserName !== "chromium", "typed attr() is asserted in Chromium only (Firefox keeps the fallback bar height)");
  await page.goto("/play/ds-110/");
  const bars = await page.locator(".attr-spark span").evaluateAll(els =>
    els.map(el => ({ w: el.offsetWidth, h: el.offsetHeight })));
  expect(bars).toHaveLength(6);
  for (const bar of bars) expect(bar.w).toBeGreaterThan(8);
  // data-v 72 vs 34, read through typed attr(): heights must follow the data.
  expect(bars[3].h / bars[0].h).toBeCloseTo(72 / 34, 1);
});

test("ds-105 meter fill width follows its own data-value", async ({ page, browserName }) => {
  test.skip(browserName !== "chromium", "typed attr() is asserted in Chromium only (Firefox keeps the 0% fallback)");
  await page.goto("/play/ds-105/");
  const { track, fill } = await page.evaluate(() => ({
    track: document.querySelector(".attr-meter").clientWidth,
    fill: document.querySelector(".attr-meter-fill").offsetWidth,
  }));
  expect(track).toBeGreaterThan(100);
  expect(fill / track).toBeCloseTo(0.72, 1);
  // The canonical authored markup must agree with the CSS: attr() reads the
  // styled element, never its parent.
  const authored = spells.find(s => s.id === "ds-105").html;
  expect(authored).toMatch(/class="attr-meter-fill"\s+data-value="72"/);
});

test("ds-63 hyphenation has a column narrower than its text", async ({ page, browserName }) => {
  await page.goto("/play/ds-63/");
  const m = await page.evaluate(lineWidths => {
    const rows = new Function("el", `return (${lineWidths})(el)`);
    const p = document.querySelector("article p");
    const auto = rows(p);
    const lang = document.documentElement.lang;
    const hyphens = getComputedStyle(p).hyphens;
    p.style.hyphens = "manual";
    const manual = rows(p);
    return { auto, manual, hyphens, lang, width: p.offsetWidth };
  }, lineWidths.toString());
  expect(m.lang).toBe("en");
  expect(m.hyphens).toBe("auto");
  expect(m.width).toBeLessThanOrEqual(240);
  // Wrapping to several lines is the precondition for any hyphenation.
  expect(m.auto.length).toBeGreaterThanOrEqual(3);
  // Control: breaking inside words must save a line versus hyphens: manual.
  // Hyphenation dictionaries ship with some browser builds and not others (a
  // local Chromium hyphenates; CI's runner build renders auto and manual
  // identically), so where the build cannot hyphenate this is annotated, not asserted.
  if (browserName === "chromium") {
    if (m.auto.length === m.manual.length) {
      test.info().annotations.push({ type: "skipped-assertion", description: "this browser build has no hyphenation dictionary: auto and manual wrap identically" });
    } else {
      expect(m.auto.length).toBeLessThan(m.manual.length);
    }
  }
});

test("ds-bonus text-wrap: balance changes where the heading breaks", async ({ page }) => {
  await page.goto("/play/ds-bonus/");
  const { balanced, greedy } = await page.evaluate(lineWidths => {
    const rows = new Function("el", `return (${lineWidths})(el)`);
    const h = document.querySelector("h2.text-balance");
    const balanced = rows(h);
    h.style.textWrap = "wrap";
    return { balanced, greedy: rows(h) };
  }, lineWidths.toString());
  expect(balanced.length).toBe(2);
  expect(greedy.length).toBe(2);
  expect(balanced[1] / balanced[0]).toBeGreaterThan(0.6);
  expect(greedy[1] / greedy[0]).toBeLessThan(0.5);
});

const viewTimelineSpells = spells.filter(s => /animation-timeline:\s*view\(/.test(s.css)).map(s => s.id);

for (const id of ["ds-91", "ds-135", "ds-139"]) {
  test(`${id} view() timeline follows page scroll, not a clipped wrapper`, async ({ page, browserName }) => {
    test.skip(browserName !== "chromium", "scroll-driven animation timelines are asserted in Chromium only");
    await page.goto(`/play/${id}/`);
    const read = () => page.evaluate(() => document.getAnimations()
      .filter(a => a.timeline instanceof ViewTimeline)
      .map(a => ({ root: a.timeline.source === document.documentElement, p: a.effect.getComputedTiming().progress })));
    const before = await read();
    expect(before.length).toBeGreaterThan(0);
    expect(before.every(a => a.root)).toBe(true);
    await page.evaluate(() => scrollTo({ top: (document.documentElement.scrollHeight - innerHeight) * 0.7, behavior: "instant" }));
    await expect.poll(async () => (await read())[0].p).not.toBe(before[0].p);
  });
}

test("every document-scroll view() demo binds its timeline to a scroller that can scroll", async ({ page, browserName }) => {
  test.skip(browserName !== "chromium", "scroll-driven animation timelines are asserted in Chromium only");
  expect(viewTimelineSpells.length).toBeGreaterThan(8);
  for (const id of viewTimelineSpells) {
    await page.goto(`/play/${id}/`);
    const bad = await page.evaluate(() => document.getAnimations()
      .filter(a => a.timeline instanceof ViewTimeline)
      .map(a => a.timeline.source)
      .filter(src => src !== document.documentElement && src.scrollHeight <= src.clientHeight && src.scrollWidth <= src.clientWidth)
      .map(src => src.tagName.toLowerCase() + "." + [...src.classList].join(".")));
    expect(bad, `${id}: timeline bound to a box that never scrolls`).toEqual([]);
  }
});

test("ds-94 sticky header stays pinned inside a scroller that really overflows", async ({ page }) => {
  await page.goto("/play/ds-94/");
  const scroller = page.locator(".table-scroller");
  const dims = await scroller.evaluate(el => ({ sh: el.scrollHeight, ch: el.clientHeight }));
  expect(dims.sh).toBeGreaterThan(dims.ch + 100);
  await scroller.evaluate(el => { el.scrollTop = el.scrollHeight; });
  await expect.poll(() => scroller.evaluate(el => el.scrollTop)).toBeGreaterThan(100);
  const offset = await page.evaluate(() => {
    const box = document.querySelector(".table-scroller").getBoundingClientRect();
    const th = document.querySelector(".table-scroller thead th").getBoundingClientRect();
    return th.top - box.top;
  });
  expect(offset).toBeLessThanOrEqual(2); // border width only: the header did not scroll away
});

test("ds-81 overflow hint reflects whether the crumbs overflow", async ({ page, browserName }) => {
  test.skip(browserName !== "chromium", "container scroll-state queries are asserted in Chromium only");
  await page.goto("/play/ds-81/");
  const wrap = page.locator(".crumbs-wrap");
  const hint = page.locator(".crumb-hint");
  expect(await wrap.evaluate(el => el.scrollWidth - el.clientWidth)).toBeGreaterThan(20);
  await expect(hint).toHaveCSS("opacity", "1");
  await wrap.evaluate(el => { el.style.inlineSize = "100%"; });
  expect(await wrap.evaluate(el => el.scrollWidth - el.clientWidth)).toBeLessThanOrEqual(1);
  await expect(hint).toHaveCSS("opacity", "0");
});

test("ds-50 settings pattern is a valid regular expression and rejects bad values", async ({ page }) => {
  const errors = [];
  page.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
  await page.goto("/play/ds-50/");
  const field = page.locator("#profile-url");
  await field.fill("Not Valid!");
  expect(await field.evaluate(el => el.validity.patternMismatch)).toBe(true);
  await field.fill("good-slug-1");
  expect(await field.evaluate(el => el.validity.valid)).toBe(true);
  expect(errors).toEqual([]);
});

test("ds-141 skip link is reachable by Tab and has a real destination", async ({ page }) => {
  await page.goto("/play/ds-141/");
  const link = page.locator(".skip-link");
  await expect(page.locator("#main-content")).toHaveCount(1);
  const offscreen = await link.evaluate(el => el.getBoundingClientRect().bottom);
  expect(offscreen).toBeLessThan(0);
  await page.keyboard.press("Tab");
  await expect(link).toBeFocused();
  await expect.poll(() => link.evaluate(el => el.getBoundingClientRect().top)).toBeGreaterThanOrEqual(0);
  await page.keyboard.press("Enter");
  expect(new URL(page.url()).hash).toBe("#main-content");
  await expect(page.locator("#main-content:target")).toHaveCount(1);
});

for (const [id, focusable] of [["ds-3", ".destination-card a"], ["ds-13", ".destination-card a"], ["ds-25", ".media-card a"]]) {
  test(`${id} keyboard focus produces the same state change as hover`, async ({ page }) => {
    await page.goto(`/play/${id}/`);
    const link = page.locator(focusable).first();
    await expect(link).toHaveCount(1);
    const rest = await page.evaluate(styleSignature);
    await page.keyboard.press("Tab");
    await expect(link).toBeFocused();
    await expect.poll(() => page.evaluate(styleSignature)).not.toBe(rest);
  });
}

test("ds-68 marquee can be paused from the keyboard", async ({ page }) => {
  await page.goto("/play/ds-68/");
  const states = () => page.evaluate(() => document.getAnimations().map(a => a.playState));
  expect(await states()).toContain("running");
  await page.keyboard.press("Tab");
  await expect(page.locator(".marquee a").first()).toBeFocused();
  await expect.poll(async () => (await states()).every(s => s === "paused")).toBe(true);
});

test("ds-112 a text-fragment link paints ::target-text", async ({ page, browserName }) => {
  test.skip(browserName !== "chromium", "::target-text and same-page text fragments are asserted in Chromium only");
  await page.goto("/play/ds-112/");
  const para = page.locator(".stage p").first();
  const before = await para.screenshot();
  await page.getByRole("link", { name: "Follow a text-fragment link" }).click();
  await expect.poll(async () => Buffer.compare(before, await para.screenshot())).not.toBe(0);
});

test("ds-146 overscroll containment keeps the page still while the dialog scrolls", async ({ page, browserName }) => {
  test.skip(browserName !== "chromium", "modal wheel chaining is asserted in Chromium only");
  await page.goto("/play/ds-146/");
  await page.getByRole("button", { name: "Open modal" }).click();
  const dialog = page.locator("dialog.guard-modal");
  await expect(dialog).toHaveJSProperty("open", true);
  const dims = await dialog.evaluate(el => ({ sh: el.scrollHeight, ch: el.clientHeight }));
  expect(dims.sh).toBeGreaterThan(dims.ch + 50);
  const box = await dialog.boundingBox();
  const scrollThrough = async () => {
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    for (let i = 0; i < 10; i++) { await page.mouse.wheel(0, 400); await page.waitForTimeout(40); }
    await page.waitForTimeout(250);
    return page.evaluate(() => ({ page: Math.round(scrollY), dialog: Math.round(document.querySelector("dialog.guard-modal").scrollTop) }));
  };
  const contained = await scrollThrough();
  expect(contained.dialog).toBeGreaterThan(0);
  expect(contained.page).toBe(0);
  // Control: without the spell's containment the same wheel input chains to the page.
  await page.evaluate(() => { document.querySelector("dialog.guard-modal").style.overscrollBehavior = "auto"; });
  const chained = await scrollThrough();
  expect(chained.page).toBeGreaterThan(0);
});

test("every standalone demo loads with no console errors, failed requests or broken images", async ({ page }) => {
  test.setTimeout(240_000);
  const problems = [];
  let current = "";
  page.on("console", m => { if (m.type() === "error") problems.push(`${current}: console ${m.text().slice(0, 120)}`); });
  page.on("pageerror", e => problems.push(`${current}: pageerror ${e.message.slice(0, 120)}`));
  page.on("response", r => { if (r.status() >= 400) problems.push(`${current}: HTTP ${r.status()} ${r.url().slice(-60)}`); });
  for (const { id } of spells) {
    current = id;
    await page.goto(`/play/${id}/`, { waitUntil: "load" });
    const broken = await page.evaluate(() => [...document.images].filter(i => i.complete && i.naturalWidth === 0).length);
    if (broken) problems.push(`${id}: ${broken} broken image(s)`);
  }
  expect(problems).toEqual([]);
});
