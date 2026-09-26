/**
 * Arena task 0001 — shared Chromium launch options for reproducible, network-restricted runs.
 *
 * Single source of truth used by both `verify-chromium.mjs` (the security
 * self-check) and `playwright.arena.config.mjs` (the test-runner config), so
 * the verified launch options are exactly the ones the suite runs under.
 *
 * Executable resolution (in priority order):
 *   1. `CHROMIUM_PATH` env var (the same hook the repo's `playwright.config.mjs`
 *      already honours) — used as-is.
 *   2. The session-local scratch directory prepared by `bootstrap.mjs`
 *      (`ARENA_BROWSER_SCRATCH`, default `/tmp/arena-browser-scratch`), which
 *      holds `playwright-core@1.63.0` + `@sparticuz/chromium@153.0.0`.
 *
 * Nothing here passes `@sparticuz/chromium.args` wholesale. Only two
 * deliberately chosen network-boundary flags are added:
 *
 *   --host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1, EXCLUDE localhost
 *       Chromium fails DNS resolution for every host except loopback. Covers
 *       hostname navigation and subresources in every context and page,
 *       including raw `browser.newContext()` calls inside the specs.
 *
 *   --proxy-server=http://127.0.0.1:9
 *       Everything that is not loopback is routed to a closed local port and
 *       fails fast, which also blocks direct-IP requests that never touch the
 *       resolver. Chromium's implicit bypass rules keep 127.0.0.1/localhost
 *       (the test server) on direct connections.
 *
 * The sandbox is explicitly requested (`chromiumSandbox: true`). Playwright
 * defaults it to false, which adds `--no-sandbox`; this run must stay sandboxed
 * if the platform supports it (verified by `verify-chromium.mjs`).
 */
import { existsSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

export const PLAYWRIGHT_CORE_VERSION = "1.63.0";
export const SPARTICUZ_CHROMIUM_VERSION = "153.0.0";

/**
 * Browser subprocesses must not inherit the agent/session environment.
 * Playwright otherwise defaults to process.env, potentially forwarding
 * GitHub tokens and other credentials. Keep the list intentionally small.
 */
export const BROWSER_ENV_ALLOWLIST = Object.freeze([
  "PATH", "TMPDIR", "TMP", "TEMP", "LD_LIBRARY_PATH",
  "FONTCONFIG_PATH", "LANG", "LC_ALL", "LC_CTYPE", "TZ",
  "XDG_RUNTIME_DIR",
]);

export function browserEnvironment() {
  const env = Object.fromEntries(
    BROWSER_ENV_ALLOWLIST
      .filter((key) => typeof process.env[key] === "string")
      .map((key) => [key, process.env[key]]),
  );
  // Isolate browser home from the agent's home/credential configuration.
  env.HOME = join(scratchDir(), "browser-home");
  mkdirSync(env.HOME, { recursive: true });
  return env;
}

/** Flags that must never appear in the effective browser command line. */
export const FORBIDDEN_ARGS = ["--disable-web-security", "--allow-running-insecure-content"];

/** Loopback-only host resolver: deny everything, allow the two loopback names. */
export const HOST_RESOLVER_RULES =
  "MAP * ~NOTFOUND, EXCLUDE 127.0.0.1, EXCLUDE localhost";

/** Closed local port: non-loopback destinations (incl. raw IPs) fail fast. */
export const DEAD_PROXY = "http://127.0.0.1:9";

export function scratchDir() {
  return process.env.ARENA_BROWSER_SCRATCH ?? "/tmp/arena-browser-scratch";
}

function scratchModule(...segments) {
  return join(scratchDir(), "node_modules", ...segments);
}

async function importScratch(...segments) {
  return import(pathToFileURL(scratchModule(...segments)));
}

/**
 * Resolves the executable path from the scratch bootstrap, extracting the
 * sparticuz binary and its bundled AL2023 shared libraries. The package only
 * extracts those libraries when running under AWS Lambda, so on other hosts
 * this replicates the extraction and points the dynamic loader at them.
 */
async function resolveExecutablePath() {
  const chromiumBin = join(tmpdir(), "chromium");
  const libDir = join(tmpdir(), "al2023", "lib");

  const chromium = (await importScratch("@sparticuz", "chromium", "build", "index.js")).default;
  const { inflate } = await importScratch("@sparticuz", "chromium", "build", "lambdafs.js");
  const binDir = scratchModule("@sparticuz", "chromium", "bin");

  if (!existsSync(chromiumBin)) await inflate(join(binDir, "chromium.br"));
  if (!existsSync(join(tmpdir(), "fonts"))) await inflate(join(binDir, "fonts.tar.br"));
  if (!existsSync(libDir)) await inflate(join(binDir, "al2023.tar.br"));
  // swiftshader.tar.br is optional (software GL); try but never fail on it.
  try {
    if (!existsSync(join(tmpdir(), "libvk_swiftshader.so"))) {
      await inflate(join(binDir, "swiftshader.tar.br"));
    }
  } catch {}

  process.env.LD_LIBRARY_PATH = [libDir, process.env.LD_LIBRARY_PATH]
    .filter(Boolean)
    .join(":");
  process.env.FONTCONFIG_PATH ??= join(tmpdir(), "fonts");

  if (!existsSync(chromiumBin)) {
    throw new Error(`Bootstrap did not produce ${chromiumBin}; run scripts/arena-browser/bootstrap.mjs first.`);
  }
  return chromiumBin;
}

/**
 * Returns the Playwright `launchOptions` for the arena run and prepares this
 * process environment so the spawned browser finds its libraries.
 *
 */
export async function arenaLaunchOptions() {
  const executablePath = process.env.CHROMIUM_PATH || (await resolveExecutablePath());
  if (!existsSync(executablePath)) {
    throw new Error(`CHROMIUM_PATH does not exist: ${executablePath}`);
  }
  return {
    executablePath,
    chromiumSandbox: true,
    env: browserEnvironment(),
    args: [
      `--host-resolver-rules=${HOST_RESOLVER_RULES}`,
      `--proxy-server=${DEAD_PROXY}`,
    ],
  };
}

/** Replaces volatile per-session paths in an argv array for logging. */
export function redactArgs(argv) {
  return argv.map((arg) =>
    arg
      .replaceAll(process.env.HOME ?? "\u0000", "$HOME")
      .replaceAll(scratchDir(), "$SCRATCH")
      .replace(/--user-data-dir=\S+/, "--user-data-dir=$SESSION_TMP"),
  );
}
