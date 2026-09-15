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
SESSION_ID="${SESSION_ID:-}"
CONTINUE_SESSION=false
DO_DISTILL=false
RUN_FITNESS=true
RUN_COMPILE=true
PRINT_MODE=false
USER_PROMPT=""

# Usage help
usage() {
    cat <<EOF
Usage: ./run_b_sdd.sh [OPTIONS] [PROMPT...]

Options:
  --agent <name>       AI harness: 'agy', 'claude', 'codex', or 'auto' (default: auto)
  --new-session        Start a completely new clean session (default behavior)
  --session <id>       Resume a specific conversation ID
  --continue, -c       Resume the most recent conversation
  --print, -p          Run non-interactively and print response
  --distill            Run session distillation before invoking the agent
  --skip-fitness       Skip pre-flight architecture fitness tests
  --skip-compile       Skip pre-flight active rule compilation
  --prompt <text>      Prompt to supply to the agent harness
  -h, --help           Show this help message

Examples:
  # Start a fresh new session with B-SDD compiled invariants:
  ./run_b_sdd.sh "Розпочати Milestone 1: Синхронізувати фронтенд та оновити бота"

  # Run non-interactively (print mode):
  ./run_b_sdd.sh --print "Перевірити стан модулів"

  # Resume a specific session:
  ./run_b_sdd.sh --session 5eb693e8-b86f-40fc-a2c5-20a08128c6c6 "Продовжити розробку"
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
        --continue|-c)
            CONTINUE_SESSION=true
            shift
            ;;
        --new-session)
            SESSION_ID=""
            CONTINUE_SESSION=false
            shift
            ;;
        --print|-p)
            PRINT_MODE=true
            shift
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
    DISTILL_ID="${SESSION_ID:-${AGY_CONVERSATION_ID:-5eb693e8-b86f-40fc-a2c5-20a08128c6c6}}"
    echo "📜 Distilling session '$DISTILL_ID'..."
    python3 -m src.cli.main distill --session "$DISTILL_ID" --json
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
        elif [[ "$CONTINUE_SESSION" = true ]]; then
            AGY_CMD+=("--continue")
        fi

        if [[ -n "$FINAL_PROMPT" ]]; then
            if [[ "$PRINT_MODE" = true ]]; then
                AGY_CMD+=("-p" "$FINAL_PROMPT")
            else
                AGY_CMD+=("-i" "$FINAL_PROMPT")
            fi
        fi
        exec "${AGY_CMD[@]}"
        ;;
    claude)
        echo "🚀 Launching Claude Code CLI..."
        CLAUDE_CMD=("claude")
        if [[ "$CONTINUE_SESSION" = true ]]; then
            CLAUDE_CMD+=("-c")
        fi
        if [[ -n "$FINAL_PROMPT" ]]; then
            if [[ "$PRINT_MODE" = true ]]; then
                CLAUDE_CMD+=("-p" "$FINAL_PROMPT")
            else
                CLAUDE_CMD+=("$FINAL_PROMPT")
            fi
        fi
        exec "${CLAUDE_CMD[@]}"
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
