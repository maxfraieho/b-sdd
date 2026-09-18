# Sprint 012 Tasks: Utopia DB DAG, Pi Harness Orchestration & Ingestion

- [ ] **TASK-012-1 (Φ1 Intent Framing):** Author ADR-013, behavioral spec, and action-level tasks.
- [ ] **TASK-012-2 (Φ2 Visual Flow):** Validate Sprint 012 planar DRAKON flow (`specs/012-dag-and-pi-harness/logic.drakon.json`) and architecture topology (`structure.drakon.json`).
- [ ] **TASK-012-3 (Φ3 TDD Harness):** Implement unit and invariant tests in `tests/test_sprint_012_dag_and_pi.py`.
- [ ] **TASK-012-4 (Φ4 Utopia DAG Proxy):** Implement `GET /api/utopia/graph` proxy with $T_v/T_t$ filtering in `src/server/workbench_server.py`.
- [ ] **TASK-012-5 (Φ4 Pi Harness Runner):** Implement `PiHarnessRunner` in `src/adapters/pi_harness.py` for headless JSONL RPC and `AGENTS.md` compilation (<500 words).
- [ ] **TASK-012-6 (Φ4 Ingestion Engine):** Implement `POST /api/projects/ingest` for GitNexus AST analysis and base MADR 3.0 synthesis.
- [ ] **TASK-012-7 (Φ4 Frontend Zone D):** Implement `UtopiaDagCanvas.tsx` and dual-mode toggle `[ Cards | DAG View ]` in `TimelineSlider.tsx`.
- [ ] **TASK-012-8 (Φ4 Frontend Copilot):** Integrate Pi Harness SSE streaming into `b-sdd-ui`.
- [ ] **TASK-012-9 (Φ5 Fitness Gates):** Pass 100% pytest suite and compile `npm run build` in `b-sdd-ui`.
- [ ] **TASK-012-10 (Φ6 HITL Gate):** Generate cryptographic review proof in `.context/sprint_012_handoff.json`.
- [ ] **TASK-012-11 (Φ7 Handoff):** Generate `.context/next_sprint.md` and chained orchestrator.
