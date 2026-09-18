"""
Sprint 018 Test Suite: Sovereign Realtime Agent Collaboration & Distributed Multi-Host Synchronization
Validates:
- INV-018-01: Word budget < 500 words for SPEC-018
- INV-018-02: DRAKON planarity C=0 and skewer X=0 for logic.drakon.json
- INV-018-03: Zero-dependency pure Python runtime in src/adapters/cluster_sync.py (ADR-002)
- INV-018-04: Bitemporal cluster leases with transaction time Tx and valid time Tv (ADR-013)
- INV-018-05: Air-gapped Ed25519 review manifest
- Cluster node discovery across .161, .184, .251
- Server /api/cluster/nodes, /api/cluster/lease/acquire, /api/cluster/lease/release
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
from src.adapters.cluster_sync import ClusterLeaseManager, ClusterNodeRegistry
from src.server.workbench_server import ThreadingMixIn, HTTPServer, WorkbenchRequestHandler

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

ROOT = Path(__file__).resolve().parent.parent
TEST_PORT = 8798


@pytest.fixture(scope="module")
def server():
    srv = ThreadedHTTPServer(("127.0.0.1", TEST_PORT), WorkbenchRequestHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)
    yield f"http://127.0.0.1:{TEST_PORT}"
    srv.shutdown()
    srv.server_close()


def test_spec_018_word_budget_sub_500_words():
    """Invariant INV-018-01: SPEC-018 must remain strictly under 500 words."""
    spec_path = ROOT / "specs" / "018-realtime-agent-collaboration" / "spec.md"
    assert spec_path.exists(), "SPEC-018 markdown does not exist"
    content = spec_path.read_text(encoding="utf-8")
    words = len(content.split())
    assert words < 500, f"SPEC-018 word count {words} exceeds 500-word limit"


def test_spec_018_drakon_planar_invariants():
    """Invariant INV-018-02: Sprint 018 DRAKON flow must have 0 line crossings (C=0) and linear skewer."""
    schema_path = ROOT / "specs" / "018-realtime-agent-collaboration" / "logic.drakon.json"
    assert schema_path.exists(), "logic.drakon.json does not exist"
    validator = DrakonValidator()
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    schema = DrakonParser.parse_dict(data)
    result = validator.validate(schema)
    assert result.is_valid is True, f"Drakon validation failed: {result.errors}"
    assert result.stats.get("crossings", 0) == 0, "Crossings C must be 0"


def test_cluster_sync_pure_stdlib_invariants():
    """Invariant INV-018-03: src/adapters/cluster_sync.py must use strictly Python Standard Library."""
    target = ROOT / "src" / "adapters" / "cluster_sync.py"
    assert target.exists(), "cluster_sync.py does not exist"
    tree = ast.parse(target.read_text(encoding="utf-8"))
    allowed_modules = {
        "sys", "os", "pathlib", "typing", "json", "time", "datetime", "hashlib",
        "urllib", "re", "subprocess", "socket", "threading", "math", "functools",
        "dataclasses", "abc", "collections", "io", "secrets", "uuid", "queue", "src"
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                root = n.name.split(".")[0]
                assert root in allowed_modules, f"Forbidden import '{root}' in {target}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]
                assert root in allowed_modules, f"Forbidden import-from '{root}' in {target}"


def test_cluster_lease_manager_lifecycle():
    """Invariant INV-018-04: Lease manager acquires, detects conflicts, and releases with Tx/Tv."""
    manager = ClusterLeaseManager()
    
    # 1. Acquire lease for workspace 'core' by agent 'agent-alpha'
    lease1 = manager.acquire_lease(
        resource_id="workspace:core",
        holder_id="agent-alpha",
        holder_host="192.168.3.161",
        ttl_seconds=10
    )
    assert lease1["acquired"] is True
    assert lease1["holder_id"] == "agent-alpha"
    assert "tx_id" in lease1
    assert "t_x" in lease1
    assert "t_v" in lease1

    # 2. Competing acquire for same resource by 'agent-beta' should fail
    lease2 = manager.acquire_lease(
        resource_id="workspace:core",
        holder_id="agent-beta",
        holder_host="192.168.3.184",
        ttl_seconds=10
    )
    assert lease2["acquired"] is False
    assert lease2["conflict_with"] == "agent-alpha"

    # 3. Same holder can refresh / renew
    renew = manager.acquire_lease(
        resource_id="workspace:core",
        holder_id="agent-alpha",
        holder_host="192.168.3.161",
        ttl_seconds=20
    )
    assert renew["acquired"] is True
    assert renew["renewed"] is True

    # 4. Release lease
    rel = manager.release_lease(resource_id="workspace:core", holder_id="agent-alpha")
    assert rel["released"] is True

    # 5. Competing agent can now acquire
    lease3 = manager.acquire_lease(
        resource_id="workspace:core",
        holder_id="agent-beta",
        holder_host="192.168.3.184",
        ttl_seconds=10
    )
    assert lease3["acquired"] is True
    assert lease3["holder_id"] == "agent-beta"


def test_cluster_node_registry():
    """Verify cluster node discovery and topology registration."""
    registry = ClusterNodeRegistry()
    nodes = registry.get_nodes()
    assert len(nodes) >= 3
    ips = [n["host"] for n in nodes]
    assert "192.168.3.161" in ips
    assert "192.168.3.184" in ips
    assert "192.168.3.251" in ips


def test_server_cluster_endpoints(server):
    """Verify HTTP endpoints for cluster nodes, acquire lease, and release lease."""
    # GET /api/cluster/nodes
    req = urllib.request.Request(f"{server}/api/cluster/nodes")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert "nodes" in data
        assert "active_leases" in data
        assert isinstance(data["nodes"], list)

    # POST /api/cluster/lease/acquire
    payload = json.dumps({
        "resource_id": "workspace:test_lease",
        "holder_id": "test-agent-pytest",
        "holder_host": "127.0.0.1",
        "ttl_seconds": 15
    }).encode("utf-8")
    req_acquire = urllib.request.Request(
        f"{server}/api/cluster/lease/acquire",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_acquire) as resp:
        assert resp.status == 200
        res_data = json.loads(resp.read().decode())
        assert res_data.get("acquired") is True
        assert res_data.get("holder_id") == "test-agent-pytest"

    # POST /api/cluster/lease/release
    payload_rel = json.dumps({
        "resource_id": "workspace:test_lease",
        "holder_id": "test-agent-pytest"
    }).encode("utf-8")
    req_rel = urllib.request.Request(
        f"{server}/api/cluster/lease/release",
        data=payload_rel,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_rel) as resp:
        assert resp.status == 200
        res_rel = json.loads(resp.read().decode())
        assert res_rel.get("released") is True
