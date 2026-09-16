// src/App.tsx
import React, { useState, useRef, useMemo } from 'react';
import { Topbar } from '@/components/Topbar';
import { PhaseStepper } from '@/components/PhaseStepper';
import { ReviewGateModal } from '@/components/ReviewGateModal';
import { DrakonCanvas, type DrakonCanvasHandle } from '@/components/DrakonStudio/DrakonCanvas';
import { DrakonToolbar } from '@/components/DrakonStudio/DrakonToolbar';
import { NodeInspector } from '@/components/DrakonStudio/NodeInspector';
import { CopilotStream } from '@/components/CopilotPanel/CopilotStream';
import { TimelineSlider } from '@/components/BitemporalRadar/TimelineSlider';
import { AdrListCard } from '@/components/BitemporalRadar/AdrListCard';
import { InvariantDrawer } from '@/components/InvariantDrawer';

import { MOCK_ADRS } from '@/data/mockAdrs';
import { CANONICAL_DRAKON_DIAGRAM, CANONICAL_HITL_DRAKON_IR } from '@/data/mockDrakonSchema';
import { MOCK_SPRINT_STATE, MOCK_MODEL_SLOTS } from '@/data/mockSprints';
import type { HitlPhaseId, RejectAndBranchPayload } from '@/types/sprint';
import type { DrakonNodeIR } from '@/types/drakon';
import type { BitemporalAdr } from '@/types/adr';
import type { TokenBudget } from '@/types/copilot';

export const App: React.FC = () => {
  // Global Project & Sprint State
  const [selectedProject, setSelectedProject] = useState('B-SDD Framework Core');
  const [sprintState, setSprintState] = useState(MOCK_SPRINT_STATE);
  const [isReviewGateOpen, setIsReviewGateOpen] = useState(false);
  const [isInvariantDrawerOpen, setIsInvariantDrawerOpen] = useState(false);

  // Drakon Studio State
  const canvasRef = useRef<DrakonCanvasHandle>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>('cond_phi6');

  // Copilot State
  const [activeSlotId, setActiveSlotId] = useState('coding-proxy');
  const [tokenBudget] = useState<TokenBudget>({
    maxWords: 500,
    currentWords: 476,
    tokensEstimated: 642,
    isExceeded: false,
  });

  // Bitemporal Timeline State (1-16 = Sept 1 - Sept 16, 2026)
  const [validTimeDay, setValidTimeDay] = useState(16);
  const [txTimeDay, setTxTimeDay] = useState(16);
  const [selectedAdr, setSelectedAdr] = useState<BitemporalAdr | null>(null);

  // Total invariant count
  const totalInvariantCount = useMemo(() => {
    return MOCK_ADRS.reduce((sum, adr) => sum + adr.invariants.length, 0);
  }, []);

  // Selected Drakon Node IR
  const selectedNodeIR: DrakonNodeIR | null = useMemo(() => {
    if (!selectedNodeId) return null;
    return CANONICAL_HITL_DRAKON_IR.nodes.find((n) => n.node_id === selectedNodeId) || null;
  }, [selectedNodeId]);

  // Phase selection handler
  const handleSelectPhase = (phaseId: HitlPhaseId) => {
    setSprintState((prev) => ({
      ...prev,
      currentPhase: phaseId,
    }));
  };

  // Phase 6 Human Review Gate Approve
  const handleApproveReview = () => {
    setSprintState((prev) => {
      const updatedPhases = prev.phases.map((p) => {
        if (p.id === 'phi_6') return { ...p, status: 'completed' as const };
        if (p.id === 'phi_7') return { ...p, status: 'running' as const };
        return p;
      });
      return {
        ...prev,
        currentPhase: 'phi_7',
        phases: updatedPhases,
      };
    });
  };

  // Phase 6 Reject & Branch
  const handleRejectAndBranch = (payload: RejectAndBranchPayload) => {
    setSprintState((prev) => {
      const updatedPhases = prev.phases.map((p) => {
        if (p.id === 'phi_6') return { ...p, status: 'rejected' as const };
        return p;
      });
      return {
        ...prev,
        phases: updatedPhases,
        deltaC: payload.negativeInvariants,
      };
    });
  };

  // Export JSON handler
  const handleExportJson = () => {
    const jsonStr = canvasRef.current?.exportJson() || JSON.stringify(CANONICAL_HITL_DRAKON_IR, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${CANONICAL_HITL_DRAKON_IR.name.toLowerCase().replace(/\s+/g, '_')}.drakon.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-canvas text-slate-100 overflow-hidden select-none">
      {/* 1. TOPBAR (48px) */}
      <Topbar
        selectedProject={selectedProject}
        onProjectChange={setSelectedProject}
        onOpenInvariantDrawer={() => setIsInvariantDrawerOpen(true)}
        invariantCount={totalInvariantCount}
      />

      {/* 2. PHASE STEPPER (64px) */}
      <PhaseStepper
        phases={sprintState.phases}
        currentPhaseId={sprintState.currentPhase}
        onSelectPhase={handleSelectPhase}
        onOpenReviewGate={() => setIsReviewGateOpen(true)}
      />

      {/* 3. MAIN WORKSPACE (Zone A: Drakon Studio 55%, Zone B: Copilot Panel 45%) */}
      <main className="flex-1 flex min-h-0 overflow-hidden border-b border-border-subtle">
        {/* Zone A: DRAKON Algorithmic Studio */}
        <section className="w-[55%] flex flex-col border-r border-border-subtle relative bg-canvas">
          <DrakonToolbar
            onZoomIn={() => canvasRef.current?.zoomIn()}
            onZoomOut={() => canvasRef.current?.zoomOut()}
            onGoHome={() => canvasRef.current?.goHome()}
            onExportJson={handleExportJson}
            diagramName={CANONICAL_DRAKON_DIAGRAM.name}
          />

          <div className="flex-1 relative overflow-hidden">
            <DrakonCanvas
              ref={canvasRef}
              diagram={CANONICAL_DRAKON_DIAGRAM}
              diagramId="hitl-7phase-pipeline"
              onSelectNode={setSelectedNodeId}
              selectedNodeId={selectedNodeId}
            />

            {/* Slide-out Node Inspector when node selected */}
            <NodeInspector
              node={selectedNodeIR}
              onClose={() => setSelectedNodeId(null)}
              onOpenInvariantDetails={() => setIsInvariantDrawerOpen(true)}
            />
          </div>
        </section>

        {/* Zone B: Sovereign LLM Copilot Panel */}
        <section className="w-[45%] flex flex-col bg-panel">
          <CopilotStream
            modelSlots={MOCK_MODEL_SLOTS}
            activeSlotId={activeSlotId}
            onSelectSlot={setActiveSlotId}
            tokenBudget={tokenBudget}
          />
        </section>
      </main>

      {/* 4. ZONE C: BITEMPORAL ADR RADAR & TIMELINE SLIDER (Bottom 130px) */}
      <footer className="h-[135px] bg-panel flex flex-col shrink-0 select-none overflow-hidden">
        <TimelineSlider
          validTimeDay={validTimeDay}
          onValidTimeChange={setValidTimeDay}
          txTimeDay={txTimeDay}
          onTxTimeChange={setTxTimeDay}
          activeAdrCount={MOCK_ADRS.length}
          supersededCount={0}
        />

        <AdrListCard
          adrs={MOCK_ADRS}
          validTimeDay={validTimeDay}
          onSelectAdr={(adr) => {
            setSelectedAdr(adr);
            setIsInvariantDrawerOpen(true);
          }}
          selectedAdrId={selectedAdr?.id}
        />
      </footer>

      {/* 5. MODALS & DRAWERS */}
      <ReviewGateModal
        isOpen={isReviewGateOpen}
        onClose={() => setIsReviewGateOpen(false)}
        fitnessSummary={sprintState.fitnessSummary}
        onApprove={handleApproveReview}
        onRejectAndBranch={handleRejectAndBranch}
      />

      <InvariantDrawer
        isOpen={isInvariantDrawerOpen}
        onClose={() => setIsInvariantDrawerOpen(false)}
        adrs={MOCK_ADRS}
        onSelectInvariant={(id) => {
          // Highlight node with matching invariant if any
          const matchingNode = CANONICAL_HITL_DRAKON_IR.nodes.find(
            (n) => n.semantic_binding?.adr_invariant_id === id
          );
          if (matchingNode) {
            setSelectedNodeId(matchingNode.node_id);
          }
        }}
      />
    </div>
  );
};

export default App;
