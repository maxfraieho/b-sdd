#!/usr/bin/env python3
"""
B-SDD Autonomous Supervisor Harness.
Listens for dispatch requests, coordinates task execution (scripts or agy CLI),
and guarantees closed-loop artifact delivery to NotebookLM (Invariant FL-01).
100% Pure Python Standard Library (ADR-002).
"""
import json
import logging
import os
import re
import shutil
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import urllib.error
from threading import Thread
from typing import Dict, List, Optional, Tuple, Any

PORT = 8161
PROJECT_DIR = os.path.expanduser("~/projects/b-sdd")
N8N_CALLBACK_WEBHOOK = "https://n8n.exodus.pp.ua/webhook/bsdd-supervisor-result"
NOTEBOOK_ID_METHODOLOGY = "205ee2ec-e0d2-4ba6-badf-44f2de02c7e2"
NOTEBOOK_ID_LEGAL = "6813ab1c-ac22-4c3c-9c8e-9dd67e35da99"
PRIMARY_NOTEBOOKS = [NOTEBOOK_ID_METHODOLOGY, NOTEBOOK_ID_LEGAL]
NOTEBOOKLM_MCP_URL = "http://192.168.3.184:8002/mcp"
AGY_CLI_PATH = os.path.expanduser("~/.local/bin/agy")

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
                "clientInfo": {"name": "bsdd-supervisor", "version": "1.1"}
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
        with urllib.request.urlopen(req_tool, timeout=30) as resp:
            raw_body = resp.read().decode("utf-8", errors="replace")

        # Parse SSE stream or JSON
        for line in raw_body.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                payload_str = line[5:].strip()
                data = json.loads(payload_str)
                if "result" in data:
                    content_list = data["result"].get("content", [])
                    if content_list and "text" in content_list[0]:
                        text = content_list[0]["text"]
                        try:
                            return json.loads(text)
                        except Exception:
                            # Handle python repr format e.g. SourceFulltext(...)
                            m = re.search(r"content=(['\"])(.*?)\1(?:,\s*url=|\))", text, re.DOTALL)
                            if m:
                                raw_str = m.group(2)
                                try:
                                    return raw_str.encode("utf-8").decode("unicode_escape")
                                except Exception:
                                    return raw_str
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
    step_clean = re.sub(r"^(OUTBOX_AGI_|INBOX_GEMINI_)", "", step_clean)
    step_clean = re.sub(rf"^{sprint_clean}_?", "", step_clean)
    return f"INBOX_GEMINI_{sprint_clean}_{step_clean}_REPORT"


def publish_report_to_notebooklm(
    sprint_id: str,
    step_name: str,
    report_path: Optional[str] = None,
    target_notebook_id: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Fallback Ingestion & Delivery Gate (Invariant FL-01).
    Ensures that the artifact is physically present in target NotebookLM notebooks.
    """
    source_title = determine_canonical_source_title(sprint_id, step_name)
    logging.info(f"Перевірка/публікація звіту в NotebookLM під назвою: {source_title}")

    client = NotebookLmMcpClient()
    notebooks_to_sync = list(PRIMARY_NOTEBOOKS)
    if target_notebook_id and target_notebook_id not in notebooks_to_sync:
        notebooks_to_sync.insert(0, target_notebook_id)

    # 1. Locate report content on disk
    target_file = None
    if report_path and os.path.isfile(report_path):
        target_file = report_path
    else:
        logs_dir = os.path.join(PROJECT_DIR, "logs")
        candidates = [
            os.path.join(logs_dir, f"{sprint_id}_{step_name}_report.json"),
            os.path.join(logs_dir, f"{sprint_id}_isolate_extended_skills_report.md"),
            os.path.join(logs_dir, f"{sprint_id}_isolate_extended_skills_report.json"),
            os.path.join(logs_dir, f"{sprint_id}_skills_refactor_report.json"),
            os.path.join(logs_dir, f"{sprint_id}_scout_report.json"),
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
            "message": "Report generated by supervisor."
        }, indent=2)

    all_synced = True
    for nb_id in notebooks_to_sync:
        try:
            existing_sources = client.list_sources(nb_id)
            existing_titles = {s.get("title") for s in existing_sources if isinstance(s, dict)}

            if source_title in existing_titles:
                logging.info(f"Джерело '{source_title}' вже присутнє в Notebook {nb_id}.")
                continue

            logging.info(f"Публікація артефакту '{source_title}' у Notebook {nb_id}...")
            client.add_text_source(
                notebook_id=nb_id,
                title=source_title,
                content=f"# {source_title}\n\n{content_body}\n"
            )
            logging.info(f"Успішно опубліковано '{source_title}' у Notebook {nb_id}.")
        except Exception as e:
            logging.error(f"Помилка публікації в Notebook {nb_id}: {e}")
            all_synced = False

    return all_synced, source_title


def execute_task_async(
    instruction_name: str,
    sprint_id: str,
    correlation_id: str = "",
    target_notebook_id: Optional[str] = None
):
    logging.info(f"Старт обробки завдання: {instruction_name} (sprint: {sprint_id}, corr: {correlation_id})")
    client = NotebookLmMcpClient()
    commands = []
    instruction_text = ""

    # 1. Fetch instruction text from NotebookLM
    try:
        candidate_nbs = [target_notebook_id] if target_notebook_id else PRIMARY_NOTEBOOKS
        for nb_id in candidate_nbs:
            if not nb_id:
                continue
            sources = client.list_sources(nb_id)
            matched_id = None
            for s in sources:
                if isinstance(s, dict) and s.get("title") == instruction_name:
                    matched_id = s.get("id")
                    break
            if matched_id:
                fulltext = client.call_tool("sources_get_fulltext", {
                    "notebook_id": nb_id,
                    "source_id": matched_id
                })
                if isinstance(fulltext, dict):
                    instruction_text = fulltext.get("content", "")
                elif isinstance(fulltext, str):
                    instruction_text = fulltext
                break

        if instruction_text:
            in_code_block = False
            in_exec_commands = False
            for line in instruction_text.splitlines():
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
                for line in instruction_text.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("python3 ") or stripped.startswith("pytest ") or stripped.startswith("bash "):
                        commands.append(stripped)
    except Exception as e:
        logging.warning(f"Помилка отримання інструкцій через MCP: {e}")

    logs = []
    failed = False
    failed_cmd = None

    proc_env = os.environ.copy()
    user_paths = ["/home/vokov/.local/bin", "/home/vokov/bin"]
    proc_env["PATH"] = ":".join(user_paths) + ":" + proc_env.get("PATH", "")

    # If no shell commands found, but instruction is an AGI directive: call agy CLI
    if not commands and instruction_name.startswith("OUTBOX_AGI_") and os.path.isfile(AGY_CLI_PATH):
        logging.info(f"Немає явних bash-команд. Запуск оркестратора AGI через agy CLI...")
        prompt_arg = instruction_text if instruction_text else f"Виконай інструкцію {instruction_name} для спринту {sprint_id}."
        cmd = f"{AGY_CLI_PATH} -p {json.dumps(prompt_arg)} --dangerously-skip-permissions"
        p = subprocess.run(cmd, shell=True, cwd=PROJECT_DIR, capture_output=True, text=True, env=proc_env)
        logs.append({
            "cmd": f"agy -p <{instruction_name}>",
            "code": p.returncode,
            "stdout": p.stdout[-1000:],
            "stderr": p.stderr[-1000:]
        })
        if p.returncode != 0:
            failed = True
            failed_cmd = "agy_cli_execution"
    elif not commands:
        commands = ["echo 'No explicit commands found. Dry-run success.'"]

    if commands and not failed:
        pytest_bin = shutil.which("pytest", path=proc_env["PATH"]) or "/home/vokov/.local/bin/pytest"
        for c in commands:
            if c.strip().startswith("python3 -m pytest"):
                c = c.replace("python3 -m pytest", pytest_bin)
            elif c.strip().startswith("pytest"):
                c = pytest_bin + c.strip()[6:]
            logging.info(f"Виконання: {c}")
            p = subprocess.run(c, shell=True, cwd=PROJECT_DIR, capture_output=True, text=True, env=proc_env)
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
    synced, source_title = publish_report_to_notebooklm(sprint_id, instruction_name, target_notebook_id=target_notebook_id)
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
        "correlation_id": correlation_id,
        "status": status,
        "report_name": source_title,
        "source_title": source_title,
        "notebooklm_synced": synced,
        "target_notebook_id": target_notebook_id or NOTEBOOK_ID_METHODOLOGY,
        "failed_command": failed_cmd,
        "require_user": failed,
        "logs": logs
    }
    try:
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "B-SDD-Supervisor/1.1"
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
            self.wfile.write(b'{"status": "UP", "service": "bsdd-supervisor", "version": "1.1", "port": 8161}\n')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/dispatch":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            instruction_name = body.get("instruction_name", "UNKNOWN")
            sprint_id = body.get("sprint_id", "sprint_021")
            correlation_id = body.get("correlation_id", "")
            target_notebook_id = body.get("notebook_id", "")

            logging.info(f"Отримано POST /dispatch: {instruction_name} (sprint: {sprint_id}, corr: {correlation_id})")

            self.send_response(202)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "QUEUED"}\n')

            Thread(
                target=execute_task_async,
                args=(instruction_name, sprint_id, correlation_id, target_notebook_id),
                daemon=True
            ).start()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        logging.info("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args))


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), DispatchHandler)
    logging.info(f"B-SDD Supervisor v1.1 слухає на 0.0.0.0:{PORT}...")
    server.serve_forever()
