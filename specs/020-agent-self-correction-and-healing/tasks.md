# Sprint 020 Tasks: Sovereign Agent Self-Correction, Automated Rollback Compensation & Self-Healing AST Harness

- [x] **TASK-020-1 (Φ1 Intent Framing):** Finalize SPEC-020 requirements, compensation protocols, and AST repair schema.
- [x] **TASK-020-2 (Φ2 Visual Flow):** Model and validate planar DRAKON flow (`specs/020-agent-self-correction-and-healing/logic.drakon.json`).
- [x] **TASK-020-3 (Φ3 TDD Harness):** Implement unit and invariant tests in `tests/test_sprint_020_self_healing.py`.
- [x] **TASK-020-4 (Φ4 Self-Healing Engine):** Implement pure stdlib checkpoint manager, diff reverser, and AST healing analyzer in `src/adapters/self_healing_engine.py`.
- [x] **TASK-020-5 (Φ4 Server Endpoints):** Wire `POST /api/healing/checkpoint`, `POST /api/healing/compensate`, and `GET /api/healing/status` into `workbench_server.py`.
- [x] **TASK-020-6 (Φ4 UI Pulse & Copilot):** Add self-healing status indicator in Astryx Topbar and quick prompt pill in CopilotStream.
- [x] **TASK-020-7 (Φ5 Fitness Gates):** Pass 100% pytest suite and compile clean `npm run build` in `b-sdd-ui`.
- [x] **TASK-020-8 (Φ6 Review Gate):** Verify air-gapped Ed25519 review manifest in `.context/sprint_020_handoff.json`.
- [x] **TASK-020-9 (Φ7 Distillation):** Synthesize handoff artifacts and establish next sprint baseline.
