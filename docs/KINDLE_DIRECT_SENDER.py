# KINDLE DIRECT DIAGNOSTIC & SENDING MODULE
"""
Autonomous script to diagnose and execute real delivery of EPUB to Kindle.
Uses pure Python standard library (Invariant L-02).
"""
import os
import sys
import smtplib
import ssl
import json
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path

EPUB_PATH = Path("/home/vokov/projects/b-sdd-legal/build/dossier_legal_vaud_ed10.epub")
TARGET_KINDLE = "tukroschu@kindle.com"
BACKUP_EMAIL = "tukroschu@gmail.com"
N8N_WEBHOOK = "https://n8n.exodus.pp.ua/webhook/bsdd-supervisor-result"

def check_file():
    if not EPUB_PATH.exists():
        # Check fallback
        alt_path = Path("/home/vokov/projects/b-sdd-legal/test_dossier.epub")
        if alt_path.exists():
            return alt_path
        return None
    return EPUB_PATH

def send_via_n8n(epub_file: Path):
    try:
        with open(epub_file, "rb") as f:
            data = f.read()
        import base64
        b64_content = base64.b64encode(data).decode("utf-8")
        payload = {
            "event": "KINDLE_DISPATCH_REQUEST",
            "target": TARGET_KINDLE,
            "filename": epub_file.name,
            "file_size": len(data),
            "content_base64": b64_content
        }
        req = urllib.request.Request(
            N8N_WEBHOOK,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return True, f"n8n Webhook HTTP {resp.status}"
    except Exception as e:
        return False, f"n8n webhook error: {str(e)}"

def run():
    results = {}
    f = check_file()
    if not f:
        results["file_check"] = "FAILED: EPUB file not found in build/ or root"
        print(json.dumps(results))
        return
    results["file_found"] = str(f)
    results["file_size"] = f.stat().st_size
    
    # Try n8n relay
    n8n_ok, n8n_msg = send_via_n8n(f)
    results["n8n_dispatch"] = {"success": n8n_ok, "message": n8n_msg}
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run()
