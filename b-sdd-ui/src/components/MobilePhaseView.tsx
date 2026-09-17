// src/components/MobilePhaseView.tsx
// Astryx-native Mobile Phase Cockpit (ADR-009)
import React from 'react';
import type { HitlPhase, HitlPhaseId } from '@/types/sprint';
import { Button, Badge, Dot } from './astryx/primitives';
import {
  CheckCircle2,
  Clock,
  ShieldAlert,
  AlertTriangle,
  Play,
  ArrowRight,
} from 'lucide-react';

interface MobilePhaseViewProps {
  phases: HitlPhase[];
  currentPhaseId: HitlPhaseId;
  onSelectPhase: (phaseId: HitlPhaseId) => void;
  onOpenReviewGate: () => void;
}

export const MobilePhaseView: React.FC<MobilePhaseViewProps> = ({
  phases,
  currentPhaseId,
  onSelectPhase,
  onOpenReviewGate,
}) => {
  const currentPhase = phases.find((p) => p.id === currentPhaseId) || phases[0];
  const isReviewGate = currentPhaseId === 'phi_6';

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-[#090d13] text-slate-100 pb-20">
      {/* Current Phase Highlight Banner */}
      <div className="bg-[#0d121c] border border-[#1e293b] rounded-xl p-4 shadow-lg">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Badge tone="amber" outline>
              Поточна фаза
            </Badge>
            <span className="text-xs font-mono text-slate-400">
              {currentPhase.hitlLevel}
            </span>
          </div>
          <span className="text-sm font-mono font-bold text-amber">
            {currentPhase.symbol}
          </span>
        </div>

        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2 font-mono">
          {currentPhase.name}
        </h2>
        <p className="text-xs text-slate-400 mt-1 leading-relaxed font-sans">
          {currentPhase.description ||
            'Автоматизований цикл перевірки архітектурних інваріантів та синхронізації бітемпоральних намірів.'}
        </p>

        {isReviewGate && (
          <div className="mt-4 pt-3 border-t border-[#1e293b]">
            <Button
              variant="primary"
              size="lg"
              className="w-full justify-between"
              icon={<ShieldAlert className="w-4 h-4" />}
              iconRight={<ArrowRight className="w-3.5 h-3.5" />}
              onClick={onOpenReviewGate}
            >
              Відкрити Human Review Gate
            </Button>
          </div>
        )}
      </div>

      {/* 7-Phase Pipeline List */}
      <div className="space-y-2">
        <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400 px-1">
          Конвеєр фаз B-SDD (HITL Φ1 - Φ7)
        </div>

        {phases.map((phase) => {
          const isSelected = phase.id === currentPhaseId;
          const isPhaseReviewGate = phase.id === 'phi_6';

          let statusBg = 'bg-[#141b27]/70 border-[#1e293b] text-slate-300';
          let statusBadge = (
            <Badge tone="neutral" outline>
              <Clock className="w-3 h-3" /> Очікує
            </Badge>
          );

          if (phase.status === 'completed') {
            statusBg = 'bg-emerald/10 border-emerald/30 text-emerald-200';
            statusBadge = (
              <Badge tone="emerald" outline>
                <CheckCircle2 className="w-3 h-3" /> Завершено
              </Badge>
            );
          } else if (phase.status === 'running') {
            statusBg = 'bg-cyan/15 border-cyan text-cyan-100 ring-1 ring-cyan';
            statusBadge = (
              <Badge tone="cyan" outline>
                <Dot tone="cyan" pulse /> В процесі
              </Badge>
            );
          } else if (phase.status === 'rejected') {
            statusBg = 'bg-rose/20 border-rose text-rose-200';
            statusBadge = (
              <Badge tone="rose" outline>
                <AlertTriangle className="w-3 h-3" /> Відхилено
              </Badge>
            );
          }

          return (
            <div
              key={phase.id}
              onClick={() => {
                onSelectPhase(phase.id);
                if (isPhaseReviewGate && (phase.status === 'running' || phase.status === 'completed')) {
                  onOpenReviewGate();
                }
              }}
              className={`p-3 rounded border flex items-center justify-between cursor-pointer transition-all ${statusBg} ${
                isSelected ? 'ring-1 ring-amber border-amber shadow-md' : 'hover:border-slate-600'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded bg-[#090d13] border border-[#1e293b] flex items-center justify-center font-mono font-bold text-amber text-xs">
                  {phase.symbol}
                </div>
                <div>
                  <div className="text-xs font-semibold text-slate-200">
                    {phase.name}
                  </div>
                  <div className="text-[10px] font-mono text-slate-400">
                    {phase.hitlLevel}
                  </div>
                </div>
              </div>

              <div>{statusBadge}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default MobilePhaseView;
