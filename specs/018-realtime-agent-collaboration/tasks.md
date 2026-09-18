# Sprint 018 Tasks: Sovereign Realtime Agent Collaboration & Distributed Multi-Host Synchronization

- [ ] **TASK-018-1 (Φ1 Intent Framing):** Finalize SPEC-018 requirements, cluster discovery protocol, and distributed lease model.
- [ ] **TASK-018-2 (Φ2 Visual Flow):** Model and validate planar DRAKON flow (`specs/018-realtime-agent-collaboration/logic.drakon.json`).
- [ ] **TASK-018-3 (Φ3 TDD Harness):** Implement unit and invariant tests in `tests/test_sprint_018_cluster_sync.py`.
- [ ] **TASK-018-4 (Φ4 Cluster Adapter):** Implement pure stdlib cluster discovery and lease manager in `src/adapters/cluster_sync.py`.
- [ ] **TASK-018-5 (Φ4 Server Endpoints):** Wire `GET /api/cluster/nodes`, `POST /api/cluster/lease/acquire`, and `POST /api/cluster/lease/release` into `workbench_server.py`.
- [ ] **TASK-018-6 (Φ4 UI Pulse & Topology):** Add cluster node presence card and active lease badge in Astryx Workbench.
- [ ] **TASK-018-7 (Φ5 Fitness Gates):** Pass 100% pytest suite and compile clean `npm run build` in `b-sdd-ui`.
- [ ] **TASK-018-8 (Φ6 Review Gate):** Verify air-gapped Ed25519 review manifest in `.context/sprint_018_handoff.json`.
- [ ] **TASK-018-9 (Φ7 Distillation):** Synthesize handoff artifacts and establish next sprint baseline.
