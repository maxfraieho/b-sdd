"""
Distillation and Permanent Vault DTO Schemas and Serialization Contracts.
Compliant with ADR-001 (Bitemporal WORM Ledger), ADR-002 (Pure Stdlib Core), and ADR-010 (Tripartite ADR Ontology).
100% Pure Python Standard Library.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class WormPayloadDTO:
    """Immutable bitemporal payload for Utopia DB WORM commit (ADR-001)."""
    transaction_time: float        # Physical Tx timestamp (monotonically increasing)
    valid_time_start: str          # Valid time Tv start (ISO 8601)
    valid_time_end: str            # Valid time Tv end (ISO 8601 or 'INFINITY')
    payload_hash: str              # Cryptographic SHA-256 digest
    sprint_id: str
    commit_hash: str
    record_id: Optional[str] = None
    replicated_drive: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_time": self.transaction_time,
            "valid_time_start": self.valid_time_start,
            "valid_time_end": self.valid_time_end,
            "payload_hash": self.payload_hash,
            "sprint_id": self.sprint_id,
            "commit_hash": self.commit_hash,
            "record_id": self.record_id,
            "replicated_drive": self.replicated_drive,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WormPayloadDTO":
        return cls(
            transaction_time=float(data.get("transaction_time", 0.0)),
            valid_time_start=data.get("valid_time_start", ""),
            valid_time_end=data.get("valid_time_end", "INFINITY"),
            payload_hash=data.get("payload_hash", ""),
            sprint_id=data.get("sprint_id", ""),
            commit_hash=data.get("commit_hash", ""),
            record_id=data.get("record_id"),
            replicated_drive=bool(data.get("replicated_drive", False)),
        )


@dataclass
class SprintDistillationDTO:
    """Structured knowledge delta distilled from sprint closure raw telemetry."""
    sprint_id: str
    commit_hash: str
    verified_invariants: List[str] = field(default_factory=list)
    ast_deltas: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    worm_tx_id: Optional[str] = None
    data_adr_delta: List[str] = field(default_factory=list)
    skill_adr_delta: List[str] = field(default_factory=list)
    spec_adr_delta: List[str] = field(default_factory=list)
    superseded_invariants: List[str] = field(default_factory=list)
    summary: str = ""
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sprint_id": self.sprint_id,
            "commit_hash": self.commit_hash,
            "verified_invariants": list(self.verified_invariants),
            "ast_deltas": list(self.ast_deltas),
            "metrics": dict(self.metrics),
            "worm_tx_id": self.worm_tx_id,
            "data_adr_delta": list(self.data_adr_delta),
            "skill_adr_delta": list(self.skill_adr_delta),
            "spec_adr_delta": list(self.spec_adr_delta),
            "superseded_invariants": list(self.superseded_invariants),
            "summary": self.summary,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SprintDistillationDTO":
        return cls(
            sprint_id=data.get("sprint_id", ""),
            commit_hash=data.get("commit_hash", ""),
            verified_invariants=list(data.get("verified_invariants", [])),
            ast_deltas=list(data.get("ast_deltas", [])),
            metrics=dict(data.get("metrics", {})),
            worm_tx_id=data.get("worm_tx_id"),
            data_adr_delta=list(data.get("data_adr_delta", [])),
            skill_adr_delta=list(data.get("skill_adr_delta", [])),
            spec_adr_delta=list(data.get("spec_adr_delta", [])),
            superseded_invariants=list(data.get("superseded_invariants", [])),
            summary=data.get("summary", ""),
            timestamp=float(data.get("timestamp", 0.0)),
        )
