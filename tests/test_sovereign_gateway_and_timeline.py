import json
from pathlib import Path
from src.drakon.parser import DrakonParser
from src.drakon.validator import DrakonValidator

def test_sovereign_copilot_template_planar_valid():
    """Verify planar invariants for the sovereign copilot pipeline template."""
    tmpl_path = Path("src/drakon/templates/sovereign_copilot_and_gateway.json")
    assert tmpl_path.exists(), "Template must exist"
    data = json.loads(tmpl_path.read_text(encoding="utf-8"))
    schema = DrakonParser.parse_dict(data)
    validator = DrakonValidator()
    result = validator.validate(schema)
    assert result.is_valid, f"Template planar validation failed: {result.errors}"
    assert len(schema.nodes) >= 6, "Expected at least 6 nodes in the pipeline"

def test_temporal_timeline_extraction():
    """Verify git timeline extraction returns valid commits and timestamps."""
    from src.server.workbench_server import extract_git_timeline
    timeline = extract_git_timeline()
    assert isinstance(timeline, dict)
    assert "commits" in timeline
    assert "min_time" in timeline
    assert "max_time" in timeline
    assert len(timeline["commits"]) > 0
    assert timeline["min_time"] <= timeline["max_time"]
    assert "hash" in timeline["commits"][0]
    assert "timestamp" in timeline["commits"][0]
