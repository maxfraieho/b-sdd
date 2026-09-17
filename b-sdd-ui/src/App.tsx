// src/App.tsx
import React, { useState, useRef, useMemo, useCallback } from 'react';
import { Topbar } from '@/components/Topbar';
import { PhaseStepper } from '@/components/PhaseStepper';
import { ReviewGateModal } from '@/components/ReviewGateModal';
import { DrakonCanvas, type DrakonCanvasHandle } from '@/components/DrakonStudio/DrakonCanvas';
import { DrakonToolbar, type SaveState, type DrakonViewMode } from '@/components/DrakonStudio/DrakonToolbar';
import { DrakonIconPalette } from '@/components/DrakonStudio/DrakonIconPalette';
import { PseudocodeModal } from '@/components/DrakonStudio/PseudocodeModal';
import { VisualFlowCanvas } from '@/components/DrakonStudio/VisualFlowCanvas';
import { NodeInspector } from '@/components/DrakonStudio/NodeInspector';
import { CopilotStream } from '@/components/CopilotPanel/CopilotStream';
import { TimelineSlider } from '@/components/BitemporalRadar/TimelineSlider';
import { AdrListCard } from '@/components/BitemporalRadar/AdrListCard';
import { InvariantDrawer } from '@/components/InvariantDrawer';
import { TasksDrawer } from '@/components/TasksPanel/TasksDrawer';
import { AdrLibraryModal } from '@/components/AdrLibraryModal';
import { AdrReaderModal } from '@/components/AdrReaderModal';
import { useIsMobile } from '@/hooks/useIsMobile';
import { MobileNavigation, type MobileTabId } from '@/components/MobileNavigation';
import { MobilePhaseView } from '@/components/MobilePhaseView';
import { MobileRadarView } from '@/components/MobileRadarView';

import { MOCK_ADRS } from '@/data/mockAdrs';
import { CANONICAL_DRAKON_DIAGRAM, CANONICAL_HITL_DRAKON_IR } from '@/data/mockDrakonSchema';
import { MOCK_SPRINT_STATE, MOCK_MODEL_SLOTS } from '@/data/mockSprints';
import type { HitlPhaseId, RejectAndBranchPayload } from '@/types/sprint';
import type { DrakonNodeIR, DrakonSchemaIR } from '@/types/drakon';
import type { BitemporalAdr } from '@/types/adr';
import type { TokenBudget } from '@/types/copilot';
import type { SpecItem, ProjectInfo, ProjectsResponse, SpecsResponse } from '@/types/specs';

// Live backend integration
import {
  getActiveRules,
  getAdrs,
  getHealth,
  getDrakonSchema,
  saveDrakonSchema,
  getProjects,
  getSpecs,
  toggleTask,
  syncUtopia,
} from '@/lib/api';
import { useLiveData } from '@/hooks/useLiveData';
import type {
  ActiveRulesResponse,
  AdrsResponse,
  HealthResponse,
  DrakonSchemaResponse,
} from '@/lib/backend-types';

const FALLBACK_HEALTH: HealthResponse = {
  server: 'online',
  utopia_db: { host: '192.168.3.251', port: 9922, status: 'online' },
  llm_gateway: { host: '192.168.3.184', port: 18880, status: 'online', slots_available: 3 },
  checked_at: new Date().toISOString(),
};
const FALLBACK_DRAKON: DrakonSchemaResponse = {
  schema_ir: CANONICAL_HITL_DRAKON_IR,
  diagram: CANONICAL_DRAKON_DIAGRAM,
  validation: { is_valid: true, errors: [] },
};
const FALLBACK_RULES: ActiveRulesResponse = {
  compiled_snapshot: '',
  word_count: 476,
  max_budget: 500,
  recommended_skills: ['architecture-designer', 'b-sdd', 'skill-creator'],
  latency_ms: 14.5,
};
const FALLBACK_ADRS: AdrsResponse = {
  adrs: MOCK_ADRS,
  total: MOCK_ADRS.length,
};
const FALLBACK_PROJECTS: ProjectsResponse = {
  current_project: {
    id: 'b-sdd',
    name: 'B-SDD Framework Core',
    path: '/home/vokov/projects/b-sdd',
    branch: 'master',
    commit: 'bffae39',
    dirty_files: 0,
    description: 'Bitemporal Spec-Driven Development Framework',
    stats: { specs: 4, adrs: 8, tests: 36, utopia_kb: '01a08474-0000-7000-8000-000000000001' },
  },
  workspaces: [
    { id: 'b-sdd', name: 'B-SDD Framework Core', path: '/home/vokov/projects/b-sdd', active: true },
  ],
};
const FALLBACK_SPECS: SpecsResponse = {
  total: 4,
  specs: [
    {
      id: '004-multi-session-handoff-and-drakon',
      title: 'Spec 004: Multi-Session Handoff & DRAKON',
      path: 'specs/004-multi-session-handoff-and-drakon',
      tasks_count: 8,
      completed_count: 8,
      percent: 100,
      has_diagram: true,
      diagrams: ['logic.drakon.json'],
      tasks: [
        { id: 'task-001', title: 'Extend SessionDistiller with handoff payload synthesis', completed: true },
        { id: 'task-002', title: 'Wire main.py handoff sub-command in CLI', completed: true },
        { id: 'task-003', title: 'Author architectural contract ADR-007', completed: true },
        { id: 'task-004', title: 'Author architectural contract ADR-008', completed: true },
        { id: 'task-005', title: 'Implement pure stdlib DRAKON schema validator', completed: true },
        { id: 'task-006', title: 'Port React/Vite visualization workbench', completed: true },
        { id: 'task-007', title: 'Connect workbench to local .context/ and Utopia DB', completed: true },
        { id: 'task-008', title: 'Add end-to-end multi-sprint chaining automated tests', completed: true },
      ],
    },
  ],
};

export const App: React.FC = () => {
  // Global Project & Sprint State
  const [sprintState, setSprintState] = useState(MOCK_SPRINT_STATE);
  const [isReviewGateOpen, setIsReviewGateOpen] = useState(false);
  const [isInvariantDrawerOpen, setIsInvariantDrawerOpen] = useState(false);
  const [isTasksDrawerOpen, setIsTasksDrawerOpen] = useState(false);
  const [isAdrLibraryOpen, setIsAdrLibraryOpen] = useState(false);
  const [isPseudocodeOpen, setIsPseudocodeOpen] = useState(false);
  const [isSyncingUtopia, setIsSyncingUtopia] = useState(false);
  const [selectedSpecId, setSelectedSpecId] = useState('004-multi-session-handoff-and-drakon');
  const isMobile = useIsMobile(768);
  const [activeMobileTab, setActiveMobileTab] = useState<MobileTabId>('drakon');

  // DRAKON Studio State — default to full 'widget' editor
  const canvasRef = useRef<DrakonCanvasHandle>(null);
  const [drakonViewMode, setDrakonViewMode] = useState<DrakonViewMode>('widget');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>('cond_phi6');
  const [drakonNodes, setDrakonNodes] = useState<DrakonNodeIR[]>(CANONICAL_HITL_DRAKON_IR.nodes);
  const [activeSocketType, setActiveSocketType] = useState<string | null>(null);
  const [saveState, setSaveState] = useState<SaveState>('idle');
  const [saveError, setSaveError] = useState<string | null>(null);

  // Copilot State
  const [activeSlotId, setActiveSlotId] = useState('coding-proxy');

  // Bitemporal Timeline State (1-16 = Sept 1 - Sept 16, 2026)
  const [validTimeDay, setValidTimeDay] = useState(16);
  const [txTimeDay, setTxTimeDay] = useState(16);
  const [selectedAdr, setSelectedAdr] = useState<BitemporalAdr | null>(null);

  // Live data hooks
  const liveHealth = useLiveData<HealthResponse>({
    fetcher: () => getHealth(FALLBACK_HEALTH),
    fallback: FALLBACK_HEALTH,
    pollMs: 5_000,
  });

  const liveRules = useLiveData<ActiveRulesResponse>({
    fetcher: () => getActiveRules(FALLBACK_RULES),
    fallback: FALLBACK_RULES,
    pollMs: 15_000,
  });

  const liveProjects = useLiveData<ProjectsResponse>({
    fetcher: () => getProjects(FALLBACK_PROJECTS),
    fallback: FALLBACK_PROJECTS,
    pollMs: 10_000,
  });

  const liveSpecs = useLiveData<SpecsResponse>({
    fetcher: () => getSpecs(FALLBACK_SPECS),
    fallback: FALLBACK_SPECS,
    pollMs: 5_000,
  });

  const liveAdrs = useLiveData<AdrsResponse>({
    fetcher: () =>
      getAdrs(FALLBACK_ADRS, {
        validTime: `2026-09-${String(validTimeDay).padStart(2, '0')}`,
        txTime: `2026-09-${String(txTimeDay).padStart(2, '0')}`,
      }),
    fallback: FALLBACK_ADRS,
    pollMs: 0,
    deps: [validTimeDay, txTimeDay],
  });

  const liveDrakon = useLiveData<DrakonSchemaResponse>({
    fetcher: () => getDrakonSchema(FALLBACK_DRAKON, selectedSpecId),
    fallback: FALLBACK_DRAKON,
    pollMs: 0,
    deps: [selectedSpecId],
  });

  const currentDiagram = liveDrakon.data.diagram || CANONICAL_DRAKON_DIAGRAM;

  // Synchronize IR nodes from backend specification when loaded
  React.useEffect(() => {
    if (liveDrakon.data.schema_ir?.nodes && liveDrakon.data.schema_ir.nodes.length > 0) {
      setDrakonNodes(liveDrakon.data.schema_ir.nodes);
    }
  }, [liveDrakon.data.schema_ir]);

  const effectiveAdrs: BitemporalAdr[] =
    liveAdrs.data.adrs.length > 0 ? [...liveAdrs.data.adrs] : MOCK_ADRS;

  const totalInvariantCount = useMemo(() => {
    return effectiveAdrs.reduce((sum, adr) => sum + (adr.invariants?.length || 0), 0);
  }, [effectiveAdrs]);

  const liveTokenBudget: TokenBudget = useMemo(
    () => ({
      maxWords: liveRules.data.max_budget,
      currentWords: liveRules.data.word_count,
      tokensEstimated: Math.round(liveRules.data.word_count * 1.35),
      isExceeded: liveRules.data.word_count > liveRules.data.max_budget,
    }),
    [liveRules.data],
  );

  // Selected Node object
  const selectedNodeIR: DrakonNodeIR | null = useMemo(() => {
    if (!selectedNodeId) return null;
    return drakonNodes.find((n) => n.node_id === selectedNodeId) || null;
  }, [selectedNodeId, drakonNodes]);

  // Node editing handlers
  const handleUpdateNode = useCallback((updatedNode: DrakonNodeIR) => {
    setDrakonNodes((prev) =>
      prev.map((n) => (n.node_id === updatedNode.node_id ? updatedNode : n)),
    );
    // Also update label on visual widget canvas if available
    canvasRef.current?.setContent(updatedNode.node_id, updatedNode.label);
  }, []);

  const handleDeleteNode = useCallback((nodeId: string) => {
    setDrakonNodes((prev) => prev.filter((n) => n.node_id !== nodeId));
    setSelectedNodeId(null);
    canvasRef.current?.deleteSelection();
  }, []);

  const handleAddNode = useCallback((type: 'action' | 'question' | 'end', afterNodeId?: string) => {
    const newId = `node_${Date.now().toString().slice(-4)}`;
    const newNode: DrakonNodeIR = {
      node_id: newId,
      node_type: type,
      label:
        type === 'question'
          ? 'Нова умова: Чи перевірено архітектурні обмеження?'
          : type === 'end'
            ? 'Завершення гілки'
            : 'Нова інженерна дія',
      edges: {
        down: null,
        right: null,
      },
      x: 0,
      y: 0,
    };

    setDrakonNodes((prev) => {
      if (afterNodeId) {
        const index = prev.findIndex((n) => n.node_id === afterNodeId);
        if (index !== -1) {
          const updated = [...prev];
          const prevNode = updated[index];
          newNode.edges.down = prevNode.edges.down;
          updated[index] = {
            ...prevNode,
            edges: { ...prevNode.edges, down: newId },
          };
          updated.splice(index + 1, 0, newNode);
          return updated;
        }
      }
      return [...prev, newNode];
    });

    setSelectedNodeId(newId);
  }, []);

  const handleInsertIconFromPalette = useCallback((type: string) => {
    setActiveSocketType(type);
    canvasRef.current?.showInsertionSockets(type);
  }, []);

  // Tasks toggle handler
  const handleToggleTask = useCallback(
    async (specId: string, taskId: string, completed: boolean) => {
      await toggleTask({ spec_id: specId, task_id: taskId, completed });
      liveSpecs.refresh();
    },
    [liveSpecs],
  );

  // Utopia DB On-Demand Sync
  const handleSyncUtopia = useCallback(async () => {
    setIsSyncingUtopia(true);
    try {
      await syncUtopia();
      liveHealth.refresh();
      liveAdrs.refresh();
    } catch (err) {
      console.error('Failed to sync Utopia DB:', err);
    } finally {
      setIsSyncingUtopia(false);
    }
  }, [liveHealth, liveAdrs]);

  // Phase transition handlers
  const handlePhaseSelect = (phaseId: HitlPhaseId) => {
    setSprintState((prev) => ({
      ...prev,
      currentPhase: phaseId,
    }));
  };

  const handleApproveSprint = () => {
    setSprintState((prev) => ({
      ...prev,
      currentPhase: 'phi_7',
      phases: prev.phases.map((p) =>
        p.id === 'phi_6'
          ? { ...p, status: 'completed' }
          : p.id === 'phi_7'
            ? { ...p, status: 'running' }
            : p,
      ),
    }));
  };

  const handleRejectAndBranch = (payload: RejectAndBranchPayload) => {
    setSprintState((prev) => ({
      ...prev,
      currentPhase: 'phi_1',
      phases: prev.phases.map((p) => ({
        ...p,
        status: p.id === 'phi_1' ? 'running' : 'pending',
      })),
    }));
  };

  const handleExportJson = () => {
    const jsonStr =
      canvasRef.current?.exportJson() ||
      JSON.stringify(
        {
          schema_version: '1.0',
          name: CANONICAL_DRAKON_DIAGRAM.name,
          nodes: drakonNodes,
        },
        null,
        2,
      );
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedSpecId}-logic.drakon.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleSaveSpec = useCallback(async () => {
    setSaveState('saving');
    setSaveError(null);
    try {
      const schemaIR: DrakonSchemaIR = {
        schema_version: '1.0',
        name: CANONICAL_DRAKON_DIAGRAM.name,
        params: 'sprint_id: str, context: dict',
        nodes: drakonNodes,
      };

      await saveDrakonSchema({
        schema_ir: schemaIR,
      });
      setSaveState('saved');
      window.setTimeout(() => setSaveState('idle'), 2200);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : String(err));
      setSaveState('error');
      window.setTimeout(() => setSaveState('idle'), 3200);
    }
  }, [drakonNodes]);

  return (
    <div className="h-screen w-screen flex flex-col bg-canvas text-slate-100 overflow-hidden select-none">
      {/* 1. TOPBAR (48px) */}
      <Topbar
        projectInfo={liveProjects.data.current_project}
        specs={liveSpecs.data.specs}
        selectedSpecId={selectedSpecId}
        onSelectSpec={setSelectedSpecId}
        onOpenTasksDrawer={() => setIsTasksDrawerOpen(true)}
        onOpenAdrLibrary={() => setIsAdrLibraryOpen(true)}
        onOpenInvariantDrawer={() => setIsInvariantDrawerOpen(true)}
        invariantCount={totalInvariantCount}
        utopiaOnline={liveHealth.data?.utopia_db?.status === 'online'}
        llmOnline={liveHealth.data?.llm_gateway?.status === 'online'}
        onSyncUtopia={handleSyncUtopia}
        isSyncingUtopia={isSyncingUtopia}
      />

      {isMobile ? (
        <>
          {/* MOBILE MAIN CONTENT */}
          <main className="flex-1 flex flex-col overflow-hidden relative">
            {activeMobileTab === 'drakon' && (
              <div className="flex-1 relative flex flex-col bg-canvas overflow-hidden">
                <DrakonToolbar
                  onZoomIn={() => canvasRef.current?.zoomIn()}
                  onZoomOut={() => canvasRef.current?.zoomOut()}
                  onGoHome={() => canvasRef.current?.goHome()}
                  onExportJson={handleExportJson}
                  onSaveSpec={handleSaveSpec}
                  onOpenPseudocode={() => setIsPseudocodeOpen(true)}
                  onUndo={() => canvasRef.current?.undo()}
                  onRedo={() => canvasRef.current?.redo()}
                  saveState={saveState}
                  saveErrorMessage={saveError}
                  diagramName={currentDiagram.name}
                  viewMode={drakonViewMode}
                  onViewModeChange={setDrakonViewMode}
                  onAddNode={handleAddNode}
                />

                {drakonViewMode === 'widget' && (
                  <DrakonIconPalette
                    onInsertIcon={handleInsertIconFromPalette}
                    activeSocketType={activeSocketType}
                  />
                )}

                <div className="flex-1 relative overflow-hidden">
                  {drakonViewMode === 'widget' ? (
                    <DrakonCanvas
                      ref={canvasRef}
                      diagram={currentDiagram}
                      diagramId={selectedSpecId}
                      onSelectNode={setSelectedNodeId}
                      selectedNodeId={selectedNodeId}
                      onDiagramChange={(newDiag) => {
                        console.log('[Workbench] Diagram edited:', newDiag.name);
                      }}
                    />
                  ) : drakonViewMode === 'flow' ? (
                    <VisualFlowCanvas
                      nodes={drakonNodes}
                      selectedNodeId={selectedNodeId}
                      onSelectNode={setSelectedNodeId}
                      onAddNode={handleAddNode}
                    />
                  ) : (
                    <div className="w-full h-full p-4 overflow-auto bg-canvas font-mono text-xs text-amber leading-relaxed select-text">
                      <pre>{JSON.stringify({ schema_version: '1.0', name: CANONICAL_DRAKON_DIAGRAM.name, nodes: drakonNodes }, null, 2)}</pre>
                    </div>
                  )}

                  {/* Interactive Node Editor / Inspector */}
                  {selectedNodeIR && (
                    <NodeInspector
                      node={selectedNodeIR}
                      allNodes={drakonNodes}
                      adrs={effectiveAdrs}
                      onClose={() => setSelectedNodeId(null)}
                      onUpdateNode={handleUpdateNode}
                      onDeleteNode={handleDeleteNode}
                      onOpenInvariantDetails={(invId) => {
                        const matchingAdr = effectiveAdrs.find((a) =>
                          a.invariants?.some((inv) => inv.id === invId),
                        );
                        if (matchingAdr) setSelectedAdr(matchingAdr);
                      }}
                    />
                  )}
                </div>
              </div>
            )}

            {activeMobileTab === 'copilot' && (
              <div className="flex-1 bg-panel flex flex-col overflow-hidden">
                <CopilotStream
                  modelSlots={MOCK_MODEL_SLOTS}
                  activeSlotId={activeSlotId}
                  onSelectSlot={setActiveSlotId}
                  tokenBudget={liveTokenBudget}
                />
              </div>
            )}

            {activeMobileTab === 'radar' && (
              <MobileRadarView
                adrs={effectiveAdrs}
                validTimeDay={validTimeDay}
                onValidTimeChange={setValidTimeDay}
                txTimeDay={txTimeDay}
                onTxTimeChange={setTxTimeDay}
                selectedAdrId={selectedAdr?.id}
                onSelectAdr={(adr) => setSelectedAdr(adr)}
                onOpenAdrLibrary={() => setIsAdrLibraryOpen(true)}
              />
            )}

            {activeMobileTab === 'phases' && (
              <MobilePhaseView
                phases={sprintState.phases}
                currentPhaseId={sprintState.currentPhase}
                onSelectPhase={handlePhaseSelect}
                onOpenReviewGate={() => setIsReviewGateOpen(true)}
              />
            )}
          </main>

          {/* MOBILE BOTTOM NAVIGATION (56px) */}
          <MobileNavigation
            activeTab={activeMobileTab}
            onSelectTab={setActiveMobileTab}
            currentPhaseId={sprintState.currentPhase}
            isReviewGatePending={sprintState.currentPhase === 'phi_6'}
            onOpenTasksDrawer={() => setIsTasksDrawerOpen(true)}
            onOpenInvariantDrawer={() => setIsInvariantDrawerOpen(true)}
            onOpenAdrLibrary={() => setIsAdrLibraryOpen(true)}
          />
        </>
      ) : (
        <>
          {/* 2. HITL 7-PHASE STEPPER BAR (44px) */}
          <PhaseStepper
            phases={sprintState.phases}
            currentPhaseId={sprintState.currentPhase}
            onSelectPhase={handlePhaseSelect}
            onOpenReviewGate={() => setIsReviewGateOpen(true)}
          />

          {/* 3. MAIN WORKBENCH BODY */}
          <main className="flex-1 flex overflow-hidden">
            {/* CENTER / LEFT: DRAKON STUDIO */}
            <section className="flex-1 relative flex flex-col border-r border-border-subtle bg-canvas overflow-hidden">
              <DrakonToolbar
                onZoomIn={() => canvasRef.current?.zoomIn()}
                onZoomOut={() => canvasRef.current?.zoomOut()}
                onGoHome={() => canvasRef.current?.goHome()}
                onExportJson={handleExportJson}
                onSaveSpec={handleSaveSpec}
                onOpenPseudocode={() => setIsPseudocodeOpen(true)}
                onUndo={() => canvasRef.current?.undo()}
                onRedo={() => canvasRef.current?.redo()}
                saveState={saveState}
                saveErrorMessage={saveError}
                diagramName={currentDiagram.name}
                viewMode={drakonViewMode}
                onViewModeChange={setDrakonViewMode}
                onAddNode={handleAddNode}
              />

              {/* Icon Palette when in DrakonWidget view */}
              {drakonViewMode === 'widget' && (
                <DrakonIconPalette
                  onInsertIcon={handleInsertIconFromPalette}
                  activeSocketType={activeSocketType}
                />
              )}

              <div className="flex-1 relative overflow-hidden">
                {drakonViewMode === 'widget' ? (
                  <DrakonCanvas
                    ref={canvasRef}
                    diagram={currentDiagram}
                    diagramId={selectedSpecId}
                    onSelectNode={setSelectedNodeId}
                    selectedNodeId={selectedNodeId}
                    onDiagramChange={(newDiag) => {
                      console.log('[Workbench] Diagram edited:', newDiag.name);
                    }}
                  />
                ) : drakonViewMode === 'flow' ? (
                  <VisualFlowCanvas
                    nodes={drakonNodes}
                    selectedNodeId={selectedNodeId}
                    onSelectNode={setSelectedNodeId}
                    onAddNode={handleAddNode}
                  />
                ) : (
                  <div className="w-full h-full p-6 overflow-auto bg-canvas font-mono text-xs text-amber leading-relaxed select-text">
                    <pre>{JSON.stringify({ schema_version: '1.0', name: CANONICAL_DRAKON_DIAGRAM.name, nodes: drakonNodes }, null, 2)}</pre>
                  </div>
                )}

                {/* Interactive Node Editor / Inspector */}
                {selectedNodeIR && (
                  <NodeInspector
                    node={selectedNodeIR}
                    allNodes={drakonNodes}
                    adrs={effectiveAdrs}
                    onClose={() => setSelectedNodeId(null)}
                    onUpdateNode={handleUpdateNode}
                    onDeleteNode={handleDeleteNode}
                    onOpenInvariantDetails={(invId) => {
                      const matchingAdr = effectiveAdrs.find((a) =>
                        a.invariants?.some((inv) => inv.id === invId),
                      );
                      if (matchingAdr) setSelectedAdr(matchingAdr);
                    }}
                  />
                )}
              </div>
            </section>

            {/* RIGHT: SOVEREIGN COPILOT PANEL (420px) */}
            <section className="w-[420px] shrink-0 bg-panel flex flex-col overflow-hidden">
              <CopilotStream
                modelSlots={MOCK_MODEL_SLOTS}
                activeSlotId={activeSlotId}
                onSelectSlot={setActiveSlotId}
                tokenBudget={liveTokenBudget}
              />
            </section>
          </main>

          {/* 4. BOTTOM DUAL-AXIS BITEMPORAL RADAR (110px) */}
          <footer className="h-28 bg-card border-t border-border-subtle flex shrink-0 select-none overflow-hidden">
            <TimelineSlider
              validTimeDay={validTimeDay}
              onValidTimeChange={setValidTimeDay}
              txTimeDay={txTimeDay}
              onTxTimeChange={setTxTimeDay}
              activeAdrCount={effectiveAdrs.length}
              supersededCount={effectiveAdrs.filter((a) => a.status === 'superseded').length}
            />

            <AdrListCard
              adrs={effectiveAdrs}
              validTimeDay={validTimeDay}
              onSelectAdr={(adr) => {
                setSelectedAdr(adr);
              }}
              selectedAdrId={selectedAdr?.id}
            />
          </footer>
        </>
      )}

      {/* 5. MODALS & DRAWERS */}
      <TasksDrawer
        isOpen={isTasksDrawerOpen}
        onClose={() => setIsTasksDrawerOpen(false)}
        specs={liveSpecs.data.specs}
        projectInfo={liveProjects.data.current_project}
        onToggleTask={handleToggleTask}
        selectedSpecId={selectedSpecId}
        onSelectSpec={setSelectedSpecId}
      />

      <AdrLibraryModal
        isOpen={isAdrLibraryOpen}
        onClose={() => setIsAdrLibraryOpen(false)}
        adrs={effectiveAdrs}
        onSelectAdrForInspect={(adr) => setSelectedAdr(adr)}
      />

      <AdrReaderModal
        adr={selectedAdr}
        allAdrs={effectiveAdrs}
        onClose={() => setSelectedAdr(null)}
        onSelectAdr={(adr) => setSelectedAdr(adr)}
        onAdrSaved={() => liveAdrs.refresh()}
      />

      <PseudocodeModal
        isOpen={isPseudocodeOpen}
        onClose={() => setIsPseudocodeOpen(false)}
        diagramJson={CANONICAL_DRAKON_DIAGRAM}
        diagramName={CANONICAL_DRAKON_DIAGRAM.name}
      />

      <InvariantDrawer
        isOpen={isInvariantDrawerOpen}
        onClose={() => setIsInvariantDrawerOpen(false)}
        adrs={effectiveAdrs}
        onSelectInvariant={(id) => {
          setSelectedNodeId(id);
        }}
      />

      <ReviewGateModal
        isOpen={isReviewGateOpen}
        onClose={() => setIsReviewGateOpen(false)}
        fitnessSummary={sprintState.fitnessSummary}
        onApprove={handleApproveSprint}
        onRejectAndBranch={handleRejectAndBranch}
      />
    </div>
  );
};

export default App;
