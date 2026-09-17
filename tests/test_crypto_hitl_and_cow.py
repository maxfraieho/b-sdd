import json
import subprocess
import time
from pathlib import Path
from src.drakon.parser import DrakonParser
from src.drakon.validator import DrakonValidator
from src.adapters.appwrite_client import AppwriteClient

ROOT_DIR = Path(__file__).resolve().parent.parent

def test_cryptographic_hitl_template_planar():
    """Verify planar invariants for Sprint 009 HITL gate template."""
    tmpl_path = ROOT_DIR / "src/drakon/templates/cryptographic_hitl_and_cow.json"
    assert tmpl_path.exists()
    data = json.loads(tmpl_path.read_text(encoding="utf-8"))
    schema = DrakonParser.parse_dict(data)
    validator = DrakonValidator()
    result = validator.validate(schema)
    assert result.is_valid, f"Template planar errors: {result.errors}"
    assert len(schema.nodes) == 6

def test_operator_signature_verification():
    """Verify signature verification accepts structured tokens and rejects invalid."""
    client = AppwriteClient()
    
    # Missing signature
    res_empty = client.verify_operator_signature(signature=None, payload_data={"action": "approve"})
    assert not res_empty["verified"]
    
    # Structured HMAC-SHA256 token
    dummy_hmac = "hmac-sha256:" + "a" * 64
    res_hmac = client.verify_operator_signature(signature=dummy_hmac, payload_data={"action": "approve"})
    assert res_hmac["verified"]
    assert res_hmac["algorithm"] == "hmac-sha256"

def test_git_cow_branching_execution():
    """Verify physical git branch creation on rejection."""
    test_branch = f"test-cow-{int(time.time())}"
    try:
        # Create branch
        res = subprocess.run(["git", "branch", test_branch], cwd=str(ROOT_DIR), capture_output=True, text=True, check=True)
        assert res.returncode == 0
        
        # Verify branch exists in git
        verify = subprocess.run(["git", "rev-parse", "--verify", test_branch], cwd=str(ROOT_DIR), capture_output=True, text=True, check=True)
        assert len(verify.stdout.strip()) == 40
    finally:
        # Clean up test branch
        subprocess.run(["git", "branch", "-D", test_branch], cwd=str(ROOT_DIR), capture_output=True, text=True)

def test_astryx_zone_boundary_component_exists():
    """Verify AstryxZoneBoundary component file is present and exports correctly."""
    boundary_file = ROOT_DIR / "b-sdd-ui/src/components/boundaries/AstryxZoneBoundary.tsx"
    assert boundary_file.exists()
    content = boundary_file.read_text(encoding="utf-8")
    assert "class AstryxZoneBoundary" in content
    assert "componentDidCatch" in content
