/* =========================================================
   B-SDD Workbench · mock data (mirrors b-sdd-ui/src/data/*)
   Kept 1:1 with backend DTOs in b-sdd-ui/src/lib/backend-types.ts
   ========================================================= */
window.BSDD = (function () {
  // -------------------- Project & workspace --------------------
  const PROJECT = {
    id: 'b-sdd',
    name: 'B-SDD Framework Core',
    path: '/home/vokov/projects/b-sdd',
    branch: 'main',
    commit: 'bffae39',
    dirty_files: 0,
    description: 'Bitemporal Spec-Driven Development Framework',
    stats: { specs: 4, adrs: 8, tests: 36, utopia_kb: '01a08474-…-0001' },
  };

  // -------------------- Specs / tasks --------------------
  const SPECS = [
    {
      id: '001-compiler-core',
      title: 'Spec 001 · Compiler Core',
      path: 'specs/001-compiler-core',
      tasks_count: 6,
      completed_count: 6,
      percent: 100,
      has_diagram: false,
      diagrams: [],
      tasks: [],
    },
    {
      id: '002-utopia-bitemporal',
      title: 'Spec 002 · Utopia Bitemporal',
      path: 'specs/002-utopia-bitemporal',
      tasks_count: 5,
      completed_count: 5,
      percent: 100,
      has_diagram: false,
      diagrams: [],
      tasks: [],
    },
    {
      id: '003-skill-lifecycle',
      title: 'Spec 003 · Skill Lifecycle',
      path: 'specs/003-skill-lifecycle',
      tasks_count: 4,
      completed_count: 4,
      percent: 100,
      has_diagram: false,
      diagrams: [],
      tasks: [],
    },
    {
      id: '004-multi-session-handoff-and-drakon',
      title: 'Spec 004 · Multi-Session Handoff & DRAKON',
      path: 'specs/004-multi-session-handoff-and-drakon',
      tasks_count: 8,
      completed_count: 8,
      percent: 100,
      has_diagram: true,
      diagrams: ['logic.drakon.json'],
      tasks: [
        { id: 'task-001', title: 'Extend SessionDistiller with handoff payload synthesis', completed: true },
        { id: 'task-002', title: 'Wire main.py handoff sub-command in CLI', completed: true },
        { id: 'task-003', title: 'Author architectural contract ADR-007', completed: true },
        { id: 'task-004', title: 'Author architectural contract ADR-008', completed: true },
        { id: 'task-005', title: 'Implement pure-stdlib DRAKON schema validator', completed: true },
        { id: 'task-006', title: 'Port React/Vite visualization workbench', completed: true },
        { id: 'task-007', title: 'Connect workbench to local .context/ and Utopia DB', completed: true },
        { id: 'task-008', title: 'End-to-end multi-sprint chaining automated tests', completed: true },
      ],
    },
  ];

  // -------------------- ADRs (bitemporal) --------------------
  const ADRS = [
    {
      id: 'ADR-001',
      title: 'Bitemporal Intent Graph & Immutable Audit Ledger',
      status: 'accepted',
      component: 'core',
      date: '2026-09-01',
      valid_from: '2026-09-01T00:00:00Z',
      valid_to: null,
      tx_time: '2026-09-01T12:00:00Z',
      supersedes: null,
      superseded_by: null,
      file_path: 'docs/adr/ADR-001-bitemporal-intent-graph.md',
      invariants: [
        { id: 'ADR-001-INV-01', statement: 'Rules where valid_to < NOW must never be compiled into the active agent context.', severity: 'mandatory', component: 'core' },
        { id: 'ADR-001-INV-02', statement: 'No historical intent records may be physically deleted from the database.', severity: 'critical', component: 'core' },
      ],
      context: 'Autonomous coding agents need a consistent view of historical and active rules without drift.',
      decision_outcome: 'Adopt bitemporal modeling (Tv, Tt) in Utopia DB with directed DAG supersession.',
    },
    {
      id: 'ADR-002',
      title: 'Deterministic Pre-Flight Compilation (<500 words, <50ms)',
      status: 'accepted', component: 'core', date: '2026-09-02',
      valid_from: '2026-09-02T00:00:00Z', valid_to: null, tx_time: '2026-09-02T10:30:00Z',
      supersedes: null, superseded_by: null,
      file_path: 'docs/adr/ADR-002-deterministic-pre-flight-compilation.md',
      invariants: [
        { id: 'ADR-002-INV-01', statement: 'Warm pre-flight compilation latency must strictly remain under 50 milliseconds.', severity: 'critical', component: 'core' },
        { id: 'ADR-002-INV-02', statement: 'Compiled active rules snapshot must strictly remain under 500 words budget.', severity: 'critical', component: 'core' },
      ],
      context: 'Large unstructured context windows cause hallucination and stochastic LLM drift.',
      decision_outcome: 'Build an ultra-fast in-memory compiler that compresses ADRs into a sub-500 word snapshot.',
    },
    {
      id: 'ADR-003',
      title: 'Procedural Skill Lifecycle & The Rule of 2',
      status: 'accepted', component: 'skills', date: '2026-09-03',
      valid_from: '2026-09-03T00:00:00Z', valid_to: null, tx_time: '2026-09-03T14:15:00Z',
      supersedes: null, superseded_by: null,
      file_path: 'docs/adr/ADR-003-procedural-skill-lifecycle-and-rule-of-2.md',
      invariants: [
        { id: 'ADR-003-INV-01', statement: 'Operational workflows repeated >= 2 times must be crystallized into an agent skill.', severity: 'mandatory', component: 'skills' },
        { id: 'ADR-003-INV-02', statement: 'Skills must follow the standard agent skill format (SKILL.md with YAML frontmatter).', severity: 'mandatory', component: 'skills' },
      ],
      context: 'Repetitive ad-hoc tasks waste tokens and result in inconsistent execution standards.',
      decision_outcome: 'Formalize autonomous skill crystallization via skill-creator under the Rule of 2.',
    },
    {
      id: 'ADR-004',
      title: 'Static AST Impact Graph Routing via GitNexus',
      status: 'accepted', component: 'analysis', date: '2026-09-05',
      valid_from: '2026-09-05T00:00:00Z', valid_to: null, tx_time: '2026-09-05T09:00:00Z',
      supersedes: null, superseded_by: null,
      file_path: 'docs/adr/ADR-004-ast-impact-graph-routing.md',
      invariants: [
        { id: 'ADR-004-INV-01', statement: 'Domain resolution from file paths must execute in sub-millisecond time (<1ms).', severity: 'recommended', component: 'analysis' },
      ],
      context: 'Knowing which ADR applies to which file requires AST-level call-graph mapping.',
      decision_outcome: 'Index code changes with the GitNexus AST topological graph.',
    },
    {
      id: 'ADR-005',
      title: 'Pure Python Standard Library Core Runtime',
      status: 'accepted', component: 'core', date: '2026-09-07',
      valid_from: '2026-09-07T00:00:00Z', valid_to: null, tx_time: '2026-09-07T11:45:00Z',
      supersedes: null, superseded_by: null,
      file_path: 'docs/adr/ADR-005-automated-architectural-fitness-gates.md',
      invariants: [
        { id: 'ADR-005-INV-01', statement: 'Zero external third-party dependencies in src/ runtime code.', severity: 'critical', component: 'core' },
      ],
      context: 'Dependency hell on edge nodes causes setup friction and expands the security attack surface.',
      decision_outcome: 'Enforce 100% Python standard library for all src/ core and adapter components.',
    },
    {
      id: 'ADR-006',
      title: 'Sovereign VPC Architecture & Offline Local Parity',
      status: 'accepted', component: 'infra', date: '2026-09-10',
      valid_from: '2026-09-10T00:00:00Z', valid_to: null, tx_time: '2026-09-10T16:00:00Z',
      supersedes: null, superseded_by: null,
      file_path: 'docs/adr/ADR-006-multi-harness-session-distillation-and-context-compaction.md',
      invariants: [
        { id: 'ADR-006-INV-01', statement: 'Developer workbench must function in 100% standalone offline mode on local repository.', severity: 'mandatory', component: 'infra' },
      ],
      context: 'Enterprise air-gapped deployments cannot depend on public cloud SaaS services.',
      decision_outcome: 'Host Utopia DB (.251) and LLM Gateway (.184) inside sovereign VPC with local cache parity.',
    },
    {
      id: 'ADR-007',
      title: 'Multi-Session Sprint Chaining & Dynamic Handoff',
      status: 'accepted', component: 'handoff', date: '2026-09-14',
      valid_from: '2026-09-14T00:00:00Z', valid_to: null, tx_time: '2026-09-14T13:20:00Z',
      supersedes: null, superseded_by: null,
      file_path: 'docs/adr/ADR-007-multi-session-sprint-chaining-and-handoff.md',
      invariants: [
        { id: 'ADR-007-INV-01', statement: 'Downstream sprints cannot start if upstream fitness gates fail.', severity: 'critical', component: 'handoff' },
        { id: 'ADR-007-INV-02', statement: 'Dynamic handoffs must synthesize next_sprint.md and sprint_handoff.json atomically.', severity: 'mandatory', component: 'handoff' },
      ],
      context: 'Multi-turn agent chats degrade as token windows fill with debugging debris.',
      decision_outcome: 'Implement dynamic handoff engine chaining fresh sprints with distilled context.',
    },
    {
      id: 'ADR-008',
      title: 'DRAKON Visual Algorithmic Logic & Developer Workbench Integration',
      status: 'accepted', component: 'specs', date: '2026-09-16',
      valid_from: '2026-09-16T00:00:00Z', valid_to: null, tx_time: '2026-09-16T17:00:00Z',
      supersedes: null, superseded_by: null,
      file_path: 'docs/adr/ADR-008-drakon-visual-logic-and-developer-workbench.md',
      invariants: [
        { id: 'ADR-008-INV-01', statement: 'DRAKON schemes must satisfy the 4 canonical rules: vertical skewer, right-is-worse, zero crossings, silhouette.', severity: 'critical', component: 'specs' },
        { id: 'ADR-008-INV-02', statement: 'Visual nodes must maintain verifiable semantic bindings to active ADR invariant IDs.', severity: 'mandatory', component: 'specs' },
        { id: 'ADR-008-INV-03', statement: 'Transitions through Phase 6 Human Review Gate require synchronous operator sign-off.', severity: 'critical', component: 'specs' },
      ],
      context: 'Natural language specs cause agent drift; informal flowcharts lack a mathematical grammar.',
      decision_outcome: 'Port visual workbench from ai-drakon-scaffolder leveraging stepan-mitkin/drakonwidget.',
    },
  ];

  // -------------------- Sample ADR file content (full-text reader) --------------------
  const ADR_CONTENT = {
    'ADR-008': `# ADR-008 · DRAKON Visual Algorithmic Logic & Developer Workbench Integration

- **Status:** Accepted
- **Date:** 2026-09-16
- **Component:** specs
- **Supersedes:** —
- **Valid From:** 2026-09-16T00:00:00Z

## Context

Natural language specifications alone lead to autonomous LLM agents drifting from
architectural intent. Informal flowcharts (Mermaid, PlantUML) lack a mathematical
grammar strong enough for machine consumption. The B-SDD framework demands a
canonical visual language whose planar topology is verifiable and whose nodes can
carry semantic bindings to bitemporal invariants.

## Decision

Adopt **DRAKON-as-Spec** using the canonical \`stepan-mitkin/drakonwidget\`
runtime as the DRAKON rendering & editing engine. Each visual node MUST carry a
semantic binding to an active ADR invariant ID resolvable through Utopia DB.

## Invariants

- **ADR-008-INV-01** *(critical)*: DRAKON schemes MUST satisfy the four
  canonical rules: vertical skewer, right-is-worse, zero crossings, silhouette.
- **ADR-008-INV-02** *(mandatory)*: Visual nodes MUST maintain verifiable
  semantic bindings to active ADR invariant IDs.
- **ADR-008-INV-03** *(critical)*: Transitions through Phase 6 Human Review Gate
  REQUIRE synchronous operator sign-off before Φ7 handoff dispatch.

## Consequences

**Positive:** Machine-verifiable specifications, planar topology guarantees
correct execution branches, tight binding to Utopia DB invariants.

**Negative:** Editor learning curve for operators unfamiliar with the DRAKON
notation. Mitigated by the built-in 17-icon palette and inline text editing.

## Related

- ADR-001 · Bitemporal Intent Graph
- ADR-007 · Multi-Session Sprint Chaining
`,
    'ADR-007': `# ADR-007 · Multi-Session Sprint Chaining & Dynamic Handoff

- **Status:** Accepted
- **Date:** 2026-09-14
- **Component:** handoff

## Context

Long agent conversations degrade catastrophically as token windows fill with
debugging debris, retracted assumptions and superseded intent. Each fresh
sprint should start from distilled state, not raw transcript history.

## Decision

Implement a dynamic handoff engine that emits \`sprint_handoff.json\` and
\`next_sprint.md\` atomically at Φ7. Downstream sprints receive only distilled
context and cannot start unless upstream fitness gates pass.

## Invariants

- **ADR-007-INV-01** *(critical)*: Downstream sprints CANNOT start if upstream
  fitness gates fail.
- **ADR-007-INV-02** *(mandatory)*: Dynamic handoffs MUST synthesize
  \`next_sprint.md\` and \`sprint_handoff.json\` atomically.
`,
  };
  // fill in a lightweight placeholder for the rest
  ADRS.forEach((adr) => {
    if (!ADR_CONTENT[adr.id]) {
      ADR_CONTENT[adr.id] = `# ${adr.id} · ${adr.title}

- **Status:** ${adr.status}
- **Date:** ${adr.date}
- **Component:** ${adr.component}

## Context
${adr.context}

## Decision
${adr.decision_outcome}

## Invariants
${adr.invariants.map((i) => `- **${i.id}** *(${i.severity || 'mandatory'})*: ${i.statement}`).join('\n')}
`;
    }
  });

  // -------------------- HITL phases & sprint state --------------------
  const PHASES = [
    { id: 'phi_1', index: 1, symbol: 'Φ1', name: 'Intent Framing',            description: 'MADR formulation with bitemporal horizons in Utopia DB',   hitlLevel: '100% Operator',     status: 'completed', validationGate: 'Zero conflicts with active ADRs' },
    { id: 'phi_2', index: 2, symbol: 'Φ2', name: 'Algorithmic Spec',          description: 'DRAKON-as-Spec modeling (vertical skewer, non-crossing)',  hitlLevel: '50% Supervision',   status: 'completed', validationGate: 'Topological planarity & semantic bindings' },
    { id: 'phi_3', index: 3, symbol: 'Φ3', name: 'Pre-Flight Compilation',    description: 'Deterministic rule compilation (<50ms, <500w budget)',     hitlLevel: '0% Automated',      status: 'completed', validationGate: 'Latency < 50ms · Words ≤ 500 · 0 stale ADRs' },
    { id: 'phi_4', index: 4, symbol: 'Φ4', name: 'Phased Code Execution',     description: 'Autonomous LLM synthesis bounded to leaf action bodies',   hitlLevel: '0% Automated',      status: 'completed', validationGate: 'Control-flow topology immutability locked' },
    { id: 'phi_5', index: 5, symbol: 'Φ5', name: 'Automated Fitness Gates',   description: 'Pytest architectural fitness & AST boundary verification', hitlLevel: '0% Automated',      status: 'completed', validationGate: '100% pass rate · 0 external imports in src/' },
    { id: 'phi_6', index: 6, symbol: 'Φ6', name: 'Human Review Gate',         description: 'Synchronous blocking review of diffs, AST logs & fitness', hitlLevel: '100% Chief Arch.',  status: 'running',   validationGate: 'Cryptographic operator approval or Reject & Branch' },
    { id: 'phi_7', index: 7, symbol: 'Φ7', name: 'Distillation & Handoff',    description: 'Transcript compaction & atomic handoff generation',        hitlLevel: '20% Supervision',   status: 'pending',   validationGate: 'sprint_handoff.json & next_sprint.md verified' },
  ];

  const SPRINT_STATE = {
    sprintId: 'sprint-2026-09-16-004',
    projectName: 'B-SDD Framework Core',
    currentPhase: 'phi_6',
    phases: PHASES,
    fitnessSummary: {
      total: 25, passed: 25, failed: 0,
      durationSeconds: 18.33,
      astIsolationScore: 100,
      latencyMs: 16.4,
      tokenCount: 476,
      coverage: 94.2,
    },
    isReviewGateOpen: false,
    deltaC: [],
    handoffPayload: {
      sprint_id: 'sprint-2026-09-16-004',
      next_tasks: [
        'task-009: Migrate b-sdd-ui to Astryx design system components',
        'task-010: Wire live SSE stream from Copilot to Utopia DB writes',
      ],
      launch_command: './run_next_sprint.sh --task "task-009: Migrate b-sdd-ui to Astryx design system components"',
      markdown_preview: `### Next Sprint Objective
Migrate \`b-sdd-ui\` from raw Tailwind primitives to the canonical
\`@astryxdesign/core\` component library, per the ΔC-ASTRYX-OMISSION
directive filed at 2026-09-16.

### Invariants Maintained
- 100% offline parity (ADR-006-INV-01)
- Bitemporal DAG integrity (ADR-001-INV-01)
- <500-word active rules budget (ADR-002-INV-02)`,
    },
  };

  // -------------------- LLM slots --------------------
  const MODEL_SLOTS = [
    { id: 'agent-proxy',     name: 'agent-proxy',     port: 18880, model: 'meta-llama/Llama-3.2-11B-Vision', description: 'Fast architectural routing & prompt distillation', latencyAvg: 620,  active: false },
    { id: 'coding-proxy',    name: 'coding-proxy',    port: 18880, model: 'Qwen/Qwen2.5-Coder-32B-Instruct',  description: 'High-precision TS/Py AST synthesis & leaf coding', latencyAvg: 1420, active: true  },
    { id: 'reasoning-proxy', name: 'reasoning-proxy', port: 8082,  model: 'DeepSeek-R1-Distill-Qwen-32B',      description: 'Deep graph validation & bitemporal proving',       latencyAvg: 3100, active: false },
  ];

  // -------------------- DRAKON diagram (canonical HITL) --------------------
  // Ready for both SVG mock renderer and real DrakonWidget
  const DRAKON_DIAGRAM = {
    name: 'HITL 7-Phase Execution & Handoff Pipeline',
    access: 'write',
    params: 'sprint_id, context',
    items: {
      b0: { type: 'branch', branchId: 0, content: 'HITL Pipeline', one: 'step_phi1' },
      step_phi1:      { type: 'action',   content: 'Phase 1: Intent Framing (MADR formulation)',                secondary: '[ADR-001-INV-01]', one: 'step_phi2' },
      step_phi2:      { type: 'action',   content: 'Phase 2: Algorithmic Specification (DRAKON-as-Spec)',        secondary: '[ADR-008-INV-01]', one: 'cond_phi3' },
      cond_phi3:      { type: 'question', content: 'Phase 3: Pre-Flight Gate (<500 words · <50ms)?',             secondary: '[ADR-002-INV-02]', one: 'step_phi4', two: 'err_phi3_abort' },
      err_phi3_abort: { type: 'action',   content: 'Compilation failure: abort sprint & refine ADR budget',      secondary: '[ADR-002-INV-01]', one: 'end' },
      step_phi4:      { type: 'action',   content: 'Phase 4: Phased Code Execution (leaf action synthesis)',     secondary: '[ADR-008-INV-02]', one: 'cond_phi5' },
      cond_phi5:      { type: 'question', content: 'Phase 5: Fitness Gate (Pytest suite 100%)?',                 secondary: '[ADR-007-INV-01]', one: 'cond_phi6', two: 'err_phi5_retry' },
      err_phi5_retry: { type: 'action',   content: 'Fitness failure: inject ΔC negative invariant vector',       secondary: '[ADR-007-INV-01]', one: 'end' },
      cond_phi6:      { type: 'question', content: 'Phase 6: Human Review Gate (approved by operator)?',         secondary: '[ADR-008-INV-03]', one: 'step_phi7', two: 'err_phi6_reject' },
      err_phi6_reject:{ type: 'action',   content: 'Operator rejection: trigger Reject & Branch (COW snapshot)', secondary: '[ADR-008-INV-03]', one: 'end' },
      step_phi7:      { type: 'action',   content: 'Phase 7: Distill session → sprint_handoff.json / next_sprint.md', secondary: '[ADR-007-INV-02]', one: 'end' },
      end:            { type: 'end',      content: 'Кінець процедури' },
    },
  };

  // -------------------- DRAKON 17-icon palette (with Ukrainian labels) --------------------
  const DRAKON_ICONS = [
    { type: 'action',    label: 'Дія',       group: 'core',    hint: 'Executable step' },
    { type: 'question',  label: 'Умова',     group: 'core',    hint: 'Binary decision' },
    { type: 'select',    label: 'Вибір',     group: 'core',    hint: 'Multi-way branch' },
    { type: 'case',      label: 'Варіант',   group: 'core',    hint: 'Case leg' },
    { type: 'branch',    label: 'Гілка',     group: 'core',    hint: 'Silhouette branch header' },
    { type: 'end',       label: 'Кінець',    group: 'core',    hint: 'Terminal / return' },
    { type: 'input',     label: 'Ввід',      group: 'io',      hint: 'Input parameter' },
    { type: 'output',    label: 'Вивід',     group: 'io',      hint: 'Output value' },
    { type: 'shelf',     label: 'Полиця',    group: 'io',      hint: 'Storage / shelf' },
    { type: 'process',   label: 'Процес',    group: 'control', hint: 'Sub-procedure call' },
    { type: 'timer',     label: 'Таймер',    group: 'control', hint: 'Timed guard' },
    { type: 'pause',     label: 'Пауза',     group: 'control', hint: 'Wait / delay' },
    { type: 'duration',  label: 'Тривалість',group: 'control', hint: 'Duration window' },
    { type: 'foreach',   label: 'Цикл',      group: 'control', hint: 'For-each loop' },
    { type: 'par',       label: 'Паралель',  group: 'control', hint: 'Parallel block' },
    { type: 'insertion', label: 'Вставка',   group: 'meta',    hint: 'Insertion socket' },
    { type: 'comment',   label: 'Коментар',  group: 'meta',    hint: 'Comment / note' },
  ];

  // -------------------- Health / active rules --------------------
  const HEALTH = {
    server: 'online',
    utopia_db:   { host: '192.168.3.251', port: 9922,  status: 'online', latency_ms: 1.2 },
    llm_gateway: { host: '192.168.3.184', port: 18880, status: 'online', slots_available: 3 },
    gitnexus_ast:{ host: '192.168.3.184', port: 4747,  status: 'online' },
    checked_at: '2026-09-17T10:14:22Z',
  };

  const ACTIVE_RULES = {
    compiled_snapshot: `§§0§§ utopia §§1§§ Bitemporal, Invariant
§§0§§ gateway §§1§§ SlotPool, TokenBudget

BUDGET_WORDS = 500 §§0§§

§§0§§ SovereignRouter:
    §§0§§
    §§0§§ __init__(§§1§§, pool: SlotPool, budget: TokenBudget):
        §§0§§.pool = pool
        §§0§§.budget = budget`,
    word_count: 476,
    max_budget: 500,
    latency_ms: 14.5,
    recommended_skills: ['b-sdd', 'architecture-designer', 'skill-creator', 'find-skills'],
  };

  // -------------------- SSE token stream sample --------------------
  const STREAM_SAMPLE = [
    'from utopia import Bitemporal, Invariant\n',
    'from gateway import SlotPool, TokenBudget\n',
    '\n',
    'BUDGET_WORDS = 500\n',
    '\n',
    'class SovereignRouter:\n',
    '    """Routes prompts respecting the ADR-002 pre-flight budget."""\n',
    '\n',
    '    def __init__(self, pool: SlotPool, budget: TokenBudget):\n',
    '        self.pool = pool\n',
    '        self.budget = budget\n',
    '        self._invariants = Bitemporal.load_active()\n',
    '\n',
    '    def route(self, prompt: str) -> Slot:\n',
    '        if self.budget.word_count(prompt) > BUDGET_WORDS:\n',
    '            raise Invariant.Violation("ADR-002-INV-02")\n',
    '        return self.pool.acquire(strategy="lowest-latency")\n',
  ];

  return {
    PROJECT, SPECS, ADRS, ADR_CONTENT, PHASES, SPRINT_STATE, MODEL_SLOTS,
    DRAKON_DIAGRAM, DRAKON_ICONS, HEALTH, ACTIVE_RULES, STREAM_SAMPLE,
  };
})();
