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
const SUPPORT_AS_OF = catalogue.supportAsOf ?? "2026-08-24";

function categories() {
  const counts = new Map();
  for (const s of SPELLS) counts.set(s.category, (counts.get(s.category) ?? 0) + 1);
  return [...counts.entries()].map(([category, count]) => ({ category, count }));
}

const STATUSES = ["baseline", "newer", "progressive"];
const JS_NEEDS = ["none", "markup"];

/* ------------------------------------------------------------- error types */

class RpcError extends Error {
  constructor(code, message, data = undefined) {
    super(message);
    this.code = code;
    this.data = data;
  }
}

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
    featureKeys: spell.featureKeys,
    feature: spell.feature,
    browsers: spell.browsers,
    supportNote: spell.supportNote,
    previewEnvironment: spell.previewEnvironment,
    previewAction: spell.previewAction,
    description: spell.description,
  };
}

function validateArgs(name, args) {
  if (args !== undefined && (typeof args !== "object" || args === null || Array.isArray(args))) {
    throw new RpcError(-32602, `Invalid arguments: expected an object, got ${typeof args}`);
  }
  const safeArgs = args ?? {};

  switch (name) {
    case "list_categories":
      return safeArgs;

    case "search_spells": {
      if (safeArgs.limit !== undefined) {
        const num = Number(safeArgs.limit);
        if (!Number.isInteger(num) || num < 1 || num > 200) {
          throw new RpcError(-32602, `Invalid argument "limit": expected integer between 1 and 200, got ${safeArgs.limit}`);
        }
      }
      if (safeArgs.status !== undefined && !STATUSES.includes(safeArgs.status)) {
        throw new RpcError(-32602, `Invalid argument "status": expected one of ${JSON.stringify(STATUSES)}, got "${safeArgs.status}"`);
      }
      if (safeArgs.jsNeed !== undefined && !JS_NEEDS.includes(safeArgs.jsNeed)) {
        throw new RpcError(-32602, `Invalid argument "jsNeed": expected one of ${JSON.stringify(JS_NEEDS)}, got "${safeArgs.jsNeed}"`);
      }
      if (safeArgs.query !== undefined && typeof safeArgs.query !== "string") {
        throw new RpcError(-32602, `Invalid argument "query": expected string, got ${typeof safeArgs.query}`);
      }
      if (safeArgs.category !== undefined && typeof safeArgs.category !== "string") {
        throw new RpcError(-32602, `Invalid argument "category": expected string, got ${typeof safeArgs.category}`);
      }
      return safeArgs;
    }

    case "get_spell": {
      if (!safeArgs.id || typeof safeArgs.id !== "string" || !safeArgs.id.trim()) {
        throw new RpcError(-32602, `Missing or invalid required argument "id": expected non-empty string`);
      }
      return safeArgs;
    }

    default:
      throw new RpcError(-32602, `Unknown tool "${name}".`);
  }
}

function callTool(name, rawArgs = {}) {
  const args = validateArgs(name, rawArgs);

  switch (name) {
    case "list_categories":
      return {
        supportAsOf: SUPPORT_AS_OF,
        total: TOTAL,
        categories: categories(),
        statuses: STATUSES,
        jsNeeds: JS_NEEDS,
      };

    case "search_spells": {
      const limit = Math.min(200, Math.max(1, Number(args.limit) || 20));
      const results = SPELLS.filter((s) => matches(s, args)).slice(0, limit);
      return {
        supportAsOf: SUPPORT_AS_OF,
        count: results.length,
        spells: results.map(summary),
      };
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
        previewEnvironment: spell.previewEnvironment,
        previewAction: spell.previewAction,
        previewHtml: spell.previewHtml,
        previewCss: spell.previewCss,
      };
    }

    default:
      throw new RpcError(-32602, `Unknown tool "${name}".`);
  }
}

/* ----------------------------------------------------------- MCP framing */

let lifecycleState = "UNINITIALIZED"; // UNINITIALIZED | INITIALIZING | READY

function send(msg) {
  process.stdout.write(JSON.stringify(msg) + "\n");
}

function respond(id, result) {
  send({ jsonrpc: "2.0", id, result });
}

function respondError(id, code, message, data = undefined) {
  const errObj = { code, message };
  if (data !== undefined) errObj.data = data;
  send({ jsonrpc: "2.0", id, error: errObj });
}

function handle(message) {
  if (!message || typeof message !== "object" || Array.isArray(message)) {
    respondError(null, -32600, "Invalid Request");
    return;
  }

  const { id, method, params } = message;

  // Handle notifications (no id)
  if (id === undefined) {
    if (method === "notifications/initialized") {
      lifecycleState = "READY";
    }
    return;
  }

  try {
    switch (method) {
      case "initialize": {
        lifecycleState = "INITIALIZING";
        let protocolVersion = SUPPORTED_PROTOCOL_VERSIONS[SUPPORTED_PROTOCOL_VERSIONS.length - 1];
        if (params?.protocolVersion && SUPPORTED_PROTOCOL_VERSIONS.includes(params.protocolVersion)) {
          protocolVersion = params.protocolVersion;
        }
        respond(id, {
          protocolVersion,
          capabilities: { tools: {} },
          serverInfo: { name: NAME, version: VERSION },
        });
        break;
      }

      case "ping":
        respond(id, {});
        break;

      case "tools/list":
        if (lifecycleState === "UNINITIALIZED") {
          throw new RpcError(-32002, "Server not initialized");
        }
        respond(id, { tools: TOOLS });
        break;

      case "tools/call":
        if (lifecycleState === "UNINITIALIZED") {
          throw new RpcError(-32002, "Server not initialized");
        }
        if (!params || typeof params !== "object" || !params.name) {
          throw new RpcError(-32602, "Invalid params: missing tool name");
        }
        try {
          const result = callTool(params.name, params.arguments ?? {});
          respond(id, {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
            isError: false,
          });
        } catch (err) {
          if (err instanceof RpcError) {
            throw err;
          }
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
    if (err instanceof RpcError) {
      respondError(id, err.code, err.message, err.data);
    } else {
      respondError(id, -32603, String(err.message || err));
    }
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
    const parsed = JSON.parse(text);
    handle(parsed);
  } catch {
    respondError(null, -32700, "Parse error");
  }
});

rl.on("close", () => process.exit(0));
