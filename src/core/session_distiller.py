"""
B-SDD (Bitemporal Spec-Driven Development) Session Distiller
Extracts, compactifies, and distills architectural decisions, invariants,
and actionable tasks from long-running CLI AI agent sessions (AGY, Claude Code, Codex).
Operates using 100% Pure Python Standard Library.
"""
import os
import re
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

DEFAULT_AGY_DATA_DIR = Path.home() / ".gemini" / "antigravity-cli"


class SessionDistiller:
    """Extracts architectural decisions, user directives, and tasks from agent transcripts."""

    def __init__(self, app_data_dir: Optional[Path] = None):
        self.app_data_dir = (app_data_dir or DEFAULT_AGY_DATA_DIR).resolve()

    @staticmethod
    def _clean_user_content(raw: str) -> str:
        """Removes XML wrapper tags, metadata blocks, and system summaries."""
        text = raw
        # Remove context summary blocks
        text = re.sub(r"<CONTEXT_SUMMARY>.*?</CONTEXT_SUMMARY>", "", text, flags=re.DOTALL)
        # Remove metadata tags
        text = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", text, flags=re.DOTALL)
        # Remove system message blocks
        text = re.sub(r"<SYSTEM_MESSAGE>.*?</SYSTEM_MESSAGE>", "", text, flags=re.DOTALL)
        # Extract user request if enclosed
        m = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", text, flags=re.DOTALL)
        if m:
            text = m.group(1)
        return text.strip()

    def distill_agy_session(self, conversation_id: str) -> Dict[str, Any]:
        """
        Parses Antigravity CLI transcript.jsonl for given conversation_id.
        Streams line-by-line to avoid loading 30MB+ JSON into memory at once.
        """
        transcript_path = self.app_data_dir / "brain" / conversation_id / ".system_generated" / "logs" / "transcript.jsonl"
        if not transcript_path.exists():
            raise FileNotFoundError(f"Transcript not found at {transcript_path}")

        user_requests: List[Dict[str, Any]] = []
        files_modified: Set[str] = set()
        tools_used: Dict[str, int] = {}
        total_steps = 0
        first_ts = None
        last_ts = None

        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                total_steps += 1
                try:
                    d = json.loads(line)
                except Exception:
                    continue

                ts = d.get("created_at")
                if not first_ts and ts:
                    first_ts = ts
                if ts:
                    last_ts = ts

                step_type = d.get("type")
                source = d.get("source")

                # Track user requests
                if step_type == "USER_INPUT":
                    raw_content = d.get("content", "")
                    cleaned = self._clean_user_content(raw_content)
                    if cleaned and not cleaned.startswith("<CONTEXT_SUMMARY"):
                        user_requests.append({
                            "index": len(user_requests) + 1,
                            "timestamp": ts,
                            "content": cleaned
                        })

                # Track tool usage and file modifications
                tool_calls = d.get("tool_calls", [])
                for tc in tool_calls:
                    tname = tc.get("name") or tc.get("tool") or "unknown"
                    tools_used[tname] = tools_used.get(tname, 0) + 1
                    args = tc.get("args") or tc.get("arguments") or {}
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {}

                    target = args.get("TargetFile") or args.get("target_file") or args.get("path")
                    if target:
                        files_modified.add(str(target))

        # Identify key themes and architectural topics
        key_topics = self._extract_key_topics(user_requests)

        return {
            "conversation_id": conversation_id,
            "transcript_path": str(transcript_path),
            "total_steps": total_steps,
            "first_timestamp": first_ts,
            "last_timestamp": last_ts,
            "user_requests_count": len(user_requests),
            "user_requests": user_requests,
            "files_modified_count": len(files_modified),
            "files_modified": sorted(list(files_modified)),
            "tools_used": tools_used,
            "key_topics": key_topics
        }

    def _extract_key_topics(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Categorizes and extracts milestones from chronological user requests."""
        topics = []
        for req in requests:
            txt = req["content"].lower()
            topic = "general"
            if "adr" in txt or "архітектур" in txt:
                topic = "architecture"
            elif "mini-app" in txt or "кнопк" in txt or "скріншот" in txt or "ui" in txt or "інтерфейс" in txt:
                topic = "ui_ux"
            elif "скрап" in txt or "flatfox" in txt or "проксі" in txt or "вакансі" in txt or "житл" in txt:
                topic = "data_scrapers"
            elif "privacy" in txt or "конфіденційн" in txt or "про проект" in txt:
                topic = "legal_privacy"
            elif "utopia" in txt or "db" in txt or "баз" in txt:
                topic = "utopia_db"
            elif "b-sdd" in txt or "методик" in txt or "репозитор" in txt:
                topic = "b_sdd_methodology"
            elif "бот" in txt or "telegram" in txt:
                topic = "telegram_bot"

            topics.append({
                "index": req["index"],
                "timestamp": req["timestamp"],
                "topic": topic,
                "summary": req["content"][:160] + ("..." if len(req["content"]) > 160 else "")
            })
        return topics

    def render_distilled_markdown(self, data: Dict[str, Any]) -> str:
        """Generates a structured, compact Markdown summary of the distilled session."""
        lines = [
            f"# Distilled Session Intelligence (B-SDD)",
            f"- **Conversation ID:** `{data['conversation_id']}`",
            f"- **Steps Analyzed:** {data['total_steps']} steps across {data['user_requests_count']} user turns",
            f"- **Time Horizon:** `{data.get('first_timestamp')}` → `{data.get('last_timestamp')}`",
            f"- **Files Modified:** {data['files_modified_count']} unique files",
            "",
            "## 1. Key Milestones & Directives Timeline",
            "| # | Topic | Directive Summary |",
            "| :--- | :--- | :--- |"
        ]

        # Sample recent / key turns
        reqs = data.get("key_topics", [])
        for t in reqs[-25:]:  # most recent 25 key milestones
            topic_badge = f"`{t['topic']}`"
            summary_escaped = t['summary'].replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {t['index']} | {topic_badge} | {summary_escaped} |")

        lines.extend([
            "",
            "## 2. Modified Artifacts & Code Seams",
            "```"
        ])
        for f in data.get("files_modified", [])[:40]:
            lines.append(f)
        if len(data.get("files_modified", [])) > 40:
            lines.append(f"... and {len(data['files_modified']) - 40} more files")
        lines.append("```")

        lines.extend([
            "",
            "## 3. Actionable Invariants & Pending Work Items",
            "- [ ] **UI / TMA Polish:** Adjust UI layout per user screenshots, remove extraneous buttons, fix broken footer links.",
            "- [ ] **Project Narrative & Legal:** Add 'Про проект' page and ACCORD-styled Privacy Policy (based on sonate-solidaire.me/privacy).",
            "- [ ] **Bot & Web Parity:** Synchronize Telegram bot buttons and catalogs with Resilience Navigator / ACCORD-S.",
            "- [ ] **B-SDD Continuity:** Enforce active rules pre-flight check before subsequent tasks."
        ])

        return "\n".join(lines) + "\n"
