// Right-side inspector drawer for DRAKON node → linked ADR/invariant

function InspectorDrawer({ node, onClose }) {
  if (!node) return null;

  const adrId = (node.adr || '').split('-INV-')[0];
  const invNum = (node.adr || '').split('-INV-')[1];
  const adr = BSDD.ADRS.find(a => a.id === adrId);

  const invariantText = {
    'ADR-002-INV-02': 'wordCount(activeRules) ≤ 500 ∧ compileTime(rules) < 20ms',
    'ADR-024-INV-01': '∀ req ∈ SSE : mTLS(req.origin) = valid ∧ waf.bypass(req) = false',
    'ADR-024-INV-02': '∀ chunk ∈ stream : encoding = utf8 ∧ transport = mTLS(sovereign_vpc)',
    'ADR-002-INV-01': 'load(activeRules) < 20ms ∧ ¬containsDeprecatedAdr(activeRules)',
    'ADR-003-INV-01': 'pool.available ≥ 1 ∧ slot.model ∈ {llama-3.2, qwen-2.5-coder, deepseek-r1}',
    'ADR-003-INV-02': 'classify(req.intent) ∈ {coding, agentic, reasoning}',
    'ADR-003-INV-03': 'req.is_code = true ⇒ slot.pool = coding-proxy',
    'ADR-003-INV-04': 'downgrade(coding) ⇒ slot.pool = reasoning-proxy ∧ timeout ≤ 8s',
    'ADR-003-INV-05': 'circuit.open ⇒ req.status = 503 ∧ audit.log(req.id)',
    'ADR-002-INV-03': 'truncate(ctx, 500w) ∧ preserve(criticalInvariants)',
    'ADR-007-INV-01': 'handoff.next_sprint.md contains(deltaC ∪ nextGoal) ∧ signed(operator)',
    'ADR-008-INV-01': 'graph.planar = true ∧ crossings = 0 ∧ ∀ n ∈ nodes : n.type ∈ {headline, action, question, silhouette, end}',
  };

  const facts = [
    { k: 'Entity ID',    v: 'ent_groq_stt_router' },
    { k: 'Node ID',      v: node.id },
    { k: 'Node type',    v: node.type },
    { k: 'Bound ADR',    v: node.adr || '—' },
    { k: 'Utopia T_v',   v: adr ? adr.tv : '—' },
    { k: 'Utopia T_t',   v: adr ? adr.tt : '—' },
    { k: 'Status',       v: adr ? adr.status : '—' },
  ];

  const codeSnippet = node.type === 'action'
    ? `# Generated inside «${node.label}» icon
async def ${node.id}_impl(ctx):
    inv = await Invariant.load("${node.adr || 'ADR-*'}")
    assert inv.holds(ctx), f"Violation: {inv.formula}"
    return await gateway.stream(ctx, slot="coding-proxy")`
    : node.type === 'question'
    ? `# Guard inside «${node.label}»
def ${node.id}_guard(ctx) -> bool:
    return TokenBudget(ctx).fits(500)   # ADR-002-INV-02`
    : `# ${node.type} node — no synthesized code
# (structural only, orchestrated by DRAKON runtime)`;

  return (
    <>
      <div className="drawer-backdrop" onClick={onClose}/>
      <div className="drawer" role="dialog">
        <div className="drawer-header">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="8" r="6.5" stroke="var(--violet)" strokeWidth="1.5" fill="var(--violet-dim)"/>
            <path d="M8 4v4l2.5 2.5" stroke="var(--violet)" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <div className="title">Node Inspector</div>
          {node.adr && <span className="adr-id">{node.adr}</span>}
          <button className="icon-btn close" onClick={onClose} title="Close (Esc)">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
          </button>
        </div>

        <div className="drawer-body">
          <div className="drawer-section">
            <h5>{node.type.toUpperCase()} · {node.label}</h5>
            <div style={{fontSize: 11.5, color: 'var(--text-secondary)', lineHeight: 1.5, marginTop: 6}}>
              {node.type === 'action' && 'Кодогенерація дозволена суворо всередині цієї ікони. Топологія графа заблокована; кодер-агент може синтезувати тільки тіло функції з зв\'язаним інваріантом.'}
              {node.type === 'question' && 'Гарантія розгалуження. Ліва гілка = happy path (шампур); права гілка = деградація.'}
              {node.type === 'headline' && 'Точка входу шампуру. Прив\'язує всю схему до ADR-контракту.'}
              {node.type === 'silhouette' && 'Асинхронний перехід до під-шампуру. Не блокує основний потік.'}
              {node.type === 'end' && (node.reject ? 'Термінальний вузол відхилення. Емітує ΔC-інваріанти для наступного циклу.' : 'Успішне завершення. Тригер естафети до Φ7.')}
            </div>
          </div>

          {node.adr && (
            <div className="drawer-section">
              <h5>Bound Invariant · {node.adr}</h5>
              <div className="invariant-block">
                <div style={{marginBottom: 6}}>
                  <span className="lbl">rule:</span> {adr?.title || 'Sovereign gateway contract'}
                </div>
                <div>
                  <span className="lbl">∀ ctx:</span> <span className="formula">{invariantText[node.adr] || 'invariant.evaluate(ctx) = TRUE'}</span>
                </div>
              </div>
            </div>
          )}

          <div className="drawer-section">
            <h5>Utopia DB Facts</h5>
            <div>
              {facts.map((f, i) => (
                <div key={i} className="fact-row">
                  <span className="k">{f.k}</span>
                  <span className="v">{f.v}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="drawer-section">
            <h5>Generated Code Fragment</h5>
            <div className="code-block">{codeSnippet}</div>
          </div>

          <div className="drawer-section">
            <h5>Hybrid Search · Tantivy + pgvector</h5>
            <div style={{display: 'flex', gap: 4, flexWrap: 'wrap'}}>
              {['gateway.stream', 'mtls_tunnel', 'invariant_check', 'circuit_breaker', 'token_budget'].map(t => (
                <span key={t} className="attach-chip mono" style={{fontSize: 10}}>{t}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

window.InspectorDrawer = InspectorDrawer;
