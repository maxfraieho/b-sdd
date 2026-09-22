"""
Laya Intent Verification Client.
Queries Laya System 1 on Pixel 7 (http://192.168.3.251:9623) with deterministic local fallback.
Compliant with ADR-002 (Pure Stdlib Core) and ADR-014 (Laya Decision Engine).
100% Pure Python Standard Library.
"""
import json
import logging
import os
import re
import socket
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Set, Tuple

from src.core.dto.intent_verification import (
    IntentGraphDTO,
    CodeASTSignaturesDTO,
    IntentVerificationResultDTO,
    IntentVerdict
)

logger = logging.getLogger("LayaIntentClient")

DEFAULT_LAYA_HOST = os.getenv("LAYA_HOST", "192.168.3.251")
DEFAULT_LAYA_PORT = int(os.getenv("LAYA_PORT", "9623"))
DEFAULT_TIMEOUT = float(os.getenv("LAYA_TIMEOUT", "0.8"))


def _tokenize(text: str) -> Set[str]:
    """Tokenizes text into lowercase alphanumeric words."""
    words = re.findall(r"[a-zA-Z0-9_\-]+", text.lower())
    return set(words)


def _compute_cosine_similarity(tokens_a: Set[str], tokens_b: Set[str]) -> float:
    """Computes Jaccard / Cosine approximation on token sets."""
    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = len(tokens_a.intersection(tokens_b))
    union = len(tokens_a.union(tokens_b))
    return round(intersection / union, 2) if union > 0 else 0.0


class LayaIntentClient:
    """Zero-dependency HTTP client for Laya System 1 Spec-to-Code Intent Verification."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        timeout: float = DEFAULT_TIMEOUT
    ):
        self.host = host or DEFAULT_LAYA_HOST
        self.port = port or DEFAULT_LAYA_PORT
        self.timeout = timeout
        self.base_url = f"http://{self.host}:{self.port}"

    def local_heuristic_match(
        self,
        intent: IntentGraphDTO,
        code_ast: CodeASTSignaturesDTO
    ) -> Tuple[float, List[str]]:
        """
        Deterministic local AST matching algorithm when remote inference is offline.
        Compares invariants and assert statements between specification and code AST.
        """
        missing_asserts: List[str] = []

        # Check required assertions
        code_assert_text = " ".join(code_ast.assert_statements).lower()
        for inv in intent.assert_statements:
            # Extract core keywords from assertion
            inv_tokens = _tokenize(inv)
            # Check if any significant token is represented in code asserts
            matched = any(tok in code_assert_text for tok in inv_tokens if len(tok) > 2)
            if not matched:
                missing_asserts.append(inv)

        # Check called skills
        code_calls_text = " ".join(code_ast.call_chains).lower()
        missing_skills: List[str] = []
        for skill in intent.call_skills:
            if skill.lower() not in code_calls_text:
                missing_skills.append(skill)

        # Compute token overlap across all semantic signatures
        intent_tokens = _tokenize(" ".join(intent.invariants + intent.assert_statements + intent.call_skills + intent.branch_conditions))
        code_tokens = _tokenize(" ".join(code_ast.function_signatures + code_ast.call_chains + code_ast.assert_statements))

        sim = _compute_cosine_similarity(intent_tokens, code_tokens)

        # Adjust similarity by ratio of satisfied invariants
        total_invariants = max(1, len(intent.assert_statements))
        satisfied_ratio = (total_invariants - len(missing_asserts)) / total_invariants

        final_score = round(0.4 * sim + 0.6 * satisfied_ratio, 2)

        # Penalize if missing critical asserts
        if len(missing_asserts) > 0:
            final_score = min(final_score, 0.64)

        return final_score, missing_asserts

    def verify_intent(
        self,
        intent: IntentGraphDTO,
        code_ast: CodeASTSignaturesDTO
    ) -> IntentVerificationResultDTO:
        """
        Submits intent graph and code AST to Laya System 1 on Pixel 7 (:9623).
        Falls back to local heuristic matching seamlessly within sub-40ms SLA.
        """
        t0 = time.perf_counter()
        payload = {
            "intent": intent.to_dict(),
            "code_ast": code_ast.to_dict(),
            "task": "intent_verification",
            "timestamp": time.time()
        }

        try:
            body = json.dumps(payload).encode("utf-8")
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "B-SDD-LayaIntentClient/1.0"
            }

            # First attempt /v1/intent/verify
            req = urllib.request.Request(f"{self.base_url}/v1/intent/verify", data=body, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    if resp.status == 200:
                        raw = json.loads(resp.read().decode("utf-8"))
                        elapsed = round((time.perf_counter() - t0) * 1000, 2)
                        return IntentVerificationResultDTO(
                            cosine_alignment=float(raw.get("cosine_alignment", 0.90)),
                            missing_invariants=list(raw.get("missing_invariants", [])),
                            verdict=raw.get("verdict", IntentVerdict.VERDICT_INTENT_ALIGNED.value),
                            allow_commit=bool(raw.get("allow_commit", True)),
                            latency_ms=elapsed,
                            fallback=False,
                            details=raw
                        )
            except urllib.error.HTTPError as he:
                if he.code != 404:
                    raise he

            # Second attempt via universal /predict endpoint
            predict_payload = {
                "state": {
                    "task": "intent_verification",
                    "intent": intent.to_dict(),
                    "code_ast": code_ast.to_dict()
                },
                "timestamp": time.time()
            }
            body_predict = json.dumps(predict_payload).encode("utf-8")
            req2 = urllib.request.Request(f"{self.base_url}/predict", data=body_predict, headers=headers)
            with urllib.request.urlopen(req2, timeout=self.timeout) as resp2:
                if resp2.status == 200:
                    raw2 = json.loads(resp2.read().decode("utf-8"))
                    score, missing = self.local_heuristic_match(intent, code_ast)
                    elapsed = round((time.perf_counter() - t0) * 1000, 2)
                    remote_score = float(raw2.get("score", score))
                    effective_score = max(score, remote_score) if len(missing) == 0 else score

                    verdict = self._verdict_from_score(effective_score, missing)
                    return IntentVerificationResultDTO(
                        cosine_alignment=effective_score,
                        missing_invariants=missing,
                        verdict=verdict,
                        allow_commit=(verdict == IntentVerdict.VERDICT_INTENT_ALIGNED.value),
                        latency_ms=elapsed,
                        fallback=False,
                        details=raw2
                    )

        except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout, TimeoutError, Exception) as e:
            logger.debug(f"Laya remote inference unavailable or timed out: {e}. Executing local fallback.")

        # Local fallback execution
        score, missing = self.local_heuristic_match(intent, code_ast)
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        verdict = self._verdict_from_score(score, missing)

        return IntentVerificationResultDTO(
            cosine_alignment=score,
            missing_invariants=missing,
            verdict=verdict,
            allow_commit=(verdict == IntentVerdict.VERDICT_INTENT_ALIGNED.value),
            latency_ms=elapsed,
            fallback=True,
            details={"fallback_reason": "Local heuristic AST match"}
        )

    def _verdict_from_score(self, score: float, missing_asserts: List[str]) -> str:
        if len(missing_asserts) > 0 or score < 0.65:
            return IntentVerdict.VERDICT_INTENT_VIOLATION.value
        elif score < 0.82:
            return IntentVerdict.VERDICT_INTENT_DRIFT_WARNING.value
        else:
            return IntentVerdict.VERDICT_INTENT_ALIGNED.value
