"""
B-SDD (Bitemporal Spec-Driven Development) Universal CLI
Command line interface for compiling architectural rules, syncing bitemporal intents,
running fitness tests, and scaffolding new specifications and ADRs.
Operates using 100% Pure Python Standard Library.
"""
import sys
import argparse
import subprocess
from pathlib import Path
from src.core.compiler import BSDDCompiler
from src.adapters.utopia_db import UtopiaDBAdapter


def cmd_compile(args):
    """Compiles active rules snapshot."""
    compiler = BSDDCompiler(
        output_path=Path(args.output).resolve() if args.output else None
    )
    res = compiler.compile(
        target_files=args.files,
        target_domains=set(args.domains) if args.domains else None
    )
    words = len(res.split())
    print(f"✓ B-SDD active rules compiled successfully ({words} words) -> {compiler.output_path}")


def cmd_sync(args):
    """Synchronizes active intents and graph entities to Utopia DB."""
    compiler = BSDDCompiler()
    intents = compiler.scan_and_sync_intents()
    kb_id = args.kb or compiler.config.get("utopia_kb_id", "01a08474-0000-7000-8000-000000000001")

    adapter = UtopiaDBAdapter(kb_id=kb_id)
    if not adapter.test_connection():
        print(f"❌ Failed to connect to Utopia DB on {adapter.host}:{adapter.ssh_port}")
        sys.exit(1)

    print(f"Connecting to Utopia DB on host {adapter.host} (KB: {kb_id})...")

    # Ingest into intent_store in a single transaction
    intent_res = adapter.sync_all_intents(intents)

    # Sync to Knowledge Graph
    kg_res = adapter.sync_to_knowledge_graph(intents)

    print(f"✓ Utopia DB Synchronization Complete:")
    print(f"  - Ingested Intents : {intent_res.get('registered', 0)} / {intent_res.get('total', 0)}")
    print(f"  - Supersessions    : {intent_res.get('supersessions', 0)}")
    print(f"  - KG Entities      : {kg_res.get('entities', 0)}")
    print(f"  - KG Facts         : {kg_res.get('facts', 0)}")


def cmd_fitness(args):
    """Executes automated architectural fitness tests."""
    print("Running B-SDD architectural fitness tests (pytest)...")
    res = subprocess.run(["pytest", "-v", "tests/test_architecture_fitness.py"])
    sys.exit(res.returncode)


def cmd_init(args):
    """Initializes B-SDD structure in current working directory."""
    root = Path.cwd()
    dirs = [
        root / ".specify",
        root / ".context",
        root / "docs" / "adr",
        root / "specs",
        root / "templates"
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    const_file = root / ".specify" / "constitution.md"
    if not const_file.exists():
        const_file.write_text("""# Project Constitution (.specify/constitution.md)

## 1. System Principles
1. **Spec-Driven Consistency:** All implementations must conform to specifications in specs/.
2. **Architecture Continuity:** Decisions are recorded as ADRs with explicit supersession.
3. **Procedural Skills Lifecycle (Rule of 2):** Any workflow repeated >= 2 times must be crystallized into an autonomous agent skill.

## Invariants
- Zero unverified architecture drift.
- Pre-flight compiled active rules must strictly remain under 500 words.
- Operational workflows repeated >= 2 times must be crystallized via skill-creator.
""", encoding="utf-8")

    print(f"✓ Initialized B-SDD workspace in {root}")


def cmd_new_adr(args):
    """Generates a new ADR file."""
    adr_dir = Path.cwd() / "docs" / "adr"
    adr_dir.mkdir(parents=True, exist_ok=True)

    existing = list(adr_dir.glob("ADR-*.md")) + list(adr_dir.glob("????-*.md"))
    next_num = len(existing) + 1
    adr_id = f"ADR-{next_num:03d}"
    filename = f"{adr_id}-{args.title.lower().replace(' ', '-')}.md"
    target = adr_dir / filename

    content = f"""# {adr_id}: {args.title}

* **Status:** Accepted
* **Date:** {subprocess.getoutput('date -I')}
* **Component:** {args.component or 'core'}
* **Supersedes:** {args.supersedes or 'None'}

## Context and Problem Statement
Describe the technical context and architectural problem being addressed.

## Decision Drivers
* Driver 1
* Driver 2

## Considered Options
* Option 1
* Option 2

## Decision Outcome
Chosen option and rationale.

## Invariants
- Mandatory invariant 1 for this decision.
- Mandatory invariant 2 for this decision.
"""
    target.write_text(content, encoding="utf-8")
    print(f"✓ Created new ADR: {target.relative_to(Path.cwd())}")


def main():
    parser = argparse.ArgumentParser(description="B-SDD Framework CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # compile
    p_comp = subparsers.add_parser("compile", help="Compile active rules snapshot")
    p_comp.add_argument("--files", nargs="*", help="Changed files")
    p_comp.add_argument("--domains", nargs="*", help="Target domains")
    p_comp.add_argument("--output", help="Output file")

    # sync
    p_sync = subparsers.add_parser("sync", help="Sync active intents to Utopia DB")
    p_sync.add_argument("--kb", help="Custom Utopia Knowledge Base UUID")

    # fitness
    subparsers.add_parser("fitness", help="Run architectural fitness tests")

    # init
    p_init = subparsers.add_parser("init", help="Initialize B-SDD in repo")
    p_init.add_argument("--name", help="Project name")

    # adr
    p_adr = subparsers.add_parser("adr", help="ADR commands")
    adr_sub = p_adr.add_subparsers(dest="adr_command")
    p_adr_new = adr_sub.add_parser("new", help="Create new ADR")
    p_adr_new.add_argument("title", help="ADR title")
    p_adr_new.add_argument("--component", default="core", help="Target component")
    p_adr_new.add_argument("--supersedes", default="None", help="Superseded ADR ID")

    args = parser.parse_args()
    if args.command == "compile":
        cmd_compile(args)
    elif args.command == "sync":
        cmd_sync(args)
    elif args.command == "fitness":
        cmd_fitness(args)
    elif args.command == "init":
        cmd_init(args)
    elif args.command == "adr" and getattr(args, "adr_command", None) == "new":
        cmd_new_adr(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
