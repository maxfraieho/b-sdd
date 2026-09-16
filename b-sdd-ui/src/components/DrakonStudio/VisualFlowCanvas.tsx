// src/components/DrakonStudio/VisualFlowCanvas.tsx
import React from 'react';
import type { DrakonNodeIR } from '@/types/drakon';
import {
  HelpCircle,
  PlayCircle,
  StopCircle,
  Tag,
  ArrowDown,
  CornerDownRight,
  Shield,
  Plus,
  Compass,
} from 'lucide-react';

interface VisualFlowCanvasProps {
  nodes: DrakonNodeIR[];
  selectedNodeId: string | null;
  onSelectNode: (nodeId: string | null) => void;
  onAddNode: (type: 'action' | 'question' | 'end', afterNodeId?: string) => void;
}

export const VisualFlowCanvas: React.FC<VisualFlowCanvasProps> = ({
  nodes,
  selectedNodeId,
  onSelectNode,
  onAddNode,
}) => {
  // Sort or sequence nodes topologically starting with headline/start
  const orderedNodes = [...nodes].sort((a, b) => {
    if (a.node_type === 'headline') return -1;
    if (b.node_type === 'headline') return 1;
    if (a.node_type === 'end') return 1;
    if (b.node_type === 'end') return -1;
    return (a.y ?? 0) - (b.y ?? 0);
  });

  return (
    <div className="w-full h-full overflow-auto bg-canvas p-8 flex flex-col items-center select-none font-sans">
      <div className="max-w-2xl w-full flex flex-col items-center space-y-3 pb-16">
        {orderedNodes.map((node, index) => {
          const isSelected = node.node_id === selectedNodeId;
          const isQuestion = node.node_type === 'question';
          const isHeadline = node.node_type === 'headline';
          const isEnd = node.node_type === 'end';
          const isAction = node.node_type === 'action';

          const binding = node.semantic_binding;

          return (
            <React.Fragment key={node.node_id}>
              {/* The Node Card */}
              <div
                onClick={() => onSelectNode(node.node_id)}
                className={`relative w-full transition-all cursor-pointer rounded-xl border p-4 shadow-lg ${
                  isSelected
                    ? 'border-amber ring-2 ring-amber/50 bg-panel shadow-amber/10'
                    : isQuestion
                      ? 'border-amber/40 bg-card/90 hover:border-amber hover:bg-card'
                      : isHeadline
                        ? 'border-purple-500/40 bg-purple-950/20 hover:border-purple-400'
                        : isEnd
                          ? 'border-slate-700 bg-slate-900/60 hover:border-slate-500'
                          : 'border-border-subtle bg-card/80 hover:border-border-subtle/80 hover:bg-card'
                }`}
              >
                {/* Node Top Header */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {isHeadline ? (
                      <Tag className="w-4 h-4 text-purple-400" />
                    ) : isQuestion ? (
                      <HelpCircle className="w-4 h-4 text-amber" />
                    ) : isEnd ? (
                      <StopCircle className="w-4 h-4 text-rose-400" />
                    ) : (
                      <PlayCircle className="w-4 h-4 text-blue-400" />
                    )}

                    <span
                      className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border font-semibold ${
                        isHeadline
                          ? 'bg-purple-500/10 text-purple-300 border-purple-500/30'
                          : isQuestion
                            ? 'bg-amber/10 text-amber border-amber/30'
                            : isEnd
                              ? 'bg-rose-500/10 text-rose-300 border-rose-500/30'
                              : 'bg-blue-500/10 text-blue-300 border-blue-500/30'
                      }`}
                    >
                      {node.node_type}
                    </span>

                    <span className="font-mono text-[11px] text-slate-400">
                      #{node.node_id}
                    </span>
                  </div>

                  {binding?.adr_invariant_id && (
                    <span className="flex items-center gap-1 text-[10px] font-mono text-amber bg-amber/10 px-2 py-0.5 rounded border border-amber/30">
                      <Shield className="w-3 h-3" />
                      <span>{binding.adr_invariant_id}</span>
                    </span>
                  )}
                </div>

                {/* Node Label Text */}
                <p className="text-xs text-slate-100 font-medium leading-relaxed font-sans">
                  {node.label}
                </p>

                {/* Question Branches Info */}
                {isQuestion && (
                  <div className="mt-3 pt-2.5 border-t border-border-subtle flex items-center justify-between text-[11px] font-mono">
                    <span className="flex items-center gap-1 text-emerald-400">
                      <ArrowDown className="w-3 h-3" />
                      <span>ТАК (Yes) → {node.edges.down || 'Next'}</span>
                    </span>
                    <span className="flex items-center gap-1 text-rose-400">
                      <CornerDownRight className="w-3 h-3" />
                      <span>НІ (No / Error) → {node.edges.right || 'Branch'}</span>
                    </span>
                  </div>
                )}
              </div>

              {/* Connecting Down Arrow + Quick Add Node Button */}
              {index < orderedNodes.length - 1 && (
                <div className="flex flex-col items-center my-0.5 group">
                  <div className="w-0.5 h-3 bg-border-subtle group-hover:bg-amber transition-colors" />
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onAddNode('action', node.node_id);
                    }}
                    className="w-5 h-5 rounded-full bg-panel border border-border-subtle text-slate-400 hover:text-amber hover:border-amber hover:bg-slate-800 flex items-center justify-center text-[10px] transition-all shadow-sm my-0.5"
                    title="Додати новий крок після цього вузла"
                  >
                    <Plus className="w-3 h-3" />
                  </button>
                  <div className="w-0.5 h-3 bg-border-subtle group-hover:bg-amber transition-colors" />
                  <ArrowDown className="w-3.5 h-3.5 text-slate-500 -mt-1" />
                </div>
              )}
            </React.Fragment>
          );
        })}

        {/* Add Node Footer Bar */}
        <div className="pt-6 flex items-center gap-2">
          <button
            onClick={() => onAddNode('action')}
            className="px-3 py-2 rounded-lg bg-card hover:bg-slate-800 border border-border-subtle hover:border-amber text-slate-200 text-xs font-mono flex items-center gap-1.5 transition-all shadow-md"
          >
            <Plus className="w-3.5 h-3.5 text-blue-400" />
            <span>+ Дія (Action)</span>
          </button>

          <button
            onClick={() => onAddNode('question')}
            className="px-3 py-2 rounded-lg bg-card hover:bg-slate-800 border border-border-subtle hover:border-amber text-slate-200 text-xs font-mono flex items-center gap-1.5 transition-all shadow-md"
          >
            <Plus className="w-3.5 h-3.5 text-amber" />
            <span>+ Питання / Умова (Question)</span>
          </button>

          <button
            onClick={() => onAddNode('end')}
            className="px-3 py-2 rounded-lg bg-card hover:bg-slate-800 border border-border-subtle hover:border-rose-500 text-slate-200 text-xs font-mono flex items-center gap-1.5 transition-all shadow-md"
          >
            <Plus className="w-3.5 h-3.5 text-rose-400" />
            <span>+ Кінець (End)</span>
          </button>
        </div>
      </div>
    </div>
  );
};
