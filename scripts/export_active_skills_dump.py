#!/usr/bin/env python3
"""
B-SDD Active Skills Raw Dump Synthesizer for Gemini Spark Offload.
100% Pure Python Standard Library (ADR-002).
Iterates over all 59 active skills in ~/.agents/skills/, extracts their current
SKILL.md and existing .drakon.json files, and synthesizes an unambiguous,
structured plain-text dump for Gemini Spark in Google NotebookLM.
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

SKILLS_DIR = Path(os.path.expanduser("~/.agents/skills")).resolve()

# Classification based on ADR-015
SYSTEM_SKILLS = {
    "b-sdd",
    "b-sdd-sprint-closure",
    "intent-continuity",
    "laya-decision-router",
    "drakon-compiler",
    "utopia-intent-ledger",
    "session-distiller",
    "safe-refactor",
    "surgical-patch",
    "code-reviewer",
    "test-driven-development",
    "diagnosing-bugs",
    "investigate-first",
    "systematic-debugging",
    "root-cause-tracing",
    "astryx-scaffolder",
    "kindle-release-pipeline",
    "architecture-designer",
    "skill-creator",
    "skill-audit",
    "find-skills",
    "writing-skills",
    "writing-great-skills",
    "codebase-design",
    "improve-codebase-architecture",
    "testing-anti-patterns",
    "condition-based-waiting",
    "defense-in-depth",
    "verification-before-completion",
    "using-git-worktrees",
    "cloudflare-pages-expert",
    "b-sdd-notebooklm-sync",
    "b-sdd-kindle-docs",
    "b-sdd-ui-export",
}


def parse_frontmatter(content: str) -> Dict[str, str]:
    meta = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].splitlines():
                line = line.strip()
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip("'\"")
    return meta


def generate_skills_dump(output_path: Path) -> Tuple[int, int]:
    skills = sorted([
        d for d in SKILLS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    ], key=lambda x: x.name)

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

    header = f"""# B-SDD ACTIVE SKILLS RAW CORPUS FOR GEMINI SPARK STANDARDIZATION
================================================================================
Generated At      : {now_iso}
Source Directory  : {SKILLS_DIR}
Total Skills Count: {len(skills)}
Purpose           : Batch standardization to ADR-015 & ADR-016 Tripartite Standard
Target Engine     : Gemini Spark in Google NotebookLM
Format            : Plain Text with strict delimiters (<<< SKILL_START: <name> >>>)
================================================================================

## INSTRUCTIONS FOR GEMINI SPARK:
For each skill block below:
1. Re-structure SKILL.md per ADR-016 (Tripartite Standard):
   - YAML frontmatter with exact type (SYSTEM_SKILL vs PROJECT_SKILL) and immutability.
   - Architectural Context & Negative Invariants (WHAT MUST NEVER HAPPEN).
   - Canonical Algorithmic Pseudocode (ALGORITHM <SkillName> with TRY/ASSERT/IF/ELSE/CALL_SKILL/HALT_AND_DEGRADE).
   - DRAKON Visual Anchor (<!-- DRAKON_VISUAL_FLOW_START --> ... <!-- DRAKON_VISUAL_FLOW_END -->).
   - Operational CLI guide.
2. Re-synthesize <skill-name>.drakon.json:
   - 100% valid JSON isomorphic to the pseudocode.
   - Strict planar vertical skewer (X=0.0) for primary spine, right-branches (X=4.0) for error/degradation.
   - Correct node types: headline, action, question, insertion, end.
================================================================================

"""

    total_bytes = 0
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(header)
        total_bytes += len(header.encode("utf-8"))

        for idx, skill_dir in enumerate(skills, 1):
            skill_name = skill_dir.name
            skill_md_file = skill_dir / "SKILL.md"
            drakon_file = skill_dir / f"{skill_name}.drakon.json"

            skill_md_content = ""
            if skill_md_file.exists():
                try:
                    skill_md_content = skill_md_file.read_text(encoding="utf-8", errors="replace")
                except Exception as e:
                    skill_md_content = f"[ERROR READING SKILL.MD: {e}]"

            drakon_content = ""
            if drakon_file.exists():
                try:
                    drakon_content = drakon_file.read_text(encoding="utf-8", errors="replace")
                except Exception as e:
                    drakon_content = f"[ERROR READING DRAKON.JSON: {e}]"

            meta = parse_frontmatter(skill_md_content)
            is_sys = skill_name in SYSTEM_SKILLS or meta.get("type") == "SYSTEM_SKILL"
            skill_type = "SYSTEM_SKILL" if is_sys else "PROJECT_SKILL"
            immutable = "true" if is_sys else "false"

            skill_block = f"""
================================================================================
<<< SKILL_START: {skill_name} >>>
INDEX: {idx}/{len(skills)}
NAME: {skill_name}
CATEGORY: {meta.get("category", "bssd-system-skill" if is_sys else "bssd-project-skill")}
TYPE: {skill_type}
IMMUTABLE: {immutable}
--------------------------------------------------------------------------------
--- FILE: SKILL.md ---
{skill_md_content.strip()}
--------------------------------------------------------------------------------
--- FILE: {skill_name}.drakon.json ---
{drakon_content.strip()}
<<< SKILL_END: {skill_name} >>>
================================================================================
"""
            out.write(skill_block)
            total_bytes += len(skill_block.encode("utf-8"))

        stats = f"""
================================================================================
## SUMMARY CORPUS STATISTICS
Total Processed Skills: {len(skills)}
Total System Skills: {sum(1 for s in skills if s.name in SYSTEM_SKILLS)}
Total Project Skills: {sum(1 for s in skills if s.name not in SYSTEM_SKILLS)}
Corpus Size: {total_bytes:,} bytes ({total_bytes / (1024*1024):.2f} MB)
Timestamp: {now_iso}
================================================================================
"""
        out.write(stats)
        total_bytes += len(stats.encode("utf-8"))

    return len(skills), total_bytes


def main():
    parser = argparse.ArgumentParser(description="Export all 59 active skills into a single raw text corpus for Gemini Spark offloading")
    parser.add_argument("--output", type=str, default="active_skills_raw_dump.txt", help="Target output plain-text file")
    parser.add_argument("--sync-remote", action="store_true", help="Stage dump to remote host 192.168.3.184")
    args = parser.parse_args()

    out_file = Path(args.output).resolve()
    print(f"🚀 Compiling active skills dump from: {SKILLS_DIR}")
    count, size = generate_skills_dump(out_file)
    print(f"✅ Generated {out_file.name}: {size:,} bytes ({size / (1024*1024):.2f} MB) across {count} skills.")

    if args.sync_remote:
        print("🌐 Staging raw dump to host 192.168.3.184...")
        remote_dest = "vokov@192.168.3.184:/home/vokov/active_skills_raw_dump.txt"
        remote_copilot = "vokov@192.168.3.184:/home/vokov/notebooklm-agent-copilot/active_skills_raw_dump.txt"
        subprocess.run(["scp", "-o", "StrictHostKeyChecking=no", str(out_file), remote_dest], check=True)
        subprocess.run(["scp", "-o", "StrictHostKeyChecking=no", str(out_file), remote_copilot], check=True)
        print("✓ Staged to /home/vokov/ and /home/vokov/notebooklm-agent-copilot/ on .184")


if __name__ == "__main__":
    main()
