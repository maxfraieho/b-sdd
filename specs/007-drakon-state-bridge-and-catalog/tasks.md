# TASKS: SPEC-007 Drakon State Bridge & Visual Flow Parity

**Parent Spec:** `specs/007-drakon-state-bridge-and-catalog/spec.md`  
**Execution Order:** Sequential (TDD First)  

---

## Task Checklist

- [ ] **task-001 (TDD Test Suite):**
  Create `tests/test_drakon_bridge_and_catalog.py` asserting:
  1. `PipelineCatalogModal` templates contain $\ge 5$ non-empty nodes.
  2. Canvas mutations produce valid `DrakonNodeIR[]` with planar skewer.
  3. Pseudocode generator produces code matching live edited node labels.

- [ ] **task-002 (Catalog Schema Population):**
  Populate `b-sdd-ui/src/components/PipelineCatalogModal.tsx` `DEFAULT_TEMPLATES` with canonical schemas loaded from `src/drakon/templates/*.json`.

- [ ] **task-003 (DrakonStateBridge Engine):**
  Implement `b-sdd-ui/src/lib/drakon/DrakonStateBridge.ts` to subscribe to `drakonwidget.js` DOM events, normalize mutations to `DrakonNodeIR[]`, and verify $C = 0$ planar skewer.

- [ ] **task-004 (App.tsx Reactive Binding):**
  Wire `DrakonCanvas:onDiagramChange` in `b-sdd-ui/src/App.tsx` to update `drakonNodes` state and pass live schema snapshot to `PseudocodeModal`.

- [ ] **task-005 (Automated Fitness Gate & Chaining):**
  Run pytest on `tests/test_drakon_bridge_and_catalog.py` (100% pass required).
  Synthesize `.context/sprint_007_handoff.json` and generate `run_sprint_008.sh`.
