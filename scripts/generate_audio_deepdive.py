#!/usr/bin/env python3
"""
B-SDD Autonomous Audio Overview (Deep Dive) Generator for Google NotebookLM.
100% Pure Python Standard Library (ADR-002).
Generates maximal-length (AudioLength.LONG), deep-dive (AudioFormat.DEEP_DIVE)
podcast discussions in standard literary Ukrainian via NotebookLM MCP.
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

NOTEBOOKLM_MCP_URL = os.environ.get("NOTEBOOKLM_MCP_URL", "http://192.168.3.184:8002/mcp")
SUPERVISOR_WEBHOOK_URL = os.environ.get("SUPERVISOR_WEBHOOK_URL", "https://n8n.exodus.pp.ua/webhook/bsdd-supervisor-result")
TELEGRAM_BOT_TOKEN = "8717667434:AAFWddh_xwTfMVHW7puxrlIFprbO9m_Au7Y"
TELEGRAM_CHAT_ID = "6412868393"

DEFAULT_NOTEBOOK_ID = "b371bcda-77c6-4803-84e7-8aed42817454"  # FDE Guide Book
DEFAULT_UKRAINIAN_INSTRUCTIONS = (
    "Проведіть глибокий, детальний та вичерпний експертний аналіз матеріалів цього записника українською мовою. "
    "Формат: інтелектуальний, динамічний діалог двох фахових аналітиків (Deep Dive Podcast). "
    "1. Автоматично виділіть та ретельно розберіть усі ключові концептуальні, інженерні та практичні тези з першоджерел. "
    "2. Детально розкрийте реальні кейси, виклики впровадження, цифри, методології та причинно-наслідкові зв'язки. "
    "3. Мова розмови — виключно якісна українська мова з коректною професійною термінологією. "
    "4. Забезпечте максимальну повноту викладу матеріалу, утримуючи фокус на практичній цінності для інженера та архітектора."
)

LOG_FILE = Path("/home/vokov/projects/b-sdd/logs/audio_generation.log")


def log_event(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


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
                "clientInfo": {"name": "b-sdd-audio-deepdive", "version": "1.0"}
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


def send_telegram_alert(message: str) -> bool:
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[-] Telegram notification notice: {e}", file=sys.stderr)
        return False


def send_supervisor_telemetry(payload: Dict[str, Any]) -> bool:
    try:
        req = urllib.request.Request(
            SUPERVISOR_WEBHOOK_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[-] Supervisor telemetry notice: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate maximal-length Ukrainian Audio Overview in NotebookLM")
    parser.add_argument("--notebook", default=DEFAULT_NOTEBOOK_ID, help="Target NotebookLM Notebook ID")
    parser.add_argument("--length", default="LONG", choices=["SHORT", "DEFAULT", "LONG"], help="Audio length (default: LONG)")
    parser.add_argument("--format", default="DEEP_DIVE", choices=["DEEP_DIVE", "BRIEF", "CRITIQUE", "DEBATE"], help="Audio format (default: DEEP_DIVE)")
    parser.add_argument("--language", default="uk", help="Language code (default: uk)")
    parser.add_argument("--instructions", default=DEFAULT_UKRAINIAN_INSTRUCTIONS, help="Custom prompt instructions")
    parser.add_argument("--sources", nargs="*", default=None, help="Specific source IDs (default: all sources)")
    parser.add_argument("--no-telegram", action="store_true", help="Skip Telegram notification")
    args = parser.parse_args()

    client = NotebookLmMcpClient()
    log_event(f"=== [B-SDD Audio Overview Deep Dive Pipeline] ===")
    log_event(f"Notebook ID : {args.notebook}")
    log_event(f"Audio Length: {args.length} (Maximal Extent)")
    log_event(f"Audio Format: {args.format}")
    log_event(f"Language    : {args.language}")

    # 1. Verify sources in notebook
    sources = client.call_tool("sources_list", {"notebook_id": args.notebook})
    if not isinstance(sources, list) or len(sources) == 0:
        log_event(f"[-] ERROR: No sources found in notebook {args.notebook}")
        sys.exit(1)

    log_event(f"[*] Verified {len(sources)} active sources in target notebook.")

    # 2. Trigger Audio Generation via MCP
    gen_args = {
        "notebook_id": args.notebook,
        "instructions": args.instructions,
        "language": args.language,
        "audio_length": args.length,
        "audio_format": args.format
    }
    if args.sources:
        gen_args["source_ids"] = args.sources

    log_event(f"[*] Dispatching generate_audio call to NotebookLM MCP...")
    result = client.call_tool("generate_audio", gen_args)
    log_event(f"MCP Response: {json.dumps(result, ensure_ascii=False)}")

    task_id = result.get("task_id") if isinstance(result, dict) else None
    status = result.get("status", "unknown") if isinstance(result, dict) else "unknown"

    if not task_id:
        log_event(f"[-] ERROR: Failed to obtain task_id from generate_audio.")
        sys.exit(1)

    log_event(f"[+] SUCCESS: Audio generation task started: task_id={task_id}, status={status}")

    # 3. Telemetry emission
    notebook_url = f"https://notebooklm.google.com/notebook/{args.notebook}"
    tg_msg = (
        f"🎙 *B-SDD Audio Overview (Deep Dive) Ініційовано!*\n\n"
        f"📓 *Записник:* [{args.notebook}]({notebook_url})\n"
        f"⏱ *Розмір переказу:* `{args.length}` (Максимальний обсяг)\n"
        f"🎭 *Формат:* `{args.format}`\n"
        f"🇺🇦 *Мова:* `{args.language}` (Українська)\n"
        f"🆔 *Task ID:* `{task_id}`\n\n"
        f"ШІ розпочав генерацію максимального аудіопереказу з виділенням ключових тез."
    )
    if not args.no_telegram:
        send_telegram_alert(tg_msg)

    # 4. Supervisor Dual-Loop
    supervisor_payload = {
        "project": "B-SDD-AUDIO-DEEPDIVE",
        "status": "SUCCESS",
        "node": "192.168.3.161",
        "sprint_id": "AUDIO_OVERVIEW_LONG_UK",
        "commit": "HEAD",
        "tests_summary": f"AudioLength={args.length}, Format={args.format}, Language={args.language}",
        "report_name": f"NotebookLM Audio Overview ({task_id})"
    }
    send_supervisor_telemetry(supervisor_payload)

    print(json.dumps({
        "status": "SUCCESS",
        "task_id": task_id,
        "notebook_id": args.notebook,
        "audio_length": args.length,
        "audio_format": args.format,
        "language": args.language,
        "sources_count": len(sources),
        "notebook_url": notebook_url
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
