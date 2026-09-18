# SPEC-013: Astryx Workbench v3 Polish, DRAKON Normalization & Conversational Copilot

* **Status:** Implemented & Verified
* **Phase:** Φ6 (Review Gate) / Φ7 (Handoff)
* **Date:** 2026-09-18
* **Author:** Senior Sovereign Systems Architect
* **Component:** core, server, ui

## Problem Statement
The developer workbench required critical ergonomic and topological remediations: canvas runtime crashes (`TypeError: reading 'tail'`) caused by ungrounded DRAKON diagrams, excessive horizontal telemetry cluttering the Topbar, static right panel logs lacking interactive critique, and unwanted modal popups on page reload (F5 bug).

## Decision Drivers & Invariants
1. **INV-013-01 (Word Budget & Compaction):** Rules snapshot and spec must remain under 500 words with compile latency <50 ms.
2. **INV-013-02 (Planar DRAKON Safety):** `normalizeDrakonDiagram` must guarantee C=0 planarity, X=0 linear skewer, terminal end nodes, and prune dangling pointers before canvas rendering.
3. **INV-013-03 (Ergonomic System Pulse):** Topbar telemetry must be consolidated into an interactive popover with live status for Utopia DB (:9922), LLM Gateway (:18880), Appwrite, and GitHub.
4. **INV-013-04 (Conversational Critique):** Copilot panel must deliver conversational chat bubbles and Architectural Critique Cards for immediate invariant violation warnings.
5. **INV-013-05 (Zero Pip Dependencies):** Server context persistence and handlers in `src/` must strictly use Python 3 Standard Library.

## Target Deliverables
- `normalizeDrakonDiagram` in `b-sdd-ui/src/lib/drakon/ir-bridge.ts` integrated with `DrakonCanvas.tsx`.
- Compact `System Pulse` popover in `Topbar.tsx`.
- Breadcrumb trail and Fullscreen Zen mode (`Maximize2` / `Minimize2`) in `DrakonToolbar.tsx`.
- Conversational chat with Architectural Critique Cards in `CopilotStream.tsx`.
- F5 bug fix (`selectedNodeId = null`) and active project context persistence in `workbench_server.py`.
- 100% test pass rate in pytest suite (88/88) and Cloudflare Pages deployment.
