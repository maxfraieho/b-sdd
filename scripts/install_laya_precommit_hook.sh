#!/usr/bin/env bash
# ==============================================================================
# B-SDD Fast-Path Pre-Commit & Diff Risk Gatekeeper Hook Installer
# Sprint 030 - Deliverable B (ADR-002, ADR-014)
# Integrates Laya System 1 pre-commit evaluation into .git/hooks/pre-commit
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"
HOOK_TARGET="$GIT_HOOKS_DIR/pre-commit"

usage() {
    cat <<EOF
Usage: bash scripts/install_laya_precommit_hook.sh [OPTIONS]

Options:
  --install      Install or overwrite the Laya pre-commit hook (default)
  --verify       Verify hook installation, permissions, and test diff evaluation
  --uninstall    Remove the Laya pre-commit hook
  -h, --help     Show this help message
EOF
    exit 0
}

verify_hook() {
    echo "================================================================================"
    echo "▶ Verifying Laya Fast-Path Pre-Commit Hook (Sprint 030)"
    echo "================================================================================"

    if [[ ! -f "$HOOK_TARGET" ]]; then
        echo "❌ Hook file not found at $HOOK_TARGET. Run with --install first."
        exit 1
    fi

    if [[ ! -x "$HOOK_TARGET" ]]; then
        echo "⚠️ Hook file exists but is not executable. Fixing permissions..."
        chmod +x "$HOOK_TARGET"
    fi
    echo "✓ Pre-commit hook exists and is executable at $HOOK_TARGET"

    # Test Gatekeeper execution with synthetic safe diff
    echo "⚙ Testing gatekeeper execution against synthetic safe diff..."
    SAFE_DIFF="diff --git a/docs/test_doc.md b/docs/test_doc.md
--- a/docs/test_doc.md
+++ b/docs/test_doc.md
@@ -1 +1 @@
-old doc
+verified new documentation"

    VERIFY_OUT=$(printf '%s' "$SAFE_DIFF" | python3 -m src.core.diff_risk_gatekeeper --diff-text "$SAFE_DIFF" 2>&1)
    echo "   $VERIFY_OUT"

    if [[ "$VERIFY_OUT" == *"Verdict=PROCEED"* ]]; then
        echo "✓ Fast-Path verification PASSED: Low-risk diff granted instant PROCEED."
    else
        echo "❌ Fast-Path verification failed unexpected verdict."
        exit 1
    fi

    # Test Gatekeeper execution against synthetic suspicious diff
    echo "⚙ Testing gatekeeper veto against synthetic suspicious diff..."
    SUSPICIOUS_DIFF="diff --git a/src/core/eval.py b/src/core/eval.py
new file mode 100644
--- /dev/null
+++ b/src/core/eval.py
@@ -0,0 +1,2 @@
+def hack():
+    eval('dangerous_input')"

    set +e
    VETO_OUT=$(python3 -m src.core.diff_risk_gatekeeper --diff-text "$SUSPICIOUS_DIFF" 2>&1)
    VETO_EXIT=$?
    set -e

    if [[ $VETO_EXIT -ne 0 && "$VETO_OUT" == *"Verdict=HALT_FOR_INSPECTION"* ]]; then
        echo "✓ Security gatekeeper veto PASSED: Suspicious diff correctly blocked (Exit code: $VETO_EXIT)."
    else
        echo "❌ Security gatekeeper veto failed to block suspicious diff."
        exit 1
    fi

    echo "================================================================================"
    echo "✓ All Laya Pre-Commit Hook verification gates PASSED (100% compliant)."
    echo "================================================================================"
    exit 0
}

uninstall_hook() {
    if [[ -f "$HOOK_TARGET" ]]; then
        rm -f "$HOOK_TARGET"
        echo "✓ Successfully uninstalled Laya pre-commit hook from $HOOK_TARGET"
    else
        echo "ℹ No pre-commit hook was present at $HOOK_TARGET."
    fi
    exit 0
}

install_hook() {
    mkdir -p "$GIT_HOOKS_DIR"

    cat << 'EOF' > "$HOOK_TARGET"
#!/usr/bin/env bash
# ==============================================================================
# B-SDD Laya Fast-Path Pre-Commit Hook (Sprint 030 - Vector 2)
# Evaluates staged diff risk using Laya System 1 (Pixel 7 :9623).
# Bypass with: git commit --no-verify  OR  LAYA_SKIP_PRECOMMIT=1 git commit
# ==============================================================================
set -euo pipefail

if [[ "${LAYA_SKIP_PRECOMMIT:-0}" == "1" ]]; then
    echo "ℹ LAYA_SKIP_PRECOMMIT=1 set. Skipping Laya pre-commit risk gate."
    exit 0
fi

# If no staged changes, pass through
if git diff --cached --quiet; then
    exit 0
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# Run Fast-Path Diff Risk Gatekeeper
set +e
python3 -m src.core.diff_risk_gatekeeper --cached
GATE_EXIT=$?
set -e

if [[ $GATE_EXIT -ne 0 ]]; then
    echo ""
    echo "================================================================================"
    echo "❌ [LAYA FAST-PATH PRE-COMMIT GATE]: Commit rejected due to risk assessment."
    echo "   To remediate: add test coverage or refactor mutations in staging."
    echo "   To force (Operator Override): git commit --no-verify"
    echo "================================================================================"
    exit $GATE_EXIT
fi

exit 0
EOF

    chmod +x "$HOOK_TARGET"
    echo "✓ Successfully installed Laya Fast-Path Pre-Commit Hook at: $HOOK_TARGET"
}

# CLI Argument handling
ACTION="install"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --verify)
            ACTION="verify"
            shift
            ;;
        --uninstall)
            ACTION="uninstall"
            shift
            ;;
        --install)
            ACTION="install"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

case "$ACTION" in
    verify)
        verify_hook
        ;;
    uninstall)
        uninstall_hook
        ;;
    install)
        install_hook
        ;;
esac
