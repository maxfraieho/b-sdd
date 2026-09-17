#!/usr/bin/env bash
# ==============================================================================
# B-SDD Framework · Next Sprint Execution & Design Integration Command
# ==============================================================================
# Usage:
#   ./run_next_sprint.sh [path_to_genspark_output]
#
# Examples:
#   ./run_next_sprint.sh /home/vokov/projects/b-sdd/docs/dewsign
#   ./run_next_sprint.sh ~/Downloads/genspark_astryx_result
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     B-SDD SPRINT N+2 · ASTRYX WORKBENCH INTEGRATION          ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"

# Check for help flag
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  echo -e "Usage:"
  echo -e "  ${BOLD}./run_next_sprint.sh [path_to_genspark_output]${NC}"
  echo -e ""
  echo -e "Options:"
  echo -e "  path_to_genspark_output   Path to folder containing Genspark Astryx design export"
  echo -e "  -h, --help                Show this help message"
  exit 0
fi

# Check git branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -e "${YELLOW}» Current git branch: ${BOLD}${CURRENT_BRANCH}${NC}"

if [ "${CURRENT_BRANCH}" != "main" ]; then
  echo -e "${YELLOW}» Switching to main branch to match Genspark upstream...${NC}"
  git checkout main || git checkout -b main
fi

# Step 1: Design Import (if path provided)
if [ $# -ge 1 ] && [ -n "$1" ]; then
  GENSPARK_DIR="$1"
  echo -e "\n${CYAN}» Step 1: Importing Genspark Astryx Design from:${NC} ${GENSPARK_DIR}"
  "${SCRIPT_DIR}/scripts/import_genspark_design.sh" "${GENSPARK_DIR}"
else
  echo -e "\n${YELLOW}ℹ No Genspark design folder specified.${NC}"
  echo -e "  To import Genspark Astryx design, run:"
  echo -e "    ${BOLD}./run_next_sprint.sh <path_to_genspark_result>${NC}"
  echo -e "  Proceeding with current codebase verification..."
fi

# Step 2: Pre-Flight Rule Compilation Gate
echo -e "\n${CYAN}» Step 2: Running Deterministic Pre-Flight Rule Compilation...${NC}"
python3 "${SCRIPT_DIR}/src/cli/main.py" compile

# Step 3: Architectural Fitness Gate
echo -e "\n${CYAN}» Step 3: Executing B-SDD Architectural Invariants Gate (pytest)...${NC}"
pytest -v

# Step 4: Utopia DB Knowledge Base Sync
echo -e "\n${CYAN}» Step 4: Synchronizing Invariants with Sovereign Utopia DB...${NC}"
if python3 "${SCRIPT_DIR}/scripts/sync_utopia.py"; then
  echo -e "${GREEN}[✓ PASS] Utopia DB synchronization complete.${NC}"
else
  echo -e "${YELLOW}[WARN] Utopia DB not reachable directly; local fallback active.${NC}"
fi

# Step 5: Start Workbench Dev Server
echo -e "\n${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}[✓ READY] Sprint verification complete. Starting Workbench...${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
exec "${SCRIPT_DIR}/run_workbench.sh" dev
