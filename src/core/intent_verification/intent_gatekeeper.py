"""
Vector 3 Intent Gatekeeper.
Evaluates semantic spec-to-code alignment and enforces the dual-gate pre-commit invariant.
Compliant with ADR-002 (Pure Stdlib Core) and ADR-016 (Tripartite Skill Architecture).
100% Pure Python Standard Library.
"""
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.dto.intent_verification import (
    IntentGraphDTO,
    CodeASTSignaturesDTO,
    IntentVerificationResultDTO,
    IntentVerdict
)
from src.core.intent_verification.spec_extractor import SpecIntentExtractor
from src.core.intent_verification.code_ast_encoder import CodeASTEncoder
from src.core.intent_verification.laya_intent_client import LayaIntentClient

logger = logging.getLogger("IntentGatekeeper")


class IntentGatekeeper:
    """Pre-commit verification gatekeeper binding code diffs to formal specifications."""

    def __init__(
        self,
        extractor: Optional[SpecIntentExtractor] = None,
        encoder: Optional[CodeASTEncoder] = None,
        client: Optional[LayaIntentClient] = None
    ):
        self.extractor = extractor or SpecIntentExtractor()
        self.encoder = encoder or CodeASTEncoder()
        self.client = client or LayaIntentClient()

    def classify_score(self, score: float, missing_asserts: Optional[List[str]] = None) -> str:
        """Classifies numerical score and missing assertion count into discrete IntentVerdict."""
        missing = missing_asserts or []
        if len(missing) > 0 or score < 0.65:
            return IntentVerdict.VERDICT_INTENT_VIOLATION.value
        elif score < 0.82:
            return IntentVerdict.VERDICT_INTENT_DRIFT_WARNING.value
        else:
            return IntentVerdict.VERDICT_INTENT_ALIGNED.value

    def evaluate_intent(
        self,
        intent: IntentGraphDTO,
        code_ast: CodeASTSignaturesDTO
    ) -> IntentVerificationResultDTO:
        """
        Evaluates alignment between an IntentGraphDTO and a CodeASTSignaturesDTO.
        """
        return self.client.verify_intent(intent, code_ast)

    def evaluate_staged_changes(self, repo_root: Optional[Path] = None) -> IntentVerificationResultDTO:
        """
        Main pre-commit entry point.
        Analyzes staged git files. Fast-bypasses non-core and non-spec diffs in < 5ms.
        """
        t0 = time.perf_counter()
        root = repo_root or Path.cwd()

        try:
            res = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                cwd=str(root),
                check=True
            )
            staged_files = [line.strip() for line in res.stdout.splitlines() if line.strip()]
        except Exception as e:
            logger.error(f"Failed to read git diff --cached: {e}")
            staged_files = []

        if not staged_files:
            elapsed = round((time.perf_counter() - t0) * 1000, 2)
            return IntentVerificationResultDTO(
                cosine_alignment=1.0,
                missing_invariants=[],
                verdict=IntentVerdict.VERDICT_INTENT_ALIGNED.value,
                allow_commit=True,
                latency_ms=elapsed,
                fallback=False,
                details={"reason": "No staged files"}
            )

        # Fast path check: if diff only touches docs, tests, or telemetry without core logic / skills
        touches_specs = any("SKILL.md" in f or f.endswith(".drakon.json") for f in staged_files)
        touches_core = any(f.startswith("src/core/") for f in staged_files)

        if not touches_specs and not touches_core:
            elapsed = round((time.perf_counter() - t0) * 1000, 2)
            return IntentVerificationResultDTO(
                cosine_alignment=1.0,
                missing_invariants=[],
                verdict=IntentVerdict.VERDICT_INTENT_ALIGNED.value,
                allow_commit=True,
                latency_ms=elapsed,
                fallback=False,
                details={"reason": "Fast-path bypass: changes outside core / specifications"}
            )

        # Encode staged files
        file_map: Dict[str, str] = {}
        for f in staged_files:
            p = root / f
            if p.exists() and p.is_file() and p.suffix == ".py":
                try:
                    file_map[f] = p.read_text(encoding="utf-8")
                except Exception:
                    pass

        code_ast = self.encoder.encode_files(file_map)

        # Find relevant skills in staged files or default golden core skills
        relevant_skills_dirs: List[Path] = []
        for f in staged_files:
            if "skills/" in f:
                parts = f.split("skills/")
                if len(parts) > 1:
                    s_name = parts[1].split("/")[0]
                    s_dir = root / ".agents" / "skills" / s_name
                    if s_dir.exists() and s_dir not in relevant_skills_dirs:
                        relevant_skills_dirs.append(s_dir)

        # Fallback to core b-sdd skill if no specific skill staged
        if not relevant_skills_dirs:
            b_sdd_dir = root / ".agents" / "skills" / "b-sdd"
            if b_sdd_dir.exists():
                relevant_skills_dirs.append(b_sdd_dir)

        # Aggregate intents
        combined_intent = IntentGraphDTO(skill_name="staged_context")
        for s_dir in relevant_skills_dirs:
            sub_intent = self.extractor.extract_from_skill_dir(s_dir)
            combined_intent.invariants.extend(sub_intent.invariants)
            combined_intent.assert_statements.extend(sub_intent.assert_statements)
            combined_intent.call_skills.extend(sub_intent.call_skills)
            combined_intent.branch_conditions.extend(sub_intent.branch_conditions)
            combined_intent.drakon_nodes_count += sub_intent.drakon_nodes_count

        combined_intent.invariants = list(dict.fromkeys(combined_intent.invariants))
        combined_intent.assert_statements = list(dict.fromkeys(combined_intent.assert_statements))
        combined_intent.call_skills = list(dict.fromkeys(combined_intent.call_skills))

        # Evaluate through Laya
        result = self.client.verify_intent(combined_intent, code_ast)
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        result.latency_ms = elapsed

        return result
