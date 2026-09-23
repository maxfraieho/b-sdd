"""
B-SDD MCP Gateway Toolkit: Procedural Skills Catalog & Rule of 2 Crystallizer.
Implements skills catalog inspection, system skills immutability verification,
and Rule of 2 procedural crystallization compliant with ADR-003 and ADR-015.
100% Pure Python Standard Library (ADR-002).
"""
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.drakon.skill_visual_bridge import (
    list_skills_dto,
    load_skill_drakon,
    verify_system_skills_immutability,
)
from src.core.skill_crystallizer import RuleOfTwoSkillCrystallizer


def inspect_skills_catalog(
    category: Optional[str] = None,
    search: Optional[str] = None,
    include_drakon: bool = False
) -> Dict[str, Any]:
    """
    Inspects the sovereign procedural skills inventory.
    Returns SkillDTO representations, system immutability flags, and optional DRAKON twin schemas.
    """
    try:
        dtos = list_skills_dto()
        results = []
        for dto in dtos:
            d = dto.to_dict()
            if category and d.get("category") != category:
                continue
            if search:
                s_lower = search.lower()
                name_match = s_lower in d.get("name", "").lower()
                desc_match = s_lower in d.get("description", "").lower()
                if not (name_match or desc_match):
                    continue
            if include_drakon:
                try:
                    drakon_schema = load_skill_drakon(dto.name)
                    d["drakon_schema"] = drakon_schema
                except Exception:
                    d["drakon_schema"] = None
            results.append(d)

        return {
            "status": "SUCCESS",
            "total_skills": len(results),
            "category_filter": category,
            "search_filter": search,
            "skills": results
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e)
        }


def crystallize_rule_of_two(
    pattern_id: str,
    title: str,
    description: str,
    instructions: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Enforces the ADR-003 'Rule of 2' mandate:
    Records an operational workflow observation. When observed >= 2 times,
    crystallizes into a persistent procedural skill under .pi/skills/<pattern_id>/SKILL.md.
    """
    try:
        crystallizer = RuleOfTwoSkillCrystallizer(
            skills_root=ROOT_DIR / ".pi" / "skills",
            ledger_path=ROOT_DIR / ".context" / "skill_pattern_counter.json"
        )
        res = crystallizer.record_pattern(
            pattern_id=pattern_id,
            title=title,
            description=description,
            instructions=instructions,
            metadata=metadata
        )
        return {
            "status": "SUCCESS",
            "pattern_id": res.get("pattern_id"),
            "crystallized": res.get("crystallized", False),
            "frequency": res.get("frequency", 1),
            "skill_path": res.get("skill_path"),
            "message": res.get("message")
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "pattern_id": pattern_id,
            "error": str(e)
        }


def verify_immutability() -> Dict[str, Any]:
    """
    Verifies that core system skills have not been deleted, mutated, or corrupted (ADR-015).
    """
    try:
        valid, violations = verify_system_skills_immutability()
        return {
            "status": "SUCCESS",
            "is_immutable_and_intact": valid,
            "violation_count": len(violations),
            "violations": violations,
            "summary": "All core system skills verified immutable and intact" if valid else f"{len(violations)} skill immutability violations detected"
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e)
        }


def get_tools_spec() -> List[Dict[str, Any]]:
    """Returns MCP tools catalog definition for toolkit_skills."""
    return [
        {
            "name": "skills_catalog_inspect",
            "description": "Inspects the sovereign procedural skills inventory and DRAKON visual schemas.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Optional category filter."},
                    "search": {"type": "string", "description": "Optional search term for name/description."},
                    "include_drakon": {"type": "boolean", "default": False, "description": "Include DRAKON schema."}
                }
            }
        },
        {
            "name": "skills_rule_of_two_crystallize",
            "description": "Records an operational workflow; crystallizes into a permanent skill on >= 2 repeats (ADR-003).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pattern_id": {"type": "string", "description": "Unique identifier for the procedure."},
                    "title": {"type": "string", "description": "Human-readable title."},
                    "description": {"type": "string", "description": "Concise description of the procedure."},
                    "instructions": {"type": "string", "description": "Operational instructions and steps."},
                    "metadata": {"type": "object", "description": "Optional metadata."}
                },
                "required": ["pattern_id", "title", "description", "instructions"]
            }
        },
        {
            "name": "skills_verify_immutability",
            "description": "Verifies that all 15 protected B-SDD system skills are intact and unmutated (ADR-015).",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    ]
