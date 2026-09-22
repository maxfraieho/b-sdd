#!/usr/bin/env python3
"""B-SDD Send to Kindle script (Pure stdlib & n8n gateway fallback).

Complies with ADR-002 (pure stdlib).
Dispatches EPUB to Amazon Send-to-Kindle (tukroschu@kindle.com)
with zero CC and proper MIME application/epub+zip.
Primary Channel: https://n8n.exodus.pp.ua/webhook/dispatch-kindle-book
Fallback Channel: Remote Node 192.168.3.184 (send_digest.py)
"""
import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ENDPOINT = "https://n8n.exodus.pp.ua/webhook/dispatch-kindle-book"
DEFAULT_TO = "tukroschu@kindle.com"
DEFAULT_SUBJECT = "B-SDD Practical User Guide Sprint 032"


def log_delivery(epub_path: Path, to_addr: str, status: str, details: str = "") -> None:
    """Logs delivery attempt to logs/kindle_delivery.log."""
    try:
        # Resolve repo root
        root_dir = Path(__file__).resolve().parent.parent
        logs_dir = root_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / "kindle_delivery.log"
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
        size = epub_path.stat().st_size if epub_path.exists() else 0
        entry = (
            f"[{ts}] === B-SDD Kindle Delivery Dispatch ===\n"
            f"[{ts}] EPUB Artifact: {epub_path} ({size} bytes, {size/1024:.1f} KB)\n"
            f"[{ts}] Kindle Target: {to_addr}\n"
            f"[{ts}] Sender Address: tukroschu@gmail.com\n"
            f"[{ts}] Execution Status: {status}\n"
            f"[{ts}] Details: {details}\n\n"
        )
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        print(f"[-] Warning: Failed to write kindle_delivery.log: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Send EPUB to Kindle")
    parser.add_argument("--file", type=Path, required=True, help="Path to .epub file")
    parser.add_argument("--to", default=DEFAULT_TO, help="Target kindle address")
    parser.add_argument("--subject", default=DEFAULT_SUBJECT, help="Email subject")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run")
    args = parser.parse_args()

    epub_file = args.file
    if not epub_file.exists():
        print(f"[-] Error: File not found: {epub_file}", file=sys.stderr)
        log_delivery(epub_file, args.to, "FAILED", f"File not found: {epub_file}")
        sys.exit(1)

    if args.dry_run:
        print(f"[dry-run] Would dispatch {epub_file} ({epub_file.stat().st_size} bytes) -> {args.to}")
        sys.exit(0)

    print(f"[*] Dispatching {epub_file} to {args.to} via Kindle gateway...")

    # Call dispatch_kindle_book.sh if available
    script_sh = Path(__file__).resolve().parent / "dispatch_kindle_book.sh"
    if script_sh.exists():
        res = subprocess.run(
            ["bash", str(script_sh), str(epub_file), args.subject],
            capture_output=True,
            text=True,
        )
        print(res.stdout)
        if res.returncode == 0:
            log_delivery(epub_file, args.to, "SUCCESS", f"Delivered via dispatch_kindle_book.sh: {res.stdout.strip()}")
            return
        else:
            print(f"[-] Primary gateway failed: {res.stderr}", file=sys.stderr)
            # Fall through to fallback

    # Direct curl to n8n webhook
    res = subprocess.run(
        [
            "curl", "-s", "-w", "\n%{http_code}", "-X", "POST", DEFAULT_ENDPOINT,
            "-F", f"subject={args.subject}",
            "-F", f"data=@{epub_file};type=application/epub+zip",
        ],
        capture_output=True,
        text=True,
    )
    lines = res.stdout.strip().split("\n")
    http_code = lines[-1] if lines else "0"
    body = "\n".join(lines[:-1]) if len(lines) > 1 else ""

    if http_code == "200":
        print(f"[+] SUCCESS: Book delivered to Kindle! Response: {body}")
        log_delivery(epub_file, args.to, "SUCCESS", f"HTTP 200 via n8n: {body}")
        return

    # Fallback: remote node .184
    print(f"[-] n8n Gateway returned HTTP {http_code}. Attempting fallback to node 192.168.3.184...", file=sys.stderr)
    try:
        fb_res = subprocess.run(
            [
                "ssh", "-o", "ConnectTimeout=5", "vokov@192.168.3.184",
                f"cd /home/vokov/projects/send-to-kindle && python3 send_digest.py {epub_file} --to {args.to} --subject '{args.subject}'"
            ],
            capture_output=True,
            text=True,
        )
        if fb_res.returncode == 0:
            print(f"[+] SUCCESS: Delivered via node .184 fallback! Response: {fb_res.stdout.strip()}")
            log_delivery(epub_file, args.to, "SUCCESS", f"Delivered via .184 fallback: {fb_res.stdout.strip()}")
            return
        else:
            print(f"[-] Fallback to .184 also failed: {fb_res.stderr.strip()}", file=sys.stderr)
    except Exception as fb_err:
        print(f"[-] Fallback execution error: {fb_err}", file=sys.stderr)

    log_delivery(epub_file, args.to, "FAILED", f"Gateway HTTP {http_code}: {body}")
    sys.exit(1)


if __name__ == "__main__":
    main()
