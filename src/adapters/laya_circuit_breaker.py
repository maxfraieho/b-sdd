"""
Laya Circuit Breaker & Cluster Health Cache Adapter.
Sprint 032 - Phase 3.
Compliant with ADR-002 (Pure Stdlib Core) and ADR-014 (Laya Decision Engine).
100% Pure Python Standard Library.
"""
import json
import logging
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger("LayaCircuitBreaker")

CACHE_PATHS = [
    Path(os.getenv("CLUSTER_HEALTH_PATH", "/var/run/b_sdd_cluster_health.json")),
    Path("/tmp/b_sdd_cluster_health.json"),
    Path("b_sdd_cluster_health.json"),
]


def get_cached_cluster_health() -> Optional[Dict[str, Any]]:
    """Reads the latest cluster health cache from known paths."""
    for p in CACHE_PATHS:
        try:
            if p.exists():
                content = p.read_text(encoding="utf-8")
                return json.loads(content)
        except Exception:
            continue
    return None


def get_cached_service_health(service_id: str = "laya_decision_engine") -> Optional[Dict[str, Any]]:
    """Returns the cached status dictionary for a specific service."""
    report = get_cached_cluster_health()
    if not report:
        return None
    for s in report.get("services", []):
        if s.get("service_id") == service_id:
            return s
    return None


def is_laya_cached_down() -> bool:
    """
    Returns True if the cluster watchdog has marked Laya as DOWN in the health cache.
    Enables sub-1ms fast-path fallback without waiting for network timeouts.
    """
    svc = get_cached_service_health("laya_decision_engine")
    if svc and svc.get("is_up") is False:
        return True
    return False


class LayaCircuitBreaker:
    """
    Adaptive Circuit Breaker evaluating local health cache before remote network dispatch.
    """

    def __init__(self, service_id: str = "laya_decision_engine"):
        self.service_id = service_id

    def is_available(self) -> bool:
        """Fast check: returns False if known to be DOWN via cache."""
        return not is_laya_cached_down()

    def get_status(self) -> str:
        """Returns 'DOWN' if cached down, else 'UP'."""
        svc = get_cached_service_health(self.service_id)
        if svc:
            return "UP" if svc.get("is_up") else "DOWN"
        return "UNKNOWN"
