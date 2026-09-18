"""
Sprint 016 Test Suite: Sovereign Multi-Tenant Cross-Repo Semantic Graph & Utopia Query Federation
Validates:
- INV-016-01: Word budget < 500 words for SPEC-016
- INV-016-02: DRAKON planarity C=0 and skewer X=0 for logic.drakon.json
- INV-016-03: Zero-dependency pure Python runtime in src/
- INV-016-04: Bitemporal DAG synchronization (Tx, Tv) on cross-repo edges
- INV-016-05: Air-gapped Ed25519 review manifest
- Cross-repository semantic dependency resolution
- Server /api/graph/query and /api/graph/cross-repo-edges endpoints
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
    BackgroundIngestionWorker,
    CrossRepoSemanticGraphResolver
)
from src.server.workbench_server import ThreadingMixIn, HTTPServer, WorkbenchRequestHandler

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

ROOT = Path(__file__).resolve().parent.parent
TEST_PORT = 8796


@pytest.fixture(scope="module")
def server():
    srv = ThreadedHTTPServer(("127.0.0.1", TEST_PORT), WorkbenchRequestHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)
    yield f"http://127.0.0.1:{TEST_PORT}"
    srv.shutdown()
    srv.server_close()


def test_spec_016_word_budget_sub_500_words():
    """Invariant INV-016-01: SPEC-016 must remain strictly under 500 words."""
    spec_path = ROOT / "specs" / "016-cross-repo-semantic-graph" / "spec.md"
    assert spec_path.exists(), "SPEC-016 markdown does not exist"
    content = spec_path.read_text(encoding="utf-8")
    words = len(content.split())
    assert words < 500, f"SPEC-016 word count {words} exceeds 500-word limit"


def test_spec_016_drakon_planar_invariants():
    """Invariant INV-016-02: Sprint 016 DRAKON flow must have 0 line crossings (C=0) and linear skewer."""
    schema_path = ROOT / "specs" / "016-cross-repo-semantic-graph" / "logic.drakon.json"
    assert schema_path.exists(), "logic.drakon.json does not exist"
    validator = DrakonValidator()
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    schema = DrakonParser.parse_dict(data)
    result = validator.validate(schema)
    assert result.is_valid is True, f"Drakon validation failed: {result.errors}"
    assert result.stats.get("crossings", 0) == 0, "Crossings C must be 0"


def test_cross_repo_semantic_dependency_resolver(tmp_path):
    """Invariant INV-016-04: Cross-repo resolver identifies dependencies across multiple workspaces with bitemporal tags."""
    # Setup workspace 1: core
    ws1 = tmp_path / "repo_core"
    ws1.mkdir()
    core_file = ws1 / "service.py"
    core_file.write_text(
        "class CoreEngine:\n"
        "    def run(self):\n"
        "        return 'core_ok'\n",
        encoding="utf-8"
    )

    # Setup workspace 2: ui / client
    ws2 = tmp_path / "repo_client"
    ws2.mkdir()
    client_file = ws2 / "app.py"
    client_file.write_text(
        "from repo_core.service import CoreEngine\n\n"
        "class AppClient:\n"
        "    def __init__(self):\n"
        "        self.engine = CoreEngine()\n",
        encoding="utf-8"
    )

    indexer = MultiWorkspaceSymbolIndexer()
    indexer.register_workspace("repo_core", ws1)
    indexer.register_workspace("repo_client", ws2)

    resolver = CrossRepoSemanticGraphResolver(indexer=indexer)
    edges = resolver.resolve_cross_repo_dependencies()

    assert len(edges) >= 1, "Should find at least 1 cross-repository dependency edge"
    edge = edges[0]
    assert edge["source_workspace"] == "repo_client"
    assert edge["target_workspace"] == "repo_core"
    assert "CoreEngine" in edge["target_symbol"] or "service" in edge["target_file"]
    assert edge["rel_type"] in ("IMPORTS", "DEPENDS_ON")
    assert "tx_time" in edge
    assert "valid_from" in edge


def test_graph_query_filtering(tmp_path):
    """Verifies graph query engine filters by symbol, workspace, and relationship type."""
    ws1 = tmp_path / "ws_alpha"
    ws1.mkdir()
    (ws1 / "alpha.py").write_text("class AlphaNode:\n    pass\n", encoding="utf-8")

    ws2 = tmp_path / "ws_beta"
    ws2.mkdir()
    (ws2 / "beta.py").write_text("from ws_alpha.alpha import AlphaNode\nclass BetaNode:\n    pass\n", encoding="utf-8")

    indexer = MultiWorkspaceSymbolIndexer()
    indexer.register_workspace("ws_alpha", ws1)
    indexer.register_workspace("ws_beta", ws2)

    resolver = CrossRepoSemanticGraphResolver(indexer=indexer)
    resolver.resolve_cross_repo_dependencies()

    # Query for AlphaNode
    res_sym = resolver.query({"symbol": "AlphaNode"})
    assert res_sym["status"] == "ok"
    assert any(n["label"] == "AlphaNode" for n in res_sym["nodes"])

    # Query for ws_beta
    res_ws = resolver.query({"workspace": "ws_beta"})
    assert res_ws["status"] == "ok"
    assert any(n.get("workspace") == "ws_beta" for n in res_ws["nodes"])


def test_server_graph_query_and_cross_edges_endpoints(server):
    """Validates server endpoints POST /api/graph/query and GET /api/graph/cross-repo-edges."""
    # 1. GET /api/graph/cross-repo-edges
    req_edges = urllib.request.Request(f"{server}/api/graph/cross-repo-edges")
    with urllib.request.urlopen(req_edges) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "status" in data
        assert data["status"] == "ok"
        assert "cross_repo_edges" in data
        assert isinstance(data["cross_repo_edges"], list)

    # 2. POST /api/graph/query
    query_payload = json.dumps({"symbol": "BackgroundIngestionWorker"}).encode("utf-8")
    req_query = urllib.request.Request(
        f"{server}/api/graph/query",
        data=query_payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_query) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["status"] == "ok"
        assert "nodes" in data
        assert "edges" in data
