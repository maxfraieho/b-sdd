#!/usr/bin/env python3
"""
B-SDD Fast-Path Pre-Commit & Diff Risk Gatekeeper (Vector 2).
Sprint 030 - OUTBOX_AGI_SPRINT_030_FAST_PATH_DIFF_RISK_GATEKEEPER.
100% Python 3 Standard Library (ADR-002 Pure Stdlib Core).

Evaluates staged git diffs via Laya System 1 non-autoregressive engine (Pixel 7 :9623):
- P(violation) < 0.15      -> PROCEED (Instant commit, 0 tokens)
- 0.15 <= P <= 0.65       -> REMEDIATE_INVARIANTS (Run local safe-refactor)
- P > 0.65                -> HALT_FOR_INSPECTION (Veto, escalate to Operator Φ6)
"""
import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

# Pure StdLib imports
from src.core.laya_client import LayaClient, get_laya_client

logger = logging.getLogger("DiffRiskGatekeeper")

SUSPICIOUS_DIFF_PATTERNS = [
    (r"\beval\(", "Dynamic code execution via eval()"),
    (r"\bexec\(", "Dynamic code execution via exec()"),
    (r"shell\s*=\s*True", "Unsanitized shell subprocess execution"),
    (r"\bbreakpoint\(|\bimport\s+pdb", "Leftover interactive debugging breakpoint"),
    (r"invariants_satisfied\s*=\s*False", "Hardcoded invariant satisfaction breach"),
    (r"\bno-verify\b|\bskip-fitness\b|\bskip-compile\b", "Bypass of architectural gates"),
    (r"\bdisable_invariants\b|\boverride_safety\b", "Explicit safety gate bypass"),
    (r"BEGIN\s+(PRIVATE\s+KEY|RSA\s+PRIVATE\s+KEY)", "Potential leaked cryptographic private key"),
]


class DiffRiskGatekeeper:
    """Fast-Path Pre-Commit & Diff Risk Gatekeeper powered by Laya System 1."""

    def __init__(
        self,
        client: Optional[LayaClient] = None,
        timeout: float = 3.0
    ):
        self.client = client or get_laya_client(timeout=timeout)
        self.timeout = timeout

    @staticmethod
    def parse_diff(git_diff_text: str) -> Dict[str, Any]:
        """
        Extracts structural AST-level features from git diff text without external dependencies.
        """
        lines = git_diff_text.splitlines()
        changed_files: List[str] = []
        additions = 0
        deletions = 0
        added_lines: List[str] = []
        suspicious_matches: List[Dict[str, str]] = []

        current_file = ""
        for line in lines:
            if line.startswith("diff --git "):
                parts = line.split()
                if len(parts) >= 4:
                    b_path = parts[3]
                    if b_path.startswith("b/"):
                        current_file = b_path[2:]
                    else:
                        current_file = b_path
                    if current_file not in changed_files:
                        changed_files.append(current_file)
            elif line.startswith("+++ b/"):
                f = line[6:].strip()
                if f not in changed_files and f != "/dev/null":
                    changed_files.append(f)
                    current_file = f
            elif line.startswith("+") and not line.startswith("+++"):
                additions += 1
                content = line[1:].strip()
                added_lines.append(content)
                # Check for suspicious patterns in newly added lines of executable code files (excluding tests, dumps & docs)
                is_executable_code = (
                    current_file.endswith((".py", ".sh", ".bash", ".js", ".ts"))
                    and not current_file.startswith("tests/")
                    and "dump" not in current_file
                )
                if is_executable_code:
                    for pat, desc in SUSPICIOUS_DIFF_PATTERNS:
                        if re.search(pat, content):
                            suspicious_matches.append({
                                "pattern": pat,
                                "file": current_file,
                                "line_snippet": content[:100],
                                "reason": desc
                            })
            elif line.startswith("-") and not line.startswith("---"):
                deletions += 1

        total_lines = additions + deletions
        touches_core = any(f.startswith("src/core/") for f in changed_files)
        touches_tests = any(f.startswith("tests/") for f in changed_files)
        touches_infra = any(f.startswith("deploy/") or f.startswith("scripts/") or ".github" in f for f in changed_files)
        touches_docs = any(f.startswith("docs/") or f.endswith(".md") for f in changed_files)
        touches_adr = any("docs/adr/" in f for f in changed_files)

        # Detect if core was mutated without corresponding test additions/updates
        untested_core_mutation = touches_core and not touches_tests

        return {
            "changed_files_count": len(changed_files),
            "files": changed_files,
            "additions": additions,
            "deletions": deletions,
            "total_lines": total_lines,
            "touches_core": touches_core,
            "touches_tests": touches_tests,
            "touches_infra": touches_infra,
            "touches_docs": touches_docs,
            "touches_adr": touches_adr,
            "untested_core_mutation": untested_core_mutation,
            "has_suspicious_patterns": len(suspicious_matches) > 0,
            "suspicious_matches": suspicious_matches,
            "is_empty": len(lines) == 0 or total_lines == 0
        }

    def _static_heuristic_risk(self, features: Dict[str, Any]) -> Tuple[float, str, str, str, bool]:
        """
        Deterministic static heuristic risk calculation fallback (ADR-002 / ADR-014).
        Returns (p_violation, choice, action, reason, noul).
        """
        if features["is_empty"]:
            return 0.0, "PROCEED", "INSTANT_COMMIT", "Empty diff", True

        p = 0.02

        # 1. Critical security / invariant breaches
        if features["has_suspicious_patterns"]:
            p = max(p, 0.85)
            reasons = [m["reason"] for m in features["suspicious_matches"]]
            return p, "HALT_FOR_INSPECTION", "REQUIRE_OPERATOR_REVIEW_PHI6", "; ".join(reasons), False

        # 2. Untested core logic mutation
        if features["untested_core_mutation"]:
            p += 0.25

        # 3. Blast radius scaling
        if features["touches_core"]:
            p += 0.08
        if features["touches_infra"]:
            p += 0.05
        if features["total_lines"] > 300:
            p += 0.20
        elif features["total_lines"] > 100:
            p += 0.10
        if features["changed_files_count"] > 6:
            p += 0.15

        # 4. Safe operations discount (documentation or test-only changes)
        if features["touches_docs"] and not features["touches_core"] and not features["touches_infra"]:
            p = min(p, 0.03)

        p = round(max(0.0, min(1.0, p)), 2)

        if p < 0.15:
            choice = "PROCEED"
            action = "INSTANT_COMMIT"
            reason = "Diff within safe architectural invariant limits"
            noul = True
        elif p <= 0.65:
            choice = "REMEDIATE_INVARIANTS"
            action = "RUN_LOCAL_SAFE_REFACTOR"
            reason = "Moderate risk diff detected; invariant remediation or test coverage required"
            noul = False
        else:
            choice = "HALT_FOR_INSPECTION"
            action = "REQUIRE_OPERATOR_REVIEW_PHI6"
            reason = "High invariant breach risk; escalation to operator review mandated"
            noul = False

        return p, choice, action, reason, noul

    def evaluate_diff_risk(
        self,
        git_diff_text: str,
        correlation_id: str = ""
    ) -> Dict[str, Any]:
        """
        Main entry point for evaluating staged git diff risk.
        Invokes Laya System 1 on Pixel 7 with automatic fallback to static AST heuristics.
        """
        t0 = time.perf_counter()
        features = self.parse_diff(git_diff_text)

        if features["is_empty"]:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            capsule = "[DIFF_RISK_GATE: Verdict=PROCEED, P(violation)=0.00, Score=1.00, Action=INSTANT_COMMIT, AllowCommit=True]"
            return {
                "status": "ok",
                "choice": "PROCEED",
                "verdict": "PROCEED",
                "action": "INSTANT_COMMIT",
                "score": 1.0,
                "p_violation": 0.0,
                "noul": True,
                "allow_commit": True,
                "reason": "Empty diff",
                "features": features,
                "fallback": False,
                "latency_ms": elapsed_ms,
                "capsule": capsule,
                "correlation_id": correlation_id
            }

        # Query Laya edge inference node
        risk_level = "critical" if features["has_suspicious_patterns"] else ("high" if features["untested_core_mutation"] else "low")
        state_payload = {
            "task": "pre_commit_diff_risk",
            "instruction_name": "OUTBOX_AGI_SPRINT_030_FAST_PATH_DIFF_RISK_GATEKEEPER",
            "risk_level": risk_level,
            "invariants_satisfied": not features["has_suspicious_patterns"],
            "blocked": [m["reason"] for m in features["suspicious_matches"]] if features["has_suspicious_patterns"] else [],
            "diff_stats": {
                "files_count": features["changed_files_count"],
                "total_lines": features["total_lines"],
                "touches_core": features["touches_core"],
                "untested_core": features["untested_core_mutation"]
            }
        }

        remote_res = self.client.predict(
            directive=f"Pre-commit diff risk evaluation: {features['changed_files_count']} files, {features['total_lines']} lines",
            state=state_payload,
            timeout=self.timeout
        )

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        is_fallback = bool(remote_res.get("fallback", False))

        # Check whether we rely on remote model prediction or refine with local AST features
        if is_fallback or features["has_suspicious_patterns"] or features["untested_core_mutation"]:
            p_violation, choice, action, reason, noul = self._static_heuristic_risk(features)
            score = round(1.0 - p_violation, 2)
        else:
            p_violation = float(remote_res.get("p_violation", 0.02))
            score = float(remote_res.get("score", 0.98))
            choice = remote_res.get("choice", "PROCEED")
            action = remote_res.get("action", "AUTO_EXECUTE")
            noul = bool(remote_res.get("noul", True))
            reason = "Evaluated via Laya System 1 neural model"

            # Apply strict discrete thresholds from Sprint 030 specification:
            # P < 0.15 -> PROCEED
            # 0.15 <= P <= 0.65 -> REMEDIATE_INVARIANTS
            # P > 0.65 -> HALT_FOR_INSPECTION
            if p_violation < 0.15:
                choice = "PROCEED"
                action = "INSTANT_COMMIT"
            elif p_violation <= 0.65:
                choice = "REMEDIATE_INVARIANTS"
                action = "RUN_LOCAL_SAFE_REFACTOR"
            else:
                choice = "HALT_FOR_INSPECTION"
                action = "REQUIRE_OPERATOR_REVIEW_PHI6"

        allow_commit = (choice == "PROCEED")

        capsule = (
            f"[DIFF_RISK_GATE: Verdict={choice}, P(violation)={p_violation:.2f}, "
            f"Score={score:.2f}, Action={action}, AllowCommit={allow_commit}]"
        )

        return {
            "status": "ok",
            "choice": choice,
            "verdict": choice,
            "action": action,
            "score": score,
            "p_violation": p_violation,
            "noul": noul,
            "allow_commit": allow_commit,
            "reason": reason,
            "features": features,
            "fallback": is_fallback,
            "latency_ms": elapsed_ms,
            "capsule": capsule,
            "correlation_id": correlation_id
        }


def get_staged_diff(cwd: Optional[str] = None) -> str:
    """Executes git diff --cached to get currently staged changes."""
    try:
        res = subprocess.run(
            ["git", "diff", "--cached", "--unified=3"],
            capture_output=True,
            text=True,
            cwd=cwd or os.getcwd(),
            check=True
        )
        return res.stdout
    except Exception as e:
        logger.error(f"Failed to fetch staged git diff: {e}")
        return ""


def main():
    parser = argparse.ArgumentParser(description="B-SDD Fast-Path Pre-Commit & Diff Risk Gatekeeper")
    parser.add_argument("--cached", action="store_true", help="Evaluate staged git diff (default)")
    parser.add_argument("--diff-text", default="", help="Evaluate explicit raw diff text")
    parser.add_argument("--diff-file", default="", help="Evaluate diff text from file")
    parser.add_argument("--json", action="store_true", help="Print structured JSON output")
    parser.add_argument("--force", action="store_true", help="Bypass block and exit with code 0")
    parser.add_argument("--timeout", type=float, default=3.0, help="Laya query timeout")
    args = parser.parse_args()

    diff_text = ""
    if args.diff_text:
        diff_text = args.diff_text
    elif args.diff_file:
        try:
            with open(args.diff_file, "r", encoding="utf-8") as f:
                diff_text = f.read()
        except Exception as e:
            sys.stderr.write(f"Error reading diff file {args.diff_file}: {e}\n")
            sys.exit(1)
    else:
        diff_text = get_staged_diff()

    gatekeeper = DiffRiskGatekeeper(timeout=args.timeout)
    result = gatekeeper.evaluate_diff_risk(diff_text)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(result["capsule"])
        if not result["allow_commit"]:
            print(f"❌ Commit BLOCKED: {result['reason']}")
            print(f"▶ Recommended Action: {result['action']}")
            if result['choice'] == "REMEDIATE_INVARIANTS":
                print("💡 Suggestion: Run safe-refactor or add unit tests for modified core modules.")
            elif result['choice'] == "HALT_FOR_INSPECTION":
                print("⚠️ Critical security or invariant risk. Escalating to Operator Review (Φ6).")

    if args.force:
        print("⚠️ Bypass requested via --force. Exiting 0.")
        sys.exit(0)

    sys.exit(0 if result["allow_commit"] else 1)


if __name__ == "__main__":
    main()
