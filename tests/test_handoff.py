"""
Tests for B-SDD Multi-Session Sprint Chaining and Dynamic Handoff (ADR-007).
Validates handoff schema compliance, fitness gate enforcement,
task introspection, prompt synthesis, and multi-sprint chaining simulation.
"""
import os
import sys
import json
import tempfile
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.core.session_distiller import SessionDistiller
from src.cli.main import cmd_handoff


def test_handoff_schema_structure(tmp_path):
    """ADR-007 Invariant: sprint_handoff.json must satisfy machine-readable schema."""
    distiller = SessionDistiller(root_dir=ROOT)
    payload = distiller.generate_handoff(
        conversation_id="test-conv-abc",
        output_json=tmp_path / "sprint_handoff.json",
        output_md=tmp_path / "next_sprint.md",
        enforce_fitness=False
    )

    assert payload["schema_version"] == "1.0.0"
    assert payload["session_id"] == "test-conv-abc"
    assert "handoff-" in payload["handoff_id"]
    assert "timestamp" in payload
    assert "git" in payload
    assert "branch" in payload["git"]
    assert "commit" in payload["git"]
    assert isinstance(payload["git"]["dirty_files"], list)
    assert "fitness" in payload
    assert isinstance(payload["fitness"]["passed"], bool)
    assert isinstance(payload["completed_tasks"], list)
    assert isinstance(payload["pending_tasks"], list)
    assert isinstance(payload["modified_files"], list)
    assert "next_sprint" in payload
    assert "task_id" in payload["next_sprint"]
    assert "title" in payload["next_sprint"]
    assert "prompt" in payload["next_sprint"]
    assert "run_command" in payload["next_sprint"]

    # Verify written JSON file matches payload
    saved_json = json.loads((tmp_path / "sprint_handoff.json").read_text(encoding="utf-8"))
    assert saved_json["handoff_id"] == payload["handoff_id"]


def test_handoff_markdown_rendering(tmp_path):
    """ADR-007 Invariant: next_sprint.md must provide concise, actionable briefing."""
    distiller = SessionDistiller(root_dir=ROOT)
    md_path = tmp_path / "next_sprint.md"
    payload = distiller.generate_handoff(
        conversation_id="test-conv-xyz",
        output_json=tmp_path / "sprint_handoff.json",
        output_md=md_path,
        enforce_fitness=False
    )

    content = md_path.read_text(encoding="utf-8")
    assert "# Next Sprint Handoff Briefing (ADR-007)" in content
    assert payload["handoff_id"] in content
    assert "## 1. Upstream Work Summary" in content
    assert "## 2. Active Architectural Constraints" in content
    assert "## 3. Downstream Target (Sprint N+1)" in content
    assert "### Executable Dispatch Command" in content
    assert payload["next_sprint"]["run_command"] in content


def test_fitness_gate_blocks_handoff_on_failure(monkeypatch):
    """ADR-007 Invariant: Handoff cannot be generated if architectural fitness fails."""
    distiller = SessionDistiller(root_dir=ROOT)

    # Mock verify_fitness_status to return failure
    monkeypatch.setattr(
        distiller,
        "verify_fitness_status",
        lambda repo_dir=None: {
            "passed": False,
            "gate": "tests/test_architecture_fitness.py",
            "exit_code": 1,
            "details": "FAILED test_compile_latency_sub_50ms"
        }
    )

    with pytest.raises(RuntimeError) as exc_info:
        distiller.generate_handoff(enforce_fitness=True)

    assert "ADR-007 invariant violation" in str(exc_info.value)
    assert "Architectural fitness gate failed" in str(exc_info.value)


def test_find_tasks_introspection(tmp_path):
    """Tests discovery and segregation of completed vs pending tasks across specs."""
    specs_dir = tmp_path / "specs" / "001-feature"
    specs_dir.mkdir(parents=True)
    tasks_file = specs_dir / "tasks.md"
    tasks_file.write_text("""# Tasks: Feature 001

- [x] `task-001`: Implement core algorithm.
- [ ] `task-002`: Wire CLI command.
- [ ] `task-003`: Add integration tests.
""", encoding="utf-8")

    distiller = SessionDistiller(root_dir=tmp_path)
    res = distiller.find_tasks(repo_dir=tmp_path)

    assert len(res["completed"]) == 1
    assert res["completed"][0]["id"] == "task-001"
    assert len(res["pending"]) == 2
    assert res["pending"][0]["id"] == "task-002"
    assert res["pending"][1]["id"] == "task-003"
    assert res["next_task"]["id"] == "task-002"


def test_synthesize_next_sprint_prompt():
    """Validates invariant prefixing and command construction for downstream sprint."""
    distiller = SessionDistiller(root_dir=ROOT)
    next_task = {
        "id": "task-042",
        "description": "task-042: Build GraphQL adapter",
        "file": "specs/002/tasks.md"
    }

    res = distiller.synthesize_next_sprint(next_task)
    assert res["task_id"] == "task-042"
    assert "[B-SDD Invariants: Consult .context/active_rules.md for active architecture constraints]" in res["prompt"]
    assert "task-042: Build GraphQL adapter" in res["prompt"]
    assert res["run_command"].startswith("./run_b_sdd.sh --new-session")

    # Custom prompt override
    res_custom = distiller.synthesize_next_sprint(next_task, custom_prompt="Emergency hotfix for auth")
    assert "Emergency hotfix for auth" in res_custom["prompt"]


def test_cli_handoff_command_execution(tmp_path):
    """Tests main.py handoff CLI subcommand with custom file destinations."""
    json_dest = tmp_path / "custom_handoff.json"
    md_dest = tmp_path / "custom_briefing.md"

    class Args:
        session = "session-test-cli"
        prompt = "Custom CLI task prompt"
        spec = None
        output_json = str(json_dest)
        output_md = str(md_dest)
        skip_fitness = True

    cmd_handoff(Args())

    assert json_dest.exists()
    assert md_dest.exists()
    data = json.loads(json_dest.read_text(encoding="utf-8"))
    assert data["session_id"] == "session-test-cli"
    assert "Custom CLI task prompt" in data["next_sprint"]["prompt"]


def test_multi_sprint_chaining_simulation(tmp_path):
    """Simulates 3 consecutive sprints in an automated chain."""
    specs_dir = tmp_path / "specs" / "001-chain"
    specs_dir.mkdir(parents=True)
    tasks_file = specs_dir / "tasks.md"

    # Sprint 1 start state
    tasks_file.write_text("""# Tasks
- [ ] `task-001`: Step 1
- [ ] `task-002`: Step 2
""", encoding="utf-8")

    distiller = SessionDistiller(root_dir=tmp_path)

    # Sprint 1 completes task-001
    tasks_file.write_text("""# Tasks
- [x] `task-001`: Step 1
- [ ] `task-002`: Step 2
""", encoding="utf-8")

    handoff_1 = distiller.generate_handoff(
        conversation_id="sprint-1-id",
        repo_dir=tmp_path,
        output_json=tmp_path / "handoff_1.json",
        output_md=tmp_path / "next_1.md",
        enforce_fitness=False
    )
    assert handoff_1["next_sprint"]["task_id"] == "task-002"
    assert len(handoff_1["pending_tasks"]) == 1

    # Sprint 2 completes task-002
    tasks_file.write_text("""# Tasks
- [x] `task-001`: Step 1
- [x] `task-002`: Step 2
""", encoding="utf-8")

    handoff_2 = distiller.generate_handoff(
        conversation_id="sprint-2-id",
        repo_dir=tmp_path,
        output_json=tmp_path / "handoff_2.json",
        output_md=tmp_path / "next_2.md",
        enforce_fitness=False
    )
    assert handoff_2["next_sprint"]["task_id"] == "complete"
    assert len(handoff_2["pending_tasks"]) == 0
