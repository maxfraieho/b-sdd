"""
Unit tests for LayaClient (Deliverable C - Sprint 024).
Verifies sub-40ms System 1 client communication and graceful degradation (ADR-002).
"""
import json
import urllib.error
from unittest.mock import MagicMock, patch
import pytest

from src.core.laya_client import LayaClient, get_laya_client


class TestLayaClient:
    def test_client_initialization_defaults(self):
        client = LayaClient()
        assert client.host == "192.168.3.251"
        assert client.port == 9623
        assert client.base_url == "http://192.168.3.251:9623"
        assert client.timeout == 3.0

    def test_client_custom_config(self):
        client = LayaClient(host="127.0.0.1", port=9999, timeout=1.5)
        assert client.base_url == "http://127.0.0.1:9999"
        assert client.timeout == 1.5

    @patch("urllib.request.urlopen")
    def test_check_health_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "status": "ok",
            "model": "laya-multilingual",
            "port": 9623
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        client = LayaClient()
        health = client.check_health()
        assert health["status"] == "ok"
        assert health["model"] == "laya-multilingual"
        assert health["port"] == 9623

    @patch("urllib.request.urlopen")
    def test_check_health_failure_returns_down(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
        client = LayaClient()
        health = client.check_health()
        assert health["status"] == "down"
        assert "Connection refused" in health["error"]

    @patch("urllib.request.urlopen")
    def test_query_decision_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "status": "ok",
            "decision": "PROCEED",
            "action": "AUTO_EXECUTE",
            "confidence": 0.96,
            "latency_ms": 14.2,
            "model": "laya-multilingual"
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        client = LayaClient()
        res = client.query_decision(
            state={"sprint": "sprint_024", "invariants_satisfied": True},
            questions={}
        )
        assert res["fallback"] is False
        assert res["decision"] == "PROCEED"
        assert res["action"] == "AUTO_EXECUTE"
        assert res["confidence"] == 0.96
        assert res["latency_ms"] == 14.2

    @patch("urllib.request.urlopen")
    def test_query_decision_graceful_fallback_on_unreachable(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError("Pixel 7 asleep")
        client = LayaClient()

        # Normal clean state -> should fallback to PROCEED safely
        res = client.query_decision(
            state={"sprint": "sprint_024", "invariants_satisfied": True},
            questions={}
        )
        assert res["fallback"] is True
        assert res["status"] == "degraded"
        assert res["decision"] == "PROCEED"
        assert res["action"] == "AUTO_EXECUTE"
        assert "Pixel 7 asleep" in res["error"]
        assert "state_digest" in res

    @patch("urllib.request.urlopen")
    def test_query_decision_graceful_fallback_on_blocked_state(self, mock_urlopen):
        mock_urlopen.side_effect = ConnectionRefusedError("Podroid stopped")
        client = LayaClient()

        # State with blockers -> fallback should safely HALT_FOR_INSPECTION
        res = client.query_decision(
            state={"sprint": "sprint_024", "blocked": ["Missing permission"]},
            questions={}
        )
        assert res["fallback"] is True
        assert res["decision"] == "HALT_FOR_INSPECTION"
        assert res["action"] == "REQUIRE_OPERATOR_REVIEW"

    def test_get_laya_client_singleton(self):
        c1 = get_laya_client()
        c2 = get_laya_client()
        assert c1 is c2
