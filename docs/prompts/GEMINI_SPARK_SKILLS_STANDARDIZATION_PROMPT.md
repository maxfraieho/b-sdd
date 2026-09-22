# GEMINI SPARK INSTRUCTION & PROMPT: B-SDD TRIPARTITE SKILLS STANDARDIZATION
================================================================================
**Target Model:** Gemini Spark / Gemini Pro 1.5/2.0 in Google NotebookLM  
**Context Notebook:** "B-SDD Methodology, Multi-Session Handoff & Architecture" (`205ee2ec-e0d2-4ba6-badf-44f2de02c7e2`)  
**Input Source File:** `active_skills_raw_dump.txt` (59 active skills)  
**Governing ADRs:** ADR-002, ADR-003, ADR-008, ADR-015, ADR-016  
**Output Format:** Plain Text file (`standardized_skills_corpus.txt`) with strict machine-parseable delimiters  
================================================================================

## 1. РОЛЬ ТА КОНТЕКСТ ДЛЯ GEMINI SPARK

Ти — провідний системний архітектор та генератор знань проєкту **B-SDD (Behavior & Specification-Driven Development)**.
Твоє завдання — виконати пакетну стандартизацію всіх 59 активних скілів агента Agy з файлу-джерела `active_skills_raw_dump.txt`, перетворивши їх на канонічний **Трипартитний Стандарт (Tripartite Skill Standard)** за нормами **ADR-015** (Taxonomy & Immutability) та **ADR-016** (Algorithmic Pseudocode & Visual DRAKON Round-Trip).

На виході ти формуєш єдиний структурований текстовий файл, де кожен скіл упакований у суворі машиночитабельні маркери. Цей файл буде збережено в блокноті NotebookLM, звідки локальний оркестратор Agy (`scripts/unpack_standardized_skills.py`) автоматично розпакує файли по робочих папках, перевірить валідність JSON та топологію планарних графів і запустить тести.

---

## 2. АРХІТЕКТУРНІ ВИМОГИ ТА ІНВАРІАНТИ

Кожен скіл після стандартизації складається з **двох неподільних ізоморфних артефактів**:
1. `SKILL.md` — людино-читабельний маніфест, що містить:
   - Стандартний YAML-frontmatter (ADR-015).
   - Архітектурні інваріанти (негативні вимоги: ЩО КАТЕГОРИЧНО ЗАБОРОНЕНО).
   - **Канонічний алгоритмічний псевдокод** (ADR-016): точна алгоритмічна логіка з ключовими словами `ALGORITHM`, `INPUT/OUTPUT`, `BEGIN/END`, `TRY/CATCH`, `ASSERT`, `IF/THEN/ELSE`, `BRANCH_RIGHT(X=4.0)`, `CALL_SKILL`, `HALT_AND_DEGRADE`.
   - Візуальний якір ДРАКОН-схеми: блок `<!-- DRAKON_VISUAL_FLOW_START -->` ... `<!-- DRAKON_VISUAL_FLOW_END -->`.
   - Операційний посібник та приклади CLI-команд.
2. `<skill_name>.drakon.json` — машинно-виконуваний планарний граф ДРАКОН-IR:
   - 100% валідний JSON.
   - Головний шампур успішного виконання строго вертикальний на координаті $X = 0.0$ ($C = 0$).
   - Гілки перевірок, помилок та деградації відходять виключно вправо на координату $X = 4.0$.
   - Типи вузлів: `headline`, `action`, `question`, `insertion` (для `CALL_SKILL`), `end`.
   - Повна відповідність крокам алгоритмічного псевдокоду 1:1.

### Класифікація системних та проєктних скілів (ADR-015):
- **SYSTEM_SKILL** (`category: bssd-system-skill`, `immutable: true`):
  `b-sdd`, `b-sdd-sprint-closure`, `intent-continuity`, `laya-decision-router`, `drakon-compiler`, `utopia-intent-ledger`, `session-distiller`, `safe-refactor`, `surgical-patch`, `code-reviewer`, `test-driven-development`, `diagnosing-bugs`, `investigate-first`, `systematic-debugging`, `root-cause-tracing`, `astryx-scaffolder`, `kindle-release-pipeline`, `architecture-designer`, `skill-creator`, `skill-audit`, `find-skills`, `writing-skills`, `writing-great-skills`, `codebase-design`, `improve-codebase-architecture`, `testing-anti-patterns`, `condition-based-waiting`, `defense-in-depth`, `verification-before-completion`, `using-git-worktrees`, `cloudflare-pages-expert`, `b-sdd-notebooklm-sync`, `b-sdd-kindle-docs`, `b-sdd-ui-export`.
- **PROJECT_SKILL** (`category: <domain>`, `immutable: false`):
  Усі інші скіли (наприклад, `to-spec`, `to-tickets`, `wayfinder`, `subagent-driven-development`, `handoff`, `brainstorming`, `grill-with-docs`, `frontend-design`, `make-interfaces-feel-better`, `web-design-guidelines`, `vercel-react-best-practices`, `vercel-composition-patterns`, `web-artifacts-builder`, `theme-factory`, `mcp-builder`, `api-designer`, `cli-developer`, `caveman`, `ast-grep`, `webapp-testing`, `writing-plans`, `executing-plans`, `notebooklm`, `notebooklm-gitnexus-copilot`).

---

## 3. СТРОГИЙ МАШИНОЧИТАБЕЛЬНИЙ ФОРМАТ ВИВОДУ (DELIMITERS)

Для кожного скіла виводь строго такий блок (без зайвого вступного чи заключного тексту між блоками):

```text
=== BSSD_STANDARDIZED_SKILL_START: <skill_name> ===
--- FILE: SKILL.md ---
---
name: <skill_name>
description: <Короткий опис українською або англійською мовою>
type: SYSTEM_SKILL | PROJECT_SKILL
category: bssd-system-skill | <category>
immutable: true | false
invoked_skills: [<skill-1>, <skill-2>]
---

# <Назва Скіла>

<Короткий опис призначення скіла>

---

## 1. Architectural Context & Negative Invariants
- **ADR Compliance**: ADR-015 (Taxonomy), ADR-016 (Tripartite Standard), ADR-002 (Pure Stdlib).
- **Negative Invariants**:
  - **NEVER** break ...
  - **NEVER** skip verification of ...
  - **NEVER** crash without entering fallback degradation (X=4.0).

---

## 2. Algorithmic Workflow (ADR-016 Standard)

```text
ALGORITHM Execute<SkillNameCamelCase>
INPUT:
    <param1>: <Type>
    <param2>: <Type>
OUTPUT:
    status: str ("SUCCESS" | "FAILED" | "DEGRADED")

BEGIN
    TRY
        ASSERT Preconditions(...)

        // STEP 1: Main vertical spine (X=0.0, Y=2.0)
        EXECUTE Step1Action(...)

        // STEP 2: Condition check (X=0.0, Y=4.0)
        IF CheckCondition(...) THEN
            CONTINUE along Vertical Skewer (X=0.0)
        ELSE
            BRANCH_RIGHT(X=4.0, Y=4.0): Failure/Degradation
            LOG_ERROR("Condition failed")
            HALT_AND_DEGRADE("REASON")
        FI

        // STEP 3: Skill composition (X=0.0, Y=6.0)
        CALL_SKILL(<invoked_skill>, {param: value})

        // STEP 4: Verification & Completion (X=0.0, Y=8.0)
        ASSERT VerificationCheck(...)
        EMIT_TELEMETRY(status="SUCCESS")
        RETURN Status="SUCCESS"

    CATCH Error AS e
        LOG_CRITICAL("Execution failed: " + e.Message)
        HALT_AND_DEGRADE(e.Message)
    END
END
```

---

<!-- DRAKON_VISUAL_FLOW_START -->
## DRAKON Visual Workflow (Planar Skewer X=0)
- **Schema File:** `<skill_name>.drakon.json`
- **Total Algorithmic Nodes:** N
- **Spine Topology:** Vertical Skewer ($X=0, C=0$) verified with degradation branches ($X=4.0$).
  1. `[HEADLINE]` Початок: ...
  2. `[ACTION]` Крок 1: ...
  3. `[QUESTION]` Крок 2: ...
  4. `[INSERTION]` CALL_SKILL(<invoked_skill>): Крок 3: ...
  5. `[END]` Успішне завершення: ...
  6. `[ACTION]` Помилка/деградація (X=4.0): ...
  7. `[END]` Аварійне завершення (X=4.0): ...
<!-- DRAKON_VISUAL_FLOW_END -->

---

## 3. Operational Guide & CLI Execution
<Конкретні інструкції, команди shell, приклади використання>

--- FILE: <skill_name>.drakon.json ---
{
  "schema_version": "1.0",
  "name": "<Human Readable Title>",
  "category": "bssd_system_skill",
  "description": "<Description>",
  "params": "<parameters signature>",
  "nodes": [
    {
      "node_id": "start",
      "node_type": "headline",
      "label": "Початок: ...",
      "edges": { "down": "step_1", "right": null },
      "semantic_binding": { "adr_invariant_id": "ADR-015-INV-01", "severity": "normal" },
      "x": 0.0,
      "y": 0.0
    },
    {
      "node_id": "step_1",
      "node_type": "action",
      "label": "Крок 1: ...",
      "edges": { "down": "cond_check", "right": null },
      "semantic_binding": { "severity": "normal" },
      "x": 0.0,
      "y": 2.0
    },
    {
      "node_id": "cond_check",
      "node_type": "question",
      "label": "Крок 2: Умова виконана?",
      "edges": { "down": "step_2", "right": "step_err" },
      "semantic_binding": { "severity": "normal" },
      "x": 0.0,
      "y": 4.0
    },
    {
      "node_id": "step_err",
      "node_type": "action",
      "label": "Помилка перевірки: деградація",
      "edges": { "down": "end_failed", "right": null },
      "semantic_binding": { "severity": "critical" },
      "x": 4.0,
      "y": 4.0
    },
    {
      "node_id": "step_2",
      "node_type": "insertion",
      "label": "Крок 3: Виклик підпорядкованого скіла",
      "edges": { "down": "end_success", "right": null },
      "semantic_binding": { "call_skill": "<invoked_skill>", "severity": "normal" },
      "x": 0.0,
      "y": 6.0
    },
    {
      "node_id": "end_success",
      "node_type": "end",
      "label": "Успішне завершення",
      "edges": { "down": null, "right": null },
      "semantic_binding": { "severity": "normal" },
      "x": 0.0,
      "y": 8.0
    },
    {
      "node_id": "end_failed",
      "node_type": "end",
      "label": "Аварійне завершення",
      "edges": { "down": null, "right": null },
      "semantic_binding": { "severity": "critical" },
      "x": 4.0,
      "y": 8.0
    }
  ],
  "meta": {
    "skill_name": "<skill_name>",
    "skill_type": "SYSTEM_SKILL",
    "immutable": true,
    "skewer_x": 0.0,
    "is_planar": true,
    "crossings_count": 0
  }
}
=== BSSD_STANDARDIZED_SKILL_END: <skill_name> ===
```

---

## 4. ЗОЛОТИЙ ЕТАЛОН (REFERENCE EXAMPLE)

Поглянь на вже стандартизований скіл `b-sdd-ui-export` у джерелі `active_skills_raw_dump.txt` або `b-sdd-sprint-closure`. Це зразки 100% відповідності:
- Чіткий вертикальний шампур ($X=0, C=0$).
- Правильні типи вузлів (`headline`, `action`, `question`, `insertion`, `end`).
- Точний псевдокод, що дублює граф.
- Відсутність незамкнених ребер чи невідомих `node_id`.

---

## 5. ПОРЯДОК ПАКЕТНОГО ВИКОНАННЯ

Оскільки скілів 59, ти можеш видавати результат **пакетами по 10-15 скілів** за запитом оператора (або послідовно єдиним потоком):
- **Пакет 1 (1–10):** `api-designer`, `architecture-designer`, `ast-grep`, `astryx-scaffolder`, `b-sdd`, `b-sdd-kindle-docs`, `b-sdd-notebooklm-sync`, `b-sdd-sprint-closure`, `b-sdd-ui-export`, `brainstorming`.
- **Пакет 2 (11–20):** `caveman`, `cli-developer`, `cloudflare-pages-expert`, `code-documenter`, `code-reviewer`, `codebase-design`, `condition-based-waiting`, `defense-in-depth`, `diagnosing-bugs`, `drakon-compiler`.
- **Пакет 3 (21–30):** `executing-plans`, `find-skills`, `frontend-design`, `grill-with-docs`, `handoff`, `improve-codebase-architecture`, `intent-continuity`, `investigate-first`, `kindle-release-pipeline`, `laya-decision-router`.
- **Пакет 4 (31–40):** `make-interfaces-feel-better`, `mcp-builder`, `notebooklm`, `notebooklm-gitnexus-copilot`, `root-cause-tracing`, `safe-refactor`, `session-distiller`, `skill-audit`, `skill-creator`, `subagent-driven-development`.
- **Пакет 5 (41–50):** `surgical-patch`, `systematic-debugging`, `test-driven-development`, `testing-anti-patterns`, `theme-factory`, `to-spec`, `to-tickets`, `using-git-worktrees`, `utopia-intent-ledger`, `vercel-composition-patterns`.
- **Пакет 6 (51–59):** `vercel-react-best-practices`, `verification-before-completion`, `wayfinder`, `web-artifacts-builder`, `web-design-guidelines`, `webapp-testing`, `writing-great-skills`, `writing-plans`, `writing-skills`.

Оператор може скопіювати згенерований текст у файл `standardized_skills_corpus.txt` і запустити:
```bash
python3 scripts/unpack_standardized_skills.py standardized_skills_corpus.txt
```
який автоматично оновить усі каталоги, перевірить топологію та запустить валідаційні тести.
