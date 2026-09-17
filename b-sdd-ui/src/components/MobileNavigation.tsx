// src/components/MobileNavigation.tsx
import React from 'react';
import {
  Workflow,
  Bot,
  Compass,
  ShieldCheck,
  ListTodo,
  Layers,
  Menu,
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
}

export const MobileNavigation: React.FC<MobileNavigationProps> = ({
  activeTab,
  onSelectTab,
  currentPhaseId,
  isReviewGatePending = false,
  onOpenTasksDrawer,
  onOpenInvariantDrawer,
  onOpenAdrLibrary,
}) => {
  return (
    <nav
      aria-label="Mobile Navigation"
      className="md:hidden h-14 bg-[#0d121c] border-t border-[#1e293b] flex items-center justify-around px-2 shrink-0 z-40 select-none pb-safe"
    >
      {/* 1. DRAKON Studio */}
      <button
        onClick={() => onSelectTab('drakon')}
        className={`flex flex-col items-center justify-center flex-1 py-1 transition-colors relative ${
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
        className={`flex flex-col items-center justify-center flex-1 py-1 transition-colors relative ${
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
        className={`flex flex-col items-center justify-center flex-1 py-1 transition-colors relative ${
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
        className={`flex flex-col items-center justify-center flex-1 py-1 transition-colors relative ${
          activeTab === 'phases'
            ? 'text-amber font-semibold'
            : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        <div className="relative">
          <ShieldCheck className="w-5 h-5 mb-0.5" />
          {isReviewGatePending && (
            <span className="absolute -top-1 -right-1.5 w-2.5 h-2.5 bg-rose-500 rounded-full animate-ping" />
          )}
          {isReviewGatePending && (
            <span className="absolute -top-1 -right-1.5 w-2.5 h-2.5 bg-rose-500 rounded-full" />
          )}
        </div>
        <span className="text-[10px] tracking-tight font-mono">
          {currentPhaseId.toUpperCase()}
        </span>
        {activeTab === 'phases' && (
          <span className="absolute top-0 w-8 h-0.5 bg-amber rounded-full" />
        )}
      </button>

      {/* 5. More Drawers Action Menu */}
      <div className="flex items-center gap-1 pl-1 border-l border-[#1e293b]/60">
        <button
          onClick={onOpenTasksDrawer}
          title="Завдання"
          aria-label="Завдання"
          className="p-1.5 text-slate-400 hover:text-slate-100 rounded active:bg-slate-800"
        >
          <ListTodo className="w-4 h-4" />
        </button>
        <button
          onClick={onOpenInvariantDrawer}
          title="Інваріанти"
          aria-label="Інваріанти"
          className="p-1.5 text-slate-400 hover:text-slate-100 rounded active:bg-slate-800"
        >
          <Layers className="w-4 h-4" />
        </button>
      </div>
    </nav>
  );
};

export default MobileNavigation;
