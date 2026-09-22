"""
Unit and Integration Tests for Laya System 1 Edge Cognitive Offloading & Token Optimization Suite.
Sprint 029 - Deliverable Phase 1: Vector 1 (ADR Re-Ranker) and Vector 3 (Traceback Compaction).
Complies with ADR-002 (Pure Stdlib Core) and ADR-014 (Laya System 1 & Circuit Breaker).
"""
import json
from unittest.mock import MagicMock, patch
import pytest

from src.core.laya_client import LayaClient, get_laya_client


class TestLayaTokenOptimization:
    """Tests for Vector 1 (ADR Re-ranking) and Vector 3 (Traceback Compaction)."""

    # -------------------------------------------------------------------------
    # VECTOR 1: Utopia DB & ADR Cross-Encoder Re-Ranker
    # -------------------------------------------------------------------------

    def test_rerank_adrs_mock_remote(self):
        client = LayaClient()
        mock_candidates = [
            {"id": "ADR-002", "title": "Deterministic Pre-Flight Compilation", "component": "core", "relevance_score": 0.95},
            {"id": "ADR-008", "title": "DRAKON Visual Logic", "component": "ui", "relevance_score": 0.35},
            {"id": "ADR-009", "title": "Astryx Design System", "component": "ui", "relevance_score": 0.10}
        ]

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.read.return_value = json.dumps({
                "status": "ok",
                "results": mock_candidates[:2],
                "count": 2,
                "latency_ms": 11.2,
                "sub_40ms": True
            }).encode("utf-8")
            mock_urlopen.return_value.__enter__.return_value = mock_resp

            results = client.rerank_adrs(
                query="compile active rules and check word budget",
                adr_candidates=mock_candidates,
                top_k=2
            )

            assert len(results) == 2
            assert results[0]["id"] == "ADR-002"
            assert results[0]["fallback"] is False
            assert results[0]["relevance_score"] >= 0.90

    def test_rerank_adrs_graceful_fallback(self):
        client = LayaClient()
        candidates = [
            {
                "id": "ADR-002",
                "title": "Deterministic Pre-Flight Compilation",
                "invariants": ["INV-002-01: Word count under 500 words"],
                "component": "core"
            },
            {
                "id": "ADR-009",
                "title": "Astryx Universal Cockpit Design",
                "invariants": ["INV-009-01: Dark theme and ergonomics"],
                "component": "ui"
            },
            {
                "id": "ADR-014",
                "title": "Laya System 1 Decision Engine",
                "invariants": ["INV-014-01: Sub-40ms latency on Pixel 7"],
                "component": "infrastructure"
            }
        ]

        with patch("urllib.request.urlopen", side_effect=ConnectionRefusedError("Pixel 7 asleep")):
            ranked = client.rerank_adrs(
                query="preflight compilation budget under 500 words",
                adr_candidates=candidates,
                top_k=2
            )

            assert len(ranked) == 2
            assert ranked[0]["id"] == "ADR-002"
            assert ranked[0]["fallback"] is True
            assert ranked[0]["relevance_score"] > 0.3

    def test_rerank_preserves_candidate_ordering_by_score(self):
        client = LayaClient()
        candidates = [
            {"id": "ADR-009", "title": "Astryx UI Cockpit", "component": "ui"},
            {"id": "ADR-014", "title": "Laya Decision Engine Edge Node", "component": "infrastructure"},
            {"id": "ADR-001", "title": "Bitemporal Intent Graph", "component": "core"}
        ]

        # Query targeting ADR-014
        ranked = client._fallback_rerank("pixel 7 edge decision engine", candidates, top_k=1)
        assert len(ranked) == 1
        assert ranked[0]["id"] == "ADR-014"

    # -------------------------------------------------------------------------
    # VECTOR 3: Log & Traceback Compaction (Error Triage)
    # -------------------------------------------------------------------------

    def test_compact_traceback_assertion_error_with_invariant(self):
        client = LayaClient()
        raw_tb = """
Traceback (most recent call last):
  File "/home/vokov/projects/b-sdd/src/core/planar_solver.py", line 42, in solve
    raise AssertionError("INV-008-01: Planar graph crossing count C > 0")
  File "/home/vokov/projects/b-sdd/tests/test_planar_solver.py", line 84, in test_planar
    solve(graph)
AssertionError: INV-008-01: Planar graph crossing count C > 0
"""
        triage = client._fallback_compact_traceback(raw_tb)

        assert triage["error_type"] == "AssertionError"
        assert "tests/test_planar_solver.py" in triage["file"]
        assert triage["line"] == 84
        assert triage["failed_invariant"] == "INV-008-01"
        assert "Planar graph crossing count C > 0" in triage["summary"]
        assert triage["capsule"].startswith("[ERROR_TRIAGE:")
        assert "Type=AssertionError" in triage["capsule"]
        assert "FailedInvariant=INV-008-01" in triage["capsule"]

    def test_compact_traceback_taxonomy_classification(self):
        client = LayaClient()

        # SyntaxError
        tb_syntax = "File 'src/foo.py', line 12\n  def bad(\nIndentationError: unexpected indent"
        res_syntax = client._fallback_compact_traceback(tb_syntax)
        assert res_syntax["error_type"] == "SyntaxError"

        # ImportError
        tb_import = "ModuleNotFoundError: No module named 'non_existent_module'"
        res_import = client._fallback_compact_traceback(tb_import)
        assert res_import["error_type"] == "ImportError"

        # FlakyNetwork
        tb_net = "urllib.error.URLError: <urlopen error [Errno 111] Connection refused>"
        res_net = client._fallback_compact_traceback(tb_net)
        assert res_net["error_type"] == "FlakyNetwork"

        # DatabaseLock
        tb_db = "sqlite3.OperationalError: database is locked"
        res_db = client._fallback_compact_traceback(tb_db)
        assert res_db["error_type"] == "DatabaseLock"

        # StateDrift
        tb_drift = "src.exceptions.InvariantViolation: ArchitectureFitnessError: state drift detected"
        res_drift = client._fallback_compact_traceback(tb_drift)
        assert res_drift["error_type"] == "StateDrift"

    def test_token_compression_ratio(self):
        client = LayaClient()
        # Simulated 500-line verbose traceback
        verbose_traceback = "\n".join([
            "DEBUG 2026-09-22 04:00:00 [pytest] Collecting test session...",
            "INFO Loading test runner configuration from pyproject.toml",
            "DEBUG Initializing db connection pool...",
            * [f"  File '/usr/lib/python3.13/site-packages/pytest/runner.py', line {i}, in run" for i in range(100, 200)],
            "  File 'tests/test_architecture_fitness.py', line 92, in test_context_budget",
            "    assert 540 < 500, 'INV-002: Context budget exceeded'",
            "AssertionError: INV-002: Context budget exceeded",
            * [f"DEBUG cleaning up thread {i}..." for i in range(50)]
        ])

        triage = client._fallback_compact_traceback(verbose_traceback)

        raw_char_count = len(verbose_traceback)
        capsule_token_est = triage["tokens_estimated"]

        # Raw log is > 6,000 chars (~1,500 tokens). Capsule must be < 30 tokens (>95% reduction).
        assert raw_char_count > 4000
        assert capsule_token_est <= 25
        assert triage["failed_invariant"] == "INV-002"
        assert triage["file"] == "tests/test_architecture_fitness.py"
        assert triage["line"] == 92

    def test_remote_triage_mock(self):
        client = LayaClient()
        mock_triage_payload = {
            "error_type": "AssertionError",
            "file": "tests/test_planar_solver.py",
            "line": 84,
            "failed_invariant": "INV-002",
            "summary": "Topology is non-planar",
            "capsule": "[ERROR_TRIAGE: Type=AssertionError, File=tests/test_planar_solver.py:84, FailedInvariant=INV-002, Summary='Topology is non-planar']",
            "tokens_estimated": 7
        }

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.read.return_value = json.dumps({
                "status": "ok",
                "triage": mock_triage_payload,
                "latency_ms": 14.5,
                "sub_40ms": True
            }).encode("utf-8")
            mock_urlopen.return_value.__enter__.return_value = mock_resp

            triage = client.compact_traceback("Some raw stack trace...")
            assert triage["fallback"] is False
            assert triage["error_type"] == "AssertionError"
            assert triage["capsule"].startswith("[ERROR_TRIAGE:")
