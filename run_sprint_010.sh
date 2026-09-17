#!/usr/bin/env bash
set -euo pipefail
echo "⚡ [B-SDD] EXECUTING SPRINT 010: Astryx Design System Ergonomics & Mobile Parity"
test -f ".context/sprint_009_handoff.json"
cd b-sdd-ui && npm run build && cd ..
pytest -q tests/
echo "✅ [B-SDD] ALL REMEDIATION SPRINTS (007..010) COMPLETED AND VERIFIED 100%!"
