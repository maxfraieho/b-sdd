// src/components/Topbar.tsx
// High-Density Astryx TopNav (Zone 1) with Universal Project & Catalog Integration
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
  Workflow,
  Smartphone,
  Monitor,
  Github,
  Activity,
} from 'lucide-react';
import { Button, IconButton, Badge, Dot } from './astryx/primitives';

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
  appwriteOnline?: boolean;
  appwriteLatency?: number | null;
  githubOnline?: boolean;
  githubLive?: boolean;
  onSyncUtopia?: () => Promise<void>;
  isSyncingUtopia?: boolean;
  onOpenProjectSwitcher?: () => void;
  onOpenPipelineCatalog?: () => void;
  isMobileMode?: boolean;
  onToggleMobileMode?: () => void;
  onOpenTelemetryDrawer?: () => void;
  telemetryLatency?: number;
  telemetrySlaOk?: boolean;
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
  appwriteOnline = true,
  appwriteLatency = 22,
  githubOnline = true,
  githubLive = true,
  onSyncUtopia,
  isSyncingUtopia = false,
  onOpenProjectSwitcher,
  onOpenPipelineCatalog,
  isMobileMode = false,
  onToggleMobileMode,
  onOpenTelemetryDrawer,
  telemetryLatency,
  telemetrySlaOk = true,
}) => {
  const currentSpec = specs.find((s) => s.id === selectedSpecId) || specs[0] || null;
  const totalTasks = specs.reduce((sum, s) => sum + s.tasks_count, 0);
  const completedTasks = specs.reduce((sum, s) => sum + s.completed_count, 0);

  return (
    <header className="h-12 bg-[#0d121c] border-b border-[#1e293b] px-2 sm:px-3 md:px-4 flex items-center justify-between shrink-0 select-none z-30 font-mono">
      {/* Left: Brand & Universal Project Selector */}
      <div className="flex items-center gap-1.5 sm:gap-2 md:gap-3">
        {/* Brand Tile */}
        <div className="flex items-center gap-1.5">
          <div className="w-7 h-7 rounded bg-[#162035] border border-[#1e293b] flex items-center justify-center text-amber shadow-xs shrink-0">
            <Layers className="w-4 h-4" />
          </div>
          <div className="flex flex-col">
            <span className="text-xs font-bold tracking-wider uppercase text-slate-100 font-mono">
              B-SDD
            </span>
            <span className="hidden md:inline text-[9px] text-slate-400 font-mono">Astryx Cockpit</span>
          </div>
        </div>

        <div className="hidden sm:block h-4 w-px bg-[#1e293b] mx-0.5" />

        {/* Universal Workspace / GitHub Repository Trigger */}
        <button
          onClick={onOpenProjectSwitcher}
          className="flex items-center gap-1.5 bg-[#141b27] hover:bg-[#1a2233] border border-[#1e293b] hover:border-cyan/50 px-2 py-1 rounded text-xs text-slate-200 transition-colors"
          title="Натисніть для вибору або підключення репозиторію з GitHub"
        >
          <FolderGit2 className="w-3.5 h-3.5 text-cyan shrink-0" />
          <span className="font-semibold truncate max-w-[75px] sm:max-w-[110px] md:max-w-none">
            {projectInfo?.name || 'b-sdd'}
          </span>
          <span className="text-slate-600 hidden sm:inline">·</span>
          <span className="text-emerald hidden sm:flex items-center gap-1">
            <GitBranch className="w-3 h-3 shrink-0" />
            <span className="truncate max-w-[50px]">{projectInfo?.branch || 'main'}</span>
          </span>
          <ChevronDown className="w-3 h-3 text-slate-500" />
        </button>

        {/* Active Spec Selector (hidden on smallest screens) */}
        {specs.length > 0 && (
          <div className="relative group hidden sm:block">
            <button className="flex items-center gap-1.5 bg-[#141b27] hover:bg-[#1a2233] border border-[#1e293b] px-2 py-1 rounded text-xs text-slate-200 transition-colors">
              <span className="text-amber font-semibold">
                {currentSpec?.id.split('-')[0] || 'Spec 004'}
              </span>
              <span className="text-slate-400 truncate max-w-[90px] md:max-w-[130px] hidden md:inline">
                {currentSpec?.title || 'Multi-Session'}
              </span>
              <ChevronDown className="w-3 h-3 text-slate-500" />
            </button>
            <div className="hidden group-hover:block absolute left-0 top-full mt-1 w-64 bg-[#141b27] border border-[#1e293b] rounded shadow-xl py-1 z-50">
              <div className="px-3 py-1 text-[10px] uppercase text-slate-500 border-b border-[#1e293b]">
                Активні специфікації (specs/)
              </div>
              {specs.map((spec) => (
                <button
                  key={spec.id}
                  onClick={() => onSelectSpec(spec.id)}
                  className={`w-full text-left px-3 py-1.5 text-xs hover:bg-[#1a2233] transition-colors flex items-center justify-between ${
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

        {/* Standard Pipelines Catalog Trigger */}
        {onOpenPipelineCatalog && (
          <Button
            size="sm"
            variant="ghost"
            onClick={onOpenPipelineCatalog}
            icon={<Workflow className="w-3.5 h-3.5 text-amber" />}
            className="hidden lg:inline-flex text-slate-300 hover:text-amber border-[#1e293b]"
            title="Відкрити бібліотеку стандартних алгоритмів ДРАКОН та B-SDD пайплайнів"
          >
            <span>Алгоритми</span>
          </Button>
        )}
      </div>

      {/* Middle: Sovereign Infrastructure Status & Utopia Sync */}
      <div className="hidden xl:flex items-center gap-2.5 text-[11px]">
        {/* Appwrite RT Status Chip (ADR-011) */}
        <div className="flex items-center gap-1.5 bg-[#141b27] border border-[#1e293b] px-2 py-1 rounded text-slate-300">
          <Workflow className={`w-3.5 h-3.5 ${appwriteOnline ? 'text-emerald' : 'text-slate-400'}`} />
          <span>Appwrite RT</span>
          <span className="text-[10px] text-slate-500">{appwriteLatency ? `${appwriteLatency}ms` : 'Connected'}</span>
          <Dot tone={appwriteOnline ? 'emerald' : 'amber'} pulse={!appwriteOnline} />
        </div>

        {/* GitHub API Live Sync Chip (ADR-011) */}
        <div className="flex items-center gap-1.5 bg-[#141b27] border border-[#1e293b] px-2 py-1 rounded text-slate-300">
          <Github className={`w-3.5 h-3.5 ${githubOnline ? 'text-cyan' : 'text-slate-400'}`} />
          <span>GitHub</span>
          <span className="text-[10px] text-slate-500">{githubLive ? 'Live Sync' : 'Cached'}</span>
          <Dot tone={githubOnline ? 'emerald' : 'cyan'} />
        </div>

        <div className="flex items-center gap-2 bg-[#141b27] border border-[#1e293b] px-2.5 py-1 rounded">
          <div className="flex items-center gap-1.5 text-slate-300">
            <Database className={`w-3.5 h-3.5 ${utopiaOnline ? 'text-emerald' : 'text-rose'}`} />
            <span>Utopia DB</span>
            <span className="text-[10px] text-slate-500">.251:9922</span>
            <Dot tone={utopiaOnline ? 'emerald' : 'rose'} pulse={!utopiaOnline} />
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

        <div className="flex items-center gap-1.5 bg-[#141b27] border border-[#1e293b] px-2.5 py-1 rounded text-slate-300">
          <Cpu className={`w-3.5 h-3.5 ${llmOnline ? 'text-blue-400' : 'text-rose'}`} />
          <span>LLM Gateway</span>
          <span className="text-[10px] text-slate-500">.184:18880</span>
          <Dot tone={llmOnline ? 'emerald' : 'rose'} pulse={!llmOnline} />
        </div>
      </div>

      {/* Right: Actions, Responsive Mode Switcher, Drawers */}
      <div className="flex items-center gap-1 sm:gap-1.5 md:gap-2">
        {/* Device Viewport Preview Toggle (Desktop <-> Mobile) */}
        {onToggleMobileMode && (
          <button
            onClick={onToggleMobileMode}
            className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors border ${
              isMobileMode
                ? 'bg-amber/20 text-amber border-amber/50 font-bold'
                : 'bg-[#141b27] hover:bg-[#1a2233] text-slate-300 border-[#1e293b]'
            }`}
            title={isMobileMode ? 'Увімкнено мобільний кокпіт. Натисніть для десктопного перегляду' : 'Увімкнено десктопний кокпіт. Натисніть для мобільного перегляду'}
          >
            {isMobileMode ? <Smartphone className="w-3.5 h-3.5 text-amber" /> : <Monitor className="w-3.5 h-3.5 text-slate-400" />}
            <span className="text-[10px] hidden sm:inline">{isMobileMode ? 'Мобільний' : 'Десктоп'}</span>
          </button>
        )}

        {/* Pipeline Catalog (compact icon for medium screens) */}
        {onOpenPipelineCatalog && (
          <button
            onClick={onOpenPipelineCatalog}
            className="lg:hidden p-1.5 rounded bg-[#141b27] text-amber border border-[#1e293b] hover:bg-[#1a2233]"
            title="Каталог алгоритмів ДРАКОН"
          >
            <Workflow className="w-3.5 h-3.5" />
          </button>
        )}

        {/* Telemetry & SLA Drawer Button (ADR-012) */}
        {onOpenTelemetryDrawer && (
          <button
            onClick={onOpenTelemetryDrawer}
            className={`flex items-center gap-1 px-2 py-1 rounded text-xs border transition-colors shadow-xs ${
              telemetrySlaOk
                ? 'bg-[#141b27] hover:bg-[#1a2233] text-slate-200 border-[#1e293b] hover:border-cyan/50'
                : 'bg-rose-950/40 text-rose-300 border-rose-800 hover:border-rose-600'
            }`}
            title="Відкрити дашборд продакшн-телеметрії та SLA компілятора (ADR-012)"
          >
            <Activity className={`w-3.5 h-3.5 ${telemetrySlaOk ? 'text-cyan' : 'text-rose-400 animate-pulse'}`} />
            <span className="hidden sm:inline text-[10px] font-bold">
              {telemetryLatency != null ? `${telemetryLatency}ms` : 'SLA'}
            </span>
          </button>
        )}

        {/* Tasks & Stages Button */}
        <button
          onClick={onOpenTasksDrawer}
          className="flex items-center gap-1 px-2 py-1 rounded bg-[#141b27] hover:bg-[#1a2233] text-slate-200 border border-[#1e293b] hover:border-amber/50 transition-colors text-xs shadow-xs"
          title="Відкрити перелік задач специфікації (specs/)"
        >
          <ListTodo className="w-3.5 h-3.5 text-amber" />
          <span className="hidden md:inline">Задачі</span>
          <span className="px-1.5 py-0.2 rounded bg-amber/15 text-amber text-[10px] font-bold">
            {completedTasks}/{totalTasks}
          </span>
        </button>

        {/* ADR Library Button */}
        <button
          onClick={onOpenAdrLibrary}
          className="flex items-center gap-1 px-2 py-1 rounded bg-[#141b27] hover:bg-[#1a2233] text-slate-200 border border-[#1e293b] hover:border-emerald/50 transition-colors text-xs shadow-xs"
          title="Відкрити бібліотеку рішень ADR"
        >
          <BookOpen className="w-3.5 h-3.5 text-emerald" />
          <span className="hidden md:inline">ADR</span>
        </button>

        {/* Invariant Drawer Button */}
        <button
          onClick={onOpenInvariantDrawer}
          className="flex items-center gap-1 px-2 py-1 rounded bg-[#141b27] hover:bg-[#1a2233] text-slate-200 border border-[#1e293b] hover:border-violet/50 transition-colors text-xs shadow-xs"
          title="Інспектор активних інваріантів"
        >
          <ShieldCheck className="w-3.5 h-3.5 text-violet" />
          <span className="text-[11px] font-bold">{invariantCount}</span>
        </button>
      </div>
    </header>
  );
};

export default Topbar;
