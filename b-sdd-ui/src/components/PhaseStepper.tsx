// src/components/PhaseStepper.tsx
import React from 'react';
import type { HitlPhase, HitlPhaseId } from '@/types/sprint';
import {
  CheckCircle2,
  Clock,
  ShieldAlert,
  AlertTriangle,
  Play,
  RotateCcw,
} from 'lucide-react';

interface PhaseStepperProps {
  phases: HitlPhase[];
  currentPhaseId: HitlPhaseId;
  onSelectPhase: (phaseId: HitlPhaseId) => void;
  onOpenReviewGate: () => void;
}

export const PhaseStepper: React.FC<PhaseStepperProps> = ({
  phases,
  currentPhaseId,
  onSelectPhase,
  onOpenReviewGate,
}) => {
  return (
    <div className="h-16 bg-panel/80 border-b border-border-subtle px-4 flex items-center justify-between shrink-0 overflow-x-auto select-none">
      <div className="flex items-center gap-2 min-w-max">
        {phases.map((phase, idx) => {
          const isCurrent = phase.id === currentPhaseId;
          const isReviewGate = phase.id === 'phi_6';

          let statusBg = 'bg-card border-border-subtle text-slate-400';
          let icon = <Clock className="w-3.5 h-3.5 text-slate-500" />;

          if (phase.status === 'completed') {
            statusBg = 'bg-emerald-500/10 border-emerald-500/40 text-emerald-300';
            icon = <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />;
          } else if (phase.status === 'running') {
            if (isReviewGate) {
              statusBg = 'bg-violet-500/20 border-violet-500 text-violet-200 animate-pulse';
              icon = <ShieldAlert className="w-4 h-4 text-violet-400" />;
            } else {
              statusBg = 'bg-blue-500/15 border-blue-500 text-blue-200 animate-pulse';
              icon = <Play className="w-3.5 h-3.5 text-blue-400" />;
            }
          } else if (phase.status === 'rejected') {
            statusBg = 'bg-rose-500/20 border-rose-500 text-rose-300';
            icon = <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />;
          }

          return (
            <React.Fragment key={phase.id}>
              {idx > 0 && (
                <div
                  className={`w-6 h-0.5 ${
                    phases[idx - 1].status === 'completed'
                      ? 'bg-emerald-500/50'
                      : 'bg-border-subtle'
                  }`}
                />
              )}

              <button
                onClick={() => {
                  onSelectPhase(phase.id);
                  if (isReviewGate && (phase.status === 'running' || phase.status === 'completed')) {
                    onOpenReviewGate();
                  }
                }}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md border text-xs font-mono transition-all ${statusBg} ${
                  isCurrent ? 'ring-2 ring-amber ring-offset-1 ring-offset-canvas shadow-lg' : 'hover:border-slate-500'
                }`}
              >
                <div className="flex items-center justify-center">{icon}</div>
                <div className="flex flex-col items-start">
                  <div className="flex items-center gap-1.5">
                    <span className="font-bold">{phase.symbol}</span>
                    <span className="text-[11px] font-sans font-medium text-slate-200">{phase.name}</span>
                  </div>
                  <span className="text-[9px] text-slate-400 font-mono">{phase.hitlLevel}</span>
                </div>
              </button>
            </React.Fragment>
          );
        })}
      </div>

      {/* Action shortcuts */}
      <div className="flex items-center gap-2 ml-4 shrink-0">
        {currentPhaseId === 'phi_6' && (
          <button
            onClick={onOpenReviewGate}
            className="flex items-center gap-1.5 bg-violet-600 hover:bg-violet-500 text-white px-3 py-1.5 rounded-md text-xs font-semibold shadow-md transition-colors"
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Human Review Gate</span>
          </button>
        )}
      </div>
    </div>
  );
};
