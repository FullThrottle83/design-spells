# Design Spells agent guide

This repository is a canonical reference bank of ~150 zero-client-JS design spells (CSS animations, micro-interactions, UI polish patterns) optimized for Astro projects. It is exposed as both a browsable human catalogue and an MCP server, backed by a strict JSON Schema contract.

## Sources of truth

When working in this repository, rely on these files as the authoritative sources:
- **Data:** `README.md` is the canonical source for all spell content. `scripts/build.py` parses it and generates `public/spells.json`.
- **Contracts:** `public/spells.schema.json` defines the strict JSON Schema, and `schema/spells.d.ts` provides the TypeScript types.
- **MCP Server:** `mcp/server.mjs` is the entry point exposing the catalogue via the Model Context Protocol.

## The hard Zero-JS rule

This is a Zero-JS repository. Only spells marked **"0 JS"** or **"Markup"** belong here. **Never introduce client-side JavaScript** for any interaction, animation, or state that the catalogue already solves natively with CSS and HTML patterns.

## Adding or editing a spell

- **Stable numbering:** Always preserve and use stable spell numbers.
- **Consistency:** Edit `README.md` for spell content. You only need to synchronize `public/spells.schema.json` and `schema/spells.d.ts` when the actual data contract changes, not for ordinary spell edits.
- **Validation:** Run `npm run build` after making changes. When your change warrants the full test suite, run `npm test`.

## Working style

- **Minimal edits:** Make the smallest change necessary to solve the given task. Do not refactor or reorganize unrelated content.
- **Referencing:** Always refer to spells by their stable number.
- **Selection priority:** When selecting spells, follow the priority order: **Baseline → Newer → Progressive**.


## Safe execution and handoff
- Check worktree status and preserve other work. Confirm scripts, dependencies and CI from the repo before editing; read the affected README, generator, contract and tests. Verify uncertain APIs against installed versions or version-matched docs. Never weaken checks or validation to get a pass.
- Stop after two unsuccessful repair cycles for one failure; report errors and remaining work instead of a third blind edit.
- Do not enable auto-merge, remove `hold`, delete a branch or deploy without Jonas's separate explicit approval. Propose changes in a draft PR with `hold`; do not merge.
- Never place personnummer or customer data in spells, code, prompts, fixtures, logs or PR text; use synthetic data.
- Start the Swedish report with one sentence stating klart, delvis or blockerat and the next action Jonas needs, if any. Mark claims VERIFIERAT or ANTAGET; list exact checks, results and anything unverified.
