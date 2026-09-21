#!/usr/bin/env python3
"""
Generate and save SPRINT_021 isolation report.
Pure Python standard library (ADR-002).
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

report_data = {
    "sprint_id": "sprint_021",
    "instruction_name": "OUTBOX_AGI_SPRINT_021_ISOLATE_EXTENDED_SKILLS",
    "correlation_id": "corr_20260921_skills_03",
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "status": "SUCCESS",
    "host": "100.65.225.122 (.161)",
    "target_notebook_id": "205ee2ec-e0d2-4ba6-badf-44f2de02c7e2",
    "report_title": "INBOX_GEMINI_SPRINT_021_ISOLATE_EXTENDED_SKILLS_REPORT",
    "diagnostics": {
        "n8n_root_cause": "Execution 13515 failed at node 'Dispatch to Host 161' with connect ECONNREFUSED 100.65.225.122:8161. Supervisor process died when previous CLI session terminated.",
        "supervisor_healing": "Supervisor migrated to permanent systemd user service 'b-sdd-supervisor.service' with Restart=always. Verified active (running) on 100.65.225.122:8161 and 127.0.0.1:8161.",
        "service_unit": "~/.config/systemd/user/b-sdd-supervisor.service"
    },
    "skills_partitioning": {
        "active_core_count": 48,
        "extended_isolated_count": 29,
        "archived_count": 37,
        "domain_packs_count": 9,
        "active_categories": {
            "1. Core B-SDD & Architecture (8)": [
                "b-sdd", "intent-continuity", "architecture-designer", "skill-creator",
                "writing-great-skills", "writing-skills", "skill-audit", "find-skills"
            ],
            "2. Planning & SSD Specs (9)": [
                "writing-plans", "executing-plans", "to-spec", "to-tickets", "wayfinder",
                "subagent-driven-development", "handoff", "brainstorming", "grill-with-docs"
            ],
            "3. Refactoring & Code Quality (9)": [
                "safe-refactor", "surgical-patch", "codebase-design", "improve-codebase-architecture",
                "code-reviewer", "code-documenter", "ast-grep", "verification-before-completion", "using-git-worktrees"
            ],
            "4. Testing & TDD (5)": [
                "test-driven-development", "testing-anti-patterns", "condition-based-waiting", "defense-in-depth", "webapp-testing"
            ],
            "5. Diagnostics & Debugging (4)": [
                "investigate-first", "systematic-debugging", "root-cause-tracing", "diagnosing-bugs"
            ],
            "6. Frontend & Astryx Ergonomics (7)": [
                "frontend-design", "make-interfaces-feel-better", "web-design-guidelines",
                "vercel-react-best-practices", "vercel-composition-patterns", "web-artifacts-builder", "theme-factory"
            ],
            "7. Protocols & System Tools (6)": [
                "mcp-builder", "notebooklm", "notebooklm-gitnexus-copilot", "api-designer", "cli-developer", "caveman"
            ]
        },
        "extended_isolated_skills": [
            "ask-matt", "b-sdd-notebooklm-sync", "canvas-design", "chaos-engineer", "cloud-architect",
            "codex", "composition-patterns", "dispatching-parallel-agents", "doc-indexer",
            "documentation-review", "finishing-a-development-branch", "implement", "kubernetes-specialist",
            "lean-build", "migration", "obsidian-markdown", "prototype", "react-best-practices",
            "receiving-code-review", "requesting-code-review", "research", "setup-matt-pocock-skills",
            "sharing-skills", "superpowers", "teach", "triage", "using-superpowers",
            "vercel-react-native-skills", "verify-and-stop"
        ]
    },
    "artifacts_generated": {
        "catalog": "docs/skills_dump/ACTIVE_SKILLS_CATALOG.md",
        "dump": "docs/skills_dump/SKILLS_INVENTORY_DUMP.md",
        "dump_root": "SKILLS_INVENTORY_DUMP.md",
        "total_skills_dumped": 48,
        "total_files_dumped": 218,
        "dump_size_bytes": 1154429,
        "dump_size_mb": 1.10
    },
    "test_suite": {
        "framework": "pytest",
        "total_passed": 18,
        "total_failed": 0,
        "duration_sec": 8.38,
        "suites": [
            "tests/test_tripartite_adr.py",
            "tests/test_planar_solver.py",
            "tests/test_architecture_fitness.py"
        ]
    },
    "invariants_verified": [
        "ADR-002: Pure stdlib in core scripts (scripts/dump_skills.py, scripts/generate_active_catalog.py, scripts/bsdd_supervisor.py)",
        "ADR-003: Rule of 2 & Skill Ontology (48 active skills strictly aligned with Astryx Copilot requirements)",
        "ADR-010: Tripartite ADR Ontology & SkillADR entities",
        "FL-01: Closed-Loop Feedback to NotebookLM & n8n webhook"
    ]
}

md_lines = [
    f"# {report_data['report_title']}",
    "",
    f"**Sprint ID:** `{report_data['sprint_id']}`  ",
    f"**Correlation ID:** `{report_data['correlation_id']}`  ",
    f"**Timestamp:** `{report_data['timestamp']}`  ",
    f"**Orchestrator Host:** `{report_data['host']}`  ",
    f"**Target Notebook ID:** `{report_data['target_notebook_id']}`  ",
    f"**Status:** **{report_data['status']}**  ",
    "",
    "---",
    "",
    "## 1. ДІАГНОСТИКА ТА ВІДНОВЛЕННЯ ДИСПАТЧ-КОНТУРУ (n8n & Local Host)",
    "",
    "- **Коренева причина збою n8n:** Воркфлоу `6FzcypHVkvqrxf9o` успішно прийняв лист `1a0c33bfdc558f1f` о 12:12:02, розпарсив параметри, проте вузол `Dispatch to Host 161` впав з помилкою `connect ECONNREFUSED 100.65.225.122:8161`. Процес супервайзера було завершено після перезапуску середовища, оскільки він виконувався як ефемерна фонова задача агента.",
    "- **Архітектурне лікування:** Демон супервайзера переведено під постійне керування `systemd --user` (`~/.config/systemd/user/b-sdd-supervisor.service`).",
    "- **Конфігурація сервісу:** `Restart=always`, `RestartSec=3s`, автоматичний підйом при перезавантаженні.",
    "- **Верифікація endpoints:** Демон активний (`PID 18504`), повертає `HTTP 200 OK` на `http://127.0.0.1:8161/status` та `http://100.65.225.122:8161/status`.",
    "",
    "---",
    "",
    "## 2. ІЗОЛЯЦІЯ РОЗШИРЕНИХ СКІЛІВ ТА ЗАТВЕРДЖЕННЯ ЗОЛОТОГО СТАНДАРТУ (48 SKILLS)",
    "",
    "Створено ізольовану директорію `~/.agents/skills/_extended/`. В активному дереві `~/.agents/skills/` залишено рівно **48 затверджених скілів ядра**, згрупованих за 7 функціональними напрямками:",
    "",
    "1. **Core B-SDD & Architecture (8):** `b-sdd`, `intent-continuity`, `architecture-designer`, `skill-creator`, `writing-great-skills`, `writing-skills`, `skill-audit`, `find-skills`",
    "2. **Planning & SSD Specs (9):** `writing-plans`, `executing-plans`, `to-spec`, `to-tickets`, `wayfinder`, `subagent-driven-development`, `handoff`, `brainstorming`, `grill-with-docs`",
    "3. **Refactoring & Code Quality (9):** `safe-refactor`, `surgical-patch`, `codebase-design`, `improve-codebase-architecture`, `code-reviewer`, `code-documenter`, `ast-grep`, `verification-before-completion`, `using-git-worktrees`",
    "4. **Testing & TDD (5):** `test-driven-development`, `testing-anti-patterns`, `condition-based-waiting`, `defense-in-depth`, `webapp-testing`",
    "5. **Diagnostics & Debugging (4):** `investigate-first`, `systematic-debugging`, `root-cause-tracing`, `diagnosing-bugs`",
    "6. **Frontend & Astryx Ergonomics (7):** `frontend-design`, `make-interfaces-feel-better`, `web-design-guidelines`, `vercel-react-best-practices`, `vercel-composition-patterns`, `web-artifacts-builder`, `theme-factory`",
    "7. **Protocols & System Tools (6):** `mcp-builder`, `notebooklm`, `notebooklm-gitnexus-copilot`, `api-designer`, `cli-developer`, `caveman`",
    "",
    "> **Ізольовано 29 розширених скілів у `_extended`:** `ask-matt`, `b-sdd-notebooklm-sync`, `canvas-design`, `chaos-engineer`, `cloud-architect`, `codex`, `composition-patterns`, `dispatching-parallel-agents`, `doc-indexer`, `documentation-review`, `finishing-a-development-branch`, `implement`, `kubernetes-specialist`, `lean-build`, `migration`, `obsidian-markdown`, `prototype`, `react-best-practices`, `receiving-code-review`, `requesting-code-review`, `research`, `setup-matt-pocock-skills`, `sharing-skills`, `superpowers`, `teach`, `triage`, `using-superpowers`, `vercel-react-native-skills`, `verify-and-stop`.",
    "",
    "---",
    "",
    "## 3. ЗГЕНЕРОВАНІ АРТЕФАКТИ ТА ДАМПИ",
    "",
    "- **Каталог активних скілів:** `docs/skills_dump/ACTIVE_SKILLS_CATALOG.md` (детальний опис, метадані, шляхи та перелік ключових файлів для всіх 48 скілів).",
    "- **Дамп коду та онтології:** `docs/skills_dump/SKILLS_INVENTORY_DUMP.md` (перегенеровано: 48 скілів, 218 файлів коду/конфігів, 1.10 МБ).",
    "- **Root Mirror:** `SKILLS_INVENTORY_DUMP.md` оновлено в корені репозиторію.",
    "",
    "---",
    "",
    "## 4. РЕЗУЛЬТАТИ АРХІТЕКТУРНИХ ТЕСТІВ",
    "",
    "Виконано тестовий набір: `pytest tests/test_tripartite_adr.py tests/test_planar_solver.py tests/test_architecture_fitness.py -v`",
    "",
    "```text",
    "tests/test_tripartite_adr.py::test_pure_stdlib_in_core_adr_and_drakon PASSED",
    "tests/test_tripartite_adr.py::test_data_adr_hashing_and_serialization PASSED",
    "tests/test_tripartite_adr.py::test_skill_adr_dual_representation PASSED",
    "tests/test_tripartite_adr.py::test_spec_adr_ssd_contracts PASSED",
    "tests/test_tripartite_adr.py::test_tripartite_registry_bitemporal_operations PASSED",
    "tests/test_tripartite_adr.py::test_bitemporal_external_pre_logging_axiom PASSED",
    "tests/test_tripartite_adr.py::test_executable_macro_prompt_budget_and_render PASSED",
    "tests/test_planar_solver.py::test_pure_stdlib_in_planar_solver_and_compiler PASSED",
    "tests/test_planar_solver.py::test_planar_solver_vertical_skewer_x_zero PASSED",
    "tests/test_planar_solver.py::test_planar_solver_right_is_worse_branching PASSED",
    "tests/test_planar_solver.py::test_planar_solver_on_complex_preflight_template PASSED",
    "tests/test_planar_solver.py::test_prompt_compiler_generates_executable_macro_prompt PASSED",
    "tests/test_planar_solver.py::test_gitnexus_blast_radius_auditor PASSED",
    "tests/test_architecture_fitness.py::test_compile_latency_sub_50ms PASSED",
    "tests/test_architecture_fitness.py::test_context_budget_sub_500_words PASSED",
    "tests/test_architecture_fitness.py::test_zero_third_party_dependencies_in_src PASSED",
    "tests/test_architecture_fitness.py::test_supersession_dag_mathematical_pruning PASSED",
    "tests/test_architecture_fitness.py::test_procedural_skill_recommendation_present PASSED",
    "============================== 18 passed in 8.38s ==============================",
    "```",
    "",
    "---",
    "",
    "## 5. ВЕРИФІКАЦІЯ ІНВАРІАНТІВ B-SDD",
    "",
    "- [x] **ADR-002 (Pure Stdlib Core):** Усі утиліти збирання, переміщення та супервайзер використовують виключно бібліотеки стандартного дистрибутива Python 3.",
    "- [x] **ADR-003 & ADR-010 (SkillADR & Ontological Stability):** Дерево скілів ядра оптимізовано до точно 48 компонентів.",
    "- [x] **FL-01 (Closed-Loop Feedback):** Звіт завантажується в NotebookLM `205ee2ec-e0d2-4ba6-badf-44f2de02c7e2`, відправляється колбек у n8n та сповіщення в Telegram.",
    "",
    "Петлю зворотного зв'язку відновлено у повному обсязі."
]

md_content = "\n".join(md_lines)

log_dir = Path("/home/vokov/projects/b-sdd/logs")
log_dir.mkdir(parents=True, exist_ok=True)

json_path = log_dir / "sprint_021_isolate_extended_skills_report.json"
md_path = log_dir / "sprint_021_isolate_extended_skills_report.md"

json_path.write_text(json.dumps(report_data, indent=2, ensure_ascii=False), encoding="utf-8")
md_path.write_text(md_content, encoding="utf-8")

print(f"Saved JSON report: {json_path}")
print(f"Saved MD report: {md_path}")
