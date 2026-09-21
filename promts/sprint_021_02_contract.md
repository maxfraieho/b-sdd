# SPRINT_021_02_CONTRACT: Tripartite ADR Ontology & Macro-Prompt IR

## РОЛЬ ТА КОНТЕКСТ
Ти — автономний агент виконання B-SDD (хост 161).
Крок: Step 2 (Formal Contracts & ADR-010 Integration) мікро-спринту SPRINT_021.
Оркестратор: Gemini Spark (через NotebookLM `205ee2ec-e0d2-4ba6-badf-44f2de02c7e2`).
Оператор: Human Operator (пасивний моніторинг у Telegram).

## ІНВАРІАНТИ ТА ОБМЕЖЕННЯ
1. Pure Python Stdlib Core (ADR-002): жодних `pydantic` або інших бібліотек у `src/core/`.
2. Bitemporal Consistency (ADR-001 & ADR-010): WORM-реєстр із підтримкою зрізів `(T_v, T_t)` та атомарної суперсесії.
3. External Pre-Logging Axiom (ADR-010): будь-які виклики зовнішніх API спочатку бітемпорально фіксуються в `DataADR`.
4. Closed-Loop Orchestration (INVARIANT FL-01): обов'язкова фізична публікація звітного артефакту в NotebookLM.

## ЗАВДАННЯ КРОКУ
1. Створити та реалізувати трипартитну онтологію ADR:
   - `src/core/adr/ontology.py` (`DataADR`, `SkillADR`, `SpecADR`, `TripartiteAdrRegistry`, `BitemporalExternalPreLogger`).
2. Створити схему DTO для ДРАКОН-як-Промпт:
   - `src/core/drakon/macro_prompt.py` (`FlowDirective`, `SkillInvocation`, `AdrQuery`, `MacroPromptStep`, `ExecutableMacroPrompt`).
3. Додати та запустити тести контрактів: `tests/test_tripartite_adr.py`.

## ФІНАЛЬНИЙ БЛОК ВИХОДУ (MANDATORY EXIT CRITERIA)
1. Збережи детальний звіт у `logs/sprint_021_contract_report.json`.
2. Виклич інструмент MCP NotebookLM:
   - notebook_id: `205ee2ec-e0d2-4ba6-badf-44f2de02c7e2`
   - display_name: `INBOX_GEMINI_SPRINT_021_CONTRACT_REPORT`
   - content: повний вміст JSON-звіту + pytest summary + GitNexus impact output.
3. Тільки після успішної відповіді від NotebookLM MCP завершуй сесію.
