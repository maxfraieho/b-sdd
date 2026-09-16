// src/components/BitemporalRadar/TimelineSlider.tsx
import React from 'react';
import { Calendar, History, RotateCcw, Play, Pause } from 'lucide-react';

interface TimelineSliderProps {
  validTimeDay: number; // 1 to 16 (representing Sept 1 - Sept 16, 2026)
  onValidTimeChange: (day: number) => void;
  txTimeDay: number;
  onTxTimeChange: (day: number) => void;
  activeAdrCount: number;
  supersededCount: number;
}

export const TimelineSlider: React.FC<TimelineSliderProps> = ({
  validTimeDay,
  onValidTimeChange,
  txTimeDay,
  onTxTimeChange,
  activeAdrCount,
  supersededCount,
}) => {
  const [isPlaying, setIsPlaying] = React.useState(false);

  React.useEffect(() => {
    if (!isPlaying) return;
    const timer = setInterval(() => {
      onValidTimeChange(validTimeDay >= 16 ? 1 : validTimeDay + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [isPlaying, validTimeDay, onValidTimeChange]);

  const validDateFormatted = `2026-09-${String(validTimeDay).padStart(2, '0')} 18:00 UTC`;
  const txDateFormatted = `2026-09-${String(txTimeDay).padStart(2, '0')} 18:00 UTC`;

  return (
    <div className="bg-panel border-t border-border-subtle p-3 flex flex-col md:flex-row items-center gap-4 select-none">
      {/* Left: Indicator & Playback */}
      <div className="flex items-center gap-3 shrink-0">
        <button
          onClick={() => setIsPlaying(!isPlaying)}
          className="p-2 rounded bg-card hover:bg-slate-800 border border-border-subtle text-amber transition-colors"
          title={isPlaying ? 'Pause Timeline' : 'Play Timeline'}
        >
          {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
        </button>

        <button
          onClick={() => {
            setIsPlaying(false);
            onValidTimeChange(16);
            onTxTimeChange(16);
          }}
          className="p-2 rounded bg-card hover:bg-slate-800 border border-border-subtle text-slate-400 hover:text-slate-200 transition-colors"
          title="Reset to NOW (Live State)"
        >
          <RotateCcw className="w-4 h-4" />
        </button>

        <div className="flex flex-col">
          <span className="text-[10px] uppercase font-mono text-slate-500 font-bold">
            Bitemporal Lens
          </span>
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="text-emerald-400 font-bold">{activeAdrCount} Active</span>
            <span className="text-slate-500">·</span>
            <span className="text-slate-400">{supersededCount} Superseded</span>
          </div>
        </div>
      </div>

      {/* Center: Dual-axis Scrubbers */}
      <div className="flex-1 w-full grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Valid Time (Tv) Slider */}
        <div className="bg-card border border-border-subtle rounded-lg p-2.5 flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
              <Calendar className="w-3.5 h-3.5" />
              <span>Valid Time (T_v):</span>
            </span>
            <span className="text-slate-300 font-bold text-[11px]">{validDateFormatted}</span>
          </div>

          <input
            type="range"
            min={1}
            max={16}
            value={validTimeDay}
            onChange={(e) => onValidTimeChange(Number(e.target.value))}
            className="w-full accent-emerald-400 cursor-pointer h-1.5 bg-canvas rounded-lg appearance-none"
          />

          <div className="flex justify-between text-[9px] text-slate-500 font-mono">
            <span>2026-09-01 (Genesis)</span>
            <span>2026-09-16 (NOW)</span>
          </div>
        </div>

        {/* Transaction Time (Tt) Slider */}
        <div className="bg-card border border-border-subtle rounded-lg p-2.5 flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="flex items-center gap-1.5 text-blue-400 font-semibold">
              <History className="w-3.5 h-3.5" />
              <span>Transaction Time (T_t):</span>
            </span>
            <span className="text-slate-300 font-bold text-[11px]">{txDateFormatted}</span>
          </div>

          <input
            type="range"
            min={1}
            max={16}
            value={txTimeDay}
            onChange={(e) => onTxTimeChange(Number(e.target.value))}
            className="w-full accent-blue-400 cursor-pointer h-1.5 bg-canvas rounded-lg appearance-none"
          />

          <div className="flex justify-between text-[9px] text-slate-500 font-mono">
            <span>Snapshot: Commit Log</span>
            <span>Utopia DB Ledger</span>
          </div>
        </div>
      </div>
    </div>
  );
};
