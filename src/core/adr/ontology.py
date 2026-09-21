"""
Tripartite ADR Ontology and Bitemporal Pre-Logging Engine.
Compliant with ADR-001 (WORM Ledger & Bitemporal Consistency),
ADR-002 (Pure Stdlib Core), and ADR-010 (Tripartite ADR Ontology).
100% Pure Python Standard Library.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from typing import Dict, List, Optional, Any, Union


class ADRType(str, Enum):
    """Tripartite ADR classification defined in ADR-010."""
    DATA = "data"       # Facts, context, state, external API raw logs, skill dumps
    SKILL = "skill"     # Procedural actions, DRAKON algorithmic blueprints, operations
    SPEC = "spec"       # SSD contracts, acceptance criteria, invariant constraints


def _now_iso() -> str:
    """Returns current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _compute_hash(payload: Any) -> str:
    """Computes deterministic SHA256 hex digest of JSON-serializable payload."""
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@dataclass
class BaseADR:
    """Canonical base bitemporal Architectural Decision Record."""
    adr_id: str
    title: str
    adr_type: ADRType = ADRType.SPEC
    status: str = "proposed"  # proposed | accepted | rejected | superseded
    valid_from: str = field(default_factory=_now_iso)
    valid_to: Optional[str] = None
    tx_time: str = field(default_factory=_now_iso)
    tx_superseded: Optional[str] = None
    supersedes: Optional[str] = None
    superseded_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_valid_at(self, tv: str) -> bool:
        """Evaluates whether this record is active at valid time coordinate tv."""
        if tv < self.valid_from:
            return False
        if self.valid_to is not None and tv >= self.valid_to:
            return False
        return True

    def is_visible_at(self, tt: str) -> bool:
        """Evaluates whether this record is visible in ledger at transaction time coordinate tt."""
        if tt < self.tx_time:
            return False
        if self.tx_superseded is not None and tt >= self.tx_superseded:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "adr_id": self.adr_id,
            "title": self.title,
            "adr_type": self.adr_type.value,
            "status": self.status,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "tx_time": self.tx_time,
            "tx_superseded": self.tx_superseded,
            "supersedes": self.supersedes,
            "superseded_by": self.superseded_by,
            "metadata": self.metadata,
        }


@dataclass
class DataADR(BaseADR):
    adr_type: ADRType = ADRType.DATA
    data_payload: Dict[str, Any] = field(default_factory=dict)
    source_uri: Optional[str] = None
    raw_hash: Optional[str] = None
    folder_dump_ref: Optional[str] = None  # Path to markdown dump (.md)

    def __post_init__(self):
        self.adr_type = ADRType.DATA
        if not self.raw_hash and self.data_payload:
            self.raw_hash = _compute_hash(self.data_payload)

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "data_payload": self.data_payload,
            "source_uri": self.source_uri,
            "raw_hash": self.raw_hash,
            "folder_dump_ref": self.folder_dump_ref,
        })
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataADR":
        return cls(
            adr_id=data["adr_id"],
            title=data["title"],
            adr_type=ADRType.DATA,
            status=data.get("status", "proposed"),
            valid_from=data.get("valid_from", _now_iso()),
            valid_to=data.get("valid_to"),
            tx_time=data.get("tx_time", _now_iso()),
            tx_superseded=data.get("tx_superseded"),
            supersedes=data.get("supersedes"),
            superseded_by=data.get("superseded_by"),
            metadata=data.get("metadata", {}),
            data_payload=data.get("data_payload", {}),
            source_uri=data.get("source_uri"),
            raw_hash=data.get("raw_hash"),
            folder_dump_ref=data.get("folder_dump_ref"),
        )


@dataclass
class SkillADR(BaseADR):
    adr_type: ADRType = ADRType.SKILL
    drakon_schema_ref: Optional[str] = None  # Link to .drakon.json
    dump_path: Optional[str] = None          # Link to .md dump
    input_adr_types: List[str] = field(default_factory=list)
    output_adr_types: List[str] = field(default_factory=list)
    invariants: List[str] = field(default_factory=list)
    pseudocode: Optional[str] = None

    def __post_init__(self):
        self.adr_type = ADRType.SKILL

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "drakon_schema_ref": self.drakon_schema_ref,
            "dump_path": self.dump_path,
            "input_adr_types": self.input_adr_types,
            "output_adr_types": self.output_adr_types,
            "invariants": self.invariants,
            "pseudocode": self.pseudocode,
        })
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillADR":
        return cls(
            adr_id=data["adr_id"],
            title=data["title"],
            adr_type=ADRType.SKILL,
            status=data.get("status", "proposed"),
            valid_from=data.get("valid_from", _now_iso()),
            valid_to=data.get("valid_to"),
            tx_time=data.get("tx_time", _now_iso()),
            tx_superseded=data.get("tx_superseded"),
            supersedes=data.get("supersedes"),
            superseded_by=data.get("superseded_by"),
            metadata=data.get("metadata", {}),
            drakon_schema_ref=data.get("drakon_schema_ref"),
            dump_path=data.get("dump_path"),
            input_adr_types=data.get("input_adr_types", []),
            output_adr_types=data.get("output_adr_types", []),
            invariants=data.get("invariants", []),
            pseudocode=data.get("pseudocode"),
        )


@dataclass
class SpecADR(BaseADR):
    adr_type: ADRType = ADRType.SPEC
    contract_schema: Dict[str, Any] = field(default_factory=dict)
    acceptance_criteria: List[str] = field(default_factory=list)
    operator_editable: bool = True
    specification_text: str = ""

    def __post_init__(self):
        self.adr_type = ADRType.SPEC

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "contract_schema": self.contract_schema,
            "acceptance_criteria": self.acceptance_criteria,
            "operator_editable": self.operator_editable,
            "specification_text": self.specification_text,
        })
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpecADR":
        return cls(
            adr_id=data["adr_id"],
            title=data["title"],
            adr_type=ADRType.SPEC,
            status=data.get("status", "proposed"),
            valid_from=data.get("valid_from", _now_iso()),
            valid_to=data.get("valid_to"),
            tx_time=data.get("tx_time", _now_iso()),
            tx_superseded=data.get("tx_superseded"),
            supersedes=data.get("supersedes"),
            superseded_by=data.get("superseded_by"),
            metadata=data.get("metadata", {}),
            contract_schema=data.get("contract_schema", {}),
            acceptance_criteria=data.get("acceptance_criteria", []),
            operator_editable=data.get("operator_editable", True),
            specification_text=data.get("specification_text", ""),
        )


def deserialize_adr(data: Dict[str, Any]) -> Union[DataADR, SkillADR, SpecADR, BaseADR]:
    """Factory helper to reconstruct the typed ADR instance from serialized dictionary."""
    atype = data.get("adr_type")
    if atype == ADRType.DATA.value or atype == ADRType.DATA:
        return DataADR.from_dict(data)
    elif atype == ADRType.SKILL.value or atype == ADRType.SKILL:
        return SkillADR.from_dict(data)
    elif atype == ADRType.SPEC.value or atype == ADRType.SPEC:
        return SpecADR.from_dict(data)
    else:
        return BaseADR(
            adr_id=data["adr_id"],
            title=data["title"],
            adr_type=ADRType(atype) if atype else ADRType.SPEC,
            status=data.get("status", "proposed"),
            valid_from=data.get("valid_from", _now_iso()),
            valid_to=data.get("valid_to"),
            tx_time=data.get("tx_time", _now_iso()),
            tx_superseded=data.get("tx_superseded"),
            supersedes=data.get("supersedes"),
            superseded_by=data.get("superseded_by"),
            metadata=data.get("metadata", {}),
        )


class TripartiteAdrRegistry:
    """
    Bitemporal WORM ledger and registry for Tripartite ADRs (Data, Skills, Specs).
    Preserves all versions without destructive mutations.
    """

    def __init__(self):
        self._records: List[Union[DataADR, SkillADR, SpecADR, BaseADR]] = []

    def register(self, adr: Union[DataADR, SkillADR, SpecADR, BaseADR]) -> str:
        """Appends a new ADR record to the append-only ledger."""
        self._records.append(adr)
        return adr.adr_id

    def get(
        self,
        adr_id: str,
        as_of_tv: Optional[str] = None,
        as_of_tt: Optional[str] = None,
    ) -> Optional[Union[DataADR, SkillADR, SpecADR, BaseADR]]:
        """
        Retrieves the active ADR version matching the bitemporal slice (Tv, Tt).
        If as_of_tv or as_of_tt is omitted, assumes current time (NOW).
        """
        target_tv = as_of_tv or _now_iso()
        target_tt = as_of_tt or _now_iso()

        candidates = [
            r for r in self._records
            if r.adr_id == adr_id and r.is_visible_at(target_tt) and r.is_valid_at(target_tv)
        ]
        if not candidates:
            return None
        # Return latest transaction version
        candidates.sort(key=lambda r: r.tx_time, reverse=True)
        return candidates[0]

    def list_by_type(
        self,
        adr_type: ADRType,
        as_of_tv: Optional[str] = None,
        as_of_tt: Optional[str] = None,
    ) -> List[Union[DataADR, SkillADR, SpecADR, BaseADR]]:
        """Returns all active ADRs of a given ontological category."""
        target_tv = as_of_tv or _now_iso()
        target_tt = as_of_tt or _now_iso()

        active = {}
        for r in self._records:
            if r.adr_type == adr_type and r.is_visible_at(target_tt) and r.is_valid_at(target_tv):
                # Keep latest transaction version per adr_id
                if r.adr_id not in active or r.tx_time > active[r.adr_id].tx_time:
                    active[r.adr_id] = r
        return list(active.values())

    def supersede(
        self,
        old_adr_id: str,
        new_adr: Union[DataADR, SkillADR, SpecADR, BaseADR],
        tv: Optional[str] = None,
        tt: Optional[str] = None,
    ) -> bool:
        """
        Atomically supersedes old_adr_id with new_adr at bitemporal coordinate (Tv, Tt).
        Sets valid_to and tx_superseded on previous active version and records supersedes links.
        """
        now = _now_iso()
        cut_tv = tv or now
        cut_tt = tt or now

        # Find existing active record
        old = self.get(old_adr_id, as_of_tv=cut_tv, as_of_tt=cut_tt)
        if not old:
            return False

        # Mark old version closed
        old.valid_to = cut_tv
        old.tx_superseded = cut_tt
        old.status = "superseded"
        old.superseded_by = new_adr.adr_id

        # Prepare new version
        new_adr.supersedes = old_adr_id
        new_adr.valid_from = cut_tv
        new_adr.tx_time = cut_tt
        self.register(new_adr)
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the entire registry state."""
        return {
            "records": [r.to_dict() for r in self._records]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TripartiteAdrRegistry":
        """Reconstructs registry state from serialized dictionary."""
        reg = cls()
        for item in data.get("records", []):
            reg.register(deserialize_adr(item))
        return reg


class BitemporalExternalPreLogger:
    """
    Enforces the External Source Pre-Logging Axiom (ADR-010):
    'All requests to external services or APIs must first create or update an ADR of type
    Data in Utopia DB, and only after bitemporal commitment may be passed to skill logic.'
    """

    def __init__(self, registry: TripartiteAdrRegistry):
        self.registry = registry
        self._pre_logged_ids: List[str] = []

    def pre_log_external_call(
        self,
        service_name: str,
        endpoint: str,
        request_payload: Dict[str, Any],
        raw_response: Dict[str, Any],
        tv: Optional[str] = None,
    ) -> DataADR:
        """
        Persists raw external API response into a DataADR prior to downstream processing.
        """
        now = _now_iso()
        timestamp_slug = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        adr_id = f"ADR-DATA-EXT-{service_name.upper()}-{timestamp_slug}"

        payload_hash = _compute_hash(raw_response)
        data_adr = DataADR(
            adr_id=adr_id,
            title=f"External Data Capture: {service_name} [{endpoint}]",
            adr_type=ADRType.DATA,
            status="accepted",
            valid_from=tv or now,
            valid_to=None,
            tx_time=now,
            data_payload={
                "service": service_name,
                "endpoint": endpoint,
                "request": request_payload,
                "response": raw_response,
            },
            source_uri=f"ext://{service_name}/{endpoint.lstrip('/')}",
            raw_hash=payload_hash,
            metadata={
                "pre_logged": True,
                "pre_logged_at": now,
            }
        )

        self.registry.register(data_adr)
        self._pre_logged_ids.append(adr_id)
        return data_adr

    def verify_pre_logged(self, adr_id: str) -> bool:
        """Verifies if given data ADR was committed via bitemporal pre-logging."""
        record = self.registry.get(adr_id)
        if not record or record.adr_type != ADRType.DATA:
            return False
        return bool(record.metadata.get("pre_logged", False))
