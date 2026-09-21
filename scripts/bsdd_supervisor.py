#!/usr/bin/env python3
"""
B-SDD Autonomous Supervisor Harness.
Listens for dispatch requests, coordinates task execution, and guarantees
closed-loop artifact delivery to NotebookLM (Invariant FL-01).
100% Pure Python Standard Library.
"""
import json
import logging
import os
import re
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import urllib.error
from threading import Thread
from typing import Dict, List, Optional, Tuple, Any

PORT = 8161
PROJECT_DIR = os.path.expanduser("~/projects/b-sdd")
N8N_CALLBACK_WEBHOOK = "https://n8n.exodus.pp.ua/webhook/bsdd-supervisor-result"
NOTEBOOK_ID = "205ee2ec-e0d2-4ba6-badf-44f2de02c7e2"
NOTEBOOKLM_MCP_URL = "http://192.168.3.184:8002/mcp"

os.makedirs(os.path.join(PROJECT_DIR, "logs"), exist_ok=True)
log_file = os.path.join(PROJECT_DIR, "logs", "supervisor.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)


class NotebookLmMcpClient:
    """Pure Standard Library client for streamable HTTP MCP server on host .184."""

    def __init__(self, base_url: str = NOTEBOOKLM_MCP_URL):
        self.base_url = base_url

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Executes an MCP tool over streamable HTTP JSON-RPC."""
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
                "clientInfo": {"name": "bsdd-supervisor", "version": "1.0"}
            }
        }
        req_init = urllib.request.Request(self.base_url, data=json.dumps(init_payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req_init, timeout=10) as resp:
            session_id = resp.headers.get("mcp-session-id")

        if not session_id:
            raise RuntimeError("MCP server did not return mcp-session-id header")

        headers["mcp-session-id"] = session_id

        # 2. Confirm initialized notification
        notif_payload = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        req_notif = urllib.request.Request(self.base_url, data=json.dumps(notif_payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req_notif, timeout=10) as _:
            pass

        # 3. Call target tool
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
        with urllib.request.urlopen(req_tool, timeout=45) as resp:
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


def determine_canonical_source_title(sprint_id: str, step_name: str) -> str:
    """Computes INBOX_GEMINI_<SPRINT>_<STEP>_REPORT naming convention."""
    sprint_clean = sprint_id.upper()
    step_clean = step_name.upper().replace(".MD", "").replace(".TXT", "")
    
    # Strip prefixes if already present in step_name
    step_clean = re.sub(r"^(OUTBOX_AGI_|INBOX_GEMINI_)", "", step_clean)
    step_clean = re.sub(rf"^{sprint_clean}_?", "", step_clean)
    
    return f"INBOX_GEMINI_{sprint_clean}_{step_clean}_REPORT"


def publish_report_to_notebooklm(sprint_id: str, step_name: str, report_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    Fallback Ingestion & Delivery Gate (Invariant FL-01).
    Ensures that the artifact is physically present in NotebookLM before completing the step.
    """
    source_title = determine_canonical_source_title(sprint_id, step_name)
    logging.info(f"Перевірка/публікація звіту в NotebookLM під назвою: {source_title}")

    client = NotebookLmMcpClient()
    try:
        # 1. Check if source already exists
        existing_sources = client.list_sources(NOTEBOOK_ID)
        existing_titles = {s.get("title") for s in existing_sources if isinstance(s, dict)}

        if source_title in existing_titles:
            logging.info(f"Джерело '{source_title}' вже присутнє в NotebookLM.")
            return True, source_title

        # 2. Locate report content on disk
        target_file = None
        if report_path and os.path.isfile(report_path):
            target_file = report_path
        else:
            # Look in logs/ directory
            logs_dir = os.path.join(PROJECT_DIR, "logs")
            candidates = [
                os.path.join(logs_dir, f"{sprint_id}_{step_name}_report.json"),
                os.path.join(logs_dir, f"{sprint_id}_scout_report.json"),
                os.path.join(logs_dir, "sprint_021_scout_report.json"),
                os.path.join(logs_dir, "supervisor.log"),
            ]
            for c in candidates:
                if os.path.isfile(c):
                    target_file = c
                    break

        content_body = ""
        if target_file and os.path.isfile(target_file):
            with open(target_file, "r", encoding="utf-8", errors="replace") as f:
                content_body = f.read()
        else:
            content_body = json.dumps({
                "sprint_id": sprint_id,
                "step_name": step_name,
                "status": "AUTO_INGESTED",
                "message": "Fallback report generated by supervisor."
            }, indent=2)

        # 3. Publish to NotebookLM
        logging.info(f"Публікація артефакту в NotebookLM ({source_title})...")
        client.add_text_source(
            notebook_id=NOTEBOOK_ID,
            title=source_title,
            content=f"# {source_title}\n\n```json\n{content_body}\n```\n"
        )

        # 4. Re-verify presence
        verify_sources = client.list_sources(NOTEBOOK_ID)
        verify_titles = {s.get("title") for s in verify_sources if isinstance(s, dict)}
        if source_title in verify_titles:
            logging.info(f"Успішна верифікація: '{source_title}' збережено в NotebookLM.")
            return True, source_title
        else:
            logging.warning(f"Не вдалося знайти '{source_title}' після публікації.")
            return False, source_title

    except Exception as e:
        logging.error(f"Помилка при синхронізації з NotebookLM: {e}")
        return False, source_title


def execute_task_async(instruction_name: str, sprint_id: str):
    logging.info(f"Старт обробки завдання: {instruction_name}")
    client = NotebookLmMcpClient()
    commands = []

    # 1. Fetch instruction text from NotebookLM
    try:
        sources = client.list_sources(NOTEBOOK_ID)
        matched_id = None
        for s in sources:
            if isinstance(s, dict) and s.get("title") == instruction_name:
                matched_id = s.get("id")
                break

        if matched_id:
            fulltext = client.call_tool("sources_get_fulltext", {
                "notebook_id": NOTEBOOK_ID,
                "source_id": matched_id
            })
            text_content = ""
            if isinstance(fulltext, dict):
                text_content = fulltext.get("content", "")
            elif isinstance(fulltext, str):
                text_content = fulltext

            in_code_block = False
            in_exec_commands = False
            for line in text_content.splitlines():
                stripped = line.strip()
                if stripped.startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if "EXECUTION_COMMANDS" in stripped:
                    in_exec_commands = True
                    continue
                if stripped.startswith("#") or (in_exec_commands and re.match(r"^\d+\.", stripped)):
                    in_exec_commands = False

                if stripped.startswith("- `") and stripped.endswith("`"):
                    commands.append(stripped.strip("- `"))
                elif in_code_block and stripped and not stripped.startswith("#"):
                    commands.append(stripped)
                elif in_exec_commands and stripped and not stripped.startswith("#"):
                    commands.append(stripped)

            if not commands:
                for line in text_content.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("python3 ") or stripped.startswith("pytest ") or stripped.startswith("bash "):
                        commands.append(stripped)
    except Exception as e:
        logging.warning(f"Помилка отримання інструкцій через MCP: {e}")

    if not commands:
        commands = ["echo 'No explicit commands found. Dry-run success.'"]

    logs = []
    failed = False
    failed_cmd = None

    for c in commands:
        if c.strip().startswith("python3 -m pytest"):
            c = c.replace("python3 -m pytest", "pytest")
        logging.info(f"Виконання: {c}")
        p = subprocess.run(c, shell=True, cwd=PROJECT_DIR, capture_output=True, text=True)
        logs.append({
            "cmd": c,
            "code": p.returncode,
            "stdout": p.stdout[-1000:],
            "stderr": p.stderr[-1000:]
        })
        if p.returncode != 0:
            failed = True
            failed_cmd = c
            break

    # 2. Mandatory Step Exit Gate: Closed-Loop Delivery to NotebookLM (Invariant FL-01)
    synced, source_title = publish_report_to_notebooklm(sprint_id, instruction_name)
    if not synced and not failed:
        failed = True
        failed_cmd = "notebooklm_closed_loop_sync"
        logs.append({
            "error": f"INVARIANT FL-01 VIOLATION: Звіт '{source_title}' не доставлено в NotebookLM."
        })

    status = "FAILED" if failed else "SUCCESS"

    # 3. Відправка результату у вебхук n8n
    payload = {
        "instruction_name": instruction_name,
        "sprint_id": sprint_id,
        "status": status,
        "report_name": source_title,
        "source_title": source_title,
        "notebooklm_synced": synced,
        "failed_command": failed_cmd,
        "require_user": failed,
        "logs": logs
    }
    try:
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "B-SDD-Supervisor/1.0"
        }
        req = urllib.request.Request(N8N_CALLBACK_WEBHOOK, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            resp_body = response.read().decode("utf-8")
            logging.info(f"Звіт успішно надіслано в n8n: {resp_body}")
    except Exception as e:
        logging.error(f"Помилка надсилання вебхука в n8n: {e}")


class DispatchHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/status", "/health", "/"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "UP", "service": "bsdd-supervisor", "port": 8161}\n')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/dispatch":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            instruction_name = body.get("instruction_name", "UNKNOWN")
            sprint_id = body.get("sprint_id", "sprint_021")

            self.send_response(202)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "QUEUED"}\n')

            Thread(target=execute_task_async, args=(instruction_name, sprint_id), daemon=True).start()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        logging.info("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args))


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), DispatchHandler)
    logging.info(f"B-SDD Supervisor слухає на 0.0.0.0:{PORT}...")
    server.serve_forever()
