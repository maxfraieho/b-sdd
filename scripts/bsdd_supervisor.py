#!/usr/bin/env python3
"""
B-SDD Autonomous Supervisor Harness v1.3.
Listens for dispatch requests, coordinates task execution via canonical ./run_b_sdd.sh,
enforces thread-safe deduplication with cooldown mutex, provides dynamic circuit breaker
and stateful recovery for Laya Decision Engine on Pixel 7 (192.168.3.251:9623),
and guarantees closed-loop artifact delivery to NotebookLM (Invariant FL-01).
100% Pure Python Standard Library (ADR-002).
"""
import json
import logging
import os
import re
import shutil
import shlex
import subprocess
import time
import hashlib
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import urllib.error
from threading import Lock, Thread
from typing import Dict, List, Optional, Tuple, Any


def load_env_file(dotenv_path: Optional[str] = None) -> None:
    """Pure stdlib loader for .env files without external dependencies."""
    candidates = []
    if dotenv_path:
        candidates.append(dotenv_path)
    candidates.extend([
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"),
        os.path.join(os.getcwd(), ".env"),
        os.path.expanduser("~/projects/b-sdd-feedback-loop/daemon/.env"),
        os.path.expanduser("~/projects/b-sdd-feedback-loop/.env"),
        os.path.expanduser("~/projects/b-sdd/.env")
    ])
    for p in candidates:
        if os.path.isfile(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
                break
            except Exception:
                pass


load_env_file()

PORT = int(os.getenv("SUPERVISOR_PORT", os.getenv("PORT", "8161")))
PROJECT_DIR = os.getenv("PROJECT_DIR", os.path.expanduser("~/projects/b-sdd"))
N8N_CALLBACK_WEBHOOK = os.getenv("N8N_CALLBACK_WEBHOOK", "https://n8n.exodus.pp.ua/webhook/bsdd-supervisor-result")
NOTEBOOK_ID_METHODOLOGY = os.getenv("NOTEBOOK_ID_METHODOLOGY", "205ee2ec-e0d2-4ba6-badf-44f2de02c7e2")
NOTEBOOK_ID_LEGAL = os.getenv("NOTEBOOK_ID_LEGAL", "6813ab1c-ac22-4c3c-9c8e-9dd67e35da99")
PRIMARY_NOTEBOOKS = [NOTEBOOK_ID_METHODOLOGY, NOTEBOOK_ID_LEGAL]
NOTEBOOKLM_MCP_URL = os.getenv("NOTEBOOKLM_MCP_URL", "http://192.168.3.184:8002/mcp")
AGY_CLI_PATH = os.getenv("AGY_CLI_PATH", os.path.expanduser("~/.local/bin/agy"))
BSDD_NODE_IP = os.getenv("BSDD_NODE_IP", "192.168.3.161")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8717667434:AAFWddh_xwTfMVHW7puxrlIFprbO9m_Au7Y")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6412868393")
COOLDOWN_SECONDS = float(os.getenv("COOLDOWN_SECONDS", "300.0"))

CLUSTER_HEALTH_PATH = os.getenv("CLUSTER_HEALTH_PATH", "/tmp/b_sdd_cluster_health.json")
UTOPIA_WORM_HOST = os.getenv("UTOPIA_WORM_HOST", "192.168.3.251")
UTOPIA_WORM_PORT = int(os.getenv("UTOPIA_WORM_PORT", "9622"))

LAYA_HOST = os.getenv("LAYA_HOST", "192.168.3.251")
LAYA_PORT = int(os.getenv("LAYA_PORT", "9623"))
LAYA_TIMEOUT = float(os.getenv("LAYA_TIMEOUT", "2.5"))

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

# Mutex & Cooldown Task Tracking
task_lock = Lock()
active_tasks: Dict[str, float] = {}
completed_tasks: Dict[str, float] = {}


def is_duplicate_task(instruction_name: str, sprint_id: str) -> bool:
    """Checks whether task is actively running or completed within cooldown window."""
    if sprint_id == "smoke_test" or "PING" in instruction_name or "TEST" in instruction_name:
        return False
    now = time.time()
    with task_lock:
        expired = [k for k, t in completed_tasks.items() if now - t > COOLDOWN_SECONDS]
        for k in expired:
            del completed_tasks[k]

        keys = [k for k in (instruction_name, sprint_id) if k and k != "UNKNOWN"]
        for k in keys:
            if k in active_tasks:
                return True
            if k in completed_tasks and (now - completed_tasks[k] < COOLDOWN_SECONDS):
                return True
        return False



def mark_task_active(instruction_name: str, sprint_id: str) -> None:
    """Marks task identifiers as actively running."""
    now = time.time()
    with task_lock:
        if instruction_name and instruction_name != "UNKNOWN":
            active_tasks[instruction_name] = now
        if sprint_id and sprint_id != "UNKNOWN":
            active_tasks[sprint_id] = now


def mark_task_completed(instruction_name: str, sprint_id: str) -> None:
    """Transitions task from active to completed with cooldown timestamp."""
    now = time.time()
    with task_lock:
        if instruction_name and instruction_name != "UNKNOWN":
            active_tasks.pop(instruction_name, None)
            completed_tasks[instruction_name] = now
        if sprint_id and sprint_id != "UNKNOWN":
            active_tasks.pop(sprint_id, None)
            completed_tasks[sprint_id] = now


def send_telegram_alert(text: str) -> bool:
    """Dispatches state transition alerts to operator Telegram."""
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        logging.warning("Telegram alert skipped: missing credentials")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            logging.info(f"Telegram alert dispatched successfully (status {resp.status})")
            return resp.status == 200
    except Exception as e:
        logging.error(f"Failed to dispatch Telegram alert: {e}")
        return False


def check_cluster_state() -> Tuple[bool, bool, Dict[str, Any]]:
    """
    Reads /tmp/b_sdd_cluster_health.json.
    Returns (is_degraded, is_worm_up, full_report).
    """
    is_degraded = False
    is_worm_up = True
    report: Dict[str, Any] = {}

    if os.path.isfile(CLUSTER_HEALTH_PATH):
        try:
            with open(CLUSTER_HEALTH_PATH, "r", encoding="utf-8") as f:
                report = json.load(f)
            if report.get("overall_status") == "DOWN":
                is_degraded = True
            for svc in report.get("services", []):
                sid = svc.get("service_id", "")
                is_up = svc.get("is_up", False)
                if sid == "laya_decision_engine" and not is_up:
                    is_degraded = True
                if sid == "utopia_db_worm" and not is_up:
                    is_worm_up = False
        except Exception as e:
            logging.warning(f"Помилка читання кешу здоров'я кластера {CLUSTER_HEALTH_PATH}: {e}")
    else:
        # Fallback quick socket probes
        try:
            with socket.create_connection((LAYA_HOST, LAYA_PORT), timeout=0.3):
                pass
        except Exception:
            is_degraded = True
        try:
            with socket.create_connection((UTOPIA_WORM_HOST, UTOPIA_WORM_PORT), timeout=0.3):
                pass
        except Exception:
            is_worm_up = False

    return is_degraded, is_worm_up, report


def record_worm_entry(sprint_id: str, correlation_id: str, status: str, worm_up: bool, target_repo: str) -> str:
    """Records immutable WORM transaction to local ledger and remote daemon if online."""
    worm_tx_id = f"WORM_{sprint_id}_{hashlib.sha256(f'{correlation_id}:{time.time()}'.encode()).hexdigest()[:12]}"
    entry = {
        "tx_id": worm_tx_id,
        "sprint_id": sprint_id,
        "correlation_id": correlation_id,
        "status": status,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "synced": worm_up
    }
    local_worm_path = os.path.join(target_repo, "docs", "utopia_local_worm.jsonl")
    try:
        os.makedirs(os.path.dirname(local_worm_path), exist_ok=True)
        with open(local_worm_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        logging.info(f"Local WORM record written: {local_worm_path} (tx: {worm_tx_id})")
    except Exception as ex:
        logging.error(f"Failed to append local WORM entry: {ex}")

    if worm_up:
        try:
            worm_url = f"http://{UTOPIA_WORM_HOST}:{UTOPIA_WORM_PORT}/worm"
            req = urllib.request.Request(
                worm_url,
                data=json.dumps(entry).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                logging.info(f"WORM transaction {worm_tx_id} committed to Utopia DB daemon (status {resp.status})")
        except Exception as ex:
            logging.warning(f"Failed to post to Utopia DB daemon: {ex}. Retained in local queue.")
    else:
        logging.warning(f"Utopia DB WORM offline. Transaction {worm_tx_id} queued in {local_worm_path}")

    return worm_tx_id


class LayaClient:
    """Zero-dependency HTTP client for Laya System 1 decision engine on Podroid."""

    def __init__(self, host: str = LAYA_HOST, port: int = LAYA_PORT, timeout: float = LAYA_TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{self.host}:{self.port}"

    def check_health(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Queries GET /health endpoint."""
        to = timeout or self.timeout
        url = f"{self.base_url}/health"
        req = urllib.request.Request(url, headers={"User-Agent": "B-SDD-LayaClient/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=to) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
                return {"status": "down", "error": f"HTTP {resp.status}"}
        except Exception as e:
            return {"status": "down", "error": str(e)}

    def classify_heuristic(
        self,
        state: Dict[str, Any],
        questions: Optional[Dict[str, Any]] = None,
        instruction_name: str = "",
        directive: str = ""
    ) -> Dict[str, Any]:
        """Static heuristic classifier when Podroid Laya engine is asleep or unreachable."""
        combined_text = " ".join([
            instruction_name,
            directive,
            str(state.get("instruction_name", "")),
            str(state.get("task", "")),
            str(state.get("directive", "")),
            str(state.get("sprint_id", ""))
        ]).lower()

        if any(k in combined_text for k in ("ui", "frontend", "css", "html", "cockpit", "astryx", "web", "panel", "view", "react", "component", "canvas")):
            domain = "ui"
        elif any(k in combined_text for k in ("skill", "skills", "catalog", "golden", "dump_skills", "crystalliz")):
            domain = "skills"
        elif any(k in combined_text for k in ("podroid", "watchdog", "deploy", "systemd", "alpine", "daemon", "infra", "network", "n8n", "pixel", "port")):
            domain = "infrastructure"
        else:
            domain = "core"

        skills_map = {
            "core": ["b-sdd", "intent-continuity", "safe-refactor"],
            "ui": ["frontend-design", "make-interfaces-feel-better", "web-artifacts-builder"],
            "skills": ["skill-creator", "skill-audit", "writing-skills"],
            "infrastructure": ["cli-developer", "mcp-builder", "defense-in-depth"],
        }
        rec_skills = skills_map.get(domain, skills_map["core"])
        skills_formatted = ", ".join(f"@{s}" for s in rec_skills)

        return {
            "domain": domain,
            "p_violation": 0.02,
            "choice": "PROCEED",
            "score": 0.98,
            "noul": True,
            "decision": "PROCEED",
            "action": "AUTO_EXECUTE",
            "recommended_skills": rec_skills,
            "skills_formatted": skills_formatted
        }

    def query_decision(
        self,
        state: Dict[str, Any],
        questions: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Queries non-autoregressive decision from Laya engine with graceful fallback."""
        to = timeout or self.timeout
        url = f"{self.base_url}/predict"
        payload = {
            "state": state,
            "questions": questions or {},
            "timestamp": time.time()
        }
        try:
            body = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=body,
                headers={"Content-Type": "application/json", "User-Agent": "B-SDD-LayaClient/1.0"}
            )
            t0 = time.perf_counter()
            with urllib.request.urlopen(req, timeout=to) as resp:
                elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
                if resp.status == 200:
                    raw_data = resp.read().decode("utf-8")
                    data = json.loads(raw_data)
                    data["fallback"] = False
                    data["latency_ms"] = elapsed_ms
                    return data
                return self._fallback_response(state, questions or {}, f"HTTP {resp.status}")
        except Exception as e:
            return self._fallback_response(state, questions or {}, str(e))

    def _fallback_response(
        self,
        state: Dict[str, Any],
        questions: Dict[str, Any],
        error_msg: str
    ) -> Dict[str, Any]:
        """Local heuristic fallback when Podroid is asleep or unreachable."""
        heuristic = self.classify_heuristic(state, questions)
        return {
            "fallback": True,
            "status": "degraded",
            "decision": heuristic["decision"],
            "action": heuristic["action"],
            "choice": heuristic["choice"],
            "score": heuristic["score"],
            "noul": heuristic["noul"],
            "domain": heuristic["domain"],
            "p_violation": heuristic["p_violation"],
            "recommended_skills": heuristic["recommended_skills"],
            "skills_formatted": heuristic["skills_formatted"],
            "confidence": 0.5,
            "latency_ms": 0.0,
            "model": "local-heuristic-fallback",
            "error": error_msg,
            "note": "Podroid Laya engine asleep or unreachable; safe heuristic applied."
        }


class LayaCircuitBreaker:
    """
    Finite State Machine / Circuit Breaker for Laya Decision Engine on Pixel 7.
    Tracks health state ('ONLINE' <-> 'OFFLINE') with anti-spam stateful alerting.
    """

    def __init__(self, host: str = LAYA_HOST, port: int = LAYA_PORT):
        self.host = host
        self.port = port
        self.state = "ONLINE"  # 'ONLINE' | 'OFFLINE'
        self.lock = Lock()

    def query_with_recovery(
        self,
        client: LayaClient,
        state: Dict[str, Any],
        questions: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], str]:
        """Queries Laya with thread-safe state machine transitions and debounced alerting."""
        with self.lock:
            decision = client.query_decision(state=state, questions=questions)
            is_fallback = decision.get("fallback", False)

            # Перехід Online -> Offline
            if is_fallback and self.state == "ONLINE":
                self.state = "OFFLINE"
                err = decision.get("error", "unreachable")
                logging.warning(f"[CIRCUIT BREAKER] Laya перейшла в OFFLINE: {err}")
                send_telegram_alert(
                    f"⚠️ [ALERT: LAYA OFFLINE] Вузол Laya на Pixel 7 ({self.host}:{self.port}) недоступний ({err})!\n"
                    f"🤖 Agy переходить в автономний режим локальних евристик."
                )

            # Перехід Offline -> Online (Самовідновлення)
            elif not is_fallback and self.state == "OFFLINE":
                self.state = "ONLINE"
                logging.info(f"[CIRCUIT BREAKER] Laya відновила зв'язок (RECOVERED -> ONLINE)")
                send_telegram_alert(
                    f"🟢 [RECOVERED: LAYA ONLINE] Зв'язок із моделлю Laya на Pixel 7 ({self.host}:{self.port}) відновлено!\n"
                    f"🧠 Agy повертається до використання нейромоделі прийняття рішень."
                )

            return decision, self.state


laya_client = LayaClient(host=LAYA_HOST, port=LAYA_PORT, timeout=LAYA_TIMEOUT)
laya_breaker = LayaCircuitBreaker(host=LAYA_HOST, port=LAYA_PORT)


def perform_preflight_hook(
    instruction_name: str = "",
    directive: str = "",
    sprint_id: str = ""
) -> Dict[str, Any]:
    """Preflight hook querying Laya client for decision context."""
    try:
        from src.core.laya_client import get_laya_client
        return get_laya_client().predict(
            instruction_name=instruction_name,
            directive=directive,
            sprint_id=sprint_id
        )
    except Exception:
        # Fallback to local heuristic
        return {
            "domain": "core",
            "choice": "PROCEED",
            "score": 0.98,
            "confidence": 0.95,
            "skills_formatted": "@b-sdd, @intent-continuity, @safe-refactor",
            "recommended_skills": ["b-sdd", "intent-continuity", "safe-refactor"],
            "fallback": True
        }




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
                "clientInfo": {"name": "bsdd-supervisor", "version": "1.3"}
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
                payload = json.loads(line[5:].strip())
                if "result" in payload:
                    res = payload["result"]
                    if isinstance(res, dict) and "content" in res:
                        for c in res["content"]:
                            if isinstance(c, dict) and c.get("type") == "text":
                                txt = c.get("text", "")
                                try:
                                    return json.loads(txt)
                                except Exception:
                                    return txt
                    return res
                if "error" in payload:
                    raise RuntimeError(f"MCP Tool Error: {payload['error']}")
        return None

    def list_sources(self, notebook_id: str) -> List[Dict[str, Any]]:
        """Lists sources in a given notebook."""
        try:
            res = self.call_tool("sources_list", {"notebook_id": notebook_id})
            if isinstance(res, list):
                return res
            if isinstance(res, dict) and "sources" in res:
                return res["sources"]
            return []
        except Exception as e:
            logging.warning(f"Failed to list sources in {notebook_id}: {e}")
            return []


def extract_step_from_instruction(instruction_name: str) -> str:
    """Extracts step name from INSTRUCTION string."""
    m = re.search(r"OUTBOX_AGI_[A-Za-z0-9]+_([A-Za-z0-9_]+)", instruction_name)
    if m:
        return m.group(1).upper()
    return "STEP"


def find_latest_report(sprint_id: str, t_start: Optional[float] = None) -> Tuple[Optional[str], Optional[str]]:
    """Finds latest report content and filename matching the sprint created during current task run."""
    logs_dir = os.path.join(PROJECT_DIR, "logs")
    if not os.path.exists(logs_dir):
        return None, None

    matching_files = []
    for f in os.listdir(logs_dir):
        if sprint_id in f and (f.endswith(".json") or f.endswith(".md") or f.endswith(".txt")):
            fp = os.path.join(logs_dir, f)
            if t_start is not None:
                # Disregard stale files generated before current run started
                if os.path.getmtime(fp) < t_start - 1.0:
                    continue
            matching_files.append(fp)

    if not matching_files:
        return None, None

    matching_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest = matching_files[0]
    try:
        with open(latest, "r", encoding="utf-8") as f:
            return f.read(), os.path.basename(latest)
    except Exception as e:
        logging.error(f"Помилка читання логу {latest}: {e}")
        return None, None


def publish_report_to_notebooklm(
    sprint_id: str,
    instruction_name: str,
    status: str = "SUCCESS",
    target_notebook_id: Optional[str] = None,
    target_repo: Optional[str] = None,
    extra_content: str = "",
    t_start: Optional[float] = None,
    failed_cmd: str = ""
) -> Tuple[bool, str]:
    """Publishes execution telemetry to NotebookLM (Invariant FL-01). Enforces Anti-False-Positive Guard."""
    step_name = extract_step_from_instruction(instruction_name)
    repo_dir = target_repo or PROJECT_DIR

    if status == "FAILED":
        source_title = f"INBOX_GEMINI_{sprint_id.upper()}_{step_name}_FAILED_REPORT"
    else:
        source_title = f"INBOX_GEMINI_{sprint_id.upper()}_{step_name}_REPORT"

    content, fname = find_latest_report(sprint_id, t_start=t_start)
    # If status is FAILED, NEVER publish a report claiming SUCCESS!
    if status == "FAILED" or not content or (content and status == "FAILED" and "Status:** SUCCESS" in content):
        git_status = subprocess.run(["git", "status", "--short"], cwd=repo_dir, capture_output=True, text=True).stdout
        git_rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=repo_dir, capture_output=True, text=True).stdout.strip()
        status_label = "❌ FAILED" if status == "FAILED" else "✅ SUCCESS"
        content = (
            f"# Execution Report: {source_title}\n\n"
            f"- **Instruction:** {instruction_name}\n"
            f"- **Sprint:** {sprint_id}\n"
            f"- **Status:** {status_label}\n"
            f"- **Failed Reason / Command:** {failed_cmd if status == 'FAILED' else 'None'}\n"
            f"- **Git Revision:** {git_rev}\n"
            f"- **Host:** {BSDD_NODE_IP}\n\n"
            f"## Execution Telemetry\n"
            f"{extra_content}\n\n"
            f"## Git Status\n```\n{git_status}\n```\n\n"
            f"Generated autonomously by B-SDD Supervisor v1.4 (Anti-False-Positive Guard Active)."
        )

    client = NotebookLmMcpClient()
    destinations = list(PRIMARY_NOTEBOOKS)
    if target_notebook_id and target_notebook_id not in destinations:
        destinations.append(target_notebook_id)

    success_any = False
    for nb_id in destinations:
        try:
            logging.info(f"Публікація артефакту '{source_title}' у NotebookLM ({nb_id})...")
            client.call_tool("sources_add_text", {
                "notebook_id": nb_id,
                "title": source_title,
                "content": content
            })
            logging.info(f"Артефакт успішно опубліковано у NotebookLM ({nb_id})!")
            success_any = True
        except Exception as e:
            logging.error(f"Помилка публікації артефакту в NotebookLM ({nb_id}): {e}")

    return success_any, source_title


def find_sprint_commands(sprint_id: str) -> List[str]:
    """Finds explicit script execution commands for the sprint if present."""
    script_candidates = [
        os.path.join(PROJECT_DIR, f"run_{sprint_id}.sh"),
        os.path.join(PROJECT_DIR, "scripts", f"run_{sprint_id}.sh")
    ]
    for sc in script_candidates:
        if os.path.exists(sc) and os.access(sc, os.X_OK):
            return [sc]
    return []


def verify_task_postconditions(
    sprint_id: str,
    instruction_name: str,
    repo_dir: str,
    logs: List[Dict[str, Any]],
    t_start: float
) -> Tuple[bool, str]:
    """
    Mandatory Postcondition Guard (Defends against tautological success).
    Requires actual verification before marking status as SUCCESS.
    """
    instr_upper = instruction_name.upper()
    sprint_upper = sprint_id.upper()

    # 1. Inspect all logged subprocess results
    for log_item in logs:
        code = log_item.get("code")
        if code is not None and code != 0:
            return False, f"Command '{log_item.get('cmd')}' failed with exit code {code}"
        stderr = log_item.get("stderr", "")
        # Detect fatal exceptions in stderr
        if "Traceback (most recent call last)" in stderr:
            return False, f"Unhandled traceback in stderr: {stderr[-250:].strip()}"
        if "google.auth.exceptions" in stderr or "RefreshError" in stderr or "invalid_grant" in stderr:
            return False, f"Authentication failure in stderr: {stderr[-250:].strip()}"
        if "ConnectionRefusedError" in stderr:
            return False, f"Connection refused error in stderr: {stderr[-250:].strip()}"

    # 2. Kindle & Documentation Delivery Postconditions
    if any(k in instr_upper or k in sprint_upper for k in ("KINDLE", "BOOK", "EPUB", "HANDBOOK")):
        epub_candidates = [
            os.path.join(repo_dir, "b_sdd_user_guide_sprint032.epub"),
            os.path.join(repo_dir, "b_sdd_architecture_vol2.epub"),
            os.path.join(repo_dir, "docs", "b_sdd_user_guide.epub"),
            os.path.join(repo_dir, "docs", "b_sdd_architecture_vol2.epub"),
        ]
        valid_epubs = [p for p in epub_candidates if os.path.exists(p) and os.path.getsize(p) >= 30000]
        if not valid_epubs:
            return False, "Kindle postcondition failed: No valid compiled EPUB (>30KB) found."

        kindle_log = os.path.join(repo_dir, "logs", "kindle_delivery.log")
        if not os.path.exists(kindle_log):
            return False, "Kindle postcondition failed: logs/kindle_delivery.log missing."

        try:
            with open(kindle_log, "r", encoding="utf-8") as kf:
                recent_lines = kf.readlines()[-30:]
            recent_text = "".join(recent_lines)
            if "RefreshError" in recent_text or "invalid_grant" in recent_text:
                return False, "Kindle postcondition failed: Gmail token error in kindle_delivery.log."
            if "SUCCESS" not in recent_text and "SENT" not in recent_text:
                return False, "Kindle postcondition failed: No SUCCESS/SENT delivery recorded in kindle_delivery.log."
        except Exception as e:
            return False, f"Kindle postcondition log check error: {e}"

    # 3. Must have executed at least one command unless directive is purely informational
    if not logs:
        return False, "Empty execution harness: zero commands executed."

    return True, ""


def execute_task_core(
    instruction_name: str,
    sprint_id: str,
    correlation_id: str,
    target_notebook_id: Optional[str] = None,
    target_repo: Optional[str] = None,
    timeout_seconds: int = 900,
    prompt_text: str = "",
    directive: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Synchronous core task execution pipeline with strict invariant and postcondition validation."""
    repo_dir = target_repo or PROJECT_DIR
    logging.info(f"=== Початок виконання core: {instruction_name} (sprint: {sprint_id}, corr: {correlation_id}, repo: {repo_dir}) ===")
    t_start = time.perf_counter()
    logs: List[Dict[str, Any]] = []
    failed = False
    failed_cmd = ""
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    tests_duration = 0.0
    stdout_tail = ""
    circuit_state = "UNKNOWN"
    domain = "core"
    score = 1.00
    choice = "PROCEED"
    decision: Dict[str, Any] = {}

    proc_env = os.environ.copy()
    user_home = os.path.expanduser("~")
    extra_paths = [
        f"{user_home}/.local/bin",
        f"{user_home}/bin",
        "/usr/local/bin",
        "/usr/bin",
        "/bin"
    ]
    proc_env["PATH"] = ":".join(extra_paths) + ":" + proc_env.get("PATH", "")

    # 1. Check Cluster State & Resilience (Section 1.1)
    is_degraded, is_worm_up, cluster_report = check_cluster_state()
    if is_degraded:
        proc_env["DEGRADED_MODE"] = "1"
        logging.info("Кластер у стані DEGRADED_MODE=1. Використовуються локальні евристики без очікування таймаутів Laya.")
    else:
        logging.info("Кластер номінальний (overall_status=UP, WORM=UP).")

    # 2. Check if this is a smoke test / ping directive (Section 3)
    if sprint_id == "smoke_test" or correlation_id.startswith("PING-"):
        logging.info(f"Виконання наскрізного тесту PING ({correlation_id}) в {repo_dir}")
        test_cmd = ["pytest", "tests/test_architecture_fitness.py"]
        p_test = subprocess.run(
            test_cmd,
            cwd=repo_dir,
            capture_output=True,
            text=True,
            env=proc_env,
            timeout=timeout_seconds
        )
        elapsed = round(time.perf_counter() - t_start, 2)
        tests_duration = elapsed

        m_pass = re.search(r"(\d+)\s+passed", p_test.stdout or "")
        if m_pass:
            passed_tests = int(m_pass.group(1))
        m_fail = re.search(r"(\d+)\s+failed", p_test.stdout or "")
        if m_fail:
            failed_tests = int(m_fail.group(1))
        total_tests = passed_tests + failed_tests

        if p_test.returncode == 0 and failed_tests == 0 and passed_tests > 0:
            status = "SUCCESS"
            failed = False
        else:
            status = "FAILED"
            failed = True
            failed_cmd = test_cmd

        logs.append({
            "cmd": test_cmd,
            "code": p_test.returncode,
            "stdout": p_test.stdout[-1500:] if p_test.stdout else "",
            "stderr": p_test.stderr[-1500:] if p_test.stderr else ""
        })
        lines = (p_test.stdout or "").strip().splitlines()
        stdout_tail = "\n".join(lines[-15:]) if lines else ""

        domain = "infrastructure"
        circuit_state = "LOCAL_HEURISTIC" if is_degraded else "ONLINE"
        score = 1.00
        choice = "PROCEED"
        decision = {"fallback": is_degraded}
    else:
        # 3. Regular Task Execution Flow
        instruction_text = ""
        client = NotebookLmMcpClient()
        candidate_nbs = [target_notebook_id] if target_notebook_id else PRIMARY_NOTEBOOKS
        for nb_id in candidate_nbs:
            if not nb_id:
                continue
            try:
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
                    if instruction_text:
                        logging.info(f"Отримано повний текст директиви з NotebookLM ({nb_id})")
                        break
            except Exception as e:
                logging.warning(f"Не вдалося витягнути директиву з Notebook {nb_id}: {e}")

        # Query Laya Circuit Breaker
        laya_state = {
            "instruction_name": instruction_name,
            "sprint_id": sprint_id,
            "correlation_id": correlation_id,
            "task": instruction_name
        }
        laya_questions = {
            "is_safe": {"status": "OPEN"},
            "target_skill": {"status": "OPEN"}
        }
        decision, circuit_state = laya_breaker.query_with_recovery(
            client=laya_client,
            state=laya_state,
            questions=laya_questions
        )

        domain = decision.get("domain", "core")
        skills = decision.get("skills_formatted", "@b-sdd, @intent-continuity, @safe-refactor")
        score = decision.get("score", 0.98)
        choice = decision.get("choice", "PROCEED")

        if circuit_state == "ONLINE" and not decision.get("fallback"):
            capsule = (
                f"[LAYA DECISION: Mode=NeuralInference, Domain={domain}, "
                f"Choice={choice}, Score={score}, Recommended Skills={skills}]"
            )
        else:
            capsule = (
                f"[LAYA CONTEXT: Mode=LocalHeuristicFallback, Domain={domain}, "
                f"Choice={choice}, Score={score}, Recommended Skills={skills}]"
            )
        logging.info(f"Сформовано Laya контекст (стан: {circuit_state}): {capsule}")

        if prompt_text:
            base_prompt = prompt_text
        elif instruction_text:
            base_prompt = instruction_text
        else:
            prompts_dir = os.path.join(repo_dir, "prompts")
            prompt_file = None
            if os.path.exists(prompts_dir):
                for f in os.listdir(prompts_dir):
                    if (sprint_id in f or instruction_name in f) and f.endswith(".md"):
                        prompt_file = os.path.join(prompts_dir, f)
                        break
            if prompt_file:
                try:
                    with open(prompt_file, "r", encoding="utf-8") as pf:
                        base_prompt = pf.read()
                except Exception as e:
                    logging.error(f"Помилка читання файлу {prompt_file}: {e}")
                    base_prompt = f"Виконай завдання інструкції {instruction_name} для спринту {sprint_id} за методологією B-SDD."
            else:
                base_prompt = f"Виконай завдання інструкції {instruction_name} для спринту {sprint_id} за методологією B-SDD."

        prompt_arg = f"{base_prompt}\n\n{capsule}"

        run_b_sdd_script = os.path.join(repo_dir, "run_b_sdd.sh")
        explicit_commands = find_sprint_commands(sprint_id)

        if os.path.exists(run_b_sdd_script) and os.access(run_b_sdd_script, os.X_OK):
            b_sdd_cmd = ["./run_b_sdd.sh", "--agent", "agy", "--prompt", prompt_arg]
            logging.info(f"Запуск канонічного B-SDD агента: {' '.join(b_sdd_cmd[:3])}...")
            p = subprocess.run(
                b_sdd_cmd,
                cwd=repo_dir,
                capture_output=True,
                text=True,
                env=proc_env,
                timeout=timeout_seconds
            )
            logs.append({
                "cmd": f"./run_b_sdd.sh --agent agy --prompt <{instruction_name}>",
                "laya_state": circuit_state,
                "code": p.returncode,
                "stdout": p.stdout[-1500:] if p.stdout else "",
                "stderr": p.stderr[-1500:] if p.stderr else ""
            })
            lines = (p.stdout or "").strip().splitlines()
            stdout_tail = "\n".join(lines[-15:]) if lines else ""
            if p.returncode != 0:
                failed = True
                failed_cmd = "run_b_sdd.sh"
        elif explicit_commands:
            for c in explicit_commands:
                logging.info(f"Виконання явного скрипту спринту: {c}")
                cmd_args = shlex.split(c) if isinstance(c, str) else c
                p = subprocess.run(cmd_args, cwd=repo_dir, capture_output=True, text=True, env=proc_env, timeout=timeout_seconds)
                logs.append({
                    "cmd": c,
                    "code": p.returncode,
                    "stdout": p.stdout[-1500:] if p.stdout else "",
                    "stderr": p.stderr[-1500:] if p.stderr else ""
                })
                lines = (p.stdout or "").strip().splitlines()
                stdout_tail = "\n".join(lines[-15:]) if lines else ""
                if p.returncode != 0:
                    failed = True
                    failed_cmd = c
                    break
        else:
            logging.error(f"Критична помилка: канонічний скрипт {run_b_sdd_script} та команди для спринту {sprint_id} відсутні.")
            failed = True
            failed_cmd = "no_valid_execution_harness"
            logs.append({
                "error": f"B-SDD harness {run_b_sdd_script} не знайдено, хибний dry-run заборонено."
            })

        # Anti-False-Positive: Strict Postcondition Check
        postcond_ok, postcond_err = verify_task_postconditions(sprint_id, instruction_name, repo_dir, logs, t_start)
        if not postcond_ok:
            failed = True
            failed_cmd = failed_cmd or postcond_err
            logging.error(f"[ANTI-FALSE-POSITIVE GUARD TRIGGERED] Postcondition failed: {postcond_err}")

        elapsed = round(time.perf_counter() - t_start, 2)
        status = "FAILED" if failed else "SUCCESS"

    git_rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_dir, capture_output=True, text=True).stdout.strip() or "HEAD"

    # Eliminating tautological test counts: report ONLY actual observed tests
    tests_summary_obj = {
        "total": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "duration_seconds": tests_duration if tests_duration > 0 else elapsed
    }
    tests_summary_str = f"{passed_tests}/{total_tests} PASSED ({tests_summary_obj['duration_seconds']}s)"

    return {
        "correlation_id": correlation_id,
        "sprint_id": sprint_id,
        "instruction_name": instruction_name,
        "status": status,
        "failed": failed,
        "failed_command": failed_cmd,
        "execution_time_seconds": elapsed,
        "git_commit": git_rev,
        "tests_summary": tests_summary_obj,
        "tests_summary_str": tests_summary_str,
        "vector3_intent_score": 1.00 if status == "SUCCESS" else 0.00,
        "dual_gate_passed": (status == "SUCCESS"),
        "stdout_tail": stdout_tail,
        "is_worm_up": is_worm_up,
        "repo_dir": repo_dir,
        "t_start": t_start,
        "logs": logs,
        "laya": {
            "circuit_state": circuit_state,
            "domain": domain,
            "score": score,
            "choice": choice,
            "fallback": decision.get("fallback", False)
        }
    }


def execute_task_async(
    instruction_name: str,
    sprint_id: str,
    correlation_id: str,
    target_notebook_id: Optional[str] = None,
    target_repo: Optional[str] = None,
    timeout_seconds: int = 900,
    prompt_text: str = "",
    directive: Optional[Dict[str, Any]] = None
) -> None:
    """Asynchronous worker executing task with guaranteed error handling and zero false positives."""
    repo_dir = target_repo or PROJECT_DIR
    t_start = time.perf_counter()
    status = "FAILED"
    failed_cmd = ""
    try:
        core_result = execute_task_core(
            instruction_name=instruction_name,
            sprint_id=sprint_id,
            correlation_id=correlation_id,
            target_notebook_id=target_notebook_id,
            target_repo=repo_dir,
            timeout_seconds=timeout_seconds,
            prompt_text=prompt_text,
            directive=directive
        )

        status = core_result["status"]
        failed = core_result["failed"]
        failed_cmd = core_result["failed_command"]
        elapsed = core_result["execution_time_seconds"]
        git_rev = core_result["git_commit"]
        is_worm_up = core_result["is_worm_up"]
        tests_summary_obj = core_result["tests_summary"]
        tests_summary_str = core_result["tests_summary_str"]
        stdout_tail = core_result["stdout_tail"]
        logs = core_result["logs"]
        laya_info = core_result["laya"]

        # 4. Mandatory Step Exit Gate: Closed-Loop Delivery to NotebookLM (Invariant FL-01)
        synced, source_title = publish_report_to_notebooklm(
            sprint_id=sprint_id,
            instruction_name=instruction_name,
            status=status,
            target_notebook_id=target_notebook_id,
            target_repo=repo_dir,
            extra_content=f"- **Status:** {status}\n- **Execution Time:** {elapsed}s\n- **Tests Passed:** {tests_summary_str}",
            t_start=t_start,
            failed_cmd=failed_cmd
        )

        # 5. Record WORM Entry
        worm_tx_id = record_worm_entry(sprint_id, correlation_id, status, is_worm_up, repo_dir)

        # 6. Build Payload
        payload = {
            "correlation_id": correlation_id,
            "sprint_id": sprint_id,
            "status": status,
            "execution_time_seconds": elapsed,
            "git_commit": git_rev,
            "tests_summary": tests_summary_obj,
            "vector3_intent_score": core_result["vector3_intent_score"],
            "dual_gate_passed": core_result["dual_gate_passed"],
            "worm_transaction_id": worm_tx_id,
            "notebooklm_synced": synced,
            "stdout_tail": stdout_tail,
            "project": "B-SDD",
            "node": BSDD_NODE_IP,
            "host": BSDD_NODE_IP,
            "commit": git_rev,
            "report_name": source_title,
            "source_title": source_title,
            "failed_command": failed_cmd,
            "require_user": failed,
            "error_details": failed_cmd if failed else "",
            "tests_summary_str": tests_summary_str,
            "laya": laya_info,
            "logs": logs
        }

        # 7. Dispatch Callback to n8n Webhook with Direct Telegram Fallback
        n8n_delivered = False
        try:
            data = json.dumps(payload).encode("utf-8")
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "B-SDD-Supervisor/1.4"
            }
            req = urllib.request.Request(N8N_CALLBACK_WEBHOOK, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                if 200 <= resp.status < 300:
                    n8n_delivered = True
                    resp_body = resp.read().decode("utf-8")
                    logging.info(f"Звіт успішно надіслано в n8n ({N8N_CALLBACK_WEBHOOK}): status {resp.status} - {resp_body}")
                else:
                    logging.warning(f"n8n повернув статус {resp.status}, ініціюємо прямий фолбек у Telegram.")
        except Exception as e:
            logging.warning(f"Помилка надсилання вебхука в n8n ({N8N_CALLBACK_WEBHOOK}): {e}. Ініціюємо прямий фолбек.")

        if not n8n_delivered:
            try:
                tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                tg_text = (
                    f"⚠️ [B-SDD FALLBACK DIRECT ALERT]\n"
                    f"n8n unreachable. Dispatch {correlation_id} finished with status {status}.\n"
                    f"Error details: {failed_cmd if failed else 'None'}"
                )
                tg_payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": tg_text}).encode("utf-8")
                tg_req = urllib.request.Request(tg_url, data=tg_payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(tg_req, timeout=5.0) as tg_resp:
                    logging.info(f"Direct Telegram alert fallback sent successfully: status {tg_resp.status}")
            except Exception as tg_err:
                logging.error(f"Failed to send direct Telegram fallback: {tg_err}")

        if (sprint_id == "smoke_test" or correlation_id.startswith("PING-")) and status == "SUCCESS":
            send_telegram_alert(f"✅ [B-SDD] {correlation_id} Verified successfully. All systems nominal.")
        elif status == "FAILED":
            send_telegram_alert(f"🚨 [B-SDD TASK FAILED] {instruction_name} ({sprint_id}) FAILED: {failed_cmd}")

    except Exception as exc:
        logging.error(f"Непередбачена помилка під час виконання завдання: {exc}", exc_info=True)
        status = "FAILED"
        failed_cmd = f"unhandled_exception: {exc}"
        elapsed = round(time.perf_counter() - t_start, 2)
        try:
            publish_report_to_notebooklm(
                sprint_id=sprint_id,
                instruction_name=instruction_name,
                status="FAILED",
                target_notebook_id=target_notebook_id,
                target_repo=repo_dir,
                extra_content=f"- **Status:** ❌ FAILED\n- **Unhandled Exception:** {exc}\n- **Execution Time:** {elapsed}s",
                t_start=t_start,
                failed_cmd=failed_cmd
            )
        except Exception as pub_err:
            logging.error(f"Failed to publish exception failure report: {pub_err}")
        send_telegram_alert(f"🚨 [B-SDD CRITICAL EXCEPTION] {instruction_name} ({sprint_id}) error: {exc}")
    finally:
        mark_task_completed(instruction_name, sprint_id)
        logging.info(f"=== Завершено обробку завдання: {instruction_name} (sprint: {sprint_id}, status: {status}) ===\n\n")


class DispatchHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/status", "/health", "/"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            with task_lock:
                act = list(active_tasks.keys())
                comp = list(completed_tasks.keys())
            resp = {
                "status": "UP",
                "service": "bsdd-supervisor",
                "version": "1.4",
                "port": PORT,
                "node": BSDD_NODE_IP,
                "laya_circuit_state": laya_breaker.state,
                "active_tasks": act,
                "recent_completed_tasks": comp
            }
            self.wfile.write((json.dumps(resp) + "\n").encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/dispatch":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8"))

            correlation_id = body.get("correlation_id", f"DSP-{int(time.time())}")
            sprint_id = body.get("sprint_id", "sprint_033")
            target_repo = body.get("target_repo", PROJECT_DIR)
            timeout_seconds = int(body.get("timeout_seconds", 900))
            target_notebook_id = body.get("notebook_id", "")

            directive = body.get("directive", {})
            if isinstance(directive, dict):
                instruction_name = directive.get("title") or body.get("instruction_name", "") or correlation_id
                prompt_text = directive.get("prompt_text", "")
            else:
                instruction_name = body.get("instruction_name", "UNKNOWN")
                prompt_text = str(directive) if directive else ""

            if not instruction_name:
                instruction_name = f"TASK_{sprint_id}_{correlation_id}"

            logging.info(f"Отримано POST /dispatch: {instruction_name} (sprint: {sprint_id}, corr: {correlation_id}, repo: {target_repo})")

            # Mutex / Cooldown Deduplication Gate
            if is_duplicate_task(instruction_name, sprint_id):
                logging.warning(
                    f"[DEDUP GATE] Відхилено дублікат запиту: instruction='{instruction_name}', sprint='{sprint_id}' "
                    f"(завдання активно виконується або завершилось менше {COOLDOWN_SECONDS}с тому)"
                )
                self.send_response(409)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status": "ALREADY_ACTIVE_OR_PROCESSED"}\n')
                return

            mark_task_active(instruction_name, sprint_id)

            self.send_response(202)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "QUEUED"}\n')

            Thread(
                target=execute_task_async,
                kwargs={
                    "instruction_name": instruction_name,
                    "sprint_id": sprint_id,
                    "correlation_id": correlation_id,
                    "target_notebook_id": target_notebook_id,
                    "target_repo": target_repo,
                    "timeout_seconds": timeout_seconds,
                    "prompt_text": prompt_text,
                    "directive": directive if isinstance(directive, dict) else {}
                },
                daemon=True
            ).start()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        logging.info("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args))


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), DispatchHandler)
    logging.info(f"B-SDD Supervisor v1.4 слухає на 0.0.0.0:{PORT} (Laya={LAYA_HOST}:{LAYA_PORT}, State={laya_breaker.state})...")
    server.serve_forever()

