"""
Unit tests for Podroid Watchdog (Deliverable B - Sprint 024).
Verifies LAN health checks, Telegram formatting, and state debounce transitions.
"""
import json
import socket
from unittest.mock import MagicMock, patch
import pytest

from scripts.podroid_watchdog import (
    check_utopia_socket,
    check_laya_http,
    check_podroid_all,
    format_downtime_alert,
    format_recovery_alert,
    run_once,
    load_state,
    save_state
)


class TestPodroidWatchdog:
    def test_alert_messages_formatting(self):
        downtime_msg = format_downtime_alert("192.168.3.251")
        assert "🚨 [ALERT: B-SDD PODROID DOWNTIME] Podroid на Pixel 7 (192.168.3.251) вимкнено!" in downtime_msg
        assert "❌ Utopia DB (порт 9622) або Laya (порт 9623) не відповідають." in downtime_msg
        assert "📱 Дія для оператора: Відкрийте застосунок Podroid на Pixel 7 та запустіть сервіси." in downtime_msg

        rec_msg = format_recovery_alert("192.168.3.251")
        assert "🟢 [RECOVERED: B-SDD PODROID] Podroid на Pixel 7 успішно відновив роботу (Utopia DB: 9622, Laya: 9623)." in rec_msg

    @patch("socket.create_connection")
    def test_check_utopia_socket_up(self, mock_create_conn):
        mock_sock = MagicMock()
        mock_create_conn.return_value = mock_sock

        ok, reason = check_utopia_socket("127.0.0.1", 9622)
        assert ok is True
        assert "Connected" in reason
        mock_sock.close.assert_called_once()

    @patch("socket.create_connection")
    def test_check_utopia_socket_down(self, mock_create_conn):
        mock_create_conn.side_effect = ConnectionRefusedError("Connection refused")

        ok, reason = check_utopia_socket("127.0.0.1", 9622)
        assert ok is False
        assert "Connection refused" in reason

    @patch("urllib.request.urlopen")
    def test_check_laya_http_up(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"status": "ok", "model": "laya-multilingual"}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        ok, reason = check_laya_http("127.0.0.1", 9623)
        assert ok is True
        assert "HTTP 200 OK" in reason

    @patch("urllib.request.urlopen")
    def test_check_laya_http_down(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError("Pixel 7 asleep")

        ok, reason = check_laya_http("127.0.0.1", 9623)
        assert ok is False
        assert "Pixel 7 asleep" in reason

    @patch("scripts.podroid_watchdog.check_laya_http")
    @patch("scripts.podroid_watchdog.check_utopia_socket")
    def test_check_podroid_all(self, mock_utopia, mock_laya):
        mock_utopia.return_value = (True, "OK")
        mock_laya.return_value = (True, "OK")

        diag = check_podroid_all("127.0.0.1", 9622, 9623)
        assert diag["is_healthy"] is True
        assert diag["utopia_ok"] is True
        assert diag["laya_ok"] is True

    @patch("scripts.podroid_watchdog.send_telegram")
    @patch("scripts.podroid_watchdog.check_podroid_all")
    @patch("scripts.podroid_watchdog.load_state")
    @patch("scripts.podroid_watchdog.save_state")
    def test_run_once_transitions(self, mock_save, mock_load, mock_check, mock_tg):
        # 1. Transition UP -> DOWN triggers alert
        mock_load.return_value = {"last_status": "UP", "last_alert_time": 0}
        mock_check.return_value = {
            "is_healthy": False,
            "utopia_ok": False,
            "utopia_reason": "Refused",
            "laya_ok": False,
            "laya_reason": "Timeout"
        }

        res = run_once("192.168.3.251", 9622, 9623, dry_run=False)
        assert res is False
        mock_tg.assert_called_once()
        alert_sent = mock_tg.call_args[0][0]
        assert "🚨 [ALERT: B-SDD PODROID DOWNTIME]" in alert_sent

        # 2. Subsequent check while still DOWN within cooldown -> no repeated alert
        mock_tg.reset_mock()
        mock_load.return_value = {"last_status": "DOWN", "last_alert_time": 9999999999.0}
        res2 = run_once("192.168.3.251", 9622, 9623, dry_run=False)
        assert res2 is False
        mock_tg.assert_not_called()

        # 3. Transition DOWN -> UP triggers recovery alert
        mock_tg.reset_mock()
        mock_load.return_value = {"last_status": "DOWN", "last_alert_time": 100}
        mock_check.return_value = {
            "is_healthy": True,
            "utopia_ok": True,
            "utopia_reason": "OK",
            "laya_ok": True,
            "laya_reason": "OK"
        }
        res3 = run_once("192.168.3.251", 9622, 9623, dry_run=False)
        assert res3 is True
        mock_tg.assert_called_once()
        rec_sent = mock_tg.call_args[0][0]
        assert "🟢 [RECOVERED: B-SDD PODROID]" in rec_sent
