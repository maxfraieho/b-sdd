@echo off
REM ============================================================================
REM B-SDD Universal Pre-Flight Execution Hook (Windows)
REM ============================================================================
echo [B-SDD] Running deterministic pre-flight compilation...
python -m src.cli.main compile

if exist "%APPDATA%\npm\agy.cmd" (
    echo [B-SDD] Launching Antigravity CLI...
    call "%APPDATA%\npm\agy.cmd" %*
) else (
    echo [B-SDD] Pre-flight complete. Agent environment ready.
)
