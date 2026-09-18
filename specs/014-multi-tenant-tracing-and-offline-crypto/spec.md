# SPEC-014: Multi-Tenant Symbol Tracing, Direct SSE & Air-Gapped Proofs

* **Status:** Ready for Execution
* **Phase:** Φ1 (Intent Framing)
* **Date:** 2026-09-18
* **Author:** Senior Sovereign Systems Architect
* **Component:** core, server, adapters, ui

## Problem Statement
While the workbench supports single-workspace project switching, multi-repo architectures require cross-repository AST symbol navigation across linked workspaces without context degradation. Additionally, LLM streaming latency must be minimized using direct binarized SSE, and review gate verifications must support air-gapped offline environments with self-contained Ed25519 signatures.

## Decision Drivers & Invariants
1. **INV-014-01 (Word Budget & Pre-Flight Compaction):** All generated task contexts and compiled rules must remain strictly under 500 words with compilation latency <50 ms.
2. **INV-014-02 (Planar DRAKON Invariant):** Multi-tenant routing and offline verification flows must guarantee C=0 planarity (zero line crossings).
3. **INV-014-03 (Zero-Dependency Pure Runtime):** All cross-repo AST mapping and Ed25519 signature generators in `src/` must strictly use the Python 3 Standard Library.
4. **INV-014-04 (Air-Gapped Autonomous Proofs):** Review gates in Φ6 must verify artifact cryptographic hashes without requiring outbound network connectivity.
5. **INV-014-05 (Rule-of-2 Skill Crystallization):** Any engineering procedure repeated $\ge 2$ times across sessions must be crystallized into a persistent procedural skill in `.pi/skills/`.

## Target Deliverables
- Cross-repository AST symbol indexer in `src/adapters/gitnexus_graph.py` supporting multi-workspace navigation.
- High-throughput direct SSE streaming bridge in `src/server/workbench_server.py` with latency metrics.
- Air-gapped Ed25519 cryptographic gate validator in `src/core/crypto_verifier.py`.
- Automated test suite `tests/test_sprint_014_multi_tenant.py` with 100% pass rate.
- Executable runner script `run_sprint_014.sh` adhering to the 7-phase HITL protocol.
