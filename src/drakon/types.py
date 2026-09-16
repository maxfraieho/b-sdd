"""
DRAKON-IR (Intermediate Representation) Types and Data Models.
Compliant with ADR-008 (DRAKON Visual Algorithmic Logic & Developer Workbench).
100% Pure Python Standard Library.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum


class DrakonNodeType(str, Enum):
    """Canonical primitive types for DRAKON graph elements."""
    HEADLINE = "headline"
    HEADER = "header"             # Alias for headline
    BRANCH = "branch"             # Silhouette subtree entry
    ACTION = "action"             # Atomic state mutation / task
    QUESTION = "question"         # Invariant condition / decision
    CHOICE = "choice"             # Multi-way branch option
    SELECT = "select"             # Multi-way selection header
    SILHOUETTE_ROUTE = "silhouette_route"  # Inter-branch transfer / address
    ADDRESS = "address"           # Alias for silhouette_route
    LOOP_BEGIN = "loopbegin"      # Loop header
    LOOP_END = "loopend"          # Loop terminal
    INSERTION = "insertion"       # Subroutine macro-icon
    END = "end"                   # Terminal exit node


@dataclass
class SemanticBinding:
    """Bitemporal and ontological semantic binding for DRAKON nodes (ADR-008)."""
    adr_invariant_id: Optional[str] = None
    utopia_entity_id: Optional[str] = None
    temporal_scope: Optional[Dict[str, Optional[str]]] = None
    severity: Optional[str] = None  # normal, mild, degraded, severe, fatal

    def to_dict(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {}
        if self.adr_invariant_id:
            res["adr_invariant_id"] = self.adr_invariant_id
        if self.utopia_entity_id:
            res["utopia_entity_id"] = self.utopia_entity_id
        if self.temporal_scope:
            res["temporal_scope"] = self.temporal_scope
        if self.severity:
            res["severity"] = self.severity
        return res

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "SemanticBinding":
        if not data:
            return cls()
        return cls(
            adr_invariant_id=data.get("adr_invariant_id"),
            utopia_entity_id=data.get("utopia_entity_id"),
            temporal_scope=data.get("temporal_scope"),
            severity=data.get("severity")
        )


@dataclass
class DrakonEdges:
    """Outward transition edges partitioned into down (skewer) and right (degradation)."""
    down: Optional[str] = None       # Primary success skewer target ("one")
    right: Optional[str] = None      # Degradation / alternative branch target ("two")
    extra: Dict[str, str] = field(default_factory=dict)  # Case options or additional ports

    def all_targets(self) -> List[str]:
        targets = []
        if self.down:
            targets.append(self.down)
        if self.right:
            targets.append(self.right)
        targets.extend(self.extra.values())
        return targets

    def to_dict(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {}
        if self.down is not None:
            res["down"] = self.down
        if self.right is not None:
            res["right"] = self.right
        if self.extra:
            res["extra"] = self.extra
        return res

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "DrakonEdges":
        if not data:
            return cls()
        down = data.get("down")
        right = data.get("right")
        extra = data.get("extra", {})
        return cls(down=down, right=right, extra=extra)


@dataclass
class DrakonNode:
    """Canonical DRAKON-IR graph node."""
    node_id: str
    node_type: str
    label: str = ""
    edges: DrakonEdges = field(default_factory=DrakonEdges)
    semantic_binding: Optional[SemanticBinding] = None
    x: Optional[float] = None
    y: Optional[float] = None
    branch_id: Optional[int] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @property
    def normalized_type(self) -> str:
        t = self.node_type.lower().strip()
        if t == "header":
            return DrakonNodeType.HEADLINE.value
        if t == "address":
            return DrakonNodeType.SILHOUETTE_ROUTE.value
        return t

    def to_dict(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {
            "node_id": self.node_id,
            "node_type": self.normalized_type,
            "label": self.label,
            "edges": self.edges.to_dict()
        }
        if self.semantic_binding:
            binding_dict = self.semantic_binding.to_dict()
            if binding_dict:
                res["semantic_binding"] = binding_dict
        if self.x is not None:
            res["x"] = self.x
        if self.y is not None:
            res["y"] = self.y
        if self.branch_id is not None:
            res["branch_id"] = self.branch_id
        return res


@dataclass
class DrakonSchema:
    """Represents a complete DRAKON diagram parsed into canonical DRAKON-IR."""
    name: str
    schema_version: str = "1.0"
    params: Optional[Any] = None
    nodes: Dict[str, DrakonNode] = field(default_factory=dict)
    branch_order: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    def get_node(self, node_id: str) -> Optional[DrakonNode]:
        return self.nodes.get(node_id)

    def get_entry_nodes(self) -> List[DrakonNode]:
        """Returns the diagram root entry nodes (headline or ordered silhouette branches)."""
        if self.branch_order:
            return [self.nodes[bid] for bid in self.branch_order if bid in self.nodes]
        # Search for headline or root nodes with no incoming edges
        incoming: Set[str] = set()
        for node in self.nodes.values():
            for target in node.edges.all_targets():
                incoming.add(target)
        roots = [n for n_id, n in self.nodes.items() if n_id not in incoming]
        if not roots:
            # Fallback to headline / header
            roots = [n for n in self.nodes.values() if n.normalized_type in (DrakonNodeType.HEADLINE.value, DrakonNodeType.BRANCH.value)]
        return roots

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "name": self.name,
            "params": self.params,
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "branch_order": self.branch_order,
            "meta": self.meta
        }


@dataclass
class ValidationError:
    """Individual rule violation detected during DRAKON schema validation."""
    rule: str               # e.g. VERTICAL_SKEWER, RIGHT_IS_WORSE, ZERO_CROSSING, SILHOUETTE_ORDER, BITEMPORAL_INVARIANT
    message: str
    node_id: Optional[str] = None
    severity: str = "error" # "error" | "warning"

    def to_dict(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {
            "rule": self.rule,
            "message": self.message,
            "severity": self.severity
        }
        if self.node_id:
            res["node_id"] = self.node_id
        return res


@dataclass
class ValidationResult:
    """Comprehensive outcome of DRAKON schema validation."""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "stats": self.stats
        }

    def raise_if_invalid(self):
        if not self.is_valid:
            err_msgs = "\n".join(f" - [{e.rule}] (node: {e.node_id or 'graph'}): {e.message}" for e in self.errors)
            raise ValueError(f"DRAKON Schema Validation Failed with {len(self.errors)} error(s):\n{err_msgs}")
