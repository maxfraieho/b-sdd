#!/usr/bin/env python3
"""
Laya Decision Engine Client Hook.
Zero-dependency client for the System 1 non-autoregressive decision engine
hosted on Google Pixel 7 (Podroid Alpine VM: 192.168.3.251:9623).
Provides sub-40ms decision queries with zero RAM overhead on Host .161.
Gracefully degrades with fallback=True if Podroid is sleeping or unreachable (ADR-002).
"""
import hashlib
import json
import logging
import os
import socket
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

DEFAULT_LAYA_HOST = os.getenv("LAYA_HOST", "192.168.3.251")
DEFAULT_LAYA_PORT = int(os.getenv("LAYA_PORT", "9623"))
DEFAULT_TIMEOUT = float(os.getenv("LAYA_TIMEOUT", "3.0"))

logger = logging.getLogger("LayaClient")


class LayaClient:
    """Zero-dependency HTTP client for Laya System 1 decision engine on Podroid."""

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

    def check_health(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Queries GET /health endpoint on Podroid.
        Returns health status dictionary or error dict without throwing exceptions.
        """
        to = timeout if timeout is not None else self.timeout
        url = f"{self.base_url}/health"
        headers = {"User-Agent": "B-SDD-LayaClient/1.0"}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=to) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data
                return {"status": "down", "error": f"Unexpected HTTP status {resp.status}"}
        except Exception as e:
            return {"status": "down", "error": str(e)}

    def query_decision(
        self,
        state: Dict[str, Any],
        questions: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Queries non-autoregressive decision from Laya engine on Pixel 7.

        Args:
            state: Current pipeline/sprint state dictionary.
            questions: Dictionary of pending/active architectural questions.
            timeout: Request timeout in seconds (default: 3.0s).

        Returns:
            Dict containing decision, confidence, latency, or graceful fallback response.
            Never raises exceptions to guarantee supervisor resilience.
        """
        if questions is None:
            questions = {}

        to = timeout if timeout is not None else self.timeout
        url = f"{self.base_url}/predict"
        payload = {
            "state": state,
            "questions": questions,
            "timestamp": time.time()
        }

        try:
            body = json.dumps(payload).encode("utf-8")
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "B-SDD-LayaClient/1.0"
            }
            req = urllib.request.Request(url, data=body, headers=headers)

            t0 = time.perf_counter()
            with urllib.request.urlopen(req, timeout=to) as resp:
                raw_resp = resp.read().decode("utf-8")
                elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

                if resp.status == 200:
                    data = json.loads(raw_resp)
                    data["fallback"] = False
                    if "latency_ms" not in data:
                        data["latency_ms"] = elapsed_ms
                    return data
                else:
                    return self._fallback_response(state, questions, f"HTTP {resp.status}: {raw_resp}")

        except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout, TimeoutError, Exception) as e:
            logger.warning(f"Laya daemon on {self.base_url} unreachable: {e}. Activating graceful fallback.")
            return self._fallback_response(state, questions, str(e))

    def _fallback_response(
        self,
        state: Dict[str, Any],
        questions: Dict[str, Any],
        error_msg: str
    ) -> Dict[str, Any]:
        """Local heuristic fallback when Podroid is asleep or unreachable."""
        state_str = json.dumps(state, sort_keys=True, default=str)
        digest = hashlib.sha256(state_str.encode("utf-8")).hexdigest()[:16]

        has_blockers = bool(state.get("blocked") or state.get("blockers"))
        risk = state.get("risk_level", "low").lower()
        invariants_ok = state.get("invariants_satisfied", True)

        if has_blockers or risk in ("high", "critical"):
            decision = "HALT_FOR_INSPECTION"
            action = "REQUIRE_OPERATOR_REVIEW"
        elif not invariants_ok:
            decision = "REMEDIATE_INVARIANTS"
            action = "APPLY_AUTONOMOUS_FIX"
        else:
            decision = "PROCEED"
            action = "AUTO_EXECUTE"

        return {
            "fallback": True,
            "status": "degraded",
            "decision": decision,
            "action": action,
            "confidence": 0.5,
            "latency_ms": 0.0,
            "model": "local-heuristic-fallback",
            "error": error_msg,
            "state_digest": digest,
            "note": "Podroid Laya engine asleep or unreachable; safe heuristic applied."
        }


_global_client: Optional[LayaClient] = None


def get_laya_client(
    host: Optional[str] = None,
    port: Optional[int] = None,
    timeout: float = DEFAULT_TIMEOUT
) -> LayaClient:
    """Returns singleton or configured LayaClient instance."""
    global _global_client
    if _global_client is None or host is not None or port is not None:
        _global_client = LayaClient(host=host, port=port, timeout=timeout)
    return _global_client
