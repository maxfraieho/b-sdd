# SPRINT_021_04_FITNESS: Fitness Gates & Full Blast-Radius Audit

## РОЛЬ ТА КОНТЕКСТ
Ти — автономний агент виконання B-SDD (хост 161).
Крок: Step 4 (Fitness Gates & Full Blast-Radius Audit) мікро-спринту SPRINT_021.
Оркестратор: Gemini Spark (через NotebookLM `205ee2ec-e0d2-4ba6-badf-44f2de02c7e2`).
Оператор: Human Operator (пасивний моніторинг у Telegram).

## ІНВАРІАНТИ ТА ОБМЕЖЕННЯ
1. Pre-Flight Latency & Words (ADR-005): латентність < 50ms, активні правила <= 500 слів.
2. Zero Third-Party Dependencies (ADR-002): 0 зовнішніх пакетів у `src/core/`.
3. Planar Flow & Right-is-Worse (ADR-008): $X=0, C=0$.
4. Closed-Loop Orchestration (INVARIANT FL-01): обов'язкова фізична публікація звітного артефакту в NotebookLM.

## ЗАВДАННЯ КРОКУ
1. Запустити повний тестовий набір:
   - `python3 -m pytest tests/test_tripartite_adr.py tests/test_planar_solver.py tests/test_architecture_fitness.py -v`
2. Перевірити компіляцію `active_rules.md`:
   - `python3 -m src.cli.main compile`
3. Звірити радіус ураження в GitNexus (перевірити відсутність витоку залежностей за межі доменів).

## ФІНАЛЬНИЙ БЛОК ВИХОДУ (MANDATORY EXIT CRITERIA)
1. Збережи детальний звіт у `logs/sprint_021_fitness_report.json`.
2. Виклич інструмент MCP NotebookLM:
   - notebook_id: `205ee2ec-e0d2-4ba6-badf-44f2de02c7e2`
   - display_name: `INBOX_GEMINI_SPRINT_021_FITNESS_REPORT`
   - content: повний вміст JSON-звіту + pytest summary + GitNexus impact output.
3. Тільки після успішної відповіді від NotebookLM MCP завершуй сесію.
