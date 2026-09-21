"""
DRAKON-as-Prompt Compiler.
Translates canonical DRAKON-IR schemas into structured, executable macro-prompts
for autonomous agent harnesses (AGY, Claude Code, Pi Harness).
Enforces ADR-002 (Pure Stdlib Core), ADR-005 (Active Rules Budget <= 500 words),
ADR-008 (Planar Flow X=0, C=0), and ADR-010 (Tripartite ADR Ontology).
100% Pure Python Standard Library.
"""
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from src.drakon.types import (
    DrakonSchema,
    DrakonNode,
    DrakonNodeType,
)
from src.core.drakon.macro_prompt import (
    StepKind,
    DirectiveType,
    TemporalFilter,
    FlowDirective,
    SkillInvocation,
    AdrQuery,
    MacroPromptStep,
    ExecutableMacroPrompt,
)
from src.core.drakon.planar_solver import DrakonPlanarSolver, PlanarLayoutResult


class DrakonPromptCompiler:
    """
    Autonomous compiler translating DRAKON diagrams into executable agent prompts.
    """

    DEFAULT_INVARIANTS = [
        "ADR-001 (WORM Ledger & Bitemporal): Immutable records in Utopia DB; state changes commit with (Tv, Tt).",
        "ADR-002 (Pure Stdlib Core): src/core/ strictly adheres to Python 3.12+ standard library (0 external dependencies).",
        "ADR-004 (AST Impact Containment): All code mutations must verify blast radius via GitNexus graph.",
        "ADR-005 (Fitness Gate & SLA): Compilation latency < 50ms, active rules budget <= 500 words.",
        "ADR-008 (DRAKON Planar Flow): Primary success path on vertical skewer X=0, right-is-worse branching, crossings C=0.",
        "ADR-010 (Tripartite ADR): Unified Data, Skills, Specs; external APIs pre-logged to DataADR before execution.",
    ]

    def __init__(
        self,
        planar_solver: Optional[DrakonPlanarSolver] = None,
        active_invariants: Optional[List[str]] = None,
    ):
        self.planar_solver = planar_solver or DrakonPlanarSolver()
        self.active_invariants = active_invariants if active_invariants is not None else list(self.DEFAULT_INVARIANTS)

    def compile(
        self,
        schema: DrakonSchema,
        objective: Optional[str] = None,
        skill_catalog: Optional[Dict[str, str]] = None,
    ) -> ExecutableMacroPrompt:
        """
        Compiles DrakonSchema into an ExecutableMacroPrompt.
        1. Solves planar layout (guaranteeing X=0 and C=0).
        2. Walks nodes in topological planar order.
        3. Emits discrete MacroPromptSteps with appropriate directives and skill bindings.
        """
        layout: PlanarLayoutResult = self.planar_solver.solve(schema)
        skill_cat = skill_catalog or {}

        steps: List[MacroPromptStep] = []
        visited = set()

        # Gather ordered list of nodes: skewer nodes first, then degradation branches
        nodes_by_y = sorted(
            schema.nodes.values(),
            key=lambda n: (n.x if n.x is not None else 0.0, n.y if n.y is not None else 0.0)
        )

        for idx, node in enumerate(nodes_by_y, start=1):
            if node.node_id in visited:
                continue
            visited.add(node.node_id)

            step = self._compile_node_to_step(
                step_idx=idx,
                node=node,
                layout=layout,
                skill_catalog=skill_cat,
            )
            steps.append(step)

        macro_prompt = ExecutableMacroPrompt(
            title=f"Autonomous DRAKON Protocol: {schema.name}",
            schema_name=schema.name,
            objective=objective or f"Execute workflow for {schema.name} adhering to DRAKON planar invariants.",
            active_invariants=self.active_invariants,
            steps=steps,
            metadata={
                "crossings_count": layout.crossings_count,
                "is_planar": layout.is_planar,
                "skewer_x": layout.skewer_x,
                "total_nodes": len(schema.nodes),
            }
        )

        return macro_prompt

    def _compile_node_to_step(
        self,
        step_idx: int,
        node: DrakonNode,
        layout: PlanarLayoutResult,
        skill_catalog: Dict[str, str],
    ) -> MacroPromptStep:
        """Transforms an individual DrakonNode into an executable MacroPromptStep."""
        step_id = f"step_{step_idx}_{node.node_id}"
        ntype = node.normalized_type
        x = node.x if node.x is not None else 0.0
        y = node.y if node.y is not None else 0.0

        kind = StepKind.SKILL_INVOCATION
        flow: Optional[FlowDirective] = None
        skill: Optional[SkillInvocation] = None
        adr_q: Optional[AdrQuery] = None
        instructions = node.label or f"Execute node {node.node_id}"

        # 1. Headline / Header
        if ntype == DrakonNodeType.HEADLINE.value:
            kind = StepKind.FLOW_DIRECTIVE
            flow = FlowDirective(
                directive_type=DirectiveType.BRANCH,
                target_down=node.edges.down,
            )
            instructions = f"Begin diagram execution: {node.label}"

        # 2. Branch
        elif ntype == DrakonNodeType.BRANCH.value:
            kind = StepKind.FLOW_DIRECTIVE
            flow = FlowDirective(
                directive_type=DirectiveType.BRANCH,
                target_down=node.edges.down,
            )
            instructions = f"Enter silhouette branch: {node.label}"

        # 3. Question / Invariant Condition
        elif ntype == DrakonNodeType.QUESTION.value:
            kind = StepKind.FLOW_DIRECTIVE
            flow = FlowDirective(
                directive_type=DirectiveType.QUESTION,
                condition_expression=node.label,
                target_down=node.edges.down,
                target_right=node.edges.right,
            )
            instructions = f"Evaluate condition: '{node.label}'. If YES proceed down, if NO branch right."

        # 4. Select / Multi-way Choice
        elif ntype in (DrakonNodeType.SELECT.value, DrakonNodeType.CHOICE.value):
            kind = StepKind.FLOW_DIRECTIVE
            flow = FlowDirective(
                directive_type=DirectiveType.SELECT,
                condition_expression=node.label,
                cases=node.edges.extra,
            )
            instructions = f"Select branch matching: '{node.label}'"

        # 5. Loops
        elif ntype == DrakonNodeType.LOOP_BEGIN.value:
            kind = StepKind.FLOW_DIRECTIVE
            flow = FlowDirective(
                directive_type=DirectiveType.LOOP_BEGIN,
                condition_expression=node.label,
                target_down=node.edges.down,
            )
            instructions = f"Begin loop: '{node.label}'"

        elif ntype == DrakonNodeType.LOOP_END.value:
            kind = StepKind.FLOW_DIRECTIVE
            flow = FlowDirective(
                directive_type=DirectiveType.LOOP_END,
                target_down=node.edges.down,
            )
            instructions = f"End of loop iteration: '{node.label}'"

        # 6. End / Terminal
        elif ntype == DrakonNodeType.END.value:
            kind = StepKind.TERMINAL
            flow = FlowDirective(directive_type=DirectiveType.HALT)
            instructions = f"Diagram flow completed: {node.label or 'HALT'}"

        # 7. Action Node (Skill invocation or ADR query)
        else:
            label_lower = (node.label or "").lower()
            if "read" in label_lower or "query" in label_lower or "fetch" in label_lower:
                kind = StepKind.ADR_QUERY
                adr_q = AdrQuery(
                    operation="READ",
                    target_adr_type="data" if "data" in label_lower else "spec",
                )
                instructions = f"Query ADR context: {node.label}"
            elif "mutate" in label_lower or "write" in label_lower or "update" in label_lower:
                kind = StepKind.ADR_QUERY
                adr_q = AdrQuery(
                    operation="MUTATE",
                    target_adr_type="data",
                )
                instructions = f"Mutate ADR state: {node.label}"
            else:
                kind = StepKind.SKILL_INVOCATION
                skill_id = skill_catalog.get(node.node_id, f"SKILL_{node.node_id.upper()}")
                skill = SkillInvocation(
                    skill_id=skill_id,
                    action_name=node.label or node.node_id,
                )
                instructions = f"Invoke skill '{skill_id}': {node.label}"

        return MacroPromptStep(
            step_id=step_id,
            node_id=node.node_id,
            kind=kind,
            label=node.label or node.node_id,
            instructions=instructions,
            skewer_x=x,
            level_y=y,
            flow_directive=flow,
            skill_invocation=skill,
            adr_query=adr_q,
            next_step_id=node.edges.down,
            alt_step_id=node.edges.right,
        )
