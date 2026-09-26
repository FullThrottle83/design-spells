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

// Synthetic canary demonstrates that the browser does not inherit the agent's
// entire environment. Never use an actual token as test data.
const CANARY_NAME = "ARENA_BROWSER_ENV_CANARY";
const originalCanary = process.env[CANARY_NAME];
process.env[CANARY_NAME] = "synthetic-only-do-not-forward";
const launchOptions = await arenaLaunchOptions(); // sandbox first, as configured
let browser;
const fellBackToUnsandboxed = false; // never downgrade the required sandbox
try {
  browser = await chromium.launch(launchOptions);
  record("launch (chromiumSandbox: true)", true, `executablePath=${launchOptions.executablePath}`);
} catch (sandboxError) {
  hardFail("launch (chromiumSandbox: true)",
    String(sandboxError.message).split("\n")[0]?.slice(0, 300));
}
if (originalCanary === undefined) delete process.env[CANARY_NAME];
else process.env[CANARY_NAME] = originalCanary;

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
if (forbidden.length) {
  hardFail("no forbidden flags", `effective args contain ${forbidden.join(", ")}`);
}
record("no forbidden flags", true, `absent: ${FORBIDDEN_ARGS.join(", ")}`);
const sandboxFlagsOk = !argv.includes("--no-sandbox") && !fellBackToUnsandboxed;
record(
  "sandbox flag outcome",
  sandboxFlagsOk,
  `--no-sandbox present: ${argv.includes("--no-sandbox")}; unsandboxed fallback: ${fellBackToUnsandboxed}; requested chromiumSandbox: true`,
);
const boundaryFlagsOk =
  argv.includes(`--host-resolver-rules=${HOST_RESOLVER_RULES}`) &&
  argv.includes(`--proxy-server=${DEAD_PROXY}`);
if (!boundaryFlagsOk) hardFail("arena boundary flags present", "required launch flags absent from effective argv");
record("arena boundary flags present", true, "host resolver and dead proxy present in effective argv");
console.log("EFFECTIVE_CMDLINE " + JSON.stringify(redacted));

// Check the *actual spawned process*, not merely the configuration object.
// Log names only; never read out or print environment values.
const browserEnvNames = readFileSync(`/proc/${pid}/environ`, "utf8")
  .split("\0").filter(Boolean).map((entry) => entry.split("=", 1)[0]);
const declaredEnvNames = new Set(Object.keys(launchOptions.env ?? {}));
const unexpectedEnvNames = browserEnvNames.filter((key) => !declaredEnvNames.has(key));
const environmentIsolated =
  unexpectedEnvNames.length === 0 &&
  !browserEnvNames.includes(CANARY_NAME) &&
  !browserEnvNames.some((key) => /(?:^|_)(?:TOKEN|SECRET|PASSWORD|CREDENTIAL|API_KEY|PRIVATE_KEY)(?:$|_)/i.test(key));
if (!environmentIsolated) {
  hardFail("browser environment isolation", `unexpected variable names: ${unexpectedEnvNames.join(", ") || "(none)"}; synthetic canary present: ${browserEnvNames.includes(CANARY_NAME)}`);
}
record("browser environment isolation", true,
  `only ${browserEnvNames.length} explicit allowlisted variables; synthetic canary and credential variables absent`);

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
  console.log("NOT_TESTED sandbox status (chrome://sandbox): " +
    String(error.message).split("\n")[0].slice(0, 160));
}

await context.close();
await browser.close();
fixture.close();

const failed = results.filter((r) => !r.passed);
console.log("JSON_EVIDENCE " + JSON.stringify({ ok: failed.length === 0, fellBackToUnsandboxed, results }));
process.exit(failed.length ? 1 : 0);
