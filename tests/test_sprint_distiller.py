"""
Unit and Integration Tests for Track B Sprint Distiller and Permanent Vault.
Sprint 031 - Track B.
100% Python Standard Library Compliance (ADR-001, ADR-002, ADR-010).
"""
import json
import os
import pytest
from pathlib import Path

from src.core.dto.distillation import SprintDistillationDTO, WormPayloadDTO
from scripts.distill_sprint import SprintDistiller


SAMPLE_RAW_CLOSURE_MD = """# Sprint 030 Final Closure Telemetry & Verification Report
Date: 2026-09-22
Sprint ID: sprint_030
Commit Hash: 97527e2a632b84cf8295e7d40760abe659cb53aa

## 1. Verified Invariants (PASSED)
- [INVARIANT-1] Pre-commit gate completes sub-15ms on safe diffs.
- [INVARIANT-2] Suspicious patterns are blocked with HALT_FOR_INSPECTION.
- [INVARIANT-3] Active rules remain under 500 words (464 words).

## 2. Discarded Architectural Hypotheses
- [DISCARDED] Direct LLM invocation inside git pre-commit hook (too slow: >1200ms).

## 3. Tripartite ADR Deltas
- [DataADR] Added SkillDTO and SkillsResponseDTO schemas in src/core/dto/skills.py.
- [SkillADR] Restored cloudflare-pages-expert and standardized 59 skills.
- [SpecADR] Established Vector 2 Diff Risk Gatekeeper specification.

## 4. AST Graph Mutations
- Mutated src/core/diff_risk_gatekeeper.py (+350 lines)
- Mutated scripts/install_laya_precommit_hook.sh (+185 lines)

## 5. Superseded Invariants
- Supersedes ADR-008 single-point manual skill editing.
"""


def test_distillation_payload_extraction_from_raw_closure(tmp_path):
    """Verifies that SprintDistiller correctly parses raw markdown closure telemetry."""
    raw_file = tmp_path / "reports" / "sprint_030_closure_raw.md"
    raw_file.parent.mkdir(parents=True)
    raw_file.write_text(SAMPLE_RAW_CLOSURE_MD, encoding="utf-8")

    distiller = SprintDistiller()
    dto = distiller.extract_from_raw_report(raw_file)

    assert isinstance(dto, SprintDistillationDTO)
    assert dto.sprint_id == "sprint_030"
    assert "97527e2" in dto.commit_hash
    assert len(dto.verified_invariants) >= 3
    assert len(dto.data_adr_delta) >= 1
    assert len(dto.skill_adr_delta) >= 1
    assert len(dto.spec_adr_delta) >= 1
    assert len(dto.superseded_invariants) >= 1
    assert any("ADR-008" in s for s in dto.superseded_invariants)


def test_mega_adr_ledger_append_with_tripartite_classification(tmp_path):
    """Verifies appending distilled quantum node into B_SDD_MEGA_ADR_MASTER.md."""
    mega_adr_file = tmp_path / "B_SDD_MEGA_ADR_MASTER.md"
    mega_adr_file.write_text(
        "# B-SDD Mega-ADR Master Architecture Ledger\n\n## Tripartite Ontology\n\n",
        encoding="utf-8"
    )

    dto = SprintDistillationDTO(
        sprint_id="sprint_030",
        commit_hash="97527e2a",
        verified_invariants=["Pre-commit gate completes sub-15ms"],
        data_adr_delta=["SkillDTO schema"],
        skill_adr_delta=["cloudflare-pages-expert restored"],
        spec_adr_delta=["Diff risk gatekeeper spec"],
        superseded_invariants=["ADR-008 manual editing"],
        summary="Diff risk gatekeeper sprint completion",
        timestamp=1789221000.0
    )

    distiller = SprintDistiller()
    updated_content = distiller.append_to_mega_adr(mega_adr_file, dto)

    assert "### Sprint 030 Knowledge Delta" in updated_content
    assert "DataADR" in updated_content
    assert "SkillADR" in updated_content
    assert "SpecADR" in updated_content
    assert "SUPERSEDED" in updated_content or "ADR-008" in updated_content


def test_utopia_worm_tx_generation():
    """Verifies generation of immutable WORM payload with monotonic Tx and bitemporal valid time."""
    distiller = SprintDistiller()
    dto = SprintDistillationDTO(
        sprint_id="sprint_030",
        commit_hash="97527e2a",
        verified_invariants=["Invariant 1"],
        data_adr_delta=["Data 1"],
        skill_adr_delta=["Skill 1"],
        spec_adr_delta=["Spec 1"]
    )

    worm_record = distiller.generate_worm_payload(dto, valid_from="2026-09-22T10:00:00Z")
    assert isinstance(worm_record, WormPayloadDTO)
    assert worm_record.sprint_id == "sprint_030"
    assert worm_record.transaction_time > 0.0
    assert worm_record.valid_time_start == "2026-09-22T10:00:00Z"
    assert worm_record.valid_time_end == "INFINITY"
    assert len(worm_record.payload_hash) == 64  # SHA-256 hex string
