/**
 * Isolated demo smoke tests — one case per spell.
 *
 * The lightweight catalogue now links to real /play/<id>/ documents. Test those
 * published artifacts directly rather than keeping the 4.6 MB legacy /classic/
 * explorer and all of its preview sandboxes alive for 150 sequential cases.
 *
 * /classic/ remains covered by the drawer/accessibility suites and by the small
 * representative smoke test at the end of this file.
 */

import fs from "node:fs";
import { test, expect } from "@playwright/test";

const catalogue = JSON.parse(
  fs.readFileSync(new URL("../public/spells.json", import.meta.url), "utf8"),
);

function cssClasses(css) {
  const code = css.replace(/\/\*[\s\S]*?\*\//g, "");
  return [...new Set([...code.matchAll(/(?<![:\w.-])\.([a-zA-Z][\w-]*)/g)].map((m) => m[1]))];
}

function isExplanatoryOnly(html) {
  return !/<[a-zA-Z]/.test(html.replace(/<p class=["']demo-note["']>[\s\S]*?<\/p>/g, ""));
}

function countOwnRules(css) {
  const sheet = new CSSStyleSheet();
  try {
    sheet.replaceSync(css);
  } catch {
    return -1;
  }
  return sheet.cssRules.length;
}

test.describe("isolated spell demos", () => {
  for (const spell of catalogue.spells) {
    test(`${spell.id} — ${spell.title}`, async ({ page }) => {
      const failures = [];
      page.on("pageerror", (error) => failures.push(`pageerror: ${error.message}`));
      page.on("console", (msg) => {
        if (msg.type() === "error") failures.push(`console.error: ${msg.text()}`);
      });

      await page.goto(`/play/${spell.id}/`, { waitUntil: "domcontentloaded" });

      await expect(page.locator("script"), `${spell.id}: demo must stay zero-script`).toHaveCount(0);
      await expect(page.locator("body")).toBeVisible();

      const geometry = await page.evaluate(() => {
        const stage = document.querySelector(".stage");
        const roots = stage
          ? [...stage.children].filter((el) => getComputedStyle(el).display !== "none")
          : [...document.body.children].filter(
              (el) => !el.classList.contains("demo-hint") && getComputedStyle(el).display !== "none",
            );
        const painted = [...document.body.querySelectorAll("*")].filter((el) => {
          const r = el.getBoundingClientRect();
          return r.width > 0 && r.height > 0;
        });
        return {
          bodyWidth: document.body.getBoundingClientRect().width,
          bodyHeight: document.body.getBoundingClientRect().height,
          stageWidth: stage?.getBoundingClientRect().width ?? document.body.getBoundingClientRect().width,
          stageHeight: stage?.getBoundingClientRect().height ?? document.body.getBoundingClientRect().height,
          roots: roots.map((el) => ({
            tag: el.tagName.toLowerCase(),
            display: getComputedStyle(el).display,
            width: el.getBoundingClientRect().width,
            height: el.getBoundingClientRect().height,
          })),
          paintedCount: painted.length,
          brokenImages: [...document.images]
            .filter((img) => !img.complete || img.naturalWidth === 0)
            .map((img) => img.getAttribute("src") || ""),
        };
      });

      expect(geometry.bodyWidth, `${spell.id}: body has no width`).toBeGreaterThan(0);
      expect(geometry.bodyHeight, `${spell.id}: body has no height`).toBeGreaterThan(0);
      expect(geometry.stageWidth, `${spell.id}: stage has no width`).toBeGreaterThan(0);
      expect(geometry.stageHeight, `${spell.id}: stage has no height`).toBeGreaterThan(0);
      expect(geometry.paintedCount, `${spell.id}: demo paints no elements`).toBeGreaterThan(0);
      expect(geometry.roots.length, `${spell.id}: demo has no visible top-level content`).toBeGreaterThan(0);
      expect(geometry.brokenImages, `${spell.id}: images failed to load`).toEqual([]);

      const rules = await page.evaluate(countOwnRules, spell.css);
      expect(rules, `${spell.id}: source CSS threw while parsing`).not.toBe(-1);
      expect(rules, `${spell.id}: source CSS produced no CSS rules`).toBeGreaterThan(0);

      const classes = cssClasses(spell.css);
      if (classes.length && !isExplanatoryOnly(spell.previewHtml)) {
        const matched = await page.evaluate((names) => names.filter((name) => {
          try {
            return Boolean(document.querySelector(`.${CSS.escape(name)}`));
          } catch {
            return false;
          }
        }), classes);
        expect(
          matched.length,
          `${spell.id}: none of the spell's own classes (${classes.join(", ")}) match demo markup`,
        ).toBeGreaterThan(0);
      }

      expect(failures, `${spell.id}: errors while rendering the isolated demo`).toEqual([]);
    });
  }
});

test("classic explorer still mounts a representative preview", async ({ page }) => {
  await page.goto("/classic/");
  const row = page.locator('.row[data-id="ds-1"]');
  await expect(row).toHaveCount(1);
  await row.locator(".row__hit").click();
  await expect(page.locator("#drawer-title-ds-1")).toHaveText("Shimmer on primary buttons");
  const host = page.locator("#preview-host-ds-1");
  await expect.poll(async () => host.evaluate((el) => Boolean(el.shadowRoot?.querySelector(".stage"))), {
    timeout: 10000,
  }).toBe(true);
  await page.keyboard.press("Escape");
  await expect(page.locator("#drawer-ds-1")).toBeHidden();
});
