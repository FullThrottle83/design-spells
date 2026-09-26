# Per-spell verification provenance

`README.md` remains canonical for authored spell HTML/CSS. `data/verification.json`
is an optional evidence overlay keyed by the stable `ds-N` ID; it starts empty.
Missing entries retain `registry-estimate`, `not-individually-verified`, and
`not-audited`. Never infer WCAG conformance from automated tests.

Each override can supply `support`, `behavior`, `accessibility`,
`dependencies` (an array of functional dependencies), `fallback`,
`accessibilityNotes`, and `evidence` (an array). An evidence item needs
`kind` (support/behavior/accessibility), a real HTTPS `url`, an actual
`checkedAt` YYYY-MM-DD date, and a specific `note`. Behavior evidence
also needs the `browser` and its actual `version`; do not substitute a
Playwright project name for a browser version. Source URLs are derived
automatically. Promotion to `source-checked`, `browser-tested`, or
`reviewed` fails without evidence of the corresponding kind. Accessibility
review also needs notes describing scope and limitations. Schema, TypeScript,
generated JSON, static documentation and MCP responses share the metadata.

Attach only evidence actually inspected. Do not infer broad support or WCAG
conformance from syntax checks, geometry or one browser. Run `npm run build`,
`npm test` and the Firefox/WebKit suite before merging; when evidence changes
generated assets, commit them alongside the source.

## First scoped observations — 26 September 2026

Ds-44, ds-45 and ds-46 now have dated, browser-versioned evidence linked to
the relevant successful GitHub Actions runs. Their `behavior: browser-tested`
status covers only the named rendered state transitions in Chromium and their
documented native fallbacks in Firefox/WebKit. It does **not** upgrade the
curated support estimate, imply support for every scroll-state descriptor, or
claim WCAG conformance. All other spells remain individually unverified.

The browser tests ran with scripts disabled. Ds-45 and ds-46 were checked under
both normal and reduced-motion preferences, but their authored transitions
still run in the reduced setting and need a separate motion/accessibility
decision. NVDA/VoiceOver, full keyboard workflows, zoom/reflow and visual
contrast are not audited by these entries.
