"""
B-SDD Sprint 011: UI Remediation, Button Optimization & Astryx Ergonomics
Automated Fitness Test Suite (ADR-002, ADR-005, ADR-008)
"""
import json
import re
from pathlib import Path
import pytest

from src.drakon.parser import DrakonParser
from src.drakon.validator import DrakonValidator
from src.core.compiler import BSDDCompiler

ROOT = Path(__file__).resolve().parent.parent


def test_spec_011_word_budget_sub_500_words():
    """Verify SPEC-011 adheres strictly to the sub-500 word invariant (ADR-002)."""
    spec_path = ROOT / "specs" / "011-ui-remediation" / "spec.md"
    assert spec_path.exists(), "specs/011-ui-remediation/spec.md must exist"
    content = spec_path.read_text(encoding="utf-8")
    words = len(content.split())
    assert words < 500, f"SPEC-011 word budget exceeded: {words} words >= 500 ceiling"


def test_spec_011_drakon_planar_invariants():
    """Verify Sprint 011 DRAKON schema is 100% planar with zero line crossings (C=0)."""
    drakon_path = ROOT / "specs" / "011-ui-remediation" / "logic.drakon.json"
    assert drakon_path.exists(), "logic.drakon.json must exist"
    data = json.loads(drakon_path.read_text(encoding="utf-8"))
    schema = DrakonParser.parse_dict(data)
    validator = DrakonValidator()
    res = validator.validate(schema)
    assert res.is_valid, f"DRAKON validation failed with errors: {res.errors}"
    assert res.stats.get("node_count", 0) >= 6, "Must contain at least 6 nodes in the pipeline"


def test_remediation_intake_files_exist():
    """Verify remediation documentation files exist and are ready for user input."""
    input_doc = ROOT / "docs" / "ui_remediation" / "remediation_input.md"
    audit_doc = ROOT / "docs" / "ui_remediation" / "ui_controls_audit.md"
    assert input_doc.exists(), "docs/ui_remediation/remediation_input.md must exist"
    assert audit_doc.exists(), "docs/ui_remediation/ui_controls_audit.md must exist"
    
    content = input_doc.read_text(encoding="utf-8")
    assert "Видалення" in content
    assert "Рефакторингу" in content
    assert "Drakon Palette" in content or "Палітри ДРАКОН" in content


def test_remediation_intake_parser():
    """Test helper logic for parsing action items from remediation_input.md."""
    input_doc = ROOT / "docs" / "ui_remediation" / "remediation_input.md"
    content = input_doc.read_text(encoding="utf-8")
    
    # Check that sections are extractable via regex
    delete_section = re.search(r"## 1\. Елементи та Кнопки для Видалення.*?(?=## 2|\Z)", content, re.DOTALL)
    assert delete_section is not None, "Section 1 (Delete) must be identifiable"
    
    refactor_section = re.search(r"## 2\. Елементи для Рефакторингу.*?(?=## 3|\Z)", content, re.DOTALL)
    assert refactor_section is not None, "Section 2 (Refactor) must be identifiable"


def test_ui_zone_boundary_integrity():
    """Verify AstryxZoneBoundary is maintained in App.tsx without regressions."""
    app_tsx = ROOT / "b-sdd-ui" / "src" / "App.tsx"
    assert app_tsx.exists(), "b-sdd-ui/src/App.tsx must exist"
    content = app_tsx.read_text(encoding="utf-8")
    assert "AstryxZoneBoundary" in content, "Must wrap zones in AstryxZoneBoundary (ADR-FE-001)"
