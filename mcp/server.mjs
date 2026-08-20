#!/usr/bin/env node
/**
 * Design Spells — MCP server (stdio transport).
 *
 * Exposes the catalogue to AI agents over the Model Context Protocol, so an
 * editor agent can do: "give my login button some magic from Design Spells"
 * and pull back the exact spell's CSS, HTML, and Tailwind source.
 *
 * Zero runtime dependencies: MCP's JSON-RPC-over-stdio framing is implemented
 * directly on top of Node's readline/process streams. The data comes from the
 * machine-readable public/spells.json that scripts/build.py generates.
 *
 * Tools:
 *   - list_categories  -> categories with counts + statuses
 *   - search_spells    -> filter by query/category/status/jsNeed
 *   - get_spell        -> full source for one spell (css, html, tailwind, preview)
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import readline from "node:readline";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_PATH = join(__dirname, "..", "public", "spells.json");

const NAME = "design-spells";
const VERSION = "1.0.0";

const SUPPORTED_PROTOCOL_VERSIONS = ["2024-11-05", "2025-03-26", "2025-06-18"];

/* ------------------------------------------------------------------ data */

const catalogue = JSON.parse(readFileSync(DATA_PATH, "utf-8"));
const SPELLS = catalogue.spells ?? [];
const TOTAL = catalogue.total ?? SPELLS.length;

function categories() {
  const counts = new Map();
  for (const s of SPELLS) counts.set(s.category, (counts.get(s.category) ?? 0) + 1);
  return [...counts.entries()].map(([category, count]) => ({ category, count }));
}

const STATUSES = ["baseline", "newer", "progressive"];
const JS_NEEDS = ["none", "markup"];

/* ------------------------------------------------------------- matching */

function matches(spell, { query = "", category, status, jsNeed } = {}) {
  if (category && spell.category !== category) return false;
  if (status && spell.status !== status) return false;
  if (jsNeed && spell.jsNeed !== jsNeed) return false;
  if (!query) return true;
  const hay = [
    spell.id, spell.number, spell.title, spell.category, spell.status,
    spell.statusLabel, spell.jsLabel, spell.feature, spell.description,
  ].join(" ").toLowerCase();
  return query.toLowerCase().split(/\s+/).every((term) => hay.includes(term));
}

/* ------------------------------------------------------------- tailwind */

function tailwindFor(spell) {
  const css = String(spell.css || "").trim();
  if (!css) return "";
  const indented = css.split("\n").map((l) => (l ? "  " + l : l)).join("\n");
  return [
    "/* Tailwind v4 — drop into a global stylesheet processed by Tailwind. */",
    '@import "tailwindcss";',
    "",
    "@layer components {",
    indented,
    "}",
    "",
  ].join("\n");
}

/* ------------------------------------------------------------- tool defs */

const TOOLS = [
  {
    name: "list_categories",
    description:
      "List every category in the Design Spells catalogue with its spell count, plus the valid status and jsNeed filter values.",
    inputSchema: { type: "object", properties: {} },
  },
  {
    name: "search_spells",
    description:
      "Search the Design Spells catalogue. Returns matching spells (id, title, category, status, browser support, feature, description). Select by id, then call get_spell for full source.",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Free-text terms; every term must match (title, category, feature, description…).",
        },
        category: {
          type: "string",
          description: "Restrict to one category (see list_categories).",
        },
        status: {
          type: "string",
          enum: STATUSES,
          description: "Browser-risk status. Prefer baseline, then newer, then progressive.",
        },
        jsNeed: {
          type: "string",
          enum: JS_NEEDS,
          description: '"none" = zero JS, "markup" = zero JS but needs a native HTML pattern.',
        },
        limit: {
          type: "integer",
          minimum: 1,
          maximum: 200,
          description: "Max results to return (default 20).",
        },
      },
    },
  },
  {
    name: "get_spell",
    description:
      "Return the full source for one spell by id (e.g. ds-43): description, HTML, modern CSS, Tailwind v4, and browser support. This is what you inject into the user's project.",
    inputSchema: {
      type: "object",
      required: ["id"],
      properties: {
        id: {
          type: "string",
          description: 'Stable spell id, e.g. "ds-43".',
        },
      },
    },
  },
];

/* ------------------------------------------------------------- tool impl */

function summary(spell) {
  return {
    id: spell.id,
    number: spell.number,
    title: spell.title,
    category: spell.category,
    status: spell.status,
    statusLabel: spell.statusLabel,
    jsNeed: spell.jsNeed,
    jsLabel: spell.jsLabel,
    feature: spell.feature,
    browsers: spell.browsers,
    supportNote: spell.supportNote,
    description: spell.description,
  };
}

function callTool(name, args = {}) {
  switch (name) {
    case "list_categories":
      return {
        total: TOTAL,
        categories: categories(),
        statuses: STATUSES,
        jsNeeds: JS_NEEDS,
      };

    case "search_spells": {
      const limit = Math.min(200, Math.max(1, Number(args.limit) || 20));
      const results = SPELLS.filter((s) => matches(s, args)).slice(0, limit);
      return { count: results.length, spells: results.map(summary) };
    }

    case "get_spell": {
      const spell = SPELLS.find((s) => s.id === args.id);
      if (!spell) {
        throw new Error(`Unknown spell id "${args.id}". Use search_spells to discover ids.`);
      }
      return {
        ...summary(spell),
        html: spell.html,
        css: spell.css,
        tailwind: tailwindFor(spell),
        previewHtml: spell.previewHtml,
      };
    }

    default:
      throw new Error(`Unknown tool "${name}".`);
  }
}

/* ----------------------------------------------------------- MCP framing */

function send(msg) {
  process.stdout.write(JSON.stringify(msg) + "\n");
}

function respond(id, result) {
  send({ jsonrpc: "2.0", id, result });
}

function respondError(id, code, message) {
  send({ jsonrpc: "2.0", id, error: { code, message } });
}

function handle(message) {
  if (!message || typeof message !== "object") return;

  // Notifications (no id) require no response.
  if (message.id === undefined) return;

  const { id, method, params } = message;

  try {
    switch (method) {
      case "initialize":
        respond(id, {
          protocolVersion: SUPPORTED_PROTOCOL_VERSIONS[SUPPORTED_PROTOCOL_VERSIONS.length - 1],
          capabilities: { tools: {} },
          serverInfo: { name: NAME, version: VERSION },
        });
        break;

      case "ping":
        respond(id, {});
        break;

      case "tools/list":
        respond(id, { tools: TOOLS });
        break;

      case "tools/call":
        try {
          const result = callTool(params?.name, params?.arguments ?? {});
          respond(id, {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
            isError: false,
          });
        } catch (err) {
          respond(id, {
            content: [{ type: "text", text: String(err.message || err) }],
            isError: true,
          });
        }
        break;

      default:
        respondError(id, -32601, `Method not found: ${method}`);
    }
  } catch (err) {
    respondError(id, -32603, String(err.message || err));
  }
}

const rl = readline.createInterface({
  input: process.stdin,
  terminal: false,
});

rl.on("line", (line) => {
  const text = line.trim();
  if (!text) return;
  try {
    handle(JSON.parse(text));
  } catch {
    // Malformed frame — ignore rather than crash the session.
  }
});

rl.on("close", () => process.exit(0));
