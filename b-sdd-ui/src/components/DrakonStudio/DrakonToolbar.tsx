// src/components/DrakonStudio/DrakonToolbar.tsx
import React from 'react';
import {
  ZoomIn,
  ZoomOut,
  Home,
  Download,
  Share2,
  CheckCircle2,
} from 'lucide-react';

interface DrakonToolbarProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onGoHome: () => void;
  onExportJson: () => void;
  diagramName: string;
}

export const DrakonToolbar: React.FC<DrakonToolbarProps> = ({
  onZoomIn,
  onZoomOut,
  onGoHome,
  onExportJson,
  diagramName,
}) => {
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
          title="Export DRAKON Schema JSON"
        >
          <Download className="w-3 h-3" />
          <span>Export IR</span>
        </button>
      </div>
    </div>
  );
};
