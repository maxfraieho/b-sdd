"""
Unit Tests for B-SDD Skill Taxonomy, Immutability & Non-Deletion Barrier.
Compliant with ADR-002 (Pure Stdlib Core) and ADR-015 (Skill Taxonomy & Immutability).
"""
import json
import shutil
import tempfile
from pathlib import Path
import pytest

from src.core.dto.skills import SkillDTO, SkillsResponseDTO, SkillType
from src.core.drakon.skill_visual_bridge import (
    parse_skill_frontmatter,
    list_skills_dto,
    verify_system_skills_immutability,
    KNOWN_SYSTEM_SKILLS,
)


def test_skill_dto_serialization():
    dto = SkillDTO(
        name="test-system-skill",
        description="A critical system skill.",
        skill_type=SkillType.SYSTEM_SKILL.value,
        category="bssd-system-skill",
        immutable=True,
        has_drakon_schema=True,
        invoked_skills=["safe-refactor", "test-driven-development"],
        drakon_path="/path/to/test-system-skill.drakon.json",
        skill_md_path="/path/to/SKILL.md",
    )
    assert dto.is_system_skill() is True
    data = dto.to_dict()
    assert data["name"] == "test-system-skill"
    assert data["skill_type"] == "SYSTEM_SKILL"
    assert data["immutable"] is True
    assert len(data["invoked_skills"]) == 2

    reconstructed = SkillDTO.from_dict(data)
    assert reconstructed.name == dto.name
    assert reconstructed.is_system_skill() is True
    assert reconstructed.has_drakon_schema is True


def test_skills_response_dto_counts():
    skills = [
        SkillDTO(name="s1", skill_type=SkillType.SYSTEM_SKILL.value, immutable=True),
        SkillDTO(name="s2", skill_type=SkillType.SYSTEM_SKILL.value, immutable=True),
        SkillDTO(name="p1", skill_type=SkillType.PROJECT_SKILL.value, immutable=False),
    ]
    resp = SkillsResponseDTO.from_skills_list(skills)
    assert resp.total == 3
    assert resp.system_skills_count == 2
    assert resp.project_skills_count == 1
    d = resp.to_dict()
    assert len(d["skills"]) == 3
    assert d["system_skills_count"] == 2


def test_parse_skill_frontmatter_system():
    raw_md = """---
name: b-sdd
description: Enforces bitemporal architectural invariants.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [safe-refactor, test-driven-development]
---

# Instruction body
Instructions follow here.
"""
    meta, body = parse_skill_frontmatter(raw_md)
    assert meta["name"] == "b-sdd"
    assert meta["type"] == SkillType.SYSTEM_SKILL.value
    assert meta["category"] == "bssd-system-skill"
    assert meta["immutable"] is True
    assert meta["invoked_skills"] == ["safe-refactor", "test-driven-development"]
    assert "Instruction body" in body


def test_parse_skill_frontmatter_project():
    raw_md = """---
name: my-domain-skill
description: Custom business logic helper.
type: PROJECT_SKILL
category: domain
immutable: false
---

# Project instructions
"""
    meta, body = parse_skill_frontmatter(raw_md)
    assert meta["name"] == "my-domain-skill"
    assert meta["type"] == SkillType.PROJECT_SKILL.value
    assert meta["immutable"] is False


def test_verify_system_skills_immutability_live():
    """Live check against ~/.agents/skills ensures 100% compliance with ADR-015."""
    valid, violations = verify_system_skills_immutability()
    assert valid is True, f"System skill violations found: {violations}"
    assert len(violations) == 0


def test_verify_system_skills_immutability_detects_tampering():
    """Simulates a missing or mutated system skill in a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        skill_dir = tmp_path / "b-sdd"
        skill_dir.mkdir(parents=True)

        # 1. Missing SKILL.md
        valid, violations = verify_system_skills_immutability(
            skills_dir=tmp_path,
            expected_system_skills=["b-sdd"]
        )
        assert valid is False
        assert any("MISSING_SKILL_MD" in v for v in violations)

        # 2. Add SKILL.md without immutable: true
        (skill_dir / "SKILL.md").write_text("""---
name: b-sdd
type: PROJECT_SKILL
immutable: false
---
body
""")
        valid, violations = verify_system_skills_immutability(
            skills_dir=tmp_path,
            expected_system_skills=["b-sdd"]
        )
        assert valid is False
        assert any("MUTABLE_SYSTEM_SKILL" in v for v in violations)
        assert any("MISSING_DRAKON_SCHEMA" in v for v in violations)

        # 3. Add immutable: true and valid drakon file -> passes!
        (skill_dir / "SKILL.md").write_text("""---
name: b-sdd
type: SYSTEM_SKILL
immutable: true
---
body
""")
        (skill_dir / "b-sdd.drakon.json").write_text(json.dumps({
            "schema_version": "1.0",
            "name": "b-sdd",
            "nodes": []
        }))
        valid, violations = verify_system_skills_immutability(
            skills_dir=tmp_path,
            expected_system_skills=["b-sdd"]
        )
        assert valid is True
        assert len(violations) == 0
