"""
Tests for Appwrite BaaS Control Plane Adapter & Realtime Phase Sync (ADR-011).
Validates Ed25519 signature checks, WORM ledger, SSE streaming, and phase transitions.
"""
import json
import time
import hashlib
import threading
import urllib.request
from pathlib import Path
import pytest

from src.adapters.appwrite_client import (
    AppwriteClient,
    ed25519_sign,
    ed25519_verify,
    _scalarmult,
    _B,
    _encode_point,
)
from src.server.workbench_server import (
    ThreadedHTTPServer,
    WorkbenchRequestHandler,
    SPRINT_PHASE_MANAGER,
)

TEST_PORT = 8773
ROOT_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def server():
    SPRINT_PHASE_MANAGER.reset()
    srv = ThreadedHTTPServer(("127.0.0.1", TEST_PORT), WorkbenchRequestHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)
    yield srv
    srv.shutdown()
    srv.server_close()
    SPRINT_PHASE_MANAGER.reset()


def test_ed25519_pure_stdlib_verification():
    """Verifies RFC 8032 Ed25519 signature creation and mathematical verification."""
    seed = hashlib.sha256(b"bsdd-head-architect-key-seed").digest()
    h = hashlib.sha512(seed).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 64
    pk = _encode_point(_scalarmult(_B, a))

    payload = b'{"action":"approve","sprint_id":"sprint-live"}'
    sig = ed25519_sign(seed, payload)

    assert len(sig) == 64
    assert len(pk) == 32
    assert ed25519_verify(pk, payload, sig) is True

    # Tampered payload fails verification
    tampered_payload = b'{"action":"reject","sprint_id":"sprint-live"}'
    assert ed25519_verify(pk, tampered_payload, sig) is False


def test_appwrite_client_record_and_ledger(tmp_path):
    """Verifies phase transition recording to local WORM ledger."""
    client = AppwriteClient(root_dir=tmp_path)
    res = client.record_phase_transition(
        sprint_id="sprint-test",
        from_phase="phi_5",
        to_phase="phi_6",
        operator_id="Operator 1",
        operator_signature="ed25519:test",
    )
    assert res["sprint_id"] == "sprint-test"
    assert res["to_phase"] == "phi_6"

    ledger_path = tmp_path / ".context" / "appwrite_cycles_ledger.json"
    assert ledger_path.exists()
    records = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert len(records) == 1
    assert records[0]["operator_id"] == "Operator 1"


def test_server_realtime_phase_sse(server):
    """Verifies GET /api/realtime/phases SSE connection and initial event."""
    url = f"http://127.0.0.1:{TEST_PORT}/api/realtime/phases"
    req = urllib.request.Request(url, headers={"Accept": "text/event-stream"})
    with urllib.request.urlopen(req, timeout=3.0) as resp:
        assert resp.status == 200
        assert "text/event-stream" in resp.headers.get("Content-Type", "")
        # Read initial event
        line1 = resp.readline().decode("utf-8")
        line2 = resp.readline().decode("utf-8")
        assert line1.startswith("data: ")
        data = json.loads(line1.replace("data: ", "").strip())
        assert data["event"] == "init"
        assert "current_phase" in data
        assert "phases" in data


def test_server_post_sprint_phase(server):
    """POST /api/sprint/phase updates phase and records in ledger."""
    url = f"http://127.0.0.1:{TEST_PORT}/api/sprint/phase"
    payload = json.dumps({"phase_id": "phi_5"}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["status"] == "updated"
        assert data["current_phase"] == "phi_5"


def test_server_sprint_review_with_ed25519_signature(server):
    """POST /api/sprint/review accepts and validates operator signature."""
    url = f"http://127.0.0.1:{TEST_PORT}/api/sprint/review"

    # Generate keypair
    seed = hashlib.sha256(b"operator-auth-seed").digest()
    h = hashlib.sha512(seed).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 64
    pk = _encode_point(_scalarmult(_B, a))

    canonical_msg = json.dumps({"action": "approve", "sprint_id": "sprint-live"}, sort_keys=True, separators=(",", ":")).encode("utf-8")
    sig = ed25519_sign(seed, canonical_msg)

    payload = json.dumps({
        "action": "approve",
        "operator_id": "Head Architect",
        "operator_signature": sig.hex(),
        "public_key": pk.hex(),
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["status"] == "approved"
        assert data["signature_verified"] is True
        assert data["next_phase"] == "phi_7"
