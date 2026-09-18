# SPEC-018: Sovereign Realtime Agent Collaboration & Distributed Multi-Host Synchronization

* **Status:** Proposed
* **Phase:** Φ1 (Intent Framing)
* **Date:** 2026-09-18
* **Author:** Senior Sovereign Systems Architect
* **Component:** core, server, adapters, ui, cluster

## Problem Statement
Having established cross-repository semantic graph federations (Sprint 016) and transactional CoW mutations (Sprint 017), autonomous coding agents must now coordinate and synchronize in realtime across the distributed sovereign cluster (`192.168.3.161` [AGY/Dev], `192.168.3.184` [Sovereign Runner/Genspark], and `192.168.3.251:9922` [Utopia DB Ledger]). Multi-agent collaboration requires distributed lock leases, realtime SSE heartbeat broadcasting, and optimistic conflict resolution under bitemporal transaction coordinates ($T_x, T_v$).

## Decision Drivers & Invariants
1. **INV-018-01 (Word Budget & Compaction):** Spec and active rules snapshot must strictly remain under 500 words with compilation latency <50 ms.
2. **INV-018-02 (Planar DRAKON Invariant):** Distributed agent state sync and lock arbitration must guarantee C=0 planarity (zero line crossings) and linear skewer X=0.
3. **INV-018-03 (Zero-Dependency Pure Runtime):** Cluster discovery, heartbeat pinging, and lease coordination in `src/` must strictly use Python 3 Standard Library (ADR-002, `urllib`, `socket`, `threading`).
4. **INV-018-04 (Bitemporal Cluster Leases):** All agent collaboration sessions, distributed lock leases, and workspace reservations must register with Utopia DB transaction time $T_x$ and valid time $T_v$.
5. **INV-018-05 (Cryptographic Review Gate):** Final merging requires air-gapped Ed25519 digital signature proof in `.context/sprint_018_handoff.json`.

## Target Deliverables
- Distributed multi-host node synchronization and lease manager in `src/adapters/cluster_sync.py`.
- Server collaboration endpoints: `GET /api/cluster/nodes`, `POST /api/cluster/lease/acquire`, `POST /api/cluster/lease/release` in `src/server/workbench_server.py`.
- Realtime SSE heartbeat stream broadcasting peer agent presence to Astryx Cockpit (`/api/cluster/events`).
- Astryx Cluster Status visualizer in `b-sdd-ui` showing active cluster topology (`.161`, `.184`, `.251`).
- Automated test suite `tests/test_sprint_018_cluster_sync.py`.
- Executable orchestrator script `run_sprint_018.sh` adhering to the 7-phase HITL protocol.
