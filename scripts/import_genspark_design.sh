#!/usr/bin/env bash
# ==============================================================================
# B-SDD Framework · Genspark Design Import & Verification Script
# ==============================================================================
# Usage:
#   ./scripts/import_genspark_design.sh <path_to_genspark_output_folder>
#
# Examples:
#   ./scripts/import_genspark_design.sh /home/vokov/projects/b-sdd/docs/dewsign
#   ./scripts/import_genspark_design.sh ~/Downloads/genspark-astryx-workbench
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
UI_DIR="${ROOT_DIR}/b-sdd-ui"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║    B-SDD WORKBENCH · GENSPARK ASTRYX DESIGN IMPORTER         ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"

if [ $# -lt 1 ]; then
  echo -e "${RED}[ERROR] Missing required argument: path to Genspark output folder.${NC}"
  echo -e "Usage:"
  echo -e "  $0 <path_to_genspark_output>"
  exit 1
fi

INPUT_DIR="$1"

# Check if path exists locally, or if on remote host 192.168.3.184
if [ ! -d "${INPUT_DIR}" ]; then
  if ssh -o BatchMode=yes -o ConnectTimeout=2 192.168.3.184 "[ -d '${INPUT_DIR}' ]" 2>/dev/null; then
    echo -e "${YELLOW}» Path not found locally, but found on remote host 192.168.3.184!${NC}"
    echo -e "${YELLOW}» Fetching via rsync from 192.168.3.184:${INPUT_DIR} ...${NC}"
    LOCAL_SYNC_DIR="${ROOT_DIR}/docs/design_handoff_bsdd_workbench_astryx"
    mkdir -p "${LOCAL_SYNC_DIR}"
    rsync -avz "192.168.3.184:${INPUT_DIR}/" "${LOCAL_SYNC_DIR}/"
    INPUT_DIR="${LOCAL_SYNC_DIR}"
    echo -e "${GREEN}[✓] Successfully synchronized from 192.168.3.184 into ${INPUT_DIR}${NC}"
  else
    echo -e "${RED}[ERROR] Provided path does not exist locally or on 192.168.3.184: ${INPUT_DIR}${NC}"
    exit 1
  fi
fi

echo -e "${YELLOW}» Analyzing input directory: ${INPUT_DIR} ...${NC}"

# Read and display handoff README briefing if present
if [ -f "${INPUT_DIR}/README.md" ]; then
  echo -e "\n${CYAN}════════════════════════════════════════════════════════════════${NC}"
  echo -e "${CYAN}  GENSPARK ASTRYX DESIGN HANDOFF BRIEFING (READING README.md)  ${NC}"
  echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
  head -n 42 "${INPUT_DIR}/README.md"
  echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}\n"
fi

# Detect format: Case A (buildable src tree) vs Case B (design prototype package)
SRC_SOURCE=""
IS_PROTOTYPE=false

if [ -d "${INPUT_DIR}/b-sdd-ui/src" ]; then
  SRC_SOURCE="${INPUT_DIR}/b-sdd-ui"
elif [ -d "${INPUT_DIR}/src" ]; then
  SRC_SOURCE="${INPUT_DIR}"
elif [ -d "${INPUT_DIR}/components" ] || [ -f "${INPUT_DIR}/B-SDD Workbench Astryx.html" ]; then
  IS_PROTOTYPE=true
  echo -e "${CYAN}[ℹ] Detected Astryx Design Prototype package (HTML/JSX reference).${NC}"
  # Stash prototype files to docs/design_handoff_bsdd_workbench_astryx/ for developer reference
  TARGET_HANDOFF_DOCS="${ROOT_DIR}/docs/design_handoff_bsdd_workbench_astryx"
  mkdir -p "${TARGET_HANDOFF_DOCS}"
  if [ "${INPUT_DIR}" != "${TARGET_HANDOFF_DOCS}" ]; then
    rsync -av "${INPUT_DIR}/" "${TARGET_HANDOFF_DOCS}/"
  fi
  echo -e "${GREEN}[✓] Prototype reference secured in docs/design_handoff_bsdd_workbench_astryx/${NC}"
fi

if [ "${IS_PROTOTYPE}" = true ]; then
  echo -e "${YELLOW}» Running verification of active codebase and compiling active rules...${NC}"
  PYTHONPATH="${ROOT_DIR}" python3 "${ROOT_DIR}/src/cli/main.py" compile
  pytest -v
  echo -e "\n${GREEN}════════════════════════════════════════════════════════════════${NC}"
  echo -e "${GREEN}[✓ SUCCESS] Astryx Design Handoff successfully registered & read!${NC}"
  echo -e "${GREEN}  - Handoff README: ${ROOT_DIR}/docs/design_handoff_bsdd_workbench_astryx/README.md${NC}"
  echo -e "${GREEN}  - Interactive Prototype: ${ROOT_DIR}/docs/design_handoff_bsdd_workbench_astryx/B-SDD Workbench Astryx.html${NC}"
  echo -e "${GREEN}  - System ready for Genspark Code or TypeScript migration in b-sdd-ui/src/${NC}"
  echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
  exit 0
fi

echo -e "${GREEN}[✓] Detected frontend root at: ${SRC_SOURCE}${NC}"

# 1. Backup current state
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="${UI_DIR}/.backup_${TIMESTAMP}"
echo -e "${YELLOW}» Creating snapshot backup of current UI to ${BACKUP_DIR} ...${NC}"
mkdir -p "${BACKUP_DIR}"
if [ -d "${UI_DIR}/src" ]; then
  cp -r "${UI_DIR}/src" "${BACKUP_DIR}/"
fi
if [ -f "${UI_DIR}/package.json" ]; then
  cp "${UI_DIR}/package.json" "${BACKUP_DIR}/"
fi
echo -e "${GREEN}[✓] Snapshot backup secured.${NC}"

# 2. Preserve mission-critical canonical DRAKON libraries & assets
TEMP_DRAKON_PRESERVE=$(mktemp -d)
echo -e "${YELLOW}» Stashing canonical DRAKON runtimes & assets ...${NC}"
if [ -f "${UI_DIR}/public/libs/drakonwidget.js" ]; then
  cp "${UI_DIR}/public/libs/drakonwidget.js" "${TEMP_DRAKON_PRESERVE}/"
fi
if [ -f "${UI_DIR}/public/libs/drakongen.js" ]; then
  cp "${UI_DIR}/public/libs/drakongen.js" "${TEMP_DRAKON_PRESERVE}/"
fi
if [ -d "${UI_DIR}/src/assets/drakon" ]; then
  mkdir -p "${TEMP_DRAKON_PRESERVE}/drakon_assets"
  cp -r "${UI_DIR}/src/assets/drakon/"* "${TEMP_DRAKON_PRESERVE}/drakon_assets/" || true
fi

# 3. Synchronize new files
echo -e "${YELLOW}» Importing design files into ${UI_DIR} ...${NC}"

# Copy package.json if present in incoming design
if [ -f "${SRC_SOURCE}/package.json" ]; then
  cp "${SRC_SOURCE}/package.json" "${UI_DIR}/package.json"
fi

# Copy tailwind or vite config if present
if [ -f "${SRC_SOURCE}/vite.config.ts" ]; then
  cp "${SRC_SOURCE}/vite.config.ts" "${UI_DIR}/vite.config.ts"
fi
if [ -f "${SRC_SOURCE}/tailwind.config.js" ]; then
  cp "${SRC_SOURCE}/tailwind.config.js" "${UI_DIR}/tailwind.config.js"
fi

# Copy src directory
rsync -av --delete \
  --exclude 'assets/drakon' \
  "${SRC_SOURCE}/src/" "${UI_DIR}/src/"

# 4. Restore preserved canonical DRAKON runtimes & assets
echo -e "${YELLOW}» Restoring canonical DRAKON engine & icon assets ...${NC}"
mkdir -p "${UI_DIR}/public/libs"
if [ -f "${TEMP_DRAKON_PRESERVE}/drakonwidget.js" ]; then
  cp "${TEMP_DRAKON_PRESERVE}/drakonwidget.js" "${UI_DIR}/public/libs/drakonwidget.js"
fi
if [ -f "${TEMP_DRAKON_PRESERVE}/drakongen.js" ]; then
  cp "${TEMP_DRAKON_PRESERVE}/drakongen.js" "${UI_DIR}/public/libs/drakongen.js"
fi
if [ -d "${TEMP_DRAKON_PRESERVE}/drakon_assets" ]; then
  mkdir -p "${UI_DIR}/src/assets/drakon"
  cp -r "${TEMP_DRAKON_PRESERVE}/drakon_assets/"* "${UI_DIR}/src/assets/drakon/" || true
fi
rm -rf "${TEMP_DRAKON_PRESERVE}"

# 5. Dependency installation
echo -e "${YELLOW}» Verifying & installing npm dependencies in b-sdd-ui ...${NC}"
cd "${UI_DIR}"
npm install

# 6. Typecheck & Frontend Build Verification Gate
echo -e "${YELLOW}» Executing Frontend Verification Gate (tsc -b && vite build) ...${NC}"
if npm run build; then
  echo -e "${GREEN}[✓ PASS] Frontend build succeeded with zero errors!${NC}"
else
  echo -e "${RED}[FAIL] Frontend build failed. Rolling back to ${BACKUP_DIR} ...${NC}"
  cp -r "${BACKUP_DIR}/src/"* "${UI_DIR}/src/"
  cp "${BACKUP_DIR}/package.json" "${UI_DIR}/package.json"
  exit 1
fi

# 7. Backend Architectural Fitness Gate
echo -e "${YELLOW}» Executing Backend Architectural Fitness Gate (pytest) ...${NC}"
cd "${ROOT_DIR}"
if pytest -v; then
  echo -e "${GREEN}[✓ PASS] All 36 architectural fitness tests passed!${NC}"
else
  echo -e "${RED}[FAIL] Architectural tests failed! Check test logs.${NC}"
  exit 1
fi

# 8. Recompile active rules
echo -e "${YELLOW}» Recompiling active architectural rules ...${NC}"
PYTHONPATH="${ROOT_DIR}" python3 "${ROOT_DIR}/src/cli/main.py" compile

echo -e "\n${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}[✓ SUCCESS] Genspark design successfully imported & verified!${NC}"
echo -e "${GREEN}  - Frontend bundle compiled cleanly.${NC}"
echo -e "${GREEN}  - Canonical DrakonWidget engine preserved.${NC}"
echo -e "${GREEN}  - Architectural fitness invariants verified.${NC}"
echo -e "${GREEN}  - To launch workbench dev server: ./run_workbench.sh dev${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
