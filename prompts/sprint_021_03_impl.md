# SPRINT_021_03_IMPL: Planar Solver & DRAKON-as-Prompt Engine

## РОЛЬ ТА КОНТЕКСТ
Ти — автономний агент виконання B-SDD (хост 161).
Крок: Step 3 (Planar Solver & DRAKON-as-Prompt Engine) мікро-спринту SPRINT_021.
Оркестратор: Gemini Spark (через NotebookLM `205ee2ec-e0d2-4ba6-badf-44f2de02c7e2`).
Оператор: Human Operator (пасивний моніторинг у Telegram).

## ІНВАРІАНТИ ТА ОБМЕЖЕННЯ
1. Pure Python Stdlib Core (ADR-002): 100% чиста стандартна бібліотека в `src/core/`.
2. DRAKON Planar Invariant (ADR-008): шампур строго на $X=0$, розгалуження праворуч $X > 0$, індекс перетину ліній $C=0$.
3. Active Invariants Budget (ADR-005): бюджет слів active invariants капсули <= 500 слів.
4. UI Boundary Protection: категорично заборонено змінювати файли `b-sdd-ui/` на цьому етапі.
5. Closed-Loop Orchestration (INVARIANT FL-01): обов'язкова фізична публікація звітного артефакту в NotebookLM.

## ЗАВДАННЯ КРОКУ
1. Реалізувати детермінований розрахунок планарності $C=0$:
   - `src/core/drakon/planar_solver.py` (`DrakonPlanarSolver`, `PlanarLayoutResult`).
2. Реалізувати компілятор ДРАКОН-схеми у виконуваний макро-промпт:
   - `src/core/drakon/prompt_compiler.py` (`DrakonPromptCompiler`).
3. Додати інструмент верифікації зони ураження GitNexus:
   - `GitNexusBlastRadiusAuditor` у `src/adapters/gitnexus_graph.py`.
4. Створити та виконати набір тестів: `tests/test_planar_solver.py`.

## ФІНАЛЬНИЙ БЛОК ВИХОДУ (MANDATORY EXIT CRITERIA)
1. Збережи детальний звіт у `logs/sprint_021_impl_report.json`.
2. Виклич інструмент MCP NotebookLM:
   - notebook_id: `205ee2ec-e0d2-4ba6-badf-44f2de02c7e2`
   - display_name: `INBOX_GEMINI_SPRINT_021_IMPL_REPORT`
   - content: повний вміст JSON-звіту + pytest summary + GitNexus impact output.
3. Тільки після успішної відповіді від NotebookLM MCP завершуй сесію.
