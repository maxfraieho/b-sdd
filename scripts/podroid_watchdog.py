#!/usr/bin/env python3
"""
B-SDD Sovereign Podroid Watchdog & Edge Resilience Monitor.
Monitors the availability of Google Pixel 7 (Podroid Alpine VM: 192.168.3.251).
Checks:
  - Port 9622: Utopia DB (WORM ledger & bitemporal store)
  - Port 9623: Laya Decision Engine (HTTP /health endpoint)

Alerts operator via Telegram on downtime and recovery.
State is cached in /tmp/podroid_watchdog_state.json to prevent alert storms.
100% Pure Python Standard Library (ADR-002).
"""
import argparse
import json
import logging
import os
import socket
import sys
import time
import urllib.request
import urllib.error
from typing import Dict, Tuple, Any

DEFAULT_PODROID_HOST = os.getenv("PODROID_HOST", "192.168.3.251")
DEFAULT_UTOPIA_PORT = int(os.getenv("UTOPIA_PORT", "9622"))
DEFAULT_LAYA_PORT = int(os.getenv("LAYA_PORT", "9623"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8717667434:AAFWddh_xwTfMVHW7puxrlIFprbO9m_Au7Y")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6412868393")
STATE_FILE = "/tmp/podroid_watchdog_state.json"
ALERT_COOLDOWN_SEC = 1800  # 30 minutes between repeat alerts when down

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [PodroidWatchdog] %(message)s"
)


def send_telegram(text: str) -> bool:
    """Dispatches Telegram notification to operator."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(url, data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        logging.error(f"Failed to dispatch Telegram message: {e}")
        return False


def check_utopia_socket(host: str = DEFAULT_PODROID_HOST, port: int = DEFAULT_UTOPIA_PORT, timeout: float = 2.5) -> Tuple[bool, str]:
    """Checks raw TCP socket connectivity to Utopia DB (port 9622)."""
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True, "TCP 9622 Connected"
    except (socket.timeout, TimeoutError):
        return False, "Connection timed out"
    except ConnectionRefusedError:
        return False, "Connection refused"
    except OSError as e:
        return False, f"Socket error: {e}"


def check_laya_http(host: str = DEFAULT_PODROID_HOST, port: int = DEFAULT_LAYA_PORT, timeout: float = 2.5) -> Tuple[bool, str]:
    """Checks HTTP /health endpoint of Laya Decision Engine (port 9623)."""
    url = f"http://{host}:{port}/health"
    headers = {"User-Agent": "B-SDD-Podroid-Watchdog/1.0"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("status") == "ok":
                    return True, "HTTP 200 OK (model: " + str(data.get("model", "laya")) + ")"
                return False, f"Unexpected payload: {data}"
            return False, f"Unexpected HTTP status: {resp.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"URL Error: {e.reason}"
    except Exception as e:
        return False, f"Health check error: {e}"


def check_podroid_all(
    host: str = DEFAULT_PODROID_HOST,
    utopia_port: int = DEFAULT_UTOPIA_PORT,
    laya_port: int = DEFAULT_LAYA_PORT,
    timeout: float = 2.5
) -> Dict[str, Any]:
    """Performs full diagnostic of Podroid services on Pixel 7."""
    utopia_ok, utopia_reason = check_utopia_socket(host, utopia_port, timeout)
    laya_ok, laya_reason = check_laya_http(host, laya_port, timeout)
    is_healthy = utopia_ok and laya_ok

    return {
        "host": host,
        "utopia_port": utopia_port,
        "utopia_ok": utopia_ok,
        "utopia_reason": utopia_reason,
        "laya_port": laya_port,
        "laya_ok": laya_ok,
        "laya_reason": laya_reason,
        "is_healthy": is_healthy,
        "timestamp": time.time()
    }


def load_state() -> Dict[str, Any]:
    """Loads state from local JSON file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "last_status": "UP",
        "last_alert_time": 0,
        "consecutive_failures": 0,
        "utopia_ok": True,
        "laya_ok": True
    }


def save_state(state: Dict[str, Any]) -> None:
    """Persists state to local JSON file."""
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save watchdog state: {e}")


def format_downtime_alert(host: str) -> str:
    return (
        f"🚨 [ALERT: B-SDD PODROID DOWNTIME] Podroid на Pixel 7 ({host}) вимкнено!\n"
        f"❌ Utopia DB (порт 9622) або Laya (порт 9623) не відповідають.\n"
        f"📱 Дія для оператора: Відкрийте застосунок Podroid на Pixel 7 та запустіть сервіси."
    )


def format_recovery_alert(host: str) -> str:
    return f"🟢 [RECOVERED: B-SDD PODROID] Podroid на Pixel 7 успішно відновив роботу (Utopia DB: 9622, Laya: 9623)."


def run_once(
    host: str = DEFAULT_PODROID_HOST,
    utopia_port: int = DEFAULT_UTOPIA_PORT,
    laya_port: int = DEFAULT_LAYA_PORT,
    dry_run: bool = False
) -> bool:
    """
    Executes a single check pass.
    Updates state and sends Telegram notifications if status changed or cooldown elapsed.
    Returns True if healthy, False if down.
    """
    state = load_state()
    diag = check_podroid_all(host, utopia_port, laya_port)
    now = time.time()

    is_healthy = diag["is_healthy"]
    logging.info(
        f"Check results for {host} -> Utopia (:{utopia_port}): {'UP' if diag['utopia_ok'] else 'DOWN'} ({diag['utopia_reason']}), "
        f"Laya (:{laya_port}): {'UP' if diag['laya_ok'] else 'DOWN'} ({diag['laya_reason']})"
    )

    if is_healthy:
        if state.get("last_status") == "DOWN":
            logging.info("Podroid services have RECOVERED. Dispatching recovery alert...")
            rec_msg = format_recovery_alert(host)
            if not dry_run:
                send_telegram(rec_msg)
            else:
                logging.info(f"[DRY-RUN] Would send recovery message:\n{rec_msg}")

        state["last_status"] = "UP"
        state["consecutive_failures"] = 0
        state["utopia_ok"] = True
        state["laya_ok"] = True
        save_state(state)
        return True
    else:
        state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
        last_alert_time = state.get("last_alert_time", 0)
        should_alert = (state.get("last_status") != "DOWN") or (now - last_alert_time > ALERT_COOLDOWN_SEC)

        if should_alert:
            logging.warning("Podroid services are DOWN. Dispatching downtime alert...")
            alert_msg = format_downtime_alert(host)
            if not dry_run:
                send_telegram(alert_msg)
            else:
                logging.info(f"[DRY-RUN] Would send downtime alert:\n{alert_msg}")
            state["last_alert_time"] = now

        state["last_status"] = "DOWN"
        state["utopia_ok"] = diag["utopia_ok"]
        state["laya_ok"] = diag["laya_ok"]
        save_state(state)
        return False


def daemon_loop(
    interval_sec: int = 120,
    host: str = DEFAULT_PODROID_HOST,
    utopia_port: int = DEFAULT_UTOPIA_PORT,
    laya_port: int = DEFAULT_LAYA_PORT,
    dry_run: bool = False
) -> None:
    """Continuous monitoring loop."""
    logging.info(f"Starting B-SDD Podroid Watchdog daemon (target: {host}, interval: {interval_sec}s)...")
    while True:
        try:
            run_once(host=host, utopia_port=utopia_port, laya_port=laya_port, dry_run=dry_run)
        except Exception as e:
            logging.error(f"Watchdog error in loop iteration: {e}")
        time.sleep(interval_sec)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="B-SDD Sovereign Podroid Watchdog")
    parser.add_argument("--host", default=DEFAULT_PODROID_HOST, help="Target Podroid host (default: 192.168.3.251)")
    parser.add_argument("--utopia-port", type=int, default=DEFAULT_UTOPIA_PORT, help="Utopia DB port (default: 9622)")
    parser.add_argument("--laya-port", type=int, default=DEFAULT_LAYA_PORT, help="Laya Decision Engine port (default: 9623)")
    parser.add_argument("--check", action="store_true", help="Run a single check and exit")
    parser.add_argument("--daemon", action="store_true", help="Run in continuous daemon mode")
    parser.add_argument("--interval", type=int, default=120, help="Daemon check interval in seconds (default: 120)")
    parser.add_argument("--dry-run", action="store_true", help="Do not send Telegram alerts (print to console)")
    args = parser.parse_args()

    if args.daemon:
        daemon_loop(args.interval, args.host, args.utopia_port, args.laya_port, args.dry_run)
    else:
        success = run_once(args.host, args.utopia_port, args.laya_port, args.dry_run)
        if args.check:
            sys.exit(0 if success else 1)
