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
