"""
B-SDD (Bitemporal Spec-Driven Development) Core Compiler
Deterministic pre-flight compiler that parses ADRs, Specs, and Constitution
to generate high-density active rules (<500 words, <50ms) for AI agents.
Operates using 100% Pure Python Standard Library.
"""
import os
import re
import sys
import json
import time
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Any, Optional

DEFAULT_WORD_BUDGET = 500

DEFAULT_DOMAIN_SKILL_MAP = {
    "core": ["architecture-designer", "intent-continuity", "safe-refactor"],
    "api": ["api-designer", "intent-continuity", "safe-refactor"],
    "web": ["frontend-design", "make-interfaces-feel-better"],
    "backend": ["architecture-designer", "safe-refactor"],
    "database": ["intent-continuity", "safe-refactor"],
    "specs": ["writing-plans", "executing-plans"],
    "docs": ["code-documenter", "doc-indexer"],
    "security": ["security-reviewer", "defense-in-depth"],
    "global": ["skill-creator", "find-skills", "architecture-designer"]
}

DEFAULT_FILE_DOMAIN_RULES = [
    (re.compile(r"^src/core/"), "core"),
    (re.compile(r"^src/adapters/"), "core"),
    (re.compile(r"^src/api/|^api/"), "api"),
    (re.compile(r"^src/gateway/"), "core"),
    (re.compile(r"^web/|^frontend/|^ui/|styles\.css|\.html$"), "web"),
    (re.compile(r"^specs/"), "specs"),
    (re.compile(r"^docs/"), "docs"),
]


class BSDDCompiler:
    """Universal B-SDD Pre-Flight Intent & Capability Compiler."""

    def __init__(self, root_dir: Optional[Path] = None, output_path: Optional[Path] = None):
        self.root_dir = (root_dir or Path.cwd()).resolve()
        self.output_path = (output_path or (self.root_dir / ".context" / "active_rules.md")).resolve()
        self.context_dir = self.root_dir / ".context"
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.context_dir / "intents_cache.sqlite"
        self.config = self._load_config()
        self._cache_mtime: float = 0.0
        self._intents_cache: Optional[List[Dict[str, Any]]] = None
        self._compiled_cache: Dict[str, str] = {}
        self._init_cache_db()

    def _load_config(self) -> Dict[str, Any]:
        """Loads optional b_sdd.config.json or returns default settings."""
        cfg_path = self.root_dir / "b_sdd.config.json"
        if cfg_path.exists():
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "project_name": self.root_dir.name,
            "word_budget": DEFAULT_WORD_BUDGET,
            "domain_skill_map": DEFAULT_DOMAIN_SKILL_MAP
        }

    def _init_cache_db(self):
        """Initializes SQLite local intent and supersession cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS local_intents (
                id TEXT PRIMARY KEY,
                source_file TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                component TEXT NOT NULL,
                status TEXT NOT NULL,
                title TEXT,
                invariants_json TEXT,
                supersedes_json TEXT,
                updated_at REAL NOT NULL
            );
            """)
            conn.commit()

    @staticmethod
    def _compute_hash(content: str) -> str:
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def parse_adr_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parses MADR / Nygard ADR Markdown file extracting invariants and supersession."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return None

        file_hash = self._compute_hash(content)
        m = re.search(r"(ADR-\d+|\b\d{4}-[\w-]+)", file_path.name, re.IGNORECASE)
        doc_id = m.group(1).upper() if m else file_path.stem.upper()

        title_m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_m.group(1).strip() if title_m else doc_id

        # Status & Supersedes detection
        status = "ACTIVE"
        supersedes: List[str] = []
        for line in content.splitlines():
            line_str = line.strip()
            if re.search(r"\bStatus:\s*superseded\b", line_str, re.IGNORECASE) or line_str.startswith("* Status: Superseded"):
                status = "SUPERSEDED"
            sup_m = re.search(r"(?:Supersedes|Replaces):\s*(.*)", line_str, re.IGNORECASE)
            if sup_m:
                sup_text = sup_m.group(1)
                found = re.findall(r"(ADR-\d+|\b\d{4}\b)", sup_text, re.IGNORECASE)
                for f in found:
                    supersedes.append(f.upper())

        # Invariants extraction
        invariants: List[str] = []
        inv_sec = re.search(r"##\s+(?:Invariants|Architecture Invariants|Rules|Constraints)(.*?)(?:\n##|\Z)", content, re.DOTALL | re.IGNORECASE)
        if inv_sec:
            raw_inv = inv_sec.group(1)
            for line in raw_inv.splitlines():
                line = line.strip()
                if line.startswith("- ") or line.startswith("* ") or re.match(r"^\d+\.\s+", line):
                    cleaned = re.sub(r"^[-*\d\.]+\s+", "", line).strip()
                    if cleaned and not cleaned.lower().startswith("none"):
                        invariants.append(cleaned)

        # Fallback to decision consequences if invariants not explicitly structured
        if not invariants:
            cons_sec = re.search(r"###?\s+(?:Consequences|Decision Outcome)(.*?)(?:\n##|\Z)", content, re.DOTALL | re.IGNORECASE)
            if cons_sec:
                for line in cons_sec.group(1).splitlines():
                    line = line.strip()
                    if line.startswith("- ") or line.startswith("* "):
                        cleaned = re.sub(r"^[-*]\s+", "", line).strip()
                        if len(cleaned) > 20:
                            invariants.append(cleaned)

        # Domain / Component detection
        comp_m = re.search(r"(?:Component|Domain):\s*`?([\w-]+)`?", content, re.IGNORECASE)
        component = comp_m.group(1).lower() if comp_m else "core"

        return {
            "id": doc_id,
            "source_file": str(file_path.relative_to(self.root_dir)),
            "file_hash": file_hash,
            "component": component,
            "status": status,
            "title": title,
            "invariants": invariants,
            "supersedes": supersedes
        }

    def parse_spec_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parses SDD spec.md or plan.md file."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return None

        file_hash = self._compute_hash(content)
        spec_id = file_path.parent.name
        title_m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_m.group(1).strip() if title_m else f"Spec {spec_id}"

        invariants: List[str] = []
        inv_sec = re.search(r"##\s+(?:Invariants|System Invariants|Requirements|Constraints)(.*?)(?:\n##|\Z)", content, re.DOTALL | re.IGNORECASE)
        if inv_sec:
            for line in inv_sec.group(1).splitlines():
                line = line.strip()
                if line.startswith("- ") or line.startswith("* ") or re.match(r"^\d+\.\s+", line):
                    cleaned = re.sub(r"^[-*\d\.]+\s+", "", line).strip()
                    if cleaned:
                        invariants.append(cleaned)

        return {
            "id": f"SPEC-{spec_id}",
            "source_file": str(file_path.relative_to(self.root_dir)),
            "file_hash": file_hash,
            "component": spec_id,
            "status": "ACTIVE",
            "title": title,
            "invariants": invariants,
            "supersedes": []
        }

    def parse_constitution(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parses .specify/constitution.md for system principles & invariants."""
        if not file_path.exists():
            return []
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return []

        file_hash = self._compute_hash(content)
        invariants: List[str] = []
        for line in content.splitlines():
            line_str = line.strip()
            if line_str.startswith("- ") or line_str.startswith("* ") or re.match(r"^\d+\.\s+", line_str):
                cleaned = re.sub(r"^[-*\d\.]+\s+", "", line_str).strip()
                if len(cleaned) > 15:
                    invariants.append(cleaned)

        if invariants:
            return [{
                "id": "CONST-001",
                "source_file": str(file_path.relative_to(self.root_dir)),
                "file_hash": file_hash,
                "component": "global",
                "status": "ACTIVE",
                "title": "System Constitution & Fundamental Principles",
                "invariants": invariants,
                "supersedes": []
            }]
        return []

    def _get_latest_mtime(self) -> float:
        """Returns the latest modification time of any intent source file."""
        max_m = 0.0
        const_path = self.root_dir / ".specify" / "constitution.md"
        if const_path.exists():
            max_m = max(max_m, const_path.stat().st_mtime)

        adr_dir = self.root_dir / "docs" / "adr"
        if adr_dir.exists():
            for f in adr_dir.glob("*.md"):
                max_m = max(max_m, f.stat().st_mtime)

        specs_dir = self.root_dir / "specs"
        if specs_dir.exists():
            for f in specs_dir.glob("**/spec.md"):
                max_m = max(max_m, f.stat().st_mtime)

        return max_m

    def scan_and_sync_intents(self) -> List[Dict[str, Any]]:
        """Scans filesystem for ADRs, Specs, and Constitution, caching in SQLite."""
        latest_mtime = self._get_latest_mtime()
        if self._intents_cache is not None and latest_mtime <= self._cache_mtime:
            return self._intents_cache

        all_intents: List[Dict[str, Any]] = []

        # 1. Constitution
        const_path = self.root_dir / ".specify" / "constitution.md"
        all_intents.extend(self.parse_constitution(const_path))

        # 2. ADRs
        adr_dir = self.root_dir / "docs" / "adr"
        if adr_dir.exists():
            for f in sorted(adr_dir.glob("*.md")):
                parsed = self.parse_adr_file(f)
                if parsed:
                    all_intents.append(parsed)

        # 3. Specs
        specs_dir = self.root_dir / "specs"
        if specs_dir.exists():
            for spec_f in sorted(specs_dir.glob("**/spec.md")):
                parsed = self.parse_spec_file(spec_f)
                if parsed:
                    all_intents.append(parsed)

        # Compute DAG supersessions locally
        superseded_ids: Set[str] = set()
        for it in all_intents:
            if it["status"] == "SUPERSEDED":
                superseded_ids.add(it["id"])
            for sup in it.get("supersedes", []):
                superseded_ids.add(sup)

        # Update SQLite cache only if needed
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            for it in all_intents:
                final_status = "SUPERSEDED" if it["id"] in superseded_ids else it["status"]
                it["status"] = final_status
                conn.execute("""
                INSERT INTO local_intents (id, source_file, file_hash, component, status, title, invariants_json, supersedes_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    source_file=excluded.source_file,
                    file_hash=excluded.file_hash,
                    component=excluded.component,
                    status=excluded.status,
                    title=excluded.title,
                    invariants_json=excluded.invariants_json,
                    supersedes_json=excluded.supersedes_json,
                    updated_at=excluded.updated_at
                """, (
                    it["id"],
                    it["source_file"],
                    it["file_hash"],
                    it["component"],
                    final_status,
                    it.get("title", ""),
                    json.dumps(it.get("invariants", [])),
                    json.dumps(it.get("supersedes", [])),
                    now
                ))
            conn.commit()

        self._intents_cache = all_intents
        self._cache_mtime = latest_mtime
        return all_intents

    def resolve_domains_from_files(self, changed_files: List[str]) -> Set[str]:
        """Resolves target components/domains from list of changed files."""
        domains: Set[str] = set()
        for file_path in changed_files:
            file_clean = file_path.strip().replace("\\", "/")
            matched = False
            for pattern, dom in DEFAULT_FILE_DOMAIN_RULES:
                if pattern.search(file_clean):
                    domains.add(dom)
                    matched = True
            if not matched:
                domains.add("core")
        return domains if domains else {"core"}

    def compile(self, target_files: Optional[List[str]] = None, target_domains: Optional[Set[str]] = None) -> str:
        """
        Compiles active rules snapshot conforming strictly to <500 words budget.
        Returns the compiled Markdown content.
        """
        t0 = time.perf_counter()
        intents = self.scan_and_sync_intents()

        active_domains: Set[str] = set()
        if target_domains:
            active_domains.update(target_domains)
        elif target_files:
            active_domains.update(self.resolve_domains_from_files(target_files))

        # Filter for active intents only (superseded are mathematically excluded)
        active_intents = [it for it in intents if it["status"] == "ACTIVE"]

        # If domain filter is active, prioritize matching domains, always keep 'global'
        if active_domains:
            primary = [it for it in active_intents if it["component"] in active_domains or it["component"] == "global"]
            secondary = [it for it in active_intents if it not in primary]
            ordered_intents = primary + secondary
        else:
            ordered_intents = active_intents

        # Build snapshot content
        project_title = self.config.get("project_name", "B-SDD Project")
        domain_label = ", ".join(sorted(active_domains)) if active_domains else "all components"

        header_lines = [
            f"# Active Architectural Invariants ({project_title})",
            f"<!-- Auto-compiled by B-SDD Compiler for domains: {domain_label} -->",
            "MANDATORY INVARIANTS:"
        ]

        rule_lines: List[str] = []
        budget = self.config.get("word_budget", DEFAULT_WORD_BUDGET)
        current_words = sum(len(h.split()) for h in header_lines)
        truncated = False

        for it in ordered_intents:
            comp_tag = f"[{it['component'].upper()}]"
            for inv in it.get("invariants", []):
                rule = f"- {comp_tag} {inv} (Ref: {it['source_file']})"
                rule_words = len(rule.split())
                if current_words + rule_words > (budget - 50):  # reserve 50 words for skills
                    truncated = True
                    break
                rule_lines.append(rule)
                current_words += rule_words
            if truncated:
                break

        if truncated:
            rule_lines.append("<!-- truncated: active rules exceeded word limit, lowest priority rules dropped -->")

        # Procedural Skills recommendations
        skill_map = self.config.get("domain_skill_map", DEFAULT_DOMAIN_SKILL_MAP)
        rec_skills: Set[str] = set()
        if active_domains:
            for dom in active_domains:
                for s in skill_map.get(dom, []):
                    rec_skills.add(s)
        else:
            for s in skill_map.get("core", []) + skill_map.get("global", []):
                rec_skills.add(s)

        rec_skills.add("b-sdd")

        skill_lines = [
            "",
            "RECOMMENDED PROCEDURAL SKILLS:",
            f"- Active Skills: {', '.join(sorted(rec_skills))}",
            "- Skill Guidance: Use 'find-skills' if capability missing, or 'skill-creator' if process repeats >=2 times."
        ]

        final_content = "\n".join(header_lines + rule_lines + skill_lines) + "\n"
        self.output_path.write_text(final_content, encoding="utf-8")

        elapsed_ms = (time.perf_counter() - t0) * 1000
        return final_content


def main():
    import argparse
    parser = argparse.ArgumentParser(description="B-SDD Deterministic Pre-Flight Compiler")
    parser.add_argument("--files", nargs="*", help="List of changed files to resolve domains")
    parser.add_argument("--domains", nargs="*", help="Target domains to compile rules for")
    parser.add_argument("--output", help="Custom output path for compiled rules snapshot")
    args = parser.parse_args()

    root = Path.cwd()
    out = Path(args.output).resolve() if args.output else None
    compiler = BSDDCompiler(root_dir=root, output_path=out)

    t_start = time.perf_counter()
    res = compiler.compile(
        target_files=args.files,
        target_domains=set(args.domains) if args.domains else None
    )
    duration_ms = (time.perf_counter() - t_start) * 1000

    word_count = len(res.split())
    print(res)
    print(f"B-SDD compiled snapshot ({word_count} words) in {duration_ms:.2f} ms -> {compiler.output_path}")


if __name__ == "__main__":
    main()
