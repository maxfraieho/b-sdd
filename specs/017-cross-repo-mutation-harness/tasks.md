# Sprint 017 Tasks: Cross-Repository Autonomous Mutation & Transactional Refactoring

- [x] **TASK-017-1 (Φ1 Intent Framing):** Finalize SPEC-017 requirements, CoW mutation boundaries, and action graph.
- [x] **TASK-017-2 (Φ2 Visual Flow):** Model and validate planar DRAKON flow (`specs/017-cross-repo-mutation-harness/logic.drakon.json`).
- [x] **TASK-017-3 (Φ3 TDD Harness):** Implement unit and invariant tests in `tests/test_sprint_017_mutation_harness.py`.
- [x] **TASK-017-4 (Φ4 Mutation Engine):** Implement transactional cross-repo mutation manager with git CoW branches in `src/adapters/gitnexus_graph.py`.
- [x] **TASK-017-5 (Φ4 Server Endpoints):** Wire `POST /api/mutation/refactor` and `POST /api/mutation/rollback` into `workbench_server.py`.
- [x] **TASK-017-6 (Φ4 UI Feedback):** Add refactoring diff preview and transactional rollback trigger in Astryx Workbench.
- [x] **TASK-017-7 (Φ5 Fitness Gates):** Pass 100% pytest suite and compile clean `npm run build` in `b-sdd-ui`.
- [x] **TASK-017-8 (Φ6 Review Gate):** Verify air-gapped Ed25519 review manifest in `.context/sprint_017_handoff.json`.
- [x] **TASK-017-9 (Φ7 Distillation):** Synthesize handoff artifacts and establish next sprint baseline.
