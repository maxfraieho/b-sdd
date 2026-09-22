---
name: b-sdd-ui-export
description: Автономний конвеєр синтезу структурованого дампа вебінтерфейсу Astryx Cockpit UI (b-sdd-ui) та його синхронізація в SSoT блокнот NotebookLM.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [b-sdd, notebooklm]
---

# B-SDD UI Export
Системний скіл проєкту B-SDD для експорту кодової бази фронтенду Astryx Cockpit (
b-sdd-ui
) у єдиний структурований текстовий дамп (
b-sdd-ui_code_dump.txt
). Забезпечує фільтрацію службових файлів, стейджинг артефакту на вузол агрегації 
.184
 та оновлення джерела знань у Google NotebookLM.

--------------------------------------------------------------------------------

1. Architectural Context & Negative Invariants
ADR Compliance
: ADR-015 (системний скіл), ADR-016 (стандарт псевдокоду), ADR-009 (Astryx UI).
Negative Invariants
:
NEVER
 включати у дамп папки 
node_modules
, 
.git
, 
dist
, 
.vite
, 
coverage
.
NEVER
 експортувати незбірочний або зламаний стан UI (обов'язкова перевірка 
npm run build
 або lint).
NEVER
 порушувати формат делімітерів файлів всередині згенерованого 
.txt
 дампа.

--------------------------------------------------------------------------------

2. Algorithmic Workflow (ADR-016 Standard)
ALGORITHM ExecuteBSddUiExport
INPUT:
    ui_source_dir: str ("/home/vokov/projects/b-sdd/b-sdd-ui")
    target_host: str ("192.168.3.184")
OUTPUT:
    status: str ("SUCCESS" | "FAILED" | "DEGRADED")
    dump_path: str

BEGIN
    TRY
        ASSERT ui_source_dir != ""

        // STEP 1: Sub-skill composition - Check B-SDD Environment (X=0.0, Y=2.0)
        CALL_SKILL(b-sdd, {action: "verify_ui_workspace"})

        // STEP 2: Main vertical spine - Aggregate Frontend Code (X=0.0, Y=4.0)
        EXECUTE RunUiCodeAggregation(ui_source_dir, output="/home/vokov/b-sdd-ui_code_dump.txt")

        // STEP 3: Question Node - Dump Integrity Check (X=0.0, Y=6.0)
        IF VerifyDumpIntegrity("/home/vokov/b-sdd-ui_code_dump.txt") THEN
            CONTINUE along Vertical Skewer (X=0.0)
        ELSE
            BRANCH_RIGHT(X=4.0, Y=6.0): Failure/Degradation
            LOG_ERROR("b-sdd-ui code dump generation failed or resulted in empty file")
            HALT_AND_DEGRADE("EMPTY_UI_DUMP")
        FI

        // STEP 4: Main vertical spine - Stage Dump to Aggregator Host (X=0.0, Y=8.0)
        EXECUTE StageDumpToRemoteHost(target_host, "/home/vokov/b-sdd-ui_code_dump.txt")

        // STEP 5: Sub-skill composition - Ingest into NotebookLM (X=0.0, Y=10.0)
        CALL_SKILL(notebooklm, {action: "update_source", source_name: "b-sdd-ui_code_dump.txt"})

        // STEP 6: Verification & Telemetry (X=0.0, Y=12.0)
        EMIT_TELEMETRY(status="SUCCESS")
        RETURN Status="SUCCESS"

    CATCH Error AS e
        LOG_CRITICAL("b-sdd-ui export failed: " + e.Message)
        HALT_AND_DEGRADE(e.Message)
    END
END

text

--------------------------------------------------------------------------------

<!-- DRAKON_VISUAL_FLOW_START -->
## 3. DRAKON Visual Workflow (Planar Skewer X=0)
Schema File:
 b-sdd-ui-export.drakon.json
Total Algorithmic Nodes:
 8
Spine Topology:
 Vertical Skewer (X=0, C=0) verified with rightward degradation branches (X=4.0).
[HEADLINE] Початок: Експорт кодової бази Astryx UI (b-sdd-ui)
[INSERTION] CALL_SKILL(b-sdd): Крок 1: Перевірка стану робочого простору
[ACTION] Крок 2: Синтез текстового дампа кодової бази b-sdd-ui
[QUESTION] Крок 3: Сформований текстовий дамп валідний та не порожній?
[ACTION] Крок 4: Стейджинг дампа на вузол-агрегатор 192.168.3.184
[INSERTION] CALL_SKILL(notebooklm): Крок 5: Завантаження дампа в SSoT блокнот
[END] Успішне завершення: Дамп Astryx UI успішно синхронізовано
[END] Аварійне завершення: Помилка генерації дампа UI (X=4.0)
<!-- DRAKON_VISUAL_FLOW_END -->

---

4. Operational Guide & CLI Execution
Генерація дампа UI локально:
python3 scripts/dump_ui_codebase.py \
  --source /home/vokov/projects/b-sdd/b-sdd-ui \
  --output /home/vokov/b-sdd-ui_code_dump.txt

bash
Копіювання на хост агрегації .184:
scp /home/vokov/b-sdd-ui_code_dump.txt vokov@192.168.3.184:/home/vokov/b-sdd-ui_code_dump.txt

bash

