#!/usr/bin/env python3
"""
B-SDD Skills Inventory Collector & Markdown Compiler.
100% Pure Python Standard Library.
Collects all available system & user skills from ~/.agents/skills/ into a single
structured, navigation-ready Markdown dump for Utopia DB (SkillADR) and NotebookLM.
"""
import argparse
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

EXCLUDED_DIRS: Set[str] = {
    ".git",
    ".gitnexus",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    "dist",
    "build",
    ".idea",
    ".vscode",
    "assets",
    "cache",
}

EXCLUDED_FILES: Set[str] = {
    ".DS_Store",
    "Thumbs.db",
    ".gitignore",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
}

BINARY_EXTENSIONS: Set[str] = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".pdf", ".epub", ".zip", ".tar", ".gz", ".db", ".sqlite",
    ".pyc", ".so", ".dylib", ".bin", ".woff", ".woff2", ".ttf"
}

ALLOWED_EXTENSIONS: Set[str] = {
    ".md", ".txt", ".py", ".sh", ".bash", ".js", ".ts", ".json",
    ".yaml", ".yml", ".toml", ".sql", ".html", ".css", ".xml",
}


def get_lang_for_ext(ext: str) -> str:
    mapping = {
        ".md": "markdown",
        ".py": "python",
        ".sh": "bash",
        ".bash": "bash",
        ".js": "javascript",
        ".ts": "typescript",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".sql": "sql",
        ".html": "html",
        ".css": "css",
        ".xml": "xml",
        ".txt": "text",
    }
    return mapping.get(ext.lower(), "text")


def parse_skill_metadata(skill_dir: Path) -> Tuple[str, str, List[Path]]:
    """Extracts skill name, description, and list of relevant files."""
    skill_file = skill_dir / "SKILL.md"
    name = skill_dir.name
    desc = "No description provided."

    if skill_file.exists():
        try:
            content = skill_file.read_text(encoding="utf-8", errors="replace")
            fm_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if fm_match:
                fm = fm_match.group(1)
                fm_lines = fm.splitlines()

                name_match = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
                if name_match:
                    name = name_match.group(1).strip().strip("\"'")

                for i, line in enumerate(fm_lines):
                    if line.strip().startswith("description:"):
                        val = line.split("description:", 1)[1].strip()
                        if val in (">", "|", ">-", "|-", ""):
                            desc_lines = []
                            for next_line in fm_lines[i + 1:]:
                                if next_line.startswith("  ") or next_line.startswith("\t"):
                                    desc_lines.append(next_line.strip())
                                else:
                                    break
                            desc = " ".join(desc_lines)
                        else:
                            desc = val.strip("\"'")
                        break
                desc = re.sub(r"\s+", " ", desc)
        except Exception:
            pass

    # Collect valid files
    relevant_files: List[Path] = []
    for root, dirs, files in os.walk(skill_dir):
        dirs[:] = sorted([d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")])
        for f in sorted(files):
            if f in EXCLUDED_FILES or f.startswith("."):
                continue
            ext = Path(f).suffix.lower()
            if ext in BINARY_EXTENSIONS:
                continue
            if ext in ALLOWED_EXTENSIONS or f == "SKILL.md":
                relevant_files.append(Path(root) / f)

    return name, desc, relevant_files


def generate_dump(source_dir: Path, output_file: Path) -> Tuple[int, int, int]:
    start_time = time.time()
    source_dir = Path(source_dir).resolve()
    output_file = Path(output_file).resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    skills_data = []

    # Iterate over top-level items in skills_dir
    for item in sorted(source_dir.iterdir()):
        if item.is_dir() and not item.is_symlink():
            name, desc, files = parse_skill_metadata(item)
            skills_data.append({
                "dir_name": item.name,
                "name": name,
                "description": desc,
                "files": files,
                "path": item
            })

    total_skills = len(skills_data)
    total_files = sum(len(s["files"]) for s in skills_data)
    total_raw_bytes = 0

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

    buf = []
    # ── HEADER ──────────────────────────────────────────────────────────────────
    buf.append("# B-SDD SKILLS INVENTORY & ONTOLOGY DUMP")
    buf.append("")
    buf.append(f"**Згенеровано:** {now_iso}  ")
    buf.append(f"**Хост збірки:** `192.168.3.161` (AntiGravity AGI Orchestrator)  ")
    buf.append(f"**Джерело:** `{source_dir}`  ")
    buf.append(f"**Загальна кількість скілів:** **{total_skills}**  ")
    buf.append(f"**Загальна кількість файлів коду/конфігів:** **{total_files}**  ")
    buf.append(f"**Стандарт онтології:** B-SDD Methodology v1.2 / ADR-001..020 (SkillADR)  ")
    buf.append("")
    buf.append("> [!NOTE]")
    buf.append("> Цей дамп містить повний зріз системних, інфраструктурних та доменних скілів.")
    buf.append("> Призначений для автоматичного семантичного індексування в Google NotebookLM,")
    buf.append("> KùzuDB/GitNexus та генерації нод ДРАКОН-схем в Astryx Cockpit.")
    buf.append("")
    buf.append("---")
    buf.append("")

    # ── TABLE OF CONTENTS ───────────────────────────────────────────────────────
    buf.append("## Таблиця-Каталог Скілів (Skills Catalog)")
    buf.append("")
    buf.append("| # | Назва скіла | Опис | Склад / Ресурси |")
    buf.append("|---|---|---|---|")

    for i, s in enumerate(skills_data, 1):
        anchor = f"skill-{re.sub(r'[^a-zA-Z0-9_-]', '-', s['name']).lower()}"
        clean_desc = s['description'].replace("|", "\\|").replace("\n", " ")
        if len(clean_desc) > 160:
            clean_desc = clean_desc[:157] + "..."

        # Summarize auxiliary files
        aux_names = [f.relative_to(s['path']).as_posix() for f in s['files'] if f.name != "SKILL.md"]
        if aux_names:
            first_aux = aux_names[0]
            if len(aux_names) > 1:
                res_str = f"`SKILL.md`, `{first_aux}` +{len(aux_names)-1}"
            else:
                res_str = f"`SKILL.md`, `{first_aux}`"
        else:
            res_str = "`SKILL.md` (1 файл)"

        buf.append(f"| {i} | [**{s['name']}**](#{anchor}) | {clean_desc} | {res_str} |")

    buf.append("")
    buf.append("---")
    buf.append("")

    # ── BODY: FULL SKILL CONTENT ────────────────────────────────────────────────
    buf.append("## Повний Вміст Скілів (Full Skills Code & Instructions)")
    buf.append("")

    for i, s in enumerate(skills_data, 1):
        anchor = f"skill-{re.sub(r'[^a-zA-Z0-9_-]', '-', s['name']).lower()}"
        buf.append(f'<a id="{anchor}"></a>')
        buf.append(f"### [{i}/{total_skills}] Скіл: `{s['name']}`")
        buf.append("")
        buf.append(f"**Каталог:** `~/.agents/skills/{s['dir_name']}`  ")
        buf.append(f"**Опис:** {s['description']}  ")
        buf.append(f"**Файлів у складі:** {len(s['files'])}  ")
        buf.append("")

        for fpath in s['files']:
            rel_path = fpath.relative_to(s['path'])
            file_size = fpath.stat().st_size
            total_raw_bytes += file_size
            ext = fpath.suffix.lower()
            lang = get_lang_for_ext(ext)

            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                content = f"[ERROR READING FILE: {e}]"

            # Use 4 backticks for outer fence to avoid collision with 3-backtick markdown blocks
            fence = "````"

            buf.append(f"#### Файл: `{s['dir_name']}/{rel_path}` ({file_size:,} байт)")
            buf.append(f"{fence}{lang}")
            buf.append(content)
            buf.append(f"{fence}")
            buf.append("")

        buf.append("---")
        buf.append("")

    final_text = "\n".join(buf)
    output_file.write_text(final_text, encoding="utf-8")

    duration = time.time() - start_time
    final_size = output_file.stat().st_size
    print(f"[SUCCESS] Skills dump compiled: {output_file}")
    print(f"Stats: {total_skills} skills, {total_files} files, {final_size:,} bytes ({final_size/1024/1024:.2f} MB)")
    print(f"Duration: {duration:.2f}s")

    return total_skills, total_files, final_size


def main():
    parser = argparse.ArgumentParser(description="Compile B-SDD Skills Inventory into Markdown Dump.")
    parser.add_argument(
        "--source",
        default=str(Path.home() / ".agents" / "skills"),
        help="Path to skills source directory (default: ~/.agents/skills)"
    )
    parser.add_argument(
        "--output",
        default="docs/skills_dump/SKILLS_INVENTORY_DUMP.md",
        help="Path to output markdown file"
    )
    args = parser.parse_args()

    generate_dump(Path(args.source), Path(args.output))


if __name__ == "__main__":
    main()
