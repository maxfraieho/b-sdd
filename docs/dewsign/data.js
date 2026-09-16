// ============================================================
// B-SDD Operator Workbench — Real project mock data
// ============================================================

window.BSDD = window.BSDD || {};

BSDD.PROJECTS = [
  {
    id: 'accord-suisse',
    name: 'ACCORD Suisse',
    workspace: 'Swiss Job Hunter / Sovereign VPC',
    phase: 6,
    branch: 'sprint-004/housing-agent',
    lastCommit: '3f8c2a1',
    color: '#8B5CF6',
  },
  {
    id: 'b-sdd-core',
    name: 'B-SDD Framework Core',
    workspace: 'Framework Development',
    phase: 2,
    branch: 'sprint-011/handoff-drakon',
    lastCommit: 'e19b7d4',
    color: '#F59E0B',
  },
];

BSDD.PHASES = [
  { n: 1, key: 'intent',   title: 'Intent Framing',        meta: 'ADR-MADR', op: '100% Оператор' },
  { n: 2, key: 'spec',     title: 'Algorithmic Spec',      meta: 'DRAKON',   op: '50% Нагляд' },
  { n: 3, key: 'preflight',title: 'Pre-Flight Compilation',meta: '<20ms · <500w', op: 'Автомат' },
  { n: 4, key: 'exec',     title: 'Phased Code Execution', meta: 'LLM :18880', op: 'Автомат' },
  { n: 5, key: 'fitness',  title: 'Automated Fitness Gates',meta: 'pytest · AST', op: 'Автомат' },
  { n: 6, key: 'review',   title: 'Human Review Gate',     meta: 'Crypto Sig', op: '100% Architect' },
  { n: 7, key: 'distill',  title: 'Distillation & Handoff',meta: 'next_sprint.md', op: '20% Нагляд' },
];

// State per phase for ACCORD Suisse @ Φ6
BSDD.PHASE_STATES = {
  1: { state: 'done',    metric: '3 ADR resolved',  latency: '—' },
  2: { state: 'done',    metric: 'graph valid (0×)', latency: '2.1s' },
  3: { state: 'done',    metric: '476/500w · 18ms', latency: '18ms' },
  4: { state: 'done',    metric: '2,140 tok / 42tok/s', latency: '51s' },
  5: { state: 'done',    metric: '70/70 tests · AST 100%', latency: '149.91s' },
  6: { state: 'active',  metric: 'awaiting sign-off', latency: 'live' },
  7: { state: 'pending', metric: 'queued',           latency: '—' },
};

BSDD.ADRS = [
  { id: 'ADR-001', title: 'Bitemporal Intent Graph in Utopia DB',        status: 'accepted',   tv: '2025-11-04', tt: '2025-11-04', supersededBy: null,     domain: 'core' },
  { id: 'ADR-002', title: 'Pre-Flight Rule Compiler (<20ms / <500w)',    status: 'accepted',   tv: '2025-12-12', tt: '2025-12-12', supersededBy: null,     domain: 'core' },
  { id: 'ADR-003', title: 'Sovereign LLM Gateway on 192.168.3.184:18880',status: 'accepted',   tv: '2026-01-19', tt: '2026-01-19', supersededBy: null,     domain: 'infra' },
  { id: 'ADR-005', title: 'Monolithic Sprint Context (deprecated)',      status: 'superseded', tv: '2026-02-11', tt: '2026-02-11', supersededBy: 'ADR-007', domain: 'process' },
  { id: 'ADR-007', title: 'Sprint Chaining via Negative Invariants ΔC',  status: 'accepted',   tv: '2026-04-02', tt: '2026-04-02', supersededBy: null,     domain: 'process' },
  { id: 'ADR-008', title: 'DRAKON-as-Spec Workbench & Node Contracts',   status: 'accepted',   tv: '2026-05-20', tt: '2026-05-20', supersededBy: null,     domain: 'ux' },
  { id: 'ADR-013', title: 'Silhouette Routing for Async Sub-Skewers',    status: 'proposed',   tv: '2026-08-15', tt: '2026-08-15', supersededBy: null,     domain: 'ux' },
  { id: 'ADR-024', title: 'Cloudflare WAF Bypass via mTLS Tunnel',       status: 'accepted',   tv: '2026-09-01', tt: '2026-09-01', supersededBy: null,     domain: 'infra' },
];

// DRAKON schema: sovereign_gateway_router.drn
// Coordinates on a 620 x 780 canvas (main skewer at x=170)
BSDD.DRAKON = {
  file: 'sovereign_gateway_router.drn',
  project: 'ACCORD Suisse',
  linkedADR: 'ADR-008',
  nodes: [
    // Main skewer (happy path) — x = 170
    { id: 'n1',  type: 'headline', x: 170, y: 40,  w: 200, h: 34, label: 'Sovereign Gateway Router', adr: 'ADR-008' },
    { id: 'n2',  type: 'action',   x: 170, y: 110, w: 200, h: 40, label: 'Parse SSE Request', adr: 'ADR-024-INV-01', state: 'done' },
    { id: 'n3',  type: 'action',   x: 170, y: 175, w: 200, h: 40, label: 'Load Active Rules (.context)', adr: 'ADR-002-INV-01', state: 'done' },
    { id: 'n4',  type: 'question', x: 170, y: 245, w: 200, h: 46, label: 'Token budget OK?', adr: 'ADR-002-INV-02' },
    { id: 'n5',  type: 'action',   x: 170, y: 320, w: 200, h: 40, label: 'Select Slot (agent-proxy)', adr: 'ADR-003-INV-01', state: 'done' },
    { id: 'n6',  type: 'question', x: 170, y: 390, w: 200, h: 46, label: 'Coding intent?', adr: 'ADR-003-INV-02' },
    { id: 'n7',  type: 'action',   x: 170, y: 465, w: 200, h: 40, label: 'Route → coding-proxy', adr: 'ADR-003-INV-03', state: 'done' },
    { id: 'n8',  type: 'action',   x: 170, y: 530, w: 200, h: 40, label: 'Stream Response via mTLS', adr: 'ADR-024-INV-02', state: 'running' },
    { id: 'n9',  type: 'silhouette', x: 170, y: 600, w: 200, h: 38, label: '→ Handoff Composer', adr: 'ADR-007-INV-01' },
    { id: 'n10', type: 'end',      x: 170, y: 665, w: 200, h: 32, label: 'END · Success' },

    // Right branches (degradation) — chem prayer, tim girshe
    { id: 'r4',  type: 'action',   x: 420, y: 245, w: 170, h: 40, label: 'Truncate context', adr: 'ADR-002-INV-03' },
    { id: 'r6',  type: 'action',   x: 420, y: 390, w: 170, h: 40, label: 'Route → reasoning-proxy', adr: 'ADR-003-INV-04' },

    // Far-right emergency (rose)
    { id: 'e1',  type: 'action',   x: 420, y: 465, w: 170, h: 40, label: 'Kill stream · Circuit break', adr: 'ADR-003-INV-05' },
    { id: 'e2',  type: 'end',      x: 420, y: 530, w: 170, h: 32, label: 'END · Reject', reject: true },
  ],
  edges: [
    // Main skewer (happy path)
    { from: 'n1', to: 'n2', kind: 'happy' },
    { from: 'n2', to: 'n3', kind: 'happy' },
    { from: 'n3', to: 'n4', kind: 'happy' },
    { from: 'n4', to: 'n5', kind: 'happy', label: 'Так' },
    { from: 'n5', to: 'n6', kind: 'happy' },
    { from: 'n6', to: 'n7', kind: 'happy', label: 'Так' },
    { from: 'n7', to: 'n8', kind: 'happy' },
    { from: 'n8', to: 'n9', kind: 'happy' },
    { from: 'n9', to: 'n10', kind: 'silhouette' },

    // Right branches
    { from: 'n4', to: 'r4', kind: 'reject', label: 'Ні' },
    { from: 'r4', to: 'n5', kind: 'reject' },  // ре-вхід у шампур
    { from: 'n6', to: 'r6', kind: 'reject', label: 'Ні' },
    { from: 'r6', to: 'n8', kind: 'reject' },  // ре-вхід

    // Emergency
    { from: 'r6', to: 'e1', kind: 'reject' },  // downgrade
    { from: 'e1', to: 'e2', kind: 'reject' },
  ],
};

// LLM slot pool at 192.168.3.184:18880
BSDD.SLOTS = [
  { id: 'agent',   name: 'agent-proxy',    model: 'Llama-3.2 11B Vision',  latency: '0.6s',  active: false },
  { id: 'coding',  name: 'coding-proxy',   model: 'Qwen2.5-Coder-32B',     latency: '1.4s',  active: true },
  { id: 'reason',  name: 'reasoning-proxy',model: 'DeepSeek-R1',           latency: '3.8s',  active: false },
];

// Token budget for current sprint context
BSDD.TOKEN_BUDGET = {
  total: 8192,
  invariants: 476,      // words in active_rules.md
  handoff: 320,
  drakon: 1120,
  code: 2140,
};

// Fitness report (Φ5 output shown at Φ6 gate)
BSDD.FITNESS = [
  { k: 'Unit Tests',   v: '70/70', sub: 'pytest · 149.91s', state: 'ok' },
  { k: 'AST Isolation',v: '100%',   sub: 'GitNexus :4747',    state: 'ok' },
  { k: 'Coverage',     v: '94.2%',  sub: 'lines / branches',  state: 'ok' },
  { k: 'Memory Peak',  v: '412 MB', sub: 'limit 512',         state: 'ok' },
  { k: 'Rules Latency',v: '17.8 ms',sub: 'budget 20',         state: 'ok' },
  { k: 'ΔC violations',v: '0',      sub: 'inherited from Φ7', state: 'ok' },
];

// Health monitors (topbar)
BSDD.HEALTH = [
  { key: 'utopia',   label: 'Utopia DB',   value: '.251:9922', state: 'ok', latency: '4ms' },
  { key: 'llm',      label: 'LLM Gateway', value: '.184:18880 · 8/8 slots', state: 'ok', latency: '11ms' },
  { key: 'gitnexus', label: 'GitNexus AST',value: '.184:4747',  state: 'ok', latency: '7ms' },
  { key: 'appwrite', label: 'Appwrite RT', value: 'mTLS · Connected', state: 'ok', latency: '22ms' },
];

// The streaming code (Python) for Φ4 continuation shown in copilot
BSDD.STREAM_CODE = [
  { code: '# ent_groq_stt_router · sovereign_gateway_router.py', cls: 'com' },
  { code: 'from utopia import Bitemporal, Invariant', cls: 'kw' },
  { code: 'from gateway import SlotPool, TokenBudget', cls: 'kw' },
  { code: '', cls: 'plain' },
  { code: 'BUDGET_WORDS = 500  # ADR-002-INV-02', cls: 'com' },
  { code: '', cls: 'plain' },
  { code: 'class SovereignRouter:', cls: 'class' },
  { code: '    """Routes SSE requests across 8-slot vLLM pool."""', cls: 'str' },
  { code: '', cls: 'plain' },
  { code: '    def __init__(self, pool: SlotPool, budget: TokenBudget):', cls: 'fn' },
  { code: '        self.pool = pool', cls: 'plain' },
  { code: '        self.budget = budget', cls: 'plain' },
  { code: '        self._inv = Invariant.load("ADR-003-INV-*")', cls: 'plain' },
  { code: '', cls: 'plain' },
  { code: '    async def route(self, req: SSERequest) -> AsyncIter[str]:', cls: 'fn' },
  { code: '        if not self.budget.fits(req.context_words):', cls: 'plain' },
  { code: '            req = req.truncate(BUDGET_WORDS)   # r4 branch', cls: 'plain' },
  { code: '        slot = self.pool.pick(kind="coding" if req.is_code else "agent")', cls: 'plain' },
  { code: '        async for tok in slot.stream_mtls(req):', cls: 'plain' },
  { code: '            yield tok', cls: 'plain' },
];

// Timeline range: 2025-11 → 2026-10 (12 months)
BSDD.TIMELINE = {
  startMs: Date.parse('2025-11-01'),
  endMs:   Date.parse('2026-10-15'),
  playheadTv: Date.parse('2026-09-16'),   // current date
  playheadTt: Date.parse('2026-09-16'),
};
