// src/components/DrakonStudio/NodeInspector.tsx
import React, { useState, useEffect } from 'react';
import type { DrakonNodeIR, DrakonNodeType } from '@/types/drakon';
import type { BitemporalAdr } from '@/types/adr';
import {
  FileCode,
  Shield,
  X,
  Trash2,
  Check,
  Save,
  ArrowDown,
  CornerDownRight,
  Sparkles,
} from 'lucide-react';

interface NodeInspectorProps {
  node: DrakonNodeIR | null;
  allNodes: DrakonNodeIR[];
  adrs: BitemporalAdr[];
  onClose: () => void;
  onUpdateNode: (updatedNode: DrakonNodeIR) => void;
  onDeleteNode: (nodeId: string) => void;
  onOpenInvariantDetails?: (invariantId: string) => void;
}

export const NodeInspector: React.FC<NodeInspectorProps> = ({
  node,
  allNodes,
  adrs,
  onClose,
  onUpdateNode,
  onDeleteNode,
  onOpenInvariantDetails,
}) => {
  const [label, setLabel] = useState('');
  const [nodeType, setNodeType] = useState<DrakonNodeType>('action');
  const [downEdge, setDownEdge] = useState<string>('');
  const [rightEdge, setRightEdge] = useState<string>('');
  const [invariantId, setInvariantId] = useState<string>('');
  const [severity, setSeverity] = useState<'normal' | 'severe' | 'fatal'>('normal');
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    if (node) {
      setLabel(node.label || '');
      setNodeType(node.node_type || 'action');
      setDownEdge(node.edges.down || '');
      setRightEdge(node.edges.right || '');
      setInvariantId(node.semantic_binding?.adr_invariant_id || '');
      setSeverity((node.semantic_binding?.severity as 'normal' | 'severe' | 'fatal') || 'normal');
      setIsSaved(false);
    }
  }, [node]);

  if (!node) return null;

  const handleSave = () => {
    const updated: DrakonNodeIR = {
      ...node,
      label,
      node_type: nodeType,
      edges: {
        down: downEdge || null,
        right: rightEdge || null,
      },
      semantic_binding: invariantId
        ? {
            adr_invariant_id: invariantId,
            severity,
          }
        : undefined,
    };
    onUpdateNode(updated);
    setIsSaved(true);
    window.setTimeout(() => setIsSaved(false), 1500);
  };

  const otherNodes = allNodes.filter((n) => n.node_id !== node.node_id);

  // Collect all known invariants from ADRs
  const availableInvariants = adrs.flatMap((adr) =>
    (adr.invariants || []).map((inv) => ({
      id: inv.id,
      adrId: adr.id,
      title: inv.statement,
    })),
  );

  return (
    <div className="absolute right-3 top-12 bottom-3 w-88 bg-panel/95 backdrop-blur-md border border-border-subtle rounded-xl shadow-2xl z-20 flex flex-col overflow-hidden text-xs">
      {/* Header */}
      <div className="px-4 py-3 bg-card border-b border-border-subtle flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <FileCode className="w-4 h-4 text-amber" />
          <span className="font-bold text-slate-100 font-mono">Редактор вузла DRAKON</span>
          <span className="font-mono text-[10px] text-amber px-1.5 py-0.2 rounded bg-amber/10 border border-amber/30">
            #{node.node_id}
          </span>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-200 p-1 rounded hover:bg-slate-800 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body: Form */}
      <div className="p-4 space-y-4 overflow-y-auto flex-1">
        {/* Node Type Selector */}
        <div>
          <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
            Тип вузла (Primitive Type)
          </label>
          <select
            value={nodeType}
            onChange={(e) => setNodeType(e.target.value as DrakonNodeType)}
            className="w-full bg-canvas border border-border-subtle rounded-lg px-2.5 py-1.5 text-slate-200 font-mono text-xs focus:border-amber focus:outline-none"
          >
            <option value="action">action (Дія / Алгоритмічний крок)</option>
            <option value="question">question (Умова / Питання ТАК/НІ)</option>
            <option value="headline">headline (Заголовок / Етап процесу)</option>
            <option value="address">address (Маршрут / Силует)</option>
            <option value="end">end (Кінець / Термінальний вузол)</option>
          </select>
        </div>

        {/* Node Label / Description */}
        <div>
          <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
            Текст вузла / Інструкція (Label)
          </label>
          <textarea
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            rows={3}
            placeholder="Опишіть дію або запитання алгоритму..."
            className="w-full bg-canvas border border-border-subtle rounded-lg p-2.5 text-slate-100 font-sans text-xs focus:border-amber focus:outline-none resize-none leading-relaxed"
          />
        </div>

        {/* Edge Connections */}
        <div className="p-3 bg-card rounded-lg border border-border-subtle space-y-3">
          <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold block">
            Маршрутизація переходів (Edges)
          </span>

          {/* Down Edge */}
          <div>
            <label className="text-[11px] font-mono text-emerald-400 flex items-center gap-1 mb-1">
              <ArrowDown className="w-3 h-3" />
              <span>{nodeType === 'question' ? 'Перехід ТАК (Down):' : 'Наступний крок (Down):'}</span>
            </label>
            <select
              value={downEdge}
              onChange={(e) => setDownEdge(e.target.value)}
              className="w-full bg-canvas border border-border-subtle rounded px-2 py-1 text-slate-200 font-mono text-[11px] focus:border-amber focus:outline-none"
            >
              <option value="">-- Кінець гілки (null) --</option>
              {otherNodes.map((n) => (
                <option key={n.node_id} value={n.node_id}>
                  [{n.node_type}] #{n.node_id} — {n.label.slice(0, 32)}...
                </option>
              ))}
            </select>
          </div>

          {/* Right Edge (for questions/branching) */}
          {nodeType === 'question' && (
            <div>
              <label className="text-[11px] font-mono text-rose-400 flex items-center gap-1 mb-1">
                <CornerDownRight className="w-3 h-3" />
                <span>Перехід НІ / Відхилення (Right):</span>
              </label>
              <select
                value={rightEdge}
                onChange={(e) => setRightEdge(e.target.value)}
                className="w-full bg-canvas border border-border-subtle rounded px-2 py-1 text-slate-200 font-mono text-[11px] focus:border-amber focus:outline-none"
              >
                <option value="">-- Немає розгалуження (null) --</option>
                {otherNodes.map((n) => (
                  <option key={n.node_id} value={n.node_id}>
                    [{n.node_type}] #{n.node_id} — {n.label.slice(0, 32)}...
                  </option>
                ))}
              </select>
              <p className="text-[10px] text-slate-500 font-mono mt-1">
                Правило «Right is Worse»: права гілка завжди веде до обробки помилки або відкату.
              </p>
            </div>
          )}
        </div>

        {/* Semantic Invariant Binding */}
        <div className="p-3 bg-card rounded-lg border border-border-subtle space-y-3">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-amber">
            <Shield className="w-3.5 h-3.5" />
            <span>Прив'язка до інваріанту ADR</span>
          </div>

          <div>
            <label className="text-[10px] font-mono text-slate-400 block mb-1">
              Оберіть інваріант:
            </label>
            <select
              value={invariantId}
              onChange={(e) => setInvariantId(e.target.value)}
              className="w-full bg-canvas border border-border-subtle rounded px-2 py-1.5 text-slate-200 font-mono text-[11px] focus:border-amber focus:outline-none"
            >
              <option value="">-- Без прив'язки --</option>
              <option value="ADR-001">ADR-001 (Bitemporal Horizon Isolation)</option>
              <option value="ADR-002">ADR-002 (Pre-Flight Context Budget ≤500w)</option>
              <option value="ADR-003">ADR-003 (The Rule of 2 Skill Lifecycle)</option>
              <option value="ADR-007">ADR-007 (Atomic Sprint Handoff & COW Branch)</option>
              <option value="ADR-008">ADR-008 (DRAKON Planar & Skewer Topology)</option>
              <option value="ADR-FE-001">ADR-FE-001 (Cockpit High-Density Grid)</option>
              {availableInvariants.map((inv) => (
                <option key={inv.id} value={inv.id}>
                  {inv.id}: {inv.title.slice(0, 40)}...
                </option>
              ))}
            </select>
          </div>

          {invariantId && (
            <div>
              <label className="text-[10px] font-mono text-slate-400 block mb-1">
                Критичність (Severity):
              </label>
              <div className="flex items-center gap-2">
                {(['normal', 'severe', 'fatal'] as const).map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => setSeverity(s)}
                    className={`px-2 py-1 rounded text-[10px] font-mono uppercase border transition-colors ${
                      severity === s
                        ? s === 'fatal'
                          ? 'bg-rose-500/20 text-rose-300 border-rose-500/50'
                          : s === 'severe'
                            ? 'bg-amber/20 text-amber border-amber/50'
                            : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50'
                        : 'bg-canvas text-slate-500 border-border-subtle hover:text-slate-300'
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer: Actions */}
      <div className="p-3 bg-card border-t border-border-subtle flex items-center justify-between shrink-0">
        <button
          onClick={() => onDeleteNode(node.node_id)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-rose-500/40 text-rose-400 hover:bg-rose-500/10 text-xs font-mono transition-colors"
          title="Видалити вузол"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Видалити</span>
        </button>

        <button
          onClick={handleSave}
          className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md transition-all font-mono"
        >
          {isSaved ? <Check className="w-3.5 h-3.5" /> : <Save className="w-3.5 h-3.5" />}
          <span>{isSaved ? 'Збережено' : 'Застосувати зміни'}</span>
        </button>
      </div>
    </div>
  );
};
