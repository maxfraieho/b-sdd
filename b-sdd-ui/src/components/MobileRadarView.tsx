// src/components/MobileRadarView.tsx
import React from 'react';
import type { BitemporalAdr } from '@/types/adr';
import { TimelineSlider } from './BitemporalRadar/TimelineSlider';
import { BookOpen, CheckCircle2, AlertTriangle, ShieldCheck, ArrowUpRight } from 'lucide-react';

interface MobileRadarViewProps {
  adrs: BitemporalAdr[];
  validTimeDay: number;
  onValidTimeChange: (day: number) => void;
  txTimeDay: number;
  onTxTimeChange: (day: number) => void;
  selectedAdrId?: string;
  onSelectAdr: (adr: BitemporalAdr) => void;
  onOpenAdrLibrary: () => void;
}

export const MobileRadarView: React.FC<MobileRadarViewProps> = ({
  adrs,
  validTimeDay,
  onValidTimeChange,
  txTimeDay,
  onTxTimeChange,
  selectedAdrId,
  onSelectAdr,
  onOpenAdrLibrary,
}) => {
  const activeAdrs = adrs.filter((a) => a.status === 'accepted');
  const supersededAdrs = adrs.filter((a) => a.status === 'superseded');

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-canvas text-slate-100 pb-20">
      {/* 1. Header Banner & Open Library */}
      <div className="flex items-center justify-between bg-panel border border-border-subtle rounded-xl p-3 shadow-md">
        <div>
          <h2 className="text-sm font-bold text-slate-100 font-mono flex items-center gap-2">
            <span>Бітемпоральний радар</span>
            <span className="text-[10px] text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-500/30">
              Tv / Tt
            </span>
          </h2>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Двовісний аналіз еволюції архітектурних рішень
          </p>
        </div>

        <button
          onClick={onOpenAdrLibrary}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-950/30 hover:bg-emerald-950/50 border border-emerald-500/30 text-emerald-300 text-xs font-mono font-semibold transition-colors"
        >
          <BookOpen className="w-3.5 h-3.5" />
          <span>Всі ADR</span>
        </button>
      </div>

      {/* 2. Touch-Friendly Timeline Slider */}
      <div className="bg-panel border border-border-subtle rounded-xl overflow-hidden shadow-md">
        <TimelineSlider
          validTimeDay={validTimeDay}
          onValidTimeChange={onValidTimeChange}
          txTimeDay={txTimeDay}
          onTxTimeChange={onTxTimeChange}
          activeAdrCount={activeAdrs.length}
          supersededCount={supersededAdrs.length}
        />
      </div>

      {/* 3. ADR Decision Cards List for Active Time */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-[11px] font-mono uppercase tracking-wider text-slate-400 px-1">
          <span>Рішення ADR на стані T_v = 2026-09-{String(validTimeDay).padStart(2, '0')}</span>
          <span>{adrs.length} рішень</span>
        </div>

        {adrs.map((adr) => {
          const isSelected = adr.id === selectedAdrId;
          const isSuperseded = adr.status === 'superseded';

          return (
            <div
              key={adr.id}
              onClick={() => onSelectAdr(adr)}
              className={`p-3 rounded-lg border cursor-pointer transition-all ${
                isSuperseded
                  ? 'bg-card/40 border-border-subtle/60 opacity-70 text-slate-400'
                  : 'bg-panel border-border-subtle text-slate-200 hover:border-slate-500'
              } ${isSelected ? 'ring-2 ring-amber border-amber bg-card' : ''}`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono text-xs font-bold text-amber flex items-center gap-1.5">
                  <span>{adr.id}</span>
                  {isSuperseded && (
                    <span className="text-[9px] font-normal uppercase bg-rose-950/40 text-rose-300 px-1.5 py-0.2 rounded border border-rose-500/30">
                      Замінено
                    </span>
                  )}
                  {!isSuperseded && (
                    <span className="text-[9px] font-normal uppercase bg-emerald-950/40 text-emerald-300 px-1.5 py-0.2 rounded border border-emerald-500/30">
                      Активне
                    </span>
                  )}
                </span>

                <ArrowUpRight className="w-3.5 h-3.5 text-slate-500" />
              </div>

              <div className="text-xs font-semibold text-slate-100 line-clamp-1">
                {adr.title}
              </div>

              {adr.invariants && adr.invariants.length > 0 && (
                <div className="mt-2 pt-2 border-t border-border-subtle/50 flex items-center gap-1.5 text-[10px] font-mono text-slate-400">
                  <ShieldCheck className="w-3 h-3 text-violet-400" />
                  <span>{adr.invariants.length} критичних інваріантів</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default MobileRadarView;
