// Approve overlay — crypto sign certificate + next-sprint CLI
const { useState: _useSt2 } = React;

function ApproveOverlay({ onClose }) {
  const [copied, setCopied] = _useSt2(false);
  const cmd = './run_b_sdd.sh "Виконати Milestone 2: Реєстр інструментів агента житла (ACCORD Suisse · Art. 262 CO)"';

  const copy = () => {
    navigator.clipboard.writeText(cmd).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1400);
    });
  };

  const now = new Date();
  const sig = 'sha256:9f2c...a41e';

  return (
    <div className="approve-overlay">
      <div className="approve-card">
        <div className="head">
          <div className="icon-wrap">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M4 12l5 5L20 6" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div>
            <h3>Cycle Approved · Crypto-Signed</h3>
            <div style={{fontSize: 11, color: 'var(--text-secondary)', marginTop: 2}}>
              Φ6 → Φ7 · Verified Execution Cycle #413 committed to Utopia DB
            </div>
          </div>
        </div>

        <div className="cert">
          <div><span className="k">operator</span> · Volodymyr Kovalenko &lt;head-architect&gt;</div>
          <div><span className="k">signed_at</span> · {now.toISOString()}</div>
          <div><span className="k">signature</span> · {sig}</div>
          <div><span className="k">artifacts</span> · sovereign_gateway_router.py · sovereign_gateway_router.drn · pytest.xml · adr-024.md</div>
          <div><span className="k">WORM lock</span> · <span style={{color: 'var(--emerald)'}}>engaged</span></div>
        </div>

        <div style={{marginTop: 14, fontSize: 11, color: 'var(--text-muted)'}}>
          Distillation агент згенерував <b style={{color: 'var(--text-primary)', fontFamily: 'var(--font-mono)'}}>.context/next_sprint.md</b>. Запустіть наступний цикл:
        </div>

        <div className="cli">
          <span className="prompt">$</span>
          <span style={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>{cmd}</span>
          <button className="copy" onClick={copy}>{copied ? '✓ copied' : '📋 copy'}</button>
        </div>

        <div className="foot">
          <button className="btn-approve" onClick={onClose} style={{padding: '8px 16px', fontSize: 11.5}}>
            Continue to Φ7 Handoff
          </button>
        </div>
      </div>
    </div>
  );
}

window.ApproveOverlay = ApproveOverlay;
