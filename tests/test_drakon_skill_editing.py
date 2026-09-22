"""
Unit Tests for DRAKON Skill Visual Round-Trip Editing & Synchronization.
Compliant with ADR-002 (Pure Stdlib Core), ADR-008 (DRAKON Invariants), and ADR-015.
"""
import io
import json
import tempfile
from pathlib import Path
import pytest

from src.core.drakon.skill_visual_bridge import (
    load_skill_drakon,
    save_skill_drakon,
    synthesize_drakon_schema,
    list_skills_dto,
)


def test_synthesize_drakon_schema():
    raw_md = """# Sample Skill

### Step 1: Initialize Workspace
Setup local repository environment.

### Step 2: Run Verification Loop
Call test-driven-development and safe-refactor to verify.

### Step 3: Emit Telemetry
Record operational metrics in Utopia DB.
"""
    meta = {
        "name": "sample-skill",
        "description": "A sample test skill",
        "type": "PROJECT_SKILL",
        "immutable": False,
    }
    schema = synthesize_drakon_schema("sample-skill", raw_md, meta)

    assert schema["schema_version"] == "1.0"
    assert schema["name"] == "sample-skill"
    nodes = schema["nodes"]
    assert len(nodes) >= 4

    # Verify Vertical Skewer X=0
    for node in nodes:
        assert node["x"] == 0.0

    assert nodes[0]["node_type"] == "headline"
    assert nodes[0]["node_id"] == "start"
    assert nodes[-1]["node_type"] == "end"
    assert nodes[-1]["node_id"] == "end"


def test_load_and_save_drakon_round_trip():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        skill_dir = tmp_path / "custom-workflow"
        skill_dir.mkdir(parents=True)

        md_file = skill_dir / "SKILL.md"
        md_file.write_text("""---
name: custom-workflow
description: Custom automated workflow.
type: PROJECT_SKILL
immutable: false
---

# Custom Workflow

### Step 1: Intake Task
Read inputs and evaluate risk.

### Step 2: Execute Patch
Run code refactoring.
""")

        # 1. Load: Should synthesize and persist custom-workflow.drakon.json
        schema = load_skill_drakon("custom-workflow", skills_dir=tmp_path)
        drakon_file = skill_dir / "custom-workflow.drakon.json"
        assert drakon_file.exists()
        assert schema["name"] == "custom-workflow"
        assert len(schema["nodes"]) >= 3

        # 2. Modify schema (visual edit simulation)
        schema["nodes"][1]["label"] = "MODIFIED: Intake Task with Guardrails"
        schema["nodes"][1]["semantic_binding"]["call_skill"] = "laya-decision-router"

        # 3. Save: Should update .drakon.json and synchronize SKILL.md
        res = save_skill_drakon("custom-workflow", schema, skills_dir=tmp_path)
        assert res["status"] == "ok"
        assert res["nodes_count"] == len(schema["nodes"])

        # Verify .drakon.json content
        saved_drakon = json.loads(drakon_file.read_text(encoding="utf-8"))
        assert saved_drakon["nodes"][1]["label"] == "MODIFIED: Intake Task with Guardrails"

        # Verify SKILL.md synchronization
        updated_md = md_file.read_text(encoding="utf-8")
        assert "<!-- DRAKON_VISUAL_FLOW_START -->" in updated_md
        assert "<!-- DRAKON_VISUAL_FLOW_END -->" in updated_md
        assert "MODIFIED: Intake Task with Guardrails" in updated_md
        assert "laya-decision-router" in updated_md


def test_system_skill_immutability_preservation_on_save():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        skill_dir = tmp_path / "b-sdd"
        skill_dir.mkdir(parents=True)

        md_file = skill_dir / "SKILL.md"
        md_file.write_text("""---
name: b-sdd
description: Enforces bitemporal architectural invariants.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
---

# b-sdd Playbook
""")

        schema = load_skill_drakon("b-sdd", skills_dir=tmp_path)

        # Attempt to save with immutable=false
        schema["meta"]["immutable"] = False
        schema["meta"]["skill_type"] = "PROJECT_SKILL"

        res = save_skill_drakon("b-sdd", schema, skills_dir=tmp_path)
        assert res["immutable"] is True

        # Check SKILL.md frontmatter remains SYSTEM_SKILL and immutable: true
        updated_md = md_file.read_text(encoding="utf-8")
        assert "type: SYSTEM_SKILL" in updated_md
        assert "immutable: true" in updated_md


def test_list_skills_dto_in_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        for s_name in ["skill-a", "skill-b"]:
            s_dir = tmp_path / s_name
            s_dir.mkdir()
            (s_dir / "SKILL.md").write_text(f"""---
name: {s_name}
description: Description for {s_name}
type: PROJECT_SKILL
---
# {s_name}
""")
            (s_dir / f"{s_name}.drakon.json").write_text("{}")

        dtos = list_skills_dto(skills_dir=tmp_path)
        assert len(dtos) == 2
        names = [d.name for d in dtos]
        assert "skill-a" in names
        assert "skill-b" in names
        for d in dtos:
            assert d.has_drakon_schema is True


def test_generate_pseudocode_from_drakon_adr016():
    from src.core.drakon.skill_visual_bridge import generate_pseudocode_from_drakon
    schema = {
        "name": "DeploySample",
        "nodes": [
            {"node_id": "start", "node_type": "headline", "label": "Start Deployment", "x": 0.0, "y": 0.0},
            {"node_id": "step_1", "node_type": "action", "label": "Run build", "instructions": "Execute build script", "x": 0.0, "y": 2.0},
            {
                "node_id": "cond_ok", "node_type": "question", "label": "Build succeeded?",
                "edges": {"down": "step_2", "right": "err_step"},
                "x": 0.0, "y": 4.0
            },
            {
                "node_id": "err_step", "node_type": "action", "label": "Handle build failure",
                "semantic_binding": {"call_skill": "diagnosing-bugs"},
                "x": 4.0, "y": 4.0
            },
            {
                "node_id": "step_2", "node_type": "insertion", "label": "Call ledger",
                "semantic_binding": {"call_skill": "utopia-intent-ledger"},
                "x": 0.0, "y": 6.0
            },
            {"node_id": "end", "node_type": "end", "label": "Completed", "x": 0.0, "y": 8.0}
        ]
    }
    pseudocode = generate_pseudocode_from_drakon("deploy-sample", schema)
    assert "ALGORITHM DeploySample" in pseudocode
    assert "BEGIN" in pseudocode
    assert "IF EvaluateCondition('Build succeeded?')" in pseudocode
    assert "BRANCH_RIGHT(X=4.0): Handle build failure" in pseudocode
    assert "CALL_SKILL(diagnosing-bugs, context)" in pseudocode
    assert "CALL_SKILL(utopia-intent-ledger, context)" in pseudocode
    assert "RETURN Success('Completed')" in pseudocode


def test_cloudflare_pages_expert_live_skill():
    from src.core.drakon.skill_visual_bridge import load_skill_drakon, USER_SKILLS_DIR
    schema = load_skill_drakon("cloudflare-pages-expert")
    assert schema["name"] in ("Cloudflare Pages Expert Pipeline", "cloudflare-pages-expert")
    assert len(schema["nodes"]) >= 6

    # Verify SKILL.md has ALGORITHM pseudocode and YAML frontmatter
    md_file = USER_SKILLS_DIR / "cloudflare-pages-expert" / "SKILL.md"
    assert md_file.exists()
    content = md_file.read_text(encoding="utf-8")
    assert "type: SYSTEM_SKILL" in content
    assert "category: bssd-system-skill" in content
    assert "immutable: true" in content
    assert "ALGORITHM DeployAstryxToCloudflarePages" in content

