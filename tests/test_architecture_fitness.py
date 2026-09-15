"""
B-SDD (Bitemporal Spec-Driven Development) Architecture Fitness Test Suite.
Validates the 5 foundational fitness invariants of the B-SDD framework:
1. Compilation latency < 50ms (warm cache).
2. Prompt context density <= 500 words.
3. Pure Python Standard Library in src/ (zero external runtime dependencies).
4. Mathematical pruning of superseded architectural decisions.
5. Procedural skill recommendation and routing integrity.
"""
import ast
import sys
import time
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.core.compiler import BSDDCompiler


def test_compile_latency_sub_50ms():
    """Invariant: Pre-flight compilation must execute in under 50ms warm cache."""
    compiler = BSDDCompiler(root_dir=ROOT)
    # Warm up cache
    compiler.compile()

    # Measure warm execution
    latencies = []
    for _ in range(5):
        t0 = time.perf_counter()
        compiler.compile()
        latencies.append((time.perf_counter() - t0) * 1000)

    avg_ms = sum(latencies) / len(latencies)
    assert avg_ms < 50.0, f"Compilation latency exceeded 50ms: {avg_ms:.2f} ms"


def test_context_budget_sub_500_words():
    """Invariant: Compiled active rules snapshot must strictly remain under 500 words."""
    compiler = BSDDCompiler(root_dir=ROOT)
    snapshot = compiler.compile()
    words = len(snapshot.split())
    assert words <= 500, f"Active rules snapshot exceeded 500 words budget: {words} words"


def test_zero_third_party_dependencies_in_src():
    """Invariant: All core modules in src/ must strictly use Python standard library."""
    src_dir = ROOT / "src"
    stdlib_modules = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else {
        "os", "sys", "re", "json", "time", "sqlite3", "hashlib", "pathlib", "typing",
        "subprocess", "logging", "datetime", "uuid", "argparse", "unittest", "shutil",
        "tempfile", "functools", "itertools", "collections", "abc", "contextlib"
    }
    # Internal project package names allowed
    internal_pkgs = {"src"}

    for py_file in src_dir.rglob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(py_file))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split(".")[0]
                    assert root_mod in stdlib_modules or root_mod in internal_pkgs, (
                        f"External third-party import '{alias.name}' detected in {py_file.name}"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_mod = node.module.split(".")[0]
                    assert root_mod in stdlib_modules or root_mod in internal_pkgs, (
                        f"External third-party from-import '{node.module}' detected in {py_file.name}"
                    )


def test_supersession_dag_mathematical_pruning(tmp_path):
    """Invariant: Decisions marked as superseded must be mathematically purged from active rules."""
    test_adr_dir = tmp_path / "docs" / "adr"
    test_adr_dir.mkdir(parents=True)

    # ADR-001: Original rule
    adr1 = test_adr_dir / "ADR-001-original.md"
    adr1.write_text("""# ADR-001: Original Rule
* Status: Accepted
## Invariants
- OLD_MANDATE_ALPHA: Must use legacy synchronous socket protocol.
""", encoding="utf-8")

    # ADR-002: Superseding rule
    adr2 = test_adr_dir / "ADR-002-replacement.md"
    adr2.write_text("""# ADR-002: Replacement Rule
* Status: Accepted
* Supersedes: ADR-001
## Invariants
- NEW_MANDATE_BETA: Must use modern asynchronous WebSocket protocol.
""", encoding="utf-8")

    compiler = BSDDCompiler(root_dir=tmp_path)
    snapshot = compiler.compile()

    assert "NEW_MANDATE_BETA" in snapshot
    assert "OLD_MANDATE_ALPHA" not in snapshot, "Superseded invariant was not mathematically purged!"


def test_procedural_skill_recommendation_present():
    """Invariant: Compiled snapshot must contain RECOMMENDED PROCEDURAL SKILLS block."""
    compiler = BSDDCompiler(root_dir=ROOT)
    snapshot = compiler.compile()

    assert "RECOMMENDED PROCEDURAL SKILLS:" in snapshot
    assert "Active Skills:" in snapshot
    assert "b-sdd" in snapshot
