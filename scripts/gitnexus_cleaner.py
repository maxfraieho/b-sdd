#!/usr/bin/env python3
"""
B-SDD GitNexus Orphan Lock & Shadow Cleaner.
100% Pure Python Standard Library (ADR-002).
Removes orphaned locks and shadow journal files (lbug.shadow, lbug.wal.checkpoint)
from GitNexus / LadybugDB / KùzuDB both locally and on the remote AST indexing node (192.168.3.184).
"""
import os
import subprocess
import sys
from pathlib import Path
from typing import List

REMOTE_HOST = "192.168.3.184"
REMOTE_USER = "vokov"
REMOTE_PROJECT_PATH = "/home/vokov/projects/b-sdd"

LOCK_PATTERNS = [
    "lbug.shadow",
    "lbug.wal.checkpoint",
    "*.lock",
    "*.tmp",
]


def clean_local(target_dir: Path) -> List[Path]:
    cleaned = []
    gitnexus_dir = target_dir / ".gitnexus"
    if not gitnexus_dir.exists():
        return cleaned

    for pattern in LOCK_PATTERNS:
        for p in gitnexus_dir.glob(pattern):
            try:
                if p.is_file():
                    p.unlink()
                    cleaned.append(p)
            except Exception as e:
                print(f"[WARN] Failed to remove local lock {p}: {e}", file=sys.stderr)
    return cleaned


def clean_remote(host: str, user: str, remote_path: str) -> bool:
    remote_cmd = (
        f"find {remote_path}/.gitnexus -name 'lbug.shadow' -o -name 'lbug.wal.checkpoint' -o -name '*.lock' "
        f"2>/dev/null | xargs -r rm -v"
    )
    ssh_cmd = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=3",
        "-o", "StrictHostKeyChecking=no",
        f"{user}@{host}",
        remote_cmd
    ]
    try:
        res = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=10)
        if res.stdout.strip():
            print(f"[INFO] Remote lock cleanup ({host}):\n{res.stdout.strip()}")
        else:
            print(f"[INFO] No orphaned remote locks found on {host}.")
        return res.returncode == 0
    except Exception as e:
        print(f"[WARN] Remote lock cleanup failed: {e}", file=sys.stderr)
        return False


def main():
    root = Path(__file__).resolve().parent.parent
    print(f"🧹 Running GitNexus Cleaner for {root.name}...")
    local_removed = clean_local(root)
    if local_removed:
        print(f"[INFO] Cleaned {len(local_removed)} local lock(s): {[p.name for p in local_removed]}")
    else:
        print("[INFO] No local orphaned locks found.")

    clean_remote(REMOTE_HOST, REMOTE_USER, REMOTE_PROJECT_PATH)
    print("✓ GitNexus cleanup complete.")


if __name__ == "__main__":
    main()
