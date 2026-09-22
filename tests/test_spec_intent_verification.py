"""
Unit and Integration Tests for Vector 3 Semantic Spec-to-Code Intent Verification.
Sprint 031 - Track A.
100% Python Standard Library Compliance (ADR-002).
"""
import json
import pytest
from pathlib import Path

from src.core.dto.intent_verification import (
    IntentGraphDTO,
    CodeASTSignaturesDTO,
    IntentVerificationResultDTO,
    IntentVerdict
)
from src.core.intent_verification.spec_extractor import SpecIntentExtractor
from src.core.intent_verification.code_ast_encoder import CodeASTEncoder
from src.core.intent_verification.laya_intent_client import LayaIntentClient
from src.core.intent_verification.intent_gatekeeper import IntentGatekeeper


SAMPLE_SKILL_MD = """---
name: sample-demo-skill
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [b-sdd, safe-refactor]
---

# Sample Demo Skill

## 1. Architectural Context & Negative Invariants
- ADR Compliance: ADR-015, ADR-016
- Negative Invariants:
  - NEVER bypass invariant checks.

## 2. Algorithmic Workflow (ADR-016 Standard)
<!-- ALGORITHMIC_PSEUDOCODE_START -->
ALGORITHM ExecuteSampleDemoSkill
INPUT:
    context: dict
OUTPUT:
    status: str
BEGIN
    TRY
        ASSERT context != null
        EXECUTE ValidatePreconditions(context)
        IF CheckIntegrity() THEN
            CALL_SKILL(safe-refactor, {target: context.file})
        ELSE
            BRANCH_RIGHT(X=4.0): Failure
            HALT_AND_DEGRADE("INTEGRITY_FAIL")
        FI
        ASSERT VerifyOutput()
        RETURN "SUCCESS"
    CATCH Error AS e
        HALT_AND_DEGRADE(e.Message)
    END
END
<!-- ALGORITHMIC_PSEUDOCODE_END -->

## 3. DRAKON Visual Workflow
<!-- DRAKON_VISUAL_FLOW_START -->
- Total Algorithmic Nodes: 6
<!-- DRAKON_VISUAL_FLOW_END -->
"""

SAMPLE_DRAKON_JSON = {
    "name": "sample-demo-skill",
    "nodes": [
        {"id": "node_1", "type": "headline", "title": "Start", "x": 0.0, "y": 0.0},
        {"id": "node_2", "type": "action", "title": "ASSERT context != null", "x": 0.0, "y": 2.0},
        {"id": "node_3", "type": "question", "title": "CheckIntegrity?", "x": 0.0, "y": 4.0},
        {"id": "node_4", "type": "insertion", "title": "CALL_SKILL(safe-refactor)", "x": 0.0, "y": 6.0},
        {"id": "node_5", "type": "action", "title": "ASSERT VerifyOutput()", "x": 0.0, "y": 8.0},
        {"id": "node_6", "type": "end", "title": "End", "x": 0.0, "y": 10.0}
    ]
}


SAMPLE_COMPLIANT_CODE = """
def execute_sample(context):
    assert context is not None, "context != null"
    validate_preconditions(context)
    if check_integrity():
        call_skill("safe-refactor", target=context.get("file"))
    else:
        raise RuntimeError("INTEGRITY_FAIL")
    assert verify_output(), "VerifyOutput"
    return "SUCCESS"
"""

SAMPLE_DRIFTED_CODE = """
def execute_sample(context):
    # Missing first assertion!
    validate_preconditions(context)
    if check_integrity():
        call_skill("safe-refactor", target=context.get("file"))
    # Has partial matching
    assert verify_output(), "VerifyOutput"
    return "SUCCESS"
"""

SAMPLE_VIOLATING_CODE = """
def execute_sample(context):
    # Completely missing all invariants and calls
    print("Random execution without assertions or skills")
    return "UNKNOWN"
"""


def test_spec_extraction_from_pseudocode_and_drakon(tmp_path):
    """Verifies that SpecIntentExtractor parses ALGORITHM pseudocode and .drakon.json."""
    skill_dir = tmp_path / "sample-demo-skill"
    skill_dir.mkdir()
    md_file = skill_dir / "SKILL.md"
    drakon_file = skill_dir / "sample-demo-skill.drakon.json"

    md_file.write_text(SAMPLE_SKILL_MD, encoding="utf-8")
    drakon_file.write_text(json.dumps(SAMPLE_DRAKON_JSON), encoding="utf-8")

    extractor = SpecIntentExtractor()
    intent = extractor.extract_from_skill_dir(skill_dir)

    assert isinstance(intent, IntentGraphDTO)
    assert intent.skill_name == "sample-demo-skill"
    assert len(intent.assert_statements) >= 2
    assert any("context != null" in a for a in intent.assert_statements)
    assert any("VerifyOutput" in a for a in intent.assert_statements)
    assert "safe-refactor" in intent.call_skills
    assert any("CheckIntegrity" in c for c in intent.branch_conditions)
    assert intent.drakon_nodes_count == 6


def test_code_ast_signature_matching():
    """Verifies that CodeASTEncoder extracts functions, calls, and assertions from Python code."""
    encoder = CodeASTEncoder()
    ast_sigs = encoder.encode_source("sample.py", SAMPLE_COMPLIANT_CODE)

    assert isinstance(ast_sigs, CodeASTSignaturesDTO)
    assert "execute_sample" in ast_sigs.function_signatures
    assert len(ast_sigs.assert_statements) >= 2
    assert any("context" in a for a in ast_sigs.assert_statements)
    assert any("verify_output" in a for a in ast_sigs.assert_statements)
    assert any("call_skill" in c or "safe-refactor" in c for c in ast_sigs.call_chains)


def test_dual_gate_verdicts():
    """
    Verifies the 3 canonical discrete verdicts of Vector 3:
    1. S_intent >= 0.82 and 0 missing asserts -> VERDICT_INTENT_ALIGNED
    2. 0.65 <= S_intent < 0.82 -> VERDICT_INTENT_DRIFT_WARNING
    3. S_intent < 0.65 or missing assert -> VERDICT_INTENT_VIOLATION
    """
    extractor = SpecIntentExtractor()
    encoder = CodeASTEncoder()
    gatekeeper = IntentGatekeeper()

    # Create dummy intent graph
    intent = IntentGraphDTO(
        skill_name="sample-demo-skill",
        invariants=["context != null", "VerifyOutput()"],
        assert_statements=["context != null", "VerifyOutput()"],
        call_skills=["safe-refactor"],
        branch_conditions=["CheckIntegrity()"],
        drakon_nodes_count=6
    )

    # 1. Aligned Code
    ast_compliant = encoder.encode_source("sample.py", SAMPLE_COMPLIANT_CODE)
    res_aligned = gatekeeper.evaluate_intent(intent, ast_compliant)
    assert res_aligned.verdict == IntentVerdict.VERDICT_INTENT_ALIGNED.value
    assert res_aligned.cosine_alignment >= 0.82
    assert len(res_aligned.missing_invariants) == 0
    assert res_aligned.allow_commit is True

    # 2. Drift Code (has minor missing item or lower similarity, but warning)
    # If an assert is explicitly missing, it violates, but if code differs structurally without missing core asserts:
    res_drift = gatekeeper.classify_score(score=0.75, missing_asserts=[])
    assert res_drift == IntentVerdict.VERDICT_INTENT_DRIFT_WARNING.value

    # 3. Violation Code
    ast_violating = encoder.encode_source("sample.py", SAMPLE_VIOLATING_CODE)
    res_violation = gatekeeper.evaluate_intent(intent, ast_violating)
    assert res_violation.verdict == IntentVerdict.VERDICT_INTENT_VIOLATION.value
    assert res_violation.cosine_alignment < 0.65 or len(res_violation.missing_invariants) > 0
    assert res_violation.allow_commit is False


def test_laya_intent_client_fallback_resilience():
    """Verifies that LayaIntentClient safely falls back to local AST cosine matcher if remote is offline."""
    client = LayaIntentClient(host="127.0.0.1", port=9999, timeout=0.1)  # invalid port
    intent = IntentGraphDTO(skill_name="demo", assert_statements=["a == 1"])
    code_ast = CodeASTSignaturesDTO(assert_statements=["a == 1"])

    result = client.verify_intent(intent, code_ast)
    assert isinstance(result, IntentVerificationResultDTO)
    assert result.fallback is True
    assert result.latency_ms >= 0.0
