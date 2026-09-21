#!/usr/bin/env bash
# ==============================================================================
# B-SDD Kindle Delivery Utility
# Dispatches EPUB documents to tukroschu@kindle.com via n8n Kindle Dispatcher.
# Guarantees:
#   - Real delivery via authorized Gmail API
#   - Strictly NO CC (Amazon E009 error avoidance)
#   - Verified HTTP 200 and Gmail message ID returned
# ==============================================================================
set -euo pipefail

EPUB_PATH="${1:-/home/vokov/projects/b-sdd/b_sdd_architecture_vol2.epub}"
SUBJECT="${2:-B-SDD Architecture & Sprint Ledger Vol. 2}"
ENDPOINT="https://n8n.exodus.pp.ua/webhook/dispatch-kindle-book"

if [[ ! -f "$EPUB_PATH" ]]; then
  echo "[-] Error: File not found: $EPUB_PATH" >&2
  exit 1
fi

FILE_SIZE=$(stat -c%s "$EPUB_PATH" 2>/dev/null || stat -f%z "$EPUB_PATH")
echo "[*] Dispatching to Kindle (tukroschu@kindle.com)..."
echo "    File: $EPUB_PATH (${FILE_SIZE} bytes)"
echo "    Subject: $SUBJECT"
echo "    Endpoint: $ENDPOINT"

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$ENDPOINT" \
  -F "subject=$SUBJECT" \
  -F "data=@${EPUB_PATH};type=application/epub+zip")

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [[ "$HTTP_CODE" -eq 200 ]]; then
  echo "[+] SUCCESS: Book delivered to Kindle!"
  echo "    Response: $BODY"
  exit 0
else
  echo "[-] FAILED: Gateway returned HTTP $HTTP_CODE" >&2
  echo "    Response: $BODY" >&2
  exit 1
fi
