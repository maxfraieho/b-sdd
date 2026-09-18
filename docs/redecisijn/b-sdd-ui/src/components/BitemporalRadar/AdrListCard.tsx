// src/components/BitemporalRadar/AdrListCard.tsx
import React from 'react';
import type { BitemporalAdr } from '@/types/adr';
import { FileText, ArrowRight, ShieldCheck, AlertOctagon } from 'lucide-react';

interface AdrListCardProps {
  adrs: BitemporalAdr[];
  validTimeDay: number;
  onSelectAdr: (adr: BitemporalAdr) => void;
  selectedAdrId?: string;
}

export const AdrListCard: React.FC<AdrListCardProps> = ({
  adrs,
  validTimeDay,
  onSelectAdr,
  selectedAdrId,
}) => {
  // Determine if ADR is active given the scrubbed validTimeDay
  // Genesis is day 1 (Sept 1), day 16 is Sept 16
  const isAdrActive = (adr: BitemporalAdr) => {
    const day = parseInt(adr.date.split('-')[2], 10);
    if (day > validTimeDay) return false; // Not yet valid
    if (adr.valid_to) {
      const endDay = parseInt(adr.valid_to.split('T')[0].split('-')[2], 10);
      if (validTimeDay >= endDay) return false; // Superseded
    }
    return true;
  };

  return (
    <div className="flex items-center gap-2 overflow-x-auto py-1 px-3 select-none">
      {adrs.map((adr) => {
        const active = isAdrActive(adr);
        const isSelected = adr.id === selectedAdrId;

        return (
          <div
            key={adr.id}
            onClick={() => onSelectAdr(adr)}
            className={`cursor-pointer shrink-0 w-64 p-2.5 rounded-lg border text-xs transition-all ${
              active
                ? isSelected
                  ? 'bg-emerald-950/40 border-emerald-400 ring-1 ring-emerald-400 shadow-md'
                  : 'bg-card hover:bg-slate-800 border-border-subtle hover:border-emerald-500/50'
                : 'bg-canvas/50 border-border-subtle/40 opacity-50 grayscale'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-1.5">
                <FileText className={`w-3.5 h-3.5 ${active ? 'text-amber' : 'text-slate-500'}`} />
                <span className="font-mono font-bold text-slate-100">{adr.id}</span>
              </div>
              <span
                className={`text-[9px] font-mono uppercase px-1.5 py-0.2 rounded border ${
                  active
                    ? 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10'
                    : 'text-slate-500 border-slate-700 bg-slate-900 line-through'
                }`}
              >
                {active ? 'Active' : 'Superseded'}
              </span>
            </div>

            <h4
              className={`font-medium text-[11px] truncate ${
                active ? 'text-slate-200' : 'text-slate-500 line-through'
              }`}
              title={adr.title}
            >
              {adr.title}
            </h4>

            {adr.superseded_by && (
              <div className="flex items-center gap-1 text-[10px] text-amber/80 font-mono mt-1">
                <span>Superseded by</span>
                <ArrowRight className="w-2.5 h-2.5" />
                <span className="font-bold">{adr.superseded_by}</span>
              </div>
            )}

            <div className="flex items-center justify-between text-[10px] text-slate-500 mt-2 font-mono">
              <span className="flex items-center gap-1">
                <ShieldCheck className="w-3 h-3 text-emerald-500/70" />
                <span>{adr.invariants.length} Invariants</span>
              </span>
              <span>{adr.date}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
