"""
Tests for Live GitHub API Sync Adapter & Endpoints (ADR-011).
Validates pure stdlib compliance, disk cache persistence, and offline fallback.
"""
import json
import time
import threading
import urllib.request
from pathlib import Path
import pytest

from src.adapters.github_sync import GitHubSyncAdapter
from src.server.workbench_server import ThreadedHTTPServer, WorkbenchRequestHandler

TEST_PORT = 8772
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


def test_github_adapter_fallback_and_cache(tmp_path):
    """Verifies that GitHubSyncAdapter writes and reads cache properly."""
    adapter = GitHubSyncAdapter(root_dir=tmp_path, account="maxfraieho")
    res = adapter.fetch_user_repositories(force_refresh=False)
    assert "repositories" in res
    assert res["total"] > 0
    assert (tmp_path / ".context" / "github_cache.json").exists()

    cached = adapter.get_cached_repositories()
    assert cached is not None
    assert cached["account"] == "maxfraieho"

    # Test offline fallback behavior when request fails
    fallback_adapter = GitHubSyncAdapter(root_dir=tmp_path, account="nonexistent-account-404-error")
    fallback_res = fallback_adapter.fetch_user_repositories(force_refresh=True)
    assert fallback_res["offline_parity"] is True
    assert fallback_res["total"] > 0


def test_github_adapter_live_sync():
    """Verifies live or cached repository fetching for maxfraieho."""
    adapter = GitHubSyncAdapter(root_dir=ROOT_DIR, account="maxfraieho")
    res = adapter.fetch_user_repositories()
    assert res["connected"] is True or res["offline_parity"] is True
    assert len(res["repositories"]) > 0
    names = [r["name"] for r in res["repositories"]]
    assert "b-sdd" in names


def test_server_github_repos_endpoint(server):
    """GET /api/github/repos endpoint verification."""
    url = f"http://127.0.0.1:{TEST_PORT}/api/github/repos"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "repositories" in data
        assert data["total"] > 0
        assert any(r["name"] == "b-sdd" for r in data["repositories"])


def test_server_github_sync_endpoint(server):
    """POST /api/github/sync endpoint verification."""
    url = f"http://127.0.0.1:{TEST_PORT}/api/github/sync"
    payload = json.dumps({"username": "maxfraieho"}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["status"] == "synced"
        assert "repositories" in data
        assert data["total"] > 0


def test_server_projects_includes_live_github_metadata(server):
    """GET /api/projects includes live-synced GitHub repositories."""
    url = f"http://127.0.0.1:{TEST_PORT}/api/projects"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "github" in data
        gh = data["github"]
        assert gh["account"] == "maxfraieho"
        assert "repositories" in gh
        assert len(gh["repositories"]) > 0
        active_repo = next((r for r in gh["repositories"] if r.get("is_active")), None)
        assert active_repo is not None
        assert active_repo["name"] == "b-sdd"
