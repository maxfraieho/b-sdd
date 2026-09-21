#!/usr/bin/env python3
"""Deploy workflow_bsdd_sdk.ts to n8n via MCP JSON-RPC API."""
import urllib.request
import json
import sys

MCP_URL = "https://n8n.exodus.pp.ua/mcp-server/http"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhYjg1MjVmYy0wYjBhLTQzZDUtYmJmMS02ZjJkNjBiY2M3M2UiLCJpc3MiOiJuOG4iLCJhdWQiOiJtY3Atc2VydmVyLWFwaSIsImp0aSI6ImFmMzhjYzFlLTRlMTEtNGIxZS04NGEwLTZhMzY4OWFlMDI4NiIsImlhdCI6MTc3NjA3NDgyNX0.2sseKoimZzBd70byLWfxBQRD9M41bMFsa7hb6qG_tH8"

def call_mcp_tool(name: str, arguments: dict):
    req_body = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": name,
            "arguments": arguments
        },
        "id": 1
    }
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    req = urllib.request.Request(MCP_URL, data=json.dumps(req_body).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
        for line in raw.splitlines():
            if line.startswith("data: "):
                data = json.loads(line[6:])
                if "error" in data:
                    print(f"MCP Error in {name}:", data["error"])
                    return None
                return data.get("result")
    return None

def main():
    with open("/home/vokov/projects/b-sdd/scripts/workflow_bsdd_sdk.ts", "r") as f:
        code = f.read()

    print("[1/3] Validating workflow code...")
    res = call_mcp_tool("validate_workflow", {"code": code})
    print("Validation result:", json.dumps(res, indent=2))

    print("\n[2/3] Updating workflow 6FzcypHVkvqrxf9o...")
    res = call_mcp_tool("update_workflow", {"workflowId": "6FzcypHVkvqrxf9o", "code": code})
    print("Update result:", json.dumps(res, indent=2))

    print("\n[3/3] Publishing workflow 6FzcypHVkvqrxf9o...")
    res = call_mcp_tool("publish_workflow", {"workflowId": "6FzcypHVkvqrxf9o"})
    print("Publish result:", json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
