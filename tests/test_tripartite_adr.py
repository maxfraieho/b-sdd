"""
Unit and Invariant Tests for B-SDD Tripartite ADR Ontology & Macro-Prompt IR.
Validates compliance with:
- ADR-001: Bitemporal consistency and WORM ledger.
- ADR-002: Pure Python Standard Library in src/core/.
- ADR-005: Active invariants capsule <= 500 words.
- ADR-010: Tripartite ADR Ontology (Data, Skills, Specs) and External Pre-Logging Axiom.
"""
import ast
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.core.adr.ontology import (
    ADRType,
    BaseADR,
    DataADR,
    SkillADR,
    SpecADR,
    TripartiteAdrRegistry,
    BitemporalExternalPreLogger,
    deserialize_adr,
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


def test_pure_stdlib_in_core_adr_and_drakon():
    """Invariant ADR-002: src/core/adr/ and src/core/drakon/ must use 100% pure Python standard library."""
    target_dirs = [
        ROOT / "src" / "core" / "adr",
        ROOT / "src" / "core" / "drakon",
    ]
    stdlib_modules = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else {
        "os", "sys", "re", "json", "time", "sqlite3", "hashlib", "pathlib", "typing",
        "subprocess", "logging", "datetime", "uuid", "argparse", "unittest", "shutil",
        "tempfile", "functools", "itertools", "collections", "abc", "contextlib", "dataclasses", "enum", "math"
    }
    internal_pkgs = {"src"}

    for tdir in target_dirs:
        for py_file in tdir.rglob("*.py"):
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


def test_data_adr_hashing_and_serialization():
    """Invariant ADR-010: DataADR deterministically hashes payload and preserves bitemporal fields."""
    payload = {"temperature": 23.5, "sensor": "alpha-01", "active": True}
    data_adr = DataADR(
        adr_id="ADR-DATA-001",
        title="Environmental Sensor Reading",
        data_payload=payload,
        source_uri="mqtt://sensors/alpha",
        valid_from="2026-09-20T10:00:00Z",
    )

    assert data_adr.adr_type == ADRType.DATA
    assert data_adr.raw_hash is not None
    assert len(data_adr.raw_hash) == 64  # SHA256 hex length

    # Serialization roundtrip
    d = data_adr.to_dict()
    restored = deserialize_adr(d)
    assert isinstance(restored, DataADR)
    assert restored.adr_id == "ADR-DATA-001"
    assert restored.data_payload == payload
    assert restored.raw_hash == data_adr.raw_hash


def test_skill_adr_dual_representation():
    """Invariant ADR-010: SkillADR links visual schema (.drakon.json) and physical folder dump (.md)."""
    skill = SkillADR(
        adr_id="ADR-SKILL-001",
        title="B-SDD Pre-Flight Compiler Skill",
        drakon_schema_ref="src/drakon/templates/bsdd_preflight_pipeline.json",
        dump_path=".agents/skills/b-sdd/SKILL.md",
        input_adr_types=["spec", "data"],
        output_adr_types=["spec"],
        invariants=["INV-001: latency < 50ms", "INV-002: words <= 500"],
        pseudocode="def compile(): read_active_adrs(); render();",
    )

    assert skill.adr_type == ADRType.SKILL
    assert skill.drakon_schema_ref.endswith(".json")
    assert skill.dump_path.endswith(".md")
    assert len(skill.invariants) == 2

    # Serialization
    d = skill.to_dict()
    restored = deserialize_adr(d)
    assert isinstance(restored, SkillADR)
    assert restored.dump_path == skill.dump_path
    assert restored.pseudocode == skill.pseudocode


def test_spec_adr_ssd_contracts():
    """Invariant ADR-010: SpecADR holds SSD acceptance criteria and operator editable flags."""
    spec = SpecADR(
        adr_id="ADR-SPEC-001",
        title="Planar Layout Invariant Specification",
        contract_schema={"properties": {"x": {"type": "number"}, "c": {"type": "integer", "const": 0}}},
        acceptance_criteria=["X=0 vertical skewer", "Line crossings C=0"],
        operator_editable=True,
        specification_text="All degradation branches must branch strictly right.",
    )

    assert spec.adr_type == ADRType.SPEC
    assert spec.operator_editable is True
    assert len(spec.acceptance_criteria) == 2

    d = spec.to_dict()
    restored = deserialize_adr(d)
    assert isinstance(restored, SpecADR)
    assert restored.acceptance_criteria == spec.acceptance_criteria


def test_tripartite_registry_bitemporal_operations():
    """Invariant ADR-001 & ADR-010: Registry supports bitemporal retrieval, type listing, and supersession."""
    reg = TripartiteAdrRegistry()

    # Register initial Data and Spec
    d1 = DataADR(
        adr_id="ADR-DATA-100",
        title="Baseline Metrics",
        data_payload={"qps": 100},
        valid_from="2026-09-01T00:00:00Z",
        tx_time="2026-09-01T00:00:00Z",
    )
    s1 = SpecADR(
        adr_id="ADR-SPEC-100",
        title="Performance Invariant",
        acceptance_criteria=["latency < 100ms"],
        valid_from="2026-09-01T00:00:00Z",
        tx_time="2026-09-01T00:00:00Z",
    )
    reg.register(d1)
    reg.register(s1)

    # Retrieval
    active_data = reg.list_by_type(ADRType.DATA, as_of_tv="2026-09-10T00:00:00Z")
    assert len(active_data) == 1
    assert active_data[0].adr_id == "ADR-DATA-100"

    active_specs = reg.list_by_type(ADRType.SPEC, as_of_tv="2026-09-10T00:00:00Z")
    assert len(active_specs) == 1
    assert active_specs[0].adr_id == "ADR-SPEC-100"

    # Supersede s1 with s2 (stricter latency)
    s2 = SpecADR(
        adr_id="ADR-SPEC-101",
        title="Strict Performance Invariant",
        acceptance_criteria=["latency < 50ms"],
        valid_from="2026-09-15T00:00:00Z",
        tx_time="2026-09-15T00:00:00Z",
    )
    success = reg.supersede(
        old_adr_id="ADR-SPEC-100",
        new_adr=s2,
        tv="2026-09-15T00:00:00Z",
        tt="2026-09-15T00:00:00Z",
    )
    assert success is True

    # Check state before supersession
    past_spec = reg.get("ADR-SPEC-100", as_of_tv="2026-09-10T00:00:00Z", as_of_tt="2026-09-10T00:00:00Z")
    assert past_spec is not None
    assert past_spec.adr_id == "ADR-SPEC-100"

    # Check state after supersession
    after_spec = reg.get("ADR-SPEC-100", as_of_tv="2026-09-16T00:00:00Z", as_of_tt="2026-09-16T00:00:00Z")
    assert after_spec is None  # Closed at 2026-09-15

    new_active = reg.get("ADR-SPEC-101", as_of_tv="2026-09-16T00:00:00Z", as_of_tt="2026-09-16T00:00:00Z")
    assert new_active is not None
    assert new_active.supersedes == "ADR-SPEC-100"


def test_bitemporal_external_pre_logging_axiom():
    """Invariant ADR-010: External API responses must be committed as DataADR before downstream consumption."""
    reg = TripartiteAdrRegistry()
    pre_logger = BitemporalExternalPreLogger(registry=reg)

    raw_response = {
        "status": "success",
        "records": [{"id": 1, "value": "A"}, {"id": 2, "value": "B"}],
        "latency_ms": 14.2
    }

    # Pre-log external call
    data_adr = pre_logger.pre_log_external_call(
        service_name="utopia_db",
        endpoint="/api/v1/entities",
        request_payload={"query": "active_invariants"},
        raw_response=raw_response,
        tv="2026-09-20T12:00:00Z"
    )

    assert data_adr.adr_id.startswith("ADR-DATA-EXT-UTOPIA_DB-")
    assert data_adr.source_uri == "ext://utopia_db/api/v1/entities"
    assert data_adr.data_payload["response"] == raw_response
    assert pre_logger.verify_pre_logged(data_adr.adr_id) is True

    # Unregistered ID fails verification
    assert pre_logger.verify_pre_logged("ADR-UNKNOWN-999") is False


def test_executable_macro_prompt_budget_and_render():
    """Invariant ADR-002 & ADR-005: Executable macro-prompt invariants capsule strictly <= 500 words."""
    invariants = [
        "ADR-001 (WORM Ledger): Inviolable immutability in Utopia DB.",
        "ADR-002 (Pure Stdlib): src/core/ uses zero external dependencies.",
        "ADR-008 (Planar Flow): Central skewer X=0, right-is-worse branching, crossings C=0.",
        "ADR-010 (Tripartite ADR): Unified Data, Skills, Specs with external pre-logging.",
    ]

    steps = [
        MacroPromptStep(
            step_id="step_1",
            node_id="node_start",
            kind=StepKind.FLOW_DIRECTIVE,
            label="Initialize Workflow",
            instructions="Check system readiness and active rules.",
            skewer_x=0.0,
            flow_directive=FlowDirective(directive_type=DirectiveType.BRANCH, target_down="step_2"),
            next_step_id="step_2",
        ),
        MacroPromptStep(
            step_id="step_2",
            node_id="node_query",
            kind=StepKind.ADR_QUERY,
            label="Fetch Active Invariants",
            instructions="Query active SpecADRs from Utopia DB.",
            skewer_x=0.0,
            adr_query=AdrQuery(operation="READ", target_adr_type="spec"),
            next_step_id="step_3",
        ),
        MacroPromptStep(
            step_id="step_3",
            node_id="node_action",
            kind=StepKind.SKILL_INVOCATION,
            label="Compile Pre-Flight Context",
            instructions="Execute skill to render active_rules.md.",
            skewer_x=0.0,
            skill_invocation=SkillInvocation(
                skill_id="ADR-SKILL-001",
                action_name="compile_preflight",
                target_parameters={"budget": 500}
            ),
            next_step_id="step_4",
        ),
        MacroPromptStep(
            step_id="step_4",
            node_id="node_check",
            kind=StepKind.FLOW_DIRECTIVE,
            label="Is Compile Latency < 50ms?",
            instructions="Verify compilation latency fitness gate.",
            skewer_x=0.0,
            flow_directive=FlowDirective(
                directive_type=DirectiveType.QUESTION,
                condition_expression="latency_ms < 50",
                target_down="step_end",
                target_right="step_fallback",
            ),
            next_step_id="step_end",
            alt_step_id="step_fallback",
        ),
        MacroPromptStep(
            step_id="step_fallback",
            node_id="node_degrade",
            kind=StepKind.SKILL_INVOCATION,
            label="Handle Compile Degradation",
            instructions="Log degradation and alert operator.",
            skewer_x=1.0,  # Branch right
            skill_invocation=SkillInvocation(skill_id="ADR-SKILL-DEGRADE", action_name="alert_operator"),
            next_step_id="step_end",
        ),
        MacroPromptStep(
            step_id="step_end",
            node_id="node_halt",
            kind=StepKind.TERMINAL,
            label="Finish Pipeline",
            instructions="Commit bitemporal transaction and exit.",
            skewer_x=0.0,
            flow_directive=FlowDirective(directive_type=DirectiveType.HALT),
        ),
    ]

    macro = ExecutableMacroPrompt(
        title="B-SDD Pre-Flight Pipeline Execution",
        schema_name="bsdd_preflight_pipeline",
        objective="Compile active architectural invariants under SLA < 50ms",
        active_invariants=invariants,
        steps=steps,
    )

    # Word budget check
    words = macro.invariants_word_count()
    assert words <= 500, f"Invariants capsule exceeded 500 words budget: {words}"
    assert words > 0

    # Render check
    md = macro.render_markdown()
    assert "# EXECUTABLE MACRO-PROMPT" in md
    assert "[SKEWER X=0]" in md
    assert "[ALT X=1.0]" in md
    assert "ADR-001" in md

    # Serialization roundtrip
    d = macro.to_dict()
    restored = ExecutableMacroPrompt.from_dict(d)
    assert restored.title == macro.title
    assert len(restored.steps) == len(macro.steps)
    assert restored.steps[3].flow_directive.directive_type == DirectiveType.QUESTION
    assert restored.steps[4].skewer_x == 1.0
