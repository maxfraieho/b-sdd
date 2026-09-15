"""
Tests for B-SDD Session Distiller.
Enforces fast streaming parsing and markdown distillation.
"""
import tempfile
import json
from pathlib import Path
from src.core.session_distiller import SessionDistiller


def test_clean_user_content():
    distiller = SessionDistiller()
    raw = "<CONTEXT_SUMMARY>Old summary</CONTEXT_SUMMARY><USER_REQUEST>Fix UI footer links</USER_REQUEST>"
    cleaned = distiller._clean_user_content(raw)
    assert cleaned == "Fix UI footer links"


def test_extract_key_topics():
    distiller = SessionDistiller()
    reqs = [
        {"index": 1, "timestamp": "2026-09-15T10:00:00Z", "content": "Update ADR-001 and architecture"},
        {"index": 2, "timestamp": "2026-09-15T10:05:00Z", "content": "Fix mini-app button layout on screenshot"},
        {"index": 3, "timestamp": "2026-09-15T10:10:00Z", "content": "Need a privacy policy and about page"},
        {"index": 4, "timestamp": "2026-09-15T10:15:00Z", "content": "Sync data to utopia db"},
    ]
    topics = distiller._extract_key_topics(reqs)
    assert len(topics) == 4
    assert topics[0]["topic"] == "architecture"
    assert topics[1]["topic"] == "ui_ux"
    assert topics[2]["topic"] == "legal_privacy"
    assert topics[3]["topic"] == "utopia_db"


def test_distill_mock_session():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        conv_id = "test-conv-123"
        log_dir = tmp_path / "brain" / conv_id / ".system_generated" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        transcript_file = log_dir / "transcript.jsonl"

        lines = [
            {"type": "USER_INPUT", "source": "USER_EXPLICIT", "created_at": "2026-09-15T09:00:00Z", "content": "<USER_REQUEST>Refactor compiler</USER_REQUEST>"},
            {"type": "PLANNER_RESPONSE", "created_at": "2026-09-15T09:01:00Z", "tool_calls": [{"name": "write_to_file", "args": {"TargetFile": "/src/core/compiler.py"}}]},
            {"type": "USER_INPUT", "source": "USER_EXPLICIT", "created_at": "2026-09-15T09:02:00Z", "content": "<USER_REQUEST>Test fitness</USER_REQUEST>"},
        ]

        with open(transcript_file, "w", encoding="utf-8") as f:
            for l in lines:
                f.write(json.dumps(l) + "\n")

        distiller = SessionDistiller(app_data_dir=tmp_path)
        data = distiller.distill_agy_session(conv_id)

        assert data["conversation_id"] == conv_id
        assert data["total_steps"] == 3
        assert data["user_requests_count"] == 2
        assert "/src/core/compiler.py" in data["files_modified"]
        assert "write_to_file" in data["tools_used"]

        md = distiller.render_distilled_markdown(data)
        assert f"# Distilled Session Intelligence (B-SDD)" in md
        assert f"Refactor compiler" in md
