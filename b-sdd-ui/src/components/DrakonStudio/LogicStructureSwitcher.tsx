// src/components/DrakonStudio/LogicStructureSwitcher.tsx
// -----------------------------------------------------------------------------
// ZONE B TOOLBAR — Сегментований перемикач [Логіка (Flow) | Структура (Structure)]
// Astryx-native: активна «Логіка» — amber; активна «Структура» — cyan.
// -----------------------------------------------------------------------------
import React from 'react';
import { Workflow, LayoutGrid } from 'lucide-react';

export type DrakonSchemaMode = 'logic' | 'structure';

interface LogicStructureSwitcherProps {
  value: DrakonSchemaMode;
  onChange: (mode: DrakonSchemaMode) => void;
  className?: string;
}

export const LogicStructureSwitcher: React.FC<LogicStructureSwitcherProps> = ({
  value,
  onChange,
  className,
}) => {
  const isLogic = value === 'logic';
  const isStructure = value === 'structure';

  return (
    <div
      role="tablist"
      aria-label="Схема: Логіка або Структура"
      className={`inline-flex items-center bg-[#090d13] border border-[#1e293b] rounded p-0.5 text-xs font-mono select-none ${
        className ?? ''
      }`}
    >
      <button
        role="tab"
        aria-selected={isLogic}
        onClick={() => onChange('logic')}
        className={`inline-flex items-center gap-1.5 px-3 h-7 rounded transition-all ${
          isLogic
            ? 'bg-[#141b27] text-[#f59e0b] font-bold'
            : 'text-slate-400 hover:text-slate-200'
        }`}
        style={isLogic ? { boxShadow: 'inset 0 -2px 0 #f59e0b' } : undefined}
      >
        <Workflow className="w-3.5 h-3.5" />
        Логіка
        <span className="text-[10px] opacity-70 font-normal">(Flow)</span>
      </button>
      <button
        role="tab"
        aria-selected={isStructure}
        onClick={() => onChange('structure')}
        className={`inline-flex items-center gap-1.5 px-3 h-7 rounded transition-all ${
          isStructure
            ? 'bg-[#141b27] text-[#06b6d4] font-bold'
            : 'text-slate-400 hover:text-slate-200'
        }`}
        style={isStructure ? { boxShadow: 'inset 0 -2px 0 #06b6d4' } : undefined}
      >
        <LayoutGrid className="w-3.5 h-3.5" />
        Структура
        <span className="text-[10px] opacity-70 font-normal">(Structure)</span>
      </button>
    </div>
  );
};

export default LogicStructureSwitcher;
