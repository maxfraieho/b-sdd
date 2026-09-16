// src/components/DrakonStudio/DrakonToolbar.tsx
import React from 'react';
import {
  ZoomIn,
  ZoomOut,
  Home,
  Download,
  CheckCircle2,
  Save,
  Loader2,
  AlertTriangle,
  Layers,
  Code2,
  Workflow,
  Plus,
} from 'lucide-react';

export type SaveState = 'idle' | 'saving' | 'saved' | 'error';
export type DrakonViewMode = 'flow' | 'widget' | 'json';

interface DrakonToolbarProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onGoHome: () => void;
  onExportJson: () => void;
  onSaveSpec?: () => void;
  diagramName: string;
  saveState?: SaveState;
  saveErrorMessage?: string | null;
  viewMode: DrakonViewMode;
  onViewModeChange: (mode: DrakonViewMode) => void;
  onAddNode?: (type: 'action' | 'question' | 'end') => void;
}

export const DrakonToolbar: React.FC<DrakonToolbarProps> = ({
  onZoomIn,
  onZoomOut,
  onGoHome,
  onExportJson,
  onSaveSpec,
  diagramName,
  saveState = 'idle',
  saveErrorMessage,
  viewMode,
  onViewModeChange,
  onAddNode,
}) => {
  const saveIcon =
    saveState === 'saving' ? (
      <Loader2 className="w-3 h-3 animate-spin" />
    ) : saveState === 'saved' ? (
      <CheckCircle2 className="w-3 h-3" />
    ) : saveState === 'error' ? (
      <AlertTriangle className="w-3 h-3" />
    ) : (
      <Save className="w-3 h-3" />
    );

  const saveClasses =
    saveState === 'saved'
      ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40'
      : saveState === 'error'
        ? 'bg-rose-500/15 text-rose-300 border-rose-500/40'
        : saveState === 'saving'
          ? 'bg-amber/15 text-amber border-amber/40 cursor-wait'
          : 'bg-panel text-slate-300 border-border-subtle hover:text-amber';

  const saveLabel =
    saveState === 'saving'
      ? 'Saving…'
      : saveState === 'saved'
        ? 'Saved'
        : saveState === 'error'
          ? 'Retry Save'
          : 'Зберегти схему';

  return (
    <div className="h-10 bg-card/90 border-b border-border-subtle px-3 flex items-center justify-between shrink-0 select-none text-xs">
      {/* Left: Title & Mode Switcher */}
      <div className="flex items-center gap-3">
        <span className="font-semibold text-slate-200 font-mono text-[11px] truncate max-w-[180px]">
          {diagramName}
        </span>

        {/* View Mode Toggle */}
        <div className="flex items-center bg-panel border border-border-subtle rounded-lg p-0.5 text-[11px] font-mono">
          <button
            onClick={() => onViewModeChange('flow')}
            className={`px-2 py-0.5 rounded flex items-center gap-1 transition-all ${
              viewMode === 'flow'
                ? 'bg-amber/15 text-amber font-bold shadow-xs'
                : 'text-slate-400 hover:text-slate-200'
            }`}
            title="Інтерактивний візуальний редактор вузлів"
          >
            <Workflow className="w-3 h-3" />
            <span>Редактор</span>
          </button>

          <button
            onClick={() => onViewModeChange('widget')}
            className={`px-2 py-0.5 rounded flex items-center gap-1 transition-all ${
              viewMode === 'widget'
                ? 'bg-amber/15 text-amber font-bold shadow-xs'
                : 'text-slate-400 hover:text-slate-200'
            }`}
            title="Канонічний рендер drakonwidget.js"
          >
            <Layers className="w-3 h-3" />
            <span>Віджет</span>
          </button>

          <button
            onClick={() => onViewModeChange('json')}
            className={`px-2 py-0.5 rounded flex items-center gap-1 transition-all ${
              viewMode === 'json'
                ? 'bg-amber/15 text-amber font-bold shadow-xs'
                : 'text-slate-400 hover:text-slate-200'
            }`}
            title="Канонічний JSON-IR код схеми"
          >
            <Code2 className="w-3 h-3" />
            <span>JSON IR</span>
          </button>
        </div>

        <div className="flex items-center gap-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded text-[10px] font-mono">
          <CheckCircle2 className="w-3 h-3" />
          <span>Planar · 0 Crossings</span>
        </div>
      </div>

      {/* Right: Quick actions & Zoom */}
      <div className="flex items-center gap-1.5">
        {onAddNode && (
          <div className="flex items-center gap-1 mr-2">
            <button
              onClick={() => onAddNode('action')}
              className="px-2 py-0.5 rounded bg-panel hover:bg-slate-800 text-blue-300 border border-border-subtle hover:border-blue-400 text-[10px] font-mono flex items-center gap-1 transition-colors"
              title="Додати вузол дії"
            >
              <Plus className="w-3 h-3" />
              <span>Дія</span>
            </button>
            <button
              onClick={() => onAddNode('question')}
              className="px-2 py-0.5 rounded bg-panel hover:bg-slate-800 text-amber border border-border-subtle hover:border-amber text-[10px] font-mono flex items-center gap-1 transition-colors"
              title="Додати умову з розгалуженням"
            >
              <Plus className="w-3 h-3" />
              <span>Умова</span>
            </button>
          </div>
        )}

        {viewMode === 'widget' && (
          <>
            <button
              onClick={onZoomOut}
              className="p-1 rounded bg-panel hover:bg-slate-800 text-slate-300 border border-border-subtle hover:text-slate-100 transition-colors"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={onZoomIn}
              className="p-1 rounded bg-panel hover:bg-slate-800 text-slate-300 border border-border-subtle hover:text-slate-100 transition-colors"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={onGoHome}
              className="p-1 rounded bg-panel hover:bg-slate-800 text-slate-300 border border-border-subtle hover:text-slate-100 transition-colors"
              title="Reset to Center (Home)"
            >
              <Home className="w-3.5 h-3.5" />
            </button>
            <div className="h-3 w-px bg-border-subtle mx-1" />
          </>
        )}

        <button
          onClick={onExportJson}
          className="flex items-center gap-1 px-2 py-1 rounded bg-panel hover:bg-slate-800 text-slate-300 border border-border-subtle hover:text-amber transition-colors text-[11px] font-mono"
          title="Завантажити схему як .drakon.json"
        >
          <Download className="w-3 h-3" />
          <span>Експорт</span>
        </button>

        {onSaveSpec && (
          <button
            onClick={onSaveSpec}
            disabled={saveState === 'saving'}
            className={`flex items-center gap-1 px-2.5 py-1 rounded border transition-colors text-[11px] font-mono font-semibold ${saveClasses}`}
            title={
              saveState === 'error' && saveErrorMessage
                ? `Помилка збереження: ${saveErrorMessage}`
                : 'POST /api/drakon/schema — зберегти схему у specs/'
            }
          >
            {saveIcon}
            <span>{saveLabel}</span>
          </button>
        )}
      </div>
    </div>
  );
};
