/**
 * Live-preview smoke test — one case per spell in the catalogue.
 *
 * Every spell is selected through the real UI (clicking its row in the
 * catalogue) so the assertions cover the whole path: spells.js → hydratePreview
 * → shadow-root sandbox. The checks are deliberately geometric and structural
 * rather than pixel-based, so they stay deterministic across animation timing.
 *
 *     npx playwright test
 */

import fs from "node:fs";
import { test, expect } from "@playwright/test";

const catalogue = JSON.parse(
  fs.readFileSync(new URL("../public/spells.json", import.meta.url), "utf8"),
);

/** Class selectors the spell's own CSS styles, ignoring comments. */
function cssClasses(css) {
  const code = css.replace(/\/\*[\s\S]*?\*\//g, "");
  return [...new Set([...code.matchAll(/(?<![:\w.-])\.([a-zA-Z][\w-]*)/g)].map((m) => m[1]))];
}

/** Previews that are only a `.demo-note` explaining why the effect cannot be
 *  shown on screen (print stylesheets, cross-document view transitions). */
function isExplanatoryOnly(html) {
  return !/<[a-zA-Z]/.test(html.replace(/<p class=["']demo-note["']>[\s\S]*?<\/p>/g, ""));
}

/* Reads the mounted preview out of either the shadow root or document iframe. Runs in the page. */
function readPreview({ id, classes }) {
  const host = document.getElementById(`preview-host-${id}`);
  if (!host) return { mounted: false, error: `no host #preview-host-${id}` };

  const iframe = host.querySelector("iframe.ds-document");
  if (iframe) {
    const doc = iframe.contentDocument || iframe.contentWindow?.document;
    const body = doc ? doc.body : null;
    const elements = body ? [...body.querySelectorAll("*")] : [];
    const painted = elements.filter((el) => {
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    });
    const roots = body
      ? [...body.children].filter(
          (el) =>
            !el.classList.contains("ds-hint") &&
            doc.defaultView?.getComputedStyle(el).display !== "none",
        )
      : [];
    const collapsed = roots
      .filter((el) => el.offsetWidth === 0 || el.offsetHeight === 0)
      .map((el) => `${el.tagName.toLowerCase()}.${el.className || "-"} ` +
        `${el.offsetWidth}×${el.offsetHeight}`);
    return {
      rootCount: roots.length,
      collapsed,
      mounted: true,
      hasStage: true,
      stageWidth: iframe.clientWidth || host.clientWidth || 300,
      stageHeight: iframe.clientHeight || host.clientHeight || 200,
      elementCount: elements.length,
      paintedCount: painted.length,
      paintedTags: painted.slice(0, 8).map((el) => el.tagName.toLowerCase()),
      brokenImages: doc ? [...doc.querySelectorAll("img")]
        .filter((img) => !img.complete || img.naturalWidth === 0)
        .map((img) => (img.getAttribute("src") || "").slice(0, 72)) : [],
      matchedClasses: classes.filter((name) => {
        try {
          return Boolean(doc && doc.querySelector(`.${CSS.escape(name)}`));
        } catch {
          return false;
        }
      }),
      hostWidth: host.clientWidth || 300,
      stageScrollWidth: body ? body.scrollWidth : 0,
    };
  }

  const root = host.shadowRoot;
  if (!root) return { mounted: false, error: `no shadowRoot on #preview-host-${id}` };

  const stage = root.querySelector(".stage");
  const stageBox = stage ? stage.getBoundingClientRect() : null;
  const elements = stage ? [...stage.querySelectorAll("*")] : [];
  const painted = elements.filter((el) => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  });

  const roots = stage
    ? [...stage.children].filter(
        (el) =>
          !el.classList.contains("ds-hint") &&
          getComputedStyle(el).display !== "none",
      )
    : [];
  const collapsed = roots
    .filter((el) => el.offsetWidth === 0 || el.offsetHeight === 0)
    .map((el) => `${el.tagName.toLowerCase()}.${el.className || "-"} ` +
      `${el.offsetWidth}×${el.offsetHeight}`);

  return {
    rootCount: roots.length,
    collapsed,
    mounted: true,
    hasStage: Boolean(stage),
    stageWidth: stageBox ? stageBox.width : 0,
    stageHeight: stageBox ? stageBox.height : 0,
    elementCount: elements.length,
    paintedCount: painted.length,
    paintedTags: painted.slice(0, 8).map((el) => el.tagName.toLowerCase()),
    brokenImages: [...root.querySelectorAll("img")]
      .filter((img) => !img.complete || img.naturalWidth === 0)
      .map((img) => (img.getAttribute("src") || "").slice(0, 72)),
    matchedClasses: classes.filter((name) => {
      try {
        return Boolean(root.querySelector(`.${CSS.escape(name)}`));
      } catch {
        return false;
      }
    }),
    hostWidth: host.clientWidth,
    stageScrollWidth: stage ? stage.scrollWidth : 0,
  };
}

/* Parses the spell's CSS on its own, away from the preview tokens the sandbox
   injects alongside it, so a wholesale parse failure cannot hide behind them. */
function countOwnRules(css) {
  const sheet = new CSSStyleSheet();
  try {
    sheet.replaceSync(css);
  } catch {
    return -1;
  }
  return sheet.cssRules.length;
}

test.describe("spell previews", () => {
  let page;
  let failures = [];

  test.beforeAll(async ({ browser }) => {
    failures = [];
    page = await browser.newPage();
    page.on("pageerror", (error) => failures.push(`pageerror: ${error.message}`));
    page.on("console", (msg) => {
      if (msg.type() === "error") failures.push(`console.error: ${msg.text()}`);
    });
    await page.goto("/classic/");
    await expect(page.locator(".row").first()).toBeVisible();
  });

  test.beforeEach(() => {
    failures = [];
  });

  test.afterAll(async () => {
    await page?.close();
  });

  for (const spell of catalogue.spells) {
    test(`${spell.id} — ${spell.title}`, async () => {
      const row = page.locator(`.row[data-id="${spell.id}"]`);
      await expect(row).toHaveCount(1);

      await row.locator(".row__hit").click();
      // A heading remains in the DOM even when its popover is closed.
      await expect(page.locator(`#drawer-${spell.id}:popover-open`)).toHaveCount(1);
      await expect(page.locator(`#drawer-title-${spell.id}`)).toHaveText(spell.title);

      await page.waitForFunction((id) => {
        const host = document.getElementById(`preview-host-${id}`);
        if (!host) return false;
        const iframe = host.querySelector("iframe.ds-document");
        if (iframe) {
          const doc = iframe.contentDocument || iframe.contentWindow?.document;
          return (
            Boolean(doc?.body) &&
            doc.body.children.length > 0 &&
            [...doc.querySelectorAll("img")].every((img) => img.complete)
          );
        }
        const root = host.shadowRoot;
        return Boolean(root?.querySelector(".stage")) && [...root.querySelectorAll("img")].every((img) => img.complete);
      }, spell.id);

      const classes = cssClasses(spell.previewCss);
      // A mounted declarative shadow root may still be waiting for its first
      // layout pass under CI load. Wait for a stable painted result, not just DOM.
      try {
        await expect.poll(async () => {
          const current = await page.evaluate(readPreview, { id: spell.id, classes });
          return current.mounted && current.hasStage &&
            current.stageWidth > 0 && current.stageHeight > 0 &&
            current.paintedCount > 0 && current.collapsed.length === 0;
        }, { timeout: 12000, message: `${spell.id}: preview did not reach a nonzero layout` }).toBe(true);
      } catch (error) {
        const snapshot = await page.evaluate(readPreview, { id: spell.id, classes });
        const state = await page.locator(`#drawer-${spell.id}`).evaluate((el) => ({
          open: el.matches(':popover-open'),
          display: getComputedStyle(el).display,
          transform: getComputedStyle(el).transform,
          reduced: matchMedia('(prefers-reduced-motion: reduce)').matches,
        }));
        throw new Error(`${spell.id}: preview diagnosis ${JSON.stringify({ snapshot, state })}`, { cause: error });
      }
      const report = await page.evaluate(readPreview, { id: spell.id, classes });

      expect(report.mounted, `${spell.id}: preview never attached a shadow root`).toBe(true);
      expect(report.hasStage, `${spell.id}: preview has no .stage`).toBe(true);
      // Animated and lazy preview geometry may change between independent reads;
      // the preceding expect.poll verified nonzero painted layout and top-level
      // elements together in one snapshot. Retain only stable structure here.
      expect(report.elementCount, `${spell.id}: stage rendered no elements`).toBeGreaterThan(0);
      expect(
        report.rootCount,
        `${spell.id}: preview has no visible top-level element`,
      ).toBeGreaterThan(0);
      // The expect.poll above already verifies every visible top-level box has
      // nonzero geometry. A second immediate snapshot is racy for lazy iframe
      // previews and animated fixed-position scroll indicators.

      expect(report.brokenImages, `${spell.id}: images failed to load`).toEqual([]);

      const rules = await page.evaluate(countOwnRules, spell.previewCss);
      expect(rules, `${spell.id}: previewCss threw while parsing`).not.toBe(-1);
      expect(rules, `${spell.id}: previewCss produced no CSS rules at all`).toBeGreaterThan(0);

      if (classes.length && !isExplanatoryOnly(spell.previewHtml)) {
        expect(
          report.matchedClasses.length,
          `${spell.id}: none of the spell's own classes (${classes.join(", ")}) match markup`,
        ).toBeGreaterThan(0);
      }

      // Document previews may own keyboard focus. Return it to the parent
      // popover so Escape tests the drawer rather than the iframe context.
      await page.locator(`#drawer-${spell.id} .drawer__close`).focus();
      await page.keyboard.press("Escape");
      // Wait for both native closure and the asynchronous toggle handler before
      // opening the next drawer; do not let stale popover state leak across tests.
      await expect(page.locator(`#drawer-${spell.id}:popover-open`)).toHaveCount(0);
      await expect(page.locator(`#drawer-${spell.id}`)).toBeHidden();
      await expect(page).not.toHaveURL(new RegExp(`#${spell.id}$`));
      expect(failures, `${spell.id}: errors while rendering the preview`).toEqual([]);
    });
  }
});
