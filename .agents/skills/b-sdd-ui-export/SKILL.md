---
name: b-sdd-ui-export
description: Autonomous pipeline for synthesizing Gemini Spark-optimized structured plain-text dumps of Astryx Cockpit UI (b-sdd-ui), staging into working NotebookLM MCP directories on host .184, and synchronizing into the B-SDD Architecture SSoT notebook.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [b-sdd, notebooklm]
---

# B-SDD UI Export & NotebookLM Sync Skill

Autonomous system skill for synthesizing structured plain-text source code dumps of the **Astryx Cockpit** (`b-sdd-ui`), staging them into working NotebookLM MCP directories on host `192.168.3.184`, and synchronizing them directly into the Single Source of Truth (SSoT) Google NotebookLM project notebook: *"B-SDD Methodology, Multi-Session Handoff & Architecture"*.

---

## 1. Architectural Context & Negative Invariants

- **ADR-015 Compliance (Skill Taxonomy & Immutability)**:
  - This skill is a declared `SYSTEM_SKILL` with `immutable: true`.
  - It is protected against accidental deletion or mutation by the Astryx Cockpit UI and automated sprint scripts.
- **ADR-016 Compliance (Tripartite Standard)**:
  - Strict isomorphism between textual algorithmic pseudocode and `<skill_name>.drakon.json`.
  - Primary vertical skewer ($X=0, C=0$) represents the clean synthesis, staging, and MCP registration path.
  - Error and offline degradation paths branch strictly to the right ($X=4.0$).
- **ADR-002 Compliance (Pure Python Standard Library)**:
  - Synthesis scripts (`scripts/dump_ui_codebase.py`) rely exclusively on Python standard library modules (`pathlib`, `os`, `re`, `datetime`, `subprocess`, `argparse`).
- **Negative Invariants**:
  - **NEVER** include raw third-party vendor minified libraries (such as `drakonwidget.js`, `drakongen.js`) or binary images in the plain-text dump.
  - **NEVER** overwrite the SSoT backend dump (`b-sdd_code_dump.txt`) with the frontend dump; use distinct canonical naming: `b-sdd-ui_code_dump.txt`.
  - **NEVER** allow failure of external NotebookLM network synchronization to crash or roll back local code synthesis (graceful offline degradation to $X=4.0$).

---

## 2. Algorithmic Workflow (ADR-016 Standard)

```text
ALGORITHM ExportAndSyncAstryxUI
INPUT:
    ui_source_dir: Path = "b-sdd-ui"
    output_dump_file: Path = "b-sdd-ui_code_dump.txt"
    remote_host: str = "192.168.3.184"
    notebook_id: str = "205ee2ec-e0d2-4ba6-badf-44f2de02c7e2"
OUTPUT:
    sync_status: str ("SUCCESS" | "DEGRADED" | "FAILED")
    source_id: Optional[str]

BEGIN
    TRY
        ASSERT DirectoryExists(ui_source_dir)
        ASSERT FileExists(ui_source_dir / "src/lib/backend-types.ts")

        // STEP 1: Primary Vertical Skewer (X=0.0, Y=2.0)
        EXECUTE ValidateUIWorkspace(ui_source_dir)

        // STEP 2: Plain-Text Dump Synthesis for Gemini Spark (X=0.0, Y=4.0)
        dump_result = EXECUTE SynthesizeGeminiSparkDump(
            source=ui_source_dir,
            output=output_dump_file,
            layers=[
                "Contracts & Backend Types",
                "Realtime SSE & API Client",
                "DRAKON Engine & IR Bridge",
                "Application Shell & TopBar",
                "Cockpit Panels & Drawers",
                "Styling & Cloudflare Config"
            ]
        )

        // STEP 3: Verification Question (X=0.0, Y=6.0)
        IF dump_result.file_size > 0 AND dump_result.file_count > 0 THEN
            CONTINUE along Vertical Skewer (X=0.0)
        ELSE
            BRANCH_RIGHT(X=4.0, Y=6.0): Dump Synthesis Failure
            LOG_CRITICAL("Failed to synthesize UI code dump")
            HALT_AND_DEGRADE("DUMP_SYNTHESIS_FAILED")
        FI

        // STEP 4: Stage to Remote Host Working Directories (X=0.0, Y=8.0)
        EXECUTE StageToMCPDirectories(
            local_file=output_dump_file,
            remote_host=remote_host,
            destinations=[
                "/home/vokov/b-sdd-ui_code_dump.txt",
                "/home/vokov/notebooklm-agent-copilot/b-sdd-ui_code_dump.txt"
            ]
        )

        // STEP 5: Check MCP Server Availability (X=0.0, Y=10.0)
        mcp_online = EXECUTE ProbeMCPServer(host=remote_host, port=8002)

        // STEP 6: MCP Online Evaluation (X=0.0, Y=12.0)
        IF mcp_online == TRUE THEN
            CONTINUE along Vertical Skewer (X=0.0)
        ELSE
            BRANCH_RIGHT(X=4.0, Y=12.0): Offline MCP Degradation
            LOG_WARNING("NotebookLM MCP server unreachable; preserving staged files")
            RETURN Status="DEGRADED", SourceID=NULL
        FI

        // STEP 7: Call NotebookLM Skill to Ingest Source (X=0.0, Y=14.0)
        CALL_SKILL(notebooklm, {
            action: "sources_add_file",
            notebook_id: notebook_id,
            file_path: "/home/vokov/b-sdd-ui_code_dump.txt",
            mime_type: "text/plain"
        })

        // STEP 8: Verify Source Registration (X=0.0, Y=16.0)
        sources = EXECUTE ListSources(notebook_id=notebook_id)
        registered_source = FindSourceByTitle(sources, "b-sdd-ui_code_dump.txt")

        // STEP 9: Final Success Invariant (X=0.0, Y=18.0)
        IF registered_source != NULL THEN
            EMIT_TELEMETRY(status="SUCCESS", source_id=registered_source.id)
            RETURN Status="SUCCESS", SourceID=registered_source.id
        ELSE
            BRANCH_RIGHT(X=4.0, Y=18.0): Ingestion Verification Failed
            LOG_CRITICAL("Source not found in NotebookLM registry after upload")
            HALT_AND_DEGRADE("NOTEBOOKLM_REGISTRATION_FAILED")
        FI

    CATCH Error AS e
        LOG_CRITICAL("Unhandled error during UI export: " + e.Message)
        HALT_AND_DEGRADE(e.Message)
    END
END
```

---

## 3. Operational Guide & CLI Execution

### Command 1: Local Synthesis with Automatic Remote Staging
```bash
python3 /home/vokov/projects/b-sdd/scripts/dump_ui_codebase.py \
  --source /home/vokov/projects/b-sdd/b-sdd-ui \
  --output /home/vokov/projects/b-sdd/b-sdd-ui_code_dump.txt \
  --sync-remote
```

### Command 2: Fallback via Remote Aggregator (`run_md_service.sh` on .184)
```bash
ssh -o StrictHostKeyChecking=no vokov@192.168.3.184 \
  "/home/vokov/projects/resume/run_md_service.sh \
   --batch \
   --source /home/vokov/projects/b-sdd/b-sdd-ui \
   --output /home/vokov/b-sdd-ui_code_dump.txt"
```

### Command 3: Synchronize to Google NotebookLM
Using MCP or `notebooklm_mcp.py`:
```bash
python3 -c '
from src.core.drakon.skill_visual_bridge import *
# Ingestion via NotebookLM MCP tool
'
```

---

<!-- DRAKON_VISUAL_FLOW_START -->
## DRAKON Visual Workflow (Planar Skewer X=0)
- **Schema File:** `b-sdd-ui-export.drakon.json`
- **Total Algorithmic Nodes:** 14
- **Spine Topology:** Vertical Skewer ($X=0, C=0$) verified with degradation paths ($X=4.0$).
  1. `[HEADLINE]` Початок: Експорт коду Astryx UI в робочу директорію NotebookLM-MCP та синхронізація SSoT
  2. `[ACTION]` Крок 1: Валідація робочого простору b-sdd-ui та контракту бекенду (backend-types.ts)
  3. `[ACTION]` Крок 2: Синтез структурованого текстового дампу для Gemini Spark (scripts/dump_ui_codebase.py)
  4. `[QUESTION]` Крок 3: Дамп успішно згенеровано (розмір > 0)?
  5. `[ACTION]` Крок 4: Стейджинг дампу в робочу директорію NotebookLM-MCP на хості 192.168.3.184
  6. `[ACTION]` Крок 5: Перевірка доступності NotebookLM MCP сервера (порт 8002)
  7. `[QUESTION]` Крок 6: MCP сервер доступний?
  8. `[INSERTION]` CALL_SKILL(notebooklm): Крок 7: Синхронізація дампу в записник 'B-SDD Methodology, Multi-Session Handoff & Architecture'
  9. `[ACTION]` Крок 8: Верифікація джерела b-sdd-ui_code_dump.txt через sources_list
  10. `[QUESTION]` Крок 9: Джерело успішно додано/оновлено в NotebookLM?
  11. `[END]` Успішне завершення: Код інтерфейсу експортовано та зафіксовано в SSoT записнику
  12. `[ACTION]` Помилка синтезу дампу b-sdd-ui: логування та зупинка (X=4.0)
  13. `[ACTION]` Помилка зв'язку з MCP: збереження локального та віддаленого дампу без онлайн реєстрації (X=4.0)
  14. `[ACTION]` Помилка додавання джерела в NotebookLM: діагностика сесії (X=4.0)
<!-- DRAKON_VISUAL_FLOW_END -->
