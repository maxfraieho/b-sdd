#!/usr/bin/env python3
"""
B-SDD Skills Frontmatter & DRAKON Schema Synchronizer.
Enforces ADR-015 (Skill Taxonomy, Immutability & DRAKON Invariant).
100% Pure Python Standard Library (ADR-002).
"""
import json
import os
import re
import sys
from pathlib import Path
from typing import Set

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.core.drakon.skill_visual_bridge import (
    load_skill_drakon,
    save_skill_drakon,
    parse_skill_frontmatter,
    KNOWN_SYSTEM_SKILLS,
    USER_SKILLS_DIR,
    PROJECT_SKILLS_DIR,
)


def process_skill_dir(skill_path: Path):
    if not skill_path.is_dir() or skill_path.name.startswith(("_", ".")):
        return

    skill_name = skill_path.name
    is_system = skill_name in KNOWN_SYSTEM_SKILLS

    md_file = skill_path / "SKILL.md"
    if not md_file.exists():
        return

    content = md_file.read_text(encoding="utf-8", errors="replace")
    meta, body = parse_skill_frontmatter(content)

    # Set taxonomy attributes
    if is_system:
        meta["type"] = "SYSTEM_SKILL"
        meta["category"] = "bssd-system-skill"
        meta["immutable"] = True
    else:
        if not meta.get("type"):
            meta["type"] = "PROJECT_SKILL"

    # Reconstruct frontmatter
    fm_lines = [
        "---",
        f"name: {meta.get('name') or skill_name}",
        f"description: {meta.get('description', '')}",
        f"type: {meta.get('type', 'PROJECT_SKILL')}",
        f"category: {meta.get('category', 'general')}",
        f"immutable: {'true' if meta.get('immutable') else 'false'}",
    ]
    if meta.get("invoked_skills"):
        fm_lines.append(f"invoked_skills: [{', '.join(meta['invoked_skills'])}]")
    fm_lines.append("---")
    new_content = "\n".join(fm_lines) + "\n" + body.lstrip()

    md_file.write_text(new_content, encoding="utf-8")

    # Load and save DRAKON schema (creates .drakon.json and verifies round-trip)
    schema = load_skill_drakon(skill_name, skills_dir=skill_path.parent)
    save_skill_drakon(skill_name, schema, skills_dir=skill_path.parent)


def sync_all():
    print("=" * 70)
    print("▶ Synchronizing B-SDD Skills Taxonomy and DRAKON Schemas (ADR-015)...")
    print("=" * 70)

    # 1. User skills dir
    if USER_SKILLS_DIR.exists():
        for item in sorted(USER_SKILLS_DIR.iterdir()):
            process_skill_dir(item)

    # 2. Project skills dir mirror
    if PROJECT_SKILLS_DIR.exists():
        for item in sorted(PROJECT_SKILLS_DIR.iterdir()):
            process_skill_dir(item)

    print("✓ All skills synchronized with ADR-015 taxonomy and paired DRAKON schemas.")


if __name__ == "__main__":
    sync_all()
