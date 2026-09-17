// src/components/DrakonStudio/DrakonToolbar.tsx
// Astryx-native Drakon Studio Toolbar (ADR-008, ADR-009)
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
  FileCode2,
  Undo2,
  Redo2,
} from 'lucide-react';
import { Button, IconButton, Badge, Segmented } from '@/components/astryx/primitives';

export type SaveState = 'idle' | 'saving' | 'saved' | 'error';
export type DrakonViewMode = 'widget' | 'flow' | 'json';

interface DrakonToolbarProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onGoHome: () => void;
  onExportJson: () => void;
  onSaveSpec?: () => void;
  onOpenPseudocode?: () => void;
  onUndo?: () => void;
  onRedo?: () => void;
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
  onOpenPseudocode,
  onUndo,
  onRedo,
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

  const saveVariant: 'secondary' | 'success' | 'destructive' =
    saveState === 'saved'
      ? 'success'
      : saveState === 'error'
        ? 'destructive'
        : 'secondary';

  const saveLabel =
    saveState === 'saving'
      ? 'Saving…'
      : saveState === 'saved'
        ? 'Saved'
        : saveState === 'error'
          ? 'Retry Save'
          : 'Зберегти схему';

  return (
    <div className="h-10 bg-[#141b27]/90 border-b border-[#1e293b] px-2 md:px-3 flex items-center justify-between shrink-0 select-none text-xs overflow-x-auto gap-2">
      {/* Left: Title & Mode Switcher */}
      <div className="flex items-center gap-2 md:gap-3 shrink-0">
        <span className="font-semibold text-slate-200 font-mono text-[11px] truncate max-w-[120px] md:max-w-[180px]">
          {diagramName}
        </span>

        {/* View Mode Toggle */}
        <Segmented
          value={viewMode}
          onChange={(val) => onViewModeChange(val as DrakonViewMode)}
          options={[
            {
              value: 'widget',
              label: (
                <span className="flex items-center gap-1">
                  <Layers className="w-3 h-3" />
                  <span className="hidden sm:inline">ДРАКОН Рушій</span>
                  <span className="sm:hidden">Рушій</span>
                </span>
              ),
            },
            {
              value: 'flow',
              label: (
                <span className="flex items-center gap-1">
                  <Workflow className="w-3 h-3" />
                  <span>Шампур</span>
                </span>
              ),
            },
            {
              value: 'json',
              label: (
                <span className="flex items-center gap-1">
                  <Code2 className="w-3 h-3" />
                  <span>JSON</span>
                </span>
              ),
            },
          ]}
        />

        <div className="hidden sm:flex items-center">
          <Badge tone="emerald" outline>
            <CheckCircle2 className="w-3 h-3" />
            <span>Planar · 0 Crossings</span>
          </Badge>
        </div>
      </div>

      {/* Right: Quick actions & Zoom */}
      <div className="flex items-center gap-1.5">
        {onUndo && (
          <IconButton
            title="Відмінити (Undo)"
            size="sm"
            onClick={onUndo}
          >
            <Undo2 className="w-3.5 h-3.5" />
          </IconButton>
        )}

        {onRedo && (
          <IconButton
            title="Повторити (Redo)"
            size="sm"
            onClick={onRedo}
          >
            <Redo2 className="w-3.5 h-3.5" />
          </IconButton>
        )}

        {onAddNode && viewMode === 'flow' && (
          <div className="flex items-center gap-1 mr-2">
            <Button
              variant="secondary"
              size="sm"
              icon={<Plus className="w-3 h-3" />}
              onClick={() => onAddNode('action')}
            >
              Дія
            </Button>
            <Button
              variant="secondary"
              size="sm"
              icon={<Plus className="w-3 h-3" />}
              onClick={() => onAddNode('question')}
            >
              Умова
            </Button>
          </div>
        )}

        {viewMode === 'widget' && (
          <>
            <IconButton
              title="Zoom Out"
              size="sm"
              onClick={onZoomOut}
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </IconButton>
            <IconButton
              title="Zoom In"
              size="sm"
              onClick={onZoomIn}
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </IconButton>
            <IconButton
              title="Reset to Center (Home)"
              size="sm"
              onClick={onGoHome}
            >
              <Home className="w-3.5 h-3.5" />
            </IconButton>
            <div className="h-3 w-px bg-[#1e293b] mx-1" />
          </>
        )}

        {onOpenPseudocode && (
          <Button
            variant="secondary"
            size="sm"
            icon={<FileCode2 className="w-3.5 h-3.5 text-amber" />}
            onClick={onOpenPseudocode}
            title="Експорт схеми в алгоритмічний псевдокод або структурні правила"
          >
            <span className="hidden sm:inline">Псевдокод & Правила</span>
            <span className="sm:hidden">Код</span>
          </Button>
        )}

        <Button
          variant="secondary"
          size="sm"
          icon={<Download className="w-3 h-3" />}
          onClick={onExportJson}
          title="Завантажити схему як .drakon.json"
        >
          JSON
        </Button>

        {onSaveSpec && (
          <Button
            variant={saveVariant}
            size="sm"
            icon={saveIcon}
            onClick={onSaveSpec}
            disabled={saveState === 'saving'}
            title={
              saveState === 'error' && saveErrorMessage
                ? `Помилка збереження: ${saveErrorMessage}`
                : 'POST /api/drakon/schema — зберегти схему у specs/'
            }
          >
            <span className="hidden sm:inline">{saveLabel}</span>
            <span className="sm:hidden">{saveState === 'saved' ? 'OK' : 'Зберегти'}</span>
          </Button>
        )}
      </div>
    </div>
  );
};

export default DrakonToolbar;
