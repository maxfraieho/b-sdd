// src/components/DrakonStudio/DrakonCanvas.tsx
import React, { useEffect, useRef, useState, useCallback, useImperativeHandle, forwardRef } from 'react';
import type { DrakonDiagram, DrakonWidget, DrakonConfig, DrakonEditSender, DrakonMenuItem } from '@/types/drakonwidget';
import { loadDrakonWidget, createWidget } from '@/lib/drakon/adapter';
import { getSwissDrakonTheme } from '@/lib/drakon/themeAdapter';
import { Loader2, AlertCircle } from 'lucide-react';

export interface DrakonCanvasHandle {
  zoomIn: () => void;
  zoomOut: () => void;
  goHome: () => void;
  exportJson: () => string | null;
  exportCanvas: () => HTMLCanvasElement | null;
  showInsertionSockets: (type: string) => void;
  undo: () => void;
  redo: () => void;
  deleteSelection: () => void;
  swapYesNo: (id: string) => void;
  setContent: (itemId: string, content: string) => void;
  toggleSilhouette: () => void;
}

interface DrakonCanvasProps {
  diagram: DrakonDiagram;
  diagramId: string;
  onSelectNode: (nodeId: string | null) => void;
  selectedNodeId: string | null;
  onDiagramChange?: (newDiagram: DrakonDiagram) => void;
}

const ZOOM_STEP = 2000;
const MIN_ZOOM = 3000;
const MAX_ZOOM = 30000;

export const DrakonCanvas = forwardRef<DrakonCanvasHandle, DrakonCanvasProps>(({
  diagram,
  diagramId,
  onSelectNode,
  selectedNodeId,
  onDiagramChange,
}, ref) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const widgetRef = useRef<DrakonWidget | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [zoom, setZoom] = useState(4000);

  // Context menu state
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; items: DrakonMenuItem[] } | null>(null);

  // Node text edit dialog
  const [editingItem, setEditingItem] = useState<{ id: string; content: string } | null>(null);

  // Edit sender that propagates mutations to parent React state
  const editSenderRef = useRef<DrakonEditSender>({
    pushEdit: (_edit) => {
      if (widgetRef.current && onDiagramChange) {
        try {
          const jsonStr = widgetRef.current.exportJson();
          if (jsonStr) {
            const parsed = JSON.parse(jsonStr) as DrakonDiagram;
            onDiagramChange(parsed);
          }
        } catch (e) {
          console.error('Failed to sync diagram on edit:', e);
        }
      }
    },
    stop: () => {},
  });

  const buildConfig = useCallback((): DrakonConfig => ({
    startEditContent: (item, isReadonly) => {
      if (isReadonly) return;
      onSelectNode(item.id);
      setEditingItem({ id: item.id, content: item.content || '' });
    },
    showContextMenu: (left, top, items) => {
      const containerEl = containerRef.current;
      if (containerEl) {
        const rect = containerEl.getBoundingClientRect();
        setContextMenu({ x: left - rect.left, y: top - rect.top, items });
      } else {
        setContextMenu({ x: left, y: top, items });
      }
    },
    canSelect: true,
    canvasIcons: true,
    textFormat: 'plain',
    font: '13px Inter, -apple-system, sans-serif',
    headerFont: 'bold 15px Inter, -apple-system, sans-serif',
    branchFont: 'bold 13px Inter, -apple-system, sans-serif',
    theme: getSwissDrakonTheme(true),
    onSelectionChanged: (items) => {
      if (items && items.length > 0) {
        onSelectNode(items[0].id);
      } else {
        onSelectNode(null);
      }
    },
    onZoomChanged: (newZoom) => setZoom(newZoom),
  }), [onSelectNode]);

  // Imperative handle for parent toolbar and icon palette
  useImperativeHandle(ref, () => ({
    zoomIn: () => {
      const newZoom = Math.min(zoom + ZOOM_STEP, MAX_ZOOM);
      setZoom(newZoom);
      widgetRef.current?.setZoom(newZoom);
    },
    zoomOut: () => {
      const newZoom = Math.max(zoom - ZOOM_STEP, MIN_ZOOM);
      setZoom(newZoom);
      widgetRef.current?.setZoom(newZoom);
    },
    goHome: () => {
      widgetRef.current?.goHome();
    },
    exportJson: () => {
      if (widgetRef.current?.exportJson) {
        return widgetRef.current.exportJson();
      }
      return JSON.stringify(diagram, null, 2);
    },
    exportCanvas: () => {
      if (widgetRef.current?.exportCanvas) {
        return widgetRef.current.exportCanvas(100);
      }
      return null;
    },
    showInsertionSockets: (type: string) => {
      widgetRef.current?.showInsertionSockets(type);
    },
    undo: () => {
      widgetRef.current?.undo();
    },
    redo: () => {
      widgetRef.current?.redo();
    },
    deleteSelection: () => {
      widgetRef.current?.deleteSelection();
    },
    swapYesNo: (id: string) => {
      widgetRef.current?.swapYesNo(id);
    },
    setContent: (itemId: string, content: string) => {
      widgetRef.current?.setContent(itemId, content);
      widgetRef.current?.redraw();
    },
    toggleSilhouette: () => {
      widgetRef.current?.toggleSilhouette();
    },
  }), [zoom, diagram]);

  // Initialize DrakonWidget instance
  useEffect(() => {
    let mounted = true;

    async function initCanvas() {
      if (!containerRef.current) return;
      setIsLoading(true);
      setError(null);

      try {
        await loadDrakonWidget();
        if (!mounted) return;

        const widget = createWidget();
        widgetRef.current = widget;

        const container = containerRef.current;
        const rect = container.getBoundingClientRect();
        container.innerHTML = '';

        const config = buildConfig();
        const element = widget.render(rect.width || 800, rect.height || 600, config);
        container.appendChild(element);

        // Always guarantee write access and root branch so socket insertions and edits work
        const items = { ...(diagram.items || {}) };
        const hasBranch = Object.values(items).some((it: any) => it?.type === 'branch');
        if (!hasBranch && Object.keys(items).length > 0) {
          const firstKey = Object.keys(items)[0];
          items['b0'] = {
            type: 'branch',
            branchId: 0,
            content: diagram.name || 'Головна гілка',
            one: firstKey,
          };
        }

        const diagramToLoad = {
          ...diagram,
          access: 'write' as const,
          items,
        };

        await widget.setDiagram(diagramId, diagramToLoad, editSenderRef.current);
        widget.setZoom(zoom);
        widget.goHome();

        setIsLoading(false);
      } catch (err) {
        if (!mounted) return;
        console.error('DrakonWidget init error:', err);
        setError(err instanceof Error ? err.message : 'Failed to initialize DrakonWidget');
        setIsLoading(false);
      }
    }

    initCanvas();

    return () => {
      mounted = false;
      if (widgetRef.current) {
        editSenderRef.current.stop();
        widgetRef.current = null;
      }
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [diagramId, diagram, buildConfig]);

  // Highlight or show selected node if changed externally
  useEffect(() => {
    if (widgetRef.current && selectedNodeId) {
      widgetRef.current.showItem(selectedNodeId);
    }
  }, [selectedNodeId]);

  // Handle ResizeObserver
  useEffect(() => {
    if (!containerRef.current || !widgetRef.current || isLoading) return;
    const container = containerRef.current;
    const widget = widgetRef.current;

    let resizeTimer: ReturnType<typeof setTimeout>;
    const observer = new ResizeObserver(() => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        if (!container || !widget) return;
        const rect = container.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0) {
          container.innerHTML = '';
          const config = buildConfig();
          const element = widget.render(rect.width, rect.height, config);
          container.appendChild(element);
          widget.redraw();
        }
      }, 150);
    });

    observer.observe(container);
    return () => {
      clearTimeout(resizeTimer);
      observer.disconnect();
    };
  }, [isLoading, buildConfig]);

  const handleConfirmEdit = () => {
    if (!editingItem) return;
    widgetRef.current?.setContent(editingItem.id, editingItem.content);
    widgetRef.current?.redraw();
    setEditingItem(null);
  };

  if (error) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-canvas p-6 text-rose-400">
        <AlertCircle className="w-8 h-8 mb-2" />
        <span className="text-sm font-semibold">DrakonWidget Canvas Error</span>
        <span className="text-xs text-slate-400 mt-1">{error}</span>
      </div>
    );
  }

  return (
    <div
      onClick={() => setContextMenu(null)}
      className="relative w-full h-full bg-canvas overflow-hidden flex flex-col select-none"
    >
      {isLoading && (
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-canvas/80 backdrop-blur-xs text-slate-400">
          <Loader2 className="w-8 h-8 animate-spin text-amber mb-2" />
          <span className="text-xs font-mono">Loading DrakonWidget Engine...</span>
        </div>
      )}

      <div
        ref={containerRef}
        className="drakon-canvas-container flex-1 w-full h-full"
      />

      {/* Floating Context Menu */}
      {contextMenu && (
        <div
          className="absolute z-50 min-w-[160px] rounded-lg border border-border-subtle bg-panel/95 backdrop-blur-md p-1 shadow-2xl text-xs font-mono select-none"
          style={{ left: contextMenu.x, top: contextMenu.y }}
          onClick={(e) => e.stopPropagation()}
        >
          {contextMenu.items.map((item, i) =>
            item.type === 'separator' ? (
              <div key={i} className="my-1 h-px bg-border-subtle" />
            ) : (
              <button
                key={i}
                className="w-full flex items-center justify-between rounded-md px-2.5 py-1.5 hover:bg-slate-800 hover:text-amber text-left text-slate-200 transition-colors"
                onClick={(e) => {
                  e.stopPropagation();
                  setContextMenu(null);
                  item.action?.();
                }}
              >
                <span>{item.text}</span>
                {item.hint && <span className="text-[10px] text-slate-500 ml-2">{item.hint}</span>}
              </button>
            )
          )}
        </div>
      )}

      {/* Double-Click Node Content Editor Modal */}
      {editingItem && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-100"
          onClick={() => setEditingItem(null)}
        >
          <div
            className="w-full max-w-md bg-panel border border-border-subtle rounded-xl shadow-2xl p-5 space-y-4 text-slate-100"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between">
              <h4 className="font-mono text-xs font-bold text-amber uppercase tracking-wider">
                Редагувати вміст вузла ({editingItem.id})
              </h4>
              <button
                onClick={() => setEditingItem(null)}
                className="text-slate-400 hover:text-slate-200"
              >
                ✕
              </button>
            </div>

            <textarea
              autoFocus
              value={editingItem.content}
              onChange={(e) => setEditingItem({ ...editingItem, content: e.target.value })}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                  e.preventDefault();
                  handleConfirmEdit();
                }
                if (e.key === 'Escape') {
                  setEditingItem(null);
                }
              }}
              className="w-full h-28 p-3 rounded-lg bg-canvas border border-border-subtle text-slate-200 font-mono text-xs focus:outline-hidden focus:border-amber leading-relaxed"
              placeholder="Введіть дію, умову чи підпис..."
            />

            <div className="flex items-center justify-between text-[11px] font-mono">
              <span className="text-slate-500">Ctrl+Enter для збереження</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setEditingItem(null)}
                  className="px-3 py-1.5 rounded-lg border border-border-subtle hover:bg-slate-800 text-slate-300"
                >
                  Скасувати
                </button>
                <button
                  onClick={handleConfirmEdit}
                  className="px-4 py-1.5 rounded-lg bg-amber text-slate-950 font-bold hover:bg-amber-400"
                >
                  Зберегти
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

export default DrakonCanvas;
