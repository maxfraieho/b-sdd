# Implementation Plan: Spec 004

## Phase 1: Dynamic Handoff Engine
- Implement `.context/sprint_handoff.json` generation in `src/core/session_distiller.py`.
- Add `handoff` command to `src/cli/main.py`.
- Update `run_b_sdd.sh` with `--auto-chain` flag.
- Write fitness tests for handoff integrity (`tests/test_handoff.py`).

## Phase 2: DRAKON Grammar & Parser (Drakon-as-Spec)
- Create `src/drakon/parser.py` (100% Python stdlib) to parse DRAKON diagrams (.drn and JSON AST).
- Validate "skewer" verticality and non-crossing constraints.
- Map visual decision boxes to ADR invariant IDs.
- Generate deterministic prompt constraints from DRAKON flows.

## Phase 3: Developer Workbench Integration
- Port visual graph components from `ai-drakon-scaffolder`.
- Build lightweight local web dashboard (`b-sdd-ui`) displaying:
  - Temporal ADR Knowledge Graph.
  - Interactive DRAKON flowchart viewer.
  - Multi-sprint cockpit with one-click session launcher.
