#!/usr/bin/env python3
"""
NotebookLM MCP Client for B-SDD Legal Node.
100% Pure Python Standard Library.
Streamable HTTP JSON-RPC 2.0 client for NotebookLM MCP Server on 192.168.3.184:8002.
"""
import argparse
import json
import logging
import sys
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

NOTEBOOKLM_MCP_URL = "http://192.168.3.184:8002/mcp"
TARGET_NOTEBOOK_ID = "6813ab1c-ac22-4c3c-9c8e-9dd67e35da99"


class NotebookLmMcpClient:
    def __init__(self, base_url: str = NOTEBOOKLM_MCP_URL):
        self.base_url = base_url

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

        # 1. Initialize MCP session
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "b-sdd-legal-node", "version": "1.0"}
            }
        }
        req_init = urllib.request.Request(self.base_url, data=json.dumps(init_payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req_init, timeout=10) as resp:
            session_id = resp.headers.get("mcp-session-id")

        if not session_id:
            raise RuntimeError("MCP server did not return mcp-session-id header")

        headers["mcp-session-id"] = session_id

        # 2. Confirm initialized
        notif_payload = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        req_notif = urllib.request.Request(self.base_url, data=json.dumps(notif_payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req_notif, timeout=10) as _:
            pass

        # 3. Call tool
        tool_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        req_tool = urllib.request.Request(self.base_url, data=json.dumps(tool_payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req_tool, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
            for line in raw.splitlines():
                if line.startswith("data:"):
                    data = json.loads(line[5:].strip())
                    if "result" in data:
                        content = data["result"].get("content", [])
                        if content and content[0].get("type") == "text":
                            text = content[0].get("text", "")
                            try:
                                return json.loads(text)
                            except Exception:
                                return text
        return None

    def list_sources(self, notebook_id: str) -> List[Dict[str, Any]]:
        res = self.call_tool("sources_list", {"notebook_id": notebook_id})
        if isinstance(res, list):
            return res
        return []

    def add_text_source(self, notebook_id: str, title: str, content: str) -> Any:
        return self.call_tool("sources_add_text", {
            "notebook_id": notebook_id,
            "title": title,
            "content": content
        })


def main():
    parser = argparse.ArgumentParser(description="NotebookLM MCP CLI Helper")
    parser.add_argument("--notebook", default=TARGET_NOTEBOOK_ID, help="Notebook ID")
    parser.add_argument("--action", choices=["list", "add"], default="list", help="Action")
    parser.add_argument("--title", help="Source title")
    parser.add_argument("--content", help="Source text content")
    args = parser.parse_args()

    client = NotebookLmMcpClient()
    if args.action == "list":
        sources = client.list_sources(args.notebook)
        print(json.dumps(sources, indent=2))
    elif args.action == "add":
        if not args.title or not args.content:
            print("ERROR: --title and --content are required for add action.")
            sys.exit(1)
        res = client.add_text_source(args.notebook, args.title, args.content)
        print(f"[SUCCESS] Ingested source '{args.title}': {res}")


if __name__ == "__main__":
    main()
