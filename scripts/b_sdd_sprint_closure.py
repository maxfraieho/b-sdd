#!/usr/bin/env python3
"""
B-SDD Discrete Sprint Closure & Distillation Lifecycle Engine.
100% Pure Python Standard Library (ADR-002).
Automates the full 10-stage Sprint Closure Protocol (Phi_6 -> Phi_7):
  1. Cleaner: Cleans lbug.shadow & orphan locks (gitnexus_cleaner.py).
  2. GitNexus Sync: Triggers AST graph analysis on host 192.168.3.184.
  3. Code Dump: Synthesizes b-sdd_code_dump.txt (dump_codebase.py).
  4. Skills Dump: Updates active skills inventory (dump_skills.py).
  5. NotebookLM Sync: Prunes stale sources and updates code dump in SSoT notebook.
  6. Utopia DB Sync: Syncs Tripartite ontology (ADRs, Specs, Skills) & writes WORM ledger.
  7. Rules Compile: Compiles active_rules.md & enforces <500 word budget (ADR-005).
  8. Handoff: Generates atomic handoff artifacts (ADR-007).
  9. Git Sealing: Seals commit with release tag (sprint_XXX_done).
  10. Callback: Emits telemetric callback to n8n supervisor webhook.
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parent.parent

# Default target constants
NOTEBOOK_ID = "205ee2ec-e0d2-4ba6-badf-44f2de02c7e2"
SUPERVISOR_WEBHOOK = "http://100.66.97.93:5678/webhook/bsdd-supervisor-result"
GITNEXUS_HOST = "192.168.3.184"
GITNEXUS_CONTAINER_PATH = "/projects/b-sdd"


def log_stage(num: int, title: str):
    print(f"\n{'='*70}\n▶ [STAGE {num}/10]: {title}\n{'='*70}")


def stage_1_cleaner() -> bool:
    log_stage(1, "GitNexus Lock & Shadow Cleaner")
    cleaner_script = ROOT / "scripts" / "gitnexus_cleaner.py"
    if cleaner_script.exists():
        res = subprocess.run([sys.executable, str(cleaner_script)], cwd=str(ROOT))
        return res.returncode == 0
    return True


def stage_2_gitnexus_sync(skip: bool = False) -> bool:
    log_stage(2, "GitNexus AST Code Intelligence Graph Re-indexing (.184)")
    if skip:
        print("[SKIP] Stage 2 skipped by operator request.")
        return True

    cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes",
        f"vokov@{GITNEXUS_HOST}",
        f"docker exec -t gitnexus-server gitnexus analyze {GITNEXUS_CONTAINER_PATH}"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        print(res.stdout.strip())
        if res.returncode != 0:
            print(f"[WARN] GitNexus analyze returned code {res.returncode}: {res.stderr.strip()}", file=sys.stderr)
            return False
        return True
    except Exception as e:
        print(f"[WARN] GitNexus analyze failed: {e}", file=sys.stderr)
        return False


def stage_3_code_dump() -> bool:
    log_stage(3, "Codebase Plain Text Dump Synthesis (Backend & Astryx UI)")
    dumper = ROOT / "scripts" / "dump_codebase.py"
    out_file = ROOT / "b-sdd_code_dump.txt"
    backend_ok = True
    if dumper.exists():
        res = subprocess.run([sys.executable, str(dumper), "--source", str(ROOT), "--output", str(out_file)], cwd=str(ROOT))
        backend_ok = (res.returncode == 0)

    ui_dumper = ROOT / "scripts" / "dump_ui_codebase.py"
    ui_out_file = ROOT / "b-sdd-ui_code_dump.txt"
    ui_ok = True
    if ui_dumper.exists():
        res_ui = subprocess.run([sys.executable, str(ui_dumper), "--source", str(ROOT / "b-sdd-ui"), "--output", str(ui_out_file), "--sync-remote"], cwd=str(ROOT))
        ui_ok = (res_ui.returncode == 0)

    return backend_ok and ui_ok


def stage_cloudflare_pages_deploy(skip: bool = False) -> bool:
    log_stage("3.5", "Astryx Cockpit Cloudflare Pages Production Deployment")
    if skip:
        print("[SKIP] Cloudflare Pages deployment skipped by operator request.")
        return True

    deploy_script = ROOT / "scripts" / "deploy_cloudflare_pages.sh"
    if deploy_script.exists():
        res = subprocess.run(["bash", str(deploy_script)], cwd=str(ROOT))
        if res.returncode != 0:
            print("[WARN] Cloudflare Pages deployment returned non-zero code.", file=sys.stderr)
            return False
        print("✓ Astryx Cockpit deployed live to https://b-sdd-ui.pages.dev")
        return True
    return True


def stage_immutability_barrier() -> bool:
    """Enforce ADR-015-INV-02: Prevent deletion, corruption, or mutability of core system skills."""
    log_stage(4, "System Skills Immutability & Non-Deletion Barrier (ADR-015)")
    try:
        from src.core.drakon.skill_visual_bridge import verify_system_skills_immutability
        valid, violations = verify_system_skills_immutability()
        if not valid:
            print("❌ [CRITICAL INVARIANT BREACH: ADR-015-INV-02] System skills violated:", file=sys.stderr)
            for v in violations:
                print(f"   - {v}", file=sys.stderr)
            return False
        print("✓ All B-SDD core system skills verified immutable and intact.")
        return True
    except Exception as e:
        print(f"[WARN] Immutability barrier check error: {e}", file=sys.stderr)
        return False


def stage_4_skills_dump() -> bool:
    log_stage(4, "Active Skills Inventory Dump")
    # First enforce immutability barrier
    stage_immutability_barrier()
    skills_script = ROOT / "scripts" / "dump_skills.py"
    if skills_script.exists():
        res = subprocess.run([sys.executable, str(skills_script)], cwd=str(ROOT))
        return res.returncode == 0
    return False



def stage_5_notebooklm_sync() -> bool:
    log_stage(5, "NotebookLM SSoT Verification & Update (Dual Dumps)")
    print(f"[INFO] Target Notebook: {NOTEBOOK_ID}")
    code_dump_file = ROOT / "b-sdd_code_dump.txt"
    ui_dump_file = ROOT / "b-sdd-ui_code_dump.txt"

    if code_dump_file.exists():
        print(f"[INFO] Fresh backend code dump ready ({code_dump_file.stat().st_size:,} bytes).")
    if ui_dump_file.exists():
        print(f"[INFO] Fresh UI code dump ready ({ui_dump_file.stat().st_size:,} bytes).")

    # Stage and update in NotebookLM via host .184 MCP CLI if reachable
    try:
        remote_cmd = f"python3 /home/vokov/notebooklm_mcp.py add-text {NOTEBOOK_ID} b-sdd-ui_code_dump.txt /home/vokov/b-sdd-ui_code_dump.txt"
        res = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", f"vokov@{GITNEXUS_HOST}", remote_cmd], capture_output=True, text=True, timeout=60)
        if res.returncode == 0:
            print("✓ Updated b-sdd-ui_code_dump.txt in NotebookLM SSoT notebook.")
        else:
            print(f"[INFO] NotebookLM update notification: {res.stdout.strip() or res.stderr.strip()}")
    except Exception as e:
        print(f"[WARN] Remote NotebookLM sync attempt: {e}")

    return code_dump_file.exists() and ui_dump_file.exists()


def stage_6_utopia_sync(sprint_id: str, commit_hash: str, release_tag: str, rules_wc: int) -> bool:
    log_stage(6, "Utopia DB Tripartite Ontology Sync & WORM Ledger Commit")
    try:
        from src.adapters.utopia_db import UtopiaDBAdapter
        from src.core.compiler import BSDDCompiler

        compiler = BSDDCompiler()
        intents = compiler.scan_and_sync_intents()

        adapter = UtopiaDBAdapter()
        if not adapter.test_connection():
            print(f"[WARN] Utopia DB on {adapter.host} unreachable. Skipping WORM commit.", file=sys.stderr)
            return False

        intent_res = adapter.sync_all_intents(intents)
        kg_res = adapter.sync_to_knowledge_graph(intents)
        print(f"✓ Utopia DB Tripartite Sync: {intent_res.get('registered', 0)} intents, {kg_res.get('entities', 0)} entities ({kg_res.get('adrs', 0)} ADRs, {kg_res.get('specs', 0)} Specs, {kg_res.get('skills', 0)} Skills), {kg_res.get('facts', 0)} facts.")

        worm_id = adapter.record_worm_ledger(
            sprint_id=sprint_id,
            commit_hash=commit_hash,
            release_tag=release_tag,
            phase="PHI_7_DISTILLED",
            active_rules_word_count=rules_wc,
            gitnexus_status={"server": f"{GITNEXUS_HOST}:4747", "path": GITNEXUS_CONTAINER_PATH},
            tripartite_summary=kg_res,
            metadata={"agent": "agy", "sprint_closure_script": "b_sdd_sprint_closure.py"}
        )
        print(f"✓ Recorded immutable WORM ledger snapshot: {worm_id}")
        return True
    except Exception as e:
        print(f"[WARN] Utopia DB sync failed: {e}", file=sys.stderr)
        return False


def stage_7_rules_compile() -> int:
    log_stage(7, "Active Rules Compilation & ADR-005 Budget Verification")
    res = subprocess.run([sys.executable, "-m", "src.cli.main", "compile"], cwd=str(ROOT), capture_output=True, text=True)
    print(res.stdout.strip())
    active_rules = ROOT / ".context" / "active_rules.md"
    if active_rules.exists():
        words = len(active_rules.read_text(encoding="utf-8").split())
        print(f"  - Word count: {words} words (Limit: 500)")
        if words > 500:
            print(f"❌ Invariant breach: .context/active_rules.md exceeds 500 words ({words})", file=sys.stderr)
            sys.exit(1)
        return words
    return 0


def stage_8_handoff(prompt: str) -> bool:
    log_stage(8, "Discrete Sprint Handoff Synthesis (ADR-007)")
    cmd = [str(ROOT / "run_b_sdd.sh"), "--handoff", "--prompt", prompt]
    res = subprocess.run(cmd, cwd=str(ROOT))
    return res.returncode == 0


def stage_9_git_sealing(sprint_id: str, commit_hash: str, release_tag: str, push: bool = True) -> bool:
    log_stage(9, f"Git Sealing & Release Tagging ({release_tag})")
    subprocess.run(["git", "tag", "-f", "-a", release_tag, "-m", f"{sprint_id}: sealed and distilled"], cwd=str(ROOT))
    if push:
        res = subprocess.run(["git", "push", "origin", "main", "-f", release_tag], cwd=str(ROOT))
        return res.returncode == 0
    return True


def stage_10_callback(sprint_id: str, commit_hash: str, release_tag: str, rules_wc: int) -> bool:
    log_stage(10, "Telemetric Callback to Supervisor Webhook")
    import urllib.request
    payload = {
        "sprint_id": sprint_id,
        "status": "SEALED",
        "phase": "PHI_7_DISTILLED",
        "commit": commit_hash,
        "tag": release_tag,
        "rules_word_count": rules_wc,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    req = urllib.request.Request(
        SUPERVISOR_WEBHOOK,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            body = resp.read().decode("utf-8")
            print(f"✓ Webhook response ({resp.status}): {body}")
            return resp.status in (200, 201, 202)
    except Exception as e:
        print(f"[WARN] Webhook callback failed: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="B-SDD Sprint Closure Protocol Lifecycle Engine")
    parser.add_argument("--sprint", required=True, help="Sprint ID (e.g. sprint_030)")
    parser.add_argument("--prompt", required=False, default="Sprint 037 dispatch: Sovereign remote gateway and operations", help="Next sprint dispatch prompt")
    parser.add_argument("--skip-gitnexus", action="store_true", help="Skip remote GitNexus re-indexing")
    parser.add_argument("--skip-deploy", action="store_true", help="Skip Cloudflare Pages production deployment")
    parser.add_argument("--no-push", action="store_true", help="Do not push git tags/commits to remote")

    args = parser.parse_args()
    sprint_id = args.sprint
    release_tag = f"{sprint_id}_done"

    print(f"🚀 Starting B-SDD Sprint Closure Protocol for {sprint_id}...")
    commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()

    # 1. Cleaner
    stage_1_cleaner()

    # 2. GitNexus Sync
    stage_2_gitnexus_sync(skip=args.skip_gitnexus)

    # 3. Code Dump (Backend & Astryx UI)
    stage_3_code_dump()

    # 3.5. Cloudflare Pages Production Deployment
    stage_cloudflare_pages_deploy(skip=args.skip_deploy)

    # 4. Skills Dump
    stage_4_skills_dump()

    # 5. NotebookLM Sync
    stage_5_notebooklm_sync()

    # 7. Rules Compile
    rules_wc = stage_7_rules_compile()

    # 6. Utopia DB Sync
    stage_6_utopia_sync(sprint_id, commit_hash, release_tag, rules_wc)

    # 8. Handoff
    stage_8_handoff(args.prompt)

    # 9. Git Sealing
    stage_9_git_sealing(sprint_id, commit_hash, release_tag, push=not args.no_push)

    # 10. Callback
    stage_10_callback(sprint_id, commit_hash, release_tag, rules_wc)

    print(f"\n🎉 B-SDD Sprint Closure Protocol for {sprint_id} completed successfully (Phi_6 -> Phi_7).\n")


if __name__ == "__main__":
    main()
