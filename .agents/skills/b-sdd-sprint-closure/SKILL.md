---
name: b-sdd-sprint-closure
description: Autonomous skill for B-SDD discrete sprint closure, distillation (Phi_6 -> Phi_7), release tagging, active rules compilation (<500 words), codebase text dump synthesis (b-sdd_code_dump.txt), GitNexus AST re-indexing (.184), Utopia DB Tripartite sync and WORM ledger commitment (.251), NotebookLM source cleanup and upload, and supervisor callback notification.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [b-sdd]
---
# B-SDD Sprint Closure & Distillation Skill

The **B-SDD Sprint Closure Skill** enforces an end-to-end, automated 10-stage protocol for finalizing discrete sprints under the B-SDD framework. It governs the transition from Implementation ($\Phi_6$) to Distillation & Handoff ($\Phi_7$), ensuring absolute architectural integrity, context compaction, AST knowledge graph currency in GitNexus, bitemporal Tripartite ontology and WORM ledger synchronization in Utopia DB, and telemetric callback to the orchestrating supervisor.

---

## 1. When to Use
- When all sprint implementation tasks, specifications, and test suites are 100% completed.
- At the formal sprint closure phase ($\Phi_6 \to \Phi_7$).
- When sealing release tags, compiling active rules into `.context/active_rules.md`, updating GitNexus AST graph, and committing WORM audit snapshots into Utopia DB.

---

## 2. The 10-Stage Discrete Sprint Closure Protocol

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        B-SDD SPRINT CLOSURE LIFECYCLE (Φ6 ──► Φ7)                      │
└────────────────────────────────────────────────────────────────────────────────────────┘
  [1. Cleaner]           python3 scripts/gitnexus_cleaner.py (cleans lbug.shadow on .184)
       │
  [2. GitNexus Sync]     docker exec gitnexus-server gitnexus analyze /projects/b-sdd (.184)
       │
  [3. Code Dump]         python3 scripts/dump_codebase.py (b-sdd_code_dump.txt)
       │
  [4. Skills Dump]       python3 scripts/dump_skills.py (ACTIVE_SKILLS_CATALOG.md)
       │
  [5. NotebookLM Sync]   Rotates codebase dump in Notebook 205ee2ec-e0d2-4ba6-badf-44f2de02c7e2
       │
  [6. Utopia DB Sync]    Tripartite (ADR + Spec + Skill) sync & WORM ledger commit on .251
       │
  [7. Rules Compile]     python3 -m src.cli.main compile (<500 words, ADR-005)
       │
  [8. Handoff]           ./run_b_sdd.sh --handoff --prompt "<Next Sprint Directive>" (ADR-007)
       │
  [9. Git Sealing]       git tag -a sprint_XXX_done & git push origin main sprint_XXX_done
       │
  [10. Callback]         POST http://100.66.97.93:5678/webhook/bsdd-supervisor-result
```

### Stage 1: GitNexus Lock & Shadow Cleaner
Removes orphaned locks and shadow files (`lbug.shadow`, `lbug.wal.checkpoint`, `*.lock`) locally and on remote AST host `192.168.3.184`:
```bash
python3 scripts/gitnexus_cleaner.py
```

### Stage 2: GitNexus AST Code Intelligence Graph Re-indexing (Host .184)
Triggers full AST re-indexing inside the `gitnexus-server` container on host `192.168.3.184`:
```bash
ssh -o StrictHostKeyChecking=no vokov@192.168.3.184 "docker exec -t gitnexus-server gitnexus analyze /projects/b-sdd"
# Verify health
curl -s http://192.168.3.184:4747/api/health
```

### Stage 3: Codebase Text Dump Generation (`b-sdd_code_dump.txt`)
Synthesizes a unified Plain Text dump of the repository (code only, no binaries/caches/markdown):
```bash
python3 scripts/dump_codebase.py --source . --output b-sdd_code_dump.txt
```

### Stage 4: Active Skills Inventory Dump
Refreshes `docs/skills_dump/ACTIVE_SKILLS_CATALOG.md` and root `SKILLS_INVENTORY_DUMP.md`:
```bash
python3 scripts/dump_skills.py
```

### Stage 5: NotebookLM SSoT Pruning & Synchronization
Target Project Notebook: `205ee2ec-e0d2-4ba6-badf-44f2de02c7e2`.
1. Prune stale code dump (`sources_delete`).
2. Prune transient test step reports and duplicate documents.
3. Upload new `b-sdd_code_dump.txt` (`sources_add_file` with `mime_type="text/plain"`).

### Stage 6: Utopia DB Tripartite Ontology Sync & WORM Ledger Commit (Host .251)
Synchronizes the 3-tier ontological model into Utopia DB (`192.168.3.251`):
1. **SPEC/ADR Layer:** All active ADRs (`ADR-001`..`ADR-014`, `ADR-FE-001`) with bitemporal coordinates $(T_v, T_t)$.
2. **DATA Layer:** Functional specifications (`SPEC-001`..`SPEC-020`) and system constitution (`CONST-001`).
3. **SKILL Layer:** All 55 active skills in `~/.agents/skills/`.
4. **WORM Ledger Record:** Writes immutable record into `intent_store.worm_ledger` with commit hash, release tag, phase, word count, and GitNexus metadata.
```bash
python3 scripts/sync_utopia.py
```

### Stage 7: Rules Compilation & Budget Enforcement (ADR-005)
Recompiles active rules snapshot and verifies word budget:
```bash
python3 -m src.cli.main compile
# Strictly < 500 words
test $(wc -w < .context/active_rules.md) -lt 500
```

### Stage 8: Discrete Sprint Handoff Synthesis (ADR-007)
Generates the atomic handoff artifact, updating `.context/sprint_handoff.json` and `.context/next_sprint.md`:
```bash
./run_b_sdd.sh --handoff --prompt "Prepare Sprint <XXX+1>: <Next Sprint Title>"
```

### Stage 9: Git Sealing & Release Tagging
Tags the exact commit and pushes to origin:
```bash
git tag -f -a sprint_<XXX>_done -m "sprint_<XXX>: sealed and distilled"
git push origin main -f sprint_<XXX>_done
```

### Stage 10: Telemetric Callback Dispatch
Emits completion signal to n8n supervisor webhook:
```bash
curl -s -X POST http://100.66.97.93:5678/webhook/bsdd-supervisor-result \
  -H "Content-Type: application/json" \
  -d '{
    "sprint_id": "sprint_<XXX>",
    "status": "SEALED",
    "phase": "PHI_7_DISTILLED",
    "commit": "'$(git rev-parse HEAD)'",
    "tag": "sprint_<XXX>_done",
    "rules_word_count": '$(wc -w < .context/active_rules.md)',
    "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"
  }'
```

---

## 3. Automated Execution

To execute the entire 10-stage lifecycle autonomously:
```bash
python3 scripts/b_sdd_sprint_closure.py --sprint sprint_<XXX> --prompt "<Next Sprint Directive>"
```
Or via the skill runner:
```bash
~/.agents/skills/b-sdd-sprint-closure/scripts/sprint_closure.py --sprint sprint_<XXX> --prompt "<Next Sprint Directive>"
```

---

## 4. Architectural Invariants
- **INV-CLOSURE-01:** Never close a sprint without a 100% passing test suite (`pytest tests/`).
- **INV-CLOSURE-02:** Active rules snapshot in `.context/active_rules.md` must never exceed 500 words (ADR-005).
- **INV-CLOSURE-03:** AST graph on host 184 must be re-indexed to match the exact sealed commit hash.
- **INV-CLOSURE-04:** Utopia DB on host 251 must record an immutable WORM ledger snapshot for the sprint.
- **INV-CLOSURE-05:** Zero external pip dependencies in core runtime or closure scripts (ADR-002 Pure Stdlib).

<!-- DRAKON_VISUAL_FLOW_START -->
## DRAKON Visual Workflow (Planar Skewer X=0)
- **Schema File:** `b-sdd-sprint-closure.drakon.json`
- **Total Algorithmic Nodes:** 10
- **Spine Topology:** Vertical Skewer ($X=0, C=0$) verified.
  1. `[HEADLINE]` Початок: b-sdd-sprint-closure
  2. `[ACTION]` When to Use
  3. `[INSERTION]` CALL_SKILL(b-sdd): The 10-Stage Discrete Sprint Closure Protocol
  4. `[ACTION]` Stage 1: GitNexus Lock & Shadow Cleaner
  5. `[INSERTION]` CALL_SKILL(b-sdd): Stage 2: GitNexus AST Code Intelligence Graph Re-indexing (H
  6. `[INSERTION]` CALL_SKILL(b-sdd): Stage 3: Codebase Text Dump Generation (`b-sdd_code_dump.txt
  7. `[ACTION]` Stage 4: Active Skills Inventory Dump
  8. `[INSERTION]` CALL_SKILL(b-sdd): Stage 5: NotebookLM SSoT Pruning & Synchronization
  9. `[ACTION]` Stage 6: Utopia DB Tripartite Ontology Sync & WORM Ledger Co
  10. `[END]` Завершення: b-sdd-sprint-closure
<!-- DRAKON_VISUAL_FLOW_END -->
