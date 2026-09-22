---
name: architecture-designer
description: Проектування високорівневої архітектури систем, складання Architecture Decision Records (ADRs), аналіз компромісів та планування масштабованості.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [b-sdd]
---

# Architecture Designer
Системний скіл ядра B-SDD для формування архітектурних концептів, структурного моделювання розподілених систем, створення та супроводу реєстру рішень (ADR) згідно з бітемпоральними нормами.

--------------------------------------------------------------------------------

1. Architectural Context & Negative Invariants
ADR Compliance
: Відповідає ADR-015 (системний рівень ядра), ADR-016 (стандартизація псевдокоду), ADR-008 (планарність графів).
Negative Invariants
:
NEVER
 змінювати архітектурний паттерн без генерації або оновлення відповідного ADR.
NEVER
 видаляти старі ADR без оформлення статусу 
SUPERSEDED
 або створення зв'язку правонаступництва.
NEVER
 приймати технологічні рішення без явної фіксації відкинутих альтернатив (Negative Selection / Trade-offs).
NEVER
 проектувати компоненти без урахування моделі відмов та ізоляції зон відповідальності.

--------------------------------------------------------------------------------

2. Algorithmic Workflow (ADR-016 Standard)
ALGORITHM ExecuteArchitectureDesigner
INPUT:
    system_intent: str
    target_constraints: dict
OUTPUT:
    status: str ("SUCCESS" | "FAILED" | "DEGRADED")
    adr_path: str

BEGIN
    TRY
        ASSERT system_intent != ""
        ASSERT target_constraints != null

        // STEP 1: Main vertical spine - Requirements Analysis (X=0.0, Y=2.0)
        EXECUTE AnalyzeFunctionalAndNonFunctionalRequirements(system_intent, target_constraints)

        // STEP 2: Main vertical spine - Evaluate Trade-offs (X=0.0, Y=4.0)
        EXECUTE EvaluateArchitecturalAlternatives(target_constraints)

        // STEP 3: Question Node - Constraint Satisfiability Check (X=0.0, Y=6.0)
        IF CheckFeasibilityAndConstraints() THEN
            CONTINUE along Vertical Skewer (X=0.0)
        ELSE
            BRANCH_RIGHT(X=4.0, Y=6.0): Failure/Degradation
            LOG_ERROR("Architecture constraints cannot be satisfied")
            HALT_AND_DEGRADE("INCOMPATIBLE_CONSTRAINTS")
        FI

        // STEP 4: Sub-skill composition - Enforce B-SDD Invariants (X=0.0, Y=8.0)
        CALL_SKILL(b-sdd, {action: "verify_adr_standards"})

        // STEP 5: Main vertical spine - Draft ADR & Structural Model (X=0.0, Y=10.0)
        EXECUTE GenerateAdrDocumentAndDrakonModel()

        // STEP 6: Verification & Completion (X=0.0, Y=12.0)
        ASSERT VerifyBitemporalRegistryConsistency()
        EMIT_TELEMETRY(status="SUCCESS")
        RETURN Status="SUCCESS"

    CATCH Error AS e
        LOG_CRITICAL("Architecture design failed: " + e.Message)
        HALT_AND_DEGRADE(e.Message)
    END
END

text

--------------------------------------------------------------------------------

<!-- DRAKON_VISUAL_FLOW_START -->
## 3. DRAKON Visual Workflow (Planar Skewer X=0)
Schema File:
 architecture-designer.drakon.json
Total Algorithmic Nodes:
 8
Spine Topology:
 Vertical Skewer (X=0, C=0) verified with rightward degradation branches (X=4.0).
[HEADLINE] Початок: Проектування архітектури та оформлення ADR
[ACTION] Крок 1: Аналіз функціональних та нефункціональних вимог
[ACTION] Крок 2: Оцінка архітектурних альтернатив та компромісів
[QUESTION] Крок 3: Архітектурні обмеження задовільні?
[INSERTION] CALL_SKILL(b-sdd): Крок 4: Перевірка стандартів B-SDD та реєстру ADR
[ACTION] Крок 5: Генерація документа ADR та структурних моделей
[END] Успішне завершення: Архітектурне рішення зафіксовано
[END] Аварійне завершення: Невідповідність системних обмежень (X=4.0)
<!-- DRAKON_VISUAL_FLOW_END -->

---

4. Operational Guide & CLI Execution
Створення нового ADR через інструментарій проєкту:
python3 -m src.cli.main adr new --title "Adopt Distributed Bus Pattern" --status PROPOSED

bash
Перевірка архітектурної відповідності кодової бази:
pytest -v tests/test_architecture_fitness.py

bash

