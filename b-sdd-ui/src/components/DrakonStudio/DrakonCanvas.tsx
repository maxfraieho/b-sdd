// src/components/DrakonStudio/DrakonCanvas.tsx
import React, { useEffect, useRef, useState, useCallback, useImperativeHandle, forwardRef } from 'react';
import type { DrakonDiagram, DrakonWidget, DrakonConfig, DrakonEditSender } from '@/types/drakonwidget';
import { loadDrakonWidget, createWidget } from '@/lib/drakon/adapter';
import { getSwissDrakonTheme } from '@/lib/drakon/themeAdapter';
import { Loader2, AlertCircle } from 'lucide-react';

export interface DrakonCanvasHandle {
  zoomIn: () => void;
  zoomOut: () => void;
  goHome: () => void;
  exportJson: () => string | null;
  exportCanvas: () => HTMLCanvasElement | null;
}

interface DrakonCanvasProps {
  diagram: DrakonDiagram;
  diagramId: string;
  onSelectNode: (nodeId: string | null) => void;
  selectedNodeId: string | null;
}

const ZOOM_STEP = 2000;
const MIN_ZOOM = 3000;
const MAX_ZOOM = 30000;

export const DrakonCanvas = forwardRef<DrakonCanvasHandle, DrakonCanvasProps>(({
  diagram,
  diagramId,
  onSelectNode,
  selectedNodeId,
}, ref) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const widgetRef = useRef<DrakonWidget | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [zoom, setZoom] = useState(4000);

  // Read-only edit sender for workbench inspection
  const editSenderRef = useRef<DrakonEditSender>({
    pushEdit: () => {},
    stop: () => {},
  });

  const buildConfig = useCallback((): DrakonConfig => ({
    startEditContent: (item) => {
      onSelectNode(item.id);
    },
    showContextMenu: () => {},
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

  // Imperative handle for parent toolbar
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

        await widget.setDiagram(diagramId, diagram, editSenderRef.current);
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
    <div className="relative w-full h-full bg-canvas overflow-hidden flex flex-col">
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
    </div>
  );
});
