#!/usr/bin/env node
/**
 * Arena task 0001 — bounded browser bootstrap.
 *
 * Installs the exact versions the task permits into a session-local scratch
 * directory (never inside the repo, never committed) and extracts the
 * Chromium binary plus its bundled AL2023 shared libraries.
 *
 *   node scripts/arena-browser/bootstrap.mjs
 *   node scripts/arena-browser/bootstrap.mjs --json   # machine-readable summary
 *
 * No apt, no root, no system installs: everything lands under
 * ARENA_BROWSER_SCRATCH (default /tmp/arena-browser-scratch) and /tmp.
 */
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import {
  PLAYWRIGHT_CORE_VERSION,
  SPARTICUZ_CHROMIUM_VERSION,
  scratchDir,
} from "./arena-launch-options.mjs";

const scratch = scratchDir();
const json = process.argv.includes("--json");
const scratchPkgs = join(scratch, "node_modules");

function pkgVersion(pkg) {
  try {
    return JSON.parse(readFileSync(join(scratchPkgs, pkg, "package.json"), "utf8")).version;
  } catch {
    return null;
  }
}

const coreVersion = pkgVersion("playwright-core");
const sparticuzVersion = pkgVersion("@sparticuz/chromium");
const needsInstall =
  coreVersion !== PLAYWRIGHT_CORE_VERSION || sparticuzVersion !== SPARTICUZ_CHROMIUM_VERSION;

if (needsInstall) {
  execFileSync(
    "npm",
    [
      "install",
      `playwright-core@${PLAYWRIGHT_CORE_VERSION}`,
      `@sparticuz/chromium@${SPARTICUZ_CHROMIUM_VERSION}`,
      "--no-audit",
      "--no-fund",
      "--loglevel=error",
      "--prefix",
      scratch,
    ],
    { stdio: json ? "ignore" : "inherit" },
  );
}

const { arenaLaunchOptions } = await import(pathToFileURL(join(import.meta.dirname, "arena-launch-options.mjs")));
const launchOptions = await arenaLaunchOptions();

const summary = {
  scratchDir: scratch,
  playwrightCore: PLAYWRIGHT_CORE_VERSION,
  sparticuzChromium: SPARTICUZ_CHROMIUM_VERSION,
  executablePath: launchOptions.executablePath,
  chromiumSandbox: launchOptions.chromiumSandbox,
  args: launchOptions.args,
  installedFresh: needsInstall,
};

if (json) {
  console.log(JSON.stringify(summary, null, 2));
} else {
  console.log(`scratch:            ${scratch}`);
  console.log(`playwright-core:    ${PLAYWRIGHT_CORE_VERSION}`);
  console.log(`@sparticuz/chromium:${SPARTICUZ_CHROMIUM_VERSION}`);
  console.log(`executablePath:     ${launchOptions.executablePath}`);
  console.log(`chromiumSandbox:    ${launchOptions.chromiumSandbox}`);
  console.log(`args:               ${launchOptions.args.join(" ")}`);
}
writeFileSync(join(scratch, "bootstrap-manifest.json"), JSON.stringify(summary, null, 2));
