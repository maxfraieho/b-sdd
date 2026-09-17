// src/data/mockDrakonSchema.ts
import type { DrakonSchemaIR } from '@/types/drakon';
import type { DrakonDiagram } from '@/types/drakonwidget';

export const CANONICAL_HITL_DRAKON_IR: DrakonSchemaIR = {
  schema_version: '1.0',
  name: 'HITL 7-Phase Execution and Handoff Pipeline',
  params: 'sprint_id: str, context: dict',
  nodes: [
    {
      node_id: 'start',
      node_type: 'headline',
      label: 'Phase 1: Intent Framing (MADR formulation)',
      edges: { down: 'step_phi2', right: null },
      semantic_binding: {
        adr_invariant_id: 'ADR-001-INV-01',
        utopia_entity_id: 'ent_madr_root',
        severity: 'normal',
      },
      x: 0,
      y: 0,
    },
    {
      node_id: 'step_phi2',
      node_type: 'action',
      label: 'Phase 2: Algorithmic Specification (DRAKON-as-Spec modeling)',
      edges: { down: 'cond_phi3', right: null },
      semantic_binding: {
        adr_invariant_id: 'ADR-008-INV-01',
        utopia_entity_id: 'ent_drakon_ir',
        severity: 'normal',
      },
      x: 0,
      y: 2,
    },
    {
      node_id: 'cond_phi3',
      node_type: 'question',
      label: 'Phase 3: Pre-Flight Gate (<500 words, <50ms)?',
      edges: { down: 'step_phi4', right: 'err_phi3_abort' },
      semantic_binding: {
        adr_invariant_id: 'ADR-002-INV-02',
        utopia_entity_id: 'ent_compiler_cache',
        severity: 'normal',
      },
      x: 0,
      y: 4,
    },
    {
      node_id: 'err_phi3_abort',
      node_type: 'action',
      label: 'Compilation failure: Abort sprint and refine ADR token budget',
      edges: { down: 'end_fail', right: null },
      semantic_binding: {
        adr_invariant_id: 'ADR-002-INV-01',
        utopia_entity_id: 'ent_compiler_err',
        severity: 'fatal',
      },
      x: 4,
      y: 4,
    },
    {
      node_id: 'step_phi4',
      node_type: 'action',
      label: 'Phase 4: Phased Code Execution (Leaf action bodies synthesis)',
      edges: { down: 'cond_phi5', right: null },
      semantic_binding: {
        adr_invariant_id: 'ADR-008-INV-02',
        utopia_entity_id: 'ent_llm_gateway_184',
        severity: 'normal',
      },
      x: 0,
      y: 6,
    },
    {
      node_id: 'cond_phi5',
      node_type: 'question',
      label: 'Phase 5: Fitness Gate (Pytest suite passes 100%)?',
      edges: { down: 'cond_phi6', right: 'err_phi5_retry' },
      semantic_binding: {
        adr_invariant_id: 'ADR-007-INV-01',
        utopia_entity_id: 'ent_pytest_harness',
        severity: 'normal',
      },
      x: 0,
      y: 8,
    },
    {
      node_id: 'err_phi5_retry',
      node_type: 'action',
      label: 'Fitness failure: Inject negative invariant vector ΔC and retry',
      edges: { down: 'end_fail', right: null },
      semantic_binding: {
        adr_invariant_id: 'ADR-007-INV-01',
        utopia_entity_id: 'ent_delta_c',
        severity: 'degraded',
      },
      x: 4,
      y: 8,
    },
    {
      node_id: 'cond_phi6',
      node_type: 'question',
      label: 'Phase 6: Human Review Gate (Approved by operator)?',
      edges: { down: 'step_phi7', right: 'err_phi6_reject' },
      semantic_binding: {
        adr_invariant_id: 'ADR-008-INV-03',
        utopia_entity_id: 'ent_hitl_cert',
        severity: 'normal',
      },
      x: 0,
      y: 10,
    },
    {
      node_id: 'err_phi6_reject',
      node_type: 'action',
      label: 'Operator rejection: Trigger Reject & Branch protocol (COW snapshot)',
      edges: { down: 'end_fail', right: null },
      semantic_binding: {
        adr_invariant_id: 'ADR-008-INV-03',
        utopia_entity_id: 'ent_reject_cow',
        severity: 'degraded',
      },
      x: 4,
      y: 10,
    },
    {
      node_id: 'step_phi7',
      node_type: 'action',
      label: 'Phase 7: Distill session into sprint_handoff.json & next_sprint.md',
      edges: { down: 'end_success', right: null },
      semantic_binding: {
        adr_invariant_id: 'ADR-007-INV-02',
        utopia_entity_id: 'ent_handoff_engine',
        severity: 'normal',
      },
      x: 0,
      y: 12,
    },
    {
      node_id: 'end_success',
      node_type: 'end',
      label: 'Sprint completed successfully. Handoff dispatched.',
      edges: { down: null, right: null },
      semantic_binding: {
        adr_invariant_id: 'ADR-007-INV-02',
        utopia_entity_id: 'ent_sprint_done',
        severity: 'normal',
      },
      x: 0,
      y: 14,
    },
    {
      node_id: 'end_fail',
      node_type: 'end',
      label: 'Sprint terminated with failure or branch divergence.',
      edges: { down: null, right: null },
      semantic_binding: {
        adr_invariant_id: 'ADR-007-INV-01',
        utopia_entity_id: 'ent_branch_diverged',
        severity: 'fatal',
      },
      x: 4,
      y: 14,
    },
  ],
  meta: {
    author: 'B-SDD Architect',
    component: 'specs',
  },
};

/**
 * Directly pre-rendered DrakonWidget diagram format for instant canvas rendering.
 */
export const CANONICAL_DRAKON_DIAGRAM: DrakonDiagram = {
  name: 'HITL 7-Phase Execution and Handoff Pipeline',
  access: 'write',
  params: 'sprint_id, context',
  items: {
    b0: {
      type: 'branch',
      branchId: 0,
      content: 'HITL Pipeline',
      one: 'step_phi1',
    },
    step_phi1: {
      type: 'action',
      content: 'Phase 1: Intent Framing (MADR formulation)',
      secondary: '[ADR-001-INV-01]',
      one: 'step_phi2',
    },
    step_phi2: {
      type: 'action',
      content: 'Phase 2: Algorithmic Specification (DRAKON-as-Spec)',
      secondary: '[ADR-008-INV-01]',
      one: 'cond_phi3',
    },
    cond_phi3: {
      type: 'question',
      content: 'Phase 3: Pre-Flight Gate (<500 words, <50ms)?',
      secondary: '[ADR-002-INV-02]',
      one: 'step_phi4',
      two: 'err_phi3_abort',
    },
    err_phi3_abort: {
      type: 'action',
      content: 'Compilation failure: Abort sprint and refine ADR budget',
      secondary: '[ADR-002-INV-01]',
      one: 'end',
    },
    step_phi4: {
      type: 'action',
      content: 'Phase 4: Phased Code Execution (Leaf action bodies synthesis)',
      secondary: '[ADR-008-INV-02]',
      one: 'cond_phi5',
    },
    cond_phi5: {
      type: 'question',
      content: 'Phase 5: Fitness Gate (Pytest suite passes 100%)?',
      secondary: '[ADR-007-INV-01]',
      one: 'cond_phi6',
      two: 'err_phi5_retry',
    },
    err_phi5_retry: {
      type: 'action',
      content: 'Fitness failure: Inject negative invariant vector ΔC and retry',
      secondary: '[ADR-007-INV-01]',
      one: 'end',
    },
    cond_phi6: {
      type: 'question',
      content: 'Phase 6: Human Review Gate (Approved by operator)?',
      secondary: '[ADR-008-INV-03]',
      one: 'step_phi7',
      two: 'err_phi6_reject',
    },
    err_phi6_reject: {
      type: 'action',
      content: 'Operator rejection: Trigger Reject & Branch protocol (COW snapshot)',
      secondary: '[ADR-008-INV-03]',
      one: 'end',
    },
    step_phi7: {
      type: 'action',
      content: 'Phase 7: Distill session into sprint_handoff.json & next_sprint.md',
      secondary: '[ADR-007-INV-02]',
      one: 'end',
    },
    end: {
      type: 'end',
      content: 'Кінець процедури',
    },
  },
};
