"""
Unit and Invariant Fitness Tests for DRAKON Planar Solver and Prompt Compiler.
Validates compliance with:
- ADR-002: Pure Python Standard Library in src/core/drakon/.
- ADR-004: GitNexus Blast Radius Audit and Containment.
- ADR-005: Active Invariants Budget <= 500 words.
- ADR-008: DRAKON Planar Invariants (Skewer X=0, Right-is-Worse, Crossings C=0).
- ADR-010: DRAKON-as-Prompt Compilation.
"""
import ast
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.drakon.types import (
    DrakonSchema,
    DrakonNode,
    DrakonNodeType,
    DrakonEdges,
)
from src.drakon.parser import DrakonParser
from src.drakon.validator import DrakonValidator
from src.core.drakon.planar_solver import DrakonPlanarSolver, PlanarLayoutResult
from src.core.drakon.prompt_compiler import DrakonPromptCompiler
from src.core.drakon.macro_prompt import ExecutableMacroPrompt, DirectiveType, StepKind
from src.adapters.gitnexus_graph import GitNexusBlastRadiusAuditor


def test_pure_stdlib_in_planar_solver_and_compiler():
    """Invariant ADR-002: src/core/drakon/ must use 100% pure Python standard library."""
    target_dir = ROOT / "src" / "core" / "drakon"
    stdlib_modules = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else {
        "os", "sys", "re", "json", "time", "sqlite3", "hashlib", "pathlib", "typing",
        "subprocess", "logging", "datetime", "uuid", "argparse", "unittest", "shutil",
        "tempfile", "functools", "itertools", "collections", "abc", "contextlib", "dataclasses", "enum", "math"
    }
    internal_pkgs = {"src"}

    for py_file in target_dir.rglob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(py_file))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split(".")[0]
                    assert root_mod in stdlib_modules or root_mod in internal_pkgs, (
                        f"Illegal external dependency '{alias.name}' in {py_file.name}"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_mod = node.module.split(".")[0]
                    assert root_mod in stdlib_modules or root_mod in internal_pkgs, (
                        f"Illegal external from-import '{node.module}' in {py_file.name}"
                    )


def test_planar_solver_vertical_skewer_x_zero():
    """Invariant ADR-008: Main success path nodes must lie strictly on vertical skewer X=0."""
    nodes = {
        "start": DrakonNode(node_id="start", node_type=DrakonNodeType.HEADLINE.value, label="Start", edges=DrakonEdges(down="step1")),
        "step1": DrakonNode(node_id="step1", node_type=DrakonNodeType.ACTION.value, label="Step 1", edges=DrakonEdges(down="step2")),
        "step2": DrakonNode(node_id="step2", node_type=DrakonNodeType.ACTION.value, label="Step 2", edges=DrakonEdges(down="end")),
        "end": DrakonNode(node_id="end", node_type=DrakonNodeType.END.value, label="Finish"),
    }
    schema = DrakonSchema(name="Linear Workflow", nodes=nodes)
    solver = DrakonPlanarSolver(skewer_x=0.0)
    result = solver.solve(schema)

    assert result.is_planar is True
    assert result.crossings_count == 0
    assert result.skewer_x == 0.0

    # Verify all skewer nodes have X=0 and monotonically increasing Y
    prev_y = -1.0
    for nid in ["start", "step1", "step2", "end"]:
        x, y = result.node_positions[nid]
        assert abs(x - 0.0) < 1e-4, f"Node {nid} has X={x}, expected 0.0"
        assert y > prev_y, f"Node {nid} has Y={y} <= prev_y={prev_y}"
        prev_y = y


def test_planar_solver_right_is_worse_branching():
    """Invariant ADR-008: Alternative/degradation branches must branch strictly right (X > 0)."""
    nodes = {
        "start": DrakonNode(node_id="start", node_type=DrakonNodeType.HEADLINE.value, label="Start", edges=DrakonEdges(down="check")),
        "check": DrakonNode(node_id="check", node_type=DrakonNodeType.QUESTION.value, label="Is Valid?", edges=DrakonEdges(down="success", right="degrade")),
        "success": DrakonNode(node_id="success", node_type=DrakonNodeType.ACTION.value, label="Proceed Success", edges=DrakonEdges(down="end")),
        "degrade": DrakonNode(node_id="degrade", node_type=DrakonNodeType.ACTION.value, label="Handle Fallback", edges=DrakonEdges(down="end_fail")),
        "end": DrakonNode(node_id="end", node_type=DrakonNodeType.END.value, label="Finish OK"),
        "end_fail": DrakonNode(node_id="end_fail", node_type=DrakonNodeType.END.value, label="Finish Degraded"),
    }
    schema = DrakonSchema(name="Branching Workflow", nodes=nodes)
    solver = DrakonPlanarSolver(skewer_x=0.0)
    result = solver.solve(schema)

    assert result.is_planar is True
    assert result.crossings_count == 0

    # Skewer path (start -> check -> success -> end)
    assert result.node_positions["start"][0] == 0.0
    assert result.node_positions["check"][0] == 0.0
    assert result.node_positions["success"][0] == 0.0
    assert result.node_positions["end"][0] == 0.0

    # Right degradation branch (degrade -> end_fail)
    degrade_x = result.node_positions["degrade"][0]
    fail_x = result.node_positions["end_fail"][0]
    assert degrade_x > 0.0, f"Expected degrade X > 0, got {degrade_x}"
    assert fail_x > 0.0, f"Expected end_fail X > 0, got {fail_x}"
    assert abs(degrade_x - fail_x) < 1e-4  # Collinear along the right branch


def test_planar_solver_on_complex_preflight_template():
    """Invariant ADR-008: Solver guarantees C=0 crossings on real template schema."""
    template_path = ROOT / "src" / "drakon" / "templates" / "bsdd_preflight_pipeline.json"
    assert template_path.exists(), "Preflight template does not exist"

    schema = DrakonParser.parse_file(str(template_path))
    solver = DrakonPlanarSolver(skewer_x=0.0)
    result = solver.solve(schema)

    assert result.is_planar is True
    assert result.crossings_count == 0
    assert len(result.node_positions) == len(schema.nodes)

    # Validate output schema against DrakonValidator
    validator = DrakonValidator(root_dir=ROOT)
    validation = validator.validate(schema)
    assert validation.is_valid is True, f"Validation failed with errors: {validation.errors}"


def test_prompt_compiler_generates_executable_macro_prompt():
    """Invariant ADR-005 & ADR-010: Prompt compiler emits structured prompt with active invariants <= 500 words."""
    nodes = {
        "start": DrakonNode(node_id="start", node_type=DrakonNodeType.HEADLINE.value, label="Sprint Verification Start", edges=DrakonEdges(down="query_spec")),
        "query_spec": DrakonNode(node_id="query_spec", node_type=DrakonNodeType.ACTION.value, label="Read Spec ADR", edges=DrakonEdges(down="run_tests")),
        "run_tests": DrakonNode(node_id="run_tests", node_type=DrakonNodeType.ACTION.value, label="Execute Test Suite", edges=DrakonEdges(down="check_pass")),
        "check_pass": DrakonNode(node_id="check_pass", node_type=DrakonNodeType.QUESTION.value, label="Tests Passed?", edges=DrakonEdges(down="commit", right="degrade")),
        "commit": DrakonNode(node_id="commit", node_type=DrakonNodeType.ACTION.value, label="Commit Transaction", edges=DrakonEdges(down="end")),
        "degrade": DrakonNode(node_id="degrade", node_type=DrakonNodeType.ACTION.value, label="Alert Operator", edges=DrakonEdges(down="end_fail")),
        "end": DrakonNode(node_id="end", node_type=DrakonNodeType.END.value, label="Success"),
        "end_fail": DrakonNode(node_id="end_fail", node_type=DrakonNodeType.END.value, label="Halt Failure"),
    }
    schema = DrakonSchema(name="Sprint Verification Pipeline", nodes=nodes)
    compiler = DrakonPromptCompiler()
    macro = compiler.compile(
        schema=schema,
        objective="Verify sprint test suite under SLA < 50ms",
        skill_catalog={
            "run_tests": "ADR-SKILL-PYTEST-RUNNER",
            "commit": "ADR-SKILL-UTOPIA-COMMIT",
            "degrade": "ADR-SKILL-OPERATOR-ALERT",
        }
    )

    assert isinstance(macro, ExecutableMacroPrompt)
    assert macro.invariants_word_count() <= 500
    assert macro.invariants_word_count() > 0
    assert len(macro.steps) == len(nodes)

    # Check step types and skill bindings
    step_map = {s.node_id: s for s in macro.steps}
    assert step_map["query_spec"].kind == StepKind.ADR_QUERY
    assert step_map["run_tests"].kind == StepKind.SKILL_INVOCATION
    assert step_map["run_tests"].skill_invocation.skill_id == "ADR-SKILL-PYTEST-RUNNER"
    assert step_map["check_pass"].kind == StepKind.FLOW_DIRECTIVE
    assert step_map["check_pass"].flow_directive.directive_type == DirectiveType.QUESTION
    assert step_map["check_pass"].flow_directive.target_down == "commit"
    assert step_map["check_pass"].flow_directive.target_right == "degrade"
    assert step_map["degrade"].skewer_x > 0.0  # Right branch

    # Render markdown check
    md = macro.render_markdown()
    assert "# EXECUTABLE MACRO-PROMPT" in md
    assert "Sprint Verification Pipeline" in md
    assert "[SKEWER X=0]" in md
    assert "ADR-SKILL-PYTEST-RUNNER" in md


def test_gitnexus_blast_radius_auditor():
    """Invariant ADR-004: Blast radius auditor verifies symbol impact and domain containment."""
    auditor = GitNexusBlastRadiusAuditor(repo_root=ROOT)

    # 1. Audit core solver symbol
    report = auditor.audit_symbol_blast_radius("DrakonPlanarSolver")
    assert report["symbol"] == "DrakonPlanarSolver"
    assert "risk" in report
    assert isinstance(report["affected_modules"], list)

    # 2. Audit ontology symbol
    report_adr = auditor.audit_symbol_blast_radius("TripartiteAdrRegistry")
    assert report_adr["symbol"] == "TripartiteAdrRegistry"
    assert "risk" in report_adr

    # 3. Containment check on core files
    containment = auditor.verify_blast_radius_contained(
        mutated_files=[
            "src/core/adr/ontology.py",
            "src/core/drakon/planar_solver.py",
            "src/core/drakon/prompt_compiler.py",
        ]
    )
    assert containment["is_contained"] is True
    assert "core" in containment["impacted_domains"]
