// Human Review Gate Φ6 — bottom persistent bar

function ReviewGate(props) {
  const activePhase = props.activePhase;
  const onApprove = props.onApprove;
  const onReject = props.onReject;

  const phaseMeta = BSDD.PHASES.find(function(p){ return p.n === activePhase; }) || BSDD.PHASES[0];
  const phaseTitle = phaseMeta ? phaseMeta.title : '';

  if (activePhase !== 6) {
    return (
      <div className="gate-zone" style={{background: 'var(--bg-panel)', borderTopColor: 'var(--border-subtle)', boxShadow: 'none'}}>
        <div className="gate-identity">
          <div className="gate-badge" style={{background: 'var(--bg-card)', color: 'var(--text-muted)', animation: 'none', boxShadow: 'none', border: '1px solid var(--border-subtle)'}}>Φ{activePhase}</div>
          <div className="info">
            <h3 style={{color: 'var(--text-secondary)'}}>{'Phase Φ' + activePhase + ' · ' + phaseTitle}</h3>
            <div className="sub">Human Review Gate opens once fitness barriers pass. Currently running upstream…</div>
          </div>
        </div>
        <div className="gate-report">
          {BSDD.FITNESS.slice(0, 4).map(function(f, i){
            return (
              <div key={i} className={'gate-metric ' + f.state} style={{opacity: 0.55}}>
                <div className="k">{f.k}</div>
                <div className="v">{f.v}</div>
                <div className="sub">{f.sub}</div>
              </div>
            );
          })}
        </div>
        <div className="gate-actions">
          <button className="btn-approve" disabled style={{opacity: 0.35}}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 8l4 4 8-8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
            Approve & Sign
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="gate-zone">
      <div className="gate-identity">
        <div className="gate-badge">Φ6</div>
        <div className="info">
          <h3>Human Review Gate · Blocking</h3>
          <div className="sub">All 5 upstream phases green · Fitness barriers passed · Awaiting human sign-off</div>
          <div className="await">
            <span className="dot"/> AWAITING HUMAN SIGN-OFF
          </div>
        </div>
      </div>

      <div className="gate-report">
        {BSDD.FITNESS.map(function(f, i){
          return (
            <div key={i} className={'gate-metric ' + f.state}>
              <div className="k">{f.k}</div>
              <div className="v">{f.v}</div>
              <div className="sub">{f.sub}</div>
            </div>
          );
        })}
      </div>

      <div className="gate-actions">
        <button className="btn-reject" onClick={onReject}>
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>
          Reject &amp; Branch
          <span className="kbd">⇧R</span>
        </button>
        <button className="btn-approve" onClick={onApprove}>
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M2 8l4 4 8-8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
          Approve &amp; Sign Certificate
          <span className="kbd">⌘⏎</span>
        </button>
      </div>
    </div>
  );
}

window.ReviewGate = ReviewGate;
