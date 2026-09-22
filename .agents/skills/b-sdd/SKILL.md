---
name: b-sdd
description: Контроль бітемпоральних архітектурних інваріантів, відповідності ADR, компіляції префлайт-правил B-SDD та кристалізації скілів за Правилом Двох.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [find-skills, skill-creator]
---

# B-SDD (Bitemporal Spec-Driven Development) Core Skill
Фундаментальний системний скіл оркестрації життєвого циклу B-SDD. Забезпечує дотримання інваріантів перед початком написання коду (Pre-Flight Phase), процедуру суперсесії архітектурних рішень, кристалізацію нових скілів за «Правилом 2-х повторень» та фінальний верифікаційний бар'єр перед коммітом.

--------------------------------------------------------------------------------

1. Architectural Context & Negative Invariants
ADR Compliance
: Ключовий скіл системи. Керує виконанням ADR-001—ADR-020, ADR-015 (Taxonomy), ADR-016 (Pseudocode/DRAKON).
Negative Invariants
:
NEVER
 починати генерацію коду без наявності скомпільованого 
.context/active_rules.md
 (<500 слів).
NEVER
 видаляти старі ADR або залишати суперечливі формулювання в репозиторії.
NEVER
 повторювати операційний ланцюжок 
\ge 2
 разів без ініціації кристалізації нового скіла (Rule of 2).
NEVER
 виконувати комміт або закривати задачу без проходження тесту фітнесу архітектури (
pytest tests/test_architecture_fitness.py
).

--------------------------------------------------------------------------------

2. Algorithmic Workflow (ADR-016 Standard)
ALGORITHM ExecuteBSdd
INPUT:
    context: dict
    task_scope: str
OUTPUT:
    status: str ("SUCCESS" | "FAILED" | "DEGRADED")

BEGIN
    TRY
        ASSERT context != null

        // STEP 1: Sub-skill composition - Pre-flight skill lookup (X=0.0, Y=2.0)
        CALL_SKILL(find-skills, {query: task_scope})

        // STEP 2: Main vertical spine - Check & Compile Active Rules (X=0.0, Y=4.0)
        EXECUTE EnsureActiveRulesCompiled()

        // STEP 3: Question Node - Pre-Flight Gate Verification (X=0.0, Y=6.0)
        IF VerifyPreconditions() THEN
            CONTINUE along Vertical Skewer (X=0.0)
        ELSE
            BRANCH_RIGHT(X=4.0, Y=6.0): Failure/Degradation
            LOG_ERROR("B-SDD pre-flight verification failed")
            HALT_AND_DEGRADE("PREFLIGHT_VERIFICATION_FAILED")
        FI

        // STEP 4: Sub-skill composition - Check Rule of 2 (X=0.0, Y=8.0)
        IF CheckPatternRepetitionGte2() THEN
            CALL_SKILL(skill-creator, {trigger: "rule_of_2", context: context})
        FI

        // STEP 5: Main vertical spine - Run Architecture Fitness Suite (X=0.0, Y=10.0)
        EXECUTE RunArchitectureFitnessSuite()

        // STEP 6: Verification & Completion (X=0.0, Y=12.0)
        ASSERT VerifyFitnessLatencyAndMemory()
        EMIT_TELEMETRY(status="SUCCESS")
        RETURN Status="SUCCESS"

    CATCH Error AS e
        LOG_CRITICAL("B-SDD invariant violation: " + e.Message)
        HALT_AND_DEGRADE(e.Message)
    END
END

text

--------------------------------------------------------------------------------

<!-- DRAKON_VISUAL_FLOW_START -->
## 3. DRAKON Visual Workflow (Planar Skewer X=0)
Schema File:
 b-sdd.drakon.json
Total Algorithmic Nodes:
 8
Spine Topology:
 Vertical Skewer (X=0, C=0) verified with rightward degradation branches (X=4.0).
[HEADLINE] Початок: Контроль архітектурних інваріантів B-SDD
[INSERTION] CALL_SKILL(find-skills): Крок 1: Префлайт пошук активних скілів
[ACTION] Крок 2: Перевірка та компіляція .context/active_rules.md
[QUESTION] Крок 3: Префлайт інваріанти задоволені?
[INSERTION] CALL_SKILL(skill-creator): Крок 4: Кристалізація за Правилом 2-х повторень
[ACTION] Крок 5: Запуск тестового набору фітнесу архітектури
[END] Успішне завершення: Архітектурну відповідність підтверджено
[END] Аварійне завершення: Порушення інваріантів B-SDD (X=4.0)
<!-- DRAKON_VISUAL_FLOW_END -->

---

4. Operational Guide & CLI Execution
Префлайт компіляція правил:
python3 -m src.cli.main compile

bash
Запуск архітектурного фітнес-сьюту:
pytest -v tests/test_architecture_fitness.py

bash

