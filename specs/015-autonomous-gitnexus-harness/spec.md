# SPEC-015: Autonomous GitNexus Graph Ingestion & Live Copilot Agent Harness

* **Status:** Proposed
* **Phase:** Φ1 (Intent Framing)
* **Date:** 2026-09-18
* **Author:** Senior Sovereign Systems Architect
* **Component:** core, server, adapters, ui

## Problem Statement
While Sprint 014 established cross-workspace symbol indexing and air-gapped Ed25519 proofs, full-cycle autonomous ingestion of remote repositories (e.g. `ai-drakon-scaffolder`, `utopia-vault`) requires live background AST synchronization with Utopia DB DAG (:9922). Furthermore, the conversational Copilot must support interactive tool-invocation intents and cross-tenant symbol inspection directly from chat cards.

## Decision Drivers & Invariants
1. **INV-015-01 (Word Budget & Pre-Flight Compaction):** All generated task contexts and compiled rules must remain strictly under 500 words with compilation latency <50 ms.
2. **INV-015-02 (Planar DRAKON Invariant):** Multi-tenant ingestion pipelines and agent harness dispatch flows must guarantee C=0 planarity (zero line crossings).
3. **INV-015-03 (Zero-Dependency Pure Runtime):** Ingestion workers and symbol linkers in `src/` must strictly use the Python 3 Standard Library.
4. **INV-015-04 (Bitemporal DAG Synchronization):** Newly ingested multi-repo symbols must bind to Utopia DB with valid transaction time $T_x$ and valid time $T_v$.
5. **INV-015-05 (Rule-of-2 Skill Crystallization):** Operational sequences repeated $\ge 2$ times must automatically crystallize into persistent `.pi/skills/`.

## Target Deliverables
- Background repository ingestion worker in `src/adapters/gitnexus_graph.py` with Utopia DAG node persistence.
- Copilot chat card symbol navigation bridge in `b-sdd-ui/src/components/CopilotPanel/CopilotStream.tsx`.
- Automated test suite `tests/test_sprint_015_autonomous_harness.py`.
- Executable orchestrator script `run_sprint_015.sh` adhering to the 7-phase HITL protocol.
