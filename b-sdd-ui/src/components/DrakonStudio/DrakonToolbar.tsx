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
  Maximize2,
  Minimize2,
} from 'lucide-react';
import { Button, IconButton, Badge, Segmented } from '@/components/astryx/primitives';
import { LogicStructureSwitcher, DrakonSchemaMode } from './LogicStructureSwitcher';

export type SaveState = 'idle' | 'saving' | 'saved' | 'error';
export type DrakonViewMode = 'widget' | 'flow' | 'json';
export type { DrakonSchemaMode };

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
  projectName?: string;
  specName?: string;
  functionName?: string;
  saveState?: SaveState;
  saveErrorMessage?: string | null;
  viewMode: DrakonViewMode;
  onViewModeChange: (mode: DrakonViewMode) => void;
  onAddNode?: (type: 'action' | 'question' | 'end') => void;
  schemaMode?: DrakonSchemaMode;
  onSchemaModeChange?: (mode: DrakonSchemaMode) => void;
  isFullscreen?: boolean;
  onToggleFullscreen?: () => void;
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
  projectName = 'b-sdd',
  specName,
  functionName,
  saveState = 'idle',
  saveErrorMessage,
  viewMode,
  onViewModeChange,
  onAddNode,
  schemaMode = 'logic',
  onSchemaModeChange,
  isFullscreen,
  onToggleFullscreen,
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
      ? 'Saving...'
      : saveState === 'saved'
        ? 'Saved'
        : saveState === 'error'
          ? 'Retry Save'
          : 'Зберегти схему';

  return (
    <div className="h-10 bg-[#141b27]/90 border-b border-[#1e293b] px-2 md:px-3 flex items-center justify-between shrink-0 select-none text-xs overflow-x-auto gap-2">
      {/* Left: Breadcrumbs & Mode Switcher */}
      <div className="flex items-center gap-2 md:gap-3 shrink-0">
        {/* Breadcrumbs Trail */}
        <div className="hidden sm:flex items-center gap-1 font-mono text-[11px] text-slate-400 bg-canvas-subtle/50 px-2 py-0.5 rounded border border-[#1e293b]">
          <span className="text-slate-300 font-medium hover:text-white transition-colors cursor-default">
            {projectName}
          </span>
          <span className="text-slate-600">/</span>
          <span className="text-slate-200 font-medium truncate max-w-[130px]" title={specName || diagramName}>
            {specName || diagramName}
          </span>
          <span className="text-slate-600">/</span>
          <span className="text-amber/90 font-medium">
            {schemaMode === 'logic' ? 'Логіка' : 'Структура'}
          </span>
          {functionName && (
            <>
              <span className="text-slate-600">/</span>
              <span className="text-indigo-300 truncate max-w-[100px]">{functionName}</span>
            </>
          )}
        </div>

        {/* Small screen fallback */}
        <span className="sm:hidden font-semibold text-slate-200 font-mono text-[11px] truncate max-w-[100px]">
          {specName || diagramName}
        </span>

        {onSchemaModeChange && (
          <LogicStructureSwitcher
            value={schemaMode}
            onChange={onSchemaModeChange}
          />
        )}

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

        {onToggleFullscreen && (
          <IconButton
            title={isFullscreen ? 'Вийти з повноекранного режиму (Esc)' : 'Повноекранний режим студії'}
            size="sm"
            onClick={onToggleFullscreen}
            className={isFullscreen ? 'text-amber bg-amber/10 border border-amber/30' : ''}
          >
            {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </IconButton>
        )}
      </div>
    </div>
  );
};

export default DrakonToolbar;
