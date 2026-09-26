#!/usr/bin/env node
/**
 * Offline regression check: Chromium's explicit environment must not inherit
 * credentials or arbitrary Arena/session variables. No browser is launched.
 * The live /proc check is in verify-chromium.mjs.
 */
import assert from "node:assert/strict";
import { statSync } from "node:fs";
import { join } from "node:path";
import {
  BROWSER_ENV_ALLOWLIST,
  browserEnvironment,
  scratchDir,
} from "./arena-launch-options.mjs";

const syntheticNames = [
  "GH_TOKEN", "GITHUB_TOKEN", "OPENAI_API_KEY",
  "ARENA_BROWSER_ENV_CANARY", "UNRELATED_RUNTIME_VARIABLE",
];
const saved = new Map(syntheticNames.map((name) => [name, process.env[name]]));
try {
  for (const name of syntheticNames) process.env[name] = "synthetic-not-a-secret";
  const browserEnv = browserEnvironment();
  const permittedNames = new Set([...BROWSER_ENV_ALLOWLIST, "HOME"]);
  assert.ok(Object.keys(browserEnv).every((name) => permittedNames.has(name)));
  for (const name of syntheticNames) assert.equal(Object.hasOwn(browserEnv, name), false, name);
  assert.equal(browserEnv.HOME, join(scratchDir(), "browser-home"));
  assert.ok(statSync(browserEnv.HOME).isDirectory());
  if (process.env.PATH !== undefined) assert.equal(browserEnv.PATH, process.env.PATH);
  console.log("PASS: explicit browser env excludes synthetic credentials and arbitrary variables");
} finally {
  for (const [name, value] of saved) {
    if (value === undefined) delete process.env[name];
    else process.env[name] = value;
  }
}
