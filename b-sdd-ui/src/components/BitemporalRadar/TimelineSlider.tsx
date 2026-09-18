// src/components/BitemporalRadar/TimelineSlider.tsx
// -----------------------------------------------------------------------------
// ZONE D — Bitemporal Timeline (Astryx High-Tech Dark)
// Redesign: жорстка 2-колонкова структура. Ліва панель = слоти дат + керування.
// Права стрічка = скролюється горизонтально; ADR-картки більше НЕ накладаються
// на панель дат через `flex-shrink-0` + `overflow-x-auto` + `min-w-0`.
// Інваріант FE-INV-01: без вертикального скролу сторінки.
// -----------------------------------------------------------------------------
import React from 'react';
import type { BitemporalAdr } from '@/types/adr';
import { AdrTimelineCard } from './AdrListCard';
import { UtopiaDagCanvas } from './UtopiaDagCanvas';
import {
  Calendar,
  History,
  Play,
  Pause,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

interface TimelineSliderProps {
  validTimeDay: number;
  onValidTimeChange: (day: number) => void;
  txTimeDay: number;
  onTxTimeChange: (day: number) => void;
  adrs: BitemporalAdr[];
  activeAdrCount: number;
  supersededCount: number;
  onSelectAdr: (adr: BitemporalAdr) => void;
  selectedAdrId?: string;
  minDay?: number;
  maxDay?: number;
}

export const TimelineSlider: React.FC<TimelineSliderProps> = ({
  validTimeDay,
  onValidTimeChange,
  txTimeDay,
  onTxTimeChange,
  adrs,
  activeAdrCount,
  supersededCount,
  onSelectAdr,
  selectedAdrId,
  minDay = 1,
  maxDay,
}) => {
  const [isPlaying, setIsPlaying] = React.useState(false);
  const [viewMode, setViewMode] = React.useState<'cards' | 'dag'>('cards');
  const maxLimit = maxDay ?? 17;
  const minLimit = minDay;
  const railRef = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    if (!isPlaying) return;
    const timer = window.setInterval(() => {
      onValidTimeChange(validTimeDay >= maxLimit ? minLimit : validTimeDay + 1);
    }, 900);
    return () => window.clearInterval(timer);
  }, [isPlaying, validTimeDay, onValidTimeChange, maxLimit, minLimit]);

  const validDate = `2026-09-${String(validTimeDay).padStart(2, '0')}`;
  const txDate = `2026-09-${String(txTimeDay).padStart(2, '0')}`;

  const step = (delta: number) => {
    const next = Math.min(maxLimit, Math.max(minLimit, validTimeDay + delta));
    onValidTimeChange(next);
  };

  const scrollRail = (dir: 1 | -1) => {
    railRef.current?.scrollBy({ left: dir * 320, behavior: 'smooth' });
  };

  return (
    <section
      aria-label="Bitemporal Timeline (Zone D)"
      className="flex border-t border-[#1e293b] bg-[#090d13] shrink-0"
      style={{ height: 168 }}
    >
      {/* ================================================================== */}
      {/* LEFT COLUMN — фіксована ширина, без переносу, границя праворуч       */}
      {/* ================================================================== */}
      <aside className="w-64 flex-shrink-0 border-r border-[#1e293b] bg-[#0d121c] p-3 flex flex-col gap-2">
        {/* Header — bitemporal label + лічильники + перемикач Cards / DAG */}
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-mono uppercase tracking-widest text-[#f59e0b] font-bold">
            Bitemporal Lens
          </span>
          <div className="flex items-center bg-[#141b27] p-0.5 rounded border border-[#1e293b]">
            <button
              onClick={() => setViewMode('cards')}
              className={`px-1.5 py-0.5 rounded text-[9px] font-mono transition-colors ${
                viewMode === 'cards'
                  ? 'bg-[#3b82f6] text-white font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Cards Rail View"
            >
              Cards
            </button>
            <button
              onClick={() => setViewMode('dag')}
              className={`px-1.5 py-0.5 rounded text-[9px] font-mono transition-colors ${
                viewMode === 'dag'
                  ? 'bg-[#f59e0b] text-slate-900 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Utopia DB DAG View"
            >
              DAG
            </button>
          </div>
        </div>

        {/* Слот T_v */}
        <div className="rounded-md border border-[#1e293b] bg-[#141b27] px-2.5 py-1.5">
          <div className="flex items-center justify-between mb-1">
            <span className="flex items-center gap-1.5 text-[10px] font-mono font-semibold text-[#10b981]">
              <span className="relative flex w-2 h-2">
                <span className="absolute inset-0 rounded-full bg-[#10b981] opacity-70 animate-ping" />
                <span className="relative w-2 h-2 rounded-full bg-[#10b981]" />
              </span>
              <Calendar className="w-3 h-3" />
              T_v
            </span>
            <span className="text-[11px] font-mono font-bold text-slate-100 tabular-nums">
              {validDate}
            </span>
          </div>
          <input
            type="range"
            min={minLimit}
            max={maxLimit}
            value={validTimeDay}
            onChange={(e) => onValidTimeChange(Number(e.target.value))}
            className="w-full h-1 appearance-none rounded bg-[#0d121c] accent-[#10b981] cursor-pointer"
            aria-label="Valid Time scrubber"
          />
        </div>

        {/* Слот T_t */}
        <div className="rounded-md border border-[#1e293b] bg-[#141b27] px-2.5 py-1.5">
          <div className="flex items-center justify-between mb-1">
            <span className="flex items-center gap-1.5 text-[10px] font-mono font-semibold text-[#06b6d4]">
              <span className="relative flex w-2 h-2">
                <span className="absolute inset-0 rounded-full bg-[#06b6d4] opacity-70 animate-ping" />
                <span className="relative w-2 h-2 rounded-full bg-[#06b6d4]" />
              </span>
              <History className="w-3 h-3" />
              T_t
            </span>
            <span className="text-[11px] font-mono font-bold text-slate-100 tabular-nums">
              {txDate}
            </span>
          </div>
          <input
            type="range"
            min={minLimit}
            max={maxLimit}
            value={txTimeDay}
            onChange={(e) => onTxTimeChange(Number(e.target.value))}
            className="w-full h-1 appearance-none rounded bg-[#0d121c] accent-[#06b6d4] cursor-pointer"
            aria-label="Transaction Time scrubber"
          />
        </div>

        {/* Керування Play/Step/Reset */}
        <div className="mt-auto flex items-center gap-1">
          <button
            onClick={() => step(-1)}
            className="flex-1 h-7 rounded border border-[#1e293b] bg-[#141b27] hover:bg-[#1a2233] text-slate-300 flex items-center justify-center transition-colors"
            title="Step back 1 day"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setIsPlaying((v) => !v)}
            className={`flex-1 h-7 rounded border flex items-center justify-center gap-1 font-mono text-[10px] font-bold transition-colors ${
              isPlaying
                ? 'bg-[#f59e0b]/15 border-[#f59e0b]/50 text-[#f59e0b]'
                : 'bg-[#141b27] border-[#1e293b] text-slate-300 hover:bg-[#1a2233]'
            }`}
            title={isPlaying ? 'Pause Timeline' : 'Play Timeline'}
          >
            {isPlaying ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
            {isPlaying ? 'PAUSE' : 'PLAY'}
          </button>
          <button
            onClick={() => step(1)}
            className="flex-1 h-7 rounded border border-[#1e293b] bg-[#141b27] hover:bg-[#1a2233] text-slate-300 flex items-center justify-center transition-colors"
            title="Step forward 1 day"
          >
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => {
              setIsPlaying(false);
              onValidTimeChange(maxLimit);
              onTxTimeChange(maxLimit);
            }}
            className="w-7 h-7 rounded border border-[#1e293b] bg-[#141b27] hover:bg-[#1a2233] text-slate-400 hover:text-slate-100 flex items-center justify-center transition-colors"
            title="Reset to NOW (Live)"
          >
            <RotateCcw className="w-3 h-3" />
          </button>
        </div>
      </aside>

      {/* ================================================================== */}
      {/* RIGHT COLUMN — flex-1 min-w-0, Cards Rail OR Utopia DAG Canvas    */}
      {/* ================================================================== */}
      {viewMode === 'dag' ? (
        <UtopiaDagCanvas
          validTimeDay={validTimeDay}
          adrs={adrs}
          selectedAdrId={selectedAdrId}
          onSelectAdr={onSelectAdr}
        />
      ) : (
        <div className="flex-1 min-w-0 relative flex items-center">
          {/* subtle grid */}
          <div
            aria-hidden
            className="absolute inset-0 pointer-events-none opacity-40"
            style={{
              backgroundImage:
                'linear-gradient(to right, #1e293b 1px, transparent 1px)',
              backgroundSize: '80px 100%',
            }}
          />

          {/* left/right rail nav */}
          <button
            onClick={() => scrollRail(-1)}
            className="absolute left-1 z-10 w-6 h-6 rounded-full bg-[#0d121c]/90 border border-[#1e293b] text-slate-400 hover:text-slate-100 flex items-center justify-center"
            title="Scroll rail left"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => scrollRail(1)}
            className="absolute right-1 z-10 w-6 h-6 rounded-full bg-[#0d121c]/90 border border-[#1e293b] text-slate-400 hover:text-slate-100 flex items-center justify-center"
            title="Scroll rail right"
          >
            <ChevronRight className="w-3.5 h-3.5" />
          </button>

          <div
            ref={railRef}
            className="flex-1 overflow-x-auto overflow-y-hidden p-3 flex gap-3 items-center min-w-0 scroll-smooth"
          >
            {adrs.map((adr) => (
              <AdrTimelineCard
                key={adr.id}
                adr={adr}
                validTimeDay={validTimeDay}
                onSelect={onSelectAdr}
                selected={adr.id === selectedAdrId}
              />
            ))}
          </div>
        </div>
      )}
    </section>
  );
};

export default TimelineSlider;
