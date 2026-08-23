#!/usr/bin/env python3
"""Integration tests for the Model Context Protocol (MCP) server.

Spawns `node mcp/server.mjs` over stdio and verifies JSON-RPC 2.0 framing,
initialization lifecycle, input schema validation, and tool output accuracy.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT / "mcp" / "server.mjs"


class McpServerTest(unittest.TestCase):
    def setUp(self):
        self.proc = subprocess.Popen(
            ["node", str(SERVER_PATH)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.msg_id = 0

    def tearDown(self):
        if self.proc.stdin and not self.proc.stdin.closed:
            self.proc.stdin.close()
        if self.proc.stdout and not self.proc.stdout.closed:
            self.proc.stdout.close()
        if self.proc.stderr and not self.proc.stderr.closed:
            self.proc.stderr.close()
        if self.proc.poll() is None:
            self.proc.terminate()
            self.proc.wait()

    def send_request(self, method: str, params: dict | None = None) -> dict:
        self.msg_id += 1
        req = {"jsonrpc": "2.0", "id": self.msg_id, "method": method}
        if params is not None:
            req["params"] = params
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        self.assertTrue(line, "Server process terminated unexpectedly")
        return json.loads(line)

    def send_notification(self, method: str, params: dict | None = None) -> None:
        notif = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            notif["params"] = params
        self.proc.stdin.write(json.dumps(notif) + "\n")
        self.proc.stdin.flush()

    def init_server(self) -> dict:
        res = self.send_request("initialize", {"protocolVersion": "2025-06-18"})
        self.send_notification("notifications/initialized")
        return res

    def test_uninitialized_call_rejected(self):
        res = self.send_request("tools/list")
        self.assertIn("error", res)
        self.assertEqual(res["error"]["code"], -32002)

    def test_initialize_handshake(self):
        res = self.init_server()
        self.assertIn("result", res)
        result = res["result"]
        self.assertEqual(result["protocolVersion"], "2025-06-18")
        self.assertEqual(result["serverInfo"]["name"], "design-spells")
        self.assertEqual(result["serverInfo"]["version"], "1.0.0")

    def test_ping(self):
        self.init_server()
        res = self.send_request("ping")
        self.assertEqual(res.get("result"), {})

    def test_tools_list(self):
        self.init_server()
        res = self.send_request("tools/list")
        self.assertIn("result", res)
        tools = res["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        self.assertEqual(tool_names, ["list_categories", "search_spells", "get_spell"])

    def test_tool_list_categories(self):
        self.init_server()
        res = self.send_request("tools/call", {"name": "list_categories", "arguments": {}})
        self.assertFalse(res["result"]["isError"])
        data = json.loads(res["result"]["content"][0]["text"])
        self.assertIn("categories", data)
        self.assertIn("total", data)
        self.assertIn("supportAsOf", data)
        self.assertEqual(data["total"], 150)

    def test_tool_search_spells(self):
        self.init_server()
        res = self.send_request("tools/call", {
            "name": "search_spells",
            "arguments": {"query": "accordion", "limit": 5},
        })
        self.assertFalse(res["result"]["isError"])
        data = json.loads(res["result"]["content"][0]["text"])
        self.assertGreater(data["count"], 0)
        self.assertLessEqual(data["count"], 5)
        for spell in data["spells"]:
            self.assertIn("id", spell)
            self.assertIn("previewEnvironment", spell)
            self.assertIn("previewAction", spell)

    def test_tool_search_spells_validation_errors(self):
        self.init_server()
        res = self.send_request("tools/call", {
            "name": "search_spells",
            "arguments": {"limit": -1},
        })
        self.assertIn("error", res)
        self.assertEqual(res["error"]["code"], -32602)

        res2 = self.send_request("tools/call", {
            "name": "search_spells",
            "arguments": {"status": "invalid_status"},
        })
        self.assertIn("error", res2)
        self.assertEqual(res2["error"]["code"], -32602)

    def test_tool_get_spell(self):
        self.init_server()
        res = self.send_request("tools/call", {
            "name": "get_spell",
            "arguments": {"id": "ds-147"},
        })
        self.assertFalse(res["result"]["isError"])
        data = json.loads(res["result"]["content"][0]["text"])
        self.assertEqual(data["id"], "ds-147")
        self.assertEqual(data["number"], "147")
        self.assertIn("css", data)
        self.assertIn("html", data)
        self.assertIn("tailwind", data)
        self.assertEqual(data["previewEnvironment"], "shadow")

    def test_tool_get_spell_missing_id(self):
        self.init_server()
        res = self.send_request("tools/call", {
            "name": "get_spell",
            "arguments": {},
        })
        self.assertIn("error", res)
        self.assertEqual(res["error"]["code"], -32602)

    def test_tool_get_spell_not_found(self):
        self.init_server()
        res = self.send_request("tools/call", {
            "name": "get_spell",
            "arguments": {"id": "ds-99999"},
        })
        self.assertTrue(res["result"]["isError"])
        self.assertIn("Unknown spell id", res["result"]["content"][0]["text"])

    def test_unknown_method(self):
        self.init_server()
        res = self.send_request("non_existent_method")
        self.assertIn("error", res)
        self.assertEqual(res["error"]["code"], -32601)

    def test_parse_error(self):
        self.proc.stdin.write("{not valid json\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        res = json.loads(line)
        self.assertIn("error", res)
        self.assertEqual(res["error"]["code"], -32700)


if __name__ == "__main__":
    unittest.main(verbosity=2)
