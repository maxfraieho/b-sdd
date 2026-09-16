// src/components/CopilotPanel/TokenGauge.tsx
import React from 'react';
import type { TokenBudget } from '@/types/copilot';
import { Gauge } from 'lucide-react';

interface TokenGaugeProps {
  budget: TokenBudget;
}

export const TokenGauge: React.FC<TokenGaugeProps> = ({ budget }) => {
  const percentage = Math.min(Math.round((budget.currentWords / budget.maxWords) * 100), 100);

  let barColor = 'bg-emerald-500';
  let textColor = 'text-emerald-400';

  if (budget.currentWords >= budget.maxWords) {
    barColor = 'bg-rose-500 animate-pulse';
    textColor = 'text-rose-400 font-bold';
  } else if (budget.currentWords >= 450) {
    barColor = 'bg-amber';
    textColor = 'text-amber font-semibold';
  }

  return (
    <div className="bg-card border border-border-subtle rounded-lg p-3 select-none">
      <div className="flex items-center justify-between text-xs mb-1.5">
        <div className="flex items-center gap-1.5 text-slate-300">
          <Gauge className="w-3.5 h-3.5 text-amber" />
          <span className="font-medium font-mono text-[11px]">Active Rules Token Budget</span>
        </div>
        <div className="font-mono text-xs">
          <span className={textColor}>{budget.currentWords}</span>
          <span className="text-slate-500"> / {budget.maxWords} words</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-2 bg-canvas rounded-full overflow-hidden border border-border-subtle">
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
