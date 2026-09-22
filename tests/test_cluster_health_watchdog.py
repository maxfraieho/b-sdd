"""
Unit and Integration Tests for Cluster Health Watchdog.
Sprint 032 - Phase 2.
100% Python Standard Library (ADR-002).
"""
import io
import json
import socket
import time
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.core.dto.cluster_health import (
    ClusterHealthReportDTO,
    ServiceHealthDTO,
    WatchdogStateDTO,
)
from daemon.cluster_health_watchdog import (
    ClusterHealthWatchdog,
    ServiceEndpoint,
    probe_http_endpoint,
    probe_tcp_endpoint,
)


def test_laya_probe_success_and_timeout():
    """Verifies that HTTP probe succeeds on 200 OK and reports timeout within SLA."""
    # 1. Success case
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b'{"status": "ok", "model": "laya-system1"}'
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        endpoint = ServiceEndpoint("laya_decision_engine", "192.168.3.251", 9623, "/health", "HTTP", 1.5)
        res = probe_http_endpoint(endpoint)
        assert res.is_up is True
        assert res.service_id == "laya_decision_engine"
        assert res.latency_ms >= 0.0
        assert res.error_message is None

    # 2. Timeout case
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timed out")):
        endpoint = ServiceEndpoint("laya_decision_engine", "192.168.3.251", 9623, "/health", "HTTP", 1.5)
        res = probe_http_endpoint(endpoint)
        assert res.is_up is False
        assert "timed out" in (res.error_message or "")


def test_utopia_socket_probe():
    """Verifies TCP socket probe connection and failure handling for Utopia DB :9622."""
    endpoint = ServiceEndpoint("utopia_db_worm", "192.168.3.251", 9622, None, "TCP", 1.5)

    # 1. Successful connection
    mock_sock = MagicMock()
    with patch("socket.create_connection", return_value=mock_sock):
        res = probe_tcp_endpoint(endpoint)
        assert res.is_up is True
        assert res.service_id == "utopia_db_worm"
        assert res.port == 9622
        mock_sock.close.assert_called_once()

    # 2. Connection refused
    with patch("socket.create_connection", side_effect=ConnectionRefusedError("Connection refused")):
        res = probe_tcp_endpoint(endpoint)
        assert res.is_up is False
        assert "Connection refused" in (res.error_message or "")


def test_stateful_debounce_two_failure_rule(tmp_path):
    """
    Tests Stateful Debounce:
    - 1 failure -> fail_streak = 1, NO alert sent.
    - 2 consecutive failures -> status = DOWN, Telegram DOWN alert sent.
    - 3rd failure -> already DOWN, NO alert storm.
    - Recovery (is_up = True) -> status = UP, Telegram RECOVERY alert sent.
    """
    state_file = tmp_path / "test_state.json"
    watchdog = ClusterHealthWatchdog(state_file=state_file)

    alerts_sent = []
    watchdog.send_telegram_alert = lambda msg: alerts_sent.append(msg)

    # Step 1: First failure
    health_fail = ServiceHealthDTO("laya_decision_engine", "192.168.3.251", 9623, is_up=False, latency_ms=1500.0, error_message="timeout")
    watchdog.process_service_state(health_fail)

    state = watchdog.states["laya_decision_engine"]
    assert state.fail_streak == 1
    assert state.status == "UP"
    assert len(alerts_sent) == 0, "No alert should be sent on first failure"

    # Step 2: Second failure -> Triggers DOWN alert
    watchdog.process_service_state(health_fail)
    assert state.fail_streak == 2
    assert state.status == "DOWN"
    assert len(alerts_sent) == 1
    assert "DOWN" in alerts_sent[0]
    assert "laya_decision_engine" in alerts_sent[0]

    # Step 3: Third failure -> Alert storm protection (no extra alert)
    watchdog.process_service_state(health_fail)
    assert state.fail_streak == 3
    assert state.status == "DOWN"
    assert len(alerts_sent) == 1, "Alert storm prevention failed"

    # Step 4: Service recovers -> Triggers RECOVERY alert
    health_ok = ServiceHealthDTO("laya_decision_engine", "192.168.3.251", 9623, is_up=True, latency_ms=35.0)
    watchdog.process_service_state(health_ok)
    assert state.fail_streak == 0
    assert state.status == "UP"
    assert len(alerts_sent) == 2
    assert "RECOVERED" in alerts_sent[1]


def test_watchdog_state_persistence(tmp_path):
    """Verifies atomic write and reload of cluster health state."""
    state_file = tmp_path / "cluster_health.json"
    watchdog = ClusterHealthWatchdog(state_file=state_file)

    mock_report = ClusterHealthReportDTO(
        timestamp="2026-09-22T15:00:00Z",
        services=[
            ServiceHealthDTO("laya_decision_engine", "192.168.3.251", 9623, is_up=True, latency_ms=25.4),
            ServiceHealthDTO("utopia_db_worm", "192.168.3.251", 9622, is_up=True, latency_ms=8.1),
            ServiceHealthDTO("n8n_orchestrator", "n8n.exodus.pp.ua", 443, is_up=True, latency_ms=95.0),
            ServiceHealthDTO("local_supervisor", "127.0.0.1", 8161, is_up=True, latency_ms=1.2)
        ],
        overall_status="UP"
    )

    watchdog.persist_health_report(mock_report)
    assert state_file.exists()

    data = json.loads(state_file.read_text(encoding="utf-8"))
    assert data["overall_status"] == "UP"
    assert len(data["services"]) == 4
    assert data["services"][0]["service_id"] == "laya_decision_engine"
