---
name: b-sdd-sprint-closure
description: Autonomous skill for B-SDD discrete sprint closure, distillation (Phi_6 -> Phi_7), release tagging, active rules compilation (<500 words), dual codebase text dump synthesis (b-sdd_code_dump.txt and b-sdd-ui_code_dump.txt), Astryx Cockpit Cloudflare Pages publication, GitNexus AST re-indexing (.184), Utopia DB Tripartite sync and WORM ledger commitment (.251), NotebookLM source cleanup and upload, and supervisor callback notification.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [b-sdd, cloudflare-pages-expert, b-sdd-ui-export, b-sdd-notebooklm-sync]
---
# B-SDD Sprint Closure & Distillation Skill

The **B-SDD Sprint Closure Skill** enforces an end-to-end, automated discrete sprint closure and distillation protocol under the B-SDD framework. It governs the transition from Implementation ($\Phi_6$) to Distillation & Handoff ($\Phi_7$), ensuring absolute architectural integrity, context compaction, AST knowledge graph currency in GitNexus, frontend deployment to Cloudflare Pages, bitemporal Tripartite ontology and WORM ledger synchronization in Utopia DB, dual code dumps in Google NotebookLM, and telemetric callback to the orchestrating supervisor.

---

## 1. When to Use
- When all sprint implementation tasks, specifications, and test suites are 100% completed.
- At the formal sprint closure phase ($\Phi_6 \to \Phi_7$).
- When sealing release tags, compiling active rules into `.context/active_rules.md`, updating GitNexus AST graph, publishing the Astryx UI to Cloudflare Pages, and committing WORM audit snapshots into Utopia DB.

---

## 2. The Sprint Closure & Distillation Lifecycle

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        B-SDD SPRINT CLOSURE LIFECYCLE (Φ6 ──► Φ7)                      │
└────────────────────────────────────────────────────────────────────────────────────────┘
  [1. Cleaner]           python3 scripts/gitnexus_cleaner.py (cleans lbug.shadow on .184)
       │
  [2. GitNexus Sync]     docker exec gitnexus-server gitnexus analyze /projects/b-sdd (.184)
       │
  [3. Code Dumps]        dump_codebase.py (b-sdd_code_dump.txt) &
                         CALL_SKILL(b-sdd-ui-export): dump_ui_codebase.py (b-sdd-ui_code_dump.txt)
       │
  [3.5. Deploy UI]       CALL_SKILL(cloudflare-pages-expert): deploy_cloudflare_pages.sh
       │
  [4. Skills Dump]       python3 scripts/dump_skills.py & Immutability Barrier (ADR-015)
       │
  [5. NotebookLM Sync]   CALL_SKILL(b-sdd-notebooklm-sync): Updates dual code dumps in SSoT Notebook
       │
  [6. Rules Compile]     python3 -m src.cli.main compile (<500 words, ADR-005)
       │
  [7. Utopia DB Sync]    Tripartite (ADR + Spec + Skill) sync & WORM ledger commit on .251
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
```

### Stage 3: Dual Codebase Text Dumps Generation
1. **Backend Code Dump**:
   ```bash
   python3 scripts/dump_codebase.py --source . --output b-sdd_code_dump.txt
   ```
2. **Astryx Cockpit UI Code Dump (via `b-sdd-ui-export`)**:
   ```bash
   python3 scripts/dump_ui_codebase.py --source b-sdd-ui --output b-sdd-ui_code_dump.txt --sync-remote
   ```

### Stage 3.5: Astryx Cockpit Cloudflare Pages Production Deployment (via `cloudflare-pages-expert`)
Builds production bundle and publishes live to Cloudflare Pages:
```bash
bash scripts/deploy_cloudflare_pages.sh
# Verifies HTTP 200 at https://b-sdd-ui.pages.dev
```

### Stage 4: Active Skills Inventory & Immutability Barrier
Verifies that all core system skills remain intact and immutable per ADR-015, then refreshes `docs/skills_dump/ACTIVE_SKILLS_CATALOG.md`:
```bash
python3 scripts/dump_skills.py
```

### Stage 5: NotebookLM SSoT Dual Dumps Update (via `b-sdd-notebooklm-sync`)
Target Project Notebook: `205ee2ec-e0d2-4ba6-badf-44f2de02c7e2`.
Synchronizes both `b-sdd_code_dump.txt` and `b-sdd-ui_code_dump.txt` into Google NotebookLM via the MCP server on host `.184`.

### Stage 6: Rules Compilation & Budget Enforcement (ADR-005)
Recompiles active rules snapshot and verifies word budget:
```bash
python3 -m src.cli.main compile
test $(wc -w < .context/active_rules.md) -lt 500
```

### Stage 7: Utopia DB Tripartite Ontology Sync & WORM Ledger Commit (Host .251)
Synchronizes the 3-tier ontological model into Utopia DB (`192.168.3.251`) and records immutable commit in `intent_store.worm_ledger`.

### Stage 8: Discrete Sprint Handoff Synthesis (ADR-007)
Generates atomic handoff artifacts (`.context/sprint_handoff.json` and `.context/next_sprint.md`).

### Stage 9: Git Sealing & Release Tagging
```bash
git tag -a sprint_XXX_done -m "sprint_XXX: sealed and distilled"
git push origin main sprint_XXX_done
```

### Stage 10: Telemetric Callback to Supervisor Webhook
Dispatches POST payload to n8n supervisor webhook (`http://100.66.97.93:5678/webhook/bsdd-supervisor-result`).

---

## 3. Algorithmic Workflow (ADR-016 Standard)

```text
ALGORITHM ExecuteSprintClosure
INPUT:
    sprint_id: str
    prompt: str
    skip_gitnexus: bool = False
    skip_deploy: bool = False
    no_push: bool = False
OUTPUT:
    closure_status: str ("SEALED" | "FAILED")

BEGIN
    TRY
        // STAGE 1: Cleaner
        EXECUTE CleanGitNexusLocks()

        // STAGE 2: GitNexus Re-indexing
        IF NOT skip_gitnexus THEN
            EXECUTE ReindexGitNexusGraph(host="192.168.3.184")
        FI

        // STAGE 3: Dual Code Dumps
        EXECUTE SynthesizeBackendDump(output="b-sdd_code_dump.txt")
        CALL_SKILL(b-sdd-ui-export, {
            source: "b-sdd-ui",
            output: "b-sdd-ui_code_dump.txt",
            sync_remote: True
        })

        // STAGE 3.5: Cloudflare Pages Deployment
        IF NOT skip_deploy THEN
            CALL_SKILL(cloudflare-pages-expert, {action: "deploy", project: "b-sdd-ui"})
        FI

        // STAGE 4: Skills Inventory & Immutability Barrier
        ASSERT VerifySystemSkillsImmutability() == TRUE
        EXECUTE RefreshSkillsCatalog()

        // STAGE 5: NotebookLM SSoT Sync
        CALL_SKILL(b-sdd-notebooklm-sync, {
            notebook_id: "205ee2ec-e0d2-4ba6-badf-44f2de02c7e2",
            sources: ["b-sdd_code_dump.txt", "b-sdd-ui_code_dump.txt"]
        })

        // STAGE 6: Rules Compilation
        wc = EXECUTE CompileActiveRules()
        ASSERT wc < 500

        // STAGE 7: Utopia DB Tripartite Sync & WORM Ledger
        EXECUTE SyncUtopiaDBAndRecordWORM(sprint_id, wc)

        // STAGE 8: Handoff Synthesis
        EXECUTE SynthesizeHandoff(prompt)

        // STAGE 9: Git Sealing
        EXECUTE GitTagAndSeal(tag=sprint_id + "_done", push=NOT no_push)

        // STAGE 10: Supervisor Callback
        EXECUTE EmitSupervisorCallback(sprint_id, status="SEALED")

        RETURN "SEALED"
    CATCH Error AS e
        LOG_CRITICAL("Sprint closure failed: " + e.Message)
        HALT_AND_DEGRADE(e.Message)
    END
END
```

---

<!-- DRAKON_VISUAL_FLOW_START -->
## DRAKON Visual Workflow (Planar Skewer X=0)
- **Schema File:** `b-sdd-sprint-closure.drakon.json`
- **Total Algorithmic Nodes:** 13
- **Spine Topology:** Vertical Skewer ($X=0, C=0$) verified.
  1. `[HEADLINE]` Початок: Повний життєвий цикл закриття спринту B-SDD (Phi_6 -> Phi_7)
  2. `[ACTION]` Етап 1: Очищення блокувань GitNexus (gitnexus_cleaner.py)
  3. `[ACTION]` Етап 2: Переіндексація AST-графа коду в GitNexus на хості 192.168.3.184
  4. `[INSERTION]` CALL_SKILL(b-sdd-ui-export): Етап 3: Синтез подвійного текстового дампу (b-sdd_code_dump.txt та b-sdd-ui_code_dump.txt)
  5. `[INSERTION]` CALL_SKILL(cloudflare-pages-expert): Етап 3.5: Публікація Astryx Cockpit у Cloudflare Pages (b-sdd-ui.pages.dev)
  6. `[ACTION]` Етап 4: Інвентаризація активних скілів та верифікація незмінності ядра (ADR-015)
  7. `[INSERTION]` CALL_SKILL(b-sdd-notebooklm-sync): Етап 5: Оновлення джерел та дампу UI у записнику NotebookLM (ID: 205ee2ec...)
  8. `[ACTION]` Етап 6: Компіляція active_rules.md та бюджет <500 слів (ADR-005)
  9. `[ACTION]` Етап 7: Синхронізація трипартитної онтології та WORM-запис в Utopia DB (.251)
  10. `[ACTION]` Етап 8: Генерація дискретного Handoff артефакту (ADR-007)
  11. `[ACTION]` Етап 9: Фіксація Git Release Tag (sprint_XXX_done) та git push
  12. `[ACTION]` Етап 10: Телеметричний callback на супервайзер (n8n webhook)
  13. `[END]` Завершення: Спринт успішно закрито та запечатано (Phi_7 Distilled)
<!-- DRAKON_VISUAL_FLOW_END -->
