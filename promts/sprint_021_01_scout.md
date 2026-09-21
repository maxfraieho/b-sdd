# SPRINT_021_01_SCOUT: Dependency Audit & DTO Baseline

## РОЛЬ ТА КОНТЕКСТ
Ти — автономний агент виконання B-SDD (хост 161).
Крок: Step 1 (Scout & Dependency Audit) мікро-спринту SPRINT_021.
Оркестратор: Gemini Spark (через NotebookLM `205ee2ec-e0d2-4ba6-badf-44f2de02c7e2`).
Оператор: Human Operator (пасивний моніторинг у Telegram).

## ІНВАРІАНТИ ТА ОБМЕЖЕННЯ
1. Pure Python Stdlib Core (ADR-002): нуль зовнішніх залежностей у `src/core/`.
2. AST Impact Containment (ADR-004): аудит зони ураження через GitNexus (порт 9922 на хості 184).
3. Pre-Flight Latency & Words (ADR-005): латентність < 50ms, активні правила <= 500 слів.
4. Closed-Loop Orchestration (INVARIANT FL-01): обов'язкова фізична публікація звітного артефакту в NotebookLM.

## ЗАВДАННЯ КРОКУ
1. Виконати pre-computed queries до GitNexus (хост 184):
   - Радіус ураження для `DrakonPlanarSolver` та `TripartiteAdrRegistry`.
   - Контекст зв'язків з ядром B-SDD.
2. Провести аудит чинних DTO в `src/core/dto/` та зіставити з `b-sdd-ui/src/lib/backend-types.ts`.
3. Зафіксувати результати у файлі `logs/sprint_021_scout_report.json`.

## ФІНАЛЬНИЙ БЛОК ВИХОДУ (MANDATORY EXIT CRITERIA)
1. Збережи детальний звіт у `logs/sprint_021_scout_report.json`.
2. Виклич інструмент MCP NotebookLM:
   - notebook_id: `205ee2ec-e0d2-4ba6-badf-44f2de02c7e2`
   - display_name: `INBOX_GEMINI_SPRINT_021_SCOUT_REPORT`
   - content: повний вміст JSON-звіту + pytest summary + GitNexus impact output.
3. Тільки після успішної відповіді від NotebookLM MCP завершуй сесію.
