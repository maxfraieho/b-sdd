// src/components/MobileNavigation.tsx
// Astryx Mobile Navigation Bar for High-Density Cockpit (ADR-009)
import React from 'react';
import { Dot, IconButton } from './astryx/primitives';
import {
  Workflow,
  Bot,
  Compass,
  ShieldCheck,
  ListTodo,
  Layers,
  FolderGit2,
  BookOpen,
} from 'lucide-react';

export type MobileTabId = 'drakon' | 'copilot' | 'radar' | 'phases';

interface MobileNavigationProps {
  activeTab: MobileTabId;
  onSelectTab: (tab: MobileTabId) => void;
  currentPhaseId: string;
  isReviewGatePending?: boolean;
  onOpenTasksDrawer: () => void;
  onOpenInvariantDrawer: () => void;
  onOpenAdrLibrary: () => void;
  onOpenProjectSwitcher?: () => void;
}

export const MobileNavigation: React.FC<MobileNavigationProps> = ({
  activeTab,
  onSelectTab,
  currentPhaseId,
  isReviewGatePending = false,
  onOpenTasksDrawer,
  onOpenInvariantDrawer,
  onOpenAdrLibrary,
  onOpenProjectSwitcher,
}) => {
  return (
    <nav
      aria-label="Mobile Navigation"
      className="h-14 bg-panel border-t border-border-subtle flex items-center justify-around px-2 shrink-0 z-40 select-none"
    >
      {/* 1. DRAKON Studio */}
      <button
        onClick={() => onSelectTab('drakon')}
        className={`flex flex-col items-center justify-center flex-1 py-1 transition-colors relative cursor-pointer ${
          activeTab === 'drakon'
            ? 'text-amber font-semibold'
            : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        <Workflow className="w-5 h-5 mb-0.5" />
        <span className="text-[10px] tracking-tight">ДРАКОН</span>
        {activeTab === 'drakon' && (
          <span className="absolute top-0 w-8 h-0.5 bg-amber rounded-full" />
        )}
      </button>

      {/* 2. Copilot */}
      <button
        onClick={() => onSelectTab('copilot')}
        className={`flex flex-col items-center justify-center flex-1 py-1 transition-colors relative cursor-pointer ${
          activeTab === 'copilot'
            ? 'text-amber font-semibold'
            : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        <Bot className="w-5 h-5 mb-0.5" />
        <span className="text-[10px] tracking-tight">Копілот</span>
        {activeTab === 'copilot' && (
          <span className="absolute top-0 w-8 h-0.5 bg-amber rounded-full" />
        )}
      </button>

      {/* 3. Bitemporal Radar */}
      <button
        onClick={() => onSelectTab('radar')}
        className={`flex flex-col items-center justify-center flex-1 py-1 transition-colors relative cursor-pointer ${
          activeTab === 'radar'
            ? 'text-amber font-semibold'
            : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        <Compass className="w-5 h-5 mb-0.5" />
        <span className="text-[10px] tracking-tight">Радар</span>
        {activeTab === 'radar' && (
          <span className="absolute top-0 w-8 h-0.5 bg-amber rounded-full" />
        )}
      </button>

      {/* 4. HITL Phases & Review Gate */}
      <button
        onClick={() => onSelectTab('phases')}
        className={`flex flex-col items-center justify-center flex-1 py-1 transition-colors relative cursor-pointer ${
          activeTab === 'phases'
            ? 'text-amber font-semibold'
            : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        <div className="relative">
          <ShieldCheck className="w-5 h-5 mb-0.5" />
          {isReviewGatePending && (
            <span className="absolute -top-1 -right-1.5">
              <Dot tone="rose" pulse />
            </span>
          )}
        </div>
        <span className="text-[10px] tracking-tight font-mono">
          {currentPhaseId.toUpperCase()}
        </span>
        {activeTab === 'phases' && (
          <span className="absolute top-0 w-8 h-0.5 bg-amber rounded-full" />
        )}
      </button>

      {/* 5. Drawers / Project Action Menu */}
      <div className="flex items-center gap-1 pl-1 border-l border-[#1e293b]/60">
        {onOpenProjectSwitcher && (
          <IconButton
            title="Проєкти та GitHub"
            size="sm"
            onClick={onOpenProjectSwitcher}
          >
            <FolderGit2 className="w-4 h-4 text-cyan" />
          </IconButton>
        )}
        <IconButton
          title="Завдання"
          size="sm"
          onClick={onOpenTasksDrawer}
        >
          <ListTodo className="w-4 h-4" />
        </IconButton>
        <IconButton
          title="ADR Бібліотека"
          size="sm"
          onClick={onOpenAdrLibrary}
        >
          <BookOpen className="w-4 h-4 text-emerald-400" />
        </IconButton>
        <IconButton
          title="Інваріанти"
          size="sm"
          onClick={onOpenInvariantDrawer}
        >
          <Layers className="w-4 h-4" />
        </IconButton>
      </div>
    </nav>
  );
};

export default MobileNavigation;
