"""
Tests for B-SDD Production Telemetry & Observability Adapter (ADR-012).
100% Pure Python Standard Library.
"""
import json
import time
import threading
import urllib.request
from pathlib import Path
import pytest

from src.adapters.telemetry import TELEMETRY, SlidingWindowQuantiles, TelemetryCollector
from src.server.workbench_server import ThreadedHTTPServer, WorkbenchRequestHandler
from src.core.compiler import BSDDCompiler

TEST_PORT = 8799
ROOT_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def server():
    TELEMETRY.reset()
    srv = ThreadedHTTPServer(("127.0.0.1", TEST_PORT), WorkbenchRequestHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)
    yield srv
    srv.shutdown()
    srv.server_close()
    TELEMETRY.reset()


def test_sliding_window_quantiles():
    """Verify statistical quantile calculations across ring buffer."""
    sw = SlidingWindowQuantiles(max_samples=100)
    for i in range(1, 101):
        sw.record(float(i))

    stats = sw.get_stats()
    assert stats["count"] == 100
    assert stats["min"] == 1.0
    assert stats["max"] == 100.0
    assert stats["avg"] == 50.5
    assert stats["p50"] == 50.0
    assert stats["p90"] == 90.0
    assert stats["p95"] == 95.0
    assert stats["p99"] == 99.0


def test_telemetry_collector_compiler_sla():
    """Verify compiler SLA recording, word budget, and SLA violation flagging (ADR-012)."""
    col = TelemetryCollector()

    # Normal compilation within SLA
    col.record_compile(duration_ms=14.2, word_count=476, success=True, budget=500)
    summary = col.get_summary()
    assert summary["compiler"]["last_compile_ms"] == 14.2
    assert summary["compiler"]["word_count"] == 476
    assert summary["compiler"]["sla_passed"] is True
    assert summary["compiler"]["sla_violations"] == 0

    # Violation of sub-50ms SLA
    col.record_compile(duration_ms=65.0, word_count=480, success=True, budget=500)
    summary2 = col.get_summary()
    assert summary2["compiler"]["last_compile_ms"] == 65.0
    assert summary2["compiler"]["sla_passed"] is False
    assert summary2["compiler"]["sla_violations"] == 1
    assert summary2["status"] == "degraded"


def test_telemetry_collector_overhead_sub_1ms():
    """Invariant ADR-012-INV-02: Telemetry collection overhead must remain strictly < 1ms."""
    col = TelemetryCollector()
    n = 1000
    t0 = time.perf_counter()
    for _ in range(n):
        with col.measure_latency("compile", word_count=450):
            pass
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    per_op_ms = elapsed_ms / n
    assert per_op_ms < 0.2, f"Telemetry overhead exceeded 0.2ms: {per_op_ms:.4f} ms"


def test_prometheus_metrics_format():
    """Invariant ADR-012-INV-03: Metrics must be exportable in standard Prometheus format."""
    col = TelemetryCollector()
    col.record_compile(duration_ms=18.5, word_count=470, success=True)
    col.record_request("GET", "/api/health", 200, 2.1)
    col.record_cache_access("github", True)
    col.record_cache_access("utopia", True)

    prom = col.get_prometheus_metrics()
    assert "# HELP bsdd_compile_latency_ms" in prom
    assert "# TYPE bsdd_compile_latency_ms summary" in prom
    assert 'bsdd_compile_latency_ms{quantile="0.5"}' in prom
    assert "bsdd_compile_last_ms 18.5" in prom
    assert "bsdd_compile_word_count 470" in prom
    assert "bsdd_http_requests_total 1" in prom
    assert 'bsdd_cache_hit_ratio{backend="github"} 1.0' in prom
    assert "bsdd_uptime_seconds" in prom


def test_server_telemetry_endpoint(server):
    """GET /api/telemetry: Verify structured JSON snapshot endpoint."""
    url = f"http://127.0.0.1:{TEST_PORT}/api/telemetry"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        assert resp.headers.get("Content-Type") == "application/json"
        data = json.loads(resp.read().decode("utf-8"))
        assert "status" in data
        assert "compiler" in data
        assert "http" in data
        assert "cache" in data
        assert "deployment" in data
        assert data["compiler"]["sla_target_ms"] == 50.0


def test_server_metrics_endpoint(server):
    """GET /api/metrics: Verify Prometheus exposition endpoint."""
    url = f"http://127.0.0.1:{TEST_PORT}/api/metrics"
    req = urllib.request.Request(url, headers={"Accept": "text/plain"})
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        assert "text/plain" in resp.headers.get("Content-Type", "")
        body = resp.read().decode("utf-8")
        assert "bsdd_http_requests_total" in body
        assert "bsdd_compile_latency_ms" in body


def test_server_realtime_telemetry_sse(server):
    """GET /api/realtime/telemetry: Verify Realtime SSE telemetry stream."""
    url = f"http://127.0.0.1:{TEST_PORT}/api/realtime/telemetry"
    req = urllib.request.Request(url, headers={"Accept": "text/event-stream"})
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        assert resp.status == 200
        assert "text/event-stream" in resp.headers.get("Content-Type", "")
        # Read the initial event
        line1 = resp.readline().decode("utf-8").strip()
        while not line1.startswith("data:"):
            line1 = resp.readline().decode("utf-8").strip()

        event_json = json.loads(line1.replace("data:", "").strip())
        assert "compiler" in event_json
        assert "http" in event_json
        assert "deployment" in event_json


def test_adr_012_invariants_compiled():
    """Verify ADR-012 invariants are parsed and recognized by B-SDD compiler."""
    compiler = BSDDCompiler(root_dir=ROOT_DIR)
    intents = compiler.scan_and_sync_intents()
    adr_12 = next((it for it in intents if it["id"] == "ADR-012"), None)
    assert adr_12 is not None, "ADR-012 not found in scanned intents!"
    assert adr_12["status"] == "ACTIVE"
    invariants = adr_12.get("invariants", [])
    assert any("ADR-012-INV-01" in inv for inv in invariants)
    assert any("ADR-012-INV-02" in inv for inv in invariants)
    assert any("ADR-012-INV-03" in inv for inv in invariants)
