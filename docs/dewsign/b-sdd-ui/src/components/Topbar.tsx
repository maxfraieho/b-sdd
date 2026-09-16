// src/components/Topbar.tsx
import React from 'react';
import {
  Layers,
  Database,
  Cpu,
  GitBranch,
  ShieldCheck,
  Search,
  ChevronDown,
  Wifi,
} from 'lucide-react';

interface TopbarProps {
  selectedProject: string;
  onProjectChange: (project: string) => void;
  onOpenInvariantDrawer: () => void;
  invariantCount: number;
}

export const Topbar: React.FC<TopbarProps> = ({
  selectedProject,
  onProjectChange,
  onOpenInvariantDrawer,
  invariantCount,
}) => {
  return (
    <header className="h-12 bg-panel border-b border-border-subtle px-4 flex items-center justify-between shrink-0 select-none z-30">
      {/* Left: Brand & Project Selector */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-card border border-border-subtle flex items-center justify-center text-amber shadow-sm">
            <Layers className="w-4 h-4" />
          </div>
          <div className="flex flex-col">
            <span className="text-xs font-bold tracking-wider uppercase text-slate-100 font-mono">
              B-SDD COCKPIT
            </span>
            <span className="text-[10px] text-slate-400 font-mono">v0.4.2 · Sovereign</span>
          </div>
        </div>

        <div className="h-4 w-px bg-border-subtle mx-1" />

        {/* Project Selector */}
        <div className="relative group">
          <button className="flex items-center gap-2 bg-card hover:bg-slate-800 border border-border-subtle px-2.5 py-1 rounded text-xs text-slate-200 transition-colors">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-medium">{selectedProject}</span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>
          <div className="hidden group-hover:block absolute left-0 top-full mt-1 w-56 bg-card border border-border-subtle rounded-md shadow-xl py-1 z-50">
            <button
              onClick={() => onProjectChange('B-SDD Framework Core')}
              className={`w-full text-left px-3 py-1.5 text-xs hover:bg-slate-800 transition-colors flex items-center justify-between ${
                selectedProject === 'B-SDD Framework Core' ? 'text-amber font-semibold' : 'text-slate-300'
              }`}
            >
              <span>B-SDD Framework Core</span>
              <span className="text-[10px] font-mono text-slate-400">Spec 004</span>
            </button>
            <button
              onClick={() => onProjectChange('ACCORD Suisse')}
              className={`w-full text-left px-3 py-1.5 text-xs hover:bg-slate-800 transition-colors flex items-center justify-between ${
                selectedProject === 'ACCORD Suisse' ? 'text-amber font-semibold' : 'text-slate-300'
              }`}
            >
              <span>ACCORD Suisse</span>
              <span className="text-[10px] font-mono text-slate-400">Art. 262 CO</span>
            </button>
          </div>
        </div>
      </div>

      {/* Middle: Sovereign Infrastructure Health */}
      <div className="hidden md:flex items-center gap-5 text-[11px] font-mono">
        <div className="flex items-center gap-1.5 text-slate-300">
          <Database className="w-3.5 h-3.5 text-emerald-400" />
          <span>Utopia DB</span>
          <span className="text-[10px] text-slate-500">.251:9922</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
        </div>

        <div className="flex items-center gap-1.5 text-slate-300">
          <Cpu className="w-3.5 h-3.5 text-blue-400" />
          <span>LLM Gateway</span>
          <span className="text-[10px] text-slate-500">.184:18880</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
        </div>

        <div className="flex items-center gap-1.5 text-slate-300">
          <GitBranch className="w-3.5 h-3.5 text-violet-400" />
          <span>GitNexus AST</span>
          <span className="text-[10px] text-slate-500">:4747</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
        </div>
      </div>

      {/* Right: Invariant Search & Tier Badge */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenInvariantDrawer}
          className="flex items-center gap-1.5 bg-card hover:bg-slate-800 border border-border-subtle px-2.5 py-1 rounded text-xs text-slate-300 transition-colors"
          title="Search Invariant Rules"
        >
          <Search className="w-3.5 h-3.5 text-amber" />
          <span>Invariants</span>
          <span className="bg-amber/20 text-amber font-mono text-[10px] px-1.5 py-0.2 rounded">
            {invariantCount}
          </span>
        </button>

        <div className="flex items-center gap-1.5 text-[11px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded">
          <Wifi className="w-3 h-3" />
          <span>Local Parity</span>
        </div>

        <div className="flex items-center gap-1 text-[11px] font-mono text-slate-200 bg-slate-800 border border-border-subtle px-2.5 py-0.5 rounded">
          <ShieldCheck className="w-3.5 h-3.5 text-amber" />
          <span className="font-semibold">Enterprise Sovereign</span>
        </div>
      </div>
    </header>
  );
};
