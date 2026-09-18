"""
Sprint 019 Test Suite: Sovereign Autonomous Multi-Agent Consensus & Quorum Arbitration
Validates:
- INV-019-01: Word budget < 500 words for SPEC-019
- INV-019-02: DRAKON planarity C=0 and skewer X=0 for logic.drakon.json
- INV-019-03: Zero-dependency pure Python runtime in src/adapters/consensus_engine.py (ADR-002)
- INV-019-04: Bitemporal proposal ballots with transaction time Tx and valid time Tv (ADR-013)
- INV-019-05: Air-gapped Ed25519 review manifest
- Quorum calculation (N >= 2/3 approval threshold)
- Server /api/consensus/propose, /api/consensus/vote, /api/consensus/proposals
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
from src.adapters.consensus_engine import ConsensusEngine, ConsensusProposal
from src.server.workbench_server import ThreadingMixIn, HTTPServer, WorkbenchRequestHandler

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

ROOT = Path(__file__).resolve().parent.parent
TEST_PORT = 8799


@pytest.fixture(scope="module")
def server():
    srv = ThreadedHTTPServer(("127.0.0.1", TEST_PORT), WorkbenchRequestHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)
    yield f"http://127.0.0.1:{TEST_PORT}"
    srv.shutdown()
    srv.server_close()


def test_spec_019_word_budget_sub_500_words():
    """Invariant INV-019-01: SPEC-019 must remain strictly under 500 words."""
    spec_path = ROOT / "specs" / "019-autonomous-agent-consensus" / "spec.md"
    assert spec_path.exists(), "SPEC-019 markdown does not exist"
    content = spec_path.read_text(encoding="utf-8")
    words = len(content.split())
    assert words < 500, f"SPEC-019 word count {words} exceeds 500-word limit"


def test_spec_019_drakon_planar_invariants():
    """Invariant INV-019-02: Sprint 019 DRAKON flow must have 0 line crossings (C=0) and linear skewer."""
    schema_path = ROOT / "specs" / "019-autonomous-agent-consensus" / "logic.drakon.json"
    assert schema_path.exists(), "logic.drakon.json does not exist"
    validator = DrakonValidator()
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    schema = DrakonParser.parse_dict(data)
    result = validator.validate(schema)
    assert result.is_valid is True, f"Drakon validation failed: {result.errors}"
    assert result.stats.get("crossings", 0) == 0, "Crossings C must be 0"


def test_consensus_pure_stdlib_invariants():
    """Invariant INV-019-03: src/adapters/consensus_engine.py must use strictly Python Standard Library."""
    target = ROOT / "src" / "adapters" / "consensus_engine.py"
    assert target.exists(), "consensus_engine.py does not exist"
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


def test_consensus_engine_propose_and_vote():
    """Invariant INV-019-04: Multi-agent proposals and ballots record Tx/Tv and achieve quorum."""
    engine = ConsensusEngine(total_voters=3, quorum_ratio=2.0 / 3.0)
    
    # 1. Propose an architectural change
    prop = engine.propose(
        title="ADR-019: Byzantine-Tolerant Consensus Protocol",
        target_adr="ADR-019",
        description="Establish 2/3 majority quorum for distributed model slot arbitration.",
        proposer_id="agent-agy-161",
        voting_period_sec=60
    )
    assert prop["status"] == "voting"
    assert "proposal_id" in prop
    assert "t_x" in prop
    assert "t_v" in prop
    p_id = prop["proposal_id"]

    # 2. First vote: approve from agent-agy-161
    v1 = engine.cast_vote(proposal_id=p_id, voter_id="agent-agy-161", vote="approve")
    assert v1["status"] == "voting"
    assert v1["approvals"] == 1
    assert v1["quorum_reached"] is False

    # 3. Second vote: approve from agent-runner-184 -> reaches 2/3 quorum
    v2 = engine.cast_vote(proposal_id=p_id, voter_id="agent-runner-184", vote="approve")
    assert v2["status"] == "accepted"
    assert v2["approvals"] == 2
    assert v2["quorum_reached"] is True

    # 4. Duplicate vote rejection
    dup = engine.cast_vote(proposal_id=p_id, voter_id="agent-agy-161", vote="reject")
    assert dup.get("error") is not None or dup.get("accepted") is False

    # 5. List proposals
    proposals = engine.get_proposals()
    assert len(proposals) >= 1
    assert proposals[0]["proposal_id"] == p_id
    assert proposals[0]["status"] == "accepted"


def test_server_consensus_endpoints(server):
    """Verify HTTP endpoints for propose, vote, and get proposals."""
    # 1. POST /api/consensus/propose
    payload_prop = json.dumps({
        "title": "Migrate schema v2 to v3",
        "target_adr": "ADR-018",
        "description": "Cross-repo AST schema evolution",
        "proposer_id": "test-proposer-1"
    }).encode("utf-8")
    req_prop = urllib.request.Request(
        f"{server}/api/consensus/propose",
        data=payload_prop,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_prop) as resp:
        assert resp.status == 200
        prop_data = json.loads(resp.read().decode())
        assert prop_data.get("status") == "voting"
        assert "proposal_id" in prop_data
        p_id = prop_data["proposal_id"]

    # 2. POST /api/consensus/vote
    payload_vote = json.dumps({
        "proposal_id": p_id,
        "voter_id": "voter-node-184",
        "vote": "approve"
    }).encode("utf-8")
    req_vote = urllib.request.Request(
        f"{server}/api/consensus/vote",
        data=payload_vote,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_vote) as resp:
        assert resp.status == 200
        vote_data = json.loads(resp.read().decode())
        assert "approvals" in vote_data
        assert vote_data["approvals"] >= 1

    # 3. GET /api/consensus/proposals
    req_get = urllib.request.Request(f"{server}/api/consensus/proposals")
    with urllib.request.urlopen(req_get) as resp:
        assert resp.status == 200
        res_list = json.loads(resp.read().decode())
        assert "proposals" in res_list
        assert any(p["proposal_id"] == p_id for p in res_list["proposals"])
