// src/components/PhaseStepper.tsx
// Astryx-native HITL 7-Phase Execution Stepper (ADR-008, ADR-009)
import React from 'react';
import type { HitlPhase, HitlPhaseId } from '@/types/sprint';
import { Button, Badge, Dot } from './astryx/primitives';
import {
  CheckCircle2,
  Clock,
  ShieldAlert,
  AlertTriangle,
  Play,
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
    <div className="h-16 bg-[#0d121c]/90 border-b border-[#1e293b] px-4 flex items-center justify-between shrink-0 overflow-x-auto select-none">
      <div className="flex items-center gap-2 min-w-max">
        {phases.map((phase, idx) => {
          const isCurrent = phase.id === currentPhaseId;
          const isReviewGate = phase.id === 'phi_6';

          let statusBg = 'bg-[#141b27] border-[#1e293b] text-slate-400';
          let icon = <Clock className="w-3.5 h-3.5 text-slate-500" />;
          let tone: 'emerald' | 'amber' | 'cyan' | 'rose' | 'violet' | 'neutral' = 'neutral';

          if (phase.status === 'completed') {
            statusBg = 'bg-emerald/10 border-emerald/40 text-emerald';
            icon = <CheckCircle2 className="w-3.5 h-3.5 text-emerald" />;
            tone = 'emerald';
          } else if (phase.status === 'running') {
            if (isReviewGate) {
              statusBg = 'bg-violet-500/20 border-violet-500 text-violet-200 shadow-sm';
              icon = <ShieldAlert className="w-4 h-4 text-violet-400" />;
              tone = 'violet';
            } else {
              statusBg = 'bg-cyan/15 border-cyan text-cyan-200 shadow-sm';
              icon = <Play className="w-3.5 h-3.5 text-cyan" />;
              tone = 'cyan';
            }
          } else if (phase.status === 'rejected') {
            statusBg = 'bg-rose/20 border-rose text-rose-300';
            icon = <AlertTriangle className="w-3.5 h-3.5 text-rose" />;
            tone = 'rose';
          }

          return (
            <React.Fragment key={phase.id}>
              {idx > 0 && (
                <div
                  className={`w-6 h-0.5 ${
                    phases[idx - 1].status === 'completed'
                      ? 'bg-emerald/50'
                      : 'bg-[#1e293b]'
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
                className={`flex items-center gap-2 px-3 py-1.5 rounded border text-xs font-mono transition-all cursor-pointer ${statusBg} ${
                  isCurrent ? 'ring-1 ring-amber border-amber shadow-md' : 'hover:border-slate-500'
                }`}
              >
                <div className="flex items-center justify-center">
                  {phase.status === 'running' ? (
                    <Dot tone={tone} pulse />
                  ) : (
                    icon
                  )}
                </div>
                <div className="flex flex-col items-start text-left">
                  <div className="flex items-center gap-1.5">
                    <span className="font-bold text-amber">{phase.symbol}</span>
                    <span className="text-[11px] font-sans font-medium text-slate-200">{phase.name}</span>
                  </div>
                  <Badge tone={tone} outline className="text-[9px] mt-0.5">
                    {phase.hitlLevel}
                  </Badge>
                </div>
              </button>
            </React.Fragment>
          );
        })}
      </div>

      {/* Action shortcuts */}
      <div className="flex items-center gap-2 ml-4 shrink-0">
        {currentPhaseId === 'phi_6' && (
          <Button
            variant="primary"
            size="sm"
            icon={<ShieldAlert className="w-3.5 h-3.5" />}
            onClick={onOpenReviewGate}
          >
            Human Review Gate
          </Button>
        )}
      </div>
    </div>
  );
};

export default PhaseStepper;
