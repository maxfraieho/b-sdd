"""
Pure Standard Library DRAKON Diagram and IR Parser.
Compliant with ADR-008 (DRAKON Visual Algorithmic Logic & Developer Workbench).
100% Pure Python Standard Library.
"""
import json
import re
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple, Set

from src.drakon.types import (
    DrakonSchema,
    DrakonNode,
    DrakonEdges,
    SemanticBinding,
    DrakonNodeType,
)


class DrakonParser:
    """Parser for DRAKON diagrams in multiple formats:
    - Classic DRAKON JSON (`items` dictionary with `one`, `two`, `type`)
    - Canonical DRAKON-IR (ADR-008 JSON schema)
    - Drakon text format (.drn)
    """

    @classmethod
    def parse_file(cls, file_path: Union[str, Path]) -> DrakonSchema:
        """Parses a diagram file (.json or .drn) from disk."""
        path = Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"DRAKON diagram file not found: {path}")

        raw_text = path.read_text(encoding="utf-8")
        return cls.parse_string(raw_text, default_name=path.stem)

    @classmethod
    def parse_string(cls, content: str, default_name: str = "Unnamed DRAKON Scheme") -> DrakonSchema:
        """Parses diagram from raw string (JSON or .drn text format)."""
        stripped = content.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                data = json.loads(stripped)
                return cls.parse_dict(data, default_name=default_name)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON syntax in DRAKON content: {exc}") from exc

        # Parse text-based .drn format
        return cls.parse_drn_text(content, default_name=default_name)

    @classmethod
    def parse_dict(cls, data: Dict[str, Any], default_name: str = "Unnamed DRAKON Scheme") -> DrakonSchema:
        """Parses raw dictionary representation into canonical DrakonSchema."""
        name = data.get("name") or default_name
        schema_version = str(data.get("schema_version", "1.0"))
        params = data.get("params")
        meta = data.get("meta", {})

        # Check if Format A: Classic Drakon format (`items: {...}`)
        if "items" in data and isinstance(data["items"], dict):
            return cls._parse_classic_format(name, params, data["items"], meta, schema_version)

        # Check if Format B: Canonical DRAKON-IR (`nodes: [...]` or `nodes: {...}`)
        if "nodes" in data:
            return cls._parse_ir_format(name, params, data["nodes"], meta, schema_version, data.get("branch_order"))

        raise ValueError("Unrecognized DRAKON diagram schema: missing 'items' or 'nodes' section.")

    @classmethod
    def _parse_classic_format(
        cls,
        name: str,
        params: Any,
        items: Dict[str, Any],
        meta: Dict[str, Any],
        schema_version: str
    ) -> DrakonSchema:
        """Parses classic DrakonHub / ai-drakon-scaffolder JSON structure."""
        nodes: Dict[str, DrakonNode] = {}
        branches: List[Tuple[int, str]] = []

        for item_id, item_data in items.items():
            if not isinstance(item_data, dict):
                continue

            node_type = str(item_data.get("type", "action")).lower().strip()
            content = str(item_data.get("content") or item_data.get("text") or item_data.get("label") or "")
            down_ref = item_data.get("one")
            right_ref = item_data.get("two")
            branch_id = item_data.get("branchId")

            if node_type == "branch" and branch_id is not None:
                branches.append((int(branch_id), str(item_id)))

            # Coordinates
            x_coord = item_data.get("x")
            y_coord = item_data.get("y")
            x_val = float(x_coord) if x_coord is not None else None
            y_val = float(y_coord) if y_coord is not None else None

            # Semantic binding if present
            binding = None
            if "semantic_binding" in item_data:
                binding = SemanticBinding.from_dict(item_data["semantic_binding"])
            elif "adr_invariant_id" in item_data or "utopia_entity_id" in item_data:
                binding = SemanticBinding(
                    adr_invariant_id=item_data.get("adr_invariant_id"),
                    utopia_entity_id=item_data.get("utopia_entity_id"),
                    temporal_scope=item_data.get("temporal_scope"),
                    severity=item_data.get("severity")
                )

            edges = DrakonEdges(
                down=str(down_ref) if down_ref is not None else None,
                right=str(right_ref) if right_ref is not None else None,
            )

            # Preserve extra case targets if present
            for k, v in item_data.items():
                if k.startswith("case_") or k.startswith("branch_"):
                    edges.extra[k] = str(v)

            node = DrakonNode(
                node_id=str(item_id),
                node_type=node_type,
                label=content,
                edges=edges,
                semantic_binding=binding,
                x=x_val,
                y=y_val,
                branch_id=int(branch_id) if branch_id is not None else None,
                raw_data=item_data
            )
            nodes[str(item_id)] = node

        # Sort branches by branchId
        branches.sort(key=lambda b: b[0])
        branch_order = [b[1] for b in branches]

        schema = DrakonSchema(
            name=name,
            schema_version=schema_version,
            params=params,
            nodes=nodes,
            branch_order=branch_order,
            meta=meta
        )

        cls._infer_missing_coordinates(schema)
        return schema

    @classmethod
    def _parse_ir_format(
        cls,
        name: str,
        params: Any,
        nodes_data: Union[List[Dict[str, Any]], Dict[str, Any]],
        meta: Dict[str, Any],
        schema_version: str,
        explicit_branch_order: Optional[List[str]] = None
    ) -> DrakonSchema:
        """Parses canonical DRAKON-IR JSON AST (ADR-008)."""
        nodes: Dict[str, DrakonNode] = {}
        branches: List[Tuple[int, str]] = []

        raw_list = nodes_data if isinstance(nodes_data, list) else list(nodes_data.values())

        for idx, item_data in enumerate(raw_list):
            if not isinstance(item_data, dict):
                continue

            node_id = str(item_data.get("node_id") or item_data.get("id") or str(idx + 1))
            node_type = str(item_data.get("node_type") or item_data.get("type", "action")).lower().strip()
            label = str(item_data.get("label") or item_data.get("content") or "")

            edges_raw = item_data.get("edges", {})
            if isinstance(edges_raw, dict):
                down = edges_raw.get("down") or edges_raw.get("one")
                right = edges_raw.get("right") or edges_raw.get("two")
                extra = {k: str(v) for k, v in edges_raw.items() if k not in ("down", "right", "one", "two")}
            else:
                down = item_data.get("one")
                right = item_data.get("two")
                extra = {}

            edges = DrakonEdges(
                down=str(down) if down is not None else None,
                right=str(right) if right is not None else None,
                extra=extra
            )

            binding_data = item_data.get("semantic_binding")
            binding = SemanticBinding.from_dict(binding_data) if binding_data else None

            branch_id = item_data.get("branch_id")
            if branch_id is None and "branchId" in item_data:
                branch_id = item_data["branchId"]

            if node_type == "branch" and branch_id is not None:
                branches.append((int(branch_id), node_id))

            x_coord = item_data.get("x")
            y_coord = item_data.get("y")
            x_val = float(x_coord) if x_coord is not None else None
            y_val = float(y_coord) if y_coord is not None else None

            node = DrakonNode(
                node_id=node_id,
                node_type=node_type,
                label=label,
                edges=edges,
                semantic_binding=binding,
                x=x_val,
                y=y_val,
                branch_id=int(branch_id) if branch_id is not None else None,
                raw_data=item_data
            )
            nodes[node_id] = node

        if explicit_branch_order:
            branch_order = [str(b) for b in explicit_branch_order]
        else:
            branches.sort(key=lambda b: b[0])
            branch_order = [b[1] for b in branches]

        schema = DrakonSchema(
            name=name,
            schema_version=schema_version,
            params=params,
            nodes=nodes,
            branch_order=branch_order,
            meta=meta
        )

        cls._infer_missing_coordinates(schema)
        return schema

    @classmethod
    def parse_drn_text(cls, content: str, default_name: str = "Unnamed DRAKON Scheme") -> DrakonSchema:
        """Parses textual DRAKON format (.drn lines)."""
        lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]
        name = default_name
        params = None
        nodes: Dict[str, DrakonNode] = {}
        branch_order: List[str] = []

        current_branch_id = 0
        prev_node_id: Optional[str] = None

        for line_idx, line in enumerate(lines):
            # Header line: name: ... or params: ...
            if line.lower().startswith("name:"):
                name = line.split(":", 1)[1].strip()
                continue
            if line.lower().startswith("params:"):
                params = line.split(":", 1)[1].strip()
                continue

            node_id = f"n{line_idx + 1}"
            parts = line.split("|", 1)
            type_part = parts[0].strip().lower()
            text_part = parts[1].strip() if len(parts) > 1 else ""

            # Check if branch header
            if type_part.startswith("branch"):
                branch_node_id = f"b{current_branch_id}"
                node = DrakonNode(
                    node_id=branch_node_id,
                    node_type=DrakonNodeType.BRANCH.value,
                    label=text_part or f"Branch {current_branch_id}",
                    branch_id=current_branch_id
                )
                nodes[branch_node_id] = node
                branch_order.append(branch_node_id)
                if prev_node_id and prev_node_id in nodes and nodes[prev_node_id].edges.down is None:
                    nodes[prev_node_id].edges.down = branch_node_id
                prev_node_id = branch_node_id
                current_branch_id += 1
                continue

            # Parse question with branch routes e.g. "question: cond ? -> one: id1, two: id2"
            if "question" in type_part:
                node_type = DrakonNodeType.QUESTION.value
            elif "end" in type_part:
                node_type = DrakonNodeType.END.value
            elif "header" in type_part or "headline" in type_part:
                node_type = DrakonNodeType.HEADLINE.value
            else:
                node_type = DrakonNodeType.ACTION.value

            node = DrakonNode(
                node_id=node_id,
                node_type=node_type,
                label=text_part or type_part
            )

            # Auto link sequential down edges
            if prev_node_id and prev_node_id in nodes:
                prev_n = nodes[prev_node_id]
                if prev_n.edges.down is None and prev_n.normalized_type != DrakonNodeType.END.value:
                    prev_n.edges.down = node_id

            nodes[node_id] = node
            prev_node_id = node_id

        schema = DrakonSchema(
            name=name,
            params=params,
            nodes=nodes,
            branch_order=branch_order
        )
        cls._infer_missing_coordinates(schema)
        return schema

    @classmethod
    def _infer_missing_coordinates(cls, schema: DrakonSchema) -> None:
        """Assigns canonical topological 2D grid coordinates (x, y) if not already present.
        Follows the vertical skewer rule:
        1. Identifies the primary skewer down paths from each entry node (x = base_x, increasing y).
        2. Places side degradation/fallback branches to the right (x > base_x).
        """
        # If all nodes already have coordinates, keep them
        if all(n.x is not None and n.y is not None for n in schema.nodes.values()) and schema.nodes:
            return

        entry_nodes = schema.get_entry_nodes()
        branch_spacing = 10.0
        visited_skewer: Set[str] = set()

        # Step 1: Assign skewer coordinates
        for b_idx, entry in enumerate(entry_nodes):
            base_x = float(b_idx) * branch_spacing
            curr_y = 0.0

            curr_id: Optional[str] = entry.node_id
            while curr_id and curr_id in schema.nodes and curr_id not in visited_skewer:
                node = schema.nodes[curr_id]
                visited_skewer.add(curr_id)

                if node.x is None:
                    node.x = base_x
                if node.y is None:
                    node.y = curr_y

                curr_y += 2.0
                curr_id = node.edges.down

        # Step 2: Assign coordinates for side branches (right-is-worse)
        visited_branches: Set[str] = set()

        def place_branch_subtree(start_node_id: str, col_x: float, start_y: float) -> None:
            curr: Optional[str] = start_node_id
            curr_y = start_y
            while curr and curr in schema.nodes and curr not in visited_skewer and curr not in visited_branches:
                visited_branches.add(curr)
                n = schema.nodes[curr]
                if n.x is None:
                    n.x = col_x
                if n.y is None:
                    n.y = curr_y

                # If this side node also branches right:
                if n.edges.right and n.edges.right in schema.nodes:
                    place_branch_subtree(n.edges.right, col_x + 2.0, curr_y)

                curr_y += 2.0
                curr = n.edges.down

        # Queue right branches from skewer nodes
        for node in list(schema.nodes.values()):
            if node.edges.right and node.edges.right in schema.nodes:
                right_id = node.edges.right
                if right_id not in visited_skewer and right_id not in visited_branches:
                    base_x = node.x if node.x is not None else 0.0
                    base_y = node.y if node.y is not None else 0.0
                    place_branch_subtree(right_id, base_x + 2.0, base_y)

        # Step 3: Handle any remaining unplaced nodes
        max_y = max((n.y for n in schema.nodes.values() if n.y is not None), default=0.0) + 2.0
        for node in schema.nodes.values():
            if node.x is None:
                node.x = 0.0
            if node.y is None:
                node.y = max_y
                max_y += 2.0

    @classmethod
    def to_ir_dict(cls, schema: DrakonSchema) -> Dict[str, Any]:
        """Serializes DrakonSchema to canonical DRAKON-IR dictionary."""
        return schema.to_dict()

    @classmethod
    def to_ir_json(cls, schema: DrakonSchema, indent: int = 2) -> str:
        """Serializes DrakonSchema to formatted DRAKON-IR JSON string."""
        return json.dumps(schema.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def generate_prompt_constraints(cls, schema: DrakonSchema) -> str:
        """Generates deterministic prompt constraints from the DRAKON flow (ADR-008).
        Ensures AI agents are strictly restricted to synthesizing leaf action bodies
        without altering the control flow topology.
        """
        lines = [
            f"# DRAKON Algorithmic Execution Specification: {schema.name}",
            f"<!-- Schema Version: {schema.schema_version} | Nodes: {len(schema.nodes)} -->",
            "",
            "## MANDATORY TOPOLOGICAL EXECUTION INVARIANTS:",
            "- [TOPOLOGY_IMMUTABILITY] The algorithm control-flow graph is fixed and mathematically proven. You MUST NOT add, delete, or alter any branching paths, condition outcomes, or state transitions.",
            "- [LEAF_ACTION_BOUNDING] Code generation is strictly bounded to implementing the inner logic of designated ACTION nodes. Do not create unmanaged loops or bypassed branches.",
            "- [RIGHT_IS_WORSE] Normal execution flows strictly down the vertical skewer. Right branches represent degradation, fallback, and error handling policies.",
            ""
        ]

        # Invariant Bindings
        bindings = []
        for n_id, n in schema.nodes.items():
            if n.semantic_binding and n.semantic_binding.adr_invariant_id:
                bindings.append((n_id, n.normalized_type, n.label, n.semantic_binding.adr_invariant_id))

        if bindings:
            lines.append("## VERIFIED ADR INVARIANT BINDINGS:")
            for n_id, n_type, lbl, adr_id in bindings:
                lines.append(f"- Node `{n_id}` ({n_type}): Invariant `{adr_id}` -> \"{lbl}\"")
            lines.append("")

        # Algorithmic Steps Execution Sequence
        lines.append("## ALGORITHMIC EXECUTION SEQUENCE:")
        entry_nodes = schema.get_entry_nodes()

        for b_idx, entry in enumerate(entry_nodes):
            if len(entry_nodes) > 1:
                lines.append(f"### Silhouette Branch {b_idx}: {entry.label or entry.node_id}")

            curr_id: Optional[str] = entry.node_id
            visited: Set[str] = set()
            step = 1

            while curr_id and curr_id in schema.nodes and curr_id not in visited:
                node = schema.nodes[curr_id]
                visited.add(curr_id)

                ntype = node.normalized_type
                if ntype == DrakonNodeType.ACTION.value:
                    lines.append(f"{step}. [ACTION] `{node.node_id}`: {node.label}")
                elif ntype == DrakonNodeType.QUESTION.value:
                    right_target = node.edges.right or "None"
                    lines.append(f"{step}. [DECISION] `{node.node_id}`: {node.label}")
                    lines.append(f"   - Happy Path (DOWN): Continue to `{node.edges.down}`")
                    lines.append(f"   - Degradation Path (RIGHT): Branch to `{right_target}`")
                elif ntype == DrakonNodeType.END.value:
                    lines.append(f"{step}. [TERMINAL] `{node.node_id}`: End of execution flow.")
                else:
                    lines.append(f"{step}. [{ntype.upper()}] `{node.node_id}`: {node.label}")

                step += 1
                curr_id = node.edges.down

        lines.append("")
        return "\n".join(lines)
