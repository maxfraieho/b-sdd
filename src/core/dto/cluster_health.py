"""
Cluster Health & Telemetry DTOs.
Sprint 032 - Phase 1.
Compliant with ADR-002 (Pure Stdlib Core) and ADR-010 (Tripartite ADR Ontology - DataADR).
100% Pure Python Standard Library.
"""
from dataclasses import asdict, dataclass, field
import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ServiceHealthDTO:
    """Represents real-time health telemetry for an individual cluster service."""
    service_id: str
    host: str
    port: int
    is_up: bool
    latency_ms: float
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServiceHealthDTO":
        return cls(
            service_id=data["service_id"],
            host=data["host"],
            port=data["port"],
            is_up=data["is_up"],
            latency_ms=data["latency_ms"],
            error_message=data.get("error_message")
        )


@dataclass
class ClusterHealthReportDTO:
    """Aggregated health status across all probed cluster endpoints."""
    timestamp: str
    services: List[ServiceHealthDTO] = field(default_factory=list)
    overall_status: str = "UP"  # "UP" | "DEGRADED" | "DOWN"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "services": [s.to_dict() for s in self.services],
            "overall_status": self.overall_status
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClusterHealthReportDTO":
        services = [ServiceHealthDTO.from_dict(s) for s in data.get("services", [])]
        return cls(
            timestamp=data["timestamp"],
            services=services,
            overall_status=data.get("overall_status", "UP")
        )


@dataclass
class WatchdogStateDTO:
    """Stateful debounce tracking for alert management."""
    service_id: str
    status: str = "UP"  # "UP" | "DOWN" | "PENDING_DOWN"
    fail_streak: int = 0
    last_alert_ts: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WatchdogStateDTO":
        return cls(
            service_id=data["service_id"],
            status=data.get("status", "UP"),
            fail_streak=data.get("fail_streak", 0),
            last_alert_ts=data.get("last_alert_ts", 0.0)
        )
