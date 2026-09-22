# Design Spells agent guide

This repository is a canonical reference bank of ~150 zero-client-JS design spells (CSS animations, micro-interactions, UI polish patterns) optimized for Astro projects. It is exposed as both a browsable human catalogue and an MCP server, backed by a strict JSON Schema contract.

## Sources of truth

When working in this repository, rely on these files as the authoritative sources:
- **Data:** `public/spells.json` is the machine-readable source of truth for all spells.
- **Contracts:** `public/spells.schema.json` defines the strict JSON Schema, and `schema/spells.d.ts` provides the TypeScript types.
- **Documentation:** `README.md` details project structure and principles.
- **MCP Server:** `mcp/server.mjs` is the entry point exposing the catalogue via the Model Context Protocol.

## The hard Zero-JS rule

This is a Zero-JS repository. Only spells marked **"0 JS"** or **"Markup"** belong here. **Never introduce client-side JavaScript** for any interaction, animation, or state that the catalogue already solves natively with CSS and HTML patterns.

## Adding or editing a spell

- **Stable numbering:** Always preserve and use stable spell numbers.
- **Consistency:** When updating spells, keep `public/spells.json`, `public/spells.schema.json`, and `schema/spells.d.ts` in sync.
- **Alignment:** Ensure that updates keep the human-readable catalogue and the MCP server consistent.

## Working style

- **Minimal edits:** Make the smallest change necessary to solve the given task. Do not refactor or reorganize unrelated content.
- **Referencing:** Always refer to spells by their stable number.
- **Selection priority:** When selecting spells, follow the priority order: **Baseline → Newer → Progressive**.
