# Arena local browser benchmark — Design Spells

**Date:** 2026-09-26 (Europe/Stockholm)  
**Scope:** local generated site only; this report makes no claim about a live deployment.

## 1. Environment and dependencies

- Repository: `FullThrottle83/design-spells`
- Base commit: `fd4a7fad59fac293408298d1e6c1a508d46f8439`
- Working branch: `arena/01a0dcb7-design-spells`
- Node `v22.22.3`; npm `10.9.8`; Python `3.11.2`
- Project install: `npm ci`; 3 packages added, 0 vulnerabilities.
- Project dependency: `@playwright/test` resolved by lockfile; browser bootstrap: `playwright-core@1.63.0`, `@sparticuz/chromium@153.0.0` installed in `/tmp/pwnode` only.
- Chromium: bundled headless shell from `@sparticuz/chromium`, executable `/tmp/chromium`.

## 2. Build

**PASS** — command: `npm run build` (which runs `python3 scripts/build.py`).

Observed output: parsed 154 spells; generated `public/spells.json` (439842 bytes), `index.html` (4899005 bytes), 154 static spell pages/isolated demos, and the light catalogue (107911 bytes). The working tree remained clean after the build, so no application files were changed.

## 3. Local server

**PASS** — command: `python3 -m http.server 4173 --bind 0.0.0.0 --directory public`.

The server listened on `0.0.0.0:4173`. Chromium navigated to `http://127.0.0.1:4173` and all six checked URLs returned HTTP 200.

## 4. Browser checks

The script tested three representative pages at desktop 1440x900 and mobile 390x844:

| Page | Title | Main landmarks | Console errors | Failed requests | Overflow |
|---|---|---|---:|---:|---|
| `/` | Design Spells — native HTML & CSS techniques | `main`, `h1`, `header` present | 0 | 0 | no (1440/1440; 390/390) |
| `/spells/ds-1/` | Shimmer on primary buttons — Design Spells | `main`, `h1`, `header` present | 0 | 0 | no (1440/1440; 390/390) |
| `/spells/ds-95/` | CSS Sparkline / Bar Chart — Design Spells | `main`, `h1`, `header` present | 0 | 0 | no (1440/1440; 390/390) |

Checks used real Chromium DOM evaluation, `console` error listeners, `requestfailed` listeners, and `document.documentElement.scrollWidth` versus `clientWidth`.

## 5. Screenshots and evidence

Screenshots are genuine PNG captures from the local server. PNG headers were parsed to validate dimensions and SHA-256 was computed from the saved bytes.

| File | Dimensions | Bytes | SHA-256 |
|---|---:|---:|---|
| `home-desktop.png` | 1440x900 | 79390 | `c78527e90c9fc9f8af51e3e81e653895c81b38c1678926eb518b2219b3180f1a` |
| `home-mobile.png` | 390x844 | 36487 | `30e704e20b3fd2b5595f257a30a6dc6eaf99bb357b356aebb159edb1b6d254ac` |
| `spells-ds-1-desktop.png` | 1440x900 | 48549 | `1137aff8ecb4f1594ea20ca25f74e933c4e7b8041673d7e526f67adba0d6c980` |
| `spells-ds-1-mobile.png` | 390x844 | 33797 | `816c79845fe7a5bc51af5b5150399881614e3e0c5b609acc7c5172d07f915078` |
| `spells-ds-95-desktop.png` | 1440x900 | 59995 | `d1043f51a89a979c6b41a5cbd751bf101ab58c951a0e5ad021f057193843a062` |
| `spells-ds-95-mobile.png` | 390x844 | 47072 | `9c7f5bae7c0e47180836cfba25dca78570ee70270830888dd7d6e1aae98e1d1f` |

Machine-readable evidence is in `results.json`; rerun `sha256sum *.png results.json` in this directory to verify the committed bytes.

## 6. Errors and limitations

- No system Chromium was present initially. Following the approved Arena procedure, the two browser packages were installed under `/tmp/pwnode`; no apt/system packages were installed and no browser security flags were intentionally supplied by the benchmark script.
- The first launch attempt failed because the package's AL2023 shared libraries were not on `LD_LIBRARY_PATH`; the second attempt used the package's extracted `/tmp/al2023/lib` directory and passed.
- The effective Playwright launch log includes Chromium/package runtime flags including `--no-sandbox` and `--disable-web-security` even though the benchmark script did not pass them. This is a limitation of the `@sparticuz/chromium` runtime and is recorded rather than hidden. The run is therefore local-rendering evidence, not a security audit.
- No live deployment was tested. No claim is made about production behavior, cookies, remote assets, headers, or third-party requests.
- The server was plain Python static HTTP because this checkout contains generated static output and no Astro application runtime/package script; the documented repository command was still used for generation/build.

## 7. Observed setup and execution time

- Repository inspection and concurrent-branch/PR checks: approximately 2 minutes.
- `npm ci` plus production generation build: 2 seconds wall time (npm reported 681 ms; build 1.56 s).
- Browser package install: approximately 4 seconds.
- Local server startup: under 1 second.
- Six Chromium navigations, DOM/network checks, screenshots and hashing: approximately 5 seconds.

## 8. Repeatability

**PASS with documented prerequisites.** A fresh Arena session can repeat the workflow by running `npm ci`, `npm run build`, starting the static server, obtaining approval for the documented `/tmp/pwnode` browser bootstrap when Chromium is absent, setting `LD_LIBRARY_PATH` to the extracted package libraries, and running the evidence script. Browser egress/live deployment behavior remains outside this result.

## Files delivered

- `REPORT.md` — this benchmark report.
- `results.json` — per-page/per-viewport machine-readable results.
- Six PNG screenshots listed above.
