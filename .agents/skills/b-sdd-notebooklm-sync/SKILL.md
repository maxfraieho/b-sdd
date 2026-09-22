---
name: b-sdd-notebooklm-sync
description: Автономна синхронізація дампів кодової бази B-SDD, активних бітемпоральних ADR з Utopia DB (.251) та посібника оператора в Google NotebookLM.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [b-sdd]
---

# B-SDD NotebookLM Sync
Системний скіл проєкту B-SDD для синхронізації знань у хмарний блокнот Google NotebookLM (ID: 
205ee2ec-e0d2-4ba6-badf-44f2de02c7e2
). Забезпечує вивантаження чистого дампа кодової бази (
b-sdd_code_dump.txt
), реєстру канонічних ADR з бази даних Utopia DB на вузлі 
.251
, повного 10-роздільного посібника оператора та оновлення аудіооглядів Deep Dive.

--------------------------------------------------------------------------------

1. Architectural Context & Negative Invariants
ADR Compliance
: ADR-015 (системний скіл ядра), ADR-016, ADR-003.
Negative Invariants
:
NEVER
 завантажувати бінарні артефакти або папки 
node_modules
, 
.git
, 
dist
, 
__pycache__
 у текстовий дамп коду.
NEVER
 перезаписувати джерела NotebookLM без попереднього очищення застарілих версій аналогічних документів.
NEVER
 передавати ADR без бітемпоральних міток 
valid_from
 та перевірки активного статусу (
valid_to = 'infinity'
).

--------------------------------------------------------------------------------

2. Algorithmic Workflow (ADR-016 Standard)
ALGORITHM ExecuteBSddNotebooklmSync
INPUT:
    notebook_id: str ("205ee2ec-e0d2-4ba6-badf-44f2de02c7e2")
    force_audio: bool
OUTPUT:
    status: str ("SUCCESS" | "FAILED" | "DEGRADED")

BEGIN
    TRY
        ASSERT notebook_id != ""

        // STEP 1: Sub-skill composition - Enforce B-SDD cluster integrity (X=0.0, Y=2.0)
        CALL_SKILL(b-sdd, {action: "verify_cluster_hosts"})

        // STEP 2: Main vertical spine - Extract Code Dump (--code-only) (X=0.0, Y=4.0)
        EXECUTE GenerateCodeDump(source="/home/vokov/projects/b-sdd", output="/home/vokov/b-sdd_code_dump.txt")

        // STEP 3: Main vertical spine - Query Active ADRs from Utopia DB (X=0.0, Y=6.0)
        EXECUTE QueryUtopiaDbActiveAdrs("192.168.3.251")

        // STEP 4: Question Node - Artifacts Integrity Check (X=0.0, Y=8.0)
        IF VerifyStagedSourcesIntegrity() THEN
            CONTINUE along Vertical Skewer (X=0.0)
        ELSE
            BRANCH_RIGHT(X=4.0, Y=8.0): Failure/Degradation
            LOG_ERROR("Staged NotebookLM sources failed integrity check")
            HALT_AND_DEGRADE("INVALID_STAGED_SOURCES")
        FI

        // STEP 5: Main vertical spine - Prune and Ingest via MCP (X=0.0, Y=10.0)
        EXECUTE IngestSourcesViaNotebookLmMcp(notebook_id)

        // STEP 6: Main vertical spine - Audio Overview Generation (X=0.0, Y=12.0)
        IF force_audio THEN
            EXECUTE TriggerNotebookLmAudioDeepDive(notebook_id, lang="uk")
        FI

        // STEP 7: Verification & Telemetry (X=0.0, Y=14.0)
        EMIT_TELEMETRY(status="SUCCESS", notebook_id=notebook_id)
        RETURN Status="SUCCESS"

    CATCH Error AS e
        LOG_CRITICAL("NotebookLM sync failed: " + e.Message)
        HALT_AND_DEGRADE(e.Message)
    END
END

text

--------------------------------------------------------------------------------

<!-- DRAKON_VISUAL_FLOW_START -->
## 3. DRAKON Visual Workflow (Planar Skewer X=0)
Schema File:
 b-sdd-notebooklm-sync.drakon.json
Total Algorithmic Nodes:
 8
Spine Topology:
 Vertical Skewer (X=0, C=0) verified with rightward degradation branches (X=4.0).
[HEADLINE] Початок: Синхронізація артефактів B-SDD у NotebookLM
[INSERTION] CALL_SKILL(b-sdd): Крок 1: Верифікація стану кластера
[ACTION] Крок 2: Генерація чистого текстового дампа кодової бази (--code-only)
[ACTION] Крок 3: Вивантаження активних бітемпоральних ADR з Utopia DB (.251)
[QUESTION] Крок 4: Сформовані файли-джерела валідні?
[ACTION] Крок 5: Очищення застарілих та завантаження нових джерел через MCP
[END] Успішне завершення: Синхронізацію знань у NotebookLM виконано
[END] Аварійне завершення: Помилка формування джерел (X=4.0)
<!-- DRAKON_VISUAL_FLOW_END -->

---

4. Operational Guide & CLI Execution
Пакетна генерація дампа коду на хості .184:
ssh vokov@192.168.3.184 "/home/vokov/projects/resume/run_md_service.sh \
  --batch \
  --source /home/vokov/projects/b-sdd \
  --output /home/vokov/b-sdd_code_dump.txt \
  --code-only"

bash
Компільована доставка посібника оператора:
bash /home/vokov/.agents/skills/b-sdd-notebooklm-sync/scripts/sync_notebooklm.sh

bash

