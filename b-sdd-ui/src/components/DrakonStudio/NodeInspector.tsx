// src/components/DrakonStudio/NodeInspector.tsx
import React from 'react';
import type { DrakonNodeIR } from '@/types/drakon';
import {
  FileCode,
  Link2,
  Shield,
  X,
  CornerDownRight,
  ArrowDown,
  Database,
} from 'lucide-react';

interface NodeInspectorProps {
  node: DrakonNodeIR | null;
  onClose: () => void;
  onOpenInvariantDetails?: (invariantId: string) => void;
}

export const NodeInspector: React.FC<NodeInspectorProps> = ({
  node,
  onClose,
  onOpenInvariantDetails,
}) => {
  if (!node) return null;

  const binding = node.semantic_binding;

  let severityColor = 'text-slate-400 bg-slate-800 border-border-subtle';
  if (binding?.severity === 'fatal') severityColor = 'text-rose-400 bg-rose-950/30 border-rose-500/40';
  else if (binding?.severity === 'degraded' || binding?.severity === 'severe') severityColor = 'text-amber bg-amber/10 border-amber/30';
  else if (binding?.severity === 'normal') severityColor = 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';

  return (
    <div className="absolute right-3 top-12 bottom-3 w-80 bg-panel/95 backdrop-blur-md border border-border-subtle rounded-lg shadow-2xl z-20 flex flex-col overflow-hidden text-xs">
      {/* Header */}
      <div className="px-3 py-2.5 bg-card border-b border-border-subtle flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileCode className="w-4 h-4 text-amber" />
          <span className="font-bold text-slate-100 font-mono">Node Inspector</span>
          <span className="font-mono text-[10px] text-slate-400">#{node.node_id}</span>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-200 p-0.5 rounded"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body */}
      <div className="p-3 space-y-4 overflow-y-auto flex-1">
        {/* Node Type & Label */}
        <div>
          <span className="text-[10px] font-mono uppercase text-slate-500">Primitive Type</span>
          <div className="mt-1 flex items-center gap-2">
            <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-mono text-[11px] uppercase">
              {node.node_type}
            </span>
            {binding?.severity && (
              <span className={`px-2 py-0.5 rounded border font-mono text-[10px] uppercase ${severityColor}`}>
                {binding.severity}
              </span>
            )}
          </div>
        </div>

        <div>
          <span className="text-[10px] font-mono uppercase text-slate-500">Label / Specification</span>
          <p className="mt-1 p-2 bg-canvas border border-border-subtle rounded text-slate-200 leading-relaxed font-sans">
            {node.label}
          </p>
        </div>

        {/* Semantic Invariant Binding */}
        {binding && (
          <div className="p-2.5 bg-card border border-border-subtle rounded space-y-2">
            <div className="flex items-center gap-1.5 text-slate-300 font-semibold">
              <Shield className="w-3.5 h-3.5 text-amber" />
              <span>Architectural Invariant Binding</span>
            </div>

            {binding.adr_invariant_id && (
              <div className="flex items-center justify-between">
                <span className="text-slate-400 text-[11px]">ADR Invariant:</span>
                <button
                  onClick={() => onOpenInvariantDetails?.(binding.adr_invariant_id!)}
                  className="flex items-center gap-1 text-amber hover:underline font-mono text-[11px]"
                >
                  <span>{binding.adr_invariant_id}</span>
                  <Link2 className="w-3 h-3" />
                </button>
              </div>
            )}

            {binding.utopia_entity_id && (
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-slate-400">Utopia Entity:</span>
                <span className="font-mono text-slate-300 flex items-center gap-1">
                  <Database className="w-3 h-3 text-emerald-400" />
                  {binding.utopia_entity_id}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Transitions / Edges */}
        <div>
          <span className="text-[10px] font-mono uppercase text-slate-500">Outward Graph Edges</span>
          <div className="mt-1.5 space-y-1.5 font-mono text-[11px]">
            <div className="flex items-center justify-between p-1.5 bg-canvas rounded border border-border-subtle">
              <span className="flex items-center gap-1.5 text-emerald-400">
                <ArrowDown className="w-3 h-3" />
                <span>down (skewer):</span>
              </span>
              <span className="text-slate-300">{node.edges.down || 'None (Terminal)'}</span>
            </div>

            {node.edges.right && (
              <div className="flex items-center justify-between p-1.5 bg-canvas rounded border border-amber/30">
                <span className="flex items-center gap-1.5 text-amber">
                  <CornerDownRight className="w-3 h-3" />
                  <span>right (degrade):</span>
                </span>
                <span className="text-slate-300">{node.edges.right}</span>
              </div>
            )}
          </div>
        </div>

        {/* Action Body Preview (Leaf synthesis) */}
        {node.node_type === 'action' && (
          <div>
            <span className="text-[10px] font-mono uppercase text-slate-500">Leaf Action Body Scope</span>
            <div className="mt-1 p-2 bg-canvas border border-border-subtle rounded font-mono text-[10px] text-slate-300 overflow-x-auto">
              <pre className="text-emerald-400"># Autonomous Leaf Scope</pre>
              <pre className="text-slate-400">def handle_{node.node_id}(ctx):</pre>
              <pre className="text-slate-200">    # Enforces {binding?.adr_invariant_id || 'ADR invariant'}</pre>
              <pre className="text-slate-200">    return ctx.execute_step()</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
