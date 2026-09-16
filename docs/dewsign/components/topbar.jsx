// Topbar: logo, project switcher, health cluster, tier badge, cycles widget, user
const { useState } = React;

function Topbar({ project, onOpenSettings }) {
  return (
    <div className="topbar">
      <div className="logo">
        <div className="logo-mark">B</div>
        <span>B-SDD <span style={{color: 'var(--text-muted)', fontWeight: 400}}>Operator Workbench</span></span>
      </div>

      <div className="divider-v" />

      <div className="project-switcher" onClick={onOpenSettings}>
        <span className="dot" />
        <span style={{fontWeight: 600}}>{project.name}</span>
        <span className="mono" style={{color: 'var(--text-muted)', fontSize: 10}}>· {project.branch}</span>
        <svg width="10" height="10" viewBox="0 0 12 12" fill="none" style={{marginLeft: 4, color: 'var(--text-muted)'}}>
          <path d="M3 5l3 3 3-3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>

      <div className="divider-v" />

      <span className="uppercase-label">Sovereign VPC</span>
      <div className="health-cluster">
        {BSDD.HEALTH.map(h => (
          <div key={h.key} className="health-chip" title={`${h.label} — latency ${h.latency}`}>
            <span className={`dot ${h.state}`} />
            <span className="label">{h.label}</span>
            <span className="value">{h.value.split(' ')[0]}</span>
          </div>
        ))}
      </div>

      <div className="spacer" />

      <div className="cycles-widget">
        <div className="row">
          <span className="uppercase-label" style={{fontSize: 9}}>Verified Cycles</span>
          <span className="mono" style={{fontSize: 11}}>412 <span style={{color: 'var(--text-muted)'}}>/ 5,000</span></span>
        </div>
        <div className="bar"><i style={{width: '8.24%'}} /></div>
      </div>

      <div className="tier-badge">
        <svg width="12" height="12" viewBox="0 0 16 16" fill="none" className="icon">
          <path d="M8 1l2 4.5 5 .5-3.75 3.25L12.5 14 8 11.5 3.5 14l1.25-4.75L1 6l5-.5L8 1z" fill="currentColor"/>
        </svg>
        <span style={{fontWeight: 600}}>Enterprise Sovereign</span>
      </div>

      <div className="divider-v" />

      <div className="user-chip">
        <div className="user-avatar">VK</div>
        <div style={{display: 'flex', flexDirection: 'column', gap: 0, paddingRight: 6}}>
          <span style={{fontSize: 10.5, fontWeight: 600, lineHeight: 1.2}}>Volodymyr K.</span>
          <span style={{fontSize: 9, color: 'var(--text-muted)', lineHeight: 1.2}}>Head Architect</span>
        </div>
      </div>
    </div>
  );
}

window.Topbar = Topbar;
