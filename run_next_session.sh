#!/usr/bin/env bash
# ==============================================================================
# B-SDD Next Session Orchestrator & Genspark Sync Gate
# Synchronizes remote git changes, validates B-SDD invariants, and launches Task-007
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
C_MAGENTA="\033[35m"

log_info() {
    echo -e "${C_CYAN}[NEXT-SESSION]${C_RESET} $1"
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
  ____        ____  ____  ____    ____  ____  ___ _   _ _____ 
 | __ )      / ___||  _ \|  _ \  / ___||  _ \|_ _| \ | |_   _|
 |  _ \ _____\___ \| | | | | | | \___ \| |_) || ||  \| | | |  
 | |_) |_____|___) | |_| | |_| |  ___) |  __/ | || |\  | | |  
 |____/      |____/|____/|____/  |____/|_|   |___|_| \_| |_|  
          DYNAMIC SPRINT DISPATCHER · GENSPARK SYNC GATE
EOF
echo -e "${C_RESET}"

# 1. Parse Optional Arguments
IMPORT_PATH=""
SKIP_PULL=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --import)
            IMPORT_PATH="$2"
            shift 2
            ;;
        --skip-pull)
            SKIP_PULL=true
            shift
            ;;
        -h|--help)
            cat << HELP_EOF
Usage: ./run_next_session.sh [OPTIONS]

Options:
  --import <file.zip|dir>   Import and overlay exported Genspark code into b-sdd-ui/
  --skip-pull               Skip git pull synchronization from origin/master
  -h, --help                Show this help message
HELP_EOF
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# 2. Synchronize Remote Repository
if [ "$SKIP_PULL" = false ]; then
    log_info "Synchronizing latest changes from GitHub (git pull origin master)..."
    if git pull origin master; then
        log_success "Git repository is up to date."
    else
        log_warn "Git pull encountered issues. Please inspect any merge conflicts."
    fi
fi

# 3. Handle Optional Genspark Import
if [ -n "$IMPORT_PATH" ]; then
    if [ ! -e "$IMPORT_PATH" ]; then
        log_error "Import target not found: $IMPORT_PATH"
        exit 1
    fi

    log_info "Importing Genspark assets from $IMPORT_PATH ..."
    if [[ "$IMPORT_PATH" == *.zip ]]; then
        TMP_DIR="$(mktemp -d)"
        unzip -q -o "$IMPORT_PATH" -d "$TMP_DIR"
        # Copy source and components preserving node_modules and drakonwidget.js
        cp -rn "$TMP_DIR"/* "$SCRIPT_DIR/b-sdd-ui/" 2>/dev/null || true
        rm -rf "$TMP_DIR"
    elif [ -d "$IMPORT_PATH" ]; then
        cp -rn "$IMPORT_PATH"/* "$SCRIPT_DIR/b-sdd-ui/" 2>/dev/null || true
    fi
    log_success "Genspark assets overlaid into b-sdd-ui/"
fi

# 4. Deterministic Pre-Flight Rule Compilation Gate
log_info "Executing B-SDD pre-flight compilation..."
python3 -m src.cli.main compile
log_success "Active rules compiled (<500 words strictly enforced)"

# 5. Automated Architecture Fitness Gate
log_info "Verifying architectural fitness invariants (pytest)..."
if command -v pytest >/dev/null 2>&1; then
    pytest -q tests/test_architecture_fitness.py
    log_success "Architecture fitness invariants: 100% PASSED"
else
    log_warn "pytest not found; skipping automated fitness verification."
fi

# 6. Read Next Sprint Target
DISPATCH_PROMPT="[B-SDD Invariants: Consult .context/active_rules.md for active architecture constraints] --mode continuous --task task-007: Connect workbench to local \`.context/\` and Utopia DB on \`.251\`. --spec specs/004-multi-session-handoff-and-drakon/tasks.md --rules .context/active_rules.md"

log_info "Ready to dispatch Task-007:"
echo -e "${C_YELLOW}${DISPATCH_PROMPT}${C_RESET}\n"

# 7. Invoke Universal Runner
log_info "Launching Universal B-SDD Agent Runner..."
exec ./run_b_sdd.sh --new-session "$DISPATCH_PROMPT"
