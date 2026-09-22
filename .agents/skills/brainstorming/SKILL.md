---
name: brainstorming
description: Дослідження концепцій, структурування ідей та генерація альтернативних рішень перед розробкою специфікацій та коду.
type: PROJECT_SKILL
category: ideation
immutable: false
invoked_skills: [using-git-worktrees]
---

# Brainstorming
Скіл для творчого та аналітичного дослідження концепцій перед початком написання коду або формування плану реалізації. Допомагає структурувати розмиті ідеї через діалог, аналіз альтернативних підходів, оцінку компромісів та інкрементну валідацію.

--------------------------------------------------------------------------------

1. Architectural Context & Negative Invariants
ADR Compliance
: Відповідає ADR-015 та ADR-016.
Negative Invariants
:
NEVER
 поспішати переходити до написання коду, доки цілі та альтернативи не зафіксовані.
NEVER
 ігнорувати слабкі сторони або ризики запропонованих підходів.
NEVER
 використовувати цей скіл для чітко детермінованих механічних задач, що мають готову інструкцію.

--------------------------------------------------------------------------------

2. Algorithmic Workflow (ADR-016 Standard)
ALGORITHM ExecuteBrainstorming
INPUT:
    initial_idea: str
    problem_context: dict
OUTPUT:
    status: str ("SUCCESS" | "FAILED" | "DEGRADED")
    design_doc: str

BEGIN
    TRY
        ASSERT initial_idea != ""

        // STEP 1: Main vertical spine - Explore Intent & Problem Space (X=0.0, Y=2.0)
        EXECUTE ExploreProblemSpaceAndRequirements(initial_idea)

        // STEP 2: Main vertical spine - Formulate Alternative Approaches (X=0.0, Y=4.0)
        EXECUTE GenerateDivergentAlternatives(count=3)

        // STEP 3: Question Node - Evaluation & Feasibility Check (X=0.0, Y=6.0)
        IF EvaluateAlternativesFeasibility() THEN
            CONTINUE along Vertical Skewer (X=0.0)
        ELSE
            BRANCH_RIGHT(X=4.0, Y=6.0): Failure/Degradation
            LOG_ERROR("All proposed alternatives fail feasibility constraints")
            HALT_AND_DEGRADE("NO_VIABLE_ALTERNATIVES")
        FI

        // STEP 4: Sub-skill composition - Prepare Isolated Exploration Workspace (X=0.0, Y=8.0)
        CALL_SKILL(using-git-worktrees, {branch_name: "explore/idea-prototype"})

        // STEP 5: Main vertical spine - Synthesize Design Document (X=0.0, Y=10.0)
        EXECUTE SynthesizeConsolidatedConceptDoc()

        // STEP 6: Verification & Completion (X=0.0, Y=12.0)
        ASSERT VerifyConceptClarityAndNextSteps()
        EMIT_TELEMETRY(status="SUCCESS")
        RETURN Status="SUCCESS"

    CATCH Error AS e
        LOG_CRITICAL("Brainstorming session failed: " + e.Message)
        HALT_AND_DEGRADE(e.Message)
    END
END

text

--------------------------------------------------------------------------------

<!-- DRAKON_VISUAL_FLOW_START -->
## 3. DRAKON Visual Workflow (Planar Skewer X=0)
Schema File:
 brainstorming.drakon.json
Total Algorithmic Nodes:
 8
Spine Topology:
 Vertical Skewer (X=0, C=0) verified with rightward degradation branches (X=4.0).
[HEADLINE] Початок: Концептуальне брейнштормінг-дослідження
[ACTION] Крок 1: Дослідження простору проблеми та цілей
[ACTION] Крок 2: Формування дивергентних альтернативних рішень
[QUESTION] Крок 3: Знайдено хоча б одну життєздатну альтернативу?
[INSERTION] CALL_SKILL(using-git-worktrees): Крок 4: Створення ізольованого робочого дерева для прототипу
[ACTION] Крок 5: Синтез концептуального документа дизайну
[END] Успішне завершення: Концепцію сформовано та узгоджено
[END] Аварійне завершення: Відсутність життєздатних альтернатив (X=4.0)
<!-- DRAKON_VISUAL_FLOW_END -->

---

4. Operational Guide & CLI Execution
Створення ізольованого воркспейсу для дослідження:
git worktree add -b explore/new-concept ../new-concept-tree main

bash
Фіксація концептуального документу в базі знань:
echo "# Concept Exploration: $TITLE" > docs/explorations/concept_draft.md

bash

