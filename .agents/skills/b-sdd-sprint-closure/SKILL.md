---
name: b-sdd-sprint-closure
description: Автономне закриття та дистиляція спринту B-SDD (Phi_6 -> Phi_7), генерація реліз-тегів, компіляція правил, оновлення дампів, деплой UI та синхронізація з Utopia DB і NotebookLM.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [b-sdd, cloudflare-pages-expert, b-sdd-ui-export, b-sdd-notebooklm-sync]
---

# B-SDD Sprint Closure & Distillation
Системний скіл ядра для повного життєвого циклу закриття спринту в парадигмі B-SDD. Реалізує перехід 
\Phi_6 \to \Phi_7
 (Implementation 
\to
 Distillation & Handoff): зачистку тіньових артефактів, оновлення графа знань GitNexus, публікацію вебінтерфейсу Astryx Cockpit у Cloudflare Pages, синхронізацію WORM-леджеру в Utopia DB та надсилання телеметричного вебхука оператору.

--------------------------------------------------------------------------------

1. Architectural Context & Negative Invariants
ADR Compliance
: ADR-005 (компактність правил <500 слів), ADR-007 (хендоф), ADR-015 (бар'єр незмінності скілів), ADR-016.
Negative Invariants
:
NEVER
 закривати спринт, якщо тестовий набір або фітнес-перевірка завершилися з помилкою.
NEVER
 залишати неспресовані правила в 
.context/active_rules.md
 (обмеження строго до 500 слів).
NEVER
 створювати релізний тег 
sprint_XXX_done
 без попереднього пушу змін у гілку 
main
.
NEVER
 пропускати крок фіксації WORM-знімку в базі даних Utopia DB на вузлі 
.251
.

--------------------------------------------------------------------------------

2. Algorithmic Workflow (ADR-016 Standard)
ALGORITHM ExecuteBSddSprintClosure
INPUT:
    sprint_id: str
    prompt: str
OUTPUT:
    status: str ("SUCCESS" | "FAILED" | "DEGRADED")

BEGIN
    TRY
        ASSERT sprint_id != ""

        // STEP 1: Main vertical spine - GitNexus Shadow Cleaner (X=0.0, Y=2.0)
        EXECUTE CleanGitNexusShadows()

        // STEP 2: Main vertical spine - Re-index AST in GitNexus (X=0.0, Y=4.0)
        EXECUTE ReindexGitNexusAst()

        // STEP 3: Sub-skill composition - Export UI Codebase Dump (X=0.0, Y=6.0)
        CALL_SKILL(b-sdd-ui-export, {sprint_id: sprint_id})

        // STEP 4: Sub-skill composition - Deploy Astryx UI to Cloudflare Pages (X=0.0, Y=8.0)
        CALL_SKILL(cloudflare-pages-expert, {project_name: "astryx-cockpit"})

        // STEP 5: Main vertical spine - Skills Catalog Audit & Immutability (X=0.0, Y=10.0)
        EXECUTE DumpSkillsAndVerifyCatalog()

        // STEP 6: Sub-skill composition - Synchronize to NotebookLM SSoT (X=0.0, Y=12.0)
        CALL_SKILL(b-sdd-notebooklm-sync, {notebook_id: "205ee2ec-e0d2-4ba6-badf-44f2de02c7e2"})

        // STEP 7: Main vertical spine - Compile Active Rules (<500 words) (X=0.0, Y=14.0)
        EXECUTE CompileActiveRulesCompact()

        // STEP 8: Question Node - Active Rules Word Count Check (X=0.0, Y=16.0)
        IF VerifyRulesWordCountLeq500() THEN
            CONTINUE along Vertical Skewer (X=0.0)
        ELSE
            BRANCH_RIGHT(X=4.0, Y=16.0): Failure/Degradation
            LOG_ERROR("Active rules exceeded 500 words limit")
            HALT_AND_DEGRADE("RULES_EXCEEDED_BUDGET")
        FI

        // STEP 9: Main vertical spine - Utopia DB Tripartite Sync & WORM Commit (X=0.0, Y=18.0)
        EXECUTE CommitUtopiaDbWormSnapshot(sprint_id)

        // STEP 10: Main vertical spine - Git Release Tag & Push (X=0.0, Y=20.0)
        EXECUTE TagAndPushGitRelease(sprint_id)

        // STEP 11: Verification & Callback Webhook (X=0.0, Y=22.0)
        EXECUTE NotifySupervisorWebhook(sprint_id)
        EMIT_TELEMETRY(status="SUCCESS", sprint_id=sprint_id)
        RETURN Status="SUCCESS"

    CATCH Error AS e
        LOG_CRITICAL("Sprint closure failed: " + e.Message)
        HALT_AND_DEGRADE(e.Message)
    END
END

text

--------------------------------------------------------------------------------

<!-- DRAKON_VISUAL_FLOW_START -->
## 3. DRAKON Visual Workflow (Planar Skewer X=0)
Schema File:
 b-sdd-sprint-closure.drakon.json
Total Algorithmic Nodes:
 13
Spine Topology:
 Vertical Skewer (X=0, C=0) verified with rightward degradation branches (X=4.0).
[HEADLINE] Початок: Життєвий цикл закриття спринту B-SDD (Phi_6 -> Phi_7)
[ACTION] Крок 1: Зачистка тіньових файлів GitNexus (.184)
[ACTION] Крок 2: Оновлення графа знань AST у GitNexus
[INSERTION] CALL_SKILL(b-sdd-ui-export): Крок 3: Синтез дампа коду b-sdd-ui
[INSERTION] CALL_SKILL(cloudflare-pages-expert): Крок 4: Деплой фронтенду в Cloudflare Pages
[ACTION] Крок 5: Аудит каталогу скілів та перевірка бар'єру незмінності ADR-015
[INSERTION] CALL_SKILL(b-sdd-notebooklm-sync): Крок 6: Синхронізація з NotebookLM
[ACTION] Крок 7: Компіляція активних правил у .context/active_rules.md
[QUESTION] Крок 8: Обсяг правил менше 500 слів (ADR-005)?
[ACTION] Крок 9: Синхронізація Tripartite з Utopia DB (.251) та фіксація WORM-знімку
[ACTION] Крок 10: Фіксація тегу sprint_done у git та пуш
[END] Успішне завершення: Спринт успішно закрито та запечатано
[END] Аварійне завершення: Порушення ліміту слів або цілісності (X=4.0)
<!-- DRAKON_VISUAL_FLOW_END -->

---

4. Operational Guide & CLI Execution
Повний автономний запуск закриття спринту:
./run_b_sdd.sh --sprint-closure --sprint-id sprint_022 --prompt "Завершено стабілізацію ядра"

bash
Ручний виклик аудиту скілів перед коммітом:
python3 scripts/dump_skills.py

bash

