#!/usr/bin/env python3
"""
B-SDD Frontend (Astryx Cockpit / b-sdd-ui) Codebase Plain Text Dump Synthesizer.
100% Pure Python Standard Library (ADR-002 Compliance).
Generates a structured, self-contained plain text dump optimized for Gemini Spark / Pro
context window understanding of frontend UI development, stages it into the working
NotebookLM MCP directory, and synchronizes with Google NotebookLM SSoT notebook.
"""
import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple

EXCLUDED_DIRS: Set[str] = {
    "node_modules",
    "dist",
    "build",
    ".git",
    ".vscode",
    ".idea",
    "__pycache__",
    ".cache",
}

EXCLUDED_FILES: Set[str] = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lock",
    ".DS_Store",
    "Thumbs.db",
    "drakonwidget.js",
    "drakongen.js",
    "tsconfig.tsbuildinfo",
}

BINARY_EXTENSIONS: Set[str] = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".pdf", ".epub", ".zip", ".tar", ".gz", ".db", ".sqlite",
    ".woff", ".woff2", ".ttf", ".eot"
}

CODE_EXTENSIONS: Set[str] = {
    ".ts", ".tsx", ".js", ".jsx", ".css", ".html",
    ".json", ".env", ".example", ".production"
}

LAYER_ORDER = [
    ("1. Core Types & Backend Contracts (ADR-015/016 Alignment)", [
        "src/lib/backend-types.ts",
        "src/types/adr.ts",
        "src/types/sprint.ts",
        "src/types/specs.ts",
        "src/types/copilot.ts",
        "src/types/drakon.ts",
        "src/types/drakonwidget.d.ts",
    ]),
    ("2. Realtime SSE & API Client Layer", [
        "src/lib/api.ts",
        "src/lib/sse.ts",
        "src/hooks/useCopilotStream.ts",
        "src/hooks/usePhaseRealtime.ts",
        "src/hooks/useTelemetryRealtime.ts",
        "src/hooks/useLiveData.ts",
        "src/hooks/useIsMobile.ts",
    ]),
    ("3. DRAKON Algorithmic Studio & IR Bridge (ADR-008/016)", [
        "src/lib/drakon/ir-bridge.ts",
        "src/lib/drakon/pseudocode.ts",
        "src/lib/drakon/themeAdapter.ts",
        "src/lib/drakon/adapter.ts",
        "src/lib/crypto/signer.ts",
        "src/components/DrakonStudio/DrakonCanvas.tsx",
        "src/components/DrakonStudio/VisualFlowCanvas.tsx",
        "src/components/DrakonStudio/DrakonToolbar.tsx",
        "src/components/DrakonStudio/DrakonIconPalette.tsx",
        "src/components/DrakonStudio/LogicStructureSwitcher.tsx",
        "src/components/DrakonStudio/NodeInspector.tsx",
        "src/components/DrakonStudio/NodeInspectorModal.tsx",
        "src/components/DrakonStudio/PseudocodeModal.tsx",
    ]),
    ("4. Application Shell, Navigation & Layout", [
        "index.html",
        "src/main.tsx",
        "src/App.tsx",
        "src/components/Topbar.tsx",
        "src/components/ProjectSwitcherModal.tsx",
        "src/components/MobileNavigation.tsx",
        "src/components/MobilePhaseView.tsx",
        "src/components/MobileRadarView.tsx",
        "src/components/PhaseStepper.tsx",
    ]),
    ("5. Astryx Cockpit Panels, Drawers & Invariant Gates", [
        "src/components/ReviewGateModal.tsx",
        "src/components/InvariantDrawer.tsx",
        "src/components/TelemetryDrawer.tsx",
        "src/components/AdrLibraryModal.tsx",
        "src/components/AdrReaderModal.tsx",
        "src/components/PipelineCatalogModal.tsx",
        "src/components/boundaries/AstryxZoneBoundary.tsx",
        "src/components/astryx/primitives.tsx",
        "src/components/BitemporalRadar/UtopiaDagCanvas.tsx",
        "src/components/BitemporalRadar/TimelineSlider.tsx",
        "src/components/BitemporalRadar/AdrListCard.tsx",
        "src/components/CopilotPanel/CopilotStream.tsx",
        "src/components/CopilotPanel/ContextBadges.tsx",
        "src/components/CopilotPanel/TokenGauge.tsx",
        "src/components/TasksPanel/TasksDrawer.tsx",
    ]),
    ("6. Mock Data & Telemetric Fixtures", [
        "src/data/mockAdrs.ts",
        "src/data/mockSprints.ts",
        "src/data/mockDrakonSchema.ts",
    ]),
    ("7. Styling, Headers & Build Infrastructure", [
        "src/index.css",
        "public/_headers",
        "public/_redirects",
        "vite.config.ts",
        "tailwind.config.js",
        "tsconfig.json",
        "package.json",
        ".env.example",
        ".env.production",
        "PHASE3_INTEGRATION.md",
    ]),
]


def build_preamble(ui_dir: Path) -> str:
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"""# B-SDD UI ARCHITECTURE & SOURCE CODE DUMP (ASTRYX COCKPIT)
===============================================================================
Source Directory : {ui_dir.resolve()}
Target Consumer  : Gemini Spark / Gemini Pro 1.5/2.0 in Google NotebookLM
Generated At     : {now_str}
Project Role     : Astryx Cockpit Frontend & B-SDD Operator Workbench
Application URL  : https://b-sdd-ui.pages.dev (Cloudflare Pages)
Topology Link    : Local Engine (.161:8765, :8161) | Utopia DB / Laya (.251) | Aggregator (.184)
===============================================================================

## 1. ARCHITECTURAL PRIMER FOR GEMINI SPARK
The Astryx Cockpit (`b-sdd-ui`) is the sovereign visual interface of the B-SDD (Behavior &
Specification-Driven Development) framework. It bridges operator intent with sovereign
cluster execution (.161, .184, .251, Pixel 7 Laya).

### Core Architectural Pillars:
1. **Tripartite Ontology (ADR-015 / ADR-016)**:
   - System Skills vs Project Skills segregation (`backend-types.ts`, `InvariantDrawer.tsx`).
   - Core system skills are immutable (`immutable: true`) and cannot be deleted or mutated by UI actions.
   - Dual representation: Formal Algorithmic Pseudocode alongside DRAKON Planar Graphs ($X=0, C=0$).

2. **DrakonStudio Visual Algorithmic Canvas**:
   - Web canvas renderer for DRAKON diagrams (`src/components/DrakonStudio/`).
   - Real-time Intermediate Representation (IR) bridge (`src/lib/drakon/ir-bridge.ts`).
   - Isomorphic Algorithmic Pseudocode generator (`src/lib/drakon/pseudocode.ts`).
   - Strict planar layout: Main spine along vertical skewer ($X=0$), error/rejection branches at $X=4.0$.

3. **Bitemporal Radar & Utopia DB DAG**:
   - Visualizes two-dimensional time: Assertion Time ($Tx$) and Validity Time ($Vt$).
   - DAG dependency rendering for active vs superseded ADRs (`src/components/BitemporalRadar/`).

4. **Fast-Path Diff Risk Gatekeeper (Sprint 030)**:
   - Evaluates pre-commit diff risk across three gates: Safety, Architectural Invariants, Word Budget.
   - Rendered via `src/components/ReviewGateModal.tsx` before code can transition to commit phase.

5. **Real-time Telemetry & Edge Cognition (Pixel 7 Laya / System 1)**:
   - Realtime streaming via Server-Sent Events (SSE) (`src/lib/sse.ts`, `src/hooks/useTelemetryRealtime.ts`).
   - Edge inference offloading metrics (sub-40ms latency gauge, token savings).

6. **Network & Deployment Isolation**:
   - Deployed on Cloudflare Pages (`https://b-sdd-ui.pages.dev`).
   - Public headers (`public/_headers`) configure CORS for LAN sovereign ports:
     - `http://192.168.3.161:8765` (B-SDD Workbench Server)
     - `http://192.168.3.161:8161` (Local API Engine)
     - `http://192.168.3.251:9623` (Laya Edge Gateway)
===============================================================================
"""


def build_directory_tree(ui_dir: Path, files: List[Path]) -> str:
    lines = [f"{ui_dir.name}/"]
    rel_paths = sorted([f.relative_to(ui_dir) for f in files])
    seen_dirs: Set[Path] = set()

    for rel_path in rel_paths:
        for parent in reversed(rel_path.parents):
            if parent != Path(".") and parent not in seen_dirs:
                indent = "  " * len(parent.parts)
                lines.append(f"{indent}├── {parent.name}/")
                seen_dirs.add(parent)
        indent = "  " * len(rel_path.parts)
        lines.append(f"{indent}├── {rel_path.name}")

    return "\n".join(lines)


def collect_ui_files(ui_dir: Path) -> List[Path]:
    collected: List[Path] = []
    for root, dirs, files in os.walk(ui_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]
        for fname in sorted(files):
            if fname in EXCLUDED_FILES or fname.startswith("."):
                continue
            p = Path(root) / fname
            if p.suffix.lower() in BINARY_EXTENSIONS:
                continue
            collected.append(p)
    return sorted(collected)


def order_files_by_layers(ui_dir: Path, all_files: List[Path]) -> List[Tuple[str, List[Path]]]:
    ordered_groups: List[Tuple[str, List[Path]]] = []
    claimed: Set[Path] = set()

    file_map: Dict[str, Path] = {}
    for f in all_files:
        rel = str(f.relative_to(ui_dir))
        file_map[rel] = f

    for layer_name, relative_patterns in LAYER_ORDER:
        layer_files: List[Path] = []
        for pat in relative_patterns:
            if pat in file_map and file_map[pat] not in claimed:
                layer_files.append(file_map[pat])
                claimed.add(file_map[pat])
        if layer_files:
            ordered_groups.append((layer_name, layer_files))

    # Catch any remaining files
    unclaimed = [f for f in all_files if f not in claimed]
    if unclaimed:
        ordered_groups.append(("8. Additional Components & Files", unclaimed))

    return ordered_groups


def synthesize_ui_dump(ui_dir: Path, output_file: Path) -> Tuple[int, int]:
    ui_dir = ui_dir.resolve()
    all_files = collect_ui_files(ui_dir)
    layer_groups = order_files_by_layers(ui_dir, all_files)

    preamble = build_preamble(ui_dir)
    tree = build_directory_tree(ui_dir, all_files)

    total_bytes = 0
    file_count = 0

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(preamble)
        out.write("\n## 2. REPOSITORY TREE STRUCTURE\n")
        out.write("```\n")
        out.write(tree)
        out.write("\n```\n\n")

        for layer_name, files in layer_groups:
            out.write(f"\n{'#'*80}\n## LAYER: {layer_name}\n{'#'*80}\n")
            for f in files:
                rel = f.relative_to(ui_dir)
                try:
                    content = f.read_text(encoding="utf-8", errors="replace")
                except Exception as e:
                    content = f"[ERROR READING FILE: {e}]"

                header = f"\n\n{'='*75}\nFILE: {rel} ({len(content)} characters, {len(content.splitlines())} lines)\n{'='*75}\n"
                out.write(header)
                out.write(content)
                out.write("\n")
                file_count += 1

        stats = f"""\n\n{'#'*80}
## SUMMARY STATISTICS
Total UI Files Dumped: {file_count}
Generated At: {datetime.now(timezone.utc).isoformat()}
Target Architecture: Gemini Spark / Gemini Pro 1.5 Context Window
{'#'*80}\n"""
        out.write(stats)

    total_bytes = output_file.stat().st_size
    return file_count, total_bytes


def main():
    parser = argparse.ArgumentParser(description="Astryx Cockpit UI Codebase Dump Synthesizer (Pure Python stdlib)")
    parser.add_argument("--source", type=str, default="b-sdd-ui", help="Path to b-sdd-ui directory")
    parser.add_argument("--output", type=str, default="b-sdd-ui_code_dump.txt", help="Path to output text dump")
    parser.add_argument("--sync-remote", action="store_true", help="Copy dump to host 192.168.3.184 working directory")
    args = parser.parse_args()

    source_dir = Path(args.source)
    output_path = Path(args.output)

    if not source_dir.exists():
        print(f"❌ Error: UI source directory not found: {source_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"🚀 Synthesizing Astryx UI code dump from: {source_dir}")
    print(f"📄 Target output: {output_path}")

    files, bytes_count = synthesize_ui_dump(source_dir, output_path)
    print(f"✅ Generated {output_path.name}: {bytes_count:,} bytes ({bytes_count / (1024*1024):.2f} MB), {files} files.")

    if args.sync_remote:
        print("🌐 Staging dump to remote host 192.168.3.184...")
        remote_dest = "vokov@192.168.3.184:/home/vokov/b-sdd-ui_code_dump.txt"
        remote_agent_dest = "vokov@192.168.3.184:/home/vokov/notebooklm-agent-copilot/b-sdd-ui_code_dump.txt"
        subprocess.run(["scp", "-o", "StrictHostKeyChecking=no", str(output_path), remote_dest], check=True)
        subprocess.run(["scp", "-o", "StrictHostKeyChecking=no", str(output_path), remote_agent_dest], check=True)
        print("✓ Staged to /home/vokov/ and /home/vokov/notebooklm-agent-copilot/ on .184")


if __name__ == "__main__":
    main()
