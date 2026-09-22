---
name: ast-grep
description: Структурний пошук, аналіз та транспіляція кодової бази за шаблонами абстрактного синтаксичного дерева (AST).
type: PROJECT_SKILL
category: code-analysis
immutable: false
invoked_skills: []
---

# ast-grep
Скіл для виконання структурного пошуку та аналізу коду на основі синтаксичного дерева AST через CLI утиліту 
ast-grep
 (
sg
). Дозволяє точно знаходити патерни коду, структурні дефекти та сигнатури функцій незалежно від форматування коду.

--------------------------------------------------------------------------------

1. Architectural Context & Negative Invariants
ADR Compliance
: Відповідає нормам ADR-015 та ADR-016.
Negative Invariants
:
NEVER
 використовувати текстовий regex-пошук там, де потрібне структурне розуміння синтаксису (вкладення, область видимості).
NEVER
 застосовувати правила без вказівки параметра 
stopBy: end
 для реляційних селекторів (
inside
, 
has
), якщо потрібен глибокий пошук.
NEVER
 виконувати масові структурні заміни (
ast-grep scan --rewrite
) без попереднього сухого прогону в режимі верифікації (
--dry-run
 або git diff перевірка).

--------------------------------------------------------------------------------

2. Algorithmic Workflow (ADR-016 Standard)
ALGORITHM ExecuteAstGrep
INPUT:
    pattern: str
    target_path: str
    language: str
OUTPUT:
    status: str ("SUCCESS" | "FAILED" | "DEGRADED")
    matches: list

BEGIN
    TRY
        ASSERT pattern != ""
        ASSERT target_path != ""
        ASSERT language != ""

        // STEP 1: Main vertical spine - Query Debugging & CST Check (X=0.0, Y=2.0)
        EXECUTE DebugAstQueryPattern(pattern, language)

        // STEP 2: Main vertical spine - Execute Search / Scan (X=0.0, Y=4.0)
        EXECUTE RunAstGrepScan(pattern, target_path, language)

        // STEP 3: Question Node - Matches Validity Check (X=0.0, Y=6.0)
        IF ValidateSearchResults() THEN
            CONTINUE along Vertical Skewer (X=0.0)
        ELSE
            BRANCH_RIGHT(X=4.0, Y=6.0): Failure/Degradation
            LOG_ERROR("AST pattern returned invalid or malformed matches")
            HALT_AND_DEGRADE("INVALID_AST_MATCHES")
        FI

        // STEP 4: Main vertical spine - Format & Export Matches (X=0.0, Y=8.0)
        EXECUTE FormatStructuredOutput(format="json")

        // STEP 5: Verification & Telemetry (X=0.0, Y=10.0)
        EMIT_TELEMETRY(status="SUCCESS")
        RETURN Status="SUCCESS"

    CATCH Error AS e
        LOG_CRITICAL("ast-grep execution failed: " + e.Message)
        HALT_AND_DEGRADE(e.Message)
    END
END

text

--------------------------------------------------------------------------------

<!-- DRAKON_VISUAL_FLOW_START -->
## 3. DRAKON Visual Workflow (Planar Skewer X=0)
Schema File:
 ast-grep.drakon.json
Total Algorithmic Nodes:
 7
Spine Topology:
 Vertical Skewer (X=0, C=0) verified with rightward degradation branches (X=4.0).
[HEADLINE] Початок: Структурний аналіз коду через ast-grep
[ACTION] Крок 1: Верифікація патерну через CST/AST парсинг
[ACTION] Крок 2: Виконання сканування цільової директорії
[QUESTION] Крок 3: Синтаксичні збіги валідні та знайдені?
[ACTION] Крок 4: Форматування результатів у структурований JSON
[END] Успішне завершення: Структурний аналіз завершено
[END] Аварійне завершення: Помилка синтаксичного патерну (X=4.0)
<!-- DRAKON_VISUAL_FLOW_END -->

---

4. Operational Guide & CLI Execution
Перевірка синтаксичного дерева AST через debug-query:
ast-grep run --pattern 'async function $NAME($$$ARGS) { $$$BODY }' --lang javascript --debug-query=cst

bash
Пошук структурного патерну з виводом у JSON:
ast-grep run --pattern 'console.log($ARG)' --lang javascript --json .

bash
Виконання складного інлайн-правила:
ast-grep scan --inline-rules "id: async-catch
language: typescript
rule:
  pattern: await $EXPR
  inside:
    kind: try_statement
    stopBy: end" src/

bash

