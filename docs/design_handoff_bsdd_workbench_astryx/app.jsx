/* =========================================================
   B-SDD Operator Workbench · Astryx Edition — App root
   Wires the 4 zones + modals + drawers + Tweaks panel.
   ========================================================= */
const { useState, useEffect, useMemo, useCallback, useRef } = React;

// Per-zone isolation so one broken subtree doesn't blank the cockpit
class Boundary extends React.Component {
  constructor(p) { super(p); this.state = { err: null }; }
  static getDerivedStateFromError(err) { return { err }; }
  componentDidCatch(err, info) { console.error('[Boundary]', this.props.name, err, info); }
  render() {
    if (this.state.err) {
      return (
        <div className="col gap-2" style={{ padding: 12, background: 'var(--color-rose-glow)', border: '1px solid var(--color-rose)', color: 'var(--color-rose)' }}>
          <div className="text-eyebrow" style={{ color: 'var(--color-rose)' }}>ERROR · {this.props.name}</div>
          <div className="mono" style={{ fontSize: 11 }}>{String(this.state.err.message || this.state.err)}</div>
        </div>
      );
    }
    return this.props.children;
  }
}

function AppInner() {
  const [t, setTweak] = useTweaks(/*EDITMODE-BEGIN*/{
    "utopiaStatus": "online",
    "llmSlots": 3,
    "tokenBudget": 476,
    "playheadTvDay": 16,
    "playheadTtDay": 16,
    "currentPhase": "phi_6",
    "drakonView": "widget",
    "themePreset": "swiss",
    "density": "standard",
    "streaming": true
  }/*EDITMODE-END*/);

  const [health, setHealth] = useState(BSDD.HEALTH);
  const [activeRules] = useState(BSDD.ACTIVE_RULES);
  const [specs, setSpecs] = useState(BSDD.SPECS);
  const [selectedSpecId, setSelectedSpecId] = useState('004-multi-session-handoff-and-drakon');
  const [selectedNodeId, setSelectedNodeId] = useState('cond_phi6');
  const [activeSocketType, setActiveSocketType] = useState(null);
  const [selectedAdr, setSelectedAdr] = useState(null);
  const [selectedInvariantId, setSelectedInvariantId] = useState(null);
  const [activeSlotId, setActiveSlotId] = useState('coding-proxy');
  const [saveState, setSaveState] = useState('idle');
  const [syncing, setSyncing] = useState(false);

  // Modals / drawers
  const [showReviewGate, setShowReviewGate] = useState(false);
  const [showAdrReader, setShowAdrReader] = useState(false);
  const [showPseudocode, setShowPseudocode] = useState(false);
  const [showAdrLibrary, setShowAdrLibrary] = useState(false);
  const [showInvariantDrawer, setShowInvariantDrawer] = useState(false);
  const [showTasksDrawer, setShowTasksDrawer] = useState(false);
  const [showNodeInspector, setShowNodeInspector] = useState(false);

  const toast = useToast();

  // Apply theme + density
  useEffect(() => { document.body.dataset.density = t.density; }, [t.density]);
  useEffect(() => { document.body.dataset.theme = t.themePreset; }, [t.themePreset]);

  // Apply Tweaks-driven mock overrides for health
  useEffect(() => {
    setHealth((h) => ({
      ...h,
      utopia_db: { ...h.utopia_db, status: t.utopiaStatus === 'offline' ? 'offline' : 'online', latency_ms: t.utopiaStatus === 'syncing' ? 42.1 : 1.2 },
      llm_gateway: { ...h.llm_gateway, status: t.llmSlots > 0 ? 'online' : 'offline', slots_available: t.llmSlots },
    }));
  }, [t.utopiaStatus, t.llmSlots]);

  // Derive sprint state with tweaks-driven active phase
  const sprintState = useMemo(() => ({
    ...BSDD.SPRINT_STATE,
    currentPhase: t.currentPhase,
    phases: BSDD.PHASES.map((p) => {
      if (p.id === t.currentPhase) return { ...p, status: 'running' };
      const currentIdx = BSDD.PHASES.findIndex((x) => x.id === t.currentPhase);
      const thisIdx = BSDD.PHASES.findIndex((x) => x.id === p.id);
      return { ...p, status: thisIdx < currentIdx ? 'completed' : 'pending' };
    }),
    fitnessSummary: {
      ...BSDD.SPRINT_STATE.fitnessSummary,
      tokenCount: t.tokenBudget,
    },
  }), [t.currentPhase, t.tokenBudget]);

  const totalInvariants = useMemo(
    () => BSDD.ADRS.reduce((s, a) => s + a.invariants.length, 0),
    []
  );
  const currentSpec = useMemo(() => specs.find((s) => s.id === selectedSpecId), [specs, selectedSpecId]);
  const taskProgress = currentSpec
    ? { completed: currentSpec.completed_count, total: currentSpec.tasks_count }
    : { completed: 0, total: 0 };

  const activeDiagram = BSDD.DRAKON_DIAGRAM;
  const selectedNode = selectedNodeId ? { ...activeDiagram.items[selectedNodeId], nodeId: selectedNodeId } : null;

  // Actions
  const handleSyncUtopia = useCallback(async () => {
    setSyncing(true);
    setTweak('utopiaStatus', 'syncing');
    await window.BSDDApi.syncUtopia();
    setSyncing(false);
    setTweak('utopiaStatus', 'online');
    toast.push({ tone: 'success', title: 'Utopia DB synchronized', message: '8 rulings · 1247ms' });
  }, [toast, setTweak]);

  const handleSaveSpec = useCallback(async () => {
    setSaveState('saving');
    await window.BSDDApi.saveDrakonSchema({ target_path: `specs/${selectedSpecId}/logic.drakon.json`, schema_ir: activeDiagram });
    setSaveState('saved');
    toast.push({ tone: 'success', title: 'DRAKON schema saved', message: '0 crossings · planar ✓' });
    setTimeout(() => setSaveState('idle'), 1600);
  }, [activeDiagram, selectedSpecId, toast]);

  const handleReviewSubmit = useCallback((decision) => {
    if (decision === 'approve') {
      setTweak('currentPhase', 'phi_7');
    } else {
      setTweak('currentPhase', 'phi_1');
    }
  }, [setTweak]);

  const handleAdrOpen = useCallback((adr) => {
    setSelectedAdr(adr);
    setShowAdrLibrary(false);
    setShowAdrReader(true);
  }, []);

  const handleInvariantClick = useCallback((invId) => {
    setSelectedInvariantId(invId);
    // find owning ADR and open reader
    const owner = BSDD.ADRS.find((a) => a.invariants.some((i) => i.id === invId));
    if (owner) {
      setSelectedAdr(owner);
      setShowAdrReader(true);
    }
  }, []);

  const handleInsertIcon = useCallback((type) => {
    setActiveSocketType((prev) => prev === type ? null : type);
    toast.push({ tone: 'info', title: `Socket active · ${type}`, message: 'Click a target position on the canvas' });
  }, [toast]);

  const handleToggleTask = useCallback((specId, taskId, completed) => {
    setSpecs((prev) => prev.map((s) => {
      if (s.id !== specId) return s;
      const tasks = s.tasks.map((t) => t.id === taskId ? { ...t, completed } : t);
      const completedCount = tasks.filter((x) => x.completed).length;
      return { ...s, tasks, completed_count: completedCount, percent: Math.round((completedCount / tasks.length) * 100) };
    }));
    window.BSDDApi.toggleTask(specId, taskId, completed);
  }, []);

  const handleNodeSelect = useCallback((id) => {
    setSelectedNodeId(id);
    setShowNodeInspector(true);
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const h = (e) => {
      if (e.key === 'Escape') {
        setShowReviewGate(false); setShowAdrReader(false); setShowAdrLibrary(false);
        setShowInvariantDrawer(false); setShowTasksDrawer(false); setShowNodeInspector(false);
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && t.currentPhase === 'phi_6') {
        setShowReviewGate(true);
      }
      if (e.shiftKey && e.key === 'R' && t.currentPhase === 'phi_6') {
        setShowReviewGate(true);
      }
    };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [t.currentPhase]);

  return (
    <div className="app-root">
      <Boundary name="Topbar">
        <Topbar
          project={BSDD.PROJECT}
          specs={specs}
          selectedSpecId={selectedSpecId}
          onSelectSpec={setSelectedSpecId}
          health={health}
          invariantCount={totalInvariants}
          taskProgress={taskProgress}
          onOpenTasks={() => setShowTasksDrawer(true)}
          onOpenAdrLibrary={() => setShowAdrLibrary(true)}
          onOpenInvariants={() => setShowInvariantDrawer(true)}
          onSyncUtopia={handleSyncUtopia}
          syncing={syncing}
        />
      </Boundary>

      <Boundary name="PhaseStepper">
        <PhaseStepper
          phases={sprintState.phases}
          currentPhaseId={t.currentPhase}
          onSelectPhase={(id) => setTweak('currentPhase', id)}
        />
      </Boundary>

      <div className="app-body">
        <Boundary name="DrakonStudio">
          <DrakonStudio
            diagram={activeDiagram}
            selectedSpecId={selectedSpecId}
            viewMode={t.drakonView}
            onViewModeChange={(v) => setTweak('drakonView', v)}
            selectedNodeId={selectedNodeId}
            onSelectNode={handleNodeSelect}
            activeSocketType={activeSocketType}
            onInsertIcon={handleInsertIcon}
            onOpenPseudocode={() => setShowPseudocode(true)}
            onSave={handleSaveSpec}
            saveState={saveState}
          />
        </Boundary>

        <Boundary name="CopilotPanel">
          <CopilotPanel
            slots={BSDD.MODEL_SLOTS}
            activeSlotId={activeSlotId}
            onSelectSlot={setActiveSlotId}
            activeRules={activeRules}
            streaming={t.streaming}
            onToggleStream={() => setTweak('streaming', !t.streaming)}
            budgetOverride={t.tokenBudget}
            onOpenReviewGate={() => setShowReviewGate(true)}
          />
        </Boundary>
      </div>

      <Boundary name="ReviewGateBar">
        <ReviewGateBar
          sprintState={sprintState}
          currentPhase={t.currentPhase}
          onApprove={() => setShowReviewGate(true)}
          onReject={() => setShowReviewGate(true)}
        />
      </Boundary>

      <Boundary name="BitemporalRadar">
        <BitemporalRadar
          adrs={BSDD.ADRS}
          playheadTvDay={t.playheadTvDay}
          playheadTtDay={t.playheadTtDay}
          onScrub={(which, day) => setTweak(which === 'tv' ? 'playheadTvDay' : 'playheadTtDay', day)}
          onSelectAdr={handleAdrOpen}
          selectedAdrId={selectedAdr?.id}
        />
      </Boundary>

      {/* --- Modals --- */}
      <ReviewGateModal
        open={showReviewGate}
        onClose={() => setShowReviewGate(false)}
        sprintState={sprintState}
        onSubmit={handleReviewSubmit}
      />
      <AdrReaderModal
        open={showAdrReader}
        adr={selectedAdr}
        onClose={() => setShowAdrReader(false)}
        onSaved={() => {}}
      />
      <PseudocodeModal
        open={showPseudocode}
        onClose={() => setShowPseudocode(false)}
        diagram={activeDiagram}
      />
      <AdrLibraryModal
        open={showAdrLibrary}
        onClose={() => setShowAdrLibrary(false)}
        adrs={BSDD.ADRS}
        onOpen={handleAdrOpen}
      />

      {/* --- Drawers --- */}
      <InvariantDrawer
        open={showInvariantDrawer}
        onClose={() => setShowInvariantDrawer(false)}
        adrs={BSDD.ADRS}
        onSelectInvariant={handleInvariantClick}
      />
      <TasksDrawer
        open={showTasksDrawer}
        onClose={() => setShowTasksDrawer(false)}
        specs={specs}
        selectedSpecId={selectedSpecId}
        onSelectSpec={setSelectedSpecId}
        onToggleTask={handleToggleTask}
      />
      <NodeInspectorDrawer
        open={showNodeInspector && !!selectedNode}
        onClose={() => setShowNodeInspector(false)}
        nodeId={selectedNodeId}
        node={selectedNode}
        adrs={BSDD.ADRS}
        onUpdate={(updated) => {
          activeDiagram.items[updated.nodeId] = { ...activeDiagram.items[updated.nodeId], content: updated.content, secondary: updated.secondary };
          toast.push({ tone: 'success', title: 'Node updated', message: updated.nodeId });
        }}
        onOpenAdr={handleAdrOpen}
      />

      {/* --- Tweaks panel --- */}
      <TweaksPanel title="Tweaks · Operator Simulation" noDeckControls>
        <TweakSuggestionBar suggestions={[
          'Set Utopia DB to Offline → topbar indicator flips to rose',
          'Push Token Budget past 500 → red banner on Copilot gauge',
          'Change Phase to Φ3 → Review Gate bar disappears',
          'Set DRAKON view to Raw IR JSON → canvas shows structured schema',
          'Try Reject & Branch → COW snapshot modal',
        ]}/>

        <TweakSection label="Utopia DB Status">
          <TweakRadio
            value={t.utopiaStatus}
            onChange={(v) => setTweak('utopiaStatus', v)}
            options={[
              { value: 'online', label: 'Online 1.2ms' },
              { value: 'offline', label: 'Offline' },
              { value: 'syncing', label: 'Syncing' },
            ]}
          />
        </TweakSection>

        <TweakSection label="LLM Gateway Slots">
          <TweakRadio
            value={t.llmSlots}
            onChange={(v) => setTweak('llmSlots', v)}
            options={[
              { value: 3, label: '3 available' },
              { value: 0, label: '0 (busy)' },
            ]}
          />
        </TweakSection>

        <TweakSection label="Token Budget (words)">
          <TweakSlider min={200} max={620} step={2} value={t.tokenBudget} onChange={(v) => setTweak('tokenBudget', v)} unit="w"/>
          <div className="row gap-2" style={{ marginTop: 6 }}>
            <button className="btn btn--sm" onClick={() => setTweak('tokenBudget', 350)}>350w · safe</button>
            <button className="btn btn--sm" onClick={() => setTweak('tokenBudget', 476)}>476w · current</button>
            <button className="btn btn--sm" onClick={() => setTweak('tokenBudget', 520)}>520w · over</button>
          </div>
        </TweakSection>

        <TweakSection label="Bitemporal Timeline (Sept 2026)">
          <TweakSlider label="T_v · Valid Time" min={1} max={30} step={1} value={t.playheadTvDay} onChange={(v) => setTweak('playheadTvDay', v)}/>
          <TweakSlider label="T_t · Transaction Time" min={1} max={30} step={1} value={t.playheadTtDay} onChange={(v) => setTweak('playheadTtDay', v)}/>
        </TweakSection>

        <TweakSection label="HITL Phase">
          <TweakSelect
            value={t.currentPhase}
            onChange={(v) => setTweak('currentPhase', v)}
            options={BSDD.PHASES.map((p) => ({ value: p.id, label: `${p.symbol} · ${p.name}` }))}
          />
        </TweakSection>

        <TweakSection label="DRAKON Canvas View">
          <TweakRadio
            value={t.drakonView}
            onChange={(v) => setTweak('drakonView', v)}
            options={[
              { value: 'widget', label: 'Widget' },
              { value: 'flow', label: 'Flow' },
              { value: 'json', label: 'Raw IR' },
            ]}
          />
        </TweakSection>

        <TweakSection label="Astryx Theme Preset">
          <TweakRadio
            value={t.themePreset}
            onChange={(v) => setTweak('themePreset', v)}
            options={[
              { value: 'swiss', label: 'Swiss Dark' },
              { value: 'gothic', label: 'Gothic' },
              { value: 'contrast', label: 'Contrast' },
            ]}
          />
        </TweakSection>

        <TweakSection label="UI Density">
          <TweakRadio
            value={t.density}
            onChange={(v) => setTweak('density', v)}
            options={[
              { value: 'ultra', label: 'Ultra' },
              { value: 'standard', label: 'Std' },
              { value: 'comfort', label: 'Comfort' },
            ]}
          />
        </TweakSection>

        <TweakSection label="Copilot Streaming">
          <TweakToggle value={t.streaming} onChange={(v) => setTweak('streaming', v)}/>
        </TweakSection>

        <TweakSection label="Quick Actions">
          <TweakButton label="Open Review Gate Modal" onClick={() => setShowReviewGate(true)}/>
          <TweakButton label="Open ADR Reader (ADR-008)" onClick={() => handleAdrOpen(BSDD.ADRS.find((a) => a.id === 'ADR-008'))}/>
          <TweakButton label="Open Pseudocode Exporter" onClick={() => setShowPseudocode(true)}/>
          <TweakButton label="Open Invariant Drawer" onClick={() => setShowInvariantDrawer(true)}/>
        </TweakSection>
      </TweaksPanel>
    </div>
  );
}

function App() {
  return (
    <ToastProvider>
      <AppInner />
    </ToastProvider>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
