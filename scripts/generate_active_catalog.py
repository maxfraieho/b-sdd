#!/usr/bin/env python3
"""
Generate ACTIVE_SKILLS_CATALOG.md for the 48 Golden Standard B-SDD skills.
Pure Python standard library (ADR-002).
"""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add scripts directory to sys.path to reuse parse_skill_metadata
sys.path.insert(0, str(Path(__file__).parent.resolve()))
from dump_skills import parse_skill_metadata

skills_dir = Path(os.path.expanduser("~/.agents/skills")).resolve()
ext_dir = skills_dir / "_extended"

categories = {
    "1. Core B-SDD & Architecture (13)": [
        "b-sdd", "b-sdd-sprint-closure", "session-distiller", "intent-continuity", "laya-decision-router", "drakon-compiler", "utopia-intent-ledger",
        "architecture-designer", "skill-creator", "writing-great-skills", "writing-skills", "skill-audit", "find-skills"
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
    "6. Frontend & Astryx Ergonomics (9)": [
        "frontend-design", "astryx-scaffolder", "cloudflare-pages-expert", "make-interfaces-feel-better", "web-design-guidelines",
        "vercel-react-best-practices", "vercel-composition-patterns", "web-artifacts-builder", "theme-factory"
    ],
    "7. Protocols & System Tools (9)": [
        "kindle-release-pipeline", "b-sdd-kindle-docs", "notebooklm", "notebooklm-gitnexus-copilot", "b-sdd-notebooklm-sync",
        "mcp-builder", "api-designer", "cli-developer", "caveman"
    ]
}



def main():
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    total_skills_count = sum(len(skills) for skills in categories.values())

    lines = []
    lines.append(f"# B-SDD ACTIVE CORE SKILLS CATALOG ({total_skills_count} ACTIVE SKILLS)")
    lines.append("")
    lines.append(f"**Дата генерації:** {now_iso}  ")
    lines.append("**Хост оркестрації:** `100.65.225.122` (`192.168.3.161`)  ")
    lines.append(f"**Каталог активних скілів:** `{skills_dir}`  ")
    lines.append(f"**Каталог розширених скілів:** `{ext_dir}`  ")
    lines.append("**Стандарт онтології:** B-SDD Methodology v1.2 / ADR-001..020 (SkillADR)  ")
    lines.append("**Статус:** Затверджено як активний стандарт для Astryx Copilot та ДРАКОН-нод.  ")
    lines.append("")
    lines.append("> [!IMPORTANT]")
    lines.append(f"> Даний каталог містить **{total_skills_count} активних скілів ядра**, включаючи відновлені скіли спринту 027 (kindle-release-pipeline, drakon-compiler, utopia-intent-ledger, astryx-scaffolder).")
    lines.append("> Допоміжні та доменні скіли (29 найменувань) надійно ізольовано в `~/.agents/skills/_extended/`")
    lines.append("> і не перевантажують контекстне вікно планувальника.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📊 Зведений огляд категорій")
    lines.append("")
    lines.append("| № | Категорія | Кількість скілів | Призначення |")
    lines.append("|---|-----------|:----------------:|-------------|")
    lines.append("| 1 | Core B-SDD & Architecture | 11 | Дотримання інваріантів B-SDD, бітемпоральність, ДРАКОН-компілятор, Utopia Ledger |")
    lines.append("| 2 | Planning & SSD Specs | 9 | Планування, декомпозиція задач, передача контексту, парне проєктування |")
    lines.append("| 3 | Refactoring & Code Quality | 9 | Безпечний рефакторинг, патчинг, AST-пошук, рев'ю та git-ізоляція |")
    lines.append("| 4 | Testing & TDD | 5 | TDD-цикли, антипатерни тестування, ліквідація гонок, веб-тести |")
    lines.append("| 5 | Diagnostics & Debugging | 4 | Системне налагодження, пошук кореневих причин, трейсинг дефектів |")
    lines.append("| 6 | Frontend & Astryx Ergonomics | 8 | Інтерфейси Astryx Cockpit, скафолдинг компонентів, React/Vercel патерни |")
    lines.append("| 7 | Protocols & System Tools | 7 | Kindle пайплайн релізів, MCP-сервери, NotebookLM, GitNexus, API та CLI |")
    lines.append(f"| **Σ** | **Всього активних скілів** | **{total_skills_count}** | **Повний замкнений контур AGI** |")
    lines.append("")
    lines.append("---")
    lines.append("")

    total_files_core = 0

    for cat_title, skill_names in categories.items():
        lines.append(f"## {cat_title}")
        lines.append("")
        for s_name in skill_names:
            s_path = skills_dir / s_name
            if not s_path.exists():
                lines.append(f"### ⚠️ `{s_name}` (MISSING)")
                continue
            name, desc, s_type, imm, has_drk, files = parse_skill_metadata(s_path)
            total_files_core += len(files)
            drk_badge = "✅ Присутня" if has_drk else "⚠️ Очікує генерації"
            tax_badge = f"`{s_type}`" + (" 🔒 [IMMUTABLE]" if imm else "")
            lines.append(f"### `{s_name}`")
            lines.append(f"- **Назва:** {name}")
            lines.append(f"- **Таксономія (ADR-015):** {tax_badge}")
            lines.append(f"- **ДРАКОН-схема (Rule of 2):** {drk_badge}")
            lines.append(f"- **Опис:** {desc}")
            lines.append(f"- **Шлях:** `~/.agents/skills/{s_name}`")
            lines.append(f"- **Кількість файлів коду/конфігів:** {len(files)}")
            if files:
                file_rel = [str(f.relative_to(s_path)) for f in files[:8]]
                more = f" (+ {len(files) - 8} more...)" if len(files) > 8 else ""
                lines.append(f"- **Ключові файли:** `{', '.join(file_rel)}`{more}")
            lines.append("")
        lines.append("---")
        lines.append("")

    # Extended section
    ext_skills = sorted([x.name for x in ext_dir.iterdir() if x.is_dir()])
    lines.append(f"## 📦 Ізольовані розширені скіли (`~/.agents/skills/_extended/`) — {len(ext_skills)} скілів")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append("> Ці скіли збережені для специфічних сценаріїв, але ізольовані від основного дерева скілів, щоб оптимізувати розмір контексту та уникнути дублювання патернів.")
    lines.append("")
    lines.append("| Скіл | Призначення / Опис |")
    lines.append("|------|--------------------|")

    for e_name in ext_skills:
        e_path = ext_dir / e_name
        name, desc, s_type, imm, has_drk, files = parse_skill_metadata(e_path)
        short_desc = (desc[:117] + "...") if len(desc) > 120 else desc
        # sanitize pipe characters for markdown table
        short_desc = short_desc.replace("|", "\\|")
        lines.append(f"| `{e_name}` | {short_desc} |")


    lines.append("")
    lines.append("---")
    lines.append(f"**Всього активних файлів коду у 48 скілах ядра:** {total_files_core}")
    lines.append("")

    out_path = Path("/home/vokov/projects/b-sdd/docs/skills_dump/ACTIVE_SKILLS_CATALOG.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {out_path} successfully. Total core files: {total_files_core}")


if __name__ == "__main__":
    main()
