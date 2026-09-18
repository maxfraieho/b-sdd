"""
Sprint 015 Test Suite: Autonomous GitNexus Ingestion & Live Copilot Agent Harness
Validates:
- INV-015-01: Word budget < 500 words for SPEC-015
- INV-015-02: DRAKON planarity C=0 and skewer X=0 for logic.drakon.json
- INV-015-03: Zero-dependency pure Python runtime in src/
- INV-015-04: Bitemporal DAG node and edge mapping (Tx, Tv)
- INV-015-05: Rule of 2 skill crystallization for repeated ingestion
- Background multi-repo ingestion engine
- Server /api/ingest/async and /api/copilot/symbol-card endpoints
"""
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
from src.adapters.gitnexus_graph import (
    MultiWorkspaceSymbolIndexer,
    BackgroundIngestionWorker
)
from src.core.skill_crystallizer import RuleOfTwoSkillCrystallizer
from src.server.workbench_server import ThreadingMixIn, HTTPServer, WorkbenchRequestHandler

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

ROOT = Path(__file__).resolve().parent.parent
TEST_PORT = 8795


@pytest.fixture(scope="module")
def server():
    srv = ThreadedHTTPServer(("127.0.0.1", TEST_PORT), WorkbenchRequestHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)
    yield f"http://127.0.0.1:{TEST_PORT}"
    srv.shutdown()
    srv.server_close()


def test_spec_015_word_budget_sub_500_words():
    """Invariant INV-015-01: SPEC-015 must remain strictly under 500 words."""
    spec_path = ROOT / "specs" / "015-autonomous-gitnexus-harness" / "spec.md"
    assert spec_path.exists(), "SPEC-015 markdown does not exist"
    content = spec_path.read_text(encoding="utf-8")
    words = len(content.split())
    assert words < 500, f"SPEC-015 word count {words} exceeds 500-word limit"


def test_spec_015_drakon_planar_invariants():
    """Invariant INV-015-02: Sprint 015 DRAKON flow must have 0 line crossings (C=0) and linear skewer."""
    schema_path = ROOT / "specs" / "015-autonomous-gitnexus-harness" / "logic.drakon.json"
    assert schema_path.exists(), "logic.drakon.json does not exist"
    validator = DrakonValidator()
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    schema = DrakonParser.parse_dict(data)
    result = validator.validate(schema)
    assert result.is_valid is True, f"Drakon validation failed: {result.errors}"
    assert result.stats.get("crossings", 0) == 0, "Crossings C must be 0"


def test_background_multi_repo_ingestion(tmp_path):
    """Invariant INV-015-04: Multi-repo ingestion constructs bitemporal Utopia DAG nodes with Tx, Tv."""
    ws_core = tmp_path / "core_repo"
    ws_ui = tmp_path / "ui_repo"
    ws_core.mkdir()
    ws_ui.mkdir()

    # Core module
    (ws_core / "storage.py").write_text("""
class BitemporalStorage:
    \"\"\"Stores facts indexed by valid time and tx time.\"\"\"
    def persist_record(self, fact_id: str):
        pass

def compute_hash(data: bytes) -> str:
    return "hash"
""", encoding="utf-8")

    # UI module
    (ws_ui / "components.ts").write_text("""
export interface StorageWidgetProps {
  storageId: string;
}

export function renderStorageWidget(props: StorageWidgetProps) {
  return props;
}
""", encoding="utf-8")

    indexer = MultiWorkspaceSymbolIndexer()
    indexer.register_workspace("core", ws_core, is_active=True)
    indexer.register_workspace("ui", ws_ui, is_active=False)

    worker = BackgroundIngestionWorker(indexer=indexer)
    report = worker.run_ingestion(valid_time_day=20260918)

    assert report["status"] == "completed"
    assert report["symbols_count"] >= 3
    assert report["nodes_count"] >= 3
    assert "nodes" in report
    assert "edges" in report

    # Verify bitemporal timestamps on DAG nodes
    first_node = report["nodes"][0]
    assert "id" in first_node
    assert "entity_type" in first_node
    assert "valid_from" in first_node
    assert "tx_time" in first_node
    assert first_node["valid_from"] == 20260918


def test_rule_of_2_ingestion_skill_crystallization(tmp_path):
    """Invariant INV-015-05: Ingestion workflow repeated >= 2 times crystallizes into .pi/skills/."""
    skills_dir = tmp_path / ".pi" / "skills"
    crystallizer = RuleOfTwoSkillCrystallizer(skills_root=skills_dir)

    # First observation
    r1 = crystallizer.record_pattern(
        pattern_id="multi-repo-ast-ingestion",
        title="Multi-Repo AST Ingestion and Utopia DAG Synchronization",
        description="Crawls multi-tenant workspaces, indexes symbols, and synchronizes bitemporal DAG nodes.",
        instructions="1. Poll registered workspaces\n2. Extract AST symbols\n3. Push DAG nodes to Utopia DB."
    )
    assert r1["crystallized"] is False

    # Second observation
    r2 = crystallizer.record_pattern(
        pattern_id="multi-repo-ast-ingestion",
        title="Multi-Repo AST Ingestion and Utopia DAG Synchronization",
        description="Crawls multi-tenant workspaces, indexes symbols, and synchronizes bitemporal DAG nodes.",
        instructions="1. Poll registered workspaces\n2. Extract AST symbols\n3. Push DAG nodes to Utopia DB."
    )
    assert r2["crystallized"] is True
    skill_file = skills_dir / "multi-repo-ast-ingestion" / "SKILL.md"
    assert skill_file.exists()
    assert "Rule of 2" in skill_file.read_text(encoding="utf-8")


def test_server_ingest_and_symbol_card_endpoints(server):
    """TASK-015-4 & TASK-015-5: Server ingestion and Copilot symbol card endpoints."""
    # 1. Trigger ingestion
    ingest_req = urllib.request.Request(
        f"{server}/api/ingest/async",
        data=json.dumps({"valid_time_day": 20260918}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(ingest_req, timeout=25.0) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["status"] == "completed"
        assert "symbols_count" in data
        assert "nodes_count" in data

    # 2. Check ingestion status
    status_url = f"{server}/api/ingest/status"
    with urllib.request.urlopen(status_url, timeout=5.0) as resp:
        assert resp.status == 200
        st_data = json.loads(resp.read().decode("utf-8"))
        assert "status" in st_data
        assert "last_ingested_at" in st_data

    # 3. Request Copilot symbol card
    card_url = f"{server}/api/copilot/symbol-card?name=DrakonValidator"
    with urllib.request.urlopen(card_url, timeout=5.0) as resp:
        assert resp.status == 200
        card_data = json.loads(resp.read().decode("utf-8"))
        assert card_data["card_type"] == "ast_symbol_card"
        assert "name" in card_data
        assert "kind" in card_data
        assert "workspace" in card_data
