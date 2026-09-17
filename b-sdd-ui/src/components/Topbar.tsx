// src/components/Topbar.tsx
import React from 'react';
import type { ProjectInfo, SpecItem } from '@/types/specs';
import {
  Layers,
  Database,
  Cpu,
  GitBranch,
  ShieldCheck,
  ListTodo,
  BookOpen,
  ChevronDown,
  FolderGit2,
  RefreshCw,
  Loader2,
} from 'lucide-react';

interface TopbarProps {
  projectInfo: ProjectInfo | null;
  specs: SpecItem[];
  selectedSpecId: string;
  onSelectSpec: (specId: string) => void;
  onOpenTasksDrawer: () => void;
  onOpenAdrLibrary: () => void;
  onOpenInvariantDrawer: () => void;
  invariantCount: number;
  utopiaOnline?: boolean;
  llmOnline?: boolean;
  onSyncUtopia?: () => Promise<void>;
  isSyncingUtopia?: boolean;
}

export const Topbar: React.FC<TopbarProps> = ({
  projectInfo,
  specs,
  selectedSpecId,
  onSelectSpec,
  onOpenTasksDrawer,
  onOpenAdrLibrary,
  onOpenInvariantDrawer,
  invariantCount,
  utopiaOnline = true,
  llmOnline = true,
  onSyncUtopia,
  isSyncingUtopia = false,
}) => {
  const currentSpec = specs.find((s) => s.id === selectedSpecId) || specs[0] || null;
  const totalTasks = specs.reduce((sum, s) => sum + s.tasks_count, 0);
  const completedTasks = specs.reduce((sum, s) => sum + s.completed_count, 0);

  return (
    <header className="h-12 bg-panel border-b border-border-subtle px-4 flex items-center justify-between shrink-0 select-none z-30">
      {/* Left: Brand & Real Workspace Context */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-card border border-border-subtle flex items-center justify-center text-amber shadow-sm">
            <Layers className="w-4 h-4" />
          </div>
          <div className="flex flex-col">
            <span className="text-xs font-bold tracking-wider uppercase text-slate-100 font-mono">
              B-SDD COCKPIT
            </span>
            <span className="text-[10px] text-slate-400 font-mono">Operator Workbench · v1.0</span>
          </div>
        </div>

        <div className="h-4 w-px bg-border-subtle mx-1" />

        {/* Real Workspace & Branch */}
        <div className="flex items-center gap-2 bg-card border border-border-subtle px-2.5 py-1 rounded-lg text-xs font-mono">
          <FolderGit2 className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-200 font-semibold">{projectInfo?.name || 'b-sdd'}</span>
          <span className="text-slate-500">·</span>
          <span className="text-emerald-400 flex items-center gap-1">
            <GitBranch className="w-3 h-3" />
            {projectInfo?.branch || 'master'}
          </span>
          {projectInfo?.commit && (
            <span className="text-slate-500 text-[10px]">({projectInfo.commit})</span>
          )}
        </div>

        {/* Active Spec Selector */}
        {specs.length > 0 && (
          <div className="relative group">
            <button className="flex items-center gap-1.5 bg-card hover:bg-slate-800 border border-border-subtle px-2.5 py-1 rounded-lg text-xs text-slate-200 font-mono transition-colors">
              <span className="text-amber font-semibold">
                {currentSpec?.id.split('-')[0] || 'Spec 004'}
              </span>
              <span className="text-slate-400 truncate max-w-[140px]">
                {currentSpec?.title || 'Multi-Session'}
              </span>
              <ChevronDown className="w-3 h-3 text-slate-400" />
            </button>
            <div className="hidden group-hover:block absolute left-0 top-full mt-1 w-64 bg-card border border-border-subtle rounded-lg shadow-xl py-1 z-50">
              <div className="px-3 py-1 text-[10px] font-mono uppercase text-slate-500 border-b border-border-subtle">
                Активні специфікації (specs/)
              </div>
              {specs.map((spec) => (
                <button
                  key={spec.id}
                  onClick={() => onSelectSpec(spec.id)}
                  className={`w-full text-left px-3 py-1.5 text-xs hover:bg-slate-800 transition-colors flex items-center justify-between font-mono ${
                    spec.id === currentSpec?.id ? 'text-amber font-semibold bg-amber/5' : 'text-slate-300'
                  }`}
                >
                  <span className="truncate">{spec.title}</span>
                  <span className="text-[10px] text-slate-400 ml-2">
                    {spec.completed_count}/{spec.tasks_count}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Middle: Sovereign Infrastructure Health & On-Demand Sync */}
      <div className="hidden lg:flex items-center gap-3 text-[11px] font-mono">
        <div className="flex items-center gap-2 bg-card border border-border-subtle px-2.5 py-1 rounded-lg">
          <div className="flex items-center gap-1.5 text-slate-300">
            <Database className={`w-3.5 h-3.5 ${utopiaOnline ? 'text-emerald-400' : 'text-rose-400'}`} />
            <span>Utopia DB</span>
            <span className="text-[10px] text-slate-500">.251:9922</span>
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                utopiaOnline ? 'bg-emerald-400' : 'bg-rose-400 animate-pulse'
              }`}
            />
          </div>
          {onSyncUtopia && (
            <button
              onClick={() => void onSyncUtopia()}
              disabled={isSyncingUtopia}
              className="text-[10px] text-amber hover:underline flex items-center gap-1 px-1.5 py-0.5 rounded bg-amber/10 hover:bg-amber/20 border border-amber/30 transition-colors disabled:opacity-50"
              title="Запустити синхронізацію активних інваріантів з Utopia DB"
            >
              {isSyncingUtopia ? <Loader2 className="w-2.5 h-2.5 animate-spin" /> : <RefreshCw className="w-2.5 h-2.5" />}
              <span>{isSyncingUtopia ? 'Синхронізація…' : 'Синхронізувати'}</span>
            </button>
          )}
        </div>

        <div className="flex items-center gap-1.5 bg-card border border-border-subtle px-2.5 py-1 rounded-lg text-slate-300">
          <Cpu className={`w-3.5 h-3.5 ${llmOnline ? 'text-blue-400' : 'text-rose-400'}`} />
          <span>LLM Gateway</span>
          <span className="text-[10px] text-slate-500">.184:18880</span>
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              llmOnline ? 'bg-emerald-400' : 'bg-rose-400 animate-pulse'
            }`}
          />
        </div>
      </div>

      {/* Right: Tasks & ADR Action Buttons */}
      <div className="flex items-center gap-2">
        {/* Tasks & Stages Button */}
        <button
          onClick={onOpenTasksDrawer}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-card hover:bg-slate-800 text-slate-200 border border-border-subtle hover:border-amber transition-colors text-xs font-mono shadow-xs"
          title="Відкрити перелік задач та етапів розробки (specs/)"
        >
          <ListTodo className="w-3.5 h-3.5 text-amber" />
          <span>Задачі</span>
          <span className="px-1.5 py-0.2 rounded bg-amber/15 text-amber text-[10px] font-bold">
            {completedTasks}/{totalTasks}
          </span>
        </button>

        {/* ADR Library Button */}
        <button
          onClick={onOpenAdrLibrary}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-card hover:bg-slate-800 text-slate-200 border border-border-subtle hover:border-emerald-500 transition-colors text-xs font-mono shadow-xs"
          title="Відкрити бібліотеку рішень ADR з повним текстом"
        >
          <BookOpen className="w-3.5 h-3.5 text-emerald-400" />
          <span>Читати ADR</span>
        </button>

        {/* Invariant Drawer Button */}
        <button
          onClick={onOpenInvariantDrawer}
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-card hover:bg-slate-800 text-slate-200 border border-border-subtle hover:border-violet-400 transition-colors text-xs font-mono shadow-xs"
          title="Інспектор інваріантів"
        >
          <ShieldCheck className="w-3.5 h-3.5 text-violet-400" />
          <span>{invariantCount}</span>
        </button>
      </div>
    </header>
  );
};

export default Topbar;
