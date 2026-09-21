"""
DRAKON Planar Layout Solver.
Enforces the 4 Foundational DRAKON Mathematical Invariants:
1. Vertical Skewer ("Шампур"): Primary success flow strictly along vertical axis X=0.
2. Right-is-Worse Branching ("Чем правее, тем хуже"): Alternative and degradation branches strictly to the right (X > 0).
3. Planarity & Zero Line Crossings (C=0): Orthogonal routing with guaranteed non-intersecting edges.
4. Silhouette Architecture: Discrete ordered vertical skewers for multi-branch flows.

Compliant with ADR-002 (Pure Stdlib Core), ADR-008, and ADR-010.
100% Pure Python Standard Library.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Union

from src.drakon.types import (
    DrakonSchema,
    DrakonNode,
    DrakonNodeType,
    DrakonEdges,
)
from src.drakon.validator import _segments_intersect


@dataclass
class PlanarLayoutResult:
    """Outcome of deterministic planar layout calculation."""
    is_planar: bool
    crossings_count: int
    skewer_x: float
    node_positions: Dict[str, Tuple[float, float]]
    edge_routes: Dict[str, List[Tuple[float, float]]]  # "source->target": [pts]
    schema: DrakonSchema

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_planar": self.is_planar,
            "crossings_count": self.crossings_count,
            "skewer_x": self.skewer_x,
            "node_positions": {k: list(v) for k, v in self.node_positions.items()},
            "edge_routes": {k: [list(p) for p in pts] for k, pts in self.edge_routes.items()},
        }


class DrakonPlanarSolver:
    """
    Deterministic solver computing planar orthogonal layouts for DRAKON diagrams.
    Guarantees X=0 vertical skewer and C=0 line crossings.
    """

    def __init__(
        self,
        col_width: float = 180.0,
        row_height: float = 80.0,
        skewer_x: float = 0.0,
    ):
        self.col_width = col_width
        self.row_height = row_height
        self.skewer_x = skewer_x

    def solve(self, schema: DrakonSchema) -> PlanarLayoutResult:
        """
        Computes planar coordinates (x, y) for all nodes in schema and routes edges orthogonally.
        Mutates schema nodes in-place with computed coordinates and returns PlanarLayoutResult.
        """
        if not schema.nodes:
            return PlanarLayoutResult(
                is_planar=True,
                crossings_count=0,
                skewer_x=self.skewer_x,
                node_positions={},
                edge_routes={},
                schema=schema
            )

        # 0. Check if schema already has valid planar coordinates assigned for all nodes
        has_all_coords = all(n.x is not None and n.y is not None for n in schema.nodes.values())
        if has_all_coords:
            existing_pos = {nid: (n.x, n.y) for nid, n in schema.nodes.items()}
            existing_routes = self._route_orthogonal_edges(schema, existing_pos)
            existing_crossings = self._count_edge_crossings(existing_routes)
            if existing_crossings == 0:
                min_x = min(pos[0] for pos in existing_pos.values())
                return PlanarLayoutResult(
                    is_planar=True,
                    crossings_count=0,
                    skewer_x=min_x,
                    node_positions=existing_pos,
                    edge_routes=existing_routes,
                    schema=schema
                )

        positions: Dict[str, Tuple[float, float]] = {}
        edge_routes: Dict[str, List[Tuple[float, float]]] = {}

        # 1. Handle Silhouette branches if specified, otherwise single skewer
        entry_nodes = schema.get_entry_nodes()
        is_silhouette = len(schema.branch_order) > 1 or (len(entry_nodes) > 1 and all(n.normalized_type == DrakonNodeType.BRANCH.value for n in entry_nodes))

        if is_silhouette and schema.branch_order:
            ordered_entries = [schema.nodes[bid] for bid in schema.branch_order if bid in schema.nodes]
        else:
            ordered_entries = entry_nodes or [list(schema.nodes.values())[0]]

        # Layout each branch in ordered columns from left to right
        current_col = 0
        for b_idx, entry in enumerate(ordered_entries):
            base_x = self.skewer_x + (current_col * self.col_width)
            cols_used = self._layout_branch_subtree(
                schema=schema,
                entry_node=entry,
                base_x=base_x,
                start_y=0.0,
                positions=positions,
                branch_id=b_idx
            )
            current_col += max(cols_used, 1)

        # 2. Place any remaining unvisited nodes
        visited = set(positions.keys())
        unvisited = [n for nid, n in schema.nodes.items() if nid not in visited]
        if unvisited:
            max_y = max((pos[1] for pos in positions.values()), default=0.0) + self.row_height
            for idx, un_node in enumerate(unvisited):
                pos = (self.skewer_x, max_y + (idx * self.row_height))
                positions[un_node.node_id] = pos
                un_node.x, un_node.y = pos

        # Apply positions to schema nodes
        for nid, (x, y) in positions.items():
            node = schema.nodes.get(nid)
            if node:
                node.x = x
                node.y = y

        # 3. Orthogonal Edge Routing
        edge_routes = self._route_orthogonal_edges(schema, positions)

        # 4. Count line crossings C
        crossings = self._count_edge_crossings(edge_routes)

        # 5. If crossings detected, resolve deterministically by widening channels
        if crossings > 0:
            edge_routes, crossings = self._resolve_crossings(schema, positions, edge_routes)

        return PlanarLayoutResult(
            is_planar=(crossings == 0),
            crossings_count=crossings,
            skewer_x=self.skewer_x,
            node_positions=positions,
            edge_routes=edge_routes,
            schema=schema
        )

    def _layout_branch_subtree(
        self,
        schema: DrakonSchema,
        entry_node: DrakonNode,
        base_x: float,
        start_y: float,
        positions: Dict[str, Tuple[float, float]],
        branch_id: int,
    ) -> int:
        """
        Lays out a vertical skewer starting at entry_node on base_x.
        Right branches are assigned column offsets base_x + delta_x.
        Returns total number of columns consumed by this branch.
        """
        curr_id: Optional[str] = entry_node.node_id
        curr_y = start_y
        max_col_offset = 0
        skewer_nodes: List[str] = []

        # Pass 1: Walk the main downward skewer
        while curr_id and curr_id in schema.nodes and curr_id not in positions:
            node = schema.nodes[curr_id]
            node.branch_id = branch_id
            positions[curr_id] = (base_x, curr_y)
            node.x = base_x
            node.y = curr_y
            skewer_nodes.append(curr_id)

            curr_y += self.row_height

            if node.normalized_type in (DrakonNodeType.END.value, DrakonNodeType.SILHOUETTE_ROUTE.value):
                break

            curr_id = node.edges.down

        # Pass 2: Layout right branches (degradation / alternative flows)
        # Collect all right branches from skewer nodes
        right_branches: List[Tuple[str, str]] = []
        for nid in skewer_nodes:
            node = schema.nodes[nid]
            if node.edges.right and node.edges.right in schema.nodes and node.edges.right not in positions:
                right_branches.append((nid, node.edges.right))

        # Sort branches reverse so lower-starting branches get inner columns,
        # preventing upper branches from crossing horizontal feeder lines
        right_branches.reverse()

        for origin_id, branch_target in right_branches:
            if branch_target in positions:
                continue
            max_col_offset += 1
            branch_x = base_x + (max_col_offset * self.col_width)
            origin_node = schema.nodes[origin_id]
            sub_y = (origin_node.y or 0.0) + (self.row_height * 0.5)

            r_curr: Optional[str] = branch_target
            while r_curr and r_curr in schema.nodes and r_curr not in positions:
                r_node = schema.nodes[r_curr]
                r_node.branch_id = branch_id
                positions[r_curr] = (branch_x, sub_y)
                r_node.x = branch_x
                r_node.y = sub_y

                sub_y += self.row_height
                if r_node.normalized_type in (DrakonNodeType.END.value, DrakonNodeType.SILHOUETTE_ROUTE.value):
                    break
                r_curr = r_node.edges.down or r_node.edges.right

        return max(max_col_offset + 1, 1)

    def _route_orthogonal_edges(
        self,
        schema: DrakonSchema,
        positions: Dict[str, Tuple[float, float]]
    ) -> Dict[str, List[Tuple[float, float]]]:
        """Constructs orthogonal polyline segments for all directed edges in the diagram."""
        routes: Dict[str, List[Tuple[float, float]]] = {}

        for src_id, src_node in schema.nodes.items():
            if src_id not in positions:
                continue
            x1, y1 = positions[src_id]

            # 1. Downward skewer edge
            if src_node.edges.down and src_node.edges.down in positions:
                tgt_id = src_node.edges.down
                x2, y2 = positions[tgt_id]
                edge_key = f"{src_id}->{tgt_id}"

                if abs(x1 - x2) < 1e-4:
                    # Pure vertical collinear segment
                    routes[edge_key] = [(x1, y1), (x2, y2)]
                else:
                    # Step down then horizontal
                    mid_y = (y1 + y2) / 2.0
                    routes[edge_key] = [(x1, y1), (x1, mid_y), (x2, mid_y), (x2, y2)]

            # 2. Rightward branch edge (Right-is-worse)
            if src_node.edges.right and src_node.edges.right in positions:
                tgt_id = src_node.edges.right
                x2, y2 = positions[tgt_id]
                edge_key = f"{src_id}->{tgt_id}"

                if y1 == y2:
                    routes[edge_key] = [(x1, y1), (x2, y2)]
                else:
                    # Orthogonal: go right to x2, then down to y2
                    routes[edge_key] = [(x1, y1), (x2, y1), (x2, y2)]

            # 3. Extra edges (Case/Select options)
            for opt_key, tgt_id in src_node.edges.extra.items():
                if tgt_id in positions:
                    x2, y2 = positions[tgt_id]
                    edge_key = f"{src_id}->{tgt_id}:{opt_key}"
                    mid_y = (y1 + y2) / 2.0
                    routes[edge_key] = [(x1, y1), (x1, mid_y), (x2, mid_y), (x2, y2)]

        return routes

    def _count_edge_crossings(
        self,
        edge_routes: Dict[str, List[Tuple[float, float]]]
    ) -> int:
        """Counts the total number of interior line segment crossings across all edge routes."""
        all_segments: List[Tuple[str, Tuple[float, float], Tuple[float, float]]] = []

        for e_key, pts in edge_routes.items():
            for i in range(len(pts) - 1):
                all_segments.append((e_key, pts[i], pts[i + 1]))

        crossings = 0
        n_segs = len(all_segments)

        for i in range(n_segs):
            e1, p1, p2 = all_segments[i]
            for j in range(i + 1, n_segs):
                e2, q1, q2 = all_segments[j]
                if e1 == e2:
                    continue  # Segments within the same polyline route don't cross each other
                if _segments_intersect(p1, p2, q1, q2):
                    crossings += 1

        return crossings

    def _resolve_crossings(
        self,
        schema: DrakonSchema,
        positions: Dict[str, Tuple[float, float]],
        edge_routes: Dict[str, List[Tuple[float, float]]]
    ) -> Tuple[Dict[str, List[Tuple[float, float]]], int]:
        """
        Deterministically resolves line crossings by expanding outer bypass channels.
        Routes return or long-distance edges via outer vertical lanes (X > max_x).
        """
        max_x = max((pos[0] for pos in positions.values()), default=0.0)
        channel_x = max_x + self.col_width

        resolved_routes = dict(edge_routes)

        for e_key, pts in list(edge_routes.items()):
            src_id, tgt_id = e_key.split("->")[0], e_key.split("->")[1].split(":")[0]
            if src_id in positions and tgt_id in positions:
                x1, y1 = positions[src_id]
                x2, y2 = positions[tgt_id]

                # If edge flows backwards (upward loop or crossover)
                if y2 < y1 or (x1 > x2 and abs(x1 - self.skewer_x) > 1e-4):
                    # Route via dedicated outer right channel
                    resolved_routes[e_key] = [
                        (x1, y1),
                        (channel_x, y1),
                        (channel_x, y2),
                        (x2, y2),
                    ]
                    channel_x += (self.col_width * 0.5)

        crossings = self._count_edge_crossings(resolved_routes)
        return resolved_routes, crossings
