"""
B-SDD MCP Gateway Toolkit: GitNexus AST Knowledge Graph & Code Intelligence.
Implements KuzuDB AST graph queries, symbol blast radius auditing,
and cross-workspace code search compliant with ADR-004 and ADR-015.
100% Pure Python Standard Library (ADR-002).
"""
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.adapters.gitnexus_graph import (
    MultiWorkspaceSymbolIndexer,
    GitNexusBlastRadiusAuditor,
    CrossRepoSemanticGraphResolver,
)

GLOBAL_INDEXER: Optional[MultiWorkspaceSymbolIndexer] = None


def _get_indexer() -> MultiWorkspaceSymbolIndexer:
    global GLOBAL_INDEXER
    if GLOBAL_INDEXER is None:
        GLOBAL_INDEXER = MultiWorkspaceSymbolIndexer(default_root=ROOT_DIR)
        ui_path = ROOT_DIR / "b-sdd-ui"
        if ui_path.exists():
            GLOBAL_INDEXER.register_workspace("ui", ui_path, is_active=False)
    return GLOBAL_INDEXER


def query_ast_graph(
    query_type: str = "cross_repo",
    valid_time_day: Optional[int] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Executes an AST knowledge graph query over the repository codebase.
    Supports cross-repo dependency resolution and call-graph path analysis.
    """
    try:
        indexer = _get_indexer()
        graph = CrossRepoSemanticGraphResolver(indexer=indexer)
        if query_type == "cross_repo":
            edges = graph.resolve_cross_repo_dependencies(valid_time_day=valid_time_day)
            return {
                "status": "SUCCESS",
                "query_type": "cross_repo",
                "valid_time_day": valid_time_day,
                "edge_count": len(edges),
                "edges": edges
            }
        else:
            res = graph.query(params or {})
            return {
                "status": "SUCCESS",
                "query_type": query_type,
                "result": res
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "query_type": query_type,
            "error": str(e)
        }


def audit_blast_radius(
    symbol_name: str,
    max_depth: int = 3,
    files: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Audits the blast radius and architectural risk score for modifying or refactoring a symbol.
    Returns direct callers, downstream affected files, and risk severity (LOW/MEDIUM/HIGH).
    """
    try:
        auditor = GitNexusBlastRadiusAuditor(repo_root=ROOT_DIR)
        res = auditor.audit_symbol_blast_radius(
            symbol_name=symbol_name,
            max_depth=max_depth
        )
        impacted = res.get("impacted_files", [])
        risk = res.get("risk", res.get("risk_level", "LOW"))
        score = res.get("blast_radius_score", float(len(impacted)) * 1.5)
        return {
            "status": "SUCCESS",
            "symbol": symbol_name,
            "direct_callers": res.get("direct_callers", res.get("target_definitions", [])),
            "affected_files": impacted,
            "blast_radius_score": score,
            "risk_level": risk,
            "contained": not res.get("reconciliation_required", False),
            "summary": f"Symbol '{symbol_name}' blast radius: {risk} (Affected files: {len(impacted)})"
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "symbol": symbol_name,
            "error": str(e)
        }


def symbol_search(
    query: str,
    workspace: Optional[str] = None,
    symbol_type: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Searches the multi-workspace code knowledge graph for matching classes, functions, and methods.
    """
    try:
        indexer = _get_indexer()
        results = indexer.search_symbols(
            query=query,
            workspace=workspace,
            symbol_type=symbol_type,
            limit=limit
        )
        return {
            "status": "SUCCESS",
            "query": query,
            "workspace": workspace,
            "match_count": len(results),
            "symbols": results
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "query": query,
            "error": str(e)
        }


def get_tools_spec() -> List[Dict[str, Any]]:
    """Returns MCP tools catalog definition for toolkit_gitnexus."""
    return [
        {
            "name": "gitnexus_ast_query",
            "description": "Queries the GitNexus KuzuDB AST knowledge graph for dependencies and edges.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query_type": {
                        "type": "string",
                        "enum": ["cross_repo", "raw"],
                        "default": "cross_repo",
                        "description": "Graph query type."
                    },
                    "valid_time_day": {
                        "type": "integer",
                        "description": "Optional temporal snapshot day."
                    },
                    "params": {"type": "object", "description": "Optional parameters."}
                }
            }
        },
        {
            "name": "gitnexus_blast_radius",
            "description": "Audits the blast radius, caller tree, and architectural risk score for modifying a symbol.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbol_name": {"type": "string", "description": "Symbol name to audit (e.g. 'LayaClient')."},
                    "max_depth": {"type": "integer", "default": 3, "description": "Max call graph depth."},
                    "files": {"type": "array", "items": {"type": "string"}, "description": "Optional file list filter."}
                },
                "required": ["symbol_name"]
            }
        },
        {
            "name": "gitnexus_symbol_search",
            "description": "Searches the codebase for symbol definitions (classes, functions, methods).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Symbol query substring."},
                    "workspace": {"type": "string", "description": "Workspace filter (e.g. 'root' or 'ui')."},
                    "symbol_type": {
                        "type": "string",
                        "enum": ["class", "function", "method"],
                        "description": "Symbol kind."
                    },
                    "limit": {"type": "integer", "default": 50}
                },
                "required": ["query"]
            }
        }
    ]
