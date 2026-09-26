# Arena task 0001 — evidence report

> **Review amendment (2026-09-26):** The 76 Python / 423 Playwright results and
> `verify-chromium.out` below were captured by Arena **before** a follow-up
> security fix on this PR branch. Review found that Playwright could inherit
> the parent agent's environment. The launcher now supplies an explicit,
> credential-free subprocess environment with a scratch HOME, and the verifier
> tests a synthetic parent-env canary against the actual browser's
> `/proc/<pid>/environ`. It now fails rather than falling back to an
> unsandboxed browser, and reports unavailable `chrome://sandbox` as
> NOT_TESTED. An offline regression check was added to CI. The original raw
> evidence is preserved, not rewritten. **The new live browser verifier and
> 423-case Arena run need a fresh execution on the amended head before their
> results can be attributed to the security fix.**


Date: 2026-09-26 · Session branch `arena/01a0de89-design-spells` · Base `main` @ `8bc1de55d6f649f4a86e66600dd2dc3c24f8f6ee` (task brief's baseline `fd4a7fa` is stale; actual verified HEAD recorded here). PR #47 (`instinct/agent-guide-design-spells-20260926`) untouched; no PR existed for this branch.

## Commands and raw outcomes

| Command | Exit | Result |
| --- | --- | --- |
| `npm ci` | 0 | added 3 packages, 0 vulnerabilities (`@playwright/test` 1.62.1 from lockfile) |
| `npm run build` | 0 | `wrote public/spells.json 463930 bytes`, classic + bundle built; `git status` clean afterwards |
| `npm run test:build` (Python) | 0 | `Ran 76 tests in 2.114s` — **76 passed, 0 failed, 0 skipped** (unittest, stdlib only) |
| `node scripts/arena-browser/bootstrap.mjs` | 0 | scratch `/tmp/arena-browser-scratch`, executablePath `/tmp/chromium` |
| `node scripts/arena-browser/verify-chromium.mjs` | 0 | 11/11 checks PASS (see below) |
| `npx playwright test --config playwright.arena.config.mjs` | 0 | **423 passed, 0 failed, 0 skipped, 0 flaky** in 5.9m (`--list` before run: 423 tests in 17 files, discovery identical to repo config; `cross-browser.spec.mjs` excluded by the repo's own `testIgnore`, it has its own Firefox/WebKit CI job) |
| `git diff --check` | 0 | no whitespace/conflict-marker issues |

Python and browser layers reported separately as required. `npm test` = `test:build && test:previews`; the browser layer ran under `playwright.arena.config.mjs` (the task's fallback path) because the repo config cannot express the network-boundary launch flags or the service-worker context block — everything else (discovery, assertions, workers, retries, webServer, exclusions) is inherited unchanged. Raw runner output: [`raw/playwright-arena-run.log`](raw/playwright-arena-run.log) (unabridged, 423 `✓` lines, no `✘`/`flaky`/`skipped`/`retry` lines).

## Browser bootstrap

- No system Chromium and no Playwright cache existed (`which chromium…` empty, `~/.cache/ms-playwright` absent) → bounded bootstrap per task: `playwright-core@1.63.0` + `@sparticuz/chromium@153.0.0` npm-installed into session-local `/tmp/arena-browser-scratch` (no apt, no root, nothing fetched outside npm; binaries/`node_modules` not committed).
- First launch failed: `libnspr4.so: cannot open shared object file`. Cause: `@sparticuz/chromium` extracts its bundled AL2023 libraries only under AWS Lambda (`isRunningInAmazonLinux2023()` gate). The committed bootstrap extracts `bin/al2023.tar.br` via the package's own `inflate()` to `/tmp/al2023/lib` and prepends it to `LD_LIBRARY_PATH`. No system packages touched.
- Resulting binary: Chromium 153.0.8010.0 at `/tmp/chromium`.

## Sandbox outcome

`chromiumSandbox: true` was tested first and **launches successfully** on this host (no `--no-sandbox` in the effective command line — verified from `/proc/<pid>/cmdline`). Playwright's default (`false`) was not used. `chrome://sandbox` is not available in this headless build (`ERR_INVALID_URL`), so the absence of `--no-sandbox` in the effective args is the recorded sandbox evidence, plus the launch succeeding where a sandbox failure would abort.

## Effective, redacted browser command line (from `/proc`, trimmed of Playwright defaults)

```
/tmp/chromium [--disable-field-trial-config --disable-background-networking
 --disable-background-timer-throttling --disable-backgrounding-occluded-windows
 --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection
 --disable-component-extensions-with-background-pages --disable-component-update
 --no-default-browser-check --disable-default-apps --disable-dev-shm-usage
 --disable-edgeupdater --disable-extensions --disable-features=... --enable-features=CDPScreenshotNewSurface
 --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection
 --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding
 --disable-updater-scheduler --force-color-profile=srgb --metrics-recording-only --no-first-run
 --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf
 --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings
 --edge-skip-compat-layer-relaunch --disable-infobars --disable-sync --enable-unsafe-swiftshader
 --headless --hide-scrollbars --mute-audio --blink-settings=...
 --host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1, EXCLUDE localhost
 --proxy-server=http://127.0.0.1:9 --user-data-dir=$SESSION_TMP --remote-debugging-pipe --no-startup-window]
```

Full verbatim list: `verify-chromium.out` (`EFFECTIVE_CMDLINE` line). **No `--no-sandbox`, no `--disable-web-security`, no `--allow-running-insecure-content`.** No credentials (`GH_TOKEN` etc.) are exported into the browser process environment; the launcher never touches them.

## Security self-check — 11/11 PASS (verify-chromium.out)

1. launch with `chromiumSandbox: true` — PASS
2. no forbidden flags in effective argv — PASS (hard-fail guard)
3. sandbox flag outcome: `--no-sandbox` absent, no unsandboxed fallback — PASS
4. arena boundary flags present — PASS
5. loopback navigation allowed (`http://127.0.0.1:<ephemeral>/` → title ok) — PASS
6. loopback subresource allowed (1×1 PNG, `naturalWidth>0`) — PASS
7. service workers blocked (`serviceWorkers:"block"` context: `getRegistrations()=0`, `context.serviceWorkers()=0` after a real register attempt) — PASS
8. external hostname blocked (`http://example.com/` → `ERR_PROXY_CONNECTION_FAILED`; DNS path separately denied by resolver rule) — PASS
9. external IP literal blocked (`http://192.0.2.1/` → `ERR_PROXY_CONNECTION_FAILED`) — PASS
10. external subresource blocked (`<img src=http://example.com/…>` → `naturalWidth=0`, requestfailed) — PASS
11. `chrome://sandbox` status page unavailable in this build — recorded, not a violation

The flags enforce the boundary inside the browser process, so it also covers contexts that specs create via raw `browser.newContext()`. No test navigates anywhere but loopback; nothing needed to change in the specs.

## Test counts (actual runner output)

| Suite | Passed | Failed | Skipped |
| --- | --- | --- | --- |
| `npm run test:build` (Python unittest) | 76 | 0 | 0 |
| Playwright suite (arena config, chromium project) | 423 | 0 | 0 |

17 spec files discovered (`previews` 145 per-spell cases, `drawer`, `accessibility`, `native-behavior`, `security`, `static-pages`, `spell-copy`, `lean-catalog`, `bundle`, `behavior-contracts`, `preview-visibility`, `scroll-state-behavior`, `gap-spells`, `showcase-pilot*3`, `walkthroughs`). `cross-browser.spec.mjs` remains excluded exactly as the repo config intends (dedicated Firefox/WebKit CI job) — not run here, reported as intended-excluded.

## Blockers / notes

- None blocking. `chrome://sandbox` is unavailable in this build, so the sandbox claim rests on the effective argv (no `--no-sandbox`) rather than Chromium's own status page.
- The scratch bootstrap is session-local by design; re-run `node scripts/arena-browser/bootstrap.mjs` in a fresh session (requires npm registry access, ~90 MB).
- No spell content, application code, existing config semantics, or assertions were modified: `git diff` on tracked files is empty; all changes are new files.

## Changed paths

- `scripts/arena-browser/` — `arena-launch-options.mjs`, `bootstrap.mjs`, `verify-chromium.mjs`, `README.md`
- `playwright.arena.config.mjs` — derives from the repo config; launch options + `serviceWorkers: "block"` only
- `docs/evidence/arena-task-0001/` — this report, `verify-chromium.out`, `raw/playwright-arena-run.log`
- `.arena/results/0001.md`

---

# Post-review revalidation (2026-09-26, amended head `4317b2c`)

This section supersedes the "pending re-run" note in the review amendment above:
the live browser verifier and the full Arena suite **have now been re-executed on
the amended head** with the environment-isolation fix active. The pre-review
evidence above is preserved unchanged for provenance (original raw log
`raw/playwright-arena-run.log`, md5 `a09bf5576130d8aee49f428e15f89f96`).

## Commands (branch fast-forwarded `14a847e` → `4317b2c`; reviewer changes intact)

| # | Command | Exit | Outcome |
| --- | --- | --- | --- |
| 1 | `npm ci` | 0 | 0 vulnerabilities |
| 2 | `npm run build` | 0 | spells.json 463,930 bytes; worktree clean after build |
| 3 | `node scripts/arena-browser/test-environment.mjs` | 0 | PASS — explicit browser env excludes synthetic credentials/canary/arbitrary variables; scratch `HOME` enforced |
| 4 | `node scripts/arena-browser/bootstrap.mjs` | 0 | scratch reused (`installedFresh: false`), playwright-core 1.63.0, @sparticuz/chromium 153.0.0, executablePath `/tmp/chromium`, sandbox true |
| 5 | `node scripts/arena-browser/verify-chromium.mjs` | 0 | 11 PASS + **browser environment isolation PASS**; `chrome://sandbox` NOT_TESTED (unavailable in this headless build) |
| 6 | `npm run test:build` | 0 | `Ran 76 tests in 1.983s` — **76 passed / 0 failed / 0 skipped** |
| 7 | `npx playwright test --config playwright.arena.config.mjs` | 0 | **423 passed / 0 failed / 0 skipped** in 5.9m (423 `✓`, zero `✘`/`flaky`/`skipped`/`interrupted`) |
| 8 | `git diff --check` | 0 | clean |

## Environment isolation — synthetic canary result

`verify-chromium.mjs` sets `ARENA_BROWSER_ENV_CANARY` in its own (parent) process
before launching, then reads the **spawned browser's actual `/proc/<pid>/environ`**
and compares variable *names* (never values) against the declared allowlist:

> PASS browser environment isolation — "only 4 explicit allowlisted variables; synthetic canary and credential variables absent"

**The synthetic canary was absent from the spawned Chromium process.** No
credential-shaped name (`*TOKEN*`, `*SECRET*`, `*PASSWORD*`, `*CREDENTIAL*`,
`*API_KEY*`, `*PRIVATE_KEY*`) appeared; every name in the child environ belonged
to the declared `BROWSER_ENV_ALLOWLIST` + scratch `HOME`. No environment values
were read out or printed by any step.

## Effective browser flags (amended head)

- Sandbox required, no fallback: `chromiumSandbox: true` launch succeeded;
  `--no-sandbox` occurrences in effective argv: **0** (hard-fails otherwise).
- Forbidden flags `--disable-web-security` / `--allow-running-insecure-content`:
  **0 occurrences** (hard-fail guard, verified against `/proc/<pid>/cmdline`).
- Boundary flags present exactly once each, as required:
  `--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1, EXCLUDE localhost`
  and `--proxy-server=http://127.0.0.1:9` (implicit loopback bypass keeps the
  test server direct). Live probes re-confirmed: loopback nav/subresource OK;
  external hostname, external IP, external subresource all blocked.

Raw post-review artifacts: `post-review-commands.log`, `post-review-test-environment.out`,
`post-review-bootstrap.json`, `post-review-verify-chromium.out`,
`raw/post-review-playwright-arena-run.log`.
