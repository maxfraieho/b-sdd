# SPEC-016: Sovereign Multi-Tenant Cross-Repo Semantic Graph & Utopia DB Query Federation

* **Status:** Proposed
* **Phase:** Φ1 (Intent Framing)
* **Date:** 2026-09-18
* **Author:** Senior Sovereign Systems Architect
* **Component:** core, server, adapters, ui

## Problem Statement
Following the autonomous repository ingestion established in Sprint 015, complex sovereign architectures require cross-repository semantic resolution. When components across different workspaces (e.g. `b-sdd-core`, `b-sdd-ui`, `ai-drakon-scaffolder`, and `utopia-vault`) invoke shared protocols or data models, the system must compute a unified dependency DAG with bitemporal transaction and valid time coordinates ($T_x, T_v$) and support realtime graph queries.

## Decision Drivers & Invariants
1. **INV-016-01 (Word Budget & Compaction):** Spec and active rules snapshot must strictly remain under 500 words with compilation latency <50 ms.
2. **INV-016-02 (Planar DRAKON Invariant):** Cross-repo semantic resolution pipelines must guarantee C=0 planarity (zero line crossings) and linear skewer X=0.
3. **INV-016-03 (Zero-Dependency Pure Runtime):** Core graph resolver and query adapters in `src/` must strictly use the Python 3 Standard Library (ADR-002).
4. **INV-016-04 (Bitemporal DAG Synchronization):** Cross-repo edges and federation mappings must bind to Utopia DB with valid transaction time $T_x$ and valid time $T_v$.
5. **INV-016-05 (HITL Cryptographic Review Gate):** Air-gapped Ed25519 digital signature proof required in `.context/sprint_016_handoff.json` prior to state transitions.

## Target Deliverables
- Cross-repository dependency resolver and query federation in `src/adapters/gitnexus_graph.py`.
- Graph query and cross-repo endpoints: `POST /api/graph/query` and `GET /api/graph/cross-repo-edges` in `src/server/workbench_server.py`.
- Automated test suite `tests/test_sprint_016_semantic_graph.py` verifying invariants and query performance.
- Executable orchestrator script `run_sprint_016.sh` adhering to the 7-phase HITL protocol.
