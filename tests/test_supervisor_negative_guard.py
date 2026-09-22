"""
Unit and Negative Guard Tests for B-SDD Supervisor (Anti-False-Positive Invariants).
Validates:
1. Exit code != 0 strictly marks status as FAILED and populates failed_command.
2. Zero tolerance for tracebacks, RefreshError, and connection errors in stderr.
3. Strict enforcement of Kindle postconditions (EPUB size & verified log status).
4. Elimination of tautological test counting (no fake 5/5 tests).
5. NotebookLM report generation guarantees FAILED status is never masked as SUCCESS.
100% Pure Python Standard Library (ADR-002).
"""
import os
import subprocess
import time
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from scripts.bsdd_supervisor import (
    execute_task_core,
    verify_task_postconditions,
    publish_report_to_notebooklm,
    find_latest_report,
)


@pytest.fixture(autouse=True)
def mock_laya_and_cluster():
    """Fast mock for Laya circuit breaker and cluster state to avoid network timeouts."""
    dummy_decision = {
        "domain": "core",
        "skills_formatted": "@b-sdd",
        "score": 1.0,
        "choice": "PROCEED",
        "fallback": True
    }
    with patch("scripts.bsdd_supervisor.check_cluster_state", return_value=(True, False, {})), \
         patch("scripts.bsdd_supervisor.laya_breaker.query_with_recovery", return_value=(dummy_decision, "LOCAL_HEURISTIC")), \
         patch("scripts.bsdd_supervisor.NotebookLmMcpClient.list_sources", return_value=[]):
        yield


def test_supervisor_fails_on_command_exit_code_nonzero(tmp_path):
    """Exit code != 0 must result in status='FAILED' and failed_command populated."""
    fake_repo = tmp_path / "repo"
    fake_repo.mkdir()
    (fake_repo / "run_b_sdd.sh").write_text("#!/bin/bash\nexit 1\n")
    (fake_repo / "run_b_sdd.sh").chmod(0o755)

    result = execute_task_core(
        instruction_name="OUTBOX_AGI_SPRINT_034_TEST_FAIL",
        sprint_id="sprint_034",
        correlation_id="test-fail-01",
        target_repo=str(fake_repo),
        timeout_seconds=5
    )

    assert result["status"] == "FAILED"
    assert result["failed"] is True
    assert "run_b_sdd.sh" in result["failed_command"]
    assert result["vector3_intent_score"] == 0.0
    assert result["dual_gate_passed"] is False


def test_supervisor_fails_on_unhandled_stderr_traceback():
    """Tracebacks or OAuth token errors in command stderr must trigger postcondition failure."""
    logs = [
        {
            "cmd": "python3 send_digest.py",
            "code": 0,
            "stdout": "",
            "stderr": "google.auth.exceptions.RefreshError: ('invalid_grant: Token has been expired or revoked.')"
        }
    ]

    ok, reason = verify_task_postconditions(
        sprint_id="sprint_034",
        instruction_name="OUTBOX_AGI_SPRINT_034_KINDLE_BOOK_DISPATCH",
        repo_dir="/tmp",
        logs=logs,
        t_start=time.time()
    )

    assert ok is False
    assert "Authentication failure" in reason or "invalid_grant" in reason


def test_supervisor_fails_on_kindle_postcondition_missing_epub(tmp_path):
    """Kindle task with missing EPUB artifact must fail postconditions."""
    repo_dir = tmp_path / "b-sdd"
    repo_dir.mkdir()
    logs_dir = repo_dir / "logs"
    logs_dir.mkdir()

    # Valid log entry, but no EPUB file exists
    (logs_dir / "kindle_delivery.log").write_text(
        f"[{time.strftime('%Y-%m-%d %H:%M:%SZ')}] Execution Status: SUCCESS\n"
    )

    logs = [{"cmd": "scripts/send_to_kindle.py", "code": 0, "stdout": "ok", "stderr": ""}]

    ok, reason = verify_task_postconditions(
        sprint_id="sprint_034",
        instruction_name="OUTBOX_AGI_SPRINT_034_KINDLE_BOOK_DISPATCH",
        repo_dir=str(repo_dir),
        logs=logs,
        t_start=time.time()
    )

    assert ok is False
    assert "No valid compiled EPUB" in reason


def test_supervisor_fails_on_kindle_postcondition_token_error_in_log(tmp_path):
    """Kindle task where kindle_delivery.log contains RefreshError must fail."""
    repo_dir = tmp_path / "b-sdd"
    repo_dir.mkdir()
    logs_dir = repo_dir / "logs"
    logs_dir.mkdir()

    # Generate a dummy EPUB > 30KB
    epub_path = repo_dir / "b_sdd_user_guide_sprint032.epub"
    epub_path.write_bytes(b"PK\x03\x04" + b"0" * 35000)

    # Log containing RefreshError
    (logs_dir / "kindle_delivery.log").write_text(
        f"[{time.strftime('%Y-%m-%d %H:%M:%SZ')}] google.auth.exceptions.RefreshError: ('invalid_grant: Token has been expired or revoked.')\n"
    )

    logs = [{"cmd": "scripts/send_to_kindle.py", "code": 0, "stdout": "ok", "stderr": ""}]

    ok, reason = verify_task_postconditions(
        sprint_id="sprint_034",
        instruction_name="OUTBOX_AGI_SPRINT_034_KINDLE_BOOK_DISPATCH",
        repo_dir=str(repo_dir),
        logs=logs,
        t_start=time.time()
    )

    assert ok is False
    assert "Gmail token error" in reason or "invalid_grant" in reason


def test_supervisor_succeeds_when_all_kindle_postconditions_met(tmp_path):
    """Kindle task with valid EPUB and SUCCESS delivery log passes postconditions."""
    repo_dir = tmp_path / "b-sdd"
    repo_dir.mkdir()
    logs_dir = repo_dir / "logs"
    logs_dir.mkdir()

    # Valid EPUB > 30KB
    epub_path = repo_dir / "b_sdd_user_guide_sprint032.epub"
    epub_path.write_bytes(b"PK\x03\x04" + b"0" * 40000)

    # Verified delivery entry
    (logs_dir / "kindle_delivery.log").write_text(
        f"[{time.strftime('%Y-%m-%d %H:%M:%SZ')}] Execution Status: SUCCESS (Verified Delivery to Amazon Send-to-Kindle)\n"
    )

    logs = [{"cmd": "scripts/send_to_kindle.py", "code": 0, "stdout": "SUCCESS", "stderr": ""}]

    ok, reason = verify_task_postconditions(
        sprint_id="sprint_034",
        instruction_name="OUTBOX_AGI_SPRINT_034_KINDLE_BOOK_DISPATCH",
        repo_dir=str(repo_dir),
        logs=logs,
        t_start=time.time()
    )

    assert ok is True
    assert reason == ""


def test_supervisor_no_tautological_test_numbers(tmp_path):
    """If no tests were executed, summary must report 0/0 tests, never fake 5/5."""
    fake_repo = tmp_path / "repo"
    fake_repo.mkdir()
    (fake_repo / "run_sprint_test.sh").write_text("#!/bin/bash\necho 'Done'\n")
    (fake_repo / "run_sprint_test.sh").chmod(0o755)

    with patch("scripts.bsdd_supervisor.find_sprint_commands", return_value=[str(fake_repo / "run_sprint_test.sh")]):
        result = execute_task_core(
            instruction_name="OUTBOX_AGI_SPRINT_TEST_SIMPLE",
            sprint_id="sprint_test",
            correlation_id="test-notauto-01",
            target_repo=str(fake_repo),
            timeout_seconds=5
        )

    assert result["tests_summary"]["total"] == 0
    assert result["tests_summary"]["passed"] == 0
    assert result["tests_summary"]["failed"] == 0


def test_publish_report_never_success_on_failed_status(tmp_path):
    """When status='FAILED', publish_report_to_notebooklm must use FAILED_REPORT title and failure content."""
    mock_client = MagicMock()
    mock_client.call_tool.return_value = {"status": "ok"}

    with patch("scripts.bsdd_supervisor.NotebookLmMcpClient", return_value=mock_client), \
         patch("scripts.bsdd_supervisor.PRIMARY_NOTEBOOKS", ["test-nb-id"]):
        synced, source_title = publish_report_to_notebooklm(
            sprint_id="sprint_034",
            instruction_name="OUTBOX_AGI_SPRINT_034_KINDLE_DISPATCH",
            status="FAILED",
            target_notebook_id="test-nb-id",
            target_repo=str(tmp_path),
            failed_cmd="Kindle postcondition failed"
        )

    assert "FAILED_REPORT" in source_title
    # Check payload sent to NotebookLM
    assert mock_client.call_tool.called
    call_args = mock_client.call_tool.call_args[0][1]
    assert "FAILED" in call_args["title"]
    assert "❌ FAILED" in call_args["content"]
    assert "Kindle postcondition failed" in call_args["content"]
