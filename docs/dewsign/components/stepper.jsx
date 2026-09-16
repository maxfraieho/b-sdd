// Phase stepper Φ1 → Φ7
function PhaseStepper({ activePhase, onSelect }) {
  const getState = (n) => {
    if (n < activePhase) return 'done';
    if (n === activePhase) return activePhase === 6 ? 'active' : (activePhase === 2 ? 'active' : 'running');
    return 'pending';
  };
  return (
    <div className="stepper">
      {BSDD.PHASES.map(ph => {
        const state = getState(ph.n);
        const metric = BSDD.PHASE_STATES[ph.n];
        return (
          <div key={ph.n} className="step" data-state={state} onClick={() => onSelect(ph.n)}>
            <div className="idx">Φ{ph.n}</div>
            <div className="body">
              <div className="title">{ph.title}</div>
              <div className="meta">{state === 'done' ? metric.metric : (state === 'active' ? '⚡ ' + metric.metric : ph.meta)}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

window.PhaseStepper = PhaseStepper;
