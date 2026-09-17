# SPEC-007: B-SDD Drakon State Bridge & Visual Flow Parity

**Phase:** Φ1 Intent Framing  
**Status:** draft  
**Author:** B-SDD Autonomous Systems Agent  
**Standard References:** ADR-001, ADR-008, ADR-FE-001  
**Word Budget:** <500 words (ADR-002 invariant)  

---

## 1. Intent & Problem Statement
During operator interaction with the `b-sdd-ui` workbench, visual manipulations in `drakonwidget.js` (Zone 2) are decoupled from the React state (`drakonNodes` in `App.tsx`), as `onDiagramChange` only emits console logs (DEF-02). Consequently, schema saves (`handleSaveSpec`) and pseudocode generation (`PseudocodeModal`) execute against stale static data (DEF-03). Additionally, the standard algorithm catalog (`PipelineCatalogModal`) supplies empty node arrays (`schema: { nodes: [] }`), rendering the 'Apply in Studio' action a no-op (DEF-01).

## 2. Formal Specification & Invariants
1. **ADR-001-INV-01 (Single Source of Truth):**
   The canonical DRAKON-IR graph (`DrakonSchemaIR`) represents the definitive truth. Any mutation inside the visual canvas MUST immediately normalize into typed `DrakonNodeIR[]` and update the React application state.
2. **ADR-008-INV-01 (Planar Skewer & Zero Crossings):**
   All inserted nodes MUST adhere to the vertical happy-path skewer ($X = 300$). Branching nodes handling negative/fallback conditions MUST divert strictly to the right ($X > 300$), ensuring zero line intersections ($C = 0$).
3. **Dynamic Pseudocode Synthesis:**
   `PseudocodeModal` MUST construct its AST tree and Python/TypeScript pseudocode directly from the live `drakonNodes` collection rather than fallback constants.
4. **Standard Algorithmic Catalog Parity:**
   The algorithm catalog MUST supply fully defined, non-empty planar graph templates (`bsdd_preflight_pipeline`, `drakon_binary_search`, `rule_of_2_crystallizer`, `utopia_sync_workflow`), enabling one-click loading into the live studio.

## 3. Success Criteria
- [ ] 100% of mutations in `drakonwidget.js` propagate to `drakonNodes`.
- [ ] Clicking 'Apply in Studio' in `PipelineCatalogModal` populates the canvas with $\ge 5$ valid nodes.
- [ ] Pseudocode modal displays newly added or edited nodes immediately without page reload.
- [ ] Unit test suite `tests/test_drakon_bridge_and_catalog.py` passes 100%.
