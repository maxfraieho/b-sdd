"""
Unit and Invariant Fitness Tests for DRAKON Schema Validator (ADR-008).
Validates:
1. Pure Python Standard Library in src/drakon/.
2. Vertical Skewer ("Шампур") invariants.
3. Right-is-Worse ("Чем правее, тем хуже") branching & severity monotonicity.
4. Planarity and Zero Line Crossings.
5. Silhouette Architecture ("Силуэт") ordering and termination.
6. Bitemporal ADR semantic binding and rejection of superseded invariants.
7. Topology immutability and leaf action node bounding.
8. CLI command execution (validate, parse, prompt).
"""
import ast
import json
import sys
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.drakon import (
    DrakonParser,
    DrakonValidator,
    DrakonSchema,
    DrakonNode,
    DrakonEdges,
    DrakonNodeType,
    SemanticBinding,
)


def test_zero_third_party_dependencies_in_drakon():
    """Invariant: All modules in src/drakon/ must strictly use Python standard library."""
    drakon_dir = ROOT / "src" / "drakon"
    stdlib_modules = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else {
        "os", "sys", "re", "json", "time", "sqlite3", "hashlib", "pathlib", "typing",
        "subprocess", "logging", "datetime", "uuid", "argparse", "unittest", "shutil",
        "tempfile", "functools", "itertools", "collections", "abc", "contextlib", "dataclasses", "enum", "math"
    }
    internal_pkgs = {"src"}

    for py_file in drakon_dir.rglob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(py_file))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split(".")[0]
                    assert root_mod in stdlib_modules or root_mod in internal_pkgs, (
                        f"External third-party import '{alias.name}' detected in {py_file.name}"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_mod = node.module.split(".")[0]
                    assert root_mod in stdlib_modules or root_mod in internal_pkgs, (
                        f"External third-party from-import '{node.module}' detected in {py_file.name}"
                    )


def test_parse_classic_and_ir_formats():
    """Invariant: DrakonParser must accurately parse classic DrakonHub JSON and canonical DRAKON-IR."""
    classic_json = {
        "name": "Classic Diagram",
        "items": {
            "1": {"type": "header", "content": "Start", "one": "2"},
            "2": {"type": "action", "content": "Do Work", "one": "3"},
            "3": {"type": "question", "content": "OK?", "one": "4", "two": "5"},
            "4": {"type": "end", "content": "Done"},
            "5": {"type": "end", "content": "Failed"}
        }
    }
    schema_classic = DrakonParser.parse_dict(classic_json)
    assert schema_classic.name == "Classic Diagram"
    assert len(schema_classic.nodes) == 5
    assert schema_classic.nodes["1"].normalized_type == DrakonNodeType.HEADLINE.value
    assert schema_classic.nodes["3"].edges.down == "4"
    assert schema_classic.nodes["3"].edges.right == "5"

    ir_json = {
        "schema_version": "1.0",
        "name": "IR Diagram",
        "nodes": [
            {
                "node_id": "start",
                "node_type": "headline",
                "label": "Start Node",
                "edges": {"down": "step1"}
            },
            {
                "node_id": "step1",
                "node_type": "action",
                "label": "Action 1",
                "edges": {"down": "end"}
            },
            {
                "node_id": "end",
                "node_type": "end",
                "label": "End Node",
                "edges": {}
            }
        ]
    }
    schema_ir = DrakonParser.parse_dict(ir_json)
    assert schema_ir.name == "IR Diagram"
    assert len(schema_ir.nodes) == 3
    ir_exported = json.loads(DrakonParser.to_ir_json(schema_ir))
    assert ir_exported["schema_version"] == "1.0"
    assert len(ir_exported["nodes"]) == 3


def test_vertical_skewer_valid_and_deviations():
    """Invariant 1: Vertical Skewer ("Шампур").
    Primary success path must be strictly vertical. Leftward deviation or horizontal offset is forbidden.
    """
    validator = DrakonValidator(root_dir=ROOT)

    # 1. Valid vertical skewer
    valid_schema = DrakonSchema(
        name="Valid Skewer",
        nodes={
            "start": DrakonNode(node_id="start", node_type="headline", x=0.0, y=0.0, edges=DrakonEdges(down="act1")),
            "act1": DrakonNode(node_id="act1", node_type="action", x=0.0, y=2.0, edges=DrakonEdges(down="end1")),
            "end1": DrakonNode(node_id="end1", node_type="end", x=0.0, y=4.0, edges=DrakonEdges())
        }
    )
    res_valid = validator.validate(valid_schema)
    assert res_valid.is_valid, [e.message for e in res_valid.errors]

    # 2. Skewer horizontal misalignment (x differs on skewer)
    invalid_misaligned = DrakonSchema(
        name="Misaligned Skewer",
        nodes={
            "start": DrakonNode(node_id="start", node_type="headline", x=0.0, y=0.0, edges=DrakonEdges(down="act1")),
            "act1": DrakonNode(node_id="act1", node_type="action", x=2.0, y=2.0, edges=DrakonEdges(down="end1")),  # x shifted!
            "end1": DrakonNode(node_id="end1", node_type="end", x=0.0, y=4.0, edges=DrakonEdges())
        }
    )
    res_misaligned = validator.validate(invalid_misaligned)
    assert not res_misaligned.is_valid
    assert any(e.rule == "VERTICAL_SKEWER" and "verticality violation" in e.message for e in res_misaligned.errors)

    # 3. Prohibited leftward deviation (x_target < x_skewer)
    invalid_left_branch = DrakonSchema(
        name="Leftward Deviation",
        nodes={
            "start": DrakonNode(node_id="start", node_type="headline", x=2.0, y=0.0, edges=DrakonEdges(down="act1")),
            "act1": DrakonNode(node_id="act1", node_type="action", x=2.0, y=2.0, edges=DrakonEdges(down="end1")),
            "end1": DrakonNode(node_id="end1", node_type="end", x=-1.0, y=4.0, edges=DrakonEdges())  # -1.0 < 2.0 !
        }
    )
    res_left = validator.validate(invalid_left_branch)
    assert not res_left.is_valid
    assert any(e.rule == "VERTICAL_SKEWER" and "leftward deviation" in e.message for e in res_left.errors)


def test_right_is_worse_branching():
    """Invariant 2: Right-is-Worse ("Чем правее, тем хуже").
    Normal execution flows down; degradation and failovers branch strictly right.
    Branching left is prohibited.
    """
    validator = DrakonValidator(root_dir=ROOT)

    # 1. Valid down & right
    valid_schema = DrakonSchema(
        name="Valid Decision",
        nodes={
            "start": DrakonNode(node_id="start", node_type="headline", x=0.0, y=0.0, edges=DrakonEdges(down="q1")),
            "q1": DrakonNode(node_id="q1", node_type="question", x=0.0, y=2.0, edges=DrakonEdges(down="happy", right="degrade")),
            "happy": DrakonNode(node_id="happy", node_type="end", x=0.0, y=4.0, edges=DrakonEdges()),
            "degrade": DrakonNode(node_id="degrade", node_type="end", x=3.0, y=2.0, edges=DrakonEdges())
        }
    )
    res_valid = validator.validate(valid_schema)
    assert res_valid.is_valid, [e.message for e in res_valid.errors]

    # 2. Invalid: Question branches left (x_right < x_node)
    invalid_left_decision = DrakonSchema(
        name="Left Branch Decision",
        nodes={
            "start": DrakonNode(node_id="start", node_type="headline", x=2.0, y=0.0, edges=DrakonEdges(down="q1")),
            "q1": DrakonNode(node_id="q1", node_type="question", x=2.0, y=2.0, edges=DrakonEdges(down="happy", right="degrade")),
            "happy": DrakonNode(node_id="happy", node_type="end", x=2.0, y=4.0, edges=DrakonEdges()),
            "degrade": DrakonNode(node_id="degrade", node_type="end", x=0.0, y=2.0, edges=DrakonEdges())  # x=0 < 2!
        }
    )
    res_left = validator.validate(invalid_left_decision)
    assert not res_left.is_valid
    assert any(e.rule == "RIGHT_IS_WORSE" and "branches left" in e.message for e in res_left.errors)


def test_monotonic_severity_ordering():
    """Invariant 2 (Ordering): Higher severity degradation must be positioned further right."""
    validator = DrakonValidator(root_dir=ROOT)

    # Non-monotonic severity: severe placed to the left of mild
    invalid_schema = DrakonSchema(
        name="Non-monotonic Severity",
        nodes={
            "start": DrakonNode(node_id="start", node_type="headline", x=0.0, y=0.0, edges=DrakonEdges(down="q1")),
            "q1": DrakonNode(
                node_id="q1",
                node_type="question",
                x=0.0,
                y=2.0,
                edges=DrakonEdges(
                    down="happy",
                    right="case_severe",
                    extra={"case_severe": "case_severe", "case_mild": "case_mild"}
                )
            ),
            "happy": DrakonNode(node_id="happy", node_type="end", x=0.0, y=4.0, edges=DrakonEdges()),
            "case_severe": DrakonNode(
                node_id="case_severe",
                node_type="action",
                x=2.0,
                y=2.0,
                edges=DrakonEdges(down="end_err"),
                semantic_binding=SemanticBinding(severity="fatal")  # weight 4
            ),
            "case_mild": DrakonNode(
                node_id="case_mild",
                node_type="action",
                x=4.0,
                y=2.0,
                edges=DrakonEdges(down="end_err"),
                semantic_binding=SemanticBinding(severity="mild")   # weight 1 placed at x=4.0!
            ),
            "end_err": DrakonNode(node_id="end_err", node_type="end", x=3.0, y=6.0, edges=DrakonEdges())
        }
    )
    res = validator.validate(invalid_schema)
    assert not res.is_valid
    assert any(e.rule == "RIGHT_IS_WORSE" and "Non-monotonic severity ordering" in e.message for e in res.errors)


def test_zero_line_crossings_planarity():
    """Invariant 3: Planarity & Zero Line Crossings. Control edges must not intersect."""
    validator = DrakonValidator(root_dir=ROOT)

    # Edge A: (0, 1) -> (4, 1) (horizontal)
    # Edge B: (2, 0) -> (2, 4) (vertical)
    # They cross at (2, 1)!
    crossing_schema = DrakonSchema(
        name="Crossing Lines Diagram",
        nodes={
            "start": DrakonNode(node_id="start", node_type="headline", x=2.0, y=0.0, edges=DrakonEdges(down="node_v_bot")),
            "node_v_bot": DrakonNode(node_id="node_v_bot", node_type="end", x=2.0, y=4.0, edges=DrakonEdges()),
            "node_h_left": DrakonNode(node_id="node_h_left", node_type="question", x=0.0, y=1.0, edges=DrakonEdges(down="node_h_end", right="node_h_right")),
            "node_h_right": DrakonNode(node_id="node_h_right", node_type="end", x=4.0, y=1.0, edges=DrakonEdges()),
            "node_h_end": DrakonNode(node_id="node_h_end", node_type="end", x=0.0, y=3.0, edges=DrakonEdges())
        }
    )
    res = validator.validate(crossing_schema)
    assert not res.is_valid
    assert any(e.rule == "ZERO_CROSSINGS" and "line crossing violation" in e.message for e in res.errors)


def test_silhouette_architecture_ordering():
    """Invariant 4: Silhouette Architecture ("Силуэт").
    Multiple branches must be ordered monotonically left-to-right.
    """
    validator = DrakonValidator(root_dir=ROOT)

    # Invalid: Branch 1 is to the left of Branch 0
    invalid_branches = DrakonSchema(
        name="Inverted Silhouette",
        branch_order=["b0", "b1"],
        nodes={
            "b0": DrakonNode(node_id="b0", node_type="branch", branch_id=0, x=10.0, y=0.0, edges=DrakonEdges(down="route0")),
            "route0": DrakonNode(node_id="route0", node_type="silhouette_route", x=10.0, y=2.0, edges=DrakonEdges(down="b1")),
            "b1": DrakonNode(node_id="b1", node_type="branch", branch_id=1, x=5.0, y=0.0, edges=DrakonEdges(down="end1")),  # x=5 < 10!
            "end1": DrakonNode(node_id="end1", node_type="end", x=5.0, y=2.0, edges=DrakonEdges())
        }
    )
    res = validator.validate(invalid_branches)
    assert not res.is_valid
    assert any(e.rule == "SILHOUETTE_ORDER" and "Silhouette branch ordering violation" in e.message for e in res.errors)


def test_bitemporal_adr_semantic_binding_rejection():
    """Invariant 5: Bitemporal ADR Semantic Binding.
    Nodes bound to superseded ADRs or expired valid_to horizons must be rejected.
    """
    validator = DrakonValidator(root_dir=ROOT)

    # 1. Active vs Superseded ADR invariant
    active_set = {"ADR-008", "ADR-007"}
    superseded_set = {"ADR-001-OLD", "ADR-003-OLD"}

    schema_superseded = DrakonSchema(
        name="Superseded ADR Binding",
        nodes={
            "start": DrakonNode(
                node_id="start",
                node_type="headline",
                x=0.0,
                y=0.0,
                edges=DrakonEdges(down="end"),
                semantic_binding=SemanticBinding(adr_invariant_id="ADR-001-OLD")
            ),
            "end": DrakonNode(node_id="end", node_type="end", x=0.0, y=2.0, edges=DrakonEdges())
        }
    )
    res_super = validator.validate(schema_superseded, active_invariants=active_set, superseded_invariants=superseded_set)
    assert not res_super.is_valid
    assert any(e.rule == "BITEMPORAL_INVARIANT" and "superseded ADR invariant" in e.message for e in res_super.errors)

    # 2. Expired temporal horizon (valid_to <= NOW)
    past_iso = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    schema_expired = DrakonSchema(
        name="Expired Horizon Binding",
        nodes={
            "start": DrakonNode(
                node_id="start",
                node_type="headline",
                x=0.0,
                y=0.0,
                edges=DrakonEdges(down="end"),
                semantic_binding=SemanticBinding(
                    adr_invariant_id="ADR-008",
                    temporal_scope={"valid_to": past_iso}
                )
            ),
            "end": DrakonNode(node_id="end", node_type="end", x=0.0, y=2.0, edges=DrakonEdges())
        }
    )
    res_expired = validator.validate(schema_expired, active_invariants=active_set, superseded_invariants=superseded_set)
    assert not res_expired.is_valid
    assert any(e.rule == "BITEMPORAL_INVARIANT" and "temporal scope expired" in e.message for e in res_expired.errors)


def test_topology_immutability_leaf_action_bounding():
    """Invariant 6: Action nodes must not alter control flow topology (no branching)."""
    validator = DrakonValidator(root_dir=ROOT)

    invalid_action_branching = DrakonSchema(
        name="Action Node Branching Violation",
        nodes={
            "start": DrakonNode(node_id="start", node_type="headline", x=0.0, y=0.0, edges=DrakonEdges(down="act1")),
            "act1": DrakonNode(
                node_id="act1",
                node_type="action",
                x=0.0,
                y=2.0,
                edges=DrakonEdges(down="end1", right="end2")  # Action node cannot branch right!
            ),
            "end1": DrakonNode(node_id="end1", node_type="end", x=0.0, y=4.0, edges=DrakonEdges()),
            "end2": DrakonNode(node_id="end2", node_type="end", x=2.0, y=2.0, edges=DrakonEdges())
        }
    )
    res = validator.validate(invalid_action_branching)
    assert not res.is_valid
    assert any(e.rule == "TOPOLOGY_IMMUTABILITY" and "contains a right-branch transition" in e.message for e in res.errors)


def test_cli_drakon_commands(tmp_path):
    """Test CLI drakon validate, parse, and prompt commands."""
    spec_diagram = ROOT / "specs" / "004-multi-session-handoff-and-drakon" / "logic.drakon.json"
    assert spec_diagram.exists()

    # 1. drakon validate
    cmd_val = subprocess.run(
        [sys.executable, "-m", "src.cli.main", "drakon", "validate", str(spec_diagram)],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    assert cmd_val.returncode == 0
    assert "topologically and bitemporally VALID" in cmd_val.stdout

    # 2. drakon parse
    cmd_parse = subprocess.run(
        [sys.executable, "-m", "src.cli.main", "drakon", "parse", str(spec_diagram)],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    assert cmd_parse.returncode == 0
    parsed_json = json.loads(cmd_parse.stdout)
    assert parsed_json["schema_version"] == "1.0"
    assert len(parsed_json["nodes"]) == 12

    # 3. drakon prompt
    cmd_prompt = subprocess.run(
        [sys.executable, "-m", "src.cli.main", "drakon", "prompt", str(spec_diagram)],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    assert cmd_prompt.returncode == 0
    assert "DRAKON Algorithmic Execution Specification" in cmd_prompt.stdout
    assert "TOPOLOGY_IMMUTABILITY" in cmd_prompt.stdout
