"""
B-SDD (Bitemporal Spec-Driven Development) Universal CLI
Command line interface for compiling architectural rules, syncing bitemporal intents,
running fitness tests, and scaffolding new specifications and ADRs.
Operates using 100% Pure Python Standard Library.
"""
import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from src.core.compiler import BSDDCompiler
from src.adapters.utopia_db import UtopiaDBAdapter
from src.core.session_distiller import SessionDistiller


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

    print(f"✓ Utopia DB Tripartite Synchronization Complete:")
    print(f"  - Ingested Intents : {intent_res.get('registered', 0)} / {intent_res.get('total', 0)}")
    print(f"  - Supersessions    : {intent_res.get('supersessions', 0)}")
    print(f"  - Tripartite Entities: {kg_res.get('entities', 0)} ({kg_res.get('adrs', 0)} ADRs, {kg_res.get('specs', 0)} Specs, {kg_res.get('skills', 0)} Skills)")
    print(f"  - Knowledge Facts  : {kg_res.get('facts', 0)}")

    if getattr(args, "sprint", None):
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        rules_path = Path.cwd() / ".context" / "active_rules.md"
        rules_wc = len(rules_path.read_text(encoding="utf-8").split()) if rules_path.exists() else 0
        worm_id = adapter.record_worm_ledger(
            sprint_id=args.sprint,
            commit_hash=commit,
            release_tag=f"{args.sprint}_done",
            phase="PHI_7_DISTILLED",
            active_rules_word_count=rules_wc,
            tripartite_summary=kg_res
        )
        print(f"  - WORM Ledger Rec  : {worm_id}")


def cmd_fitness(args):
    """Executes automated architectural fitness tests."""
    print("Running B-SDD architectural fitness tests (pytest)...")
    res = subprocess.run(["pytest", "-v", "tests/test_architecture_fitness.py"])
    sys.exit(res.returncode)


def cmd_distill(args):
    """Distills long-running session transcript into compact B-SDD intelligence."""
    distiller = SessionDistiller()
    session_id = args.session or os.environ.get("AGY_CONVERSATION_ID") or distiller.get_latest_conversation_id()
    if not session_id:
        print("❌ Error: --session argument, AGY_CONVERSATION_ID environment variable, or active transcript required.")
        sys.exit(1)

    print(f"Distilling agent session '{session_id}'...")
    try:
        data = distiller.distill_agy_session(session_id)
    except Exception as e:
        print(f"❌ Error during distillation: {e}")
        sys.exit(1)

    md_content = distiller.render_distilled_markdown(data)

    out_path = Path(args.output).resolve() if args.output else Path.cwd() / ".context" / "session_distillation.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md_content, encoding="utf-8")

    if args.json:
        json_path = Path(args.json).resolve() if isinstance(args.json, str) and args.json != "True" else out_path.with_suffix(".json")
        json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"✓ Saved raw JSON metrics to {json_path}")

    words = len(md_content.split())
    print(f"✓ Session distillation complete: {data['total_steps']} steps -> {out_path} ({words} words)")


def cmd_handoff(args):
    """Synthesizes Sprint-to-Sprint handoff payload and next sprint dispatch command."""
    distiller = SessionDistiller()
    session_id = args.session or os.environ.get("AGY_CONVERSATION_ID") or distiller.get_latest_conversation_id()
    enforce_fitness = not args.skip_fitness

    out_json = Path(args.output_json).resolve() if args.output_json else None
    out_md = Path(args.output_md).resolve() if args.output_md else None
    spec_path = Path(args.spec).resolve() if args.spec else None

    print("Synthesizing Sprint Handoff (ADR-007)...")
    try:
        payload = distiller.generate_handoff(
            conversation_id=session_id,
            next_prompt=args.prompt,
            spec_path=spec_path,
            enforce_fitness=enforce_fitness,
            output_json=out_json,
            output_md=out_md
        )
    except Exception as e:
        print(f"❌ Handoff failed: {e}")
        sys.exit(1)

    json_target = out_json or (Path.cwd() / ".context" / "sprint_handoff.json")
    md_target = out_md or (Path.cwd() / ".context" / "next_sprint.md")

    print("✓ Handoff generated successfully:")
    print(f"  - Handoff ID     : {payload['handoff_id']}")
    print(f"  - Fitness Gate   : {'PASSED' if payload['fitness']['passed'] else 'FAILED'}")
    print(f"  - Completed Tasks: {len(payload['completed_tasks'])}")
    print(f"  - Pending Tasks  : {len(payload['pending_tasks'])}")
    print(f"  - Modified Seams : {len(payload['modified_files'])} files")
    print(f"  - Machine Schema : {json_target.relative_to(Path.cwd()) if json_target.is_relative_to(Path.cwd()) else json_target}")
    print(f"  - Human Briefing : {md_target.relative_to(Path.cwd()) if md_target.is_relative_to(Path.cwd()) else md_target}")
    print(f"\n▶ Next Sprint Dispatch Command:")
    print(f"  {payload['next_sprint']['run_command']}\n")


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


def cmd_drakon(args):
    """Handles DRAKON diagram parsing, validation, and prompt generation (ADR-008)."""
    from src.drakon import DrakonParser, DrakonValidator

    if not getattr(args, "file", None):
        print("❌ Missing required argument: file")
        sys.exit(1)

    file_path = Path(args.file).resolve()
    if not file_path.exists():
        print(f"❌ DRAKON file not found: {file_path}")
        sys.exit(1)

    try:
        schema = DrakonParser.parse_file(file_path)
    except Exception as exc:
        print(f"❌ Failed to parse DRAKON file: {exc}")
        sys.exit(1)

    if args.drakon_command == "parse":
        print(DrakonParser.to_ir_json(schema))
    elif args.drakon_command == "prompt":
        print(DrakonParser.generate_prompt_constraints(schema))
    elif args.drakon_command == "validate":
        validator = DrakonValidator()
        result = validator.validate(schema)
        if result.is_valid:
            print(f"✓ DRAKON schema '{schema.name}' is topologically and bitemporally VALID.")
            print(f"  - Nodes verified    : {result.stats.get('node_count', 0)}")
            print(f"  - Invariant bindings: {result.stats.get('verified_invariants', 0)}")
            if result.warnings:
                print(f"  - Warnings ({len(result.warnings)}):")
                for w in result.warnings:
                    print(f"    * [{w.rule}] {w.message}")
        else:
            print(f"❌ DRAKON schema '{schema.name}' validation FAILED ({len(result.errors)} errors):")
            for e in result.errors:
                node_str = f" (node: {e.node_id})" if e.node_id else ""
                print(f"  - [{e.rule}]{node_str}: {e.message}")
            sys.exit(1)
    else:
        print("Usage: python3 -m src.cli.main drakon [validate|parse|prompt] <file>")


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
    p_sync.add_argument("--sprint", help="Sprint ID to record in immutable WORM ledger")

    # fitness
    subparsers.add_parser("fitness", help="Run architectural fitness tests")

    # distill
    p_dist = subparsers.add_parser("distill", help="Distill session transcript into compact B-SDD intelligence")
    p_dist.add_argument("--session", help="Session / conversation ID (defaults to AGY_CONVERSATION_ID)")
    p_dist.add_argument("--output", help="Output markdown path (default: .context/session_distillation.md)")
    p_dist.add_argument("--json", nargs="?", const="True", help="Save raw structured JSON metrics")

    # handoff
    p_handoff = subparsers.add_parser("handoff", help="Synthesize Sprint N -> N+1 handoff artifacts (ADR-007)")
    p_handoff.add_argument("--session", help="Current session ID (defaults to AGY_CONVERSATION_ID)")
    p_handoff.add_argument("--prompt", help="Explicit prompt or task description for next sprint")
    p_handoff.add_argument("--spec", help="Path to spec tasks.md file or spec folder")
    p_handoff.add_argument("--output-json", help="Custom output path for sprint_handoff.json")
    p_handoff.add_argument("--output-md", help="Custom output path for next_sprint.md")
    p_handoff.add_argument("--skip-fitness", action="store_true", help="Skip upstream architecture fitness gate check")

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
    # drakon
    p_drakon = subparsers.add_parser("drakon", help="DRAKON algorithmic diagram commands (ADR-008)")
    drakon_sub = p_drakon.add_subparsers(dest="drakon_command")

    p_drk_val = drakon_sub.add_parser("validate", help="Validate DRAKON diagram invariants")
    p_drk_val.add_argument("file", help="Path to DRAKON diagram file (.json or .drn)")

    p_drk_parse = drakon_sub.add_parser("parse", help="Parse and output canonical DRAKON-IR")
    p_drk_parse.add_argument("file", help="Path to DRAKON diagram file (.json or .drn)")

    p_drk_prompt = drakon_sub.add_parser("prompt", help="Generate prompt constraints from DRAKON diagram")
    p_drk_prompt.add_argument("file", help="Path to DRAKON diagram file (.json or .drn)")

    # serve
    p_serve = subparsers.add_parser("serve", help="Start local B-SDD workbench server & bridge gateway (ADR-008)")
    p_serve.add_argument("--port", type=int, default=8765, help="Port to listen on (default: 8765)")
    p_serve.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")

    args = parser.parse_args()
    if args.command == "compile":
        cmd_compile(args)
    elif args.command == "serve":
        from src.server.workbench_server import WorkbenchServer
        WorkbenchServer(host=args.host, port=args.port).start()
    elif args.command == "sync":
        cmd_sync(args)
    elif args.command == "fitness":
        cmd_fitness(args)
    elif args.command == "distill":
        cmd_distill(args)
    elif args.command == "handoff":
        cmd_handoff(args)
    elif args.command == "drakon":
        cmd_drakon(args)
    elif args.command == "init":
        cmd_init(args)
    elif args.command == "adr" and getattr(args, "adr_command", None) == "new":
        cmd_new_adr(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
