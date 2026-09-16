// src/data/mockSprints.ts
import type { SprintState, HitlPhase } from '@/types/sprint';
import type { ModelSlot } from '@/types/copilot';

export const INITIAL_HITL_PHASES: HitlPhase[] = [
  {
    id: 'phi_1',
    index: 1,
    symbol: 'Φ1',
    name: 'Intent Framing',
    description: 'MADR formulation with bitemporal horizons in Utopia DB',
    hitlLevel: '100% Operator',
    status: 'completed',
    validationGate: 'Zero conflicts with active ADRs',
  },
  {
    id: 'phi_2',
    index: 2,
    symbol: 'Φ2',
    name: 'Algorithmic Spec',
    description: 'DRAKON-as-Spec modeling (vertical skewer, non-crossing)',
    hitlLevel: '50% Supervision',
    status: 'completed',
    validationGate: 'Topological planarity & semantic bindings',
  },
  {
    id: 'phi_3',
    index: 3,
    symbol: 'Φ3',
    name: 'Pre-Flight Compilation',
    description: 'Deterministic rule compilation (<50ms, <500 words budget)',
    hitlLevel: '0% Automated',
    status: 'completed',
    validationGate: 'Latency < 50ms, Words <= 500, 0 stale ADRs',
  },
  {
    id: 'phi_4',
    index: 4,
    symbol: 'Φ4',
    name: 'Phased Code Execution',
    description: 'Autonomous LLM code synthesis bounded to leaf action bodies',
    hitlLevel: '0% Automated',
    status: 'completed',
    validationGate: 'Control-flow topology immutability locked',
  },
  {
    id: 'phi_5',
    index: 5,
    symbol: 'Φ5',
    name: 'Automated Fitness Gates',
    description: 'Pytest architectural fitness & AST boundary verification',
    hitlLevel: '0% Automated',
    status: 'completed',
    validationGate: '100% test pass rate, 0 external imports in src/',
  },
  {
    id: 'phi_6',
    index: 6,
    symbol: 'Φ6',
    name: 'Human Review Gate',
    description: 'Synchronous blocking review of diffs, AST logs & fitness reports',
    hitlLevel: '100% Chief Architect',
    status: 'running',
    validationGate: 'Cryptographic operator approval or Reject & Branch',
  },
  {
    id: 'phi_7',
    index: 7,
    symbol: 'Φ7',
    name: 'Distillation & Handoff',
    description: 'Transcript noise compaction & atomic handoff generation',
    hitlLevel: '20% Supervision',
    status: 'pending',
    validationGate: 'sprint_handoff.json & next_sprint.md verified',
  },
];

export const MOCK_SPRINT_STATE: SprintState = {
  sprintId: 'sprint-2026-09-16-004',
  projectName: 'B-SDD Framework Core',
  currentPhase: 'phi_6',
  phases: INITIAL_HITL_PHASES,
  fitnessSummary: {
    total: 25,
    passed: 25,
    failed: 0,
    durationSeconds: 18.33,
    astIsolationScore: 100,
    latencyMs: 16.4,
    tokenCount: 476,
  },
  isReviewGateOpen: false,
  deltaC: [],
  handoffPayload: {
    sprint_id: 'sprint-2026-09-16-004',
    next_tasks: [
      'task-007: Connect workbench to local .context/ and Utopia DB on .251',
      'task-008: End-to-end multi-sprint chaining automated verification',
    ],
    launch_command: './run_b_sdd.sh --task "task-007: Connect workbench to local .context/ and Utopia DB on .251."',
    markdown_preview: `### Next Sprint Objective
Connect developer workbench (\`b-sdd-ui\`) to local \`.context/active_rules.md\`, \`intents_cache.sqlite\` and sovereign Utopia DB node on \`192.168.3.251:9922\`.

### Invariants Maintained
- Zero dependency pure stdlib in \`src/\`
- Offline local parity guaranteed without external cloud dependencies`,
  },
};

export const MOCK_MODEL_SLOTS: ModelSlot[] = [
  {
    id: 'agent-proxy',
    name: 'agent-proxy (:18880)',
    endpoint: 'http://192.168.3.184:18880/v1',
    model: 'meta-llama/Llama-3.2-11B-Vision-Instruct',
    description: 'Fast architectural routing & prompt distillation (~0.6s latency)',
    latencyAvg: '620ms',
    active: true,
  },
  {
    id: 'coding-proxy',
    name: 'coding-proxy (:18880)',
    endpoint: 'http://192.168.3.184:18880/v1',
    model: 'Qwen/Qwen2.5-Coder-32B-Instruct',
    description: 'High-precision TypeScript/Python AST synthesis & leaf action coding',
    latencyAvg: '1420ms',
    active: false,
  },
  {
    id: 'reasoning-proxy',
    name: 'reasoning-proxy (:8082)',
    endpoint: 'http://192.168.3.184:8082/v1',
    model: 'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B',
    description: 'Deep mathematical graph validation & bitemporal theorem proving',
    latencyAvg: '3100ms',
    active: false,
  },
];
