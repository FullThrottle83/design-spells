/**
 * Drawer description rendering.
 *
 * 67 of the 145 descriptions carry inline markdown straight from the README —
 * `code` spans and **bold** runs — and 17 of those code spans contain literal
 * HTML tags (`<details>`, `<dialog>`, `<summary>`). The drawer renders them
 * through inlineMd() in app.js, which escapes every source character before
 * emitting any tag of its own.
 *
 * That makes this both a rendering check and a safety check, so it asserts
 * both: the markers become elements, and nothing in the source text ever does.
 */

import fs from "node:fs";
import { test, expect } from "@playwright/test";

const catalogue = JSON.parse(
  fs.readFileSync(new URL("../public/spells.json", import.meta.url), "utf8"),
);

const hasMarkdown = (s) => /`[^`]+`|\*\*[^*]+\*\*/.test(s.description || "");
const marked = catalogue.spells.filter(hasMarkdown);

/** The text inside each `backtick span`, in source order. */
const codeSpans = (text) => [...text.matchAll(/`([^`]+)`/g)].map((m) => m[1]);
/** The text inside each **bold run**, in source order. */
const boldRuns = (text) =>
  [...text.matchAll(/\*\*([^*]+(?:\*(?!\*)[^*]*)*)\*\*/g)].map((m) => m[1]);

test.describe("drawer descriptions", () => {
  let page;
  const failures = [];

  test.beforeAll(async ({ browser }) => {
    // openDrawer() morphs the row into the drawer with a View Transition, whose
    // snapshot overlay keeps intercepting pointer events well past the point the
    // drawer itself reports closed — 67 open/close cycles cannot outrun it.
    // supportsViewTransition() in app.js already opts out under reduced motion,
    // so this is a path the app genuinely supports, not a test-only bypass, and
    // populateDrawer() — the thing under test — runs identically either way.
    page = await browser.newPage({ reducedMotion: "reduce" });
    page.on("pageerror", (error) => failures.push(`pageerror: ${error.message}`));
    page.on("console", (msg) => {
      if (msg.type() === "error") failures.push(`console.error: ${msg.text()}`);
    });
    await page.goto("/classic/");
    await expect(page.locator(".row").first()).toBeVisible();
  });

  test.afterAll(async () => {
    await page?.close();
  });

  test(`renders inline markdown as elements for all ${marked.length} spells that carry it`, async () => {
    // This case opens and closes every marked spell, including document
    // previews. Scale the budget with the catalogue instead of capping all
    // 73 current interactions at one minute on slower CI machines.
    test.setTimeout(marked.length * 2000);
    const problems = [];

    for (const spell of marked) {
      const row = page.locator(`.row[data-id="${spell.id}"]`);
      await row.locator(".row__hit").click();
      await expect(page.locator(`#drawer-title-${spell.id}`)).toHaveText(spell.title);

      const seen = await page.evaluate((id) => {
        const el = document.querySelector(`#drawer-${id} .drawer__desc`);
        return {
          text: el ? el.textContent : "",
          tags: el ? [...el.querySelectorAll("*")].map((n) => n.tagName) : [],
          codes: el ? [...el.querySelectorAll("code")].map((n) => n.textContent) : [],
          bolds: el ? [...el.querySelectorAll("strong")].map((n) => n.textContent) : [],
        };
      }, spell.id);

      const note = (msg) => problems.push(`${spell.id}: ${msg}`);

      // The markers themselves must be gone — that was the visible bug.
      if (seen.text.includes("`")) note(`literal backtick still shown — "${seen.text.slice(0, 80)}"`);
      if (seen.text.includes("**")) note(`literal ** still shown — "${seen.text.slice(0, 80)}"`);

      // Nothing but the wrappers inlineMd emits itself may become an element.
      const stray = seen.tags.filter((t) => t !== "CODE" && t !== "STRONG");
      if (stray.length) note(`source text produced elements: ${[...new Set(stray)].join(", ")}`);

      // And the escaped text has to survive intact, not be swallowed.
      const wantCodes = codeSpans(spell.description);
      if (seen.codes.join(" ") !== wantCodes.join(" ")) {
        note(`code spans ${JSON.stringify(seen.codes)} != ${JSON.stringify(wantCodes)}`);
      }
      const wantBolds = boldRuns(spell.description);
      if (seen.bolds.join(" ") !== wantBolds.join(" ")) {
        note(`bold runs ${JSON.stringify(seen.bolds)} != ${JSON.stringify(wantBolds)}`);
      }

      // The test verifies copy/markup across 73 panels. Activate the native
      // close button via keyboard, which also exercises the zero-JS pathway
      // without a pointer hit-test against animated preview content.
      await page.locator(`#drawer-${spell.id} .drawer__close`).focus();
      await page.keyboard.press("Enter");
      try {
        await expect(page.locator(`#drawer-${spell.id}`)).toBeHidden();
      } catch (error) {
        const state = await page.locator(`#drawer-${spell.id}`).evaluate((el) => ({
          open: el.matches(':popover-open'),
          display: getComputedStyle(el).display,
          transform: getComputedStyle(el).transform,
          reduced: matchMedia('(prefers-reduced-motion: reduce)').matches,
          hash: location.hash,
        }));
        throw new Error(`${spell.id}: drawer close diagnosis ${JSON.stringify(state)}`, { cause: error });
      }
    }

    expect(problems, "drawer descriptions rendered incorrectly").toEqual([]);
    expect(failures, "errors while opening drawers").toEqual([]);
  });

  test("spells without markdown still show their description", async () => {
    const plain = catalogue.spells.find((s) => s.description && !hasMarkdown(s));
    test.skip(!plain, "every description carries markdown");

    await page.locator(`.row[data-id="${plain.id}"] .row__hit`).click();
    await expect(page.locator(`#drawer-title-${plain.id}`)).toHaveText(plain.title);
    await expect(page.locator(`#drawer-${plain.id} .drawer__desc`)).toHaveText(plain.description);
    await page.locator(`#drawer-${plain.id} .drawer__close`).click();
    await expect(page.locator(`#drawer-${plain.id}`)).toBeHidden();
  });
});
