"""
B-SDD (Bitemporal Spec-Driven Development) GitNexus Graph Adapter
Reads .gitnexus/index.sqlite in read-only mode and performs upstream-impact resolution.
Falls back to deterministic path-based domain extraction on missing index or sqlite3.Error.
Operates using 100% Pure Python Standard Library.
"""
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

