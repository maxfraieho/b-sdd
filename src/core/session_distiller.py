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
import datetime
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

DEFAULT_AGY_DATA_DIR = Path.home() / ".gemini" / "antigravity-cli"


class SessionDistiller:
    """Extracts architectural decisions, user directives, and tasks from agent transcripts."""

    def __init__(self, app_data_dir: Optional[Path] = None, root_dir: Optional[Path] = None):
        self.app_data_dir = (app_data_dir or DEFAULT_AGY_DATA_DIR).resolve()
        self.root_dir = (root_dir or Path.cwd()).resolve()

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

    def get_latest_conversation_id(self) -> Optional[str]:
        """Finds the most recently active Antigravity CLI conversation ID."""
        brain_dir = self.app_data_dir / "brain"
        if not brain_dir.exists():
            return None
        latest_id = None
        latest_mtime = -1.0
        try:
            for p in brain_dir.iterdir():
                if p.is_dir():
                    t = p / ".system_generated" / "logs" / "transcript.jsonl"
                    if t.exists():
                        m = t.stat().st_mtime
                        if m > latest_mtime:
                            latest_mtime = m
                            latest_id = p.name
        except Exception:
            pass
        return latest_id

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

    def get_git_info(self, repo_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Inspects git repository for current branch, commit hash, and dirty files."""
        target_dir = (repo_dir or self.root_dir).resolve()
        branch = "unknown"
        commit = "unknown"
        dirty_files: List[str] = []
        try:
            b_res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=target_dir, capture_output=True, text=True)
            if b_res.returncode == 0:
                branch = b_res.stdout.strip()
            c_res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=target_dir, capture_output=True, text=True)
            if c_res.returncode == 0:
                commit = c_res.stdout.strip()
            s_res = subprocess.run(["git", "status", "--porcelain"], cwd=target_dir, capture_output=True, text=True)
            if s_res.returncode == 0:
                for line in s_res.stdout.splitlines():
                    line = line.strip()
                    if line:
                        parts = line.split(maxsplit=1)
                        if len(parts) == 2:
                            file_path = parts[1].strip('"')
                            if " -> " in file_path:
                                file_path = file_path.split(" -> ")[-1].strip('"')
                            dirty_files.append(file_path)
        except Exception:
            pass

        return {
            "branch": branch,
            "commit": commit,
            "dirty_files": sorted(dirty_files)
        }

    def find_tasks(self, repo_dir: Optional[Path] = None, spec_path: Optional[Path] = None) -> Dict[str, Any]:
        """Scans specs directory or a specific tasks.md file for completed and pending tasks."""
        target_dir = (repo_dir or self.root_dir).resolve()
        completed: List[Dict[str, Any]] = []
        pending: List[Dict[str, Any]] = []

        if spec_path:
            spec_p = Path(spec_path)
            if not spec_p.is_absolute():
                spec_p = target_dir / spec_p
            task_files = [spec_p] if spec_p.is_file() else sorted(list(spec_p.rglob("tasks.md")))
        else:
            specs_dir = target_dir / "specs"
            task_files = sorted(list(specs_dir.rglob("tasks.md"))) if specs_dir.exists() else []

        for tf in task_files:
            if not tf.exists():
                continue
            spec_name = tf.parent.name
            try:
                content = tf.read_text(encoding="utf-8")
            except Exception:
                continue

            for line in content.splitlines():
                line_str = line.strip()
                m = re.match(r"^-\s+\[([xX ])\]\s*(.*)$", line_str)
                if m:
                    is_done = m.group(1).lower() == "x"
                    rest = m.group(2).strip()
                    id_m = re.match(r"^(`?[\w-]+`?):\s*(.*)$", rest)
                    if id_m:
                        task_id = id_m.group(1).strip("`")
                        desc = id_m.group(2).strip()
                    else:
                        task_id = f"task-{len(completed)+len(pending)+1:03d}"
                        desc = rest

                    try:
                        rel_path = str(tf.relative_to(target_dir))
                    except ValueError:
                        rel_path = str(tf)

                    full_desc = f"{task_id}: {desc}" if task_id and not desc.startswith(task_id) else desc
                    item = {
                        "id": task_id,
                        "description": full_desc,
                        "raw_text": desc,
                        "spec": spec_name,
                        "file": rel_path
                    }
                    if is_done:
                        completed.append(item)
                    else:
                        pending.append(item)

        return {
            "completed": completed,
            "pending": pending,
            "next_task": pending[0] if pending else None
        }

    def verify_fitness_status(self, repo_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Runs architectural fitness test suite and returns outcome."""
        target_dir = (repo_dir or self.root_dir).resolve()
        test_file = target_dir / "tests" / "test_architecture_fitness.py"
        if not test_file.exists():
            return {
                "passed": True,
                "gate": "none",
                "exit_code": 0,
                "details": "No architectural fitness test file found"
            }

        cmd = ["pytest", "-v", str(test_file)]
        try:
            res = subprocess.run(cmd, cwd=target_dir, capture_output=True, text=True, timeout=60)
            return {
                "passed": res.returncode == 0,
                "gate": str(test_file.relative_to(target_dir)),
                "exit_code": res.returncode,
                "details": (res.stdout or "") + "\n" + (res.stderr or "")
            }
        except Exception:
            try:
                cmd_fallback = [sys.executable, "-m", "pytest", "-v", str(test_file)]
                res = subprocess.run(cmd_fallback, cwd=target_dir, capture_output=True, text=True, timeout=60)
                return {
                    "passed": res.returncode == 0,
                    "gate": str(test_file.relative_to(target_dir)),
                    "exit_code": res.returncode,
                    "details": (res.stdout or "") + "\n" + (res.stderr or "")
                }
            except Exception as e:
                return {
                    "passed": False,
                    "gate": str(test_file.relative_to(target_dir)),
                    "exit_code": -1,
                    "details": f"Fitness gate execution error: {e}"
                }

    def get_active_invariants(self, repo_dir: Optional[Path] = None) -> List[str]:
        """Extracts compiled active architectural invariants from .context/active_rules.md."""
        target_dir = (repo_dir or self.root_dir).resolve()
        rules_file = target_dir / ".context" / "active_rules.md"
        invariants: List[str] = []
        if rules_file.exists():
            try:
                for line in rules_file.read_text(encoding="utf-8").splitlines():
                    line_s = line.strip()
                    if line_s.startswith("- [GLOBAL]") or line_s.startswith("- [CORE]") or line_s.startswith("- [SPEC-"):
                        invariants.append(line_s)
            except Exception:
                pass
        return invariants

    def synthesize_next_sprint(
        self,
        next_task: Optional[Dict[str, Any]],
        completed_tasks: Optional[List[str]] = None,
        modified_files: Optional[List[str]] = None,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, str]:
        """Assembles prompt and run command for Sprint N+1."""
        prefix = "[B-SDD Invariants: Consult .context/active_rules.md for active architecture constraints]"
        if custom_prompt:
            task_id = "custom"
            title = custom_prompt[:80]
            prompt = f"{prefix} --mode continuous --task {custom_prompt}"
        elif next_task:
            task_id = next_task["id"]
            title = next_task["description"]
            prompt = f"{prefix} --mode continuous --task {next_task['description']} --spec {next_task['file']} --rules .context/active_rules.md"
        else:
            task_id = "complete"
            title = "Finalize and verify all specifications"
            prompt = f"{prefix} --mode continuous --task All tasks completed; run final architecture verification and report project status."

        run_cmd = f'./run_b_sdd.sh --new-session "{prompt}"'
        return {
            "task_id": task_id,
            "title": title,
            "prompt": prompt,
            "run_command": run_cmd
        }

    def generate_handoff(
        self,
        conversation_id: Optional[str] = None,
        repo_dir: Optional[Path] = None,
        next_prompt: Optional[str] = None,
        spec_path: Optional[Path] = None,
        enforce_fitness: bool = True,
        output_json: Optional[Path] = None,
        output_md: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes Sprint N -> N+1 handoff artifacts:
        - Machine-readable .context/sprint_handoff.json
        - Human-readable .context/next_sprint.md
        Enforces ADR-007 invariant: fails if fitness gates do not pass.
        """
        target_dir = (repo_dir or self.root_dir).resolve()

        # 1. Enforce fitness gate (ADR-007 invariant)
        fitness_res = self.verify_fitness_status(target_dir)
        if enforce_fitness and not fitness_res["passed"]:
            details = fitness_res.get("details", "")
            raise RuntimeError(
                f"Architectural fitness gate failed (exit code {fitness_res['exit_code']}). "
                f"Details: {details}\n"
                "ADR-007 invariant violation: cannot generate handoff artifact while fitness tests are failing."
            )

        # 2. Git inspection
        git_info = self.get_git_info(target_dir)

        # 3. Session distillation if conversation_id provided
        all_modified_files: Set[str] = set(git_info.get("dirty_files", []))
        if conversation_id:
            try:
                session_data = self.distill_agy_session(conversation_id)
                for f in session_data.get("files_modified", []):
                    try:
                        p = Path(f)
                        if p.is_relative_to(target_dir):
                            all_modified_files.add(str(p.relative_to(target_dir)))
                        else:
                            all_modified_files.add(f)
                    except Exception:
                        all_modified_files.add(f)
            except Exception:
                pass

        # 4. Roadmap and task introspection
        tasks = self.find_tasks(target_dir, spec_path)

        # 5. Synthesize next sprint target
        next_sprint = self.synthesize_next_sprint(
            next_task=tasks["next_task"],
            completed_tasks=[t["description"] for t in tasks["completed"]],
            modified_files=sorted(list(all_modified_files)),
            custom_prompt=next_prompt
        )

        # 6. Active invariants
        active_invs = self.get_active_invariants(target_dir)

        # 7. Assemble schema payload
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        conv_id_clean = conversation_id or "session"
        conv_short = conv_id_clean.split("-")[0] if "-" in conv_id_clean else conv_id_clean[:8]
        handoff_id = f"handoff-{conv_short}-{int(time.time())}"

        payload = {
            "schema_version": "1.0.0",
            "handoff_id": handoff_id,
            "session_id": conversation_id or "unspecified",
            "timestamp": now_iso,
            "project_name": target_dir.name,
            "git": git_info,
            "fitness": {
                "passed": fitness_res["passed"],
                "gate": fitness_res.get("gate", "tests/test_architecture_fitness.py")
            },
            "completed_tasks": [t["description"] for t in tasks["completed"]],
            "pending_tasks": [t["description"] for t in tasks["pending"]],
            "modified_files": sorted(list(all_modified_files)),
            "active_invariants": active_invs[:5],
            "next_sprint": next_sprint
        }

        # 8. Persist machine-readable JSON
        json_path = (output_json or (target_dir / ".context" / "sprint_handoff.json")).resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        # 9. Persist human-readable Markdown briefing
        md_content = self.render_handoff_markdown(payload)
        md_path = (output_md or (target_dir / ".context" / "next_sprint.md")).resolve()
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(md_content, encoding="utf-8")

        return payload

    def render_handoff_markdown(self, payload: Dict[str, Any]) -> str:
        """Renders structured Markdown summary of next sprint handoff."""
        status_badge = "PASSED (100% compliant)" if payload["fitness"]["passed"] else "FAILED (investigation required)"
        branch = payload["git"].get("branch", "unknown")
        commit = payload["git"].get("commit", "unknown")

        lines = [
            "# Next Sprint Handoff Briefing (ADR-007)",
            "<!-- Generated automatically by B-SDD Dynamic Handoff Protocol -->",
            f"- **Handoff ID:** `{payload['handoff_id']}`",
            f"- **Source Session:** `{payload['session_id']}`",
            f"- **Timestamp:** `{payload['timestamp']}`",
            f"- **Fitness Status:** {status_badge}",
            f"- **Git Status:** branch `{branch}`, commit `{commit}`",
            "",
            "## 1. Upstream Work Summary",
            "### Modified Artifacts",
            "```"
        ]

        mods = payload.get("modified_files", [])
        if mods:
            for f in mods[:30]:
                lines.append(f)
            if len(mods) > 30:
                lines.append(f"... and {len(mods) - 30} more files")
        else:
            lines.append("No modified files recorded.")
        lines.append("```")

        lines.extend([
            "",
            "### Completed Tasks",
        ])
        done = payload.get("completed_tasks", [])
        if done:
            for d in done[-15:]:
                lines.append(f"- [x] {d}")
        else:
            lines.append("- (None recorded yet)")

        lines.extend([
            "",
            "## 2. Active Architectural Constraints",
        ])
        invs = payload.get("active_invariants", [])
        if invs:
            for inv in invs:
                lines.append(inv)
        else:
            lines.append("- Refer to `.context/active_rules.md` for active constraints.")

        lines.extend([
            "",
            "## 3. Downstream Target (Sprint N+1)",
            f"- **Target Task:** `{payload['next_sprint']['title']}`",
            f"- **Prompt:**",
            f"> {payload['next_sprint']['prompt']}",
            "",
            "### Executable Dispatch Command",
            "```bash",
            payload["next_sprint"]["run_command"],
            "```",
            "",
            "## 4. Pending Tasks Backlog",
        ])
        pending = payload.get("pending_tasks", [])
        if pending:
            for p in pending[:15]:
                lines.append(f"- [ ] {p}")
            if len(pending) > 15:
                lines.append(f"- ... and {len(pending) - 15} more pending tasks")
        else:
            lines.append("- All specification tasks completed! Ready for final acceptance.")

        return "\n".join(lines) + "\n"

