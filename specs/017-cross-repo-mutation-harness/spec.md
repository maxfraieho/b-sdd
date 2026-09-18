# SPEC-017: Sovereign Cross-Repo Mutation Harness & Transactional Refactoring

* **Status:** Proposed
* **Phase:** Φ1 (Intent Framing)
* **Date:** 2026-09-18
* **Author:** Senior Sovereign Systems Architect
* **Component:** core, server, adapters, ui

## Problem Statement
Having established the multi-tenant cross-repository semantic graph in Sprint 016, autonomous AI coding agents now require safe transactional mutation capabilities across workspaces. Cross-repository changes (e.g. renaming a shared model, updating an API interface, or refactoring an architectural seam) must execute under Copy-on-Write (CoW) git branches with atomic verification and bitemporal rollback in Utopia DB (:9922).

## Decision Drivers & Invariants
1. **INV-017-01 (Word Budget & Compaction):** Spec and active rules snapshot must strictly remain under 500 words with compilation latency <50 ms.
2. **INV-017-02 (Planar DRAKON Invariant):** Cross-repo mutation and atomic verification flows must guarantee C=0 planarity (zero line crossings) and linear skewer X=0.
3. **INV-017-03 (Zero-Dependency Pure Runtime):** Transactional mutation manager and refactoring harness in `src/` must strictly use the Python 3 Standard Library (ADR-002).
4. **INV-017-04 (Bitemporal Transactional Rollback):** All cross-repo mutations must register with Utopia DB transaction time $T_x$ and model valid time $T_v$, allowing zero-data-loss compensation.
5. **INV-017-05 (Cryptographic Review Gate):** Final merging requires air-gapped Ed25519 digital signature proof in `.context/sprint_017_handoff.json`.

## Target Deliverables
- Transactional cross-repo mutation manager in `src/adapters/gitnexus_graph.py` with git CoW isolation.
- Refactoring endpoints: `POST /api/mutation/refactor` and `POST /api/mutation/rollback` in `src/server/workbench_server.py`.
- Automated test suite `tests/test_sprint_017_mutation_harness.py`.
- Executable orchestrator script `run_sprint_017.sh` adhering to the 7-phase HITL protocol.
