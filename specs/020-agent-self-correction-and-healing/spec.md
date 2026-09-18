# SPEC-020: Sovereign Agent Self-Correction, Automated Rollback Compensation & Self-Healing AST Harness

* **Status:** Proposed
* **Phase:** Φ1 (Intent Framing)
* **Date:** 2026-09-18
* **Author:** Senior Sovereign Systems Architect
* **Component:** core, server, adapters, ui, self_healing

## Problem Statement
When autonomous AI coding agents execute code refactoring, AST transformations, or multi-agent consensus decisions, unexpected syntax errors, type incompatibilities, or architectural invariant breaches can compromise codebase stability. To maintain non-drifting autonomous operation without requiring human intervention, agents require an automated self-healing harness. This harness creates bitemporal transactional checkpoints ($T_x, T_v$), detects AST compilation or test failures, generates targeted syntactic repair hints, and executes instantaneous rollback compensation if fitness thresholds are violated.

## Decision Drivers & Invariants
1. **INV-020-01 (Word Budget & Compaction):** Specification and active rules snapshot must remain strictly under 500 words with compilation latency <50 ms (ADR-008).
2. **INV-020-02 (Planar DRAKON Invariant):** The self-healing compensation flow must guarantee $C=0$ planarity (zero line crossings) and linear skewer $X=0$.
3. **INV-020-03 (Zero-Dependency Pure Runtime):** Checkpointing, diff compensation, AST analysis, and rollback execution in `src/` must strictly use the Python 3 Standard Library (ADR-002, `ast`, `difflib`, `time`, `hashlib`, `threading`).
4. **INV-020-04 (Bitemporal Compensation Invariant):** Every checkpoint, compensation action, and rollback event must record transaction time $T_x$ and valid-time coordinates $T_v$.
5. **INV-020-05 (Cryptographic Review Gate):** Verification and handoff require an air-gapped Ed25519 digital signature manifest in `.context/sprint_020_handoff.json`.

## Target Deliverables
- Reversible checkpointing and compensation engine in `src/adapters/self_healing_engine.py`.
- HTTP Workbench endpoints: `POST /api/healing/checkpoint`, `POST /api/healing/compensate`, and `GET /api/healing/status` in `src/server/workbench_server.py`.
- Astryx Self-Healing badge and telemetry indicator in `b-sdd-ui/src/components/Topbar.tsx` and Copilot quick prompt pill in `b-sdd-ui/src/components/CopilotPanel/CopilotStream.tsx`.
- Automated test harness in `tests/test_sprint_020_self_healing.py`.
- Executable orchestrator script `run_sprint_020.sh` executing all 7 HITL phases.
