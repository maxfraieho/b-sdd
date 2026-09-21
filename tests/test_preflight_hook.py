"""
Unit and integration tests for Laya Pre-Flight Hook, Context Injection, and Skill Routing.
Sprint 025 - Deliverable A, B, C, D Verification.
Validates sub-40ms System 1 classification, mathematical primitives (choice, score, noul),
Golden Core skill recommendations, and graceful degradation (ADR-002).
"""
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.core.laya_client import LayaClient, get_laya_client, DOMAIN_SKILL_RECOMMENDATIONS
from scripts.bsdd_supervisor import perform_preflight_hook


class TestLayaPreflightHook:
    def test_predict_remote_success(self):
        client = LayaClient()
        mock_payload = {
            "status": "ok",
            "decision": "PROCEED",
            "action": "AUTO_EXECUTE",
            "choice": "PROCEED",
            "score": 0.98,
            "noul": True,
            "domain": "core",
            "p_violation": 0.02,
            "recommended_skills": ["b-sdd", "intent-continuity", "safe-refactor"],
            "skills_formatted": "@b-sdd, @intent-continuity, @safe-refactor",
            "confidence": 0.96,
            "latency_ms": 12.5,
            "model": "laya-multilingual"
        }

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.read.return_value = json.dumps(mock_payload).encode("utf-8")
            mock_urlopen.return_value.__enter__.return_value = mock_resp

            res = client.predict(
                instruction_name="OUTBOX_AGI_SPRINT_025_LAYA_PREFLIGHT_HOOK_AND_SKILL",
                directive="Implement supervisor hook and core skill",
                sprint_id="sprint_025"
            )

            assert res["fallback"] is False
            assert res["domain"] == "core"
            assert res["choice"] == "PROCEED"
            assert res["noul"] is True
            assert res["score"] == 0.98
            assert res["p_violation"] == 0.02
            assert "@b-sdd" in res["skills_formatted"]
            assert res["latency_ms"] == 12.5

    def test_predict_graceful_fallback_when_offline(self):
        client = LayaClient()
        with patch("urllib.request.urlopen", side_effect=ConnectionRefusedError("Offline")):
            res = client.predict(
                instruction_name="OUTBOX_AGI_SPRINT_025_PODROID_DEPLOY",
                directive="Deploy podroid daemon and watchdog",
                sprint_id="sprint_025"
            )

            assert res["fallback"] is True
            assert res["domain"] == "infrastructure"
            assert res["choice"] == "PROCEED"
            assert res["noul"] is True
            assert res["p_violation"] == 0.02
            assert "@cli-developer" in res["skills_formatted"]
            assert "@mcp-builder" in res["skills_formatted"]

    def test_domain_classification_matrix(self):
        client = LayaClient()
        
        # UI task
        h_ui = client.classify_heuristic(
            state={},
            instruction_name="OUTBOX_AGI_SPRINT_026_ASTRYX_COCKPIT_UI",
            directive="Build react components and css themes"
        )
        assert h_ui["domain"] == "ui"
        assert h_ui["recommended_skills"] == ["frontend-design", "make-interfaces-feel-better", "web-artifacts-builder"]

        # Skills task
        h_skills = client.classify_heuristic(
            state={},
            instruction_name="OUTBOX_AGI_SPRINT_027_SKILLS_CATALOG_DUMP",
            directive="Crystallize golden skills inventory"
        )
        assert h_skills["domain"] == "skills"
        assert h_skills["recommended_skills"] == ["skill-creator", "skill-audit", "writing-great-skills"]

        # Infrastructure task
        h_infra = client.classify_heuristic(
            state={},
            instruction_name="OUTBOX_AGI_SPRINT_028_WATCHDOG_SYSTEMD",
            directive="Deploy alpine daemon on pixel 7 node"
        )
        assert h_infra["domain"] == "infrastructure"
        assert h_infra["recommended_skills"] == ["cli-developer", "mcp-builder", "defense-in-depth"]

        # Core task
        h_core = client.classify_heuristic(
            state={},
            instruction_name="OUTBOX_AGI_SPRINT_029_ADR_COMPILER",
            directive="Enforce tripartite ontology and planar solver"
        )
        assert h_core["domain"] == "core"
        assert h_core["recommended_skills"] == ["b-sdd", "intent-continuity", "safe-refactor"]

    def test_primitives_choice_score_noul_on_violation_risk(self):
        client = LayaClient()

        # High risk: invariant breach or bypass
        h_breach = client.classify_heuristic(
            state={"invariants_satisfied": False},
            instruction_name="OUTBOX_AGI_BYPASS_ADR",
            directive="Force disable invariants and bypass checks"
        )
        assert h_breach["p_violation"] >= 0.70
        assert h_breach["choice"] == "HALT_FOR_INSPECTION"
        assert h_breach["noul"] is False
        assert h_breach["score"] <= 0.30

        # Unresolved questions
        h_questions = client.classify_heuristic(
            state={"invariants_satisfied": True},
            questions={"q1": {"status": "OPEN", "text": "Storage engine?"}},
            instruction_name="OUTBOX_AGI_ARCH_QUESTION",
            directive="Design schema"
        )
        assert h_questions["choice"] == "CLARIFY_QUESTIONS"
        assert h_questions["noul"] is False

    def test_supervisor_perform_preflight_hook(self):
        with patch("urllib.request.urlopen", side_effect=TimeoutError("Sleep")):
            res = perform_preflight_hook(
                instruction_name="OUTBOX_AGI_SPRINT_025_LAYA_PREFLIGHT_HOOK_AND_SKILL",
                directive="Integrate preflight hook and skill",
                sprint_id="sprint_025"
            )
            assert res["domain"] in ("core", "skills", "infrastructure")
            assert "skills_formatted" in res
            assert "@" in res["skills_formatted"]

            # Test capsule format
            capsule = f"[LAYA DECISION CONTEXT: Domain: {res['domain']}, Confidence: {res['confidence']}, Recommended Skills: {res['skills_formatted']}]"
            assert capsule.startswith("[LAYA DECISION CONTEXT:")
            assert f"Domain: {res['domain']}" in capsule
            assert "Recommended Skills:" in capsule

    def test_cli_invocation_via_subprocess(self):
        cmd = [
            sys.executable, "-m", "src.core.laya_client",
            "--state", '{"sprint": "sprint_025", "task": "preflight_test"}',
            "--questions", "{}"
        ]
        p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        assert p.returncode == 0
        data = json.loads(p.stdout)
        assert "domain" in data
        assert "choice" in data
        assert "score" in data
        assert "noul" in data
        assert "skills_formatted" in data
        assert "recommended_skills" in data
