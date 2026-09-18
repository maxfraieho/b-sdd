"""
B-SDD Sprint 012: Utopia DB DAG, Headless Pi Harness Orchestration & Dual-Contour Ingestion
Automated Fitness Test Suite (ADR-002, ADR-005, ADR-008, ADR-013)
"""
import json
import re
from pathlib import Path
import pytest

from src.core.compiler import BSDDCompiler
from src.drakon.parser import DrakonParser
from src.drakon.validator import DrakonValidator

ROOT = Path(__file__).resolve().parent.parent


def test_spec_012_word_budget_sub_500_words():
    """Verify SPEC-012 adheres strictly to the sub-500 word invariant (ADR-002, INV-012-01)."""
    spec_path = ROOT / "specs" / "012-dag-and-pi-harness" / "spec.md"
    assert spec_path.exists(), "specs/012-dag-and-pi-harness/spec.md must exist"
    content = spec_path.read_text(encoding="utf-8")
    words = len(content.split())
    assert words < 500, f"SPEC-012 word budget exceeded: {words} words >= 500 ceiling"


def test_spec_012_drakon_planar_invariants():
    """Verify Sprint 012 DRAKON schemas are 100% planar with zero line crossings (C=0)."""
    logic_path = ROOT / "specs" / "012-dag-and-pi-harness" / "logic.drakon.json"
    struct_path = ROOT / "specs" / "012-dag-and-pi-harness" / "structure.drakon.json"
    assert logic_path.exists(), "logic.drakon.json must exist"
    assert struct_path.exists(), "structure.drakon.json must exist"

    validator = DrakonValidator()
    
    # Test logic flow schema
    data_logic = json.loads(logic_path.read_text(encoding="utf-8"))
    schema_logic = DrakonParser.parse_dict(data_logic)
    res_logic = validator.validate(schema_logic)
    assert res_logic.is_valid, f"Logic schema validation failed: {res_logic.errors}"
    assert res_logic.stats.get("node_count", 0) >= 6

    # Test structure schema
    data_struct = json.loads(struct_path.read_text(encoding="utf-8"))
    schema_struct = DrakonParser.parse_dict(data_struct)
    res_struct = validator.validate(schema_struct)
    assert res_struct.is_valid, f"Structure schema validation failed: {res_struct.errors}"


def test_utopia_dag_proxy_filtering():
    """Test Utopia DB DAG proxy filtering by Valid Time (Tv) (INV-012-04)."""
    from src.adapters.utopia_db import UtopiaDBAdapter

    adapter = UtopiaDBAdapter()
    raw_graph = {
        "nodes": [
            {"id": "ADR-001", "title": "Bitemporal Intent Graph", "valid_from": 1, "valid_to": None, "status": "accepted"},
            {"id": "ADR-008", "title": "Drakon Visual Logic", "valid_from": 10, "valid_to": None, "status": "accepted"},
            {"id": "ADR-009-OLD", "title": "Legacy Palette", "valid_from": 5, "valid_to": 15, "status": "superseded"},
            {"id": "ADR-013", "title": "Utopia DAG & Pi", "valid_from": 18, "valid_to": None, "status": "proposed"},
        ],
        "edges": [
            {"source": "ADR-008", "target": "ADR-001", "type": "depends-on"},
            {"source": "ADR-009-OLD", "target": "ADR-001", "type": "depends-on"},
            {"source": "ADR-013", "target": "ADR-008", "type": "depends-on"},
        ]
    }

    # Filter at Tv = 12 (Sept 12, 2026)
    # ADR-009-OLD is active (valid_to is 15, which is > 12)
    # ADR-013 is not yet valid (valid_from is 18 > 12)
    filtered_12 = adapter.filter_dag_by_time(raw_graph, valid_time_day=12)
    node_ids_12 = {n["id"] for n in filtered_12["nodes"]}
    assert "ADR-001" in node_ids_12
    assert "ADR-008" in node_ids_12
    assert "ADR-009-OLD" in node_ids_12
    assert "ADR-013" not in node_ids_12  # Future decision pruned

    # Filter at Tv = 16 (Sept 16, 2026)
    # ADR-009-OLD is now superseded (valid_to is 15 <= 16)
    filtered_16 = adapter.filter_dag_by_time(raw_graph, valid_time_day=16)
    adr_9_status = next(n["status"] for n in filtered_16["nodes"] if n["id"] == "ADR-009-OLD")
    assert adr_9_status == "superseded"


def test_pi_agents_context_budget():
    """Verify AGENTS.md generated for Pi Harness strictly stays under 500 words (INV-012-01)."""
    from src.adapters.pi_harness import PiHarnessRunner

    runner = PiHarnessRunner(project_root=ROOT)
    agents_md = runner.generate_agents_context(
        feature_id="012-dag-and-pi-harness",
        target_action_id="step_proxy_utopia",
        prompt="Implement GET /api/utopia/graph with Tv filter."
    )

    words = len(agents_md.split())
    assert words < 500, f"AGENTS.md exceeded 500 words: {words} words"
    assert "MANDATORY ARCHITECTURAL INVARIANTS" in agents_md or "INVARIANTS" in agents_md
    assert "step_proxy_utopia" in agents_md


def test_pi_headless_leaf_isolation():
    """Verify Pi Harness strictly restricts mutations to leaf Action implementation (INV-012-03)."""
    from src.adapters.pi_harness import PiHarnessRunner

    runner = PiHarnessRunner(project_root=ROOT)

    original_schema = {
        "nodes": [
            {"node_id": "start", "node_type": "headline", "edges": {"down": "act_1"}},
            {"node_id": "act_1", "node_type": "action", "edges": {"down": "end"}},
            {"node_id": "end", "node_type": "end", "edges": {"down": None}},
        ]
    }

    # Case A: Valid code implementation with zero topology change
    valid_patch = {
        "files_modified": ["src/server/workbench_server.py"],
        "schema_mutation": None
    }
    assert runner.validate_execution_isolation(original_schema, valid_patch) is True

    # Case B: Illegal attempt by Pi to alter DRAKON edges or add unauthorized nodes
    illegal_patch = {
        "files_modified": ["specs/012-dag-and-pi-harness/logic.drakon.json"],
        "schema_mutation": {
            "nodes": [
                {"node_id": "start", "node_type": "headline", "edges": {"down": "rogue_node"}},
                {"node_id": "rogue_node", "node_type": "action", "edges": {"down": "end"}},
                {"node_id": "end", "node_type": "end", "edges": {"down": None}},
            ]
        }
    }
    assert runner.validate_execution_isolation(original_schema, illegal_patch) is False


def test_brownfield_ingestion_bootstrap():
    """Verify Dual-Contour Ingestion Engine synthesizes base MADR 3.0 records (INV-012-05)."""
    from src.adapters.gitnexus_graph import BrownfieldIngestionEngine

    engine = BrownfieldIngestionEngine(project_root=ROOT)
    sample_files = [
        "src/core/compiler.py",
        "src/server/workbench_server.py",
        "src/adapters/utopia_db.py"
    ]
    
    analysis = engine.analyze_ast_components(sample_files)
    assert "components" in analysis
    assert len(analysis["components"]) >= 2

    # Scaffolding base MADR 3.0
    madr_content = engine.generate_bootstrap_madr(
        component="core",
        title="Automated Foundation Intent for core",
        detected_modules=["src/core/compiler.py"]
    )
    assert "# ADR-" in madr_content
    assert "## Context" in madr_content
    assert "## Decision" in madr_content
    assert "## Consequences" in madr_content
    assert "## Invariants" in madr_content
