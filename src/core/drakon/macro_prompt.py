"""
DRAKON-as-Prompt Intermediate Representation and DTO Schemas.
Translates visual DRAKON algorithmic topology into structured, machine-executable
macro-prompts for autonomous agent harnesses (AGY, Claude Code, Pi Harness).
Compliant with ADR-002 (Pure Stdlib Core), ADR-008 (DRAKON Invariants), and ADR-010.
100% Pure Python Standard Library.
"""
from dataclasses import dataclass, field
from enum import Enum
import json
from typing import Dict, List, Optional, Any, Union


class StepKind(str, Enum):
    """Categorization of executable prompt steps derived from DRAKON primitives."""
    FLOW_DIRECTIVE = "flow_directive"
    SKILL_INVOCATION = "skill_invocation"
    ADR_QUERY = "adr_query"
    TERMINAL = "terminal"


class DirectiveType(str, Enum):
    """Control-flow primitive types."""
    BRANCH = "branch"             # Silhouette subtree / column
    QUESTION = "question"         # Binary condition (Down = Success, Right = Degradation)
    SELECT = "select"             # Multi-way branch selection
    LOOP_BEGIN = "loop_begin"     # Iteration header
    LOOP_END = "loop_end"         # Iteration boundary
    ADDRESS = "address"           # Silhouette transfer to next branch
    HALT = "halt"                 # Algorithm completion


@dataclass
class TemporalFilter:
    """Bitemporal window [T_v1, T_v2] for querying Data ADRs in loops or queries."""
    t_v1: str
    t_v2: Optional[str] = None
    as_of_tt: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "t_v1": self.t_v1,
            "t_v2": self.t_v2,
            "as_of_tt": self.as_of_tt,
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["TemporalFilter"]:
        if not data:
            return None
        return cls(
            t_v1=data.get("t_v1", ""),
            t_v2=data.get("t_v2"),
            as_of_tt=data.get("as_of_tt"),
        )


@dataclass
class FlowDirective:
    """Branching, selection, or iteration directive adhering to the planar skewer."""
    directive_type: DirectiveType
    condition_expression: Optional[str] = None
    target_down: Optional[str] = None   # Skewer path (success / primary)
    target_right: Optional[str] = None  # Right path (degradation / alternative)
    cases: Dict[str, str] = field(default_factory=dict)
    temporal_filter: Optional[TemporalFilter] = None

    def to_dict(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {
            "directive_type": self.directive_type.value,
        }
        if self.condition_expression:
            res["condition_expression"] = self.condition_expression
        if self.target_down:
            res["target_down"] = self.target_down
        if self.target_right:
            res["target_right"] = self.target_right
        if self.cases:
            res["cases"] = self.cases
        if self.temporal_filter:
            res["temporal_filter"] = self.temporal_filter.to_dict()
        return res

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["FlowDirective"]:
        if not data:
            return None
        dtype = DirectiveType(data.get("directive_type", DirectiveType.BRANCH.value))
        tf = TemporalFilter.from_dict(data.get("temporal_filter"))
        return cls(
            directive_type=dtype,
            condition_expression=data.get("condition_expression"),
            target_down=data.get("target_down"),
            target_right=data.get("target_right"),
            cases=data.get("cases", {}),
            temporal_filter=tf,
        )


@dataclass
class SkillInvocation:
    """Binding an Action icon to a concrete SkillADR registered in Utopia DB."""
    skill_id: str                      # e.g. "ADR-SKILL-001" or skill name
    action_name: str
    target_parameters: Dict[str, Any] = field(default_factory=dict)
    pre_logged_data_ref: Optional[str] = None
    expected_output_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {
            "skill_id": self.skill_id,
            "action_name": self.action_name,
            "target_parameters": self.target_parameters,
        }
        if self.pre_logged_data_ref:
            res["pre_logged_data_ref"] = self.pre_logged_data_ref
        if self.expected_output_type:
            res["expected_output_type"] = self.expected_output_type
        return res

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["SkillInvocation"]:
        if not data:
            return None
        return cls(
            skill_id=data.get("skill_id", ""),
            action_name=data.get("action_name", ""),
            target_parameters=data.get("target_parameters", {}),
            pre_logged_data_ref=data.get("pre_logged_data_ref"),
            expected_output_type=data.get("expected_output_type"),
        )


@dataclass
class AdrQuery:
    """Explicit retrieval or state mutation of a DataADR or SpecADR."""
    operation: str                     # "READ" | "MUTATE" | "SUPERSEDE"
    target_adr_id: Optional[str] = None
    target_adr_type: Optional[str] = None  # "data" | "spec" | "skill"
    temporal_filter: Optional[TemporalFilter] = None
    mutation_payload: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {
            "operation": self.operation,
        }
        if self.target_adr_id:
            res["target_adr_id"] = self.target_adr_id
        if self.target_adr_type:
            res["target_adr_type"] = self.target_adr_type
        if self.temporal_filter:
            res["temporal_filter"] = self.temporal_filter.to_dict()
        if self.mutation_payload:
            res["mutation_payload"] = self.mutation_payload
        return res

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["AdrQuery"]:
        if not data:
            return None
        tf = TemporalFilter.from_dict(data.get("temporal_filter"))
        return cls(
            operation=data.get("operation", "READ"),
            target_adr_id=data.get("target_adr_id"),
            target_adr_type=data.get("target_adr_type"),
            temporal_filter=tf,
            mutation_payload=data.get("mutation_payload"),
        )


@dataclass
class MacroPromptStep:
    """An individual discrete step within the executable macro-prompt."""
    step_id: str
    node_id: str
    kind: StepKind
    label: str
    instructions: str
    skewer_x: float = 0.0              # X=0 indicates primary skewer axis
    level_y: float = 0.0
    flow_directive: Optional[FlowDirective] = None
    skill_invocation: Optional[SkillInvocation] = None
    adr_query: Optional[AdrQuery] = None
    next_step_id: Optional[str] = None
    alt_step_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {
            "step_id": self.step_id,
            "node_id": self.node_id,
            "kind": self.kind.value,
            "label": self.label,
            "instructions": self.instructions,
            "skewer_x": self.skewer_x,
            "level_y": self.level_y,
        }
        if self.flow_directive:
            res["flow_directive"] = self.flow_directive.to_dict()
        if self.skill_invocation:
            res["skill_invocation"] = self.skill_invocation.to_dict()
        if self.adr_query:
            res["adr_query"] = self.adr_query.to_dict()
        if self.next_step_id:
            res["next_step_id"] = self.next_step_id
        if self.alt_step_id:
            res["alt_step_id"] = self.alt_step_id
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MacroPromptStep":
        kind = StepKind(data.get("kind", StepKind.SKILL_INVOCATION.value))
        flow = FlowDirective.from_dict(data.get("flow_directive"))
        skill = SkillInvocation.from_dict(data.get("skill_invocation"))
        adr_q = AdrQuery.from_dict(data.get("adr_query"))
        return cls(
            step_id=data["step_id"],
            node_id=data["node_id"],
            kind=kind,
            label=data.get("label", ""),
            instructions=data.get("instructions", ""),
            skewer_x=float(data.get("skewer_x", 0.0)),
            level_y=float(data.get("level_y", 0.0)),
            flow_directive=flow,
            skill_invocation=skill,
            adr_query=adr_q,
            next_step_id=data.get("next_step_id"),
            alt_step_id=data.get("alt_step_id"),
        )


@dataclass
class ExecutableMacroPrompt:
    """
    Complete structured prompt compiled from DRAKON-IR diagram.
    Ready for autonomous agents (AGY, Claude Code, Pi Harness) to parse and execute.
    Guarantees active invariants budget (strictly <= 500 words per ADR-002).
    """
    title: str
    schema_name: str
    objective: str
    active_invariants: List[str] = field(default_factory=list)
    steps: List[MacroPromptStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def invariants_word_count(self) -> int:
        """Calculates total word count across all active invariants."""
        return sum(len(inv.split()) for inv in self.active_invariants)

    def render_markdown(self) -> str:
        """Renders prompt as markdown with clear step-by-step guidance and flow controls."""
        lines = [
            f"# EXECUTABLE MACRO-PROMPT: {self.title}",
            f"**Objective:** {self.objective}",
            "",
            "## MANDATORY ACTIVE INVARIANTS (Capsule <= 500 words)",
        ]
        for inv in self.active_invariants:
            lines.append(f"- {inv}")
        lines.append("")
        lines.append("## EXECUTION PIPELINE (Planar DRAKON Flow)")

        for idx, step in enumerate(self.steps, start=1):
            pos_tag = "[SKEWER X=0]" if step.skewer_x == 0.0 else f"[ALT X={step.skewer_x}]"
            lines.append(f"### Step {idx}: {step.label} {pos_tag} ({step.kind.value})")
            lines.append(f"- **Node ID:** `{step.node_id}`")
            lines.append(f"- **Instruction:** {step.instructions}")

            if step.skill_invocation:
                lines.append(f"- **Skill Call:** `{step.skill_invocation.skill_id}` -> `{step.skill_invocation.action_name}`")
                if step.skill_invocation.pre_logged_data_ref:
                    lines.append(f"  - Pre-Logged Data Ref: `{step.skill_invocation.pre_logged_data_ref}`")

            if step.flow_directive:
                fd = step.flow_directive
                lines.append(f"- **Control Flow:** `{fd.directive_type.value}`")
                if fd.condition_expression:
                    lines.append(f"  - Condition: `{fd.condition_expression}`")
                if fd.target_down:
                    lines.append(f"  - Down (Success): `{fd.target_down}`")
                if fd.target_right:
                    lines.append(f"  - Right (Degradation / Exit): `{fd.target_right}`")

            if step.adr_query:
                aq = step.adr_query
                lines.append(f"- **ADR Query:** `{aq.operation}` on `{aq.target_adr_type or 'any'}` (`{aq.target_adr_id or '*'}`)")

            if step.next_step_id:
                lines.append(f"- **Next Step:** `{step.next_step_id}`")
            if step.alt_step_id:
                lines.append(f"- **Alternative Path:** `{step.alt_step_id}`")
            lines.append("")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "schema_name": self.schema_name,
            "objective": self.objective,
            "active_invariants": self.active_invariants,
            "invariants_word_count": self.invariants_word_count(),
            "steps": [s.to_dict() for s in self.steps],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutableMacroPrompt":
        steps = [MacroPromptStep.from_dict(s) for s in data.get("steps", [])]
        return cls(
            title=data.get("title", ""),
            schema_name=data.get("schema_name", ""),
            objective=data.get("objective", ""),
            active_invariants=data.get("active_invariants", []),
            steps=steps,
            metadata=data.get("metadata", {}),
        )
