#!/usr/bin/env bash
# ==============================================================================
# B-SDD SYNC SCRIPT: Host .161 (Orchestrator) <-> Host .234 (Legal Execution Node)
# Standard: B-SDD Methodology v1.2 (ADR-001..020)
# ==============================================================================

set -euo pipefail

REMOTE_HOST="192.168.3.234"
REMOTE_USER="vokov"
REMOTE_DIR="~/projects/b-sdd-legal"
LOCAL_LEGAL_DIR="/home/vokov/projects/b-sdd-legal"

echo "=== [B-SDD] Initiating Core Sync: .161 -> ${REMOTE_HOST} ==="

if [ -d "${LOCAL_LEGAL_DIR}" ]; then
  rsync -avz --exclude='.git' --exclude='node_modules' --exclude='dossier_benchmark' \
    "${LOCAL_LEGAL_DIR}/src" \
    "${LOCAL_LEGAL_DIR}/tests" \
    "${LOCAL_LEGAL_DIR}/.context" \
    "${LOCAL_LEGAL_DIR}/b-sdd-legal-ui" \
    "${LOCAL_LEGAL_DIR}/scripts" \
    "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/"

  echo "=== [B-SDD] Running Invariant Validation on Remote Node (.234) ==="
  ssh "${REMOTE_USER}@${REMOTE_HOST}" "cd ${REMOTE_DIR} && python3 -m unittest tests/test_legal_core.py"
  echo "=== [B-SDD] Sync and Remote Verification Complete! ==="
else
  echo "ERROR: Local legal directory ${LOCAL_LEGAL_DIR} not found!"
  exit 1
fi
