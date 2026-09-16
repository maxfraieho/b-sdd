// Reject & Branch modal — depth selector + ΔC negative invariants formulation
const { useState: _useSt } = React;

function RejectModal({ onClose, onConfirm }) {
  const [depth, setDepth] = _useSt('phase');
  const [negInvariant, setNegInvariant] = _useSt('mtls_tunnel MUST NOT fall back to plain HTTP when Cloudflare handshake fails; expected 503 + audit log, observed silent downgrade at line 47.');

  const rollbackOptions = [
    { id: 'node', n: 'NODE', d: 'Rewind single DRAKON node · retry impl only' },
    { id: 'phase', n: 'Φ4', d: 'Rewind to Phased Code Execution · fresh context' },
    { id: 'spec', n: 'Φ2', d: 'Rewind to Algorithmic Spec · re-design skewer' },
  ];

  const violatedInv = [
    { chk: '✗', txt: 'ADR-024-INV-02 · stream.transport = mTLS(sovereign_vpc)' },
    { chk: '✗', txt: 'ADR-003-INV-05 · circuit.open ⇒ req.status = 503' },
    { chk: '⚠', txt: 'ADR-002-INV-02 · wordCount(activeRules) ≤ 500' },
  ];

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" className="icon">
            <path d="M10 2L2 17h16L10 2z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" fill="rgba(244,63,94,0.15)"/>
            <path d="M10 8v4M10 15v.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <h3>Reject &amp; Branch · Copy-on-Write Snapshot</h3>
          <button className="icon-btn close" onClick={onClose}>
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="1.5"/></svg>
          </button>
        </div>

        <div className="modal-body">
          <p>
            Гілка спринту буде закрита за дійсним часом (V<sub>end</sub> = T<sub>now</sub>) у Utopia DB.
            Наступний цикл отримає <span className="mono" style={{color: 'var(--rose)'}}>ΔC</span> — вектор порушених інваріантів,
            <b> без </b> шуму попереднього коду.
          </p>

          <label>Глибина відкату</label>
          <div className="rollback-options">
            {rollbackOptions.map(o => (
              <div
                key={o.id}
                className={`rollback-opt ${depth === o.id ? 'selected' : ''}`}
                onClick={() => setDepth(o.id)}
              >
                <span className="n mono">{o.n}</span>
                <span className="d">{o.d}</span>
              </div>
            ))}
          </div>

          <label>ΔC · Автоматично виявлені порушення</label>
          <div className="invariant-list" style={{marginBottom: 14}}>
            <div className="header mono">Δ C = {'{'}</div>
            {violatedInv.map((v, i) => (
              <div key={i} className="inv">
                <span className="chk">{v.chk}</span>
                <span className="txt">{v.txt}</span>
              </div>
            ))}
            <div className="header mono">{'}'}</div>
          </div>

          <label>Формулювання негативного інваріанту (operator override)</label>
          <textarea
            className="textarea-neg"
            value={negInvariant}
            onChange={e => setNegInvariant(e.target.value)}
          />
          <div style={{marginTop: 8, fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)'}}>
            → буде записано у <b>.context/next_sprint_deltac.md</b> та передано у Φ2 наступного циклу
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>Скасувати</button>
          <button className="btn-danger" onClick={onConfirm}>
            <svg width="12" height="12" viewBox="0 0 16 16" fill="none" style={{display: 'inline-block', verticalAlign: '-2px', marginRight: 6}}>
              <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="2"/>
            </svg>
            Відхилити цикл та створити гілку
          </button>
        </div>
      </div>
    </div>
  );
}

window.RejectModal = RejectModal;
