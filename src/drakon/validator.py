"""
Pure Standard Library DRAKON Schema & Topological Validator.
Enforces the 4 Foundational DRAKON Mathematical Invariants and B-SDD Bitemporal Contracts:
1. The Vertical Skewer ("Шампур") - Happy path is strictly vertical on left-most coordinate.
2. Right-is-Worse Branching ("Чем правее, тем хуже") - Down is normal; right is degradation/exception ordered by severity.
3. Planarity & Zero Line Crossings - Control-flow edges must never intersect.
4. Silhouette Architecture ("Силуэт") - Multi-branch algorithms ordered left-to-right with zero dead code.
5. Bitemporal ADR Semantic Binding - Validates node bindings against active/superseded ADR invariants.
6. Topology Immutability - Restricts leaf action nodes from mutating graph topology.

100% Pure Python Standard Library (ADR-008).
"""
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union

from src.drakon.types import (
    DrakonSchema,
    DrakonNode,
    ValidationError,
    ValidationResult,
    DrakonNodeType,
)

SEVERITY_WEIGHTS = {
    "normal": 0,
    "success": 0,
    "info": 1,
    "mild": 1,
    "warning": 2,
    "degraded": 2,
    "retry": 2,
    "fallback": 3,
    "severe": 3,
    "error": 3,
    "critical": 4,
    "fatal": 4,
    "abort": 4,
}


def _ccw(a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> float:
    """Counter-clockwise orientation test for points A, B, C."""
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _segments_intersect(
    p1: Tuple[float, float], p2: Tuple[float, float],
    q1: Tuple[float, float], q2: Tuple[float, float]
) -> bool:
    """Checks if line segment p1-p2 and q1-q2 intersect at an INTERIOR point.
    Shared endpoints (e.g. p1 == q1) do NOT count as a crossing.
    """
    # If segments share an endpoint, they do not cross each other topologically
    if p1 == q1 or p1 == q2 or p2 == q1 or p2 == q2:
        return False

    # Check for orthogonal horizontal / vertical intersection first
    # Case 1: p1-p2 is horizontal, q1-q2 is vertical
    if p1[1] == p2[1] and q1[0] == q2[0]:
        y_h = p1[1]
        x_v = q1[0]
        min_x, max_x = min(p1[0], p2[0]), max(p1[0], p2[0])
        min_y, max_y = min(q1[1], q2[1]), max(q1[1], q2[1])
        return (min_x < x_v < max_x) and (min_y < y_h < max_y)

    # Case 2: p1-p2 is vertical, q1-q2 is horizontal
    if p1[0] == p2[0] and q1[1] == q2[1]:
        x_v = p1[0]
        y_h = q1[1]
        min_x, max_x = min(q1[0], q2[0]), max(q1[0], q2[0])
        min_y, max_y = min(p1[1], p2[1]), max(p1[1], p2[1])
        return (min_x < x_v < max_x) and (min_y < y_h < max_y)

    # General segment intersection via orientation
    d1 = _ccw(p1, p2, q1)
    d2 = _ccw(p1, p2, q2)
    d3 = _ccw(q1, q2, p1)
    d4 = _ccw(q1, q2, p2)

    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True

    return False


class DrakonValidator:
    """Pure Standard Library DRAKON Schema & Invariant Validator."""

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = (root_dir or Path.cwd()).resolve()
        self._active_adr_invariants: Set[str] = set()
        self._superseded_adr_invariants: Set[str] = set()
        self._load_repository_adr_invariants()

    def _load_repository_adr_invariants(self) -> None:
        """Discovers ADRs in docs/adr/ and categorizes active vs superseded invariants."""
        adr_dir = self.root_dir / "docs" / "adr"
        if not adr_dir.exists():
            return

        superseded_adr_ids: Set[str] = set()
        adr_map: Dict[str, Dict[str, Any]] = {}

        for file_path in adr_dir.glob("*.md"):
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            # Extract ADR ID e.g. ADR-008
            match_id = re.search(r"^(?:#\s*)?(ADR-\d+)", content, re.IGNORECASE | re.MULTILINE)
            if not match_id:
                continue
            adr_id = match_id.group(1).upper()

            # Status
            match_status = re.search(r"^\*\s*\*\*Status:\*\*\s*(\w+)", content, re.IGNORECASE | re.MULTILINE)
            status = match_status.group(1).lower() if match_status else "accepted"

            # Supersedes
            match_super = re.search(r"^\*\s*\*\*Supersedes:\*\*\s*([^\n\r]+)", content, re.IGNORECASE | re.MULTILINE)
            supersedes_raw = match_super.group(1).strip() if match_super else "none"

            if supersedes_raw.lower() != "none":
                for sup_id in re.findall(r"ADR-\d+", supersedes_raw, re.IGNORECASE):
                    superseded_adr_ids.add(sup_id.upper())

            # Extract invariants
            invariants: List[str] = []
            inv_section = re.search(r"##\s*Invariants\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
            if inv_section:
                for line in inv_section.group(1).splitlines():
                    line = line.strip()
                    if line.startswith("-") or line.startswith("*"):
                        item = line.lstrip("-*").strip()
                        inv_match = re.search(r"\b([A-Z0-9_\-]+-INV-\d+)\b", item)
                        if inv_match:
                            invariants.append(inv_match.group(1))
                        else:
                            invariants.append(item)

            adr_map[adr_id] = {
                "status": status,
                "invariants": invariants
            }

        for adr_id, info in adr_map.items():
            is_superseded = (adr_id in superseded_adr_ids) or (info["status"] == "superseded")
            target_set = self._superseded_adr_invariants if is_superseded else self._active_adr_invariants
            target_set.add(adr_id)
            for inv in info["invariants"]:
                target_set.add(inv)

    def validate(
        self,
        schema: DrakonSchema,
        active_invariants: Optional[Set[str]] = None,
        superseded_invariants: Optional[Set[str]] = None,
        current_time: Optional[datetime] = None
    ) -> ValidationResult:
        """Executes full architectural and topological validation on the DRAKON schema."""
        errors: List[ValidationError] = []
        warnings: List[ValidationError] = []

        active_inv = active_invariants if active_invariants is not None else self._active_adr_invariants
        superseded_inv = superseded_invariants if superseded_invariants is not None else self._superseded_adr_invariants
        now_dt = current_time or datetime.now(timezone.utc)

        # 1. Graph Syntactic & Structural Integrity
        self._validate_graph_integrity(schema, errors, warnings)

        # 2. Invariant 1: The Vertical Skewer ("Шампур")
        self._validate_vertical_skewer(schema, errors, warnings)

        # 3. Invariant 2: Right-is-Worse Branching ("Чем правее, тем хуже")
        self._validate_right_is_worse(schema, errors, warnings)

        # 4. Invariant 3: Planarity & Zero Line Crossings
        self._validate_zero_line_crossings(schema, errors, warnings)

        # 5. Invariant 4: Silhouette Architecture ("Силуэт")
        self._validate_silhouette_architecture(schema, errors, warnings)

        # 6. Bitemporal ADR Invariant Semantic Bindings
        self._validate_bitemporal_bindings(schema, active_inv, superseded_inv, now_dt, errors, warnings)

        # 7. Topology Immutability & Leaf Action Node Bounding
        self._validate_topology_immutability(schema, errors, warnings)

        is_valid = (len(errors) == 0)
        stats = {
            "node_count": len(schema.nodes),
            "branch_count": len(schema.branch_order) or 1,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "verified_invariants": sum(
                1 for n in schema.nodes.values()
                if n.semantic_binding and n.semantic_binding.adr_invariant_id
            )
        }

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            stats=stats
        )

    def _validate_graph_integrity(
        self,
        schema: DrakonSchema,
        errors: List[ValidationError],
        warnings: List[ValidationError]
    ) -> None:
        """Validates node existence, edge references, entry points, and reachability."""
        if not schema.nodes:
            errors.append(ValidationError(
                rule="GRAPH_INTEGRITY",
                message="DRAKON diagram contains zero nodes."
            ))
            return

        # Check entry nodes
        entry_nodes = schema.get_entry_nodes()
        if not entry_nodes:
            errors.append(ValidationError(
                rule="GRAPH_INTEGRITY",
                message="DRAKON diagram has no entry point (headline or branch)."
            ))

        # Check terminal nodes
        terminal_nodes = [
            n for n in schema.nodes.values()
            if n.normalized_type in (DrakonNodeType.END.value, DrakonNodeType.SILHOUETTE_ROUTE.value)
        ]
        if not terminal_nodes:
            errors.append(ValidationError(
                rule="GRAPH_INTEGRITY",
                message="DRAKON diagram lacks a terminal node (end or silhouette_route)."
            ))

        # Referential edge integrity
        for node_id, node in schema.nodes.items():
            for target in node.edges.all_targets():
                if target not in schema.nodes:
                    errors.append(ValidationError(
                        rule="GRAPH_INTEGRITY",
                        message=f"Edge from node '{node_id}' targets non-existent node '{target}'.",
                        node_id=node_id
                    ))

        # Reachability / Dead Code Check
        reachable: Set[str] = set()
        queue: List[str] = [n.node_id for n in entry_nodes]
        for q in queue:
            reachable.add(q)

        while queue:
            curr_id = queue.pop(0)
            node = schema.nodes.get(curr_id)
            if not node:
                continue
            for target in node.edges.all_targets():
                if target in schema.nodes and target not in reachable:
                    reachable.add(target)
                    queue.append(target)

        unreachable = set(schema.nodes.keys()) - reachable
        for dead_id in unreachable:
            errors.append(ValidationError(
                rule="DEAD_CODE",
                message=f"Unreachable dead-code node detected: '{dead_id}' ({schema.nodes[dead_id].normalized_type}).",
                node_id=dead_id
            ))

    def _validate_vertical_skewer(
        self,
        schema: DrakonSchema,
        errors: List[ValidationError],
        warnings: List[ValidationError]
    ) -> None:
        """Invariant 1: The Vertical Skewer ("Шампур").
        The main success trajectory flows strictly vertically downward on the left-most coordinate.
        Leftward deviation from the skewer is categorically prohibited.
        """
        entry_nodes = schema.get_entry_nodes()

        for entry in entry_nodes:
            skewer_x = entry.x
            curr_id: Optional[str] = entry.node_id
            visited: Set[str] = set()
            prev_y: Optional[float] = None

            while curr_id and curr_id in schema.nodes and curr_id not in visited:
                visited.add(curr_id)
                node = schema.nodes[curr_id]

                # Check vertical collinearity along skewer if coordinates specified
                if skewer_x is not None and node.x is not None:
                    if abs(node.x - skewer_x) > 1e-4:
                        errors.append(ValidationError(
                            rule="VERTICAL_SKEWER",
                            message=(
                                f"Skewer verticality violation at node '{node.node_id}': "
                                f"expected x={skewer_x}, but found x={node.x}."
                            ),
                            node_id=node.node_id
                        ))

                # Check downward monotonic progression
                if prev_y is not None and node.y is not None:
                    if node.y <= prev_y:
                        errors.append(ValidationError(
                            rule="VERTICAL_SKEWER",
                            message=(
                                f"Skewer downward flow violation at node '{node.node_id}': "
                                f"y={node.y} is not greater than preceding y={prev_y}."
                            ),
                            node_id=node.node_id
                        ))

                if node.y is not None:
                    prev_y = node.y

                # Leftward deviation check for any outward edges
                for target_id in node.edges.all_targets():
                    target_node = schema.nodes.get(target_id)
                    if target_node and skewer_x is not None and target_node.x is not None:
                        if target_node.x < skewer_x - 1e-4:
                            errors.append(ValidationError(
                                rule="VERTICAL_SKEWER",
                                message=(
                                    f"Prohibited leftward deviation from skewer from node '{node.node_id}' "
                                    f"to '{target_id}' (target x={target_node.x} < skewer x={skewer_x})."
                                ),
                                node_id=node.node_id
                            ))

                if node.normalized_type in (DrakonNodeType.END.value, DrakonNodeType.SILHOUETTE_ROUTE.value):
                    break

                curr_id = node.edges.down

    def _validate_right_is_worse(
        self,
        schema: DrakonSchema,
        errors: List[ValidationError],
        warnings: List[ValidationError]
    ) -> None:
        """Invariant 2: Right-is-Worse Branching ("Чем правее, тем хуже").
        In decision nodes:
        - Down is normal / success flow.
        - Right is degradation / error flow.
        - The branch must go strictly to the right (x_branch > x_node).
        - Multiple branches must be ordered monotonically by severity from left to right.
        """
        for node_id, node in schema.nodes.items():
            if node.normalized_type == DrakonNodeType.QUESTION.value:
                # Question must have a downward continuation
                if not node.edges.down:
                    errors.append(ValidationError(
                        rule="RIGHT_IS_WORSE",
                        message=f"Question node '{node_id}' lacks a primary downward (success) transition.",
                        node_id=node_id
                    ))

                # Question must branch right
                if not node.edges.right:
                    errors.append(ValidationError(
                        rule="RIGHT_IS_WORSE",
                        message=f"Question node '{node_id}' lacks a rightward degradation branch.",
                        node_id=node_id
                    ))
                else:
                    right_node = schema.nodes.get(node.edges.right)
                    if right_node and node.x is not None and right_node.x is not None:
                        if right_node.x < node.x - 1e-4:
                            errors.append(ValidationError(
                                rule="RIGHT_IS_WORSE",
                                message=(
                                    f"Right-is-worse violation at question '{node_id}': degradation branch "
                                    f"to '{right_node.node_id}' branches left (target x={right_node.x} < node x={node.x})."
                                ),
                                node_id=node_id
                            ))
                        elif abs(right_node.x - node.x) <= 1e-4:
                            # Reconvergent bypass jump down the same skewer: target y must be downstream
                            if right_node.y is not None and node.y is not None and right_node.y <= node.y:
                                errors.append(ValidationError(
                                    rule="RIGHT_IS_WORSE",
                                    message=(
                                        f"Right-is-worse violation at question '{node_id}': degradation branch "
                                        f"to '{right_node.node_id}' loops upward or horizontally (target y={right_node.y} <= node y={node.y})."
                                    ),
                                    node_id=node_id
                                ))

            # Check monotonic severity ordering across multiple degradation targets
            if node.edges.extra:
                ordered_cases: List[Tuple[float, int, str]] = []
                for case_label, target_id in node.edges.extra.items():
                    target_node = schema.nodes.get(target_id)
                    if not target_node or target_node.x is None:
                        continue
                    severity_str = (
                        (target_node.semantic_binding and target_node.semantic_binding.severity)
                        or case_label.lower()
                    )
                    weight = SEVERITY_WEIGHTS.get(severity_str, 1)
                    ordered_cases.append((target_node.x, weight, target_id))

                # Verify that x increases monotonically with severity
                ordered_cases.sort(key=lambda item: item[0])  # sort by x
                max_seen_weight = -1
                for x_pos, weight, t_id in ordered_cases:
                    if weight < max_seen_weight:
                        errors.append(ValidationError(
                            rule="RIGHT_IS_WORSE",
                            message=(
                                f"Non-monotonic severity ordering at branch target '{t_id}': "
                                f"higher severity was placed to the left of lower severity."
                            ),
                            node_id=node_id
                        ))
                    max_seen_weight = max(max_seen_weight, weight)

    def _validate_zero_line_crossings(
        self,
        schema: DrakonSchema,
        errors: List[ValidationError],
        warnings: List[ValidationError]
    ) -> None:
        """Invariant 3: Planarity & Zero Line Crossings.
        Control-flow edges must never intersect in 2D space.
        """
        # Collect edge segments in 2D space
        # Down edges: vertical straight line (x, y) -> (x, target.y)
        # Right edges: Manhattan orthogonal lines: (x, y) -> (target.x, y) -> (target.x, target.y)
        segments: List[Tuple[Tuple[float, float], Tuple[float, float], str, str]] = []

        for node_id, node in schema.nodes.items():
            if node.x is None or node.y is None:
                continue

            # Down edge
            if node.edges.down and node.edges.down in schema.nodes:
                target = schema.nodes[node.edges.down]
                if target.x is not None and target.y is not None:
                    if abs(node.x - target.x) < 1e-4:
                        segments.append(((node.x, node.y), (target.x, target.y), node_id, target.node_id))
                    else:
                        # Offset edge (e.g. corner routing)
                        corner = (target.x, node.y)
                        segments.append(((node.x, node.y), corner, node_id, target.node_id))
                        segments.append((corner, (target.x, target.y), node_id, target.node_id))

            # Right edge (Manhattan routing)
            if node.edges.right and node.edges.right in schema.nodes:
                target = schema.nodes[node.edges.right]
                if target.x is not None and target.y is not None:
                    if abs(node.x - target.x) < 1e-4:
                        # Bypass on same column: routes out to the right and rejoins
                        bypass_x = node.x + 2.0
                        c1 = (bypass_x, node.y)
                        c2 = (bypass_x, target.y)
                        segments.append(((node.x, node.y), c1, node_id, target.node_id))
                        segments.append((c1, c2, node_id, target.node_id))
                        segments.append((c2, (target.x, target.y), node_id, target.node_id))
                    else:
                        corner = (target.x, node.y)
                        segments.append(((node.x, node.y), corner, node_id, target.node_id))
                        if corner != (target.x, target.y):
                            segments.append((corner, (target.x, target.y), node_id, target.node_id))

        # Check all pairs of segments for intersections
        num_segments = len(segments)
        for i in range(num_segments):
            p1, p2, src1, dst1 = segments[i]
            for j in range(i + 1, num_segments):
                q1, q2, src2, dst2 = segments[j]

                # Skip if edges share same source or destination
                if src1 == src2 or dst1 == dst2 or src1 == dst2 or dst1 == src2:
                    continue

                if _segments_intersect(p1, p2, q1, q2):
                    errors.append(ValidationError(
                        rule="ZERO_CROSSINGS",
                        message=(
                            f"Topological line crossing violation detected between edge ({src1} -> {dst1}) "
                            f"and edge ({src2} -> {dst2}). DRAKON grammar requires zero edge intersections."
                        ),
                        node_id=src1
                    ))

    def _validate_silhouette_architecture(
        self,
        schema: DrakonSchema,
        errors: List[ValidationError],
        warnings: List[ValidationError]
    ) -> None:
        """Invariant 4: Silhouette Architecture ("Силуэт").
        Decomposes complex algorithms into ordered vertical subtrees (branches).
        Branches must be ordered monotonically left-to-right with valid terminal transfers.
        """
        if len(schema.branch_order) > 1:
            prev_x: Optional[float] = None
            for idx, branch_id in enumerate(schema.branch_order):
                branch_node = schema.nodes.get(branch_id)
                if not branch_node:
                    continue

                if branch_node.branch_id is not None and branch_node.branch_id != idx:
                    warnings.append(ValidationError(
                        rule="SILHOUETTE_ORDER",
                        message=f"Branch '{branch_id}' branchId {branch_node.branch_id} differs from index {idx}.",
                        node_id=branch_id,
                        severity="warning"
                    ))

                if branch_node.x is not None:
                    if prev_x is not None and branch_node.x <= prev_x:
                        errors.append(ValidationError(
                            rule="SILHOUETTE_ORDER",
                            message=(
                                f"Silhouette branch ordering violation: branch '{branch_id}' (x={branch_node.x}) "
                                f"is not to the right of preceding branch (x={prev_x})."
                            ),
                            node_id=branch_id
                        ))
                    prev_x = branch_node.x

                # Check branch terminal transfer
                curr_id: Optional[str] = branch_id
                visited: Set[str] = set()
                branch_terminated = False

                while curr_id and curr_id in schema.nodes and curr_id not in visited:
                    visited.add(curr_id)
                    node = schema.nodes[curr_id]
                    if node.normalized_type in (DrakonNodeType.END.value, DrakonNodeType.SILHOUETTE_ROUTE.value):
                        branch_terminated = True
                        break
                    curr_id = node.edges.down

                if not branch_terminated:
                    errors.append(ValidationError(
                        rule="SILHOUETTE_STRUCTURE",
                        message=f"Silhouette branch '{branch_id}' has no valid termination (end or silhouette_route).",
                        node_id=branch_id
                    ))

    def _validate_bitemporal_bindings(
        self,
        schema: DrakonSchema,
        active_invariants: Set[str],
        superseded_invariants: Set[str],
        now_dt: datetime,
        errors: List[ValidationError],
        warnings: List[ValidationError]
    ) -> None:
        """Validates semantic bindings against bitemporal ADR horizons."""
        for node_id, node in schema.nodes.items():
            binding = node.semantic_binding
            if not binding:
                continue

            # 1. ADR Invariant Check
            if binding.adr_invariant_id:
                inv_id = binding.adr_invariant_id.strip()

                # Check if superseded
                if inv_id in superseded_invariants:
                    errors.append(ValidationError(
                        rule="BITEMPORAL_INVARIANT",
                        message=(
                            f"Node '{node_id}' references superseded ADR invariant '{inv_id}'. "
                            f"Superseded invariants are mathematically pruned from agent execution."
                        ),
                        node_id=node_id
                    ))
                elif active_invariants and inv_id not in active_invariants:
                    # Invariant not found in active set
                    warnings.append(ValidationError(
                        rule="BITEMPORAL_INVARIANT",
                        message=f"Node '{node_id}' references unrecognized ADR invariant '{inv_id}'.",
                        node_id=node_id,
                        severity="warning"
                    ))

            # 2. Temporal Scope Expiry Check
            if binding.temporal_scope:
                valid_to_str = binding.temporal_scope.get("valid_to")
                if valid_to_str:
                    try:
                        # Normalize ISO string
                        clean_iso = valid_to_str.replace("Z", "+00:00")
                        valid_to_dt = datetime.fromisoformat(clean_iso)
                        if valid_to_dt.tzinfo is None:
                            valid_to_dt = valid_to_dt.replace(tzinfo=timezone.utc)
                        if valid_to_dt <= now_dt:
                            errors.append(ValidationError(
                                rule="BITEMPORAL_INVARIANT",
                                message=(
                                    f"Node '{node_id}' temporal scope expired (valid_to={valid_to_str} <= now). "
                                    f"Expired entities must not be executed."
                                ),
                                node_id=node_id
                            ))
                    except ValueError:
                        warnings.append(ValidationError(
                            rule="BITEMPORAL_INVARIANT",
                            message=f"Node '{node_id}' has malformed valid_to timestamp: '{valid_to_str}'.",
                            node_id=node_id,
                            severity="warning"
                        ))

    def _validate_topology_immutability(
        self,
        schema: DrakonSchema,
        errors: List[ValidationError],
        warnings: List[ValidationError]
    ) -> None:
        """Validates that leaf action nodes do not alter graph topology."""
        for node_id, node in schema.nodes.items():
            if node.normalized_type == DrakonNodeType.ACTION.value:
                # Action nodes cannot branch right
                if node.edges.right is not None:
                    errors.append(ValidationError(
                        rule="TOPOLOGY_IMMUTABILITY",
                        message=(
                            f"Action node '{node_id}' contains a right-branch transition ('{node.edges.right}'). "
                            f"Action nodes are leaf tasks and must not alter control flow topology."
                        ),
                        node_id=node_id
                    ))
                # Action nodes cannot have extra branches
                if node.edges.extra:
                    errors.append(ValidationError(
                        rule="TOPOLOGY_IMMUTABILITY",
                        message=(
                            f"Action node '{node_id}' contains extra branching transitions. "
                            f"Branching is restricted to Question, Choice, and Select primitives."
                        ),
                        node_id=node_id
                    ))
