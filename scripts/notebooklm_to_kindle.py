#!/usr/bin/env python3
"""
B-SDD NotebookLM-to-Kindle Autonomous Pipeline.
Pure Python Standard Library (ADR-002).
1. Connects to NotebookLM MCP server on 192.168.3.184:8002
2. Extracts all chapter sources via sources_list + sources_get_fulltext
3. Compiles EPUB 3.0 using pandoc with valid container metadata
4. Dispatches to Amazon Kindle via verified n8n gateway (NO CC, anti-E009)
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

NOTEBOOKLM_MCP_URL = os.environ.get("NOTEBOOKLM_MCP_URL", "http://192.168.3.184:8002/mcp")
KINDLE_WEBHOOK_URL = os.environ.get("KINDLE_WEBHOOK_URL", "https://n8n.exodus.pp.ua/webhook/dispatch-kindle-book")
SUPERVISOR_WEBHOOK_URL = os.environ.get("SUPERVISOR_WEBHOOK_URL", "https://n8n.exodus.pp.ua/webhook/bsdd-supervisor-result")
DEFAULT_TARGET_KINDLE = "tukroschu@kindle.com"
DEFAULT_SENDER = "tukroschu@gmail.com"


class NotebookLmMcpClient:
    def __init__(self, base_url: str = NOTEBOOKLM_MCP_URL):
        self.base_url = base_url

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "b-sdd-kindle-pipeline", "version": "1.0"}
            }
        }
        req_init = urllib.request.Request(self.base_url, data=json.dumps(init_payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req_init, timeout=15) as resp:
            session_id = resp.headers.get("mcp-session-id")

        if not session_id:
            raise RuntimeError("MCP server did not return mcp-session-id header")

        headers["mcp-session-id"] = session_id

        notif_payload = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        req_notif = urllib.request.Request(self.base_url, data=json.dumps(notif_payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req_notif, timeout=15) as _:
            pass

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

    def get_fulltext(self, notebook_id: str, source_id: str) -> str:
        res = self.call_tool("sources_get_fulltext", {"notebook_id": notebook_id, "source_id": source_id})
        return str(res) if res is not None else ""


def extract_chapters_from_notebook(client: NotebookLmMcpClient, notebook_id: str, staging_dir: Path) -> List[Path]:
    staging_dir.mkdir(parents=True, exist_ok=True)
    sources = client.list_sources(notebook_id)
    if not sources:
        raise RuntimeError(f"No sources found in notebook {notebook_id}")

    sources.sort(key=lambda s: s.get("title", ""))
    print(f"[*] Found {len(sources)} chapter sources in NotebookLM ({notebook_id})")

    chapter_files: List[Path] = []
    for idx, s in enumerate(sources):
        s_id = s.get("id")
        s_title = s.get("title", f"Chapter_{idx:02d}")
        print(f"    [{idx+1}/{len(sources)}] Fetching fulltext: {s_title} ({s_id})...")
        fulltext = client.get_fulltext(notebook_id, s_id)
        
        safe_title = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in s_title).strip()
        filename = f"{idx:02d}_{safe_title}.md".replace(" ", "_").replace("__", "_")
        target_path = staging_dir / filename
        
        content = fulltext.strip()
        if not content.startswith("#"):
            content = f"# {s_title}\n\n" + content
            
        target_path.write_text(content, encoding="utf-8")
        chapter_files.append(target_path)

    return chapter_files


def compile_epub(chapter_files: List[Path], output_epub: Path, title: str, author: str, lang: str = "uk") -> bool:
    print(f"\n=== [2/3] Compiling EPUB 3.0 via pandoc ===")
    print(f"Output File: {output_epub}")
    output_epub.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "pandoc",
        *[str(f) for f in chapter_files],
        "-o", str(output_epub),
        "--metadata", f"title={title}",
        "--metadata", f"author={author}",
        "--metadata", f"lang={lang}",
        "--metadata", "publisher=B-SDD Autonomous Core",
        "--toc", "--toc-depth=2"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[-] pandoc compilation failed:\n{res.stderr}", file=sys.stderr)
        return False

    size_kb = output_epub.stat().st_size / 1024
    print(f"[+] ✓ EPUB successfully compiled: {output_epub} ({size_kb:.1f} KB)")
    return True


def dispatch_to_kindle(epub_path: Path, subject: str, target: str = DEFAULT_TARGET_KINDLE) -> Tuple[bool, str]:
    print(f"\n=== [3/3] Dispatching to Kindle ({target}) ===")
    import mimetypes
    boundary = "----WebKitFormBoundaryBSddDispatch" + hex(int(datetime.now().timestamp()))[2:]
    
    with open(epub_path, "rb") as f:
        file_bytes = f.read()

    body = bytearray()
    # Field: subject
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="subject"\r\n\r\n'.encode("utf-8"))
    body.extend(f"{subject}\r\n".encode("utf-8"))

    # Field: data (file attachment)
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="data"; filename="{epub_path.name}"\r\n'.encode("utf-8"))
    body.extend(b"Content-Type: application/epub+zip\r\n\r\n")
    body.extend(file_bytes)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        KINDLE_WEBHOOK_URL,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            resp_body = resp.read().decode("utf-8")
            return True, f"HTTP {resp.status}: {resp_body}"
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(description="Autonomous NotebookLM-to-Kindle Book Pipeline")
    parser.add_argument("--notebook", default="b371bcda-77c6-4803-84e7-8aed42817454", help="NotebookLM Notebook ID")
    parser.add_argument("--title", default="FDE: Посібник інженера передового розгортання", help="Book Title")
    parser.add_argument("--author", default="Фань Бін (Fan Bing / XDash)", help="Book Author")
    parser.add_argument("--output", type=Path, default=Path("/home/vokov/projects/b-sdd/docs/fde_guide_ukrainian.epub"), help="Target EPUB path")
    parser.add_argument("--to", default=DEFAULT_TARGET_KINDLE, help="Target Kindle email")
    parser.add_argument("--dry-run", action="store_true", help="Compile only, skip dispatch")
    args = parser.parse_args()

    client = NotebookLmMcpClient()
    staging_dir = Path("/home/vokov/projects/b-sdd/build/kindle_book/staged")
    
    # 1. Extract from NotebookLM MCP
    chapter_files = extract_chapters_from_notebook(client, args.notebook, staging_dir)
    
    # 2. Compile EPUB 3.0
    ok = compile_epub(chapter_files, args.output, args.title, args.author)
    if not ok:
        sys.exit(1)

    # 3. Dispatch to Kindle
    if args.dry_run:
        print(f"[dry-run] Book compiled. Skipping Kindle dispatch to {args.to}")
        return

    sent, msg = dispatch_to_kindle(args.output, args.title, args.to)
    if sent:
        print(f"[+] Kindle delivery SUCCESS: {msg}")
    else:
        print(f"[-] Kindle delivery FAILED: {msg}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
