"""
B-SDD (Bitemporal Spec-Driven Development) Safety & Verification Gateway
Inspects text responses for mentions of superseded architectural contracts
and appends warnings redirecting to active replacement rules.
Operates using 100% Pure Python Standard Library.
"""
import re
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional, Union


class BSDDSafetyGateway:
    """Gateway for verifying retrieved LLM / NotebookLM texts against active architectural intents."""

    def __init__(self, db_cache_path: Optional[Union[str, Path]] = None):
        if db_cache_path:
            p = Path(db_cache_path)
            if p.is_dir():
                self.cache_path = p / ".context" / "intents_cache.sqlite"
            else:
                self.cache_path = p
        else:
            self.cache_path = Path.cwd() / ".context" / "intents_cache.sqlite"

    def _get_supersession_map(self) -> Dict[str, str]:
        """Builds old_id -> new_id map from supersedes column of active records."""
        supersession_map: Dict[str, str] = {}
        if not self.cache_path.exists():
            return supersession_map

        try:
            uri = f"file:{self.cache_path.resolve().as_posix()}?mode=ro"
            conn = sqlite3.connect(uri, uri=True, timeout=1.0)
            cursor = conn.cursor()

            # Check table name
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('local_intents', 'intents');")
            tables = [row[0] for row in cursor.fetchall()]
            if not tables:
                conn.close()
                return supersession_map

            tbl = "local_intents" if "local_intents" in tables else "intents"
            sup_col = "supersedes_json" if tbl == "local_intents" else "supersedes"

            cursor.execute(f"""
                SELECT id, {sup_col}
                FROM {tbl}
                WHERE {sup_col} IS NOT NULL AND {sup_col} != '[]'
            """)
            rows = cursor.fetchall()
            conn.close()

            for new_id, sup_str in rows:
                try:
                    sup_list = json.loads(sup_str)
                except Exception:
                    sup_list = [s.strip() for s in sup_str.strip("[]").split(",") if s.strip()]

                for old_id in sup_list:
                    if old_id:
                        supersession_map[old_id] = new_id
                        stem = Path(old_id).stem
                        supersession_map[stem] = new_id
        except Exception:
            pass

        return supersession_map

    def verify(self, response_text: str) -> str:
        """
        Verifies response_text against superseded contracts.
        If an old_id is detected with whole-word boundaries, appends an architectural
        deviation warning referencing the superseding new_id.
        """
        if not response_text:
            return ""

        sup_map = self._get_supersession_map()
        if not sup_map:
            return response_text

        violations: List[str] = []
        for old_id, new_id in sorted(sup_map.items()):
            pattern = rf"\b{re.escape(old_id)}\b"
            if re.search(pattern, response_text, re.IGNORECASE):
                violations.append(f"- '{old_id}' is SUPERSEDED by '{new_id}'. Use active mandate.")

        if violations:
            warning_block = [
                "",
                "<!-- WARNING: SUPERSEDED ARCHITECTURAL CONTRACTS DETECTED -->",
                "⚠️ [B-SDD Intent Warning] The response references superseded architectural contracts:",
                *violations,
                "Please verify active constraints in .context/active_rules.md before proceeding."
            ]
            return response_text + "\n" + "\n".join(warning_block)

        return response_text

    def inspect_and_filter(self, query_result_text: str) -> Dict[str, Any]:
        """Convenience method returning structured status and sanitized payload."""
        verified = self.verify(query_result_text)
        is_valid = (verified == query_result_text)
        return {
            "valid": is_valid,
            "original": query_result_text,
            "verified": verified,
            "warning": None if is_valid else "Response references superseded architectural contracts."
        }
