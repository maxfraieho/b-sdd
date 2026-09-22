#!/usr/bin/env python3
"""
B-SDD Cluster Health Watchdog & Proactive Telemetry Daemon.
Sprint 032 - Track A / Phase 3.
Compliant with ADR-001 (Bitemporal WORM), ADR-002 (Pure Stdlib Core), and ADR-014 (Laya Decision Engine).
100% Pure Python Standard Library.
"""
import argparse
import datetime
import json
import logging
import os
from pathlib import Path
import socket
import sys
import time
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.parse
import urllib.request

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.dto.cluster_health import (
    ClusterHealthReportDTO,
    ServiceHealthDTO,
    WatchdogStateDTO,
)

logger = logging.getLogger("ClusterHealthWatchdog")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Default Configuration
DEFAULT_STATE_FILE = Path(os.getenv("CLUSTER_HEALTH_PATH", "/var/run/b_sdd_cluster_health.json"))
FALLBACK_STATE_FILE = Path("/tmp/b_sdd_cluster_health.json")
DEFAULT_INTERVAL_SECONDS = float(os.getenv("WATCHDOG_INTERVAL", "60.0"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8717667434:AAFWddh_xwTfMVHW7puxrlIFprbO9m_Au7Y")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6412868393")


class ServiceEndpoint:
    """Descriptor for an individual cluster endpoint to probe."""
    def __init__(
        self,
        service_id: str,
        host: str,
        port: int,
        path: Optional[str] = None,
        proto: str = "HTTP",
        timeout: float = 1.5,
        scheme: str = "http"
    ):
        self.service_id = service_id
        self.host = host
        self.port = port
        self.path = path or "/"
        self.proto = proto.upper()
        self.timeout = timeout
        self.scheme = scheme


DEFAULT_ENDPOINTS = [
    ServiceEndpoint("laya_decision_engine", "192.168.3.251", 9623, "/health", "HTTP", timeout=1.5),
    ServiceEndpoint("utopia_db_worm", "192.168.3.251", 9622, None, "TCP", timeout=1.5),
    ServiceEndpoint("n8n_orchestrator", "n8n.exodus.pp.ua", 443, "/healthz", "HTTP", timeout=3.0, scheme="https"),
    ServiceEndpoint("local_supervisor", "127.0.0.1", 8161, "/health", "HTTP", timeout=1.5),
]


def probe_http_endpoint(endpoint: ServiceEndpoint) -> ServiceHealthDTO:
    """Probes HTTP/HTTPS endpoint with precise latency measurement."""
    url = f"{endpoint.scheme}://{endpoint.host}:{endpoint.port}{endpoint.path}" if endpoint.port not in (80, 443) else f"{endpoint.scheme}://{endpoint.host}{endpoint.path}"
    headers = {"User-Agent": "B-SDD-ClusterWatchdog/1.0"}
    req = urllib.request.Request(url, headers=headers)
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=endpoint.timeout) as resp:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            is_up = resp.status == 200
            return ServiceHealthDTO(
                service_id=endpoint.service_id,
                host=endpoint.host,
                port=endpoint.port,
                is_up=is_up,
                latency_ms=elapsed_ms,
                error_message=None if is_up else f"HTTP {resp.status}"
            )
    except Exception as e:
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        return ServiceHealthDTO(
            service_id=endpoint.service_id,
            host=endpoint.host,
            port=endpoint.port,
            is_up=False,
            latency_ms=elapsed_ms,
            error_message=str(e)
        )


def probe_tcp_endpoint(endpoint: ServiceEndpoint) -> ServiceHealthDTO:
    """Probes raw TCP socket connection for daemon services."""
    t0 = time.perf_counter()
    sock = None
    try:
        sock = socket.create_connection((endpoint.host, endpoint.port), timeout=endpoint.timeout)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        sock.close()
        return ServiceHealthDTO(
            service_id=endpoint.service_id,
            host=endpoint.host,
            port=endpoint.port,
            is_up=True,
            latency_ms=elapsed_ms,
            error_message=None
        )
    except Exception as e:
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        if sock:
            try:
                sock.close()
            except Exception:
                pass
        return ServiceHealthDTO(
            service_id=endpoint.service_id,
            host=endpoint.host,
            port=endpoint.port,
            is_up=False,
            latency_ms=elapsed_ms,
            error_message=str(e)
        )


class ClusterHealthWatchdog:
    """Monitors cluster nodes, tracks stateful debounce, and raises Telegram alerts."""

    def __init__(
        self,
        endpoints: Optional[List[ServiceEndpoint]] = None,
        state_file: Optional[Path] = None,
        telegram_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None
    ):
        self.endpoints = endpoints if endpoints is not None else DEFAULT_ENDPOINTS
        self.state_file = Path(state_file) if state_file else DEFAULT_STATE_FILE
        self.telegram_token = telegram_token or TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = telegram_chat_id or TELEGRAM_CHAT_ID

        # Vector 3 Semantic Invariant Verification Asserts
        assert self.state_file is not None, "state_file is not None"
        assert self.endpoints is not None, "endpoints is not None"
        assert len(self.endpoints) >= 4, "len(endpoints) >= 4"

        self.states: Dict[str, WatchdogStateDTO] = {
            ep.service_id: WatchdogStateDTO(service_id=ep.service_id, status="UP", fail_streak=0)
            for ep in self.endpoints
        }

    def send_telegram_alert(self, text: str) -> bool:
        """Dispatches notification via official Telegram Bot API."""
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram credentials missing; skipping dispatch.")
            return False

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "B-SDD-Watchdog/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                return resp.status == 200
        except Exception as e:
            logger.error(f"Failed to dispatch Telegram alert: {e}")
            return False

    def process_service_state(self, health: ServiceHealthDTO) -> Optional[str]:
        """
        Applies Stateful Debounce (The 2-Failure Rule):
        1) 1 failure -> fail_streak = 1, status remains UP, NO alert.
        2) 2 consecutive failures -> status = DOWN, send DOWN alert.
        3) 3+ failures -> fail_streak increments, alert suppressed (no storm).
        4) Recovery (is_up = True after DOWN) -> status = UP, send RECOVERY alert.
        """
        sid = health.service_id
        st = self.states.get(sid, WatchdogStateDTO(service_id=sid))
        now = time.time()
        alert_sent = None

        if not health.is_up:
            st.fail_streak += 1
            if st.fail_streak == 2 and st.status != "DOWN":
                st.status = "DOWN"
                st.last_alert_ts = now
                msg = (
                    f"🚨 <b>[ALERT: CLUSTER SERVICE DOWN]</b>\n"
                    f"• <b>Service</b>: <code>{sid}</code>\n"
                    f"• <b>Host</b>: {health.host}:{health.port}\n"
                    f"• <b>Fail Streak</b>: {st.fail_streak}\n"
                    f"• <b>Error</b>: <i>{health.error_message}</i>\n"
                    f"• <b>Timestamp</b>: {datetime.datetime.now(datetime.timezone.utc).isoformat()}"
                )
                self.send_telegram_alert(msg)
                alert_sent = "DOWN"
                logger.warning(f"Service {sid} marked DOWN (fail_streak=2). Alert dispatched.")
        else:
            if st.status == "DOWN":
                st.status = "UP"
                st.fail_streak = 0
                st.last_alert_ts = now
                msg = (
                    f"🟢 <b>[RECOVERED: CLUSTER SERVICE UP]</b>\n"
                    f"• <b>Service</b>: <code>{sid}</code>\n"
                    f"• <b>Host</b>: {health.host}:{health.port}\n"
                    f"• <b>Latency</b>: {health.latency_ms}ms\n"
                    f"• <b>Timestamp</b>: {datetime.datetime.now(datetime.timezone.utc).isoformat()}"
                )
                self.send_telegram_alert(msg)
                alert_sent = "RECOVERED"
                logger.info(f"Service {sid} RECOVERED to UP. Alert dispatched.")
            else:
                st.fail_streak = 0
                st.status = "UP"

        self.states[sid] = st
        return alert_sent

    def probe_all_services(self) -> ClusterHealthReportDTO:
        """Executes probes across all registered cluster endpoints."""
        results: List[ServiceHealthDTO] = []
        for ep in self.endpoints:
            if ep.proto == "TCP":
                h = probe_tcp_endpoint(ep)
            else:
                h = probe_http_endpoint(ep)

            self.process_service_state(h)
            results.append(h)

        # Compute overall status
        any_down = any(r.is_up is False for r in results)
        all_down = all(r.is_up is False for r in results)
        overall = "DOWN" if all_down else ("DEGRADED" if any_down else "UP")

        ts_now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        report = ClusterHealthReportDTO(
            timestamp=ts_now,
            services=results,
            overall_status=overall
        )

        # Vector 3 Invariant
        assert report.timestamp is not None, "report.timestamp is not None"

        return report

    def persist_health_report(self, report: ClusterHealthReportDTO) -> Path:
        """Writes health state atomically to disk with permissions fallback."""
        target = self.state_file
        data_str = json.dumps(report.to_dict(), indent=2)

        for candidate in [target, FALLBACK_STATE_FILE]:
            try:
                candidate.parent.mkdir(parents=True, exist_ok=True)
                tmp_file = candidate.parent / f".tmp_{candidate.name}"
                tmp_file.write_text(data_str, encoding="utf-8")
                tmp_file.replace(candidate)
                return candidate
            except PermissionError:
                continue

        # If neither writable, write to current dir
        local_fallback = Path("b_sdd_cluster_health.json")
        local_fallback.write_text(data_str, encoding="utf-8")
        return local_fallback

    def run_once(self) -> ClusterHealthReportDTO:
        """Executes single probe cycle and writes cache."""
        report = self.probe_all_services()
        persisted_path = self.persist_health_report(report)
        logger.info(f"Probe cycle complete (overall: {report.overall_status}). Cached to {persisted_path}")
        return report

    def run_loop(self, interval_seconds: float = DEFAULT_INTERVAL_SECONDS):
        """Continuous background execution loop."""
        logger.info(f"Starting Cluster Health Watchdog loop (interval={interval_seconds}s)")
        while True:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f"Error in watchdog cycle: {e}")
            time.sleep(interval_seconds)


def main():
    parser = argparse.ArgumentParser(description="B-SDD Cluster Health Watchdog Daemon")
    parser.add_argument("--once", action="store_true", help="Run a single probe cycle and exit")
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_SECONDS, help="Polling interval in seconds")
    parser.add_argument("--state-file", default=None, help="Path to state cache JSON file")
    args = parser.parse_args()

    watchdog = ClusterHealthWatchdog(state_file=Path(args.state_file) if args.state_file else None)

    if args.once:
        rep = watchdog.run_once()
        print(json.dumps(rep.to_dict(), indent=2))
    else:
        watchdog.run_loop(args.interval)


if __name__ == "__main__":
    main()
