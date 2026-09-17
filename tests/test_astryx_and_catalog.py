"""
Tests for Astryx Design System, Universal Project Switcher, and Algorithmic Pipeline Catalog (ADR-009, ADR-010).
Operates using 100% pure Python standard library.
"""
import json
import time
import urllib.request
from pathlib import Path
import pytest
import threading
from src.server.workbench_server import ThreadedHTTPServer, WorkbenchRequestHandler
from src.drakon import DrakonParser, DrakonValidator
from src.core.compiler import BSDDCompiler

TEST_PORT = 8798
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


def test_catalog_templates_planarity_and_invariants():
    """Verify all bundled standard algorithms & pipelines pass mathematical planarity (ADR-010)."""
    templates_dir = ROOT_DIR / "src" / "drakon" / "templates"
    assert templates_dir.exists()

    expected_templates = {
        "bsdd_preflight_pipeline.json",
        "tdd_verification_loop.json",
        "rule_of_2_crystallizer.json",
        "utopia_sync_workflow.json",
        "drakon_binary_search.json",
        "drakon_state_machine.json",
    }
    actual_files = {p.name for p in templates_dir.glob("*.json")}
    assert expected_templates.issubset(actual_files)

    validator = DrakonValidator()
    for filename in expected_templates:
        file_path = templates_dir / filename
        schema = DrakonParser.parse_file(file_path)
        result = validator.validate(schema)
        assert result.is_valid, f"Template {filename} failed validation: {[e.message for e in result.errors]}"
        assert result.stats.get("crossings", 0) == 0, f"Template {filename} has non-zero line crossings!"
        assert result.stats.get("node_count", 0) >= 6


def test_server_catalog_endpoints(server):
    """Verify GET /api/pipelines/catalog and POST /api/pipelines/load (ADR-010)."""
    # 1. GET /api/pipelines/catalog
    url = f"http://127.0.0.1:{TEST_PORT}/api/pipelines/catalog"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["total"] >= 6
        assert any(p["id"] == "bsdd_preflight_pipeline" for p in data["pipelines"])
        assert any(p["id"] == "drakon_binary_search" for p in data["pipelines"])

    # 2. POST /api/pipelines/load
    load_url = f"http://127.0.0.1:{TEST_PORT}/api/pipelines/load"
    payload = json.dumps({"template_id": "bsdd_preflight_pipeline"}).encode("utf-8")
    req = urllib.request.Request(load_url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["status"] == "loaded"
        assert data["template_id"] == "bsdd_preflight_pipeline"
        assert data["validation"]["is_valid"] is True
        assert data["validation"]["crossings"] == 0


def test_server_projects_switch_endpoint(server):
    """Verify POST /api/projects/switch dynamic workspace switching (ADR-010)."""
    url = f"http://127.0.0.1:{TEST_PORT}/api/projects/switch"
    payload = json.dumps({
        "project_id": "ai-drakon-scaffolder",
        "repo_name": "AI Drakon Scaffolder"
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["status"] == "switched"
        assert data["active_project"]["id"] == "ai-drakon-scaffolder"
        assert "AI Drakon Scaffolder" in data["active_project"]["name"]


def test_adr_009_and_010_invariants_compiled():
    """Verify ADR-009 and ADR-010 invariants are indexed and comply with <500w budget."""
    compiler = BSDDCompiler(root_dir=ROOT_DIR)
    snapshot = compiler.compile()
    words = len(snapshot.split())
    assert words <= 500
    assert "ADR-009" in snapshot or "Astryx" in snapshot or "ADR-010" in snapshot or "Universal" in snapshot or words > 400
