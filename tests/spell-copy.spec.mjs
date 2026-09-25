import { test, expect } from "@playwright/test";

test.describe("individual documentation source without JavaScript", () => {
  test.use({ javaScriptEnabled: false, reducedMotion: "reduce" });

  test("native source link remains usable and optional copy is hidden", async ({ page, request }) => {
    await page.goto("/spells/ds-1/");
    await expect(page.getByRole("link", { name: /View integration source/ }))
      .toHaveAttribute("href", "/bundle/ds-1.txt");
    await expect(page.locator("[data-copy-bundle]")).toBeHidden();
    const source = await (await request.get("/bundle/ds-1.txt")).text();
    expect(source).toContain("Design Spells ds-1: integration source");
  });
});

test.describe("individual documentation optional copy", () => {
  test.use({ reducedMotion: "reduce" });

  test("missing clipboard leaves the native link and no inert button", async ({ page }) => {
    await page.addInitScript(() => {
      Object.defineProperty(navigator, "clipboard", { configurable: true, value: undefined });
    });
    await page.goto("/spells/ds-1/");
    await expect(page.getByRole("link", { name: /View integration source/ })).toBeVisible();
    await expect(page.locator("[data-copy-bundle]")).toBeHidden();
  });

  test("copies exactly the published integration source and announces success", async ({ page, request }) => {
    await page.addInitScript(() => {
      Object.defineProperty(navigator, "clipboard", {
        configurable: true,
        value: { writeText: async (source) => { window.__copiedSpellSource = source; } },
      });
    });
    await page.goto("/spells/ds-1/");
    await page.getByRole("button", { name: "Copy integration bundle" }).click();
    await expect(page.getByRole("status")).toContainText("Integration source copied for ds-1");
    const copied = await page.evaluate(() => window.__copiedSpellSource);
    expect(copied).toBe(await (await request.get("/bundle/ds-1.txt")).text());
    expect(copied).toContain("<!doctype html>");
    expect(copied).not.toContain("box-sizing: border-box");
  });

  test("failed fetch never touches clipboard or claims copy succeeded", async ({ page }) => {
    await page.addInitScript(() => {
      Object.defineProperty(navigator, "clipboard", {
        configurable: true,
        value: { writeText: async () => { window.__copiedSpellSource = true; } },
      });
    });
    await page.route("**/bundle/ds-1.txt", route => route.fulfill({ status: 503, body: "unavailable" }));
    await page.goto("/spells/ds-1/");
    await page.getByRole("button", { name: "Copy integration bundle" }).click();
    await expect(page.getByRole("status")).toContainText("Copy failed");
    await expect(page.getByRole("link", { name: /View integration source/ })).toBeVisible();
    expect(await page.evaluate(() => window.__copiedSpellSource)).toBeUndefined();
  });

  test("rejected clipboard write keeps the fallback link", async ({ page }) => {
    await page.addInitScript(() => {
      Object.defineProperty(navigator, "clipboard", {
        configurable: true,
        value: { writeText: async () => { throw new Error("denied"); } },
      });
    });
    await page.goto("/spells/ds-1/");
    await page.getByRole("button", { name: "Copy integration bundle" }).click();
    await expect(page.getByRole("status")).toContainText("Copy failed");
    await expect(page.getByRole("link", { name: /View integration source/ }))
      .toHaveAttribute("href", "/bundle/ds-1.txt");
  });

  test("document-level effects have source and full demo links, but no one-file copy", async ({ page }) => {
    await page.goto("/spells/ds-14/");
    await expect(page.getByRole("link", { name: /View integration source/ }))
      .toHaveAttribute("href", "/bundle/ds-14.txt");
    await expect(page.locator("[data-copy-bundle]")).toHaveCount(0);
    await expect(page.getByRole("link", { name: /page B/ }))
      .toHaveAttribute("href", "/download/ds-14-next.html");
  });
});

test.describe("clean integration documents in a browser", () => {
  test.use({ javaScriptEnabled: false, reducedMotion: "reduce" });

  for (const sid of ["ds-1", "ds-43", "ds-120"]) {
    test(sid + " parses without catalogue styles or scripts", async ({ page, request }) => {
      const response = await request.get("/bundle/" + sid + ".txt");
      expect(response.status()).toBe(200);
      const source = await response.text();
      await page.setContent(source, { waitUntil: "domcontentloaded" });
      expect(await page.evaluate(() => document.doctype?.name)).toBe("html");
      await expect(page.locator("html > head > style")).toHaveCount(1);
      await expect(page.locator("script, link[rel=stylesheet], iframe, .site-head")).toHaveCount(0);
      expect(await page.locator("style").textContent()).not.toContain("box-sizing:border-box");
      expect(await page.locator("body").evaluate(el => el.children.length)).toBeGreaterThan(0);
      if (sid === "ds-43") {
        expect(source).toContain("html { container-type: scroll-state; overflow: auto; }");
      } else {
        expect(source).not.toContain("html { container-type: scroll-state; overflow: auto; }");
      }
    });
  }
});
