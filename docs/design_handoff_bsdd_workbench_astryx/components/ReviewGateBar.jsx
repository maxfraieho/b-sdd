/* =========================================================
   Review Gate Bar (Φ6 blocking action strip)
   Only shown when currentPhase === 'phi_6'.
   ========================================================= */
function ReviewGateBar({ sprintState, currentPhase, onApprove, onReject, onOpenGate }) {
  const isPhi6 = currentPhase === 'phi_6';
  if (!isPhi6) return null;
  const fs = sprintState.fitnessSummary;

  return (
    <div
      className="row shrink-0"
      style={{
        height: 72,
        background: 'var(--color-bg-panel)',
        borderTop: '1px solid var(--color-border-hair)',
        padding: '0 16px',
        gap: 20,
      }}
    >
      {/* Phase badge */}
      <div className="row gap-3 shrink-0">
        <div style={{
          width: 44, height: 44,
          background: 'linear-gradient(135deg,#f59e0b,#78350f)',
          borderRadius: 3,
          display: 'grid', placeItems: 'center',
          fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: 18,
          color: '#0b0f16',
        }}>Φ6</div>
        <div className="col" style={{ gap: 2, lineHeight: 1.2 }}>
          <div className="row gap-2">
            <span style={{ fontSize: 13, fontWeight: 700 }}>Human Review Gate</span>
            <Badge tone="amber">BLOCKING</Badge>
          </div>
          <div style={{ fontSize: 11, color: 'var(--color-fg-secondary)' }}>
            All 5 upstream phases green · Fitness barriers passed · Awaiting synchronous operator sign-off
          </div>
          <div className="mono" style={{ fontSize: 9.5, color: 'var(--color-amber)' }}>
            &gt; AWAITING_HUMAN_SIGNOFF · sprint-2026-09-16-004
          </div>
        </div>
      </div>

      <div className="divider-v" />

      {/* Fitness metrics */}
      <div className="row gap-4 shrink-0">
        <Metric label="UNIT TESTS" value={`${fs.passed}/${fs.total}`} unit={`pytest ${fs.durationSeconds}s`} tone="emerald"/>
        <Metric label="AST ISOLATION" value={`${fs.astIsolationScore}%`} unit="GitNexus:4747" tone="emerald"/>
        <Metric label="COVERAGE" value={`${fs.coverage}%`} unit="lines/branches" tone="emerald"/>
        <Metric label="LATENCY" value={`${fs.latencyMs}ms`} unit={`≤ 50ms budget`} tone="emerald"/>
        <Metric label="TOKENS" value={`${fs.tokenCount}w`} unit={`≤ 500w budget`} tone={fs.tokenCount > 500 ? 'rose' : 'emerald'}/>
      </div>

      <div className="grow" />

      {/* Action buttons */}
      <div className="row gap-2 shrink-0">
        <Button size="lg" variant="destructive" icon={Icons.branch} onClick={onReject} style={{ whiteSpace: 'nowrap' }}>
          Reject &amp; Branch
          <span className="mono" style={{ fontSize: 9, opacity: 0.6, marginLeft: 6 }}>⇧R</span>
        </Button>
        <Button size="lg" variant="success" icon={Icons.check} onClick={onApprove} style={{ whiteSpace: 'nowrap' }}>
          Затвердити (Approve)
          <span className="mono" style={{ fontSize: 9, opacity: 0.7, marginLeft: 6 }}>⌘⏎</span>
        </Button>
      </div>
    </div>
  );
}

function Metric({ label, value, unit, tone = 'emerald' }) {
  return (
    <div className="col" style={{ gap: 0, lineHeight: 1.1, minWidth: 96, whiteSpace: 'nowrap' }}>
      <div className="text-eyebrow" style={{ whiteSpace: 'nowrap' }}>{label}</div>
      <div className="mono tabnum" style={{ fontSize: 15, fontWeight: 700, color: `var(--color-${tone})`, whiteSpace: 'nowrap' }}>{value}</div>
      <div className="mono" style={{ fontSize: 9, color: 'var(--color-fg-muted)', whiteSpace: 'nowrap' }}>{unit}</div>
    </div>
  );
}

window.ReviewGateBar = ReviewGateBar;
