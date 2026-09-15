#!/usr/bin/env bash
# ==============================================================================
# B-SDD (Bitemporal Spec-Driven Development) Universal Agent Runner
# Orchestrates pre-flight rule compilation, architecture fitness gates,
# optional session distillation, and dispatches to selectable AI agent harnesses.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Defaults
AGENT_HARNESS="${AGENT_HARNESS:-auto}"
SESSION_ID="${AGY_CONVERSATION_ID:-5eb693e8-b86f-40fc-a2c5-20a08128c6c6}"
DO_DISTILL=false
RUN_FITNESS=true
RUN_COMPILE=true
USER_PROMPT=""

# Usage help
usage() {
    cat <<EOF
Usage: ./run_b_sdd.sh [OPTIONS] [PROMPT...]

Options:
  --agent <name>       AI harness: 'agy', 'claude', 'codex', or 'auto' (default: auto)
  --session <id>       Session conversation ID for distillation or agy continuation
  --distill            Run session distillation before invoking the agent
  --skip-fitness       Skip pre-flight architecture fitness tests
  --skip-compile       Skip pre-flight active rule compilation
  --prompt <text>      Prompt to supply to the agent harness
  -h, --help           Show this help message

Examples:
  ./run_b_sdd.sh --agent agy --prompt "Implement ADR-021 tasks"
  ./run_b_sdd.sh --distill --agent auto "Align Telegram bot buttons with TMA"
  ./run_b_sdd.sh "Run pre-flight check and continue development"
EOF
    exit 0
}

# Parse command line arguments
POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --agent)
            AGENT_HARNESS="$2"
            shift 2
            ;;
        --session)
            SESSION_ID="$2"
            shift 2
            ;;
        --distill)
            DO_DISTILL=true
            shift
            ;;
        --skip-fitness)
            RUN_FITNESS=false
            shift
            ;;
        --skip-compile)
            RUN_COMPILE=false
            shift
            ;;
        --prompt)
            USER_PROMPT="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            POSITIONAL_ARGS+=("$1")
            shift
            ;;
    esac
done

if [[ -z "$USER_PROMPT" && ${#POSITIONAL_ARGS[@]} -gt 0 ]]; then
    USER_PROMPT="${POSITIONAL_ARGS[*]}"
fi

echo "================================================================================"
echo "▶ B-SDD (Bitemporal Spec-Driven Development) Pre-Flight Phase"
echo "================================================================================"

# 1. Pre-flight Compilation
if [[ "$RUN_COMPILE" = true ]]; then
    echo "⚙ Compiling active bitemporal rules snapshot..."
    python3 -m src.cli.main compile
fi

# 2. Session Distillation
if [[ "$DO_DISTILL" = true ]]; then
    if [[ -n "$SESSION_ID" ]]; then
        echo "📜 Distilling session '$SESSION_ID'..."
        python3 -m src.cli.main distill --session "$SESSION_ID" --json
    else
        echo "⚠ Warning: --distill requested but no session ID provided. Skipping."
    fi
fi

# 3. Architecture Fitness Gate
if [[ "$RUN_FITNESS" = true ]]; then
    echo "🛡 Verifying architecture fitness gates..."
    python3 -m src.cli.main fitness
fi

echo ""
echo "================================================================================"
echo "▶ Dispatching to AI Agent Harness: [$AGENT_HARNESS]"
echo "================================================================================"

# Auto-detect harness if set to auto
if [[ "$AGENT_HARNESS" == "auto" ]]; then
    if command -v agy >/dev/null 2>&1; then
        AGENT_HARNESS="agy"
    elif command -v claude >/dev/null 2>&1; then
        AGENT_HARNESS="claude"
    elif command -v codex >/dev/null 2>&1; then
        AGENT_HARNESS="codex"
    else
        echo "❌ No supported AI harness found (agy, claude, codex). Defaulting to agy."
        AGENT_HARNESS="agy"
    fi
    echo "ℹ Auto-detected harness: $AGENT_HARNESS"
fi

# Prepare context injection note
RULES_FILE="$SCRIPT_DIR/.context/active_rules.md"
CONTEXT_PREFIX=""
if [[ -f "$RULES_FILE" ]]; then
    CONTEXT_PREFIX="[B-SDD Invariants: Consult .context/active_rules.md for active architecture constraints]"
fi

FINAL_PROMPT=""
if [[ -n "$USER_PROMPT" ]]; then
    if [[ -n "$CONTEXT_PREFIX" ]]; then
        FINAL_PROMPT="$CONTEXT_PREFIX $USER_PROMPT"
    else
        FINAL_PROMPT="$USER_PROMPT"
    fi
fi

# Execute according to selected harness
case "$AGENT_HARNESS" in
    agy)
        echo "🚀 Launching Antigravity CLI (agy)..."
        AGY_CMD=("agy")
        if [[ -n "$SESSION_ID" ]]; then
            AGY_CMD+=("--conversation=$SESSION_ID")
        fi
        if [[ -n "$FINAL_PROMPT" ]]; then
            AGY_CMD+=("$FINAL_PROMPT")
        fi
        exec "${AGY_CMD[@]}"
        ;;
    claude)
        echo "🚀 Launching Claude Code CLI..."
        if [[ -n "$FINAL_PROMPT" ]]; then
            exec claude -p "$FINAL_PROMPT"
        else
            exec claude
        fi
        ;;
    codex)
        echo "🚀 Launching OpenAI Codex CLI..."
        if [[ -n "$FINAL_PROMPT" ]]; then
            exec codex exec "$FINAL_PROMPT"
        else
            exec codex
        fi
        ;;
    *)
        echo "❌ Unsupported harness: $AGENT_HARNESS. Supported: agy, claude, codex, auto."
        exit 1
        ;;
esac
