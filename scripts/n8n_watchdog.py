#!/usr/bin/env python3
"""
B-SDD n8n Watchdog & Health Monitor.
Periodically checks the health of https://n8n.exodus.pp.ua/healthz.
If unreachable or error status returned, sends an immediate Telegram alert to operator.
When service recovers, sends a recovery confirmation.
State is tracked in /tmp/n8n_watchdog_state.json to prevent alert storms.
"""
import argparse
import json
import logging
import os
import sys
import time
import urllib.request
import urllib.error

N8N_HEALTH_URL = "https://n8n.exodus.pp.ua/healthz"
TELEGRAM_BOT_TOKEN = "8717667434:AAFWddh_xwTfMVHW7puxrlIFprbO9m_Au7Y"
TELEGRAM_CHAT_ID = "6412868393"
STATE_FILE = "/tmp/n8n_watchdog_state.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def send_telegram(text: str) -> bool:
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(url, data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        logging.error(f"Failed to send Telegram alert: {e}")
        return False

def check_n8n_health() -> tuple[bool, str]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) B-SDD-Watchdog/1.0"
    }
    req = urllib.request.Request(N8N_HEALTH_URL, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            if resp.status == 200:
                return True, "HTTP 200 OK"
            return False, f"Unexpected status: {resp.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Connection Error: {e.reason}"
    except Exception as e:
        return False, f"Error: {e}"

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_status": "UP", "last_alert_time": 0}

def save_state(state: dict) -> None:
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        logging.error(f"Failed to save state: {e}")

def run_once() -> bool:
    state = load_state()
    is_up, reason = check_n8n_health()
    now = time.time()

    if is_up:
        logging.info(f"n8n health check PASSED: {reason}")
        if state.get("last_status") == "DOWN":
            msg = f"🟢 [RECOVERED: B-SDD n8n]\n\nСервіс n8n ({N8N_HEALTH_URL}) успішно відновив роботу.\nСтатус: {reason}"
            send_telegram(msg)
            state["last_status"] = "UP"
            save_state(state)
        return True
    else:
        logging.warning(f"n8n health check FAILED: {reason}")
        if state.get("last_status") != "DOWN" or (now - state.get("last_alert_time", 0) > 1800):
            msg = (
                f"🚨 [ALERT: B-SDD n8n DOWNTIME]\n\n"
                f"Сервіс n8n недоступний!\n"
                f"📍 URL: {N8N_HEALTH_URL}\n"
                f"❌ Причина: {reason}\n\n"
                f"Можливі причини:\n"
                f"• Збій тунелю cloudflared на Oracle VM (100.66.97.93)\n"
                f"• Перевантаження або падіння Docker-контейнера n8n\n"
                f"• Збій маршрутизації Tailscale / Edge"
            )
            send_telegram(msg)
            state["last_status"] = "DOWN"
            state["last_alert_time"] = now
            save_state(state)
        return False

def daemon_loop(interval_sec: int = 60) -> None:
    logging.info(f"Starting B-SDD n8n Watchdog daemon (interval: {interval_sec}s)...")
    while True:
        try:
            run_once()
        except Exception as e:
            logging.error(f"Unexpected error in watchdog loop: {e}")
        time.sleep(interval_sec)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="n8n Health Watchdog")
    parser.add_argument("--daemon", action="store_true", help="Run in continuous daemon mode")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    parser.add_argument("--check", action="store_true", help="Run a single check and exit")
    args = parser.parse_args()

    if args.check:
        success = run_once()
        sys.exit(0 if success else 1)
    elif args.daemon:
        daemon_loop(args.interval)
    else:
        run_once()
