// B-SDD Operator Workbench — main App
const { useState, useEffect } = React;

// Simple error boundary so one broken subtree doesn't blank the whole workbench
class Boundary extends React.Component {
  constructor(p){ super(p); this.state = { err: null }; }
  static getDerivedStateFromError(err){ return { err }; }
  componentDidCatch(err, info){ console.error('Boundary caught:', err, info); }
  render(){
    if (this.state.err) {
      return <div style={{padding: 20, color: '#F43F5E', fontFamily: 'JetBrains Mono, monospace', fontSize: 12}}>
        <b>Error in {this.props.name}:</b> {String(this.state.err.message || this.state.err)}
      </div>;
    }
    return this.props.children;
  }
}

function App() {
  const t = useTweaks({
    activePhase: 6,
    density: 'standard',
    streaming: true,
    project: 'accord-suisse',
  });

  const [selectedNode, setSelectedNode] = useState(null);
  const [showReject, setShowReject] = useState(false);
  const [showApprove, setShowApprove] = useState(false);
  const [playheadTv, setPlayheadTv] = useState(BSDD.TIMELINE.playheadTv);
  const [playheadTt, setPlayheadTt] = useState(BSDD.TIMELINE.playheadTt);

  // Density → body attribute
  useEffect(() => {
    document.body.dataset.density = t.density === 'dense' ? 'dense' : (t.density === 'comfort' ? 'comfort' : '');
  }, [t.density]);

  // Keyboard shortcuts
  useEffect(() => {
    const h = (e) => {
      if (e.key === 'Escape') { setSelectedNode(null); setShowReject(false); setShowApprove(false); }
      if ((e.key === 'Enter' && (e.metaKey || e.ctrlKey)) && t.activePhase === 6) { setShowApprove(true); }
      if (e.key === 'R' && e.shiftKey && t.activePhase === 6) { setShowReject(true); }
    };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [t.activePhase]);

  const project = BSDD.PROJECTS.find(p => p.id === t.project) || BSDD.PROJECTS[0];

  const handleScrub = (which, ms) => {
    if (which === 'tv') setPlayheadTv(ms);
    else setPlayheadTt(ms);
  };

  const handleReject = () => {
    setShowReject(false);
    // Would trigger branch creation
  };

  const activePhase = t.activePhase ?? 6;

  return (
    <div className="app-root">
      <Boundary name="Topbar"><Topbar project={project} onOpenSettings={() => {}} /></Boundary>
      <Boundary name="Stepper"><PhaseStepper activePhase={activePhase} onSelect={(n) => t.setTweak('activePhase', n)} /></Boundary>

      <div className="main-grid">
        <Boundary name="DRAKON Studio">
          <DrakonStudio
            selectedNodeId={selectedNode?.id}
            onNodeClick={setSelectedNode}
          />
        </Boundary>
        <Boundary name="Copilot">
          <CopilotPanel
            streaming={t.streaming}
            onToggleStream={() => t.setTweak('streaming', !t.streaming)}
          />
        </Boundary>
      </div>

      <Boundary name="Timeline">
        <BitemporalTimeline
          playheadTv={playheadTv}
          playheadTt={playheadTt}
          onScrub={handleScrub}
        />
      </Boundary>

      <Boundary name="ReviewGate">
        <ReviewGate
          activePhase={activePhase}
          onApprove={() => setShowApprove(true)}
          onReject={() => setShowReject(true)}
        />
      </Boundary>

      {selectedNode && (
        <InspectorDrawer node={selectedNode} onClose={() => setSelectedNode(null)} />
      )}
      {showReject && (
        <RejectModal onClose={() => setShowReject(false)} onConfirm={handleReject} />
      )}
      {showApprove && (
        <ApproveOverlay onClose={() => setShowApprove(false)} />
      )}

      {/* Tweaks Panel */}
      <TweaksPanel title="Tweaks · Operator Controls">
        <TweakSuggestionBar suggestions={[
          'Перемкни фазу на Φ2 щоб побачити студію DRAKON у активному стані',
          'Спробуй скрабер T_v на 2026-04 — ADR-005 стане активним, ADR-007 зникне',
          'Клік на будь-який вузол шампуру відкриє інспектор інваріантів',
          'Натисни Reject & Branch для демо ΔC формулювання',
        ]}/>

        <TweakSection label="Активна фаза">
          <TweakSelect
            label="Phase"
            value={t.activePhase}
            options={BSDD.PHASES.map(p => ({ value: p.n, label: `Φ${p.n} · ${p.title}` }))}
            onChange={(v) => t.setTweak('activePhase', +v)}
          />
        </TweakSection>

        <TweakSection label="Активний проект">
          <TweakRadio
            label="Project"
            value={t.project}
            options={[
              { value: 'accord-suisse', label: 'ACCORD' },
              { value: 'b-sdd-core',    label: 'B-SDD Core' },
            ]}
            onChange={(v) => t.setTweak('project', v)}
          />
        </TweakSection>

        <TweakSection label="Щільність інтерфейсу">
          <TweakRadio
            label="Density"
            value={t.density}
            options={[
              { value: 'dense',    label: 'Ultra' },
              { value: 'standard', label: 'Std' },
              { value: 'comfort',  label: 'Comfort' },
            ]}
            onChange={(v) => t.setTweak('density', v)}
          />
        </TweakSection>

        <TweakSection label="Копілот стрімінг">
          <TweakToggle
            label="LLM code stream"
            value={t.streaming}
            onChange={(v) => t.setTweak('streaming', v)}
          />
        </TweakSection>

        <TweakSection label="Швидкі дії">
          <TweakButton label="Trigger Reject & Branch" onClick={() => { t.setTweak('activePhase', 6); setShowReject(true); }} />
          <TweakButton label="Trigger Approve & Sign" onClick={() => { t.setTweak('activePhase', 6); setShowApprove(true); }} />
          <TweakButton label="Reset timeline scrubbers" onClick={() => {
            setPlayheadTv(BSDD.TIMELINE.playheadTv);
            setPlayheadTt(BSDD.TIMELINE.playheadTt);
          }} />
        </TweakSection>
      </TweaksPanel>
    </div>
  );
}

// Mount
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
