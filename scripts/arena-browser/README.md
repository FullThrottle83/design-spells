# Arena browser bootstrap (task 0001)

Reproducible, network-restricted Chromium for running the repository's existing
Playwright suite in an Arena Agent Mode sandbox without `apt`, root, or any
system-level install. Binaries and `node_modules` stay out of Git: everything
runtime-related lives in a session-local scratch directory (default
`/tmp/arena-browser-scratch`) plus `/tmp` extraction targets.

## One-time setup (per session)

```bash
node scripts/arena-browser/bootstrap.mjs
```

Installs exactly `playwright-core@1.63.0` and `@sparticuz/chromium@153.0.0`
(the versions task 0001 permits) into the scratch directory, extracts the
Chromium binary to `/tmp/chromium` and the package's bundled AL2023 shared
libraries to `/tmp/al2023/lib`, and points `LD_LIBRARY_PATH` /
`FONTCONFIG_PATH` at them. The AL2023 extraction matters outside AWS Lambda:
the package only does it automatically there, but Debian 12 needs those
libraries (`libnss3.so`, `libnspr4.so`, …) to start the binary at all.

## Offline environment regression (also run in CI)

```bash
node scripts/arena-browser/test-environment.mjs
```

Uses synthetic credential names to confirm that the explicit browser environment
cannot inherit an agent/session secret or arbitrary variable. No browser,
download, or network request is involved. The live verifier additionally checks
the actual spawned process via `/proc/<pid>/environ`.

## Security self-check (required before a run)

```bash
node scripts/arena-browser/verify-chromium.mjs
```

Launches the browser exactly as the test config will and asserts, hard-failing
on violation (exit 1):

- **No forbidden flags.** The effective `/proc/<pid>/cmdline` must not contain
  `--disable-web-security` or `--allow-running-insecure-content`. Nothing here
  passes `@sparticuz/chromium.args` wholesale — only the two boundary flags
  below are added to Playwright's defaults.
- **Sandbox.** Launches with `chromiumSandbox: true` (Playwright's default is
  `false`, which adds `--no-sandbox`). Verified working in the original Arena
  session; if sandboxed launch fails, the verifier exits with failure rather
  than downgrading to an unsandboxed browser.
- **Loopback-only network boundary**, enforced inside the browser process for
  every context and page (including the raw `browser.newContext()` calls some
  specs make), via two flags set in `arena-launch-options.mjs`:
  - `--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1, EXCLUDE localhost`
    — DNS for every non-loopback host fails inside Chromium.
  - `--proxy-server=http://127.0.0.1:9` — non-loopback destinations (including
    direct IP literals, which never touch the resolver) are sent to a closed
    local port and fail with `ERR_PROXY_CONNECTION_FAILED`. Chromium's implicit
    bypass keeps the test server on `127.0.0.1` direct.
  - `use.serviceWorkers: "block"` (in `playwright.arena.config.mjs`) for
    runner-created contexts. The catalogue registers no service workers; this
    is defense in depth.
- **Explicit subprocess environment:** Chromium receives only a short allowlist
  of runtime variables plus a private scratch `HOME`. It does not inherit the
  agent's token, credential, proxy or arbitrary environment variables.
  `verify-chromium.mjs` places a synthetic canary in the parent environment
  and inspects the actual child process's `/proc/<pid>/environ`, logging only
  variable names (never values). Missing or unexpected values fail the check.
- **Live evidence:** loopback navigation + subresource succeed; navigation to
  an external hostname, an external IP, and an external subresource all fail;
  no service worker registers. The unavailable `chrome://sandbox` diagnostic
  is reported as NOT_TESTED, not a successful check.

`CHROMIUM_PATH` overrides the resolved executable (the same hook the repo's
own `playwright.config.mjs` honours). `ARENA_BROWSER_SCRATCH` overrides the
scratch directory.

## Run the existing suite

```bash
npm test                                               # Python + browser layers
npm run test:build                                     # Python only, no browser
npx playwright test --config playwright.arena.config.mjs   # browser layer, enforced
```

`playwright.arena.config.mjs` derives from `playwright.config.mjs` and changes
only the launch options and the service-worker context setting — test
discovery, assertions, workers, retries, webServer and the cross-browser
exclusion are untouched. `npm run test:previews` also works against the repo
config (`CHROMIUM_PATH=/tmp/chromium LD_LIBRARY_PATH=/tmp/al2023/lib npm run
test:previews`), but that path cannot enforce the network boundary, so the
arena config is the supported way to run the browser suite here.

## Versions recorded 2026-09-26

| Component            | Version             |
| -------------------- | ------------------- |
| playwright-core      | 1.63.0              |
| @sparticuz/chromium  | 153.0.0 (Chromium 153.0.8010.0) |
| @playwright/test     | 1.62.1 (repo lockfile) |
| Node / Python        | v22.22.3 / 3.11.2   |
| Host                 | Debian 12, x86_64   |
