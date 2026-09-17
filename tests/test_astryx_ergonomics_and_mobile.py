import json
from pathlib import Path
from src.drakon.parser import DrakonParser
from src.drakon.validator import DrakonValidator

ROOT_DIR = Path(__file__).resolve().parent.parent

def test_astryx_mobile_template_planar():
    """Verify planar invariants for Sprint 010 Astryx & Mobile template."""
    tmpl_path = ROOT_DIR / "src/drakon/templates/astryx_ergonomics_and_mobile.json"
    assert tmpl_path.exists()
    data = json.loads(tmpl_path.read_text(encoding="utf-8"))
    schema = DrakonParser.parse_dict(data)
    validator = DrakonValidator()
    result = validator.validate(schema)
    assert result.is_valid, f"Template planar errors: {result.errors}"
    assert len(schema.nodes) >= 6

def test_mobile_navigation_renders_adr_library_button():
    """Verify DEF-04: onOpenAdrLibrary is destructured and rendered."""
    nav_path = ROOT_DIR / "b-sdd-ui/src/components/MobileNavigation.tsx"
    assert nav_path.exists()
    content = nav_path.read_text(encoding="utf-8")
    assert "onOpenAdrLibrary," in content
    assert "title=\"ADR Бібліотека\"" in content
    assert "BookOpen" in content

def test_token_gauge_word_budget_and_astryx_tokens():
    """Verify INV-T1 and INV-AST: Word budget semantics and Astryx tokens."""
    gauge_path = ROOT_DIR / "b-sdd-ui/src/components/CopilotPanel/TokenGauge.tsx"
    assert gauge_path.exists()
    content = gauge_path.read_text(encoding="utf-8")
    assert "Active Rules Word Budget" in content
    assert "bg-card" in content
    assert "border-border-subtle" in content
    assert "bg-canvas" in content
    # Verify no hardcoded dark hex colors
    assert "#141b27" not in content
    assert "#1e293b" not in content
    assert "#090d13" not in content

def test_timeline_slider_dynamic_range():
    """Verify DEF-08: TimelineSlider supports dynamic date ranges."""
    slider_path = ROOT_DIR / "b-sdd-ui/src/components/BitemporalRadar/TimelineSlider.tsx"
    assert slider_path.exists()
    content = slider_path.read_text(encoding="utf-8")
    assert "maxLimit" in content
    assert "minLimit" in content
    assert "minDay" in content
    assert "maxDay" in content
