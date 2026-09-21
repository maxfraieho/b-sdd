#!/usr/bin/env python3
"""
Dispatch telemetry callback to n8n webhook and Telegram bot.
Pure Python standard library (ADR-002).
"""
import json
import urllib.request
from typing import Dict, Any

N8N_WEBHOOK_URL = "https://n8n.exodus.pp.ua/webhook/bsdd-supervisor-result"
TELEGRAM_BOT_TOKEN = "8717667434:AAFWddh_xwTfMVHW7puxrlIFprbO9m_Au7Y"
TELEGRAM_CHAT_ID = "6412868393"


def send_n8n_webhook(payload: Dict[str, Any]) -> None:
    req = urllib.request.Request(
        N8N_WEBHOOK_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "B-SDD-Supervisor/1.0"
        }
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        print(f"[n8n] HTTP {resp.status}: {body}")


def send_telegram_message(text: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        print(f"[Telegram] HTTP {resp.status}: {body}")


def main():
    n8n_payload = {
        "instruction_name": "OUTBOX_AGI_SPRINT_021_ISOLATE_EXTENDED_SKILLS",
        "sprint_id": "sprint_021",
        "correlation_id": "corr_20260921_skills_03",
        "status": "SUCCESS",
        "report_name": "INBOX_GEMINI_SPRINT_021_ISOLATE_EXTENDED_SKILLS_REPORT",
        "source_title": "INBOX_GEMINI_SPRINT_021_ISOLATE_EXTENDED_SKILLS_REPORT",
        "notebooklm_synced": True,
        "failed_command": None,
        "require_user": False,
        "metrics": {
            "active_core_skills": 48,
            "isolated_extended_skills": 29,
            "catalog_files": 218,
            "dump_size_mb": 1.10,
            "tests_passed": 18,
            "tests_failed": 0
        }
    }

    tg_text = (
        "✅ *[B-SDD SPRINT 021 · FEEDBACK LOOP FL-01 RESTORED]*\n\n"
        "• *Directive:* `OUTBOX_AGI_SPRINT_021_ISOLATE_EXTENDED_SKILLS`\n"
        "• *Correlation ID:* `corr_20260921_skills_03`\n"
        "• *Status:* SUCCESS (Closed-Loop Verified)\n"
        "• *Supervisor:* `systemd --user` daemon on `100.65.225.122:8161` (resilient)\n"
        "• *Active Core Skills:* 48 Golden Standard skills (7 categories)\n"
        "• *Extended Skills:* 29 isolated in `~/.agents/skills/_extended/`\n"
        "• *Active Catalog:* `docs/skills_dump/ACTIVE_SKILLS_CATALOG.md` (218 code files)\n"
        "• *Compiled Dump:* `SKILLS_INVENTORY_DUMP.md` (1.10 MB, 48 skills)\n"
        "• *Architectural Tests:* 18/18 PASSED (pytest)\n"
        "• *NotebookLM Artifact:* `INBOX_GEMINI_SPRINT_021_ISOLATE_EXTENDED_SKILLS_REPORT` uploaded to `205ee2ec-e0d2-4ba6-badf-44f2de02c7e2`\n"
        "• *n8n Webhook:* Delivered to `https://n8n.exodus.pp.ua/webhook/bsdd-supervisor-result`"
    )

    print("Sending n8n webhook...")
    send_n8n_webhook(n8n_payload)

    print("Sending Telegram message...")
    send_telegram_message(tg_text)


if __name__ == "__main__":
    main()
