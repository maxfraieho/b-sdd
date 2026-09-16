#!/usr/bin/env bash
# ==============================================================================
# B-SDD (Bitemporal Spec-Driven Development) Universal Agent Runner
# Orchestrates pre-flight rule compilation, architecture fitness gates,
# optional session distillation, dynamic sprint handoffs (ADR-007),
# auto-chaining, and dispatches to selectable AI agent harnesses.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Defaults
AGENT_HARNESS="${AGENT_HARNESS:-auto}"
SESSION_ID="${SESSION_ID:-}"
CONTINUE_SESSION=false
DO_DISTILL=false
DO_HANDOFF=false
AUTO_CHAIN=false
MAX_CHAIN_SPRINTS=3
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
  --handoff            Run session distillation, fitness gate, and handoff generation (ADR-007)
  --auto-chain [N]     Automatically chain up to N sprints using dynamic handoffs (default: 3)
  --skip-fitness       Skip pre-flight architecture fitness tests
  --skip-compile       Skip pre-flight active rule compilation
  --prompt <text>      Prompt to supply to the agent harness
  -h, --help           Show this help message

Examples:
  # Start a fresh new session with B-SDD compiled invariants:
  ./run_b_sdd.sh "Розпочати Milestone 1: Синхронізувати фронтенд та оновити бота"

  # Run standalone handoff generation:
  ./run_b_sdd.sh --handoff

  # Run with auto-chaining across up to 3 sprints:
  ./run_b_sdd.sh --auto-chain 3 "Реалізувати наступну чергу завдань"

  # Run non-interactively (print mode):
  ./run_b_sdd.sh --print "Перевірити стан модулів"
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
        --handoff)
            DO_HANDOFF=true
            shift
            ;;
        --auto-chain)
            AUTO_CHAIN=true
            DO_HANDOFF=true
            if [[ $# -ge 2 && "$2" =~ ^[0-9]+$ ]]; then
                MAX_CHAIN_SPRINTS="$2"
                shift 2
            else
                shift
            fi
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

# Standalone Handoff generation if requested without prompt
if [[ "$DO_HANDOFF" = true && "$AUTO_CHAIN" = false && -z "$USER_PROMPT" ]]; then
    echo "================================================================================"
    echo "▶ Standalone Handoff Generation (ADR-007)"
    echo "================================================================================"
    if [[ "$RUN_COMPILE" = true ]]; then
        python3 -m src.cli.main compile
    fi
    DISTILL_ID="${SESSION_ID:-}"
    if [[ -n "$DISTILL_ID" ]]; then
        python3 -m src.cli.main distill --session "$DISTILL_ID" --json || true
    else
        python3 -m src.cli.main distill --json || true
    fi
    if [[ "$RUN_FITNESS" = true ]]; then
        python3 -m src.cli.main fitness
    fi
    python3 -m src.cli.main handoff
    exit 0
fi

CURRENT_SPRINT=1
while [[ $CURRENT_SPRINT -le $MAX_CHAIN_SPRINTS ]]; do
    if [[ "$AUTO_CHAIN" = true ]]; then
        echo ""
        echo "================================================================================"
        echo "▶ Sprint $CURRENT_SPRINT / $MAX_CHAIN_SPRINTS: Pre-Flight Phase"
        echo "================================================================================"
    else
        echo "================================================================================"
        echo "▶ B-SDD (Bitemporal Spec-Driven Development) Pre-Flight Phase"
        echo "================================================================================"
    fi

    # 1. Pre-flight Compilation
    if [[ "$RUN_COMPILE" = true ]]; then
        echo "⚙ Compiling active bitemporal rules snapshot..."
        python3 -m src.cli.main compile
    fi

    # 2. Session Distillation
    if [[ "$DO_DISTILL" = true ]]; then
        DISTILL_ID="${SESSION_ID:-${AGY_CONVERSATION_ID:-}}"
        echo "📜 Distilling session..."
        if [[ -n "$DISTILL_ID" ]]; then
            python3 -m src.cli.main distill --session "$DISTILL_ID" --json || true
        else
            python3 -m src.cli.main distill --json || true
        fi
    fi

    # 3. Architecture Fitness Gate
    if [[ "$RUN_FITNESS" = true ]]; then
        echo "🛡 Verifying architecture fitness gates..."
        python3 -m src.cli.main fitness
    fi

    # Auto-detect harness
    ACTIVE_HARNESS="$AGENT_HARNESS"
    if [[ "$ACTIVE_HARNESS" == "auto" ]]; then
        if command -v agy >/dev/null 2>&1; then
            ACTIVE_HARNESS="agy"
        elif command -v claude >/dev/null 2>&1; then
            ACTIVE_HARNESS="claude"
        elif command -v codex >/dev/null 2>&1; then
            ACTIVE_HARNESS="codex"
        else
            echo "ℹ No external AI harness found in PATH. Defaulting to agy."
            ACTIVE_HARNESS="agy"
        fi
        echo "ℹ Selected harness: $ACTIVE_HARNESS"
    fi

    # Context injection prefix
    RULES_FILE="$SCRIPT_DIR/.context/active_rules.md"
    CONTEXT_PREFIX=""
    if [[ -f "$RULES_FILE" ]]; then
        CONTEXT_PREFIX="[B-SDD Invariants: Consult .context/active_rules.md for active architecture constraints]"
    fi

    FINAL_PROMPT=""
    if [[ -n "$USER_PROMPT" ]]; then
        if [[ "$USER_PROMPT" == *"[B-SDD Invariants:"* ]]; then
            FINAL_PROMPT="$USER_PROMPT"
        elif [[ -n "$CONTEXT_PREFIX" ]]; then
            FINAL_PROMPT="$CONTEXT_PREFIX $USER_PROMPT"
        else
            FINAL_PROMPT="$USER_PROMPT"
        fi
    fi

    echo ""
    echo "================================================================================"
    echo "▶ Dispatching to AI Agent Harness: [$ACTIVE_HARNESS]"
    echo "================================================================================"

    # If neither auto-chain nor handoff requested, we exec directly to replace shell
    if [[ "$AUTO_CHAIN" = false && "$DO_HANDOFF" = false ]]; then
        case "$ACTIVE_HARNESS" in
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
                echo "❌ Unsupported harness: $ACTIVE_HARNESS."
                exit 1
                ;;
        esac
    fi

    # Managed execution for handoff or auto-chain
    HARNESS_EXIT=0
    case "$ACTIVE_HARNESS" in
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
            set +e
            "${AGY_CMD[@]}"
            HARNESS_EXIT=$?
            set -e
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
            set +e
            "${CLAUDE_CMD[@]}"
            HARNESS_EXIT=$?
            set -e
            ;;
        codex)
            echo "🚀 Launching OpenAI Codex CLI..."
            set +e
            if [[ -n "$FINAL_PROMPT" ]]; then
                codex exec "$FINAL_PROMPT"
            else
                codex
            fi
            HARNESS_EXIT=$?
            set -e
            ;;
        *)
            echo "❌ Unsupported harness: $ACTIVE_HARNESS."
            exit 1
            ;;
    esac

    if [[ $HARNESS_EXIT -ne 0 ]]; then
        echo "⚠️ Agent process exited with non-zero status: $HARNESS_EXIT"
    fi

    # Post-Sprint Handoff Lifecycle (ADR-007)
    echo ""
    echo "================================================================================"
    echo "▶ Post-Sprint Lifecycle & Dynamic Handoff (ADR-007)"
    echo "================================================================================"
    python3 -m src.cli.main distill --json || true
    if [[ "$RUN_FITNESS" = true ]]; then
        python3 -m src.cli.main fitness
    fi
    python3 -m src.cli.main handoff

    if [[ "$AUTO_CHAIN" = false ]]; then
        break
    fi

    # Evaluate chaining termination conditions
    HANDOFF_FILE="$SCRIPT_DIR/.context/sprint_handoff.json"
    if [[ ! -f "$HANDOFF_FILE" ]]; then
        echo "❌ Handoff file not found at $HANDOFF_FILE. Stopping auto-chain."
        break
    fi

    PENDING_TASKS=$(python3 -c "import json; d=json.load(open('$HANDOFF_FILE')); print(len(d.get('pending_tasks', [])))" 2>/dev/null || echo "0")
    NEXT_CMD=$(python3 -c "import json; d=json.load(open('$HANDOFF_FILE')); print(d.get('next_sprint', {}).get('prompt', ''))" 2>/dev/null || echo "")

    if [[ "$PENDING_TASKS" -eq 0 ]]; then
        echo "🎉 All specification backlog tasks completed! Multi-sprint auto-chain finished."
        break
    fi

    if [[ -z "$NEXT_CMD" ]]; then
        echo "ℹ No subsequent sprint prompt synthesized. Stopping auto-chain."
        break
    fi

    CURRENT_SPRINT=$((CURRENT_SPRINT + 1))
    if [[ $CURRENT_SPRINT -gt $MAX_CHAIN_SPRINTS ]]; then
        echo "ℹ Reached maximum sprint iterations ($MAX_CHAIN_SPRINTS). Handoff ready for next run."
        break
    fi

    echo "🔄 Dynamic Handoff ready. Auto-chaining to Sprint $CURRENT_SPRINT / $MAX_CHAIN_SPRINTS..."
    USER_PROMPT="$NEXT_CMD"
    SESSION_ID=""
    CONTINUE_SESSION=false
    sleep 1
done
