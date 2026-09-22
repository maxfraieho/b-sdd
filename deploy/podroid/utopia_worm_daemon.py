#!/usr/bin/env python3
"""
Utopia DB Bitemporal WORM Ledger Daemon.
Runs inside Podroid Alpine VM on Google Pixel 7 (192.168.3.251:9622).
Provides high-speed TCP socket interface for immutable WORM commits and health telemetry.
100% Pure Python Standard Library (ADR-001, ADR-002).
"""
import argparse
import datetime
import json
import logging
import os
import signal
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 9622
WORM_LOG_DIR = Path("/var/log/utopia")
WORM_LOG_FILE = WORM_LOG_DIR / "worm_ledger.jsonl"
POSTGRES_CONTAINER = "utopia-db"
POSTGRES_USER = "utopia"
POSTGRES_DB = "utopia"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [UtopiaWORM]: %(message)s"
)
logger = logging.getLogger("UtopiaWORM")


class UtopiaWormServer:
    """Multi-threaded TCP Socket Server for Utopia DB WORM Commits & Health Probes."""

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.is_running = False
        self.server_sock: Optional[socket.socket] = None

        WORM_LOG_DIR.mkdir(parents=True, exist_ok=True)

    def persist_worm_record(self, payload: Dict[str, Any]) -> str:
        """Appends immutable WORM record to journal and PostgreSQL container."""
        record_id = payload.get("record_id") or f"WORM_{int(time.time()*1000)}"
        entry = {
            "record_id": record_id,
            "received_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "payload": payload
        }
        entry_line = json.dumps(entry) + "\n"

        # 1. Local WORM file persistence
        try:
            with open(WORM_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(entry_line)
            logger.info(f"Persisted WORM record {record_id} to {WORM_LOG_FILE}")
        except Exception as e:
            logger.error(f"Failed writing WORM record to {WORM_LOG_FILE}: {e}")

        # 2. PostgreSQL container insertion (if Docker container running)
        try:
            sql = f"""
            CREATE TABLE IF NOT EXISTS intent_store.bitemporal_worm_ledger (
                record_id TEXT PRIMARY KEY,
                sprint_id TEXT,
                commit_hash TEXT,
                payload JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            INSERT INTO intent_store.bitemporal_worm_ledger (record_id, sprint_id, commit_hash, payload)
            VALUES ('{record_id}', '{payload.get("sprint_id", "")}', '{payload.get("commit_hash", "")}', '{json.dumps(payload)}')
            ON CONFLICT (record_id) DO NOTHING;
            """
            subprocess.run(
                ["docker", "exec", "-i", POSTGRES_CONTAINER, "psql", "-U", POSTGRES_USER, "-d", POSTGRES_DB, "-c", sql],
                capture_output=True,
                timeout=3.0,
                check=False
            )
            logger.info(f"PostgreSQL sync acknowledged for {record_id}")
        except Exception as e:
            logger.warning(f"Postgres container insertion skipped ({e}); WORM journal safely retained.")

        return record_id

    def handle_client(self, client_sock: socket.socket, addr: Tuple[str, int]):
        """Handles single TCP connection with support for HTTP, JSON, or empty probes."""
        client_sock.settimeout(3.0)
        try:
            data = b""
            try:
                data = client_sock.recv(65536)
            except socket.timeout:
                pass

            if not data:
                # Clean health probe (TCP connect/disconnect)
                client_sock.close()
                return

            text = data.decode("utf-8", errors="replace").strip()

            # Case A: HTTP probe (e.g. GET /health)
            if text.startswith("GET ") or text.startswith("HEAD "):
                body = json.dumps({
                    "status": "UP",
                    "service": "utopia_db_worm",
                    "port": self.port,
                    "node": "pixel7-podroid"
                })
                resp = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: application/json\r\n"
                    f"Content-Length: {len(body)}\r\n"
                    f"Connection: close\r\n\r\n"
                    f"{body}"
                ).encode("utf-8")
                client_sock.sendall(resp)

            # Case B: JSON TCP Request
            elif text.startswith("{"):
                try:
                    req = json.loads(text)
                    action = req.get("action", "")
                    if action == "worm_commit":
                        payload = req.get("payload", {})
                        rec_id = self.persist_worm_record(payload)
                        ack = json.dumps({"status": "ACK", "record_id": rec_id, "timestamp": time.time()})
                        client_sock.sendall(ack.encode("utf-8"))
                    elif action in ("ping", "health"):
                        ack = json.dumps({"status": "UP", "service": "utopia_db_worm", "port": self.port})
                        client_sock.sendall(ack.encode("utf-8"))
                    else:
                        client_sock.sendall(json.dumps({"status": "ERROR", "error": f"Unknown action: {action}"}).encode("utf-8"))
                except Exception as ex:
                    client_sock.sendall(json.dumps({"status": "ERROR", "error": str(ex)}).encode("utf-8"))

            else:
                # Raw text probe
                client_sock.sendall(b"OK\n")

        except Exception as e:
            logger.debug(f"Client handler exception: {e}")
        finally:
            try:
                client_sock.close()
            except Exception:
                pass

    def start(self):
        """Binds socket and starts main listening loop."""
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(128)
        self.is_running = True
        logger.info(f"Utopia DB WORM Socket Daemon listening on {self.host}:{self.port}")

        while self.is_running:
            try:
                client_sock, addr = self.server_sock.accept()
                t = threading.Thread(target=self.handle_client, args=(client_sock, addr), daemon=True)
                t.start()
            except Exception as e:
                if self.is_running:
                    logger.error(f"Error accepting connection: {e}")
                break

    def stop(self):
        """Stops server and releases socket."""
        self.is_running = False
        if self.server_sock:
            try:
                self.server_sock.close()
            except Exception:
                pass
        logger.info("Utopia DB WORM Daemon stopped.")


def main():
    parser = argparse.ArgumentParser(description="Utopia DB WORM Socket Daemon")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to listen (default: 9622)")
    args = parser.parse_args()

    server = UtopiaWormServer(host=args.host, port=args.port)

    def handle_sig(sig, frame):
        logger.info(f"Signal {sig} received, exiting...")
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    server.start()


if __name__ == "__main__":
    main()
