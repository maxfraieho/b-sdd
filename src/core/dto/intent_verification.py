"""
Intent Verification DTO Schemas and Serialization Contracts.
Compliant with ADR-002 (Pure Stdlib Core) and ADR-016 (Tripartite Skill Architecture & Pseudocode Standard).
100% Pure Python Standard Library.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class IntentVerdict(str, Enum):
    """Discrete verdicts for Vector 3 Semantic Spec-to-Code Intent Verification."""
    VERDICT_INTENT_ALIGNED = "VERDICT_INTENT_ALIGNED"
    VERDICT_INTENT_DRIFT_WARNING = "VERDICT_INTENT_DRIFT_WARNING"
    VERDICT_INTENT_VIOLATION = "VERDICT_INTENT_VIOLATION"


@dataclass
class IntentGraphDTO:
    """Canonical representation of architectural intent extracted from SKILL.md & companion .drakon.json."""
    skill_name: str
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    invariants: List[str] = field(default_factory=list)
    assert_statements: List[str] = field(default_factory=list)
    call_skills: List[str] = field(default_factory=list)
    branch_conditions: List[str] = field(default_factory=list)
    drakon_nodes_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "nodes": list(self.nodes),
            "invariants": list(self.invariants),
            "assert_statements": list(self.assert_statements),
            "call_skills": list(self.call_skills),
            "branch_conditions": list(self.branch_conditions),
            "drakon_nodes_count": self.drakon_nodes_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntentGraphDTO":
        return cls(
            skill_name=data.get("skill_name", ""),
            nodes=list(data.get("nodes", [])),
            invariants=list(data.get("invariants", [])),
            assert_statements=list(data.get("assert_statements", [])),
            call_skills=list(data.get("call_skills", [])),
            branch_conditions=list(data.get("branch_conditions", [])),
            drakon_nodes_count=int(data.get("drakon_nodes_count", 0)),
        )


@dataclass
class CodeASTSignaturesDTO:
    """Structural AST-level execution signatures extracted from staged code changes."""
    changed_files: List[str] = field(default_factory=list)
    function_signatures: List[str] = field(default_factory=list)
    call_chains: List[str] = field(default_factory=list)
    assert_statements: List[str] = field(default_factory=list)
    has_test_coverage: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "changed_files": list(self.changed_files),
            "function_signatures": list(self.function_signatures),
            "call_chains": list(self.call_chains),
            "assert_statements": list(self.assert_statements),
            "has_test_coverage": self.has_test_coverage,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodeASTSignaturesDTO":
        return cls(
            changed_files=list(data.get("changed_files", [])),
            function_signatures=list(data.get("function_signatures", [])),
            call_chains=list(data.get("call_chains", [])),
            assert_statements=list(data.get("assert_statements", [])),
            has_test_coverage=bool(data.get("has_test_coverage", False)),
        )


@dataclass
class IntentVerificationResultDTO:
    """Consolidated verification verdict combining semantic alignment score and invariant presence."""
    cosine_alignment: float  # S_intent [0.0 .. 1.0]
    missing_invariants: List[str] = field(default_factory=list)
    verdict: str = IntentVerdict.VERDICT_INTENT_ALIGNED.value
    allow_commit: bool = True
    latency_ms: float = 0.0
    fallback: bool = False
    details: Dict[str, Any] = field(default_factory=dict)

    def is_aligned(self) -> bool:
        return (
            self.verdict == IntentVerdict.VERDICT_INTENT_ALIGNED.value
            and self.cosine_alignment >= 0.82
            and len(self.missing_invariants) == 0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cosine_alignment": self.cosine_alignment,
            "missing_invariants": list(self.missing_invariants),
            "verdict": self.verdict,
            "allow_commit": self.allow_commit,
            "latency_ms": self.latency_ms,
            "fallback": self.fallback,
            "details": dict(self.details),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntentVerificationResultDTO":
        return cls(
            cosine_alignment=float(data.get("cosine_alignment", 1.0)),
            missing_invariants=list(data.get("missing_invariants", [])),
            verdict=data.get("verdict", IntentVerdict.VERDICT_INTENT_ALIGNED.value),
            allow_commit=bool(data.get("allow_commit", True)),
            latency_ms=float(data.get("latency_ms", 0.0)),
            fallback=bool(data.get("fallback", False)),
            details=dict(data.get("details", {})),
        )
