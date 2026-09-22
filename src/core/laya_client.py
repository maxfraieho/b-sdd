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
from typing import Any, Dict, Optional

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
    parser.add_argument("--check-health", action="store_true", help="Check daemon health")
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

