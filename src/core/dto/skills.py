"""
Skill DTO Schemas and Serialization Contracts.
Compliant with ADR-002 (Pure Stdlib Core) and ADR-015 (System Skills Taxonomy & Immutability).
100% Pure Python Standard Library.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SkillType(str, Enum):
    """Categorization of agent skills under ADR-015."""
    SYSTEM_SKILL = "SYSTEM_SKILL"
    PROJECT_SKILL = "PROJECT_SKILL"


@dataclass
class SkillDTO:
    """Canonical Skill Data Transfer Object representing an agent skill and its DRAKON bindings."""
    name: str
    description: str = ""
    skill_type: str = SkillType.PROJECT_SKILL.value
    category: str = "general"
    immutable: bool = False
    has_drakon_schema: bool = False
    invoked_skills: List[str] = field(default_factory=list)
    drakon_path: Optional[str] = None
    skill_md_path: Optional[str] = None

    def is_system_skill(self) -> bool:
        return self.skill_type == SkillType.SYSTEM_SKILL.value or self.immutable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "skill_type": self.skill_type,
            "category": self.category,
            "immutable": self.immutable,
            "has_drakon_schema": self.has_drakon_schema,
            "invoked_skills": list(self.invoked_skills),
            "drakon_path": self.drakon_path,
            "skill_md_path": self.skill_md_path,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillDTO":
        skill_type = data.get("skill_type", SkillType.PROJECT_SKILL.value)
        immutable = bool(data.get("immutable", False))
        if skill_type == SkillType.SYSTEM_SKILL.value:
            immutable = True

        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            skill_type=skill_type,
            category=data.get("category", "general"),
            immutable=immutable,
            has_drakon_schema=bool(data.get("has_drakon_schema", False)),
            invoked_skills=list(data.get("invoked_skills", [])),
            drakon_path=data.get("drakon_path"),
            skill_md_path=data.get("skill_md_path"),
        )


@dataclass
class SkillsResponseDTO:
    """Payload envelope for GET /api/skills endpoint."""
    skills: List[SkillDTO] = field(default_factory=list)
    total: int = 0
    system_skills_count: int = 0
    project_skills_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skills": [s.to_dict() for s in self.skills],
            "total": self.total,
            "system_skills_count": self.system_skills_count,
            "project_skills_count": self.project_skills_count,
        }

    @classmethod
    def from_skills_list(cls, skills: List[SkillDTO]) -> "SkillsResponseDTO":
        system_count = sum(1 for s in skills if s.is_system_skill())
        project_count = len(skills) - system_count
        return cls(
            skills=skills,
            total=len(skills),
            system_skills_count=system_count,
            project_skills_count=project_count,
        )
