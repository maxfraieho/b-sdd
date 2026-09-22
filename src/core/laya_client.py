#!/usr/bin/env python3
"""
Laya Decision Engine Client Hook.
Zero-dependency client for the System 1 non-autoregressive decision engine
hosted on Google Pixel 7 (Podroid Alpine VM: 192.168.3.251:9623).
Provides sub-40ms decision queries with zero RAM overhead on Host .161.
Gracefully degrades with fallback=True if Podroid is sleeping or unreachable (ADR-002).
"""
import hashlib
import json
import logging
import os
import socket
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

DEFAULT_LAYA_HOST = os.getenv("LAYA_HOST", "192.168.3.251")
DEFAULT_LAYA_PORT = int(os.getenv("LAYA_PORT", "9623"))
DEFAULT_TIMEOUT = float(os.getenv("LAYA_TIMEOUT", "3.0"))

logger = logging.getLogger("LayaClient")



DOMAIN_SKILL_RECOMMENDATIONS = {
    "core": ["b-sdd", "intent-continuity", "safe-refactor"],
    "ui": ["frontend-design", "make-interfaces-feel-better", "web-artifacts-builder"],
    "skills": ["skill-creator", "skill-audit", "writing-great-skills"],
    "infrastructure": ["cli-developer", "mcp-builder", "defense-in-depth"],
}


class LayaClient:
    """Zero-dependency HTTP client for Laya System 1 decision engine on Podroid."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        timeout: float = DEFAULT_TIMEOUT
    ):
        self.host = host or DEFAULT_LAYA_HOST
        self.port = port or DEFAULT_LAYA_PORT
        self.timeout = timeout
        self.base_url = f"http://{self.host}:{self.port}"

    def check_health(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Queries GET /health endpoint on Podroid.
        Returns health status dictionary or error dict without throwing exceptions.
        """
        to = timeout if timeout is not None else self.timeout
        url = f"{self.base_url}/health"
        headers = {"User-Agent": "B-SDD-LayaClient/1.0"}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=to) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data
                return {"status": "down", "error": f"Unexpected HTTP status {resp.status}"}
        except Exception as e:
            return {"status": "down", "error": str(e)}

    def classify_heuristic(
        self,
        state: Dict[str, Any],
        questions: Optional[Dict[str, Any]] = None,
        instruction_name: str = "",
        directive: str = ""
    ) -> Dict[str, Any]:
        """
        Static heuristic classifier for task domain, ADR violation probability,
        and recommended procedural skills from the 48 Golden Core catalog.
        """
        qs = questions or {}
        combined_text = " ".join([
            instruction_name,
            directive,
            str(state.get("instruction_name", "")),
            str(state.get("task", "")),
            str(state.get("directive", "")),
            str(state.get("sprint_id", ""))
        ]).lower()

        # 1. Determine task domain
        if any(k in combined_text for k in ("ui", "frontend", "css", "html", "cockpit", "astryx", "web", "panel", "view", "react", "component", "theme", "layout", "modal")):
            domain = "ui"
        elif any(k in combined_text for k in ("skill", "skills", "catalog", "golden", "dump_skills", "skills_dump", "crystalliz", "agent_skills", "active_skills")):
            domain = "skills"
        elif any(k in combined_text for k in ("podroid", "watchdog", "deploy", "systemd", "alpine", "daemon", "service", "infra", "network", "n8n", "host", "ssh", "curl", "socket", "port", "pixel")):
            domain = "infrastructure"
        else:
            domain = "core"

        # 2. Assess probability of ADR invariant violation P(violation)
        has_blockers = bool(state.get("blocked") or state.get("blockers"))
        risk = str(state.get("risk_level", "low")).lower()
        invariants_ok = state.get("invariants_satisfied", True)

        if not invariants_ok:
            p_violation = 0.90
        elif has_blockers or risk in ("critical", "high"):
            p_violation = 0.85
        elif any(w in combined_text for w in ("bypass", "override", "force", "disable", "external_dep", "break", "unverified")):
            p_violation = 0.65
        elif any(w in combined_text for w in ("refactor", "migration", "isolate", "extract")):
            p_violation = 0.15
        else:
            p_violation = 0.02

        # 3. Choice, score, noul primitives
        unresolved_questions = [
            k for k, v in qs.items()
            if isinstance(v, dict) and v.get("status") != "RESOLVED"
        ]

        if p_violation >= 0.7:
            choice = "HALT_FOR_INSPECTION"
            action = "REQUIRE_OPERATOR_REVIEW"
        elif unresolved_questions:
            choice = "CLARIFY_QUESTIONS"
            action = "ROUTE_TO_OPERATOR"
        elif p_violation >= 0.4:
            choice = "REMEDIATE_INVARIANTS"
            action = "APPLY_AUTONOMOUS_FIX"
        else:
            choice = "PROCEED"
            action = "AUTO_EXECUTE"

        score = round(max(0.0, min(1.0, 1.0 - p_violation)), 2)
        noul = bool(p_violation < 0.5 and choice == "PROCEED")

        # 4. Target skills recommendation
        rec_skills = list(DOMAIN_SKILL_RECOMMENDATIONS.get(domain, DOMAIN_SKILL_RECOMMENDATIONS["core"]))
        skills_formatted = ", ".join(f"@{s}" for s in rec_skills)

        return {
            "domain": domain,
            "p_violation": p_violation,
            "choice": choice,
            "score": score,
            "noul": noul,
            "decision": choice,
            "action": action,
            "recommended_skills": rec_skills,
            "skills_formatted": skills_formatted
        }

    def query_decision(
        self,
        state: Dict[str, Any],
        questions: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Queries non-autoregressive decision from Laya engine on Pixel 7.

        Args:
            state: Current pipeline/sprint state dictionary.
            questions: Dictionary of pending/active architectural questions.
            timeout: Request timeout in seconds (default: 3.0s).

        Returns:
            Dict containing decision, confidence, latency, or graceful fallback response.
            Never raises exceptions to guarantee supervisor resilience.
        """
        if questions is None:
            questions = {}

        to = timeout if timeout is not None else self.timeout
        url = f"{self.base_url}/predict"
        payload = {
            "state": state,
            "questions": questions,
            "timestamp": time.time()
        }

        try:
            body = json.dumps(payload).encode("utf-8")
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "B-SDD-LayaClient/1.0"
            }
            req = urllib.request.Request(url, data=body, headers=headers)

            t0 = time.perf_counter()
            with urllib.request.urlopen(req, timeout=to) as resp:
                raw_resp = resp.read().decode("utf-8")
                elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

                if resp.status == 200:
                    data = json.loads(raw_resp)
                    data["fallback"] = False
                    if "latency_ms" not in data:
                        data["latency_ms"] = elapsed_ms
                    return data
                else:
                    return self._fallback_response(state, questions, f"HTTP {resp.status}: {raw_resp}")

        except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout, TimeoutError, Exception) as e:
            logger.warning(f"Laya daemon on {self.base_url} unreachable: {e}. Activating graceful fallback.")
            return self._fallback_response(state, questions, str(e))

    def _fallback_response(
        self,
        state: Dict[str, Any],
        questions: Dict[str, Any],
        error_msg: str
    ) -> Dict[str, Any]:
        """Local heuristic fallback when Podroid is asleep or unreachable."""
        state_str = json.dumps(state, sort_keys=True, default=str)
        digest = hashlib.sha256(state_str.encode("utf-8")).hexdigest()[:16]

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
            "state_digest": digest,
            "note": "Podroid Laya engine asleep or unreachable; safe heuristic applied."
        }

    def predict(
        self,
        directive: str = "",
        state: Optional[Dict[str, Any]] = None,
        questions: Optional[Dict[str, Any]] = None,
        instruction_name: str = "",
        sprint_id: str = "",
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Sub-40ms Pre-Flight classification before spawning agy or executing tasks.
        Queries Laya System 1 decision engine on Podroid, or safely falls back to local heuristic.
        """
        st = dict(state) if state else {}
        if instruction_name and "instruction_name" not in st:
            st["instruction_name"] = instruction_name
        if directive and "directive" not in st:
            st["directive"] = directive
        if sprint_id and "sprint_id" not in st:
            st["sprint_id"] = sprint_id

        res = self.query_decision(state=st, questions=questions, timeout=timeout)
        if res.get("fallback"):
            logger.warning("[WARN] Laya offline, using static heuristic")
            heuristic = self.classify_heuristic(st, questions or {}, instruction_name, directive)
            for k, v in heuristic.items():
                if k not in res or res[k] is None:
                    res[k] = v
        else:
            if "domain" not in res:
                heuristic = self.classify_heuristic(st, questions or {}, instruction_name, directive)
                for k in ("domain", "p_violation", "recommended_skills", "skills_formatted", "choice", "score", "noul"):
                    res[k] = res.get(k, heuristic[k])
        return res

    def rerank_adrs(
        self,
        query: str,
        adr_candidates: List[Dict[str, Any]],
        top_k: int = 3,
        timeout: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Vector 1: Utopia DB & ADR Cross-Encoder Re-Ranker (Semantic Distillation).
        Queries POST /rerank on Pixel 7 Podroid.
        Falls back to local lexical/stem scoring if Podroid is asleep or unreachable (ADR-002).
        """
        to = timeout if timeout is not None else self.timeout
        url = f"{self.base_url}/rerank"
        payload = {
            "query": query,
            "candidates": adr_candidates,
            "top_k": top_k,
            "timestamp": time.time()
        }

        try:
            body = json.dumps(payload).encode("utf-8")
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "B-SDD-LayaClient/1.0"
            }
            req = urllib.request.Request(url, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=to) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    results = data.get("results", [])
                    for r in results:
                        r["fallback"] = False
                    return results
                else:
                    return self._fallback_rerank(query, adr_candidates, top_k)
        except Exception as e:
            logger.warning(f"Laya /rerank on {self.base_url} unreachable: {e}. Activating graceful fallback.")
            return self._fallback_rerank(query, adr_candidates, top_k)

    def _fallback_rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Local lexical and token-stem re-ranker fallback."""
        if not candidates:
            return []

        import re
        q_tokens = set(re.findall(r"\w+", query.lower()))

        scored_candidates = []
        for cand in candidates:
            cand_id = cand.get("id", "")
            title = cand.get("title", "")
            content = cand.get("content", "")
            invariants = cand.get("invariants", [])
            component = cand.get("component", "")

            title_tokens = set(re.findall(r"\w+", title.lower()))
            inv_text = " ".join(invariants) if isinstance(invariants, list) else str(invariants)
            inv_tokens = set(re.findall(r"\w+", inv_text.lower()))
            comp_tokens = set(re.findall(r"\w+", component.lower()))
            body_tokens = set(re.findall(r"\w+", content.lower()[:1000]))

            def token_match_score(query_tokens, target_tokens, full_text):
                if not query_tokens:
                    return 0.0
                matches = 0
                for q in query_tokens:
                    if q in full_text:
                        matches += 1
                    elif any(len(q) >= 4 and (t.startswith(q[:4]) or q.startswith(t[:4])) for t in target_tokens):
                        matches += 0.8
                return min(1.0, matches / max(1, len(query_tokens)))

            title_overlap = token_match_score(q_tokens, title_tokens, title.lower())
            inv_overlap = token_match_score(q_tokens, inv_tokens, inv_text.lower())
            comp_overlap = token_match_score(q_tokens, comp_tokens, component.lower())
            body_overlap = token_match_score(q_tokens, body_tokens, content.lower())

            raw_score = (inv_overlap * 3.0) + (title_overlap * 2.5) + (comp_overlap * 1.5) + (body_overlap * 1.0)
            norm_score = round(min(1.0, raw_score / 3.0), 3)

            if cand_id and cand_id.lower() in query.lower():
                norm_score = max(norm_score, 0.95)

            item = dict(cand)
            item["relevance_score"] = norm_score
            item["fallback"] = True
            scored_candidates.append(item)

        scored_candidates.sort(key=lambda x: x.get("relevance_score", 0.0), reverse=True)
        return scored_candidates[:top_k]

    def compact_traceback(
        self,
        raw_traceback: str,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Vector 3: Log & Traceback Compaction (Error Triage).
        Queries POST /triage on Pixel 7 Podroid.
        Extracts error taxonomy, failing file/line, invariant, and 5-line diagnostic capsule.
        """
        to = timeout if timeout is not None else self.timeout
        url = f"{self.base_url}/triage"
        payload = {
            "raw_traceback": raw_traceback,
            "timestamp": time.time()
        }

        try:
            body = json.dumps(payload).encode("utf-8")
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "B-SDD-LayaClient/1.0"
            }
            req = urllib.request.Request(url, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=to) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    triage = data.get("triage", {})
                    triage["fallback"] = False
                    return triage
                else:
                    return self._fallback_compact_traceback(raw_traceback)
        except Exception as e:
            logger.warning(f"Laya /triage on {self.base_url} unreachable: {e}. Activating graceful fallback.")
            return self._fallback_compact_traceback(raw_traceback)

    def _fallback_compact_traceback(self, raw_traceback: str) -> Dict[str, Any]:
        """Local regex-based error triage fallback."""
        import re
        tb = raw_traceback or ""
        lines = [line.strip() for line in tb.splitlines() if line.strip()]

        error_type = "AssertionError"
        if any(k in tb for k in ("SyntaxError", "IndentationError", "TabError")):
            error_type = "SyntaxError"
        elif any(k in tb for k in ("ImportError", "ModuleNotFoundError", "No module named")):
            error_type = "ImportError"
        elif any(k in tb for k in ("ConnectionRefusedError", "URLError", "timeout", "timed out", "ConnectionError", "NetworkError")):
            error_type = "FlakyNetwork"
        elif any(k in tb for k in ("OperationalError", "database is locked", "deadlock detected", "DatabaseError")):
            error_type = "DatabaseLock"
        elif any(k in tb for k in ("InvariantViolation", "DriftError", "ArchitectureFitnessError", "state drift")):
            error_type = "StateDrift"
        elif "AssertionError" in tb or "assert " in tb:
            error_type = "AssertionError"
        else:
            m_err = re.search(r"([A-Z][A-Za-z0-9_]+Error):", tb)
            if m_err:
                error_type = m_err.group(1)
            else:
                error_type = "TestFailure"

        file_path = "unknown"
        line_num = 0
        file_matches = re.findall(r'File ["\']([^"\']+)["\'], line (\d+)', tb)
        if file_matches:
            chosen = file_matches[-1]
            for f_match, l_match in reversed(file_matches):
                if "tests/" in f_match or "src/" in f_match:
                    chosen = (f_match, l_match)
                    break
            file_path, line_num = chosen[0], int(chosen[1])
            if "/projects/b-sdd/" in file_path:
                file_path = file_path.split("/projects/b-sdd/", 1)[-1]
        else:
            pt_match = re.search(r'([a-zA-Z0-9_\-/\\]+\.py):(\d+):', tb)
            if pt_match:
                file_path = pt_match.group(1)
                line_num = int(pt_match.group(2))

        inv_match = re.search(r'(INV-[A-Z0-9_\-]+|ADR-\d{3})', tb)
        failed_invariant = inv_match.group(1) if inv_match else "N/A"

        summary = ""
        err_lines = [l for l in lines if l.startswith("E ") or f"{error_type}:" in l or "assert " in l]
        if err_lines:
            summary = err_lines[-1].lstrip("E ").strip()
        elif lines:
            summary = lines[-1][:120]
        else:
            summary = "Unknown failure occurred"

        if summary.startswith(f"{error_type}:"):
            summary = summary[len(error_type)+1:].strip()
        if failed_invariant != "N/A" and summary.startswith(f"{failed_invariant}:"):
            summary = summary[len(failed_invariant)+1:].strip()

        summary = summary.replace('"', "'")

        capsule = (
            f"[ERROR_TRIAGE: Type={error_type}, File={file_path}:{line_num}, "
            f"FailedInvariant={failed_invariant}, Summary='{summary}']"
        )

        return {
            "error_type": error_type,
            "file": file_path,
            "line": line_num,
            "failed_invariant": failed_invariant,
            "summary": summary,
            "capsule": capsule,
            "tokens_estimated": len(capsule.split()),
            "fallback": True
        }


_global_client: Optional[LayaClient] = None


def get_laya_client(
    host: Optional[str] = None,
    port: Optional[int] = None,
    timeout: float = DEFAULT_TIMEOUT
) -> LayaClient:
    """Returns singleton or configured LayaClient instance."""
    global _global_client
    if _global_client is None or host is not None or port is not None:
        _global_client = LayaClient(host=host, port=port, timeout=timeout)
    return _global_client


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Laya Decision Engine Client Hook (B-SDD)")
    parser.add_argument("--state", default="{}", help="State JSON payload")
    parser.add_argument("--questions", default="{}", help="Questions JSON payload")
    parser.add_argument("--instruction-name", default="", help="Instruction name")
    parser.add_argument("--directive", default="", help="Directive or prompt text")
    parser.add_argument("--sprint-id", default="", help="Sprint ID")
    parser.add_argument("--host", default=None, help="Host override")
    parser.add_argument("--port", type=int, default=None, help="Port override")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="Timeout in seconds")
    parser.add_argument("--check-health", "--health", dest="check_health", action="store_true", help="Check daemon health")
    parser.add_argument("--stdin", action="store_true", help="Read directive from standard input")
    args = parser.parse_args()

    client = get_laya_client(host=args.host, port=args.port, timeout=args.timeout)
    if args.check_health:
        result = client.check_health()
    else:
        import sys
        directive_text = args.directive
        if args.stdin and not sys.stdin.isatty():
            try:
                stdin_input = sys.stdin.read().strip()
                if stdin_input:
                    directive_text = stdin_input
            except Exception:
                pass

        try:
            state_dict = json.loads(args.state)
        except Exception:
            state_dict = {"raw_state": args.state}
        try:
            questions_dict = json.loads(args.questions)
        except Exception:
            questions_dict = {}

        result = client.predict(
            directive=directive_text,
            state=state_dict,
            questions=questions_dict,
            instruction_name=args.instruction_name,
            sprint_id=args.sprint_id
        )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

