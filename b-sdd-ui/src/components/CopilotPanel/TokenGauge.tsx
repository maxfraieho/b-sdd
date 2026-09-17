// src/components/CopilotPanel/TokenGauge.tsx
// Astryx-native Active Rules Token Budget Gauge (ADR-002, ADR-009)
import React from 'react';
import type { TokenBudget } from '@/types/copilot';
import { Gauge } from 'lucide-react';
import { Badge } from '@/components/astryx/primitives';

interface TokenGaugeProps {
  budget: TokenBudget;
}

export const TokenGauge: React.FC<TokenGaugeProps> = ({ budget }) => {
  const percentage = Math.min(Math.round((budget.currentWords / budget.maxWords) * 100), 100);

  let barColor = 'bg-emerald';
  let tone: 'emerald' | 'amber' | 'rose' = 'emerald';

  if (budget.currentWords >= budget.maxWords) {
    barColor = 'bg-rose animate-pulse';
    tone = 'rose';
  } else if (budget.currentWords >= 450) {
    barColor = 'bg-amber';
    tone = 'amber';
  }

  return (
    <div className="bg-[#141b27] border border-[#1e293b] rounded p-3 select-none">
      <div className="flex items-center justify-between text-xs mb-1.5 font-mono">
        <div className="flex items-center gap-1.5 text-slate-300">
          <Gauge className="w-3.5 h-3.5 text-amber" />
          <span className="font-medium text-[11px]">Active Rules Token Budget</span>
        </div>
        <div className="flex items-center gap-1">
          <Badge tone={tone} outline>
            {budget.currentWords} / {budget.maxWords} words
          </Badge>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-2 bg-[#090d13] rounded-full overflow-hidden border border-[#1e293b]">
        <div
          className={`h-full transition-all duration-300 ${barColor}`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="flex items-center justify-between text-[10px] text-slate-500 mt-1 font-mono">
        <span>ADR-002 Strict Invariant</span>
        <span>{percentage}% Budget Allocated</span>
      </div>
    </div>
  );
};
