/* =========================================================
   Zone 2 · HITL 7-Phase Stepper (44px)
   Astryx Segmented control with phase status states.
   ========================================================= */
function PhaseStepper({ phases, currentPhaseId, onSelectPhase, verified }) {
  const idx = phases.findIndex((p) => p.id === currentPhaseId);
  return (
    <div
      className="row shrink-0"
      style={{
        height: 'var(--h-stepper)',
        background: 'var(--color-bg-card)',
        borderBottom: '1px solid var(--color-border-hair)',
        padding: '0 12px',
        gap: 0,
      }}
    >
      {/* Left rail: verified counter */}
      <div className="row gap-2 shrink-0" style={{ paddingRight: 16, borderRight: '1px solid var(--color-border-hair)', height: '100%' }}>
        <span className="text-eyebrow">VERIFIED CYCLES</span>
        <div className="mono tabnum" style={{ fontSize: 16, fontWeight: 700, color: 'var(--color-amber)', lineHeight: 1 }}>412</div>
        <span className="mono" style={{ fontSize: 10, color: 'var(--color-fg-muted)' }}>/ 5,000</span>
      </div>

      {/* Phase cells */}
      <div className="row flex-1" style={{ overflowX: 'auto', height: '100%' }}>
        {phases.map((p, i) => {
          const isActive   = p.id === currentPhaseId;
          const isDone     = p.status === 'completed';
          const isRunning  = p.status === 'running';
          const isRejected = p.status === 'rejected';
          const tone = isRejected ? 'rose' : isActive || isRunning ? 'amber' : isDone ? 'emerald' : 'muted';
          return (
            <button
              key={p.id}
              onClick={() => onSelectPhase(p.id)}
              className="row gap-2"
              style={{
                height: '100%',
                padding: '0 12px',
                borderRight: i < phases.length - 1 ? '1px solid var(--color-border-hair)' : 'none',
                borderTop: isActive ? '2px solid var(--color-amber)' : '2px solid transparent',
                borderBottom: isActive ? '2px solid var(--color-amber)' : '2px solid transparent',
                background: isActive ? 'var(--color-bg-panel)' : 'transparent',
                cursor: 'pointer',
                minWidth: 128,
                flex: '1 1 0',
                textAlign: 'left',
                transition: 'background 120ms',
              }}
              title={p.description}
            >
              <div
                className="row"
                style={{
                  width: 22, height: 22,
                  border: `1.5px solid var(--color-${tone === 'muted' ? 'fg-faint' : tone})`,
                  background: isDone || isActive ? `var(--color-${tone === 'muted' ? 'bg-elevated' : tone + '-glow'})` : 'transparent',
                  color: `var(--color-${tone === 'muted' ? 'fg-faint' : tone})`,
                  justifyContent: 'center', alignItems: 'center',
                  fontFamily: 'var(--font-mono)', fontSize: 10, fontWeight: 700,
                  flexShrink: 0,
                  borderRadius: 2,
                }}
              >
                {isDone ? Icons.check : p.index}
              </div>
              <div className="col" style={{ gap: 0, lineHeight: 1.15, minWidth: 0 }}>
                <div className="truncate" style={{ fontSize: 11.5, fontWeight: 600, color: isActive ? 'var(--color-amber)' : 'var(--color-fg-primary)' }}>
                  {p.symbol}: {p.name}
                </div>
                <div className="mono truncate" style={{ fontSize: 9.5, color: 'var(--color-fg-muted)', letterSpacing: '0.02em' }}>
                  {isRunning ? 'awaiting sign-off' : isDone ? p.hitlLevel : p.hitlLevel}
                </div>
              </div>
              {isRunning && <Dot tone="amber" pulse />}
            </button>
          );
        })}
      </div>
    </div>
  );
}

window.PhaseStepper = PhaseStepper;
