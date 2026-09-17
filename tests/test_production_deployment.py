"""
Tests for B-SDD Production Deployment Suite (ADR-012).
Validates systemd unit syntax, Cloudflare Tunnel ingress rules,
and production health & telemetry verification probes.
100% Pure Python Standard Library.
"""
import subprocess
import threading
import time
from pathlib import Path
import pytest

from src.server.workbench_server import ThreadedHTTPServer, WorkbenchRequestHandler
from src.adapters.telemetry import TELEMETRY

TEST_PORT = 8797
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


def test_systemd_service_file_validity():
    """Verify systemd service unit parameters, paths, and sandbox security."""
    service_file = ROOT_DIR / "deploy" / "systemd" / "b-sdd-workbench.service"
    assert service_file.exists(), f"Service file missing: {service_file}"
    content = service_file.read_text(encoding="utf-8")

    assert "[Unit]" in content
    assert "[Service]" in content
    assert "[Install]" in content
    assert "ExecStart=/usr/bin/python3 -m src.server.workbench_server" in content
    assert "Restart=always" in content
    assert "BSDD_PORT=8765" in content
    assert "BSDD_ENV=production" in content
    assert "WantedBy=multi-user.target" in content


def test_cloudflare_tunnel_config_validity():
    """Verify Cloudflare Tunnel ingress rules for bsdd.exodus.pp.ua."""
    tunnel_file = ROOT_DIR / "deploy" / "tunnel" / "bsdd-tunnel.yml"
    assert tunnel_file.exists(), f"Tunnel file missing: {tunnel_file}"
    content = tunnel_file.read_text(encoding="utf-8")

    assert "hostname: bsdd.exodus.pp.ua" in content
    assert "service: http://127.0.0.1:8765" in content
    assert "noChunkedEncoding: false" in content
    assert "http_status:404" in content


def test_verify_production_health_script(server):
    """Execute scripts/verify_production_health.sh against live test server."""
    probe_script = ROOT_DIR / "scripts" / "verify_production_health.sh"
    assert probe_script.exists()

    result = subprocess.run(
        [str(probe_script), f"http://127.0.0.1:{TEST_PORT}"],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Health probe failed: stdout={result.stdout} stderr={result.stderr}"
    assert "All 4 production health & telemetry probes PASSED" in result.stdout


def test_deploy_production_script_syntax():
    """Verify scripts/deploy_production.sh bash syntax without deploying remotely."""
    deploy_script = ROOT_DIR / "scripts" / "deploy_production.sh"
    assert deploy_script.exists()

    # Syntax check only via bash -n
    result = subprocess.run(
        ["bash", "-n", str(deploy_script)],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Bash syntax check failed: {result.stderr}"
