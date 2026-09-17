import json
from pathlib import Path
from src.drakon.parser import DrakonParser
from src.drakon.validator import DrakonValidator

def test_pipeline_catalog_templates_have_valid_nodes():
    templates_dir = Path('src/drakon/templates')
    templates = list(templates_dir.glob('*.json'))
    assert len(templates) >= 5, "At least 5 standard templates required"
    for tmpl in templates:
        data = json.loads(tmpl.read_text(encoding='utf-8'))
        nodes = data.get('nodes', [])
        assert len(nodes) > 0, f"Template {tmpl.name} must have nodes > 0"

def test_drakon_bridge_planar_invariants():
    validator = DrakonValidator()
    templates_dir = Path('src/drakon/templates')
    for tmpl in templates_dir.glob('*.json'):
        data = json.loads(tmpl.read_text(encoding='utf-8'))
        schema = DrakonParser.parse_dict(data)
        res = validator.validate(schema)
        assert res.is_valid, f"Template {tmpl.name} validation failed: {res.errors}"
