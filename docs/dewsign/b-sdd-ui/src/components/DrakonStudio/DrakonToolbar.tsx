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
} from 'lucide-react';

export type SaveState = 'idle' | 'saving' | 'saved' | 'error';

interface DrakonToolbarProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onGoHome: () => void;
  onExportJson: () => void;
  onSaveSpec?: () => void;
  diagramName: string;
  saveState?: SaveState;
  saveErrorMessage?: string | null;
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
          : 'Save Spec';
  return (
  return (
    <div className="h-10 bg-card/90 border-b border-border-subtle px-3 flex items-center justify-between shrink-0 select-none text-xs">
      <div className="flex items-center gap-2">
        <span className="font-semibold text-slate-200 font-mono">{diagramName}</span>
        <div className="flex items-center gap-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded text-[10px] font-mono">
          <CheckCircle2 className="w-3 h-3" />
          <span>Planar · No Crossings</span>
        </div>
      </div>

      <div className="flex items-center gap-1.5">
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

        <button
          onClick={onExportJson}
          className="flex items-center gap-1 px-2 py-1 rounded bg-panel hover:bg-slate-800 text-slate-300 border border-border-subtle hover:text-amber transition-colors text-[11px] font-mono"
          title="Download DRAKON schema as .drakon.json"
        >
          <Download className="w-3 h-3" />
          <span>Export IR</span>
        </button>

        {onSaveSpec && (
          <button
            onClick={onSaveSpec}
            disabled={saveState === 'saving'}
            className={`flex items-center gap-1 px-2 py-1 rounded border transition-colors text-[11px] font-mono ${saveClasses}`}
            title={
              saveState === 'error' && saveErrorMessage
                ? `POST /api/drakon/schema failed: ${saveErrorMessage}`
                : 'POST /api/drakon/schema — persist IR + widget diagram to specs/'
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
