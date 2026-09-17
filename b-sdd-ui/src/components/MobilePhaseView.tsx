// src/components/MobilePhaseView.tsx
import React from 'react';
import type { HitlPhase, HitlPhaseId } from '@/types/sprint';
import {
  CheckCircle2,
  Clock,
  ShieldAlert,
  AlertTriangle,
  Play,
  ArrowRight,
  Sparkles,
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
    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-canvas text-slate-100 pb-20">
      {/* Current Phase Highlight Banner */}
      <div className="bg-panel border border-border-subtle rounded-xl p-4 shadow-lg">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold uppercase text-amber bg-amber/10 px-2 py-0.5 rounded border border-amber/20">
              Поточна фаза
            </span>
            <span className="text-xs font-mono text-slate-400">
              {currentPhase.hitlLevel}
            </span>
          </div>
          <span className="text-sm font-mono font-bold text-amber">
            {currentPhase.symbol}
          </span>
        </div>

        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          {currentPhase.name}
        </h2>
        <p className="text-xs text-slate-400 mt-1 leading-relaxed">
          {currentPhase.description ||
            'Автоматизований цикл перевірки архітектурних інваріантів та синхронізації бітемпоральних намірів.'}
        </p>

        {isReviewGate && (
          <div className="mt-4 pt-3 border-t border-border-subtle">
            <button
              onClick={onOpenReviewGate}
              className="w-full py-2.5 px-4 bg-violet-600 hover:bg-violet-500 text-white rounded-lg font-bold text-xs flex items-center justify-center gap-2 shadow-lg animate-pulse transition-colors"
            >
              <ShieldAlert className="w-4 h-4" />
              <span>Відкрити Human Review Gate (Затвердити / Відхилити)</span>
              <ArrowRight className="w-3.5 h-3.5 ml-auto" />
            </button>
          </div>
        )}
      </div>

      {/* 7-Phase Pipeline List */}
      <div className="space-y-2">
        <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400 px-1">
          Конвеєр фаз B-SDD (HITL $\Phi_1 - \Phi_7$)
        </div>

        {phases.map((phase, idx) => {
          const isSelected = phase.id === currentPhaseId;
          const isPhaseReviewGate = phase.id === 'phi_6';

          let statusBg = 'bg-card/70 border-border-subtle text-slate-300';
          let statusBadge = (
            <span className="text-[10px] font-mono text-slate-500 flex items-center gap-1">
              <Clock className="w-3 h-3" /> Очікує
            </span>
          );

          if (phase.status === 'completed') {
            statusBg = 'bg-emerald-950/20 border-emerald-500/30 text-emerald-200';
            statusBadge = (
              <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> Завершено
              </span>
            );
          } else if (phase.status === 'running') {
            statusBg = 'bg-blue-950/30 border-blue-500 text-blue-100 ring-1 ring-blue-500';
            statusBadge = (
              <span className="text-[10px] font-mono text-blue-400 flex items-center gap-1 font-bold animate-pulse">
                <Play className="w-3 h-3" /> В процесі
              </span>
            );
          } else if (phase.status === 'rejected') {
            statusBg = 'bg-rose-950/30 border-rose-500 text-rose-200';
            statusBadge = (
              <span className="text-[10px] font-mono text-rose-400 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" /> Відхилено
              </span>
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
              className={`p-3 rounded-lg border flex items-center justify-between cursor-pointer transition-all ${statusBg} ${
                isSelected ? 'ring-2 ring-amber ring-offset-1 ring-offset-canvas' : ''
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-md bg-canvas/80 border border-border-subtle flex items-center justify-center font-mono font-bold text-amber text-xs">
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
