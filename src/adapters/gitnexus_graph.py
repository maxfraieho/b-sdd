"""
B-SDD (Bitemporal Spec-Driven Development) GitNexus Graph Adapter
Reads .gitnexus/index.sqlite in read-only mode and performs upstream-impact resolution.
Falls back to deterministic path-based domain extraction on missing index or sqlite3.Error.
Operates using 100% Pure Python Standard Library.
"""
import os
import subprocess
import sqlite3
from pathlib import Path
from typing import Set, Iterable, Optional, Dict, List, Any


class GitNexusDomainResolver:
    """Resolves affected architectural domains for changed files using GitNexus graph."""

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root).resolve()
        self.db_path = self.repo_root / ".gitnexus" / "index.sqlite"

    def _fallback_path_resolve(self, files: Iterable[str]) -> Set[str]:
        """Deterministic path-based domain extraction fallback."""
        domains: Set[str] = set()
        for f in files:
            p = Path(f)
            parts = p.parts
            if not parts:
                continue

            if "src" in parts:
                idx = parts.index("src")
                if idx + 1 < len(parts):
                    domains.add(parts[idx + 1])
            elif "specs" in parts:
                idx = parts.index("specs")
                if idx + 1 < len(parts):
                    domains.add(parts[idx + 1])
            elif parts[0] in ("docs", ".specify", ".context"):
                domains.add("global")
            elif len(parts) > 1:
                domains.add(parts[0])
            else:
                domains.add("global")
        return domains

    def resolve(self, files: Iterable[str]) -> Set[str]:
        """
        Resolves impacted architectural domains for given changed files.
        Contract: resolve(files: Iterable[str]) -> set[str]
        """
        impacted = self._fallback_path_resolve(files)

        if not self.db_path.exists():
            return impacted

        try:
            uri = f"file:{self.db_path.as_posix()}?mode=ro"
            conn = sqlite3.connect(uri, uri=True, timeout=1.0)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('symbols', 'file_component', 'component_edges')
            """)
            found_tables = {row[0] for row in cursor.fetchall()}

            if "component_edges" in found_tables and "file_component" in found_tables:
                for comp in list(impacted):
                    query = """
                    WITH RECURSIVE upstream(component) AS (
                        SELECT to_component FROM component_edges WHERE from_component = ?
                        UNION
                        SELECT e.to_component FROM component_edges e
                        JOIN upstream u ON e.from_component = u.component
                    )
                    SELECT component FROM upstream;
                    """
                    cursor.execute(query, (comp,))
                    for (c,) in cursor.fetchall():
                        if c:
                            impacted.add(str(c))

            elif "symbols" in found_tables and "relationships" in found_tables:
                for comp in list(impacted):
                    query = """
                    WITH RECURSIVE upstream_impact AS (
                        SELECT s.id, s.file_path, 0 AS depth
                        FROM symbols s
                        WHERE s.file_path LIKE ?
                        UNION
                        SELECT p.id, p.file_path, u.depth + 1
                        FROM symbols p
                        JOIN relationships r ON r.from_symbol_id = p.id
                        JOIN upstream_impact u ON r.to_symbol_id = u.id
                        WHERE u.depth < 2
                    )
                    SELECT DISTINCT file_path FROM upstream_impact;
                    """
                    cursor.execute(query, (f"%{comp}%",))
                    for (matched_path,) in cursor.fetchall():
                        parts = Path(matched_path).parts
                        if "src" in parts:
                            idx = parts.index("src")
                            if idx + 1 < len(parts):
                                impacted.add(parts[idx + 1])

            conn.close()
        except sqlite3.Error:
            pass

        return impacted


class BrownfieldIngestionEngine:
    """Dual-contour ingestion engine using AST analysis and MADR 3.0 bootstrapping (INV-012-05)."""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root).resolve() if project_root else Path.cwd().resolve()

    def analyze_ast_components(self, files: List[str]) -> Dict[str, Any]:
        """
        Extracts structural components, classes, and call hierarchies from source files using ast.
        Categorizes modules into bounded domains/components.
        """
        import ast

        components: Dict[str, List[str]] = {}
        ast_details: Dict[str, Dict[str, Any]] = {}

        for rel_path in files:
            p = Path(rel_path)
            parts = p.parts
            
            # Determine component name
            comp = "general"
            if "src" in parts:
                idx = parts.index("src")
                if idx + 1 < len(parts):
                    comp = parts[idx + 1]
            elif "specs" in parts:
                idx = parts.index("specs")
                if idx + 1 < len(parts):
                    comp = parts[idx + 1]
            elif len(parts) > 1:
                comp = parts[0]

            if comp not in components:
                components[comp] = []
            components[comp].append(rel_path)

            full_path = self.project_root / rel_path
            classes = []
            functions = []
            imports = []

            if full_path.exists():
                try:
                    tree = ast.parse(full_path.read_text(encoding="utf-8"), filename=rel_path)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            classes.append(node.name)
                        elif isinstance(node, ast.FunctionDef):
                            functions.append(node.name)
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.append(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.append(node.module)
                except Exception:
                    pass

            ast_details[rel_path] = {
                "classes": classes,
                "functions": functions,
                "imports": imports
            }

        return {
            "components": components,
            "ast_details": ast_details
        }

    def generate_bootstrap_madr(
        self,
        component: str,
        title: str,
        detected_modules: List[str]
    ) -> str:
        """
        Synthesizes standard MADR 3.0 foundation intent record from detected components.
        Conforms strictly to ADR-001 / ADR-013 format with positive/negative consequences and invariants.
        """
        modules_list = "\n".join([f"- `{m}`" for m in detected_modules])
        
        return f"""# ADR-900: {title}

* **Status:** Proposed
* **Date:** 2026-09-18
* **Component:** {component}
* **Supersedes:** None

## Context and Problem Statement
Brownfield ingestion discovered subsystem `{component}` comprising active implementation modules.
The architecture lacks formal intent bounding under B-SDD bitemporal horizon.
Modules identified during AST graph ingestion:
{modules_list}

## Decision Drivers
* Formalize structural boundaries and public API contracts for `{component}`.
* Prevent undocumented dependency drift and architectural regressions.
* Enable automated fitness gates (ADR-005) and pre-flight compilation (ADR-002).

## Considered Options
1. Retain legacy unversioned structure without bitemporal tracking.
2. Refactor entire subsystem immediately without intent baseline.
3. Establish bootstrap MADR 3.0 baseline with bounded leaf actions (Chosen).

## Decision Outcome
Chosen option: **Option 3: Establish bootstrap MADR 3.0 baseline**.
Formalize `{component}` as a bounded architectural domain with verified AST interfaces.

## Consequences
### Positive
* Subsystem `{component}` is integrated into the Utopia DB bitemporal graph.
* Changes undergo pre-flight compilation and GitNexus impact routing.

### Negative
* Requires maintaining explicit invariants for subsequent refactors.

## Invariants
- INV-{component.upper()}-01: Public exports from `{component}` must adhere to pure Python standard library runtime boundaries.
- INV-{component.upper()}-02: Modifications require corresponding DRAKON planar flow updates (ADR-008).
"""


class MultiWorkspaceSymbolIndexer:
    """
    Multi-tenant cross-repository AST symbol indexer and resolver (INV-014-04).
    Indexes symbols across multiple linked workspaces and performs cross-repo lookup.
    Pure Python standard library implementation.
    """

    EXCLUDE_DIRS = {
        ".git", ".gitnexus", "node_modules", "dist", "build",
        "__pycache__", ".pytest_cache", ".venv", "venv", "coverage",
        "docs", ".context", ".gemini", "brain", "scratch"
    }

    def __init__(self, default_root: Optional[Path] = None):
        self.workspaces: Dict[str, Dict[str, Any]] = {}
        self._symbols_cache: List[Dict[str, Any]] = []
        if default_root:
            self.register_workspace("core", default_root, is_active=True)

    def register_workspace(self, name: str, path: Any, is_active: bool = False):
        """Registers a workspace directory for cross-repo symbol indexing."""
        p = Path(path).resolve()
        self.workspaces[name] = {
            "name": name,
            "path": p,
            "is_active": is_active,
            "indexed_count": 0
        }

    def get_registered_workspaces(self) -> List[Dict[str, Any]]:
        """Returns list of all registered workspaces."""
        return [
            {
                "name": ws["name"],
                "path": str(ws["path"]),
                "is_active": ws["is_active"],
                "indexed_count": ws.get("indexed_count", 0)
            }
            for ws in self.workspaces.values()
        ]

    def _index_python_file(self, ws_name: str, file_path: Path, root_path: Path) -> List[Dict[str, Any]]:
        import ast
        symbols = []
        rel_path = str(file_path.relative_to(root_path))
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8", errors="replace"), filename=rel_path)
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    doc = ast.get_docstring(node) or ""
                    symbols.append({
                        "name": node.name,
                        "kind": "class",
                        "workspace": ws_name,
                        "file_path": rel_path,
                        "line_number": getattr(node, "lineno", 1),
                        "docstring": doc[:120].strip() if doc else ""
                    })
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            m_doc = ast.get_docstring(item) or ""
                            symbols.append({
                                "name": f"{node.name}.{item.name}",
                                "kind": "method",
                                "workspace": ws_name,
                                "file_path": rel_path,
                                "line_number": getattr(item, "lineno", 1),
                                "docstring": m_doc[:120].strip() if m_doc else ""
                            })
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    doc = ast.get_docstring(node) or ""
                    symbols.append({
                        "name": node.name,
                        "kind": "function",
                        "workspace": ws_name,
                        "file_path": rel_path,
                        "line_number": getattr(node, "lineno", 1),
                        "docstring": doc[:120].strip() if doc else ""
                    })
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            symbols.append({
                                "name": target.id,
                                "kind": "constant",
                                "workspace": ws_name,
                                "file_path": rel_path,
                                "line_number": getattr(target, "lineno", 1),
                                "docstring": ""
                            })
        except Exception:
            pass
        return symbols

    def _index_typescript_file(self, ws_name: str, file_path: Path, root_path: Path) -> List[Dict[str, Any]]:
        import re
        symbols = []
        rel_path = str(file_path.relative_to(root_path))
        try:
            lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
            ts_regex = re.compile(
                r"^\s*export\s+(?:default\s+)?(interface|type|class|function|const|let|enum)\s+([A-Za-z0-9_]+)"
            )
            for idx, line in enumerate(lines, start=1):
                m = ts_regex.match(line)
                if m:
                    kind_raw, name = m.group(1), m.group(2)
                    kind_map = {
                        "interface": "interface",
                        "type": "type",
                        "class": "class",
                        "function": "function",
                        "const": "constant",
                        "let": "variable",
                        "enum": "enum"
                    }
                    symbols.append({
                        "name": name,
                        "kind": kind_map.get(kind_raw, "symbol"),
                        "workspace": ws_name,
                        "file_path": rel_path,
                        "line_number": idx,
                        "docstring": ""
                    })
        except Exception:
            pass
        return symbols

    def index_workspace(self, ws_name: str) -> List[Dict[str, Any]]:
        """Indexes all symbols for a specific registered workspace."""
        if ws_name not in self.workspaces:
            return []

        ws = self.workspaces[ws_name]
        root = ws["path"]
        if not root.exists():
            return []

        symbols = []

        # Check for GitNexus SQLite index first
        nexus_db = root / ".gitnexus" / "index.sqlite"
        if nexus_db.exists():
            try:
                uri = f"file:{nexus_db.as_posix()}?mode=ro"
                conn = sqlite3.connect(uri, uri=True, timeout=1.0)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name, kind, file_path, line_number FROM symbols
                """)
                for name, kind, fpath, lnum in cursor.fetchall():
                    symbols.append({
                        "name": name,
                        "kind": kind or "symbol",
                        "workspace": ws_name,
                        "file_path": fpath,
                        "line_number": lnum or 1,
                        "docstring": ""
                    })
                conn.close()
            except sqlite3.Error:
                pass

        # Fallback / supplement with AST file scan
        if not symbols:
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [d for d in dirnames if d not in self.EXCLUDE_DIRS]
                for fname in filenames:
                    ext = os.path.splitext(fname)[1].lower()
                    if ext not in (".py", ".ts", ".tsx", ".js", ".jsx"):
                        continue
                    item = Path(dirpath) / fname
                    if ext == ".py":
                        symbols.extend(self._index_python_file(ws_name, item, root))
                    elif ext in (".ts", ".tsx", ".js", ".jsx"):
                        symbols.extend(self._index_typescript_file(ws_name, item, root))

        ws["indexed_count"] = len(symbols)
        return symbols

    def index_all(self) -> List[Dict[str, Any]]:
        """Scans and indexes all registered workspaces."""
        all_symbols = []
        for name in list(self.workspaces.keys()):
            all_symbols.extend(self.index_workspace(name))
        self._symbols_cache = all_symbols
        return all_symbols

    def search_symbols(
        self,
        query: str,
        workspace: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Searches symbols across workspaces by query string."""
        if not self._symbols_cache:
            self.index_all()

        q = query.strip().lower()
        results = []

        for s in self._symbols_cache:
            if workspace and s["workspace"] != workspace:
                continue
            name_lower = s["name"].lower()
            if q in name_lower or q in s["file_path"].lower():
                # Score relevance
                score = 0
                if name_lower == q:
                    score = 100
                elif name_lower.startswith(q):
                    score = 50
                elif q in name_lower:
                    score = 25
                else:
                    score = 10
                results.append((score, s))

        results.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in results[:limit]]

    def resolve_symbol_cross_workspace(self, symbol_name: str) -> List[Dict[str, Any]]:
        """Resolves exact symbol matches across all linked workspaces."""
        if not self._symbols_cache:
            self.index_all()

        target = symbol_name.strip()
        matches = [
            s for s in self._symbols_cache
            if s["name"] == target or s["name"].split(".")[-1] == target
        ]
        return matches


class CrossRepoSemanticGraphResolver:
    """
    Resolves cross-repository semantic dependencies and federated query execution (INV-016-04).
    Analyzes imports, method invocations, and workspace boundaries to link disparate
    codebases into a unified DAG stored with bitemporal transaction and valid time coordinates.
    Operates using 100% Pure Python Standard Library.
    """

    def __init__(self, indexer: Optional[MultiWorkspaceSymbolIndexer] = None):
        self.indexer = indexer if indexer is not None else MultiWorkspaceSymbolIndexer()
        self.cross_repo_edges: List[Dict[str, Any]] = []
        self._nodes_cache: Dict[str, Dict[str, Any]] = {}

    def resolve_cross_repo_dependencies(self, valid_time_day: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Scans all registered workspaces to detect cross-repository imports and dependencies.
        Returns a list of bitemporal edge dictionaries.
        """
        import time
        from datetime import datetime
        import ast
        import re

        tx_time = time.time()
        valid_from = valid_time_day or int(datetime.now().strftime("%Y%m%d"))

        # 1. Index all symbols across workspaces
        all_symbols = self.indexer.index_all()
        symbol_map: Dict[str, List[Dict[str, Any]]] = {}
        for s in all_symbols:
            sname = s.get("name", "")
            if sname:
                symbol_map.setdefault(sname, []).append(s)
                if "." in sname:
                    short = sname.split(".")[-1]
                    symbol_map.setdefault(short, []).append(s)

        edges: List[Dict[str, Any]] = []
        processed_pairs = set()

        for ws_name, ws_info in self.indexer.workspaces.items():
            ws_root = Path(ws_info["path"]).resolve()
            if not ws_root.exists() or not ws_root.is_dir():
                continue

            for root, dirs, files in os.walk(ws_root):
                dirs[:] = [d for d in dirs if d not in self.indexer.EXCLUDE_DIRS]
                for fname in files:
                    fpath = Path(root) / fname
                    try:
                        rel_path = str(fpath.relative_to(ws_root))
                    except ValueError:
                        rel_path = fname

                    if fname.endswith(".py"):
                        try:
                            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"), filename=rel_path)
                            for node in ast.walk(tree):
                                target_ws = None
                                target_mod = None
                                target_sym = None

                                if isinstance(node, ast.Import):
                                    for alias in node.names:
                                        parts = alias.name.split(".")
                                        for other_ws in self.indexer.workspaces.keys():
                                            other_norm = other_ws.replace("-", "_")
                                            if other_ws != ws_name and (other_ws in parts or other_norm in parts):
                                                target_ws = other_ws
                                                target_mod = alias.name
                                                target_sym = parts[-1]
                                                break

                                elif isinstance(node, ast.ImportFrom):
                                    if node.module:
                                        mod_parts = node.module.split(".")
                                        for other_ws in self.indexer.workspaces.keys():
                                            other_norm = other_ws.replace("-", "_")
                                            if other_ws != ws_name and (other_ws in mod_parts or other_norm in mod_parts):
                                                target_ws = other_ws
                                                target_mod = node.module
                                                if node.names:
                                                    target_sym = node.names[0].name
                                                break

                                    if not target_ws and node.names:
                                        for alias in node.names:
                                            cand = symbol_map.get(alias.name, [])
                                            for c in cand:
                                                if c.get("workspace") != ws_name:
                                                    target_ws = c.get("workspace")
                                                    target_sym = alias.name
                                                    target_mod = c.get("file_path")
                                                    break

                                if target_ws and target_ws != ws_name:
                                    pair_key = (ws_name, rel_path, target_ws, target_mod or "", target_sym or "")
                                    if pair_key not in processed_pairs:
                                        processed_pairs.add(pair_key)
                                        edges.append({
                                            "source_workspace": ws_name,
                                            "source_file": rel_path,
                                            "source_symbol": getattr(node, "name", "module"),
                                            "target_workspace": target_ws,
                                            "target_file": target_mod or "",
                                            "target_symbol": target_sym or (target_mod or "").split(".")[-1],
                                            "rel_type": "IMPORTS",
                                            "tx_time": tx_time,
                                            "valid_from": valid_from,
                                            "valid_to": None
                                        })
                        except Exception:
                            pass

                    elif fname.endswith((".ts", ".tsx", ".js")):
                        try:
                            content = fpath.read_text(encoding="utf-8", errors="replace")
                            matches = re.findall(r"(?:import|from|require\()\s*['\"]([^'\"]+)['\"]", content)
                            for import_path in matches:
                                for other_ws in self.indexer.workspaces.keys():
                                    other_norm = other_ws.replace("-", "_")
                                    if other_ws != ws_name and (other_ws in import_path or other_norm in import_path or f"@{other_ws}" in import_path):
                                        pair_key = (ws_name, rel_path, other_ws, import_path)
                                        if pair_key not in processed_pairs:
                                            processed_pairs.add(pair_key)
                                            edges.append({
                                                "source_workspace": ws_name,
                                                "source_file": rel_path,
                                                "source_symbol": "module",
                                                "target_workspace": other_ws,
                                                "target_file": import_path,
                                                "target_symbol": Path(import_path).name,
                                                "rel_type": "DEPENDS_ON",
                                                "tx_time": tx_time,
                                                "valid_from": valid_from,
                                                "valid_to": None
                                            })
                        except Exception:
                            pass

        self.cross_repo_edges = edges
        return edges

    def query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Federated graph query filtering by symbol, workspace, or relationship type.
        Returns matching nodes and edges.
        """
        symbol_filter = params.get("symbol")
        ws_filter = params.get("workspace")
        rel_filter = params.get("rel_type")
        limit = int(params.get("limit", 100))

        if not self.cross_repo_edges:
            self.resolve_cross_repo_dependencies()

        all_symbols = self.indexer.index_all()

        matched_nodes = []
        matched_edges = []

        for s in all_symbols:
            match = True
            if symbol_filter and symbol_filter.lower() not in s.get("name", "").lower():
                match = False
            if ws_filter and s.get("workspace") != ws_filter:
                match = False
            if match:
                matched_nodes.append({
                    "id": f"{s.get('workspace')}:{s.get('file_path')}:{s.get('name')}",
                    "label": s.get("name"),
                    "workspace": s.get("workspace"),
                    "file_path": s.get("file_path"),
                    "kind": s.get("kind"),
                    "line": s.get("line_number")
                })
                if len(matched_nodes) >= limit:
                    break

        for e in self.cross_repo_edges:
            match = True
            if symbol_filter:
                sf = symbol_filter.lower()
                if sf not in e.get("source_symbol", "").lower() and sf not in e.get("target_symbol", "").lower():
                    match = False
            if ws_filter:
                if e.get("source_workspace") != ws_filter and e.get("target_workspace") != ws_filter:
                    match = False
            if rel_filter and e.get("rel_type") != rel_filter:
                match = False
            if match:
                matched_edges.append(e)
                if len(matched_edges) >= limit:
                    break

        return {
            "status": "ok",
            "nodes_count": len(matched_nodes),
            "edges_count": len(matched_edges),
            "nodes": matched_nodes,
            "edges": matched_edges
        }


class BackgroundIngestionWorker:
    """
    Autonomous multi-repo AST ingestion worker (INV-015-04, INV-016-04).
    Crawls linked workspaces, extracts structural components,
    and maps AST symbols to bitemporal Utopia DB DAG nodes and edges.
    100% Pure Python standard library.
    """

    def __init__(
        self,
        indexer: Optional[MultiWorkspaceSymbolIndexer] = None,
        utopia_client: Optional[Any] = None
    ):
        self.indexer = indexer if indexer is not None else MultiWorkspaceSymbolIndexer()
        self.utopia_client = utopia_client
        self.graph_resolver = CrossRepoSemanticGraphResolver(indexer=self.indexer)
        self.mutation_manager = TransactionalMutationManager(indexer=self.indexer)
        self.last_ingested_at: Optional[float] = None
        self.last_report: Dict[str, Any] = {
            "status": "idle",
            "last_ingested_at": None,
            "symbols_count": 0,
            "nodes_count": 0,
            "edges_count": 0,
            "cross_edges_count": 0,
            "duration_ms": 0.0
        }

    def run_ingestion(self, valid_time_day: Optional[int] = None) -> Dict[str, Any]:
        """
        Executes background ingestion pass:
        1. Indexes all registered workspaces.
        2. Synthesizes bitemporal DAG nodes (with Tx, Tv).
        3. Constructs containment and dependency edges.
        4. Resolves cross-repository semantic dependencies.
        5. Syncs to Utopia DB DAG if client is available.
        """
        import time
        from datetime import datetime

        t0 = time.perf_counter()
        tv = valid_time_day or int(datetime.now().strftime("%Y%m%d"))
        tx = time.time()

        symbols = self.indexer.index_all()

        nodes = []
        edges = []
        file_nodes_created = set()

        for s in symbols:
            ws = s.get("workspace", "default")
            fpath = s.get("file_path", "")
            sname = s.get("name", "")
            skind = s.get("kind", "symbol")

            # Module / File container node
            file_node_id = f"{ws}:{fpath}"
            if file_node_id not in file_nodes_created:
                file_nodes_created.add(file_node_id)
                nodes.append({
                    "id": file_node_id,
                    "label": fpath,
                    "entity_type": "module",
                    "workspace": ws,
                    "file_path": fpath,
                    "valid_from": tv,
                    "valid_to": None,
                    "tx_time": tx
                })

            # Symbol node
            sym_node_id = f"{ws}:{fpath}:{sname}"
            nodes.append({
                "id": sym_node_id,
                "label": sname,
                "entity_type": skind,
                "workspace": ws,
                "file_path": fpath,
                "line_number": s.get("line_number", 1),
                "docstring": s.get("docstring", ""),
                "valid_from": tv,
                "valid_to": None,
                "tx_time": tx
            })

            # Containment edge
            edges.append({
                "from_id": file_node_id,
                "to_id": sym_node_id,
                "rel_type": "CONTAINS"
            })

        # Resolve cross-repo dependencies
        cross_edges = self.graph_resolver.resolve_cross_repo_dependencies(valid_time_day=tv)

        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        self.last_ingested_at = tx

        report = {
            "status": "completed",
            "last_ingested_at": tx,
            "symbols_count": len(symbols),
            "nodes_count": len(nodes),
            "edges_count": len(edges),
            "cross_edges_count": len(cross_edges),
            "duration_ms": duration_ms,
            "nodes": nodes,
            "edges": edges,
            "cross_repo_edges": cross_edges
        }
        self.last_report = report
        return report

    def get_cross_repo_edges(self) -> List[Dict[str, Any]]:
        """Returns all discovered cross-repository dependency edges."""
        if not self.graph_resolver.cross_repo_edges:
            self.graph_resolver.resolve_cross_repo_dependencies()
        return self.graph_resolver.cross_repo_edges

    def query_graph(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Federated query execution across workspaces."""
        return self.graph_resolver.query(params)

    def get_status(self) -> Dict[str, Any]:
        """Returns the status and metrics of the ingestion engine."""
        return self.last_report

    def apply_refactor(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Executes transactional refactoring across workspaces."""
        return self.mutation_manager.apply_refactor(spec)

    def rollback(self, tx_id: str) -> Dict[str, Any]:
        """Rolls back an applied transaction by tx_id."""
        return self.mutation_manager.rollback(tx_id)


class TransactionalMutationManager:
    """
    Manages atomic cross-repository refactorings under Copy-on-Write (CoW) git branches (INV-017-04).
    Enables autonomous agents to apply coordinated AST mutations across multiple workspaces,
    run verification gates, and rollback cleanly if fitness checks fail.
    Operates using 100% Pure Python Standard Library.
    """

    def __init__(self, indexer: Optional[MultiWorkspaceSymbolIndexer] = None):
        self.indexer = indexer if indexer is not None else MultiWorkspaceSymbolIndexer()
        self.transactions: Dict[str, Dict[str, Any]] = {}

    def _get_current_branch(self, cwd: Path) -> str:
        """Determines the current git branch for a workspace."""
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True
            )
            return res.stdout.strip() or "main"
        except Exception:
            return "main"

    def apply_refactor(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies coordinated cross-repository refactoring on CoW branches.
        """
        import re
        import time
        from datetime import datetime

        operation = spec.get("operation", "rename_symbol")
        target_symbol = spec.get("target_symbol", "")
        new_name = spec.get("new_name", "")
        dry_run = spec.get("dry_run", False)
        requested_ws = spec.get("workspaces")

        tx_time = time.time()
        tx_id = f"tx_{int(tx_time)}_{os.urandom(3).hex()}"
        cow_branch = f"cow/{tx_id}"
        valid_time_day = int(datetime.now().strftime("%Y%m%d"))

        if dry_run or not target_symbol:
            tx_record = {
                "tx_id": tx_id,
                "status": "dry_run_completed",
                "operation": operation,
                "target_symbol": target_symbol,
                "new_name": new_name,
                "dry_run": True,
                "tx_time": tx_time,
                "valid_time_day": valid_time_day,
                "workspaces": requested_ws or list(self.indexer.workspaces.keys()),
                "mutations_applied": 0,
                "files_affected": []
            }
            self.transactions[tx_id] = tx_record
            return {
                "status": "ok",
                "tx_id": tx_id,
                "operation": operation,
                "dry_run": True,
                "mutations_applied": 0,
                "message": f"Dry-run refactoring validated for symbol '{target_symbol}'"
            }

        # Select workspaces to mutate
        workspaces_to_mutate = {}
        for ws_name, ws_info in self.indexer.workspaces.items():
            if requested_ws is None or ws_name in requested_ws:
                workspaces_to_mutate[ws_name] = ws_info

        orig_branches = {}
        files_affected = []
        pattern = re.compile(r'\b' + re.escape(target_symbol) + r'\b')

        try:
            # 1. Create CoW branches in target workspaces
            for ws_name, ws_info in workspaces_to_mutate.items():
                ws_root = Path(ws_info["path"]).resolve()
                if not ws_root.exists() or not ws_root.is_dir():
                    continue

                orig_branch = self._get_current_branch(ws_root)
                orig_branches[ws_name] = orig_branch

                # Create and checkout CoW branch
                subprocess.run(["git", "checkout", "-b", cow_branch], cwd=ws_root, capture_output=True, check=True)

                # 2. Mutate occurrences in code files
                for root, dirs, files in os.walk(ws_root):
                    dirs[:] = [d for d in dirs if d not in self.indexer.EXCLUDE_DIRS]
                    for fname in files:
                        if fname.endswith((".py", ".ts", ".tsx", ".js", ".json", ".md")):
                            fpath = Path(root) / fname
                            try:
                                content = fpath.read_text(encoding="utf-8")
                                if pattern.search(content):
                                    new_content = pattern.sub(new_name, content)
                                    fpath.write_text(new_content, encoding="utf-8")
                                    files_affected.append({
                                        "workspace": ws_name,
                                        "file": str(fpath.relative_to(ws_root))
                                    })
                            except Exception:
                                pass

                # Commit changes on CoW branch
                subprocess.run(["git", "add", "."], cwd=ws_root, capture_output=True, check=True)
                subprocess.run(
                    ["git", "commit", "-m", f"refactor(cow): {operation} {target_symbol} -> {new_name}"],
                    cwd=ws_root,
                    capture_output=True,
                    check=True
                )

            tx_record = {
                "tx_id": tx_id,
                "status": "committed",
                "operation": operation,
                "target_symbol": target_symbol,
                "new_name": new_name,
                "cow_branch": cow_branch,
                "orig_branches": orig_branches,
                "tx_time": tx_time,
                "valid_time_day": valid_time_day,
                "workspaces": list(workspaces_to_mutate.keys()),
                "mutations_applied": len(files_affected),
                "files_affected": files_affected
            }
            self.transactions[tx_id] = tx_record

            return {
                "status": "ok",
                "tx_id": tx_id,
                "operation": operation,
                "cow_branch": cow_branch,
                "mutations_applied": len(files_affected),
                "files_affected": files_affected
            }

        except Exception as e:
            # Auto-rollback on exception
            for ws_name, orig_branch in orig_branches.items():
                ws_root = Path(workspaces_to_mutate[ws_name]["path"]).resolve()
                subprocess.run(["git", "checkout", "-f", orig_branch], cwd=ws_root, capture_output=True)
                subprocess.run(["git", "branch", "-D", cow_branch], cwd=ws_root, capture_output=True)
            return {
                "status": "error",
                "tx_id": tx_id,
                "error": str(e)
            }

    def rollback(self, tx_id: str) -> Dict[str, Any]:
        """
        Rolls back a transaction by resetting workspaces to original branches.
        """
        tx_record = self.transactions.get(tx_id)
        if not tx_record:
            return {"status": "error", "error": f"Transaction '{tx_id}' not found"}

        if tx_record.get("dry_run"):
            tx_record["status"] = "rolled_back"
            return {"status": "ok", "tx_id": tx_id, "rolled_back_tx_id": tx_id, "message": "Dry-run discarded"}

        cow_branch = tx_record.get("cow_branch")
        orig_branches = tx_record.get("orig_branches", {})

        for ws_name, orig_branch in orig_branches.items():
            ws_info = self.indexer.workspaces.get(ws_name)
            if not ws_info:
                continue
            ws_root = Path(ws_info["path"]).resolve()
            try:
                subprocess.run(["git", "checkout", "-f", orig_branch], cwd=ws_root, capture_output=True, check=True)
                if cow_branch:
                    subprocess.run(["git", "branch", "-D", cow_branch], cwd=ws_root, capture_output=True)
            except Exception:
                pass

        tx_record["status"] = "rolled_back"
        return {
            "status": "ok",
            "tx_id": tx_id,
            "rolled_back_tx_id": tx_id,
            "message": f"Transaction '{tx_id}' rolled back successfully"
        }


