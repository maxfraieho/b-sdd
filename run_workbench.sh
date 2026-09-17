#!/usr/bin/env bash
# ==============================================================================
# B-SDD Operator Workbench Orchestrator
# Launches the High-Density Engineering Cockpit (b-sdd-ui) & B-SDD Architecture Engine
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
C_RESET="\033[0m"
C_BOLD="\033[1m"
C_CYAN="\033[36m"
C_GREEN="\033[32m"
C_YELLOW="\033[33m"
C_RED="\033[31m"
C_BLUE="\033[34m"
C_MAGENTA="\033[35m"

log_info() {
    echo -e "${C_CYAN}[B-SDD WORKBENCH]${C_RESET} $1"
}

log_success() {
    echo -e "${C_GREEN}[✓ PASS]${C_RESET} $1"
}

log_warn() {
    echo -e "${C_YELLOW}[⚠ WARN]${C_RESET} $1"
}

log_error() {
    echo -e "${C_RED}[✗ ERROR]${C_RESET} $1" >&2
}

echo -e "${C_MAGENTA}${C_BOLD}"
cat << "EOF"
  ____        ____  ____  ____    ____  ____  ____  _____ _____ 
 | __ )      / ___||  _ \|  _ \  |  _ \|  _ \|  _ \|_   _|_   _|
 |  _ \ _____\___ \| | | | | | | | |_) | |_) | |_) | | |   | |  
 | |_) |_____|___) | |_| | |_| | |  __/|  _ <|  __/  | |   | |  
 |____/      |____/|____/|____/  |_|   |_| \_\_|     |_|   |_|  
           OPERATOR WORKBENCH · HIGH-DENSITY COCKPIT
EOF
echo -e "${C_RESET}"

# 1. Environment Verification
log_info "Verifying execution runtime prerequisites..."

command -v python3 >/dev/null 2>&1 || {
    log_error "python3 is required but not installed."
    exit 1
}

command -v node >/dev/null 2>&1 || {
    log_error "node is required but not installed."
    exit 1
}

command -v npm >/dev/null 2>&1 || {
    log_error "npm is required but not installed."
    exit 1
}

log_success "Runtime detected: Python $(python3 --version | cut -d' ' -f2), Node $(node -v)"

# 2. Pre-Flight Compilation Gate
log_info "Executing deterministic pre-flight rule compilation..."
python3 -m src.cli.main compile
log_success "Active rules compiled into .context/active_rules.md"

# 3. Automated Architectural Fitness Gate
log_info "Running B-SDD architectural fitness verification gate (pytest)..."
if command -v pytest >/dev/null 2>&1; then
    pytest -q tests/test_architecture_fitness.py
    log_success "All 5 architectural fitness invariants verified (<50ms compile, <500 words, zero 3rd-party in src/)"
else
    log_warn "pytest not found in PATH; skipping automated fitness verification."
fi

# 4. Workbench Assets Verification
WORKBENCH_DIR="$SCRIPT_DIR/b-sdd-ui"
if [ ! -d "$WORKBENCH_DIR" ]; then
    log_error "b-sdd-ui directory not found!"
    exit 1
fi

# Check canonical drakonwidget
if [ ! -f "$WORKBENCH_DIR/public/libs/drakonwidget.js" ]; then
    log_error "Canonical drakonwidget.js not found in public/libs/!"
    exit 1
fi
log_success "DrakonWidget canonical engine verified (/libs/drakonwidget.js)"

# 5. Launch Option Selection
MODE="${1:-dev}"

case "$MODE" in
    --build)
        log_info "Building production bundle for Cloudflare Pages..."
        cd "$WORKBENCH_DIR"
        npm run build
        log_success "Production bundle built in b-sdd-ui/dist/"
        ;;
    --preview)
        if [ ! -d "$WORKBENCH_DIR/dist" ]; then
            log_info "dist/ directory not found. Running build first..."
            cd "$WORKBENCH_DIR"
            npm run build
        fi
        log_info "Launching production preview server on http://localhost:4173 ..."
        cd "$WORKBENCH_DIR"
        npm run preview
        ;;
    --backend)
        log_info "Starting standalone B-SDD Backend Gateway on http://localhost:8765 ..."
        exec python3 -m src.cli.main serve --port 8765
        ;;
    dev|--dev|*)
        fuser -k 8765/tcp 5173/tcp 2>/dev/null || true
        log_info "Starting B-SDD Backend Gateway on http://localhost:8765 ..."
        python3 -m src.cli.main serve --port 8765 &
        SERVER_PID=$!
        trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT INT TERM

        log_info "Starting Vite interactive developer workbench on http://localhost:5173 ..."
        cd "$WORKBENCH_DIR"
        npm run dev -- --host
        ;;
esac

