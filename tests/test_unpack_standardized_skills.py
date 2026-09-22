"""
Unit Tests for B-SDD Standardized Skills Unpacker Harness.
Compliant with ADR-002 (Pure Stdlib Core) and ADR-016 (Tripartite Skill Standard).
"""
import json
import tempfile
from pathlib import Path
import pytest

from scripts.unpack_standardized_skills import (
    parse_skill_corpus,
    validate_skill_md,
    validate_drakon_schema,
    unpack_skills,
)


def test_parse_and_validate_standardized_corpus(tmp_path):
    corpus_content = """
=== BSSD_STANDARDIZED_SKILL_START: sample-demo-skill ===
--- FILE: SKILL.md ---
---
name: sample-demo-skill
description: Demo skill for test suite.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [b-sdd]
---

# Sample Demo Skill

## 1. Architectural Context & Negative Invariants
- NEVER fail silently.

## 2. Algorithmic Workflow (ADR-016 Standard)
ALGORITHM ExecuteSampleDemoSkill
INPUT:
    param: str
OUTPUT:
    status: str

BEGIN
    TRY
        ASSERT param != ""
        RETURN "SUCCESS"
    CATCH Error AS e
        HALT_AND_DEGRADE(e.Message)
    END
END

<!-- DRAKON_VISUAL_FLOW_START -->
## DRAKON Visual Workflow (Planar Skewer X=0)
  1. [HEADLINE] Start
  2. [END] End
<!-- DRAKON_VISUAL_FLOW_END -->

--- FILE: sample-demo-skill.drakon.json ---
{
  "schema_version": "1.0",
  "name": "Sample Demo Skill",
  "category": "bssd_system_skill",
  "description": "Demo schema",
  "params": "param: str",
  "nodes": [
    {
      "node_id": "start",
      "node_type": "headline",
      "label": "Start",
      "edges": {"down": "end", "right": null},
      "x": 0.0,
      "y": 0.0
    },
    {
      "node_id": "end",
      "node_type": "end",
      "label": "End",
      "edges": {"down": null, "right": null},
      "x": 0.0,
      "y": 2.0
    }
  ]
}
=== BSSD_STANDARDIZED_SKILL_END: sample-demo-skill ===
"""
    corpus_file = tmp_path / "standardized_corpus.txt"
    corpus_file.write_text(corpus_content, encoding="utf-8")

    parsed = parse_skill_corpus(corpus_file)
    assert len(parsed) == 1
    assert parsed[0]["name"] == "sample-demo-skill"

    md_ok, md_errs = validate_skill_md(parsed[0]["name"], parsed[0]["skill_md"])
    assert md_ok is True
    assert len(md_errs) == 0

    drakon_dict = json.loads(parsed[0]["drakon_raw"])
    j_ok, j_errs = validate_drakon_schema(parsed[0]["name"], drakon_dict)
    assert j_ok is True
    assert len(j_errs) == 0

    # Dry-run unpacking
    res = unpack_skills(corpus_file, dry_run=True)
    assert res["total"] == 1
    assert res["valid"] == 1
    assert res["failed"] == 0
