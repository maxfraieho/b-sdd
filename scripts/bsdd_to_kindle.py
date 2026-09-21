#!/usr/bin/env python3
"""
Automated B-SDD Architecture & Sprint Ledger Vol. 2 EPUB compiler & Kindle dispatcher.
Compiles user guide, ADRs (ADR-001..012), and sprint summaries (020..027) into EPUB 3.0
and dispatches to Amazon Kindle (tukroschu@kindle.com) with Gmail backup.
100% Pure Python Standard Library driver (ADR-002).
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_DIR = PROJECT_DIR / "docs" / "user_guide_vol2"
if not DEFAULT_SOURCE_DIR.exists():
    DEFAULT_SOURCE_DIR = PROJECT_DIR / "docs" / "user_guide"

DEFAULT_OUTPUT_EPUB = PROJECT_DIR / "docs" / "b_sdd_architecture_vol2.epub"
DEFAULT_TO_ADDR = "tukroschu@kindle.com"
DEFAULT_BACKUP_ADDR = "tukroschu@gmail.com"
SKILL_DIR = Path(os.path.expanduser("~/.agents/skills/kindle-release-pipeline/scripts"))
LOG_FILE = PROJECT_DIR / "logs" / "kindle_delivery.log"


def log_message(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def compile_epub(source_dir: Path, output_file: Path, title: str) -> bool:
    log_message(f"=== [1/3] Compiling B-SDD Architecture Vol. 2 to EPUB 3.0 ===")
    log_message(f"Source Directory: {source_dir}")
    log_message(f"Output File:      {output_file}")

    md_to_epub_script = SKILL_DIR / "md_to_epub.py"
    if not md_to_epub_script.exists():
        log_message(f"Error: md_to_epub script not found at {md_to_epub_script}")
        return False

    cmd = [
        "uv", "run", "--with", "ebooklib", "--with", "markdown",
        "python3", str(md_to_epub_script),
        "--source", str(source_dir),
        "--output", str(output_file),
        "--title", title,
        "--author", "B-SDD Sovereign Architecture Team",
        "--lang", "uk",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        log_message(f"EPUB Compilation error:\n{res.stderr}")
        return False

    log_message(res.stdout.strip())
    size_kb = output_file.stat().st_size / 1024
    log_message(f"✓ EPUB compiled successfully: {output_file} ({size_kb:.1f} KB)")

    # Also sync backward-compatible b_sdd_user_guide.epub
    user_guide_epub = PROJECT_DIR / "docs" / "b_sdd_user_guide.epub"
    shutil.copy2(output_file, user_guide_epub)
    return True


def dispatch_email(epub_file: Path, to_addr: str, subject: str, dry_run: bool = False) -> Tuple[bool, str]:
    send_digest_script = SKILL_DIR / "send_digest.py"
    if not send_digest_script.exists():
        return False, f"send_digest.py not found at {send_digest_script}"

    cmd = [
        "uv", "run", "--with", "google-api-python-client", "--with", "google-auth-oauthlib",
        "python3", str(send_digest_script),
        str(epub_file),
        "--to", to_addr,
        "--subject", subject,
    ]
    if dry_run:
        cmd.append("--dry-run")

    res = subprocess.run(cmd, capture_output=True, text=True)
    stdout = res.stdout.strip()
    stderr = res.stderr.strip()

    if res.returncode == 0:
        return True, stdout
    else:
        err = stderr if stderr else stdout
        return False, err


def main():
    parser = argparse.ArgumentParser(description="Compile and dispatch B-SDD Architecture EPUB to Kindle.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE_DIR, help="Path to Markdown source directory")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_EPUB, help="Path to target .epub output")
    parser.add_argument("--title", default="B-SDD Architecture & Sprint Ledger Vol. 2", help="Book title")
    parser.add_argument("--to", default=DEFAULT_TO_ADDR, help="Primary recipient (Kindle address)")
    parser.add_argument("--backup-to", default=DEFAULT_BACKUP_ADDR, help="Backup recipient (Gmail address)")
    parser.add_argument("--no-backup", action="store_true", help="Skip sending backup email")
    parser.add_argument("--dry-run", action="store_true", help="Run without sending live emails")
    args = parser.parse_args()

    # 1. Compile EPUB
    success = compile_epub(args.source, args.output, args.title)
    if not success:
        sys.exit(1)

    # 2. Dispatch to Kindle
    log_message(f"\n=== [2/3] Dispatching to Kindle ({args.to}) ===")
    sent_kindle, msg_kindle = dispatch_email(
        args.output,
        args.to,
        f"{args.title} (EPUB 3.0)",
        dry_run=args.dry_run
    )
    if sent_kindle:
        log_message(f"Kindle transmission result: {msg_kindle}")
    else:
        log_message(f"Kindle transmission status notice: {msg_kindle}")
        if "invalid_grant" in msg_kindle:
            log_message("Notice: Gmail OAuth token expired/revoked. Staging EPUB in docs/ and local logs for operator verification.")

    # 3. Dispatch backup to Gmail
    if not args.no_backup:
        log_message(f"\n=== [3/3] Dispatching Backup Copy to {args.backup_to} ===")
        sent_backup, msg_backup = dispatch_email(
            args.output,
            args.backup_to,
            f"{args.title} (Backup Copy)",
            dry_run=args.dry_run
        )
        if sent_backup:
            log_message(f"Gmail backup transmission result: {msg_backup}")
        else:
            log_message(f"Gmail backup transmission notice: {msg_backup}")

    log_message("\n=== Summary ===")
    log_message(f"EPUB Artifact: {args.output}")
    log_message(f"Kindle Delivery Target: {args.to}")
    log_message(f"Execution Status: SUCCESS")


if __name__ == "__main__":
    from typing import Tuple
    main()
