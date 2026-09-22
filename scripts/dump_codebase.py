#!/usr/bin/env python3
"""
B-SDD Codebase Text Dump Synthesizer.
100% Pure Python Standard Library (ADR-002).
Generates a structured, self-contained plain text dump of the codebase
for NotebookLM, Utopia DB, and offline cognitive indexing.
"""
import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Set, Tuple

EXCLUDED_DIRS: Set[str] = {
    ".git",
    ".gitnexus",
    ".gemini",
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
    ".cache",
    "logs",
}

EXCLUDED_FILES: Set[str] = {
    "b-sdd_code_dump.txt",
    "b_sdd_code_dump.txt",
    ".DS_Store",
    "Thumbs.db",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
}

BINARY_EXTENSIONS: Set[str] = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".pdf", ".epub", ".zip", ".tar", ".gz", ".db", ".sqlite",
    ".pyc", ".so", ".dylib", ".bin", ".woff", ".woff2", ".ttf"
}

CODE_EXTENSIONS: Set[str] = {
    ".py", ".sh", ".bash", ".js", ".jsx", ".ts", ".tsx",
    ".json", ".yaml", ".yml", ".toml", ".sql", ".html", ".css",
}

DOCUMENTATION_EXTENSIONS: Set[str] = {
    ".md", ".txt", ".rst", ".adoc"
}


def should_skip_dir(dir_name: str) -> bool:
    return dir_name in EXCLUDED_DIRS or dir_name.startswith(".")


def collect_files(root: Path, code_only: bool = True) -> List[Path]:
    allowed_exts = CODE_EXTENSIONS if code_only else (CODE_EXTENSIONS | DOCUMENTATION_EXTENSIONS)
    files: List[Path] = []
    
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded directories in-place
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]
        
        rel_dir = Path(dirpath).relative_to(root)
        if any(part in EXCLUDED_DIRS for part in rel_dir.parts):
            continue

        for fname in sorted(filenames):
            if fname in EXCLUDED_FILES or fname.startswith("."):
                continue
            
            p = Path(dirpath) / fname
            if p.suffix.lower() in allowed_exts:
                files.append(p)
                
    return sorted(files)


def build_tree_repr(root: Path, files: List[Path]) -> str:
    lines = [f"{root.name}/"]
    paths = [f.relative_to(root) for f in files]
    
    # Simple hierarchy visualization
    seen_dirs: Set[Path] = set()
    for rel_path in paths:
        for parent in reversed(rel_path.parents):
            if parent != Path(".") and parent not in seen_dirs:
                indent = "  " * len(parent.parts)
                lines.append(f"{indent}├── {parent.name}/")
                seen_dirs.add(parent)
        indent = "  " * (len(rel_path.parts))
        lines.append(f"{indent}├── {rel_path.name}")
    return "\n".join(lines[:120]) + ("\n... [структура скорочена]" if len(lines) > 120 else "")


def synthesize_code_dump(root: Path, output_file: Path, code_only: bool = True) -> Tuple[int, int]:
    files = collect_files(root, code_only=code_only)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mode_desc = "Тільки код (без .md/.txt/документації)" if code_only else "Код та документація"
    
    header = f"""# Код проєкту: {root.name}
Згенеровано: {timestamp}
Директорія: {root.resolve()}
Формат: Plain Text
Режим: {mode_desc}
---
## Структура проєкту

{build_tree_repr(root, files)}
---
"""
    
    total_bytes = 0
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(header)
        total_bytes += len(header.encode("utf-8"))
        
        for file_path in files:
            rel_path = file_path.relative_to(root)
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                content = f"[Помилка читання файлу: {e}]"
                
            file_header = f"\n\n{'='*70}\nФайл: {rel_path}\n{'='*70}\n\n"
            out.write(file_header)
            out.write(content)
            total_bytes += len(file_header.encode("utf-8")) + len(content.encode("utf-8"))
            
        stats = f"""\n\n---
## Статистика
- Режим: {mode_desc}
- Оброблено файлів: {len(files)}
- Загальний розмір: {total_bytes:,} байт ({total_bytes / (1024*1024):.2f} MB)
- Дата створення: {timestamp}
"""
        out.write(stats)
        total_bytes += len(stats.encode("utf-8"))
        
    return len(files), total_bytes


def main():
    parser = argparse.ArgumentParser(description="B-SDD Codebase Text Dump Synthesizer (Pure Python Standard Library)")
    parser.add_argument("--source", type=str, default=".", help="Root directory of the project")
    parser.add_argument("--output", type=str, default="b-sdd_code_dump.txt", help="Target output text dump path")
    parser.add_argument("--full", action="store_true", help="Include documentation markdown and txt files")
    
    args = parser.parse_args()
    root_path = Path(args.source).resolve()
    out_path = Path(args.output).resolve()
    
    print(f"📁 Джерело:   {root_path}")
    print(f"📄 Результат: {out_path}")
    print(f"💻 Режим:     {'Повний (з документацією)' if args.full else 'Тільки код'}")
    
    file_count, byte_size = synthesize_code_dump(root_path, out_path, code_only=not args.full)
    print(f"✅ {out_path.name} — {byte_size:,} байт ({byte_size / (1024*1024):.2f} MB), {file_count} файлів.")


if __name__ == "__main__":
    main()
