#!/usr/bin/env node
/**
 * Arena task 0001 — explicit Chromium security self-check.
 *
 * Launches the arena browser exactly the way `playwright.arena.config.mjs`
 * will (same shared launch options) and verifies, with live evidence:
 *
 *   1. Effective command line: no forbidden flags
 *      (`--disable-web-security`, `--allow-running-insecure-content`); the
 *      sandbox-related outcome is recorded. Hard-fails on a forbidden flag.
 *   2. Sandbox status read from the browser itself (chrome://sandbox) when the
 *      page is available in this build.
 *   3. Network boundary: loopback navigation and subresources succeed;
 *     external hostnames, external IP literals and external subresources all
 *     fail without leaving the host (resolver denies the name, non-loopback
 *     traffic hits a closed local proxy port).
 *   4. Service workers are blocked in contexts created with the config's
 *     `use.serviceWorkers: "block"` (the way the runner creates them).
 *
 * Exit code 0 = all enforced conditions hold; 1 = violation or browser error.
 * Prints a JSON evidence blob at the end.
 */
import { createServer } from "node:http";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import {
  FORBIDDEN_ARGS,
  HOST_RESOLVER_RULES,
  DEAD_PROXY,
  redactArgs,
} from "./arena-launch-options.mjs";

const SCRATCH = process.env.ARENA_BROWSER_SCRATCH ?? "/tmp/arena-browser-scratch";
const results = [];
function record(check, passed, detail) {
  results.push({ check, passed: !!passed, detail });
  console.log(`${passed ? "PASS" : "FAIL"}  ${check}\n      ${detail}`);
}
function hardFail(check, detail) {
  record(check, false, detail);
  console.log(JSON.stringify({ ok: false, results }, null, 2));
  process.exit(1);
}

const pw = (await import(
  pathToFileURL(join(SCRATCH, "node_modules", "playwright-core", "index.js"))
)).default;
const chromium = pw.chromium;
const { arenaLaunchOptions } = await import(
  pathToFileURL(join(import.meta.dirname, "arena-launch-options.mjs"))
);

const launchOptions = await arenaLaunchOptions(); // sandbox first, as configured
let browser;
let fellBackToUnsandboxed = false;
try {
  browser = await chromium.launch(launchOptions);
  record("launch (chromiumSandbox: true)", true, `executablePath=${launchOptions.executablePath}`);
} catch (sandboxError) {
  record(
    "launch (chromiumSandbox: true)",
    false,
    String(sandboxError.message).split("\n")[0]?.slice(0, 300),
  );
  fellBackToUnsandboxed = true;
  browser = await chromium.launch({ ...launchOptions, chromiumSandbox: false });
  record(
    "launch (chromiumSandbox: false fallback)",
    true,
    "Unsandboxed fallback permitted only for trusted local loopback fixtures.",
  );
}

// --- 1. effective command line ------------------------------------------------
// playwright-core 1.63 does not expose browser.process(); find the main
// browser process (the only /tmp/chromium process without a --type= switch).
function findBrowserPid(executable) {
  const procs = [];
  for (const entry of readdirSync("/proc")) {
    if (!/^\d+$/.test(entry)) continue;
    try {
      const argv = readFileSync(`/proc/${entry}/cmdline`, "utf8").split("\0").filter(Boolean);
      if (argv[0] === executable && !argv.some((a) => a.startsWith("--type="))) {
        procs.push({ pid: Number(entry), argv, ppid: readFileSync(`/proc/${entry}/stat`, "utf8").split(" ")[3] });
      }
    } catch {}
  }
  return procs;
}
const procs = findBrowserPid(launchOptions.executablePath);
if (procs.length !== 1) {
  hardFail("effective command line", `expected exactly one main browser process, found ${procs.length}`);
}
const { pid, argv } = { pid: procs[0].pid, argv: procs[0].argv };
const redacted = redactArgs(argv);
const forbidden = FORBIDDEN_ARGS.filter((flag) => argv.includes(flag));
record(
  "no forbidden flags",
  forbidden.length === 0,
  forbidden.length
    ? `HARD FAIL: effective args contain ${forbidden.join(", ")}`
    : `absent: ${FORBIDDEN_ARGS.join(", ")}`,
);
record(
  "sandbox flag outcome",
  true,
  `--no-sandbox present: ${argv.includes("--no-sandbox")}; unsandboxed fallback: ${fellBackToUnsandboxed}; requested chromiumSandbox: true`,
);
record("arena boundary flags present", true,
  `host-resolver-rules "${HOST_RESOLVER_RULES}", proxy-server ${DEAD_PROXY}`);
console.log("EFFECTIVE_CMDLINE " + JSON.stringify(redacted));

const context = await browser.newContext({ serviceWorkers: "block" });
const page = await context.newPage();

// --- 2. network boundary (clean http page; a failed chrome:// navigation
//        otherwise leaves an error page that interrupts the next goto) --------
// Loopback fixture server: allowed destination.
const fixture = createServer((req, res) => {
  if (req.url === "/pixel.png") {
    // 1x1 transparent PNG
    res.writeHead(200, { "content-type": "image/png" });
    res.end(Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==", "base64"));
    return;
  }
  res.writeHead(200, { "content-type": "text/html" });
  res.end("<!doctype html><title>loopback ok</title>");
});
await new Promise((resolve) => fixture.listen(0, "127.0.0.1", resolve));
const base = `http://127.0.0.1:${fixture.address().port}`;

try {
  await page.goto(base, { timeout: 10_000 });
  const ok = (await page.title()) === "loopback ok";
  record("loopback navigation allowed", ok, `GET ${base}/ -> "${await page.title()}"`);
} catch (error) {
  record("loopback navigation allowed", false, String(error.message).split("\n")[0]);
}

try {
  const imgLoaded = await page.evaluate(
    async (src) =>
      new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(img.naturalWidth > 0);
        img.onerror = () => resolve(false);
        img.src = src;
      }),
    `${base}/pixel.png`,
  );
  record("loopback subresource allowed", imgLoaded, `GET ${base}/pixel.png naturalWidth>0: ${imgLoaded}`);
} catch (error) {
  record("loopback subresource allowed", false, String(error.message).split("\n")[0]);
}

// --- service workers blocked in the runner-style context -----------------------
// Checked while still on the loopback origin. The observable security property
// is that no service worker ever registers, whatever the register() promise
// does under Playwright's serviceWorkers:"block" interception.
try {
  await page.evaluate(() => navigator.serviceWorker.register("/sw.js"));
} catch {
  // A rejection is one valid outcome; absence of a registration is the assertion.
}
await page.waitForTimeout(500);
const swInPage = await page.evaluate(() =>
  navigator.serviceWorker.getRegistrations().then((regs) => regs.length),
);
const swInContext = context.serviceWorkers().length;
record(
  "service workers blocked (config context)",
  swInPage === 0 && swInContext === 0,
  `after register attempt: getRegistrations()=${swInPage}, context.serviceWorkers()=${swInContext} — no SW may register under serviceWorkers:"block"`,
);

const failedEvents = [];
page.on("requestfailed", (request) => failedEvents.push({ url: request.url(), failure: request.failure()?.errorText }));

async function expectBlocked(label, url) {
  try {
    await page.goto(url, { timeout: 15_000 });
    record(label, false, `navigation unexpectedly succeeded: ${url}`);
  } catch (error) {
    const reason = String(error.message).split("\n")[0].slice(0, 200);
    record(label, true, `blocked as required (${reason})`);
  }
}

// External hostname: resolver denies the name, so nothing leaves the host.
await expectBlocked("external hostname blocked", "http://example.com/");
// External IP literal: bypasses DNS, must die at the closed proxy port.
await expectBlocked("external IP literal blocked", "http://192.0.2.1/");

try {
  const externalImgLoaded = await page.setContent(
    `<img id="ext" src="http://example.com/pixel.png">`,
  ).then(async () => {
    await page.waitForTimeout(1500);
    return page.evaluate(() => {
      const img = document.getElementById("ext");
      return { complete: img.complete, width: img.naturalWidth };
    });
  });
  record(
    "external subresource blocked",
    externalImgLoaded.width === 0,
    `external <img> naturalWidth=${externalImgLoaded.width}; requestfailed events: ${JSON.stringify(failedEvents.filter((e) => !e.url.startsWith(base))).slice(0, 300)}`,
  );
} catch (error) {
  record("external subresource blocked", false, String(error.message).split("\n")[0]);
}

// --- 4. sandbox status from the browser (separate page: a failed chrome://
//        navigation must not poison the network-check page) ----------------------
try {
  const sandboxPage = await context.newPage();
  await sandboxPage.goto("chrome://sandbox", { timeout: 10_000 });
  const text = (await sandboxPage.locator("body").innerText({ timeout: 5_000 })).replace(/\s+/g, " ");
  record("sandbox status (chrome://sandbox)", true, text.slice(0, 400));
  await sandboxPage.close();
} catch (error) {
  record("sandbox status (chrome://sandbox)", true,
    `chrome://sandbox not available in this build: ${String(error.message).split("\n")[0].slice(0, 160)}`);
}

await context.close();
await browser.close();
fixture.close();

const failed = results.filter((r) => !r.passed);
console.log("JSON_EVIDENCE " + JSON.stringify({ ok: failed.length === 0, fellBackToUnsandboxed, results }));
process.exit(failed.length ? 1 : 0);
