"""
Unit and Integration Tests for Fast-Path Pre-Commit & Diff Risk Gatekeeper (Vector 2).
Sprint 030 - OUTBOX_AGI_SPRINT_030_FAST_PATH_DIFF_RISK_GATEKEEPER.
Complies with ADR-002 (Pure Stdlib Core) and ADR-014 (Laya System 1 & Circuit Breaker).
"""
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.core.diff_risk_gatekeeper import DiffRiskGatekeeper
from src.core.laya_client import LayaClient

ROOT = Path(__file__).resolve().parent.parent


class TestDiffRiskGatekeeper:
    """Test suite for Fast-Path Diff Risk Gatekeeper (Sprint 030)."""

    def test_empty_diff_proceeds(self):
        gatekeeper = DiffRiskGatekeeper()
        res = gatekeeper.evaluate_diff_risk("")
        assert res["choice"] == "PROCEED"
        assert res["allow_commit"] is True
        assert res["score"] == 1.0
        assert res["p_violation"] == 0.0

    def test_low_risk_diff_proceeds(self):
        gatekeeper = DiffRiskGatekeeper()
        safe_diff = """diff --git a/docs/adr/ADR-015.md b/docs/adr/ADR-015.md
new file mode 100644
--- /dev/null
+++ b/docs/adr/ADR-015.md
@@ -0,0 +1,5 @@
+# ADR-015: Documentation Enhancement
+* Status: Proposed
+* Context: Adding clarifications to documentation
+"""
        res = gatekeeper.evaluate_diff_risk(safe_diff)
        assert res["choice"] == "PROCEED"
        assert res["p_violation"] < 0.15
        assert res["allow_commit"] is True
        assert res["action"] == "INSTANT_COMMIT"

    def test_medium_risk_untested_core_remediates(self):
        gatekeeper = DiffRiskGatekeeper()
        # Modifying src/core without touching tests
        core_diff = """diff --git a/src/core/router.py b/src/core/router.py
--- a/src/core/router.py
+++ b/src/core/router.py
@@ -10,3 +10,25 @@
+def mutate_critical_pipeline_state():
+    # 25 lines of untested core logic
+    pass
"""
        res = gatekeeper.evaluate_diff_risk(core_diff)
        assert res["choice"] == "REMEDIATE_INVARIANTS"
        assert 0.15 <= res["p_violation"] <= 0.65
        assert res["allow_commit"] is False
        assert res["action"] == "RUN_LOCAL_SAFE_REFACTOR"
        assert res["features"]["untested_core_mutation"] is True

    def test_high_risk_suspicious_patterns_halt(self):
        gatekeeper = DiffRiskGatekeeper()

        # Suspicious eval
        diff_eval = """diff --git a/src/core/bad.py b/src/core/bad.py
+++ b/src/core/bad.py
@@ -0,0 +1,2 @@
+def run(cmd):
+    return eval(cmd)
"""
        res_eval = gatekeeper.evaluate_diff_risk(diff_eval)
        assert res_eval["choice"] == "HALT_FOR_INSPECTION"
        assert res_eval["p_violation"] > 0.65
        assert res_eval["allow_commit"] is False
        assert res_eval["action"] == "REQUIRE_OPERATOR_REVIEW_PHI6"

        # Suspicious shell=True
        diff_shell = """diff --git a/src/core/run.py b/src/core/run.py
+++ b/src/core/run.py
@@ -0,0 +1,2 @@
+subprocess.Popen("rm -rf /", shell=True)
"""
        res_shell = gatekeeper.evaluate_diff_risk(diff_shell)
        assert res_shell["choice"] == "HALT_FOR_INSPECTION"
        assert res_shell["allow_commit"] is False

    def test_diff_feature_parsing_statistics(self):
        diff_sample = """diff --git a/src/core/a.py b/src/core/a.py
--- a/src/core/a.py
+++ b/src/core/a.py
@@ -1,2 +1,3 @@
-old line
+new line 1
+new line 2
diff --git a/tests/test_a.py b/tests/test_a.py
--- a/tests/test_a.py
+++ b/tests/test_a.py
@@ -5,1 +5,2 @@
+added test line
"""
        features = DiffRiskGatekeeper.parse_diff(diff_sample)
        assert features["changed_files_count"] == 2
        assert features["additions"] == 3
        assert features["deletions"] == 1
        assert features["total_lines"] == 4
        assert features["touches_core"] is True
        assert features["touches_tests"] is True
        assert features["untested_core_mutation"] is False
        assert features["has_suspicious_patterns"] is False

    def test_mock_laya_remote_prediction(self):
        mock_laya_response = {
            "status": "ok",
            "choice": "PROCEED",
            "score": 0.98,
            "p_violation": 0.02,
            "noul": True,
            "decision": "PROCEED",
            "action": "AUTO_EXECUTE",
            "latency_ms": 7.4
        }

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.read.return_value = json.dumps(mock_laya_response).encode("utf-8")
            mock_urlopen.return_value.__enter__.return_value = mock_resp

            gatekeeper = DiffRiskGatekeeper()
            safe_diff = "diff --git a/README.md b/README.md\n+++ b/README.md\n@@ -1 +1 @@\n+updated"
            res = gatekeeper.evaluate_diff_risk(safe_diff)

            assert res["choice"] == "PROCEED"
            assert res["allow_commit"] is True
            assert res["p_violation"] == 0.02

    def test_graceful_fallback_when_laya_offline(self):
        with patch("urllib.request.urlopen", side_effect=ConnectionRefusedError("Pixel 7 asleep")):
            gatekeeper = DiffRiskGatekeeper()
            safe_diff = "diff --git a/docs/spec.md b/docs/spec.md\n+++ b/docs/spec.md\n@@ -1 +1 @@\n+doc change"
            res = gatekeeper.evaluate_diff_risk(safe_diff)

            assert res["status"] == "ok"
            assert res["fallback"] is True
            assert res["choice"] == "PROCEED"
            assert res["allow_commit"] is True

    def test_cli_subprocess_invocation(self):
        # Safe diff -> exit code 0
        safe_cmd = [
            sys.executable, "-m", "src.core.diff_risk_gatekeeper",
            "--diff-text", "diff --git a/docs/note.md b/docs/note.md\n+++ b/docs/note.md\n@@ -1 +1 @@\n+note"
        ]
        p_safe = subprocess.run(safe_cmd, cwd=str(ROOT), capture_output=True, text=True)
        assert p_safe.returncode == 0
        assert "Verdict=PROCEED" in p_safe.stdout

        # Blocked diff -> exit code 1
        blocked_cmd = [
            sys.executable, "-m", "src.core.diff_risk_gatekeeper",
            "--diff-text", "diff --git a/src/core/evil.py b/src/core/evil.py\n+++ b/src/core/evil.py\n@@ -0,0 +1 @@\n+eval('1')"
        ]
        p_blocked = subprocess.run(blocked_cmd, cwd=str(ROOT), capture_output=True, text=True)
        assert p_blocked.returncode == 1
        assert "Commit BLOCKED" in p_blocked.stdout

    def test_pure_stdlib_compliance_adr002(self):
        import ast
        gatekeeper_path = ROOT / "src" / "core" / "diff_risk_gatekeeper.py"
        tree = ast.parse(gatekeeper_path.read_text(encoding="utf-8"))

        imported_modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module.split(".")[0])

        stdlib_whitelist = {
            "argparse", "json", "logging", "os", "re", "subprocess",
            "sys", "time", "typing", "pathlib", "src"
        }
        for mod in imported_modules:
            assert mod in stdlib_whitelist, f"Non-stdlib import detected: {mod} (violates ADR-002)"
