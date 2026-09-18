"""
B-SDD Procedural Skill Crystallizer (INV-014-05, ADR-003).
Automates the 'Rule of 2' mandate: Any engineering procedure, command sequence,
or operational pattern observed >= 2 times is automatically crystallized into
a persistent procedural skill under .pi/skills/<skill-name>/SKILL.md.
Operates with pure Python standard library.
"""
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_SKILLS_ROOT = Path(".pi/skills")


class RuleOfTwoSkillCrystallizer:
    """Tracks procedure frequency and crystallizes persistent agent skills when repeated >= 2 times."""

    def __init__(self, skills_root: Optional[Path] = None, ledger_path: Optional[Path] = None):
        self.skills_root = Path(skills_root) if skills_root else DEFAULT_SKILLS_ROOT
        if ledger_path:
            self.ledger_path = Path(ledger_path)
        elif skills_root:
            self.ledger_path = self.skills_root.parent / "skill_pattern_counter.json"
        else:
            self.ledger_path = Path(".context/skill_pattern_counter.json")
        self._pattern_counts: Dict[str, int] = {}
        self._load_ledger()

    def _load_ledger(self):
        if self.ledger_path.exists():
            try:
                data = json.loads(self.ledger_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    self._pattern_counts = data
            except Exception:
                self._pattern_counts = {}

    def _save_ledger(self):
        try:
            self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
            self.ledger_path.write_text(json.dumps(self._pattern_counts, indent=2), encoding="utf-8")
        except Exception:
            pass

    def record_pattern(
        self,
        pattern_id: str,
        title: str,
        description: str,
        instructions: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Records an observation of an operational workflow.
        If frequency reaches >= 2, crystallizes into a permanent SKILL.md.
        """
        clean_id = pattern_id.strip().lower().replace(" ", "-")
        count = self._pattern_counts.get(clean_id, 0) + 1
        self._pattern_counts[clean_id] = count
        self._save_ledger()

        if count >= 2:
            skill_dir = self.skills_root / clean_id
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_file = skill_dir / "SKILL.md"

            content = f"""---
name: {clean_id}
description: {description}
---

# {title}

> **B-SDD Invariant (ADR-003 Rule of 2):** Crystallized after {count} repeat observations.

## Operational Instructions
{instructions}

## Invariants & Guardrails
- Mathematical planarity C=0 for any visual flows.
- 100% pure standard library in runtime components.
- Review gate verification required before final merging.
"""
            skill_file.write_text(content, encoding="utf-8")

            return {
                "pattern_id": clean_id,
                "crystallized": True,
                "frequency": count,
                "skill_path": str(skill_file),
                "message": f"Skill '{clean_id}' crystallized successfully under Rule of 2."
            }

        return {
            "pattern_id": clean_id,
            "crystallized": False,
            "frequency": count,
            "message": f"Pattern '{clean_id}' observed {count} time(s). Rule of 2 requires >= 2 repeats."
        }
