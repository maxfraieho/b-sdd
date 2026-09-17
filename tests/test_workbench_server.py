"""
Tests for B-SDD Workbench Server REST/SSE Gateway.
Validates all endpoints exposed to `b-sdd-ui`.
100% Pure Python Standard Library.
"""
import json
import time
import threading
import urllib.request
from pathlib import Path
import pytest

from src.server.workbench_server import ThreadedHTTPServer, WorkbenchRequestHandler

TEST_PORT = 8769
ROOT_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def server():
    srv = ThreadedHTTPServer(("127.0.0.1", TEST_PORT), WorkbenchRequestHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)
    yield srv
    srv.shutdown()
    srv.server_close()


def test_server_health_endpoint(server):
    url = f"http://127.0.0.1:{TEST_PORT}/api/health"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["status"] == "healthy"
        assert "nodes" in data
        assert "utopia_db" in data["nodes"]
        assert "llm_gateway" in data["nodes"]


def test_server_rules_active_endpoint(server):
    url = f"http://127.0.0.1:{TEST_PORT}/api/rules/active"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["word_count"] <= 500
        assert data["is_budget_exceeded"] is False
        assert "compiled_snapshot" in data
        assert len(data["recommended_skills"]) > 0


def test_server_adrs_endpoint(server):
    url = f"http://127.0.0.1:{TEST_PORT}/api/adrs"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["total"] > 0
        assert len(data["adrs"]) > 0


def test_server_drakon_schema_endpoint(server):
    url = f"http://127.0.0.1:{TEST_PORT}/api/drakon/schema"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "schema_ir" in data
        assert "diagram" in data
        assert "items" in data["diagram"]
        assert data["validation"]["is_valid"] is True


def test_server_sprint_state_endpoint(server):
    url = f"http://127.0.0.1:{TEST_PORT}/api/sprint/state"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["current_phase"] == "phi_6"
        assert data["fitness_summary"]["total"] == 25


def test_server_sprint_review_reject_protocol(server):
    url = f"http://127.0.0.1:{TEST_PORT}/api/sprint/review"
    payload = json.dumps({
        "action": "reject",
        "rollback_depth": 1,
        "negative_invariants": ["ADR-008-INV-03: Simulation test reject"]
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["status"] == "rejected_and_branched"
        assert "ADR-008-INV-03" in data["delta_c"][0]


def test_server_projects_endpoint(server):
    url = f"http://127.0.0.1:{TEST_PORT}/api/projects"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "current_project" in data
        assert data["current_project"]["branch"] is not None
        assert len(data["workspaces"]) > 0


def test_server_specs_endpoint(server):
    url = f"http://127.0.0.1:{TEST_PORT}/api/specs"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["total"] >= 4
        assert any(s["id"] == "004-multi-session-handoff-and-drakon" for s in data["specs"])
        spec004 = next(s for s in data["specs"] if s["id"] == "004-multi-session-handoff-and-drakon")
        assert len(spec004["tasks"]) == 8


def test_server_adrs_full_content(server):
    url = f"http://127.0.0.1:{TEST_PORT}/api/adrs"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["total"] > 0
        first_adr = data["adrs"][0]
        assert "content" in first_adr
        assert len(first_adr["content"]) > 50


def test_server_adr_save_endpoint(server, tmp_path):
    url = f"http://127.0.0.1:{TEST_PORT}/api/adrs/save"
    # Read existing ADR-001 content to preserve it
    adr_path = ROOT_DIR / "docs" / "adr" / "ADR-001-bitemporal-intent-graph.md"
    orig_content = adr_path.read_text(encoding="utf-8")

    payload = json.dumps({
        "id": "ADR-001",
        "file_path": "docs/adr/ADR-001-bitemporal-intent-graph.md",
        "content": orig_content + "\n<!-- test save -->\n"
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode("utf-8"))
            assert data["success"] is True
            assert "saved_at" in data
    finally:
        # Restore original content
        adr_path.write_text(orig_content, encoding="utf-8")


def test_server_utopia_sync_endpoint(server):
    url = f"http://127.0.0.1:{TEST_PORT}/api/sync/utopia"
    payload = json.dumps({}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert "synced_at" in data
    except urllib.error.HTTPError as e:
        # If Utopia node is temporarily unreachable, 503 is returned with error
        data = json.loads(e.read().decode("utf-8"))
        assert "synced_at" in data


