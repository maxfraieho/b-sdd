# SPEC-019: Sovereign Autonomous Multi-Agent Consensus & Quorum Arbitration

* **Status:** Proposed
* **Phase:** Φ1 (Intent Framing)
* **Date:** 2026-09-18
* **Author:** Senior Sovereign Systems Architect
* **Component:** core, server, adapters, ui, consensus

## Problem Statement
Following the realization of distributed cluster synchronization and lock leases in Sprint 018, autonomous AI coding agents operating across multiple hosts (`.161`, `.184`, `.251`) require a decentralized Byzantine-fault-tolerant consensus mechanism for controversial code mutations, architectural decision approvals, and schema migrations. The cluster requires majority quorum voting ($N \ge 2/3$) with bitemporal ballots ($T_x, T_v$) recorded in the immutable Utopia DB ledger (:9922).

## Decision Drivers & Invariants
1. **INV-019-01 (Word Budget & Compaction):** Spec and active rules snapshot must strictly remain under 500 words with compilation latency <50 ms.
2. **INV-019-02 (Planar DRAKON Invariant):** Multi-agent consensus ballot arbitration must guarantee C=0 planarity (zero line crossings) and linear skewer X=0.
3. **INV-019-03 (Zero-Dependency Pure Runtime):** Quorum computation, ballot hashing, and vote aggregation in `src/` must strictly use the Python 3 Standard Library (ADR-002, `hashlib`, `threading`, `time`).
4. **INV-019-04 (Bitemporal Ballot Invariant):** Every consensus proposal and ballot must register with transaction time $T_x$ and model valid time $T_v$ in Utopia DB.
5. **INV-019-05 (Cryptographic Review Gate):** Final merging requires air-gapped Ed25519 digital signature proof in `.context/sprint_019_handoff.json`.

## Target Deliverables
- Decentralized multi-agent quorum and ballot manager in `src/adapters/consensus_engine.py`.
- Consensus endpoints: `POST /api/consensus/propose`, `POST /api/consensus/vote`, and `GET /api/consensus/proposals` in `src/server/workbench_server.py`.
- Astryx Consensus & Quorum card in UI with real-time voting badges.
- Automated test suite `tests/test_sprint_019_consensus.py`.
- Executable orchestrator script `run_sprint_019.sh` adhering to the 7-phase HITL protocol.
