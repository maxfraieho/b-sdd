#!/usr/bin/env bash
# ==============================================================================
# B-SDD Universal Pre-Flight Execution Hook
# Deterministically compiles active rules and launches AI agent
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[B-SDD] Running deterministic pre-flight compilation..."
python3 -m src.cli.main compile

WORDS=$(wc -w < .context/active_rules.md 2>/dev/null || echo "0")
echo "[B-SDD] Active rules compiled into .context/active_rules.md (${WORDS} words)"

# Launch AGY CLI or fallback to bash
if command -v agy >/dev/null 2>&1; then
    echo "[B-SDD] Launching Antigravity CLI..."
    exec agy "$@"
else
    echo "[B-SDD] Pre-flight complete. Agent environment ready."
fi
