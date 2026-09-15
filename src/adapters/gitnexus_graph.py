"""
B-SDD (Bitemporal Spec-Driven Development) GitNexus Graph Adapter
Reads .gitnexus/index.sqlite in read-only mode and performs upstream-impact resolution.
Falls back to deterministic path-based domain extraction on missing index or sqlite3.Error.
Operates using 100% Pure Python Standard Library.
"""
import sqlite3
from pathlib import Path
from typing import Set, Iterable


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
