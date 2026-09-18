# SPEC-012: Utopia DB DAG View, Pi Harness Orchestration & Dual-Contour Ingestion

* **Status:** Draft
* **Phase:** Φ1 (Intent Framing)
* **Date:** 2026-09-18
* **Author:** B-SDD Sovereign Architect
* **Component:** core, server, ui

## Problem Statement
Developer Cockpit Zone D requires interactive visual DAG exploration of architectural decision dependencies from Utopia DB, replacing static inspection with dynamic bitemporal filtering. Simultaneously, executing engineering tasks requires a sovereign headless harness (@earendil-works/pi) bounded by token budgets (<500 words) and strict leaf action isolation. Finally, onboarding external codebases demands automated AST parsing and initial MADR 3.0 generation.

## Decision Drivers & Invariants
1. **INV-012-01 (Word Budget & Invariant Density):** Generated AGENTS.md and compiled rules must strictly remain under 500 words with deterministic compile latency <50 ms.
2. **INV-012-02 (Planar DRAKON Invariant):** Pipeline workflow must maintain C=0 (zero line crossings) with a strict vertical skewer.
3. **INV-012-03 (Leaf Action Isolation):** Pi Harness is granted implementation access strictly to leaf Action code bodies; mutations to DRAKON graph topology or ADR invariants are prohibited.
4. **INV-012-04 (Bitemporal DAG Pruning):** Utopia DB graph proxy must dynamically filter superseded edges when Valid Time Tv moves into the past.
5. **INV-012-05 (Zero-Dependency Pure Runtime):** All backend proxy, harness runner, and ingestion logic in src/ must strictly use Python 3 Standard Library.

## Target Deliverables
- Proxy endpoint `GET /api/utopia/graph` with bitemporal horizon parameters (valid_time, transaction_time).
- Interactive SVG DAG Canvas (`UtopiaDagCanvas.tsx`) in Zone D with toggle `[ Cards | DAG View ]`.
- `PiHarnessRunner` (`src/adapters/pi_harness.py`) generating `AGENTS.md` and streaming headless JSONL subprocess execution to SSE.
- Brownfield Ingestion Engine (`POST /api/projects/ingest`) extracting AST metrics via GitNexus and scaffolding base MADR 3.0 records.
- Automated test suite `tests/test_sprint_012_dag_and_pi.py` with 100% pass rate.
