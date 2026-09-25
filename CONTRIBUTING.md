# Contributing to Design Spells

Design Spells is a reference catalogue of HTML/CSS techniques, not a component framework. Contributions should make examples more correct, useful, accessible, and reproducible—not merely add visual variety.

## Source of truth

- Edit **README.md** for canonical spell content. Keep **SKILL.md** byte-identical to it.
- `scripts/build.py` generates `public/index.html` and `public/spells.json`. Never edit generated examples as the only fix.
- Keep stable spell IDs; do not renumber existing entries.
- Update `public/spells.schema.json` and `schema/spells.d.ts` together when changing the data contract.

## Before opening a pull request

1. Show a complete HTML/CSS example. If markup or shared tokens are required, include them explicitly.
2. Include an actionable demonstration and a usable fallback for features that are not widely available.
3. Verify click, keyboard, focus, dismissal, narrow viewport, and reduced-motion behavior where relevant.
4. Describe browser support conservatively. A CSS syntax probe does not prove the component works.
5. Avoid JavaScript inside spells. Optional catalogue enhancements must never be required to read or use a spell.
6. Do not add external images, fonts, trackers, or network requests to examples without documenting why.

Run:

```sh
npm ci
npm run build
npm test
git diff --check
```

The browser suite currently covers Chromium. Additional Firefox, WebKit, and assistive-technology verification must be reported separately; do not imply that a passing test suite constitutes WCAG conformance.

## Scope and review

Keep pull requests focused. For a bug, include the affected spell ID, its expected behavior, a reproduction, and a regression test. For a new feature, explain why it cannot be demonstrated with an existing spell. Screenshots or short recordings are useful for visual changes but cannot replace source and behavior tests.

See [AGENTS.md](AGENTS.md) for the repository's coding-agent constraints.
