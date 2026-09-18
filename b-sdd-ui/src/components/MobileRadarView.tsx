// src/components/MobileRadarView.tsx
// Astryx-native Mobile Radar Cockpit (ADR-009)
import React from 'react';
import type { BitemporalAdr } from '@/types/adr';
import { TimelineSlider } from './BitemporalRadar/TimelineSlider';
import { Button, Badge } from './astryx/primitives';
import { BookOpen, ShieldCheck, ArrowUpRight } from 'lucide-react';

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
    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-[#090d13] text-slate-100 pb-20">
      {/* 1. Header Banner & Open Library */}
      <div className="flex items-center justify-between bg-[#0d121c] border border-[#1e293b] rounded-xl p-3 shadow-md">
        <div>
          <h2 className="text-sm font-bold text-slate-100 font-mono flex items-center gap-2">
            <span>Бітемпоральний радар</span>
            <Badge tone="cyan" outline>Tv / Tt</Badge>
          </h2>
          <p className="text-[11px] text-slate-400 mt-0.5 font-sans">
            Двовісний аналіз еволюції архітектурних рішень
          </p>
        </div>

        <Button
          variant="secondary"
          size="sm"
          icon={<BookOpen className="w-3.5 h-3.5" />}
          onClick={onOpenAdrLibrary}
        >
          Всі ADR
        </Button>
      </div>

      {/* 2. Touch-Friendly Timeline Slider */}
      <div className="bg-[#0d121c] border border-[#1e293b] rounded-xl overflow-hidden shadow-md">
        <TimelineSlider
          validTimeDay={validTimeDay}
          onValidTimeChange={onValidTimeChange}
          txTimeDay={txTimeDay}
          onTxTimeChange={onTxTimeChange}
          adrs={adrs}
          activeAdrCount={activeAdrs.length}
          supersededCount={supersededAdrs.length}
          onSelectAdr={onSelectAdr}
          selectedAdrId={selectedAdrId}
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
              className={`p-3 rounded border cursor-pointer transition-all ${
                isSuperseded
                  ? 'bg-[#141b27]/40 border-[#1e293b]/60 opacity-70 text-slate-400'
                  : 'bg-[#0d121c] border-[#1e293b] text-slate-200 hover:border-slate-500'
              } ${isSelected ? 'ring-1 ring-amber border-amber bg-[#141b27]' : ''}`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono text-xs font-bold text-amber flex items-center gap-1.5">
                  <span>{adr.id}</span>
                  {isSuperseded ? (
                    <Badge tone="rose" outline>Замінено</Badge>
                  ) : (
                    <Badge tone="emerald" outline>Активне</Badge>
                  )}
                </span>

                <ArrowUpRight className="w-3.5 h-3.5 text-slate-500" />
              </div>

              <div className="text-xs font-semibold text-slate-100 line-clamp-1 font-mono">
                {adr.title}
              </div>

              {adr.invariants && adr.invariants.length > 0 && (
                <div className="mt-2 pt-2 border-t border-[#1e293b]/50 flex items-center gap-1.5 text-[10px] font-mono text-slate-400">
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
