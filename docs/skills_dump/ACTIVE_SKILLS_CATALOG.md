# B-SDD ACTIVE CORE SKILLS CATALOG (59 ACTIVE SKILLS)

**Дата генерації:** 2026-09-22 20:51:04Z  
**Хост оркестрації:** `100.65.225.122` (`192.168.3.161`)  
**Каталог активних скілів:** `/home/vokov/.agents/skills`  
**Каталог розширених скілів:** `/home/vokov/.agents/skills/_extended`  
**Стандарт онтології:** B-SDD Methodology v1.2 / ADR-001..020 (SkillADR)  
**Статус:** Затверджено як активний стандарт для Astryx Copilot та ДРАКОН-нод.  

> [!IMPORTANT]
> Даний каталог містить **59 активних скілів ядра**, включаючи відновлені скіли спринту 027 (kindle-release-pipeline, drakon-compiler, utopia-intent-ledger, astryx-scaffolder).
> Допоміжні та доменні скіли (29 найменувань) надійно ізольовано в `~/.agents/skills/_extended/`
> і не перевантажують контекстне вікно планувальника.

---

## 📊 Зведений огляд категорій

| № | Категорія | Кількість скілів | Призначення |
|---|-----------|:----------------:|-------------|
| 1 | Core B-SDD & Architecture | 11 | Дотримання інваріантів B-SDD, бітемпоральність, ДРАКОН-компілятор, Utopia Ledger |
| 2 | Planning & SSD Specs | 9 | Планування, декомпозиція задач, передача контексту, парне проєктування |
| 3 | Refactoring & Code Quality | 9 | Безпечний рефакторинг, патчинг, AST-пошук, рев'ю та git-ізоляція |
| 4 | Testing & TDD | 5 | TDD-цикли, антипатерни тестування, ліквідація гонок, веб-тести |
| 5 | Diagnostics & Debugging | 4 | Системне налагодження, пошук кореневих причин, трейсинг дефектів |
| 6 | Frontend & Astryx Ergonomics | 8 | Інтерфейси Astryx Cockpit, скафолдинг компонентів, React/Vercel патерни |
| 7 | Protocols & System Tools | 7 | Kindle пайплайн релізів, MCP-сервери, NotebookLM, GitNexus, API та CLI |
| **Σ** | **Всього активних скілів** | **59** | **Повний замкнений контур AGI** |

---

## 1. Core B-SDD & Architecture (13)

### `b-sdd`
- **Назва:** b-sdd
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Контроль бітемпоральних архітектурних інваріантів, відповідності ADR, компіляції префлайт-правил B-SDD та кристалізації скілів за Правилом Двох.
- **Шлях:** `~/.agents/skills/b-sdd`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, b-sdd.drakon.json`

### `b-sdd-sprint-closure`
- **Назва:** b-sdd-sprint-closure
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Автономне закриття та дистиляція спринту B-SDD (Phi_6 -> Phi_7), генерація реліз-тегів, компіляція правил, оновлення дампів, деплой UI та синхронізація з Utopia DB і NotebookLM.
- **Шлях:** `~/.agents/skills/b-sdd-sprint-closure`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, b-sdd-sprint-closure.drakon.json, scripts/sprint_closure.py`

### `session-distiller`
- **Назва:** session-distiller
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Аналітична дистиляція логів довгих сесій у компактні підсумки, архітектурні висновки та списки задач.
- **Шлях:** `~/.agents/skills/session-distiller`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, session-distiller.drakon.json`

### `intent-continuity`
- **Назва:** intent-continuity
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Забезпечення безперервності намірів та рішень крізь розподілені агентські сесії через бітемпоральний леджер.
- **Шлях:** `~/.agents/skills/intent-continuity`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, intent-continuity.drakon.json`

### `laya-decision-router`
- **Назва:** laya-decision-router
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Суб-40мс не-авторегресивна System 1 класифікація задач, оцінка ризиків порушення ADR та маршрутизація скілів на Pixel 7.
- **Шлях:** `~/.agents/skills/laya-decision-router`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, laya-decision-router.drakon.json`

### `drakon-compiler`
- **Назва:** drakon-compiler
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Компіляція планарних ДРАКОН-схем (.drakon.json) у виконуваний код (Python/TypeScript), зворотна трансляція та валідація інваріантів C=0.
- **Шлях:** `~/.agents/skills/drakon-compiler`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, drakon-compiler.drakon.json, scripts/compile_drakon.py`

### `utopia-intent-ledger`
- **Назва:** utopia-intent-ledger
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Синхронізація архітектурних рішень та графів намірів у незмінний WORM-леджер Utopia DB на вузлі 192.168.3.251.
- **Шлях:** `~/.agents/skills/utopia-intent-ledger`
- **Кількість файлів коду/конфігів:** 4
- **Ключові файли:** `SKILL.md, utopia-intent-ledger.drakon.json, scripts/sync_utopia.py, scripts/validate_ontology.py`

### `architecture-designer`
- **Назва:** architecture-designer
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Проектування високорівневої архітектури систем, складання Architecture Decision Records (ADRs), аналіз компромісів та планування масштабованості.
- **Шлях:** `~/.agents/skills/architecture-designer`
- **Кількість файлів коду/конфігів:** 7
- **Ключові файли:** `SKILL.md, architecture-designer.drakon.json, references/adr-template.md, references/architecture-patterns.md, references/database-selection.md, references/nfr-checklist.md, references/system-design.md`

### `skill-creator`
- **Назва:** skill-creator
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Створення та кристалізація нових агентських скілів за правилом 2-х повторень з повною генерацією маніфесту та схеми.
- **Шлях:** `~/.agents/skills/skill-creator`
- **Кількість файлів коду/конфігів:** 8
- **Ключові файли:** `LICENSE.txt, SKILL.md, skill-creator.drakon.json, references/output-patterns.md, references/workflows.md, scripts/init_skill.py, scripts/package_skill.py, scripts/quick_validate.py`

### `writing-great-skills`
- **Назва:** writing-great-skills
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Керівництво зі створення високоефективних, лаконічних та однозначних інструкцій для агентів.
- **Шлях:** `~/.agents/skills/writing-great-skills`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `GLOSSARY.md, SKILL.md, writing-great-skills.drakon.json`

### `writing-skills`
- **Назва:** writing-skills
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Базові стандарти синтаксису, метаданих та формулювання процедурних правил для каталогу скілів.
- **Шлях:** `~/.agents/skills/writing-skills`
- **Кількість файлів коду/конфігів:** 4
- **Ключові файли:** `SKILL.md, anthropic-best-practices.md, persuasion-principles.md, writing-skills.drakon.json`

### `skill-audit`
- **Назва:** skill-audit
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Ревізія та верифікація скілів на відповідність стандартам таксономії ADR-015, планарності ДРАКОН та актуальності.
- **Шлях:** `~/.agents/skills/skill-audit`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, skill-audit.drakon.json`

### `find-skills`
- **Назва:** find-skills
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Пошук та виявлення релевантних спеціалізованих скілів у локальному та розширеному каталозі агентів.
- **Шлях:** `~/.agents/skills/find-skills`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, find-skills.drakon.json`

---

## 2. Planning & SSD Specs (9)

### `writing-plans`
- **Назва:** writing-plans
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Складання структурованих, інкрементних планів реалізації з чіткими критеріями перевірки кожного кроку.
- **Шлях:** `~/.agents/skills/writing-plans`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, writing-plans.drakon.json`

### `executing-plans`
- **Назва:** executing-plans
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Дисципліноване пакетне виконання затверджених планів реалізації з контрольними точками верифікації.
- **Шлях:** `~/.agents/skills/executing-plans`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, executing-plans.drakon.json`

### `to-spec`
- **Назва:** to-spec
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Трансформація неструктурованих вимог та ідей у суворі, формальні інженерні специфікації поведінки.
- **Шлях:** `~/.agents/skills/to-spec`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, to-spec.drakon.json`

### `to-tickets`
- **Назва:** to-tickets
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Декомпозиція високорівневих специфікацій на атомарні, машинозчитувані тікети для автономних виконавців.
- **Шлях:** `~/.agents/skills/to-tickets`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, to-tickets.drakon.json`

### `wayfinder`
- **Назва:** wayfinder
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Навігація по великих кодових базах, пошук точок входу, картування залежностей та побудова маршруту дослідження.
- **Шлях:** `~/.agents/skills/wayfinder`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, wayfinder.drakon.json`

### `subagent-driven-development`
- **Назва:** subagent-driven-development
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Делегування ізольованих підзадач незалежним субагентам для збереження контекстного бюджету головного агента.
- **Шлях:** `~/.agents/skills/subagent-driven-development`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, subagent-driven-development.drakon.json`

### `handoff`
- **Назва:** handoff
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Формування дискретного, машинозчитуваного артефакту передачі контексту між сесіями та спринтами (ADR-007).
- **Шлях:** `~/.agents/skills/handoff`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, handoff.drakon.json`

### `brainstorming`
- **Назва:** brainstorming
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Дослідження концепцій, структурування ідей та генерація альтернативних рішень перед розробкою специфікацій та коду.
- **Шлях:** `~/.agents/skills/brainstorming`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, brainstorming.drakon.json`

### `grill-with-docs`
- **Назва:** grill-with-docs
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Інтенсивне структуроване інтерв'ю для виявлення прихованих припущень та паралельного формування ADR і глосарію домену.
- **Шлях:** `~/.agents/skills/grill-with-docs`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, grill-with-docs.drakon.json`

---

## 3. Refactoring & Code Quality (9)

### `safe-refactor`
- **Назва:** safe-refactor
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Безпечний рефакторинг коду під захистом автоматизованих тестів зі збереженням поведінкових інваріантів.
- **Шлях:** `~/.agents/skills/safe-refactor`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, safe-refactor.drakon.json, agents/openai.yaml`

### `surgical-patch`
- **Назва:** surgical-patch
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Точкове, мінімально інвазивне внесення виправлень без супутнього руйнування сусіднього коду та структури.
- **Шлях:** `~/.agents/skills/surgical-patch`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, surgical-patch.drakon.json, agents/openai.yaml`

### `codebase-design`
- **Назва:** codebase-design
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Формування архітектурної чистоти та структури кодової бази, розділення модулів, дотримання слабкої зв'язності (loose coupling).
- **Шлях:** `~/.agents/skills/codebase-design`
- **Кількість файлів коду/конфігів:** 4
- **Ключові файли:** `DEEPENING.md, DESIGN-IT-TWICE.md, SKILL.md, codebase-design.drakon.json`

### `improve-codebase-architecture`
- **Назва:** improve-codebase-architecture
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Поглиблення неглибоких модулів, реструктуризація коду за принципами Джона Оустерхаута та оптимізація інтерфейсів.
- **Шлях:** `~/.agents/skills/improve-codebase-architecture`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `HTML-REPORT.md, SKILL.md, improve-codebase-architecture.drakon.json`

### `code-reviewer`
- **Назва:** code-reviewer
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Аналіз код-дифів (PR/MR), виявлення архітектурних запахів, вразливостей безпеки, дефектів продуктивності та надання конструктивного рев'ю.
- **Шлях:** `~/.agents/skills/code-reviewer`
- **Кількість файлів коду/конфігів:** 8
- **Ключові файли:** `SKILL.md, code-reviewer.drakon.json, references/common-issues.md, references/feedback-examples.md, references/receiving-feedback.md, references/report-template.md, references/review-checklist.md, references/spec-compliance-review.md`

### `code-documenter`
- **Назва:** code-documenter
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Генерація, структурування та валідація технічної документації, коментарів JSDoc/docstrings та OpenAPI специфікацій.
- **Шлях:** `~/.agents/skills/code-documenter`
- **Кількість файлів коду/конфігів:** 10
- **Ключові файли:** `SKILL.md, code-documenter.drakon.json, references/api-docs-fastapi-django.md, references/api-docs-nestjs-express.md, references/coverage-reports.md, references/documentation-systems.md, references/interactive-api-docs.md, references/python-docstrings.md` (+ 2 more...)

### `ast-grep`
- **Назва:** ast-grep
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Структурний пошук, аналіз та транспіляція кодової бази за шаблонами абстрактного синтаксичного дерева (AST).
- **Шлях:** `~/.agents/skills/ast-grep`
- **Кількість файлів коду/конфігів:** 4
- **Ключові файли:** `README.md, SKILL.md, ast-grep.drakon.json, references/rule_reference.md`

### `verification-before-completion`
- **Назва:** verification-before-completion
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Обов'язковий попередній аудит та запуск перевірочних скриптів перед декларуванням успішного завершення задачі.
- **Шлях:** `~/.agents/skills/verification-before-completion`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, verification-before-completion.drakon.json`

### `using-git-worktrees`
- **Назва:** using-git-worktrees
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Ізоляція робочих контекстів та паралельних завдань за допомогою механізму git worktree без перемикання поточної гілки.
- **Шлях:** `~/.agents/skills/using-git-worktrees`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, using-git-worktrees.drakon.json`

---

## 4. Testing & TDD (5)

### `test-driven-development`
- **Назва:** test-driven-development
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Розробка через тестування (TDD): цикл Red-Green-Refactor, де жоден рядок коду не пишеться без попередньо падаючого тесту.
- **Шлях:** `~/.agents/skills/test-driven-development`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, test-driven-development.drakon.json`

### `testing-anti-patterns`
- **Назва:** testing-anti-patterns
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Виявлення та виправлення антипатернів тестування (надлишковий мокінг, тестування реалізації замість поведінки, tautological tests).
- **Шлях:** `~/.agents/skills/testing-anti-patterns`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, testing-anti-patterns.drakon.json`

### `condition-based-waiting`
- **Назва:** condition-based-waiting
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Ліквідація ненадійних тестів (flaky tests) через заміну фіксованих таймаутів на детерміноване очікування настання умов.
- **Шлях:** `~/.agents/skills/condition-based-waiting`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, condition-based-waiting.drakon.json, example.ts`

### `defense-in-depth`
- **Назва:** defense-in-depth
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Ешелонована багаторівнева валідація даних на межах API, бізнес-логіки та системних викликів для запобігання дефектам.
- **Шлях:** `~/.agents/skills/defense-in-depth`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, defense-in-depth.drakon.json`

### `webapp-testing`
- **Назва:** webapp-testing
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Комплексне тестування веб-додатків через Playwright/Vitest, перевірка користувацьких сценаріїв та API-інтеграцій.
- **Шлях:** `~/.agents/skills/webapp-testing`
- **Кількість файлів коду/конфігів:** 7
- **Ключові файли:** `LICENSE.txt, SKILL.md, webapp-testing.drakon.json, examples/console_logging.py, examples/element_discovery.py, examples/static_html_automation.py, scripts/with_server.py`

---

## 5. Diagnostics & Debugging (4)

### `investigate-first`
- **Назва:** investigate-first
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Обов'язкове попереднє дослідження фактичного стану системи та коду перед будь-якими змінами чи гіпотезами.
- **Шлях:** `~/.agents/skills/investigate-first`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, investigate-first.drakon.json, agents/openai.yaml`

### `systematic-debugging`
- **Назва:** systematic-debugging
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Методичне усунення дефектів: формулювання гіпотез, ізоляція причин, перевірка експериментами та закріплення тестами.
- **Шлях:** `~/.agents/skills/systematic-debugging`
- **Кількість файлів коду/конфігів:** 7
- **Ключові файли:** `CREATION-LOG.md, SKILL.md, systematic-debugging.drakon.json, test-academic.md, test-pressure-1.md, test-pressure-2.md, test-pressure-3.md`

### `root-cause-tracing`
- **Назва:** root-cause-tracing
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Глибинне трасування першопричин збоїв через граф залежностей та стек викликів до вихідного джерела помилки.
- **Шлях:** `~/.agents/skills/root-cause-tracing`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, find-polluter.sh, root-cause-tracing.drakon.json`

### `diagnosing-bugs`
- **Назва:** diagnosing-bugs
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Систематична петля діагностики критичних багів, регресій продуктивності та побудова відтворюваного детермінованого тест-кейсу.
- **Шлях:** `~/.agents/skills/diagnosing-bugs`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, diagnosing-bugs.drakon.json, scripts/hitl-loop.template.sh`

---

## 6. Frontend & Astryx Ergonomics (9)

### `frontend-design`
- **Назва:** frontend-design
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Створення виразних, ергономічних та високоякісних користувацьких вебінтерфейсів з униканням шаблонного дизайну.
- **Шлях:** `~/.agents/skills/frontend-design`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `LICENSE.txt, SKILL.md, frontend-design.drakon.json`

### `astryx-scaffolder`
- **Назва:** astryx-scaffolder
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Генерація компонентів Astryx Cockpit UI, інтерактивних віджетів ДРАКОН-полотна, телеметричних панелей та мультипроєктного середовища оператора.
- **Шлях:** `~/.agents/skills/astryx-scaffolder`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, astryx-scaffolder.drakon.json, scripts/scaffold_component.py`

### `cloudflare-pages-expert`
- **Назва:** cloudflare-pages-expert
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Автономна збірка, налаштування (_headers, _redirects, CORS, CSP) та публікація фронтенду Astryx Cockpit у Cloudflare Pages через Wrangler CLI.
- **Шлях:** `~/.agents/skills/cloudflare-pages-expert`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, cloudflare-pages-expert.drakon.json`

### `make-interfaces-feel-better`
- **Назва:** make-interfaces-feel-better
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Полірування мікроінтеракцій, реактивності інтерфейсу, оптимістичних оновлень та сприйняття швидкодії UI.
- **Шлях:** `~/.agents/skills/make-interfaces-feel-better`
- **Кількість файлів коду/конфігів:** 6
- **Ключові файли:** `SKILL.md, animations.md, make-interfaces-feel-better.drakon.json, performance.md, surfaces.md, typography.md`

### `web-design-guidelines`
- **Назва:** web-design-guidelines
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Дотримання стандартів доступності (a11y), семантичної верстки, контрастності та адаптивності веб-інтерфейсів.
- **Шлях:** `~/.agents/skills/web-design-guidelines`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, web-design-guidelines.drakon.json`

### `vercel-react-best-practices`
- **Назва:** vercel-react-best-practices
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Інженерні стандарти продуктивності React та Next.js від Vercel: мінімізація ререндерів, бандлу та затримок.
- **Шлях:** `~/.agents/skills/vercel-react-best-practices`
- **Кількість файлів коду/конфігів:** 74
- **Ключові файли:** `AGENTS.md, README.md, SKILL.md, vercel-react-best-practices.drakon.json, rules/advanced-effect-event-deps.md, rules/advanced-event-handler-refs.md, rules/advanced-init-once.md, rules/advanced-use-latest.md` (+ 66 more...)

### `vercel-composition-patterns`
- **Назва:** vercel-composition-patterns
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Архітектурні патерни компонування сучасних React-додатків, серверні компоненти (RSC) та оптимізація рендерингу.
- **Шлях:** `~/.agents/skills/vercel-composition-patterns`
- **Кількість файлів коду/конфігів:** 12
- **Ключові файли:** `AGENTS.md, README.md, SKILL.md, vercel-composition-patterns.drakon.json, rules/architecture-avoid-boolean-props.md, rules/architecture-compound-components.md, rules/patterns-children-over-render-props.md, rules/patterns-explicit-variants.md` (+ 4 more...)

### `web-artifacts-builder`
- **Назва:** web-artifacts-builder
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Автономна генерація односторінкових HTML/JS/CSS веб-артефактів, інтерактивних демонстрацій та візуалізаторів.
- **Шлях:** `~/.agents/skills/web-artifacts-builder`
- **Кількість файлів коду/конфігів:** 5
- **Ключові файли:** `LICENSE.txt, SKILL.md, web-artifacts-builder.drakon.json, scripts/bundle-artifact.sh, scripts/init-artifact.sh`

### `theme-factory`
- **Назва:** theme-factory
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Проектування та гармонізація палітр кольорів, темної та світлої теми, токенів дизайну та типографіки.
- **Шлях:** `~/.agents/skills/theme-factory`
- **Кількість файлів коду/конфігів:** 13
- **Ключові файли:** `LICENSE.txt, SKILL.md, theme-factory.drakon.json, themes/arctic-frost.md, themes/botanical-garden.md, themes/desert-rose.md, themes/forest-canopy.md, themes/golden-hour.md` (+ 5 more...)

---

## 7. Protocols & System Tools (10)

### `kindle-release-pipeline`
- **Назва:** kindle-release-pipeline
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Повний релізний конвеєр компіляції дайджестів, оновлень архітектури та книг для мобільних рідерів Kindle.
- **Шлях:** `~/.agents/skills/kindle-release-pipeline`
- **Кількість файлів коду/конфігів:** 9
- **Ключові файли:** `SKILL.md, kindle-release-pipeline.drakon.json, scripts/bsdd_to_kindle.py, scripts/dispatch_kindle_book.sh, scripts/dispatch_on_184.sh, scripts/dossier_to_kindle.py, scripts/kindle_digest.py, scripts/md_to_epub.py` (+ 1 more...)

### `b-sdd-kindle-docs`
- **Назва:** b-sdd-kindle-docs
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Автономний конвеєр компіляції документації B-SDD в EPUB 3.0 та відправка на Amazon Kindle через шлюз n8n та резервний контур на хості .184.
- **Шлях:** `~/.agents/skills/b-sdd-kindle-docs`
- **Кількість файлів коду/конфігів:** 5
- **Ключові файли:** `SKILL.md, b-sdd-kindle-docs.drakon.json, scripts/bsdd_to_kindle.py, scripts/dispatch_on_184.sh, scripts/send_mail.py`

### `notebooklm`
- **Назва:** notebooklm
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Взаємодія з Google NotebookLM API та MCP для організації досліджень, синтезу знань та аудіо-оглядів.
- **Шлях:** `~/.agents/skills/notebooklm`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, notebooklm.drakon.json`

### `notebooklm-gitnexus-copilot`
- **Назва:** notebooklm-gitnexus-copilot
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Спільний аналітичний міст між графом знань GitNexus AST на хості .184 та блокнотом NotebookLM SSoT.
- **Шлях:** `~/.agents/skills/notebooklm-gitnexus-copilot`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, notebooklm-gitnexus-copilot.drakon.json`

### `b-sdd-notebooklm-sync`
- **Назва:** b-sdd-notebooklm-sync
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Автономна синхронізація дампів кодової бази B-SDD, активних бітемпоральних ADR з Utopia DB (.251) та посібника оператора в Google NotebookLM.
- **Шлях:** `~/.agents/skills/b-sdd-notebooklm-sync`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, b-sdd-notebooklm-sync.drakon.json, scripts/sync_notebooklm.sh`

### `b-sdd-ui-export`
- **Назва:** b-sdd-ui-export
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Автономний конвеєр синтезу структурованого дампа вебінтерфейсу Astryx Cockpit UI (b-sdd-ui) та його синхронізація в SSoT блокнот NotebookLM.
- **Шлях:** `~/.agents/skills/b-sdd-ui-export`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, b-sdd-ui-export.drakon.json`

### `mcp-builder`
- **Назва:** mcp-builder
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Проектування, реалізація та тестування серверів Model Context Protocol (MCP) для підключення зовнішніх інструментів.
- **Шлях:** `~/.agents/skills/mcp-builder`
- **Кількість файлів коду/конфігів:** 11
- **Ключові файли:** `LICENSE.txt, SKILL.md, mcp-builder.drakon.json, reference/evaluation.md, reference/mcp_best_practices.md, reference/node_mcp_server.md, reference/python_mcp_server.md, scripts/connections.py` (+ 3 more...)

### `api-designer`
- **Назва:** api-designer
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Архітектурне проектування REST/GraphQL API, створення специфікацій OpenAPI 3.1, моделювання ресурсів та валідація мок-контрактів.
- **Шлях:** `~/.agents/skills/api-designer`
- **Кількість файлів коду/конфігів:** 7
- **Ключові файли:** `SKILL.md, api-designer.drakon.json, references/error-handling.md, references/openapi.md, references/pagination.md, references/rest-patterns.md, references/versioning.md`

### `cli-developer`
- **Назва:** cli-developer
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Проектування та розробка високопродуктивних консольних утиліт (CLI), парсинг прапорців, інтерактивні підказки та автодоповнення.
- **Шлях:** `~/.agents/skills/cli-developer`
- **Кількість файлів коду/конфігів:** 7
- **Ключові файли:** `SKILL.md, cli-developer.drakon.json, references/design-patterns.md, references/go-cli.md, references/node-cli.md, references/python-cli.md, references/ux-patterns.md`

### `caveman`
- **Назва:** caveman
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Ультрастислий режим комунікації для економії токенів без втрати технічного змісту та строгості.
- **Шлях:** `~/.agents/skills/caveman`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `README.md, SKILL.md, caveman.drakon.json`

---

## 📦 Ізольовані розширені скіли (`~/.agents/skills/_extended/`) — 29 скілів

> [!NOTE]
> Ці скіли збережені для специфічних сценаріїв, але ізольовані від основного дерева скілів, щоб оптимізувати розмір контексту та уникнути дублювання патернів.

| Скіл | Призначення / Опис |
|------|--------------------|
| `ask-matt` | Ask which skill or flow fits your situation. A router over the skills in this repo. |
| `b-sdd-notebooklm-sync` | Autonomous pipeline for synchronizing B-SDD codebase dumps, active bitemporal ADRs from Utopia DB (.251), comprehensi... |
| `canvas-design` | Create beautiful visual art in .png and .pdf documents using design philosophy. You should use this skill when the us... |
| `chaos-engineer` | Designs chaos experiments, creates failure injection frameworks, and facilitates game day exercises for distributed s... |
| `cloud-architect` | Designs cloud architectures, creates migration plans, generates cost optimization recommendations, and produces disas... |
| `codex` | Use when delegating implementation tasks to Codex CLI. Codex = primary implementer for bulk code/docs work. Invoke th... |
| `composition-patterns` | React composition patterns that scale. Use when refactoring components with boolean prop proliferation, building flex... |
| `dispatching-parallel-agents` | Use when facing 3+ independent failures that can be investigated without shared state or dependencies - dispatches mu... |
| `doc-indexer` | Use when creating or updating _INDEX.md files for documentation directories, auditing link coverage, or ensuring ever... |
| `documentation-review` | Use when reviewing documentation for clarity, correctness, completeness, and consistency. Apply before marking any do... |
| `finishing-a-development-branch` | Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides comple... |
| `implement` | Implement a piece of work based on a spec or set of tickets. |
| `kubernetes-specialist` | Use when deploying or managing Kubernetes workloads. Invoke to create deployment manifests, configure pod security po... |
| `lean-build` | Build feature work with high overbuilding risk. Use for new behavior, product slices, or integrations where repositor... |
| `migration` | Implement reversible compatibility-safe transitions. Use for schema, data, API, protocol, configuration, or dependenc... |
| `obsidian-markdown` | Use when working with Obsidian-flavored Markdown in the BLOOM knowledge base (src/site/notes/). Covers wiki-links, fr... |
| `prototype` | Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state mode... |
| `react-best-practices` | React and Next.js performance optimization guidelines from Vercel Engineering. This skill should be used when writing... |
| `receiving-code-review` | Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or tec... |
| `requesting-code-review` | Use when completing tasks, implementing major features, or before merging to verify work meets requirements - dispatc... |
| `research` | Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Us... |
| `setup-matt-pocock-skills` | Configure this repo for the engineering skills — set up its issue tracker, triage label vocabulary, and domain doc la... |
| `sharing-skills` | Use when you've developed a broadly useful skill and want to contribute it upstream via pull request - guides process... |
| `superpowers` | No description provided. |
| `teach` | Teach the user a new skill or concept, within this workspace. |
| `triage` | Move issues and external PRs through a state machine of triage roles — categorise, verify, grill if needed, and write... |
| `using-superpowers` | Use when starting any conversation - establishes mandatory workflows for finding and using skills, including using Sk... |
| `vercel-react-native-skills` | React Native and Expo best practices for building performant mobile apps. Use when building React Native components, ... |
| `verify-and-stop` | Prove existing work meets acceptance conditions without expanding scope. Use for validation-only tasks, completion ch... |

---
**Всього активних файлів коду у 48 скілах ядра:** 304
