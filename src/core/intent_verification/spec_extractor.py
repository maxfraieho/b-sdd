"""
Spec Intent Extractor.
Parses ALGORITHM pseudocode and .drakon.json diagrams to build formal IntentGraphDTO.
Compliant with ADR-002 (Pure Stdlib Core) and ADR-016 (Tripartite Skill Architecture).
100% Pure Python Standard Library.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.core.dto.intent_verification import IntentGraphDTO


class SpecIntentExtractor:
    """Extracts formal intent, invariants, calls, and branching from skills specifications."""

    def __init__(self):
        pass

    def extract_from_skill_dir(self, skill_dir: Union[str, Path]) -> IntentGraphDTO:
        """
        Parses both SKILL.md and companion .drakon.json in a skill directory.
        """
        dir_path = Path(skill_dir).resolve()
        skill_name = dir_path.name
        md_file = dir_path / "SKILL.md"
        
        # Look for drakon json file matching skill_name or any .drakon.json
        drakon_files = list(dir_path.glob("*.drakon.json"))
        drakon_file = drakon_files[0] if drakon_files else None

        md_content = md_file.read_text(encoding="utf-8") if md_file.exists() else ""
        drakon_data = {}
        if drakon_file and drakon_file.exists():
            try:
                drakon_data = json.loads(drakon_file.read_text(encoding="utf-8"))
            except Exception:
                drakon_data = {}

        return self.extract_from_content(skill_name, md_content, drakon_data)

    def extract_from_content(
        self,
        skill_name: str,
        skill_md_text: str,
        drakon_data: Optional[Dict[str, Any]] = None
    ) -> IntentGraphDTO:
        """
        Extracts intent graph elements from markdown text and drakon json dictionary.
        """
        drakon = drakon_data or {}
        assert_statements: List[str] = []
        call_skills: List[str] = []
        branch_conditions: List[str] = []
        invariants: List[str] = []

        # 1. Extract pseudocode block
        pseudocode_match = re.search(
            r"<!--\s*ALGORITHMIC_PSEUDOCODE_START\s*-->(.*?)<!--\s*ALGORITHMIC_PSEUDOCODE_END\s*-->",
            skill_md_text,
            re.DOTALL | re.IGNORECASE
        )
        if pseudocode_match:
            algo_text = pseudocode_match.group(1)
        else:
            # Fallback to general ALGORITHM code block
            algo_block = re.search(r"```(?:text|pseudocode|algorithm)?\s*(ALGORITHM\s+.*?)```", skill_md_text, re.DOTALL | re.IGNORECASE)
            algo_text = algo_block.group(1) if algo_block else skill_md_text

        # 2. Parse Assertions
        for line in algo_text.splitlines():
            line_str = line.strip()
            # ASSERT statement
            assert_m = re.match(r"^ASSERT\s+(.+)$", line_str, re.IGNORECASE)
            if assert_m:
                stmt = assert_m.group(1).strip()
                if stmt not in assert_statements:
                    assert_statements.append(stmt)
                    invariants.append(stmt)

            # CALL_SKILL(skill_name, ...)
            call_m = re.search(r"CALL_SKILL\s*\(\s*([a-zA-Z0-9_\-\.]+)", line_str, re.IGNORECASE)
            if call_m:
                c_skill = call_m.group(1).strip()
                if c_skill not in call_skills:
                    call_skills.append(c_skill)

            # IF condition
            if_m = re.match(r"^IF\s+(.+?)\s+THEN", line_str, re.IGNORECASE)
            if if_m:
                cond = if_m.group(1).strip()
                if cond not in branch_conditions:
                    branch_conditions.append(cond)

        # 3. Augment from DRAKON diagram
        nodes = drakon.get("nodes", [])
        for node in nodes:
            title = node.get("title", "")
            ntype = node.get("type", "")

            # If node has ASSERT
            if "ASSERT" in title:
                stmt = re.sub(r"^ASSERT\s+", "", title, flags=re.IGNORECASE).strip()
                if stmt and stmt not in assert_statements:
                    assert_statements.append(stmt)
                    invariants.append(stmt)

            # If node is insertion or calls skill
            if ntype == "insertion" or "CALL_SKILL" in title:
                call_m = re.search(r"CALL_SKILL\s*\(\s*([a-zA-Z0-9_\-\.]+)", title, re.IGNORECASE)
                if call_m:
                    c_skill = call_m.group(1).strip()
                    if c_skill not in call_skills:
                        call_skills.append(c_skill)

            # Question nodes (branching)
            if ntype == "question":
                cond = title.strip().rstrip("?")
                if cond and cond not in branch_conditions:
                    branch_conditions.append(cond)

        # 4. Invariants from section 1 of markdown if present
        inv_sec = re.search(r"##\s+1\.\s+Architectural Context & Negative Invariants(.*?)(?:\n##|\Z)", skill_md_text, re.DOTALL | re.IGNORECASE)
        if inv_sec:
            for line in inv_sec.group(1).splitlines():
                line = line.strip()
                if line.startswith("- ") or line.startswith("* "):
                    cleaned = re.sub(r"^[-*]\s+", "", line).strip()
                    if cleaned and not cleaned.startswith("ADR Compliance") and cleaned not in invariants:
                        invariants.append(cleaned)

        return IntentGraphDTO(
            skill_name=skill_name,
            nodes=nodes,
            invariants=invariants,
            assert_statements=assert_statements,
            call_skills=call_skills,
            branch_conditions=branch_conditions,
            drakon_nodes_count=len(nodes)
        )
