// src/components/BitemporalRadar/AdrListCard.tsx
// -----------------------------------------------------------------------------
// ZONE D — Fixed-width bitemporal ADR card. Використовується всередині стрічки
// TimelineSlider. `flex-shrink-0` + фіксована ширина гарантує, що картки НЕ
// заходять під ліву панель дат.
// -----------------------------------------------------------------------------
import React from 'react';
import type { BitemporalAdr } from '@/types/adr';
import { FileText, ArrowRight, ShieldCheck } from 'lucide-react';

interface AdrTimelineCardProps {
  adr: BitemporalAdr;
  validTimeDay: number;
  onSelect: (adr: BitemporalAdr) => void;
  selected?: boolean;
}

const parseDay = (iso: string) => parseInt(iso.split('T')[0].split('-')[2], 10);

export const AdrTimelineCard: React.FC<AdrTimelineCardProps> = ({
  adr,
  validTimeDay,
  onSelect,
  selected = false,
}) => {
  const startDay = parseDay(adr.date);
  const endDay = adr.valid_to ? parseDay(adr.valid_to) : null;

  const notYet = startDay > validTimeDay;
  const superseded = endDay !== null && validTimeDay >= endDay;
  const active = !notYet && !superseded;

  const state: 'active' | 'superseded' | 'pending' = active
    ? 'active'
    : superseded
      ? 'superseded'
      : 'pending';

  const stateStyles = {
    active: selected
      ? 'bg-[#10b981]/10 border-[#10b981] ring-1 ring-[#10b981]/40 shadow-[0_0_0_1px_rgba(16,185,129,0.15)]'
      : 'bg-[#141b27] border-[#1e293b] hover:border-[#10b981]/50',
    superseded: 'bg-[#0d121c]/60 border-[#1e293b] opacity-55',
    pending: 'bg-[#0d121c] border-dashed border-[#1e293b] opacity-70',
  }[state];

  return (
    <button
      type="button"
      onClick={() => onSelect(adr)}
      className={`shrink-0 w-56 text-left rounded-lg border px-3 py-2.5 transition-all font-sans ${stateStyles}`}
    >
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center gap-1.5 min-w-0">
          <FileText
            className={`w-3.5 h-3.5 shrink-0 ${
              state === 'active' ? 'text-[#f59e0b]' : 'text-slate-500'
            }`}
          />
          <span className="font-mono font-bold text-[12px] text-slate-100 truncate">
            {adr.id}
          </span>
        </div>
        <span
          className={`text-[9px] font-mono uppercase px-1.5 py-0.5 rounded border tracking-wider ${
            state === 'active'
              ? 'text-[#10b981] border-[#10b981]/40 bg-[#10b981]/10'
              : state === 'superseded'
                ? 'text-slate-500 border-slate-700 bg-slate-900/60 line-through'
                : 'text-[#06b6d4] border-[#06b6d4]/40 bg-[#06b6d4]/10'
          }`}
        >
          {state === 'active' ? 'Active' : state === 'superseded' ? 'Sup.' : 'Pending'}
        </span>
      </div>

      <h4
        className={`font-medium text-[11px] leading-snug line-clamp-2 ${
          state === 'active' ? 'text-slate-200' : 'text-slate-500'
        }`}
        title={adr.title}
      >
        {adr.title}
      </h4>

      {adr.superseded_by && (
        <div className="flex items-center gap-1 text-[10px] text-[#f59e0b]/80 font-mono mt-1.5">
          <span>→</span>
          <ArrowRight className="w-2.5 h-2.5" />
          <span className="font-bold">{adr.superseded_by}</span>
        </div>
      )}

      <div className="flex items-center justify-between text-[10px] text-slate-500 mt-2 font-mono">
        <span className="flex items-center gap-1">
          <ShieldCheck className="w-3 h-3 text-[#10b981]/70" />
          {adr.invariants.length}
        </span>
        <span className="tabular-nums">{adr.date}</span>
      </div>
    </button>
  );
};

export default AdrTimelineCard;
