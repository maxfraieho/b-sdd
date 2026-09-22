# B-SDD ACTIVE CORE SKILLS CATALOG (53 ACTIVE SKILLS)

**Дата генерації:** 2026-09-22 07:59:55Z  
**Хост оркестрації:** `100.65.225.122` (`192.168.3.161`)  
**Каталог активних скілів:** `/home/vokov/.agents/skills`  
**Каталог розширених скілів:** `/home/vokov/.agents/skills/_extended`  
**Стандарт онтології:** B-SDD Methodology v1.2 / ADR-001..020 (SkillADR)  
**Статус:** Затверджено як активний стандарт для Astryx Copilot та ДРАКОН-нод.  

> [!IMPORTANT]
> Даний каталог містить **53 активних скілів ядра**, включаючи відновлені скіли спринту 027 (kindle-release-pipeline, drakon-compiler, utopia-intent-ledger, astryx-scaffolder).
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
| **Σ** | **Всього активних скілів** | **53** | **Повний замкнений контур AGI** |

---

## 1. Core B-SDD & Architecture (11)

### `b-sdd`
- **Назва:** b-sdd
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Enforces bitemporal architectural invariants, ADR compliance, and pre-flight compilation under the B-SDD framework.
- **Шлях:** `~/.agents/skills/b-sdd`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, b-sdd.drakon.json`

### `intent-continuity`
- **Назва:** intent-continuity
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Enforces non-drifting code implementation backed by active bitemporal architectural rules, ADR compliance, and Utopia DB bitemporal synchronization.
- **Шлях:** `~/.agents/skills/intent-continuity`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, intent-continuity.drakon.json`

### `laya-decision-router`
- **Назва:** laya-decision-router
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Sub-40ms System 1 non-autoregressive decision engine for task classification, prompt guardrails, and typed skill routing.
- **Шлях:** `~/.agents/skills/laya-decision-router`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, laya-decision-router.drakon.json`

### `drakon-compiler`
- **Назва:** drakon-compiler
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Compiles DRAKON visual algorithm diagrams into Intermediate Representation (IR) and executable macro-prompts using planar graph solver (C=0, X=0) and strict skewer alignment.
- **Шлях:** `~/.agents/skills/drakon-compiler`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, drakon-compiler.drakon.json, scripts/compile_drakon.py`

### `utopia-intent-ledger`
- **Назва:** utopia-intent-ledger
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Manages bitemporal WORM ledger transactions, validates tripartite ADR ontology, and executes atomic synchronization with Utopia DB intent store and knowledge graph.
- **Шлях:** `~/.agents/skills/utopia-intent-ledger`
- **Кількість файлів коду/конфігів:** 4
- **Ключові файли:** `SKILL.md, utopia-intent-ledger.drakon.json, scripts/sync_utopia.py, scripts/validate_ontology.py`

### `architecture-designer`
- **Назва:** architecture-designer
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when designing new high-level system architecture, reviewing existing designs, or making architectural decisions. Invoke to create architecture diagrams, write Architecture Decision Records (ADRs), evaluate technology trade-offs, design component interactions, and plan for scalability. Use for system design, architecture review, microservices structuring, ADR authoring, scalability planning, and infrastructure pattern selection — distinct from code-level design patterns or database-only design tasks.
- **Шлях:** `~/.agents/skills/architecture-designer`
- **Кількість файлів коду/конфігів:** 7
- **Ключові файли:** `SKILL.md, architecture-designer.drakon.json, references/adr-template.md, references/architecture-patterns.md, references/database-selection.md, references/nfr-checklist.md, references/system-design.md`

### `skill-creator`
- **Назва:** skill-creator
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.
- **Шлях:** `~/.agents/skills/skill-creator`
- **Кількість файлів коду/конфігів:** 8
- **Ключові файли:** `LICENSE.txt, SKILL.md, skill-creator.drakon.json, references/output-patterns.md, references/workflows.md, scripts/init_skill.py, scripts/package_skill.py, scripts/quick_validate.py`

### `writing-great-skills`
- **Назва:** writing-great-skills
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Reference for writing and editing skills well — the vocabulary and principles that make a skill predictable.
- **Шлях:** `~/.agents/skills/writing-great-skills`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `GLOSSARY.md, SKILL.md, writing-great-skills.drakon.json`

### `writing-skills`
- **Назва:** writing-skills
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when creating new skills, editing existing skills, or verifying skills work before deployment - applies TDD to process documentation by testing with subagents before writing, iterating until bulletproof against rationalization
- **Шлях:** `~/.agents/skills/writing-skills`
- **Кількість файлів коду/конфігів:** 4
- **Ключові файли:** `SKILL.md, anthropic-best-practices.md, persuasion-principles.md, writing-skills.drakon.json`

### `skill-audit`
- **Назва:** skill-audit
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when auditing the skills installed in ~/.claude/skills/ for structure quality, metadata completeness, and instruction usefulness. Run after installing new skills, before sharing skills upstream, or during periodic skill maintenance.
- **Шлях:** `~/.agents/skills/skill-audit`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, skill-audit.drakon.json`

### `find-skills`
- **Назва:** find-skills
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.
- **Шлях:** `~/.agents/skills/find-skills`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, find-skills.drakon.json`

---

## 2. Planning & SSD Specs (9)

### `writing-plans`
- **Назва:** writing-plans
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when design is complete and you need detailed implementation tasks for engineers with zero codebase context - creates comprehensive implementation plans with exact file paths, complete code examples, and verification steps assuming engineer has minimal domain knowledge
- **Шлях:** `~/.agents/skills/writing-plans`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, writing-plans.drakon.json`

### `executing-plans`
- **Назва:** executing-plans
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when partner provides a complete implementation plan to execute in controlled batches with review checkpoints - loads plan, reviews critically, executes tasks in batches, reports for review between batches
- **Шлях:** `~/.agents/skills/executing-plans`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, executing-plans.drakon.json`

### `to-spec`
- **Назва:** to-spec
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Turn the current conversation into a spec and publish it to the project issue tracker — no interview, just synthesis of what you've already discussed.
- **Шлях:** `~/.agents/skills/to-spec`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, to-spec.drakon.json`

### `to-tickets`
- **Назва:** to-tickets
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the configured tracker — edges as text in a local file, or native blocking links on a real tracker.
- **Шлях:** `~/.agents/skills/to-tickets`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, to-tickets.drakon.json`

### `wayfinder`
- **Назва:** wayfinder
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Plan a huge chunk of work — more than one agent session can hold — as a shared map of investigation tickets on your issue tracker, and resolve them one at a time until the way to the destination is clear.
- **Шлях:** `~/.agents/skills/wayfinder`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, wayfinder.drakon.json`

### `subagent-driven-development`
- **Назва:** subagent-driven-development
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when executing implementation plans with independent tasks in the current session - dispatches fresh subagent for each task with code review between tasks, enabling fast iteration with quality gates
- **Шлях:** `~/.agents/skills/subagent-driven-development`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, subagent-driven-development.drakon.json`

### `handoff`
- **Назва:** handoff
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Compact the current conversation into a handoff document for another agent to pick up.
- **Шлях:** `~/.agents/skills/handoff`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, handoff.drakon.json`

### `brainstorming`
- **Назва:** brainstorming
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when creating or developing, before writing code or implementation plans - refines rough ideas into fully-formed designs through collaborative questioning, alternative exploration, and incremental validation. Don't use during clear 'mechanical' processes
- **Шлях:** `~/.agents/skills/brainstorming`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, brainstorming.drakon.json`

### `grill-with-docs`
- **Назва:** grill-with-docs
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go.
- **Шлях:** `~/.agents/skills/grill-with-docs`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, grill-with-docs.drakon.json`

---

## 3. Refactoring & Code Quality (9)

### `safe-refactor`
- **Назва:** safe-refactor
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Restructure code while preserving behavior. Use for extraction, consolidation, ownership moves, or cleanup where verification must bracket structural edits.
- **Шлях:** `~/.agents/skills/safe-refactor`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, safe-refactor.drakon.json, agents/openai.yaml`

### `surgical-patch`
- **Назва:** surgical-patch
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Fix bugs and small behavior changes at the narrowest responsible layer. Use when regression proof, preserved surrounding behavior, and task-relevant tests matter.
- **Шлях:** `~/.agents/skills/surgical-patch`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, surgical-patch.drakon.json, agents/openai.yaml`

### `codebase-design`
- **Назва:** codebase-design
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Shared vocabulary for designing deep modules. Use when the user wants to design or improve a module's interface, find deepening opportunities, decide where a seam goes, make code more testable or AI-navigable, or when another skill needs the deep-module vocabulary.
- **Шлях:** `~/.agents/skills/codebase-design`
- **Кількість файлів коду/конфігів:** 4
- **Ключові файли:** `DEEPENING.md, DESIGN-IT-TWICE.md, SKILL.md, codebase-design.drakon.json`

### `improve-codebase-architecture`
- **Назва:** improve-codebase-architecture
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick.
- **Шлях:** `~/.agents/skills/improve-codebase-architecture`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `HTML-REPORT.md, SKILL.md, improve-codebase-architecture.drakon.json`

### `code-reviewer`
- **Назва:** code-reviewer
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Analyzes code diffs and files to identify bugs, security vulnerabilities (SQL injection, XSS, insecure deserialization), code smells, N+1 queries, naming issues, and architectural concerns, then produces a structured review report with prioritized, actionable feedback. Use when reviewing pull requests, conducting code quality audits, identifying refactoring opportunities, or checking for security issues. Invoke for PR reviews, code quality checks, refactoring suggestions, review code, code quality. Complements specialized skills (security-reviewer, test-master) by providing broad-scope review across correctness, performance, maintainability, and test coverage in a single pass.
- **Шлях:** `~/.agents/skills/code-reviewer`
- **Кількість файлів коду/конфігів:** 8
- **Ключові файли:** `SKILL.md, code-reviewer.drakon.json, references/common-issues.md, references/feedback-examples.md, references/receiving-feedback.md, references/report-template.md, references/review-checklist.md, references/spec-compliance-review.md`

### `code-documenter`
- **Назва:** code-documenter
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Generates, formats, and validates technical documentation — including docstrings, OpenAPI/Swagger specs, JSDoc annotations, doc portals, and user guides. Use when adding docstrings to functions or classes, creating API documentation, building documentation sites, or writing tutorials and user guides. Invoke for OpenAPI/Swagger specs, JSDoc, doc portals, getting started guides.
- **Шлях:** `~/.agents/skills/code-documenter`
- **Кількість файлів коду/конфігів:** 10
- **Ключові файли:** `SKILL.md, code-documenter.drakon.json, references/api-docs-fastapi-django.md, references/api-docs-nestjs-express.md, references/coverage-reports.md, references/documentation-systems.md, references/interactive-api-docs.md, references/python-docstrings.md` (+ 2 more...)

### `ast-grep`
- **Назва:** ast-grep
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Guide for writing ast-grep rules to perform structural code search and analysis. Use when users need to search codebases using Abstract Syntax Tree (AST) patterns, find specific code structures, or perform complex code queries that go beyond simple text search. This skill should be used when users ask to search for code patterns, find specific language constructs, or locate code with particular structural characteristics.
- **Шлях:** `~/.agents/skills/ast-grep`
- **Кількість файлів коду/конфігів:** 4
- **Ключові файли:** `README.md, SKILL.md, ast-grep.drakon.json, references/rule_reference.md`

### `verification-before-completion`
- **Назва:** verification-before-completion
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
- **Шлях:** `~/.agents/skills/verification-before-completion`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, verification-before-completion.drakon.json`

### `using-git-worktrees`
- **Назва:** using-git-worktrees
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when starting feature work that needs isolation from current workspace or before executing implementation plans - creates isolated git worktrees with smart directory selection and safety verification
- **Шлях:** `~/.agents/skills/using-git-worktrees`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, using-git-worktrees.drakon.json`

---

## 4. Testing & TDD (5)

### `test-driven-development`
- **Назва:** test-driven-development
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when implementing any feature or bugfix, before writing implementation code - write the test first, watch it fail, write minimal code to pass; ensures tests actually verify behavior by requiring failure first
- **Шлях:** `~/.agents/skills/test-driven-development`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, test-driven-development.drakon.json`

### `testing-anti-patterns`
- **Назва:** testing-anti-patterns
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when writing or changing tests, adding mocks, or tempted to add test-only methods to production code - prevents testing mock behavior, production pollution with test-only methods, and mocking without understanding dependencies
- **Шлях:** `~/.agents/skills/testing-anti-patterns`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, testing-anti-patterns.drakon.json`

### `condition-based-waiting`
- **Назва:** condition-based-waiting
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when tests have race conditions, timing dependencies, or inconsistent pass/fail behavior - replaces arbitrary timeouts with condition polling to wait for actual state changes, eliminating flaky tests from timing guesses
- **Шлях:** `~/.agents/skills/condition-based-waiting`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, condition-based-waiting.drakon.json, example.ts`

### `defense-in-depth`
- **Назва:** defense-in-depth
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when invalid data causes failures deep in execution, requiring validation at multiple system layers - validates at every layer data passes through to make bugs structurally impossible
- **Шлях:** `~/.agents/skills/defense-in-depth`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, defense-in-depth.drakon.json`

### `webapp-testing`
- **Назва:** webapp-testing
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
- **Шлях:** `~/.agents/skills/webapp-testing`
- **Кількість файлів коду/конфігів:** 7
- **Ключові файли:** `LICENSE.txt, SKILL.md, webapp-testing.drakon.json, examples/console_logging.py, examples/element_discovery.py, examples/static_html_automation.py, scripts/with_server.py`

---

## 5. Diagnostics & Debugging (4)

### `investigate-first`
- **Назва:** investigate-first
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Diagnose ambiguous failures before editing. Use for unknown causes, intermittent behavior, performance regressions, or investigations needing evidence-ranked hypotheses.
- **Шлях:** `~/.agents/skills/investigate-first`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, investigate-first.drakon.json, agents/openai.yaml`

### `systematic-debugging`
- **Назва:** systematic-debugging
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes - four-phase framework (root cause investigation, pattern analysis, hypothesis testing, implementation) that ensures understanding before attempting solutions
- **Шлях:** `~/.agents/skills/systematic-debugging`
- **Кількість файлів коду/конфігів:** 7
- **Ключові файли:** `CREATION-LOG.md, SKILL.md, systematic-debugging.drakon.json, test-academic.md, test-pressure-1.md, test-pressure-2.md, test-pressure-3.md`

### `root-cause-tracing`
- **Назва:** root-cause-tracing
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when errors occur deep in execution and you need to trace back to find the original trigger - systematically traces bugs backward through call stack, adding instrumentation when needed, to identify source of invalid data or incorrect behavior
- **Шлях:** `~/.agents/skills/root-cause-tracing`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, find-polluter.sh, root-cause-tracing.drakon.json`

### `diagnosing-bugs`
- **Назва:** diagnosing-bugs
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Diagnosis loop for hard bugs and performance regressions. Use when the user says "diagnose"/"debug this", or reports something broken/throwing/failing/slow.
- **Шлях:** `~/.agents/skills/diagnosing-bugs`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, diagnosing-bugs.drakon.json, scripts/hitl-loop.template.sh`

---

## 6. Frontend & Astryx Ergonomics (8)

### `frontend-design`
- **Назва:** frontend-design
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code that avoids generic AI aesthetics.
- **Шлях:** `~/.agents/skills/frontend-design`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `LICENSE.txt, SKILL.md, frontend-design.drakon.json`

### `astryx-scaffolder`
- **Назва:** astryx-scaffolder
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Scaffolds Astryx Cockpit UI components, interactive DRAKON canvas widgets, real-time telemetry panels, and multi-tenant operator workbench interfaces.
- **Шлях:** `~/.agents/skills/astryx-scaffolder`
- **Кількість файлів коду/конфігів:** 3
- **Ключові файли:** `SKILL.md, astryx-scaffolder.drakon.json, scripts/scaffold_component.py`

### `make-interfaces-feel-better`
- **Назва:** make-interfaces-feel-better
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Design engineering principles for making interfaces feel polished. Use when building UI components, reviewing frontend code, implementing animations, hover states, shadows, borders, typography, micro-interactions, enter/exit animations, or any visual detail work. Triggers on UI polish, design details, "make it feel better", "feels off", stagger animations, border radius, optical alignment, font smoothing, tabular numbers, image outlines, box shadows.
- **Шлях:** `~/.agents/skills/make-interfaces-feel-better`
- **Кількість файлів коду/конфігів:** 6
- **Ключові файли:** `SKILL.md, animations.md, make-interfaces-feel-better.drakon.json, performance.md, surfaces.md, typography.md`

### `web-design-guidelines`
- **Назва:** web-design-guidelines
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".
- **Шлях:** `~/.agents/skills/web-design-guidelines`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, web-design-guidelines.drakon.json`

### `vercel-react-best-practices`
- **Назва:** vercel-react-best-practices
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** React and Next.js performance optimization guidelines from Vercel Engineering. This skill should be used when writing, reviewing, or refactoring React/Next.js code to ensure optimal performance patterns. Triggers on tasks involving React components, Next.js pages, data fetching, bundle optimization, or performance improvements.
- **Шлях:** `~/.agents/skills/vercel-react-best-practices`
- **Кількість файлів коду/конфігів:** 74
- **Ключові файли:** `AGENTS.md, README.md, SKILL.md, vercel-react-best-practices.drakon.json, rules/advanced-effect-event-deps.md, rules/advanced-event-handler-refs.md, rules/advanced-init-once.md, rules/advanced-use-latest.md` (+ 66 more...)

### `vercel-composition-patterns`
- **Назва:** vercel-composition-patterns
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** React composition patterns that scale. Use when refactoring components with boolean prop proliferation, building flexible component libraries, or designing reusable APIs. Triggers on tasks involving compound components, render props, context providers, or component architecture. Includes React 19 API changes.
- **Шлях:** `~/.agents/skills/vercel-composition-patterns`
- **Кількість файлів коду/конфігів:** 12
- **Ключові файли:** `AGENTS.md, README.md, SKILL.md, vercel-composition-patterns.drakon.json, rules/architecture-avoid-boolean-props.md, rules/architecture-compound-components.md, rules/patterns-children-over-render-props.md, rules/patterns-explicit-variants.md` (+ 4 more...)

### `web-artifacts-builder`
- **Назва:** web-artifacts-builder
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX artifacts.
- **Шлях:** `~/.agents/skills/web-artifacts-builder`
- **Кількість файлів коду/конфігів:** 5
- **Ключові файли:** `LICENSE.txt, SKILL.md, web-artifacts-builder.drakon.json, scripts/bundle-artifact.sh, scripts/init-artifact.sh`

### `theme-factory`
- **Назва:** theme-factory
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. There are 10 pre-set themes with colors/fonts that you can apply to any artifact that has been creating, or can generate a new theme on-the-fly.
- **Шлях:** `~/.agents/skills/theme-factory`
- **Кількість файлів коду/конфігів:** 13
- **Ключові файли:** `LICENSE.txt, SKILL.md, theme-factory.drakon.json, themes/arctic-frost.md, themes/botanical-garden.md, themes/desert-rose.md, themes/forest-canopy.md, themes/golden-hour.md` (+ 5 more...)

---

## 7. Protocols & System Tools (7)

### `kindle-release-pipeline`
- **Назва:** kindle-release-pipeline
- **Таксономія (ADR-015):** `SYSTEM_SKILL` 🔒 [IMMUTABLE]
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Autonomous pipeline for compiling B-SDD architecture documentation, ADRs, and sprint summaries into standard EPUB 3.0 ebooks and dispatching them directly to Amazon Kindle (tukroschu@kindle.com) via verified Gmail API / n8n Kindle Dispatcher without CC.
- **Шлях:** `~/.agents/skills/kindle-release-pipeline`
- **Кількість файлів коду/конфігів:** 9
- **Ключові файли:** `SKILL.md, kindle-release-pipeline.drakon.json, scripts/bsdd_to_kindle.py, scripts/dispatch_kindle_book.sh, scripts/dispatch_on_184.sh, scripts/dossier_to_kindle.py, scripts/kindle_digest.py, scripts/md_to_epub.py` (+ 1 more...)

### `mcp-builder`
- **Назва:** mcp-builder
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).
- **Шлях:** `~/.agents/skills/mcp-builder`
- **Кількість файлів коду/конфігів:** 11
- **Ключові файли:** `LICENSE.txt, SKILL.md, mcp-builder.drakon.json, reference/evaluation.md, reference/mcp_best_practices.md, reference/node_mcp_server.md, reference/python_mcp_server.md, scripts/connections.py` (+ 3 more...)

### `notebooklm`
- **Назва:** notebooklm
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Complete API for Google NotebookLM - full programmatic access including features not in the web UI. Create notebooks, add sources, generate all artifact types, download in multiple formats. Activates on explicit /notebooklm or intent like "create a podcast about X
- **Шлях:** `~/.agents/skills/notebooklm`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, notebooklm.drakon.json`

### `notebooklm-gitnexus-copilot`
- **Назва:** notebooklm-gitnexus-copilot
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Token-efficient AI pair programming methodology using Full-Code PDF aggregation, GitNexus code intelligence graph, and Google NotebookLM MCP. Supports atomic work packet execution where NotebookLM drafts exact code snippets from 100% full-code context. Use for refactoring, feature implementation, and architectural reviews.
- **Шлях:** `~/.agents/skills/notebooklm-gitnexus-copilot`
- **Кількість файлів коду/конфігів:** 2
- **Ключові файли:** `SKILL.md, notebooklm-gitnexus-copilot.drakon.json`

### `api-designer`
- **Назва:** api-designer
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when designing REST or GraphQL APIs, creating OpenAPI specifications, or planning API architecture. Invoke for resource modeling, versioning strategies, pagination patterns, error handling standards.
- **Шлях:** `~/.agents/skills/api-designer`
- **Кількість файлів коду/конфігів:** 7
- **Ключові файли:** `SKILL.md, api-designer.drakon.json, references/error-handling.md, references/openapi.md, references/pagination.md, references/rest-patterns.md, references/versioning.md`

### `cli-developer`
- **Назва:** cli-developer
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Use when building CLI tools, implementing argument parsing, or adding interactive prompts. Invoke for parsing flags and subcommands, displaying progress bars and spinners, generating bash/zsh/fish completion scripts, CLI design, shell completions, and cross-platform terminal applications using commander, click, typer, or cobra.
- **Шлях:** `~/.agents/skills/cli-developer`
- **Кількість файлів коду/конфігів:** 7
- **Ключові файли:** `SKILL.md, cli-developer.drakon.json, references/design-patterns.md, references/go-cli.md, references/node-cli.md, references/python-cli.md, references/ux-patterns.md`

### `caveman`
- **Назва:** caveman
- **Таксономія (ADR-015):** `PROJECT_SKILL`
- **ДРАКОН-схема (Rule of 2):** ✅ Присутня
- **Опис:** Ultra-compressed communication mode. Cuts output tokens 65% (measured) by speaking like caveman while keeping full technical accuracy. Supports intensity levels: lite, full (default), ultra, wenyan-lite, wenyan-full, wenyan-ultra. Use when user says "caveman mode", "talk like caveman", "use caveman", "less tokens", "be brief", or invokes /caveman. Also auto-triggers when token efficiency is requested.
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
**Всього активних файлів коду у 48 скілах ядра:** 287
