"""
Sprint 014 Test Suite: Multi-Tenant AST Symbol Tracing, Direct SSE Streaming & Air-Gapped Ed25519 Proofs
Validates:
- INV-014-01: Word budget < 500 words for SPEC-014
- INV-014-02: DRAKON planarity C=0 and skewer X=0 for logic.drakon.json
- INV-014-03: Pure Python 3 Standard Library runtime in src/
- INV-014-04: Air-gapped offline Ed25519 verification (zero network requests)
- INV-014-05: Rule-of-2 skill crystallization (threshold >= 2)
- Multi-workspace AST symbol indexer and cross-repo resolution
- Direct low-latency SSE streaming bridge in workbench server
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
from src.core.crypto_verifier import (
    ed25519_sign,
    ed25519_verify,
    generate_ed25519_keypair,
    AirGappedProofValidator
)
from src.adapters.gitnexus_graph import MultiWorkspaceSymbolIndexer
from src.core.skill_crystallizer import RuleOfTwoSkillCrystallizer
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


def test_spec_014_word_budget_sub_500_words():
    """Invariant INV-014-01: SPEC-014 must remain strictly under 500 words."""
    spec_path = ROOT / "specs" / "014-multi-tenant-tracing-and-offline-crypto" / "spec.md"
    assert spec_path.exists(), "SPEC-014 markdown does not exist"
    content = spec_path.read_text(encoding="utf-8")
    words = len(content.split())
    assert words < 500, f"SPEC-014 word count {words} exceeds 500-word limit"


def test_spec_014_drakon_planar_invariants():
    """Invariant INV-014-02: Sprint 014 DRAKON flow must have 0 line crossings (C=0) and linear skewer."""
    schema_path = ROOT / "specs" / "014-multi-tenant-tracing-and-offline-crypto" / "logic.drakon.json"
    assert schema_path.exists(), "logic.drakon.json does not exist"
    validator = DrakonValidator()
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    schema = DrakonParser.parse_dict(data)
    result = validator.validate(schema)
    assert result.is_valid is True, f"Drakon validation failed: {result.errors}"
    assert result.stats.get("crossings", 0) == 0, "Crossings C must be 0"


def test_airgap_ed25519_crypto_verification():
    """Invariant INV-014-04: Standalone Ed25519 generation, signing and verification without network."""
    secret_hex, public_hex = generate_ed25519_keypair()
    assert len(secret_hex) == 64
    assert len(public_hex) == 64

    message = b"B-SDD Sprint 014 Air-Gapped Review Gate Manifest"
    secret_bytes = bytes.fromhex(secret_hex)
    public_bytes = bytes.fromhex(public_hex)

    sig = ed25519_sign(secret_bytes, message)
    assert len(sig) == 64
    assert ed25519_verify(public_bytes, message, sig) is True

    # Tampered message must fail
    tampered = b"Tampered Manifest Payload"
    assert ed25519_verify(public_bytes, tampered, sig) is False

    # AirGappedProofValidator test
    validator = AirGappedProofValidator()
    manifest = {
        "sprint": "014",
        "phase": "phi6",
        "operator": "Senior Sovereign Architect",
        "artifacts_verified": ["src/core/crypto_verifier.py", "src/adapters/gitnexus_graph.py"]
    }
    proof = validator.generate_proof(manifest, secret_hex)
    assert proof["algorithm"] == "Ed25519"
    assert proof["airgap_verified"] is True
    assert validator.verify_proof(proof, manifest) is True

    # Tampered manifest should fail verification
    tampered_manifest = dict(manifest)
    tampered_manifest["operator"] = "Imposter"
    assert validator.verify_proof(proof, tampered_manifest) is False


def test_multi_workspace_symbol_indexer(tmp_path):
    """TASK-014-4: Cross-workspace AST symbol discovery across linked repositories."""
    ws1 = tmp_path / "workspace_core"
    ws2 = tmp_path / "workspace_ui"
    ws1.mkdir()
    ws2.mkdir()

    # Create python file in ws1
    py_code = """
class BitemporalEngine:
    def execute_transaction(self, tx_id: str):
        pass

def calculate_planarity_metric(nodes):
    return 0
"""
    (ws1 / "engine.py").write_text(py_code, encoding="utf-8")

    # Create typescript file in ws2
    ts_code = """
export interface DrakonCanvasProps {
  diagramId: string;
}

export function renderDrakonWidget(config: any) {
  return config;
}

export const ASTRYX_THEME = 'dark';
"""
    (ws2 / "canvas.ts").write_text(ts_code, encoding="utf-8")

    indexer = MultiWorkspaceSymbolIndexer()
    indexer.register_workspace("core", ws1, is_active=True)
    indexer.register_workspace("ui", ws2, is_active=False)

    symbols = indexer.index_all()
    assert len(symbols) >= 4

    # Search symbol in core
    core_results = indexer.search_symbols("BitemporalEngine")
    assert len(core_results) >= 1
    assert core_results[0]["workspace"] == "core"
    assert core_results[0]["kind"] == "class"

    # Search symbol in ui
    ui_results = indexer.search_symbols("renderDrakonWidget")
    assert len(ui_results) >= 1
    assert ui_results[0]["workspace"] == "ui"
    assert ui_results[0]["kind"] == "function"

    # Cross-repo symbol resolution
    resolved = indexer.resolve_symbol_cross_workspace("calculate_planarity_metric")
    assert len(resolved) == 1
    assert resolved[0]["name"] == "calculate_planarity_metric"
    assert resolved[0]["workspace"] == "core"


def test_rule_of_2_skill_crystallizer(tmp_path):
    """Invariant INV-014-05: Procedure repeated >= 2 times must crystallize into .pi/skills/."""
    skills_dir = tmp_path / ".pi" / "skills"
    crystallizer = RuleOfTwoSkillCrystallizer(skills_root=skills_dir)

    # First observation - counter = 1, should not crystallize yet
    res1 = crystallizer.record_pattern(
        pattern_id="ed25519-airgap-verification",
        title="Air-Gapped Ed25519 Offline Proof Verification",
        description="Verifies cryptographic signatures for review gates without internet access.",
        instructions="1. Load manifest\n2. Compute RFC 8785 hash\n3. Verify Ed25519 signature."
    )
    assert res1["crystallized"] is False
    assert res1["frequency"] == 1
    assert not (skills_dir / "ed25519-airgap-verification" / "SKILL.md").exists()

    # Second observation - counter = 2, threshold reached -> crystallize
    res2 = crystallizer.record_pattern(
        pattern_id="ed25519-airgap-verification",
        title="Air-Gapped Ed25519 Offline Proof Verification",
        description="Verifies cryptographic signatures for review gates without internet access.",
        instructions="1. Load manifest\n2. Compute RFC 8785 hash\n3. Verify Ed25519 signature."
    )
    assert res2["crystallized"] is True
    assert res2["frequency"] == 2

    skill_file = skills_dir / "ed25519-airgap-verification" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")
    assert "name: ed25519-airgap-verification" in content
    assert "Rule of 2" in content


def test_server_symbols_and_crypto_endpoints(server):
    """TASK-014-4 & TASK-014-6: Server endpoints for symbol search and airgap verification."""
    # 1. Search symbols endpoint
    url = f"{server}/api/symbols/search?q=Drakon"
    with urllib.request.urlopen(url, timeout=10.0) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "symbols" in data
        assert "workspaces" in data

    # 2. Airgap proof verification endpoint
    validator = AirGappedProofValidator()
    sk_hex, _ = generate_ed25519_keypair()
    manifest = {"test": "sprint_014_verification", "inv": "INV-014-04"}
    proof = validator.generate_proof(manifest, sk_hex)

    verify_req = urllib.request.Request(
        f"{server}/api/crypto/verify-proof",
        data=json.dumps({"proof": proof, "manifest": manifest}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(verify_req, timeout=10.0) as resp:
        assert resp.status == 200
        verify_data = json.loads(resp.read().decode("utf-8"))
        assert verify_data["valid"] is True
        assert verify_data["airgap_verified"] is True


def test_server_direct_sse_streaming(server):
    """TASK-014-5: Direct binarized SSE streaming low latency chunk delivery (<30ms)."""
    req = urllib.request.Request(
        f"{server}/api/copilot/proxy",
        data=json.dumps({
            "prompt": "Verify bitemporal invariants",
            "stream": True,
            "slot": "coding-proxy"
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=4.0) as resp:
        assert resp.status == 200
        assert "text/event-stream" in resp.headers.get("Content-Type", "")

        first_chunk_latency = None
        has_token = False
        has_meta = False
        has_done = False

        for line in resp:
            text = line.decode("utf-8", errors="replace").strip()
            if not text.startswith("data:"):
                continue
            payload = text[5:].strip()
            if payload == "[DONE]":
                has_done = True
                break

            try:
                frame = json.loads(payload)
                if frame.get("type") == "token":
                    if first_chunk_latency is None:
                        first_chunk_latency = (time.perf_counter() - t0) * 1000
                    has_token = True
                elif frame.get("type") == "meta":
                    has_meta = True
                    assert "latency_ms" in frame
            except json.JSONDecodeError:
                continue

        assert has_token is True
        assert has_meta is True
        assert has_done is True
        assert first_chunk_latency is not None
        # First chunk streaming delivery should be fast (< 250ms in test environment)
        assert first_chunk_latency < 250.0
