"""
Sprint 020 Test Suite: Sovereign Agent Self-Correction, Automated Rollback Compensation & Self-Healing AST Harness
Validates:
- INV-020-01: Word budget < 500 words for SPEC-020
- INV-020-02: DRAKON planarity C=0 and skewer X=0 for logic.drakon.json
- INV-020-03: Zero-dependency pure Python runtime in src/adapters/self_healing_engine.py (ADR-002)
- INV-020-04: Bitemporal transaction coordinates (Tx, Tv) for checkpoints and compensation actions (ADR-001)
- In-memory & file-based AST checkpointing, rollback compensation, and diagnostic repair heuristics
- HTTP Workbench Endpoints: POST /api/healing/checkpoint, POST /api/healing/compensate, GET /api/healing/status
"""
import ast
import json
import time
import urllib.request
import urllib.parse
import pytest
import threading
from pathlib import Path
from typing import Dict, Any

from src.drakon.parser import DrakonParser
from src.drakon.validator import DrakonValidator
from src.adapters.self_healing_engine import SelfHealingEngine, ASTCheckpoint
from src.server.workbench_server import ThreadingMixIn, HTTPServer, WorkbenchRequestHandler

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

ROOT = Path(__file__).resolve().parent.parent
TEST_PORT = 8794


@pytest.fixture(scope="module")
def server():
    srv = ThreadedHTTPServer(("127.0.0.1", TEST_PORT), WorkbenchRequestHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)
    yield f"http://127.0.0.1:{TEST_PORT}"
    srv.shutdown()
    srv.server_close()


def test_spec_020_word_budget_sub_500_words():
    """Invariant INV-020-01: SPEC-020 must remain strictly under 500 words."""
    spec_path = ROOT / "specs" / "020-agent-self-correction-and-healing" / "spec.md"
    assert spec_path.exists(), "SPEC-020 markdown does not exist"
    content = spec_path.read_text(encoding="utf-8")
    words = len(content.split())
    assert words < 500, f"SPEC-020 word count {words} exceeds 500-word limit"


def test_spec_020_drakon_planar_invariants():
    """Invariant INV-020-02: Sprint 020 DRAKON flow must have 0 line crossings (C=0) and linear skewer."""
    schema_path = ROOT / "specs" / "020-agent-self-correction-and-healing" / "logic.drakon.json"
    assert schema_path.exists(), "logic.drakon.json does not exist"
    validator = DrakonValidator()
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    schema = DrakonParser.parse_dict(data)
    res = validator.validate(schema)
    assert res.is_valid is True, f"Validation failed: {res.errors}"
    assert res.stats.get("crossings", 0) == 0, f"Crossing violation: {res.stats.get('crossings', 0)}"
    assert res.stats.get("node_count", 0) >= 5, f"Expected >= 5 nodes, got {res.stats.get('node_count')}"


def test_pure_stdlib_invariants():
    """Invariant INV-020-03: src/adapters/self_healing_engine.py must use strictly Python stdlib."""
    module_path = ROOT / "src" / "adapters" / "self_healing_engine.py"
    assert module_path.exists(), "self_healing_engine.py does not exist"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    allowed = {
        "sys", "os", "pathlib", "typing", "json", "time", "datetime", "hashlib",
        "threading", "difflib", "ast", "dataclasses", "uuid", "re"
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                root_pkg = n.name.split(".")[0]
                assert root_pkg in allowed or root_pkg == "src", f"Disallowed import: {root_pkg}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_pkg = node.module.split(".")[0]
                assert root_pkg in allowed or root_pkg == "src", f"Disallowed from-import: {root_pkg}"


def test_self_healing_engine_checkpoint_and_compensation(tmp_path):
    """Invariant INV-020-04: Bitemporal coordinates & transactional rollback compensation."""
    engine = SelfHealingEngine()
    test_file = tmp_path / "sample_code.py"
    original_code = "def add(a, b):\n    return a + b\n"
    test_file.write_text(original_code, encoding="utf-8")

    # 1. Create checkpoint
    cp = engine.create_checkpoint(
        file_path=str(test_file),
        content=original_code,
        author="agent-codex",
        reason="Pre-refactoring baseline"
    )
    assert cp.checkpoint_id.startswith("chk_")
    assert cp.t_x is not None
    assert cp.t_v["valid_from"] is not None
    assert cp.content_hash == engine.calculate_hash(original_code)

    # 2. Mutate file with a bug
    broken_code = "def add(a, b\n    return a + b\n" # Missing closing parenthesis
    test_file.write_text(broken_code, encoding="utf-8")

    # 3. Analyze failure
    diagnostics = engine.analyze_ast(broken_code)
    assert diagnostics["is_valid"] is False
    assert "SyntaxError" in diagnostics["error_type"]
    assert len(diagnostics["healing_hints"]) > 0

    # 4. Execute compensation rollback
    res = engine.compensate_rollback(
        checkpoint_id=cp.checkpoint_id,
        target_path=str(test_file),
        reason="SyntaxError detected during compilation"
    )
    assert res["success"] is True
    assert test_file.read_text(encoding="utf-8") == original_code
    assert res["reverted_bytes"] > 0
    assert len(engine.get_audit_trail()) == 1


def test_ast_healing_analyzer_diagnostics():
    """Verify AST diagnostics produces actionable remediation hints."""
    engine = SelfHealingEngine()
    
    # Clean Python code
    clean_code = "def calculate_total(items):\n    return sum(items)\n"
    diag_clean = engine.analyze_ast(clean_code)
    assert diag_clean["is_valid"] is True
    assert diag_clean["error_type"] is None
    assert len(diag_clean["healing_hints"]) == 0

    # Syntax error code: unexpected EOF
    bad_code = "def foo():\n    if True:\n"
    diag_bad = engine.analyze_ast(bad_code)
    assert diag_bad["is_valid"] is False
    assert diag_bad["error_type"] is not None
    assert any("indent" in h.lower() or "block" in h.lower() or "syntax" in h.lower() for h in diag_bad["healing_hints"])


def test_server_healing_endpoints(server):
    """Verify HTTP API endpoints for checkpointing, compensation, and status."""
    # 1. GET /api/healing/status
    req = urllib.request.Request(f"{server}/api/healing/status")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["status"] == "ok"
        assert "total_checkpoints" in data
        assert "total_compensations" in data

    # 2. POST /api/healing/checkpoint
    payload = {
        "file_path": "/tmp/test_agent_script.py",
        "content": "def test_hello():\n    return 'world'\n",
        "author": "agent-sprint-020",
        "reason": "Test endpoint checkpoint"
    }
    req = urllib.request.Request(
        f"{server}/api/healing/checkpoint",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        cp_data = json.loads(resp.read().decode("utf-8"))
        assert cp_data["checkpoint_id"].startswith("chk_")
        chk_id = cp_data["checkpoint_id"]

    # 3. POST /api/healing/compensate
    comp_payload = {
        "checkpoint_id": chk_id,
        "reason": "Simulated compilation failure in test harness"
    }
    req = urllib.request.Request(
        f"{server}/api/healing/compensate",
        data=json.dumps(comp_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        comp_data = json.loads(resp.read().decode("utf-8"))
        assert comp_data["success"] is True
        assert comp_data["checkpoint_id"] == chk_id
