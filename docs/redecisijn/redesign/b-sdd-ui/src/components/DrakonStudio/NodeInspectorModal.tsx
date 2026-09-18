// src/components/DrakonStudio/NodeInspectorModal.tsx
// -----------------------------------------------------------------------------
// Оптимізований редактор вузла:
//   • компактна форма (grid) — назва, тип, семантичний зв'язок ADR-інваріанту
//   • маршрутизація (down/right)
//   • дві головні дії з чітким контрастом:
//        [Застосувати зміни] — emerald primary
//        [Видалити]         — rose destructive
// -----------------------------------------------------------------------------
import React, { useEffect, useState } from 'react';
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
} from 'lucide-react';

interface NodeInspectorModalProps {
  node: DrakonNodeIR | null;
  allNodes: DrakonNodeIR[];
  adrs: BitemporalAdr[];
  onClose: () => void;
  onUpdateNode: (n: DrakonNodeIR) => void;
  onDeleteNode: (id: string) => void;
}

const NODE_TYPES: { value: DrakonNodeType; label: string; hint: string }[] = [
  { value: 'action',   label: 'action',   hint: 'Дія / Алгоритмічний крок' },
  { value: 'question', label: 'question', hint: 'Умова ТАК/НІ' },
  { value: 'headline', label: 'headline', hint: 'Заголовок / етап процесу' },
  { value: 'address',  label: 'address',  hint: 'Маршрут / силует' },
  { value: 'end',      label: 'end',      hint: 'Термінальний вузол' },
];

export const NodeInspectorModal: React.FC<NodeInspectorModalProps> = ({
  node,
  allNodes,
  adrs,
  onClose,
  onUpdateNode,
  onDeleteNode,
}) => {
  const [label, setLabel] = useState('');
  const [nodeType, setNodeType] = useState<DrakonNodeType>('action');
  const [downEdge, setDownEdge] = useState('');
  const [rightEdge, setRightEdge] = useState('');
  const [invariantId, setInvariantId] = useState('');
  const [severity, setSeverity] = useState<'normal' | 'severe' | 'fatal'>('normal');
  const [routing, setRouting] = useState<'one' | 'two'>('one');
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    if (!node) return;
    setLabel(node.label || '');
    setNodeType(node.node_type || 'action');
    setDownEdge(node.edges?.down || '');
    setRightEdge(node.edges?.right || '');
    setInvariantId(node.semantic_binding?.adr_invariant_id || '');
    setSeverity((node.semantic_binding?.severity as any) || 'normal');
    setRouting(node.edges?.right ? 'two' : 'one');
    setIsSaved(false);
  }, [node]);

  useEffect(() => {
    if (nodeType === 'question' && routing === 'one') setRouting('two');
  }, [nodeType, routing]);

  if (!node) return null;

  const otherNodes = allNodes.filter((n) => n.node_id !== node.node_id);

  const availableInvariants = adrs.flatMap((adr) =>
    (adr.invariants || []).map((inv) => ({
      id: inv.id,
      adrId: adr.id,
      title: inv.statement,
    })),
  );

  const handleSave = () => {
    const updated: DrakonNodeIR = {
      ...node,
      label,
      node_type: nodeType,
      edges: {
        down: downEdge || null,
        right: routing === 'two' ? rightEdge || null : null,
      },
      semantic_binding: invariantId
        ? { adr_invariant_id: invariantId, severity }
        : undefined,
    };
    onUpdateNode(updated);
    setIsSaved(true);
    window.setTimeout(() => setIsSaved(false), 1500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 select-none">
      <div className="w-full max-w-2xl bg-[#141b27] border border-[#1e293b] rounded-lg shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <header className="flex items-center justify-between px-4 py-3 bg-[#0d121c] border-b border-[#1e293b] shrink-0">
          <div className="flex items-center gap-2">
            <FileCode className="w-4 h-4 text-[#f59e0b]" />
            <span className="font-mono font-bold text-slate-100 text-sm">
              Редактор вузла DRAKON
            </span>
            <span className="font-mono text-[10px] text-[#f59e0b] px-1.5 py-0.5 rounded bg-[#f59e0b]/10 border border-[#f59e0b]/30">
              #{node.node_id}
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-100 p-1 rounded hover:bg-[#1a2233] transition-colors"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </header>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 text-xs select-text">
          {/* Row 1 — name + type */}
          <div className="grid grid-cols-3 gap-3">
            <div className="col-span-2">
              <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                Назва вузла
              </label>
              <input
                type="text"
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                placeholder="Опишіть дію або запитання…"
                className="w-full h-8 bg-[#090d13] border border-[#1e293b] rounded px-2.5 text-slate-100 font-sans text-xs focus:border-[#f59e0b] focus:outline-none focus:ring-1 focus:ring-[#f59e0b]/30 transition-colors"
              />
            </div>
            <div>
              <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                Тип
              </label>
              <select
                value={nodeType}
                onChange={(e) => setNodeType(e.target.value as DrakonNodeType)}
                className="w-full h-8 bg-[#090d13] border border-[#1e293b] rounded px-2 text-slate-100 font-mono text-xs focus:border-[#f59e0b] focus:outline-none"
              >
                {NODE_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label} — {t.hint}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Row 2 — розширений опис */}
          <div>
            <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
              Детальний текст / Інструкція
            </label>
            <textarea
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              rows={3}
              placeholder="Розширений опис кроку алгоритму…"
              className="w-full bg-[#090d13] border border-[#1e293b] rounded p-2.5 text-slate-100 font-sans text-xs focus:border-[#f59e0b] focus:outline-none resize-none leading-relaxed"
            />
          </div>

          {/* Row 3 — routing selector */}
          <div className="rounded border border-[#1e293b] bg-[#0d121c] p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold">
                Маршрутизація
              </span>
              <div className="inline-flex bg-[#090d13] border border-[#1e293b] rounded p-0.5">
                {(['one', 'two'] as const).map((r) => (
                  <button
                    key={r}
                    disabled={nodeType === 'question' && r === 'one'}
                    onClick={() => setRouting(r)}
                    className={`px-2.5 h-6 rounded text-[10px] font-mono transition-all ${
                      routing === r
                        ? 'bg-[#141b27] text-[#f59e0b] font-bold shadow-inner'
                        : 'text-slate-400 hover:text-slate-200 disabled:opacity-40'
                    }`}
                  >
                    {r === 'one' ? '1 — Down' : '2 — Down + Right'}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2.5">
              <div>
                <label className="text-[11px] font-mono text-[#10b981] flex items-center gap-1 mb-1">
                  <ArrowDown className="w-3 h-3" />
                  {nodeType === 'question' ? 'ТАК (Down):' : 'Down:'}
                </label>
                <select
                  value={downEdge}
                  onChange={(e) => setDownEdge(e.target.value)}
                  className="w-full h-7 bg-[#090d13] border border-[#1e293b] rounded px-2 text-slate-200 font-mono text-[11px] focus:border-[#f59e0b] focus:outline-none"
                >
                  <option value="">— кінець гілки —</option>
                  {otherNodes.map((n) => (
                    <option key={n.node_id} value={n.node_id}>
                      [{n.node_type}] #{n.node_id} — {(n.label || '').slice(0, 28)}
                    </option>
                  ))}
                </select>
              </div>

              <div className={routing === 'one' ? 'opacity-40 pointer-events-none' : ''}>
                <label className="text-[11px] font-mono text-[#f43f5e] flex items-center gap-1 mb-1">
                  <CornerDownRight className="w-3 h-3" />
                  {nodeType === 'question' ? 'НІ (Right):' : 'Right:'}
                </label>
                <select
                  value={rightEdge}
                  onChange={(e) => setRightEdge(e.target.value)}
                  className="w-full h-7 bg-[#090d13] border border-[#1e293b] rounded px-2 text-slate-200 font-mono text-[11px] focus:border-[#f59e0b] focus:outline-none"
                >
                  <option value="">— немає розгалуження —</option>
                  {otherNodes.map((n) => (
                    <option key={n.node_id} value={n.node_id}>
                      [{n.node_type}] #{n.node_id} — {(n.label || '').slice(0, 28)}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <p className="text-[10px] text-slate-500 font-mono mt-2">
              Правило «Right is Worse»: права гілка веде до обробки помилки або відкату.
            </p>
          </div>

          {/* Row 4 — ADR invariant binding */}
          <div className="rounded border border-[#1e293b] bg-[#0d121c] p-3">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-[#f59e0b] mb-2">
              <Shield className="w-3.5 h-3.5" />
              Прив'язка до інваріанту ADR
            </div>

            <div className="grid grid-cols-3 gap-2.5">
              <div className="col-span-2">
                <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                  adr_invariant_id
                </label>
                <select
                  value={invariantId}
                  onChange={(e) => setInvariantId(e.target.value)}
                  className="w-full h-7 bg-[#090d13] border border-[#1e293b] rounded px-2 text-slate-200 font-mono text-[11px] focus:border-[#f59e0b] focus:outline-none"
                >
                  <option value="">— без прив'язки —</option>
                  {availableInvariants.map((inv) => (
                    <option key={inv.id} value={inv.id}>
                      {inv.id} · {inv.title.slice(0, 40)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                  Severity
                </label>
                <div className="flex gap-1">
                  {(['normal', 'severe', 'fatal'] as const).map((s) => {
                    const tone =
                      s === 'fatal'
                        ? { on: 'bg-[#f43f5e]/20 text-[#f43f5e] border-[#f43f5e]/50' }
                        : s === 'severe'
                          ? { on: 'bg-[#f59e0b]/20 text-[#f59e0b] border-[#f59e0b]/50' }
                          : { on: 'bg-[#10b981]/20 text-[#10b981] border-[#10b981]/50' };
                    const isActive = severity === s;
                    return (
                      <button
                        key={s}
                        type="button"
                        onClick={() => setSeverity(s)}
                        disabled={!invariantId}
                        className={`flex-1 h-7 px-1 rounded border text-[10px] font-mono uppercase transition-colors ${
                          isActive
                            ? tone.on
                            : 'bg-[#090d13] text-slate-500 border-[#1e293b] hover:text-slate-300 disabled:opacity-40'
                        }`}
                      >
                        {s.slice(0, 3)}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="flex items-center justify-between px-4 py-3 bg-[#0d121c] border-t border-[#1e293b] shrink-0">
          <button
            onClick={() => onDeleteNode(node.node_id)}
            className="inline-flex items-center gap-1.5 h-8 px-3 rounded border border-[#f43f5e]/50 bg-[#f43f5e]/10 text-[#f43f5e] hover:bg-[#f43f5e]/20 text-xs font-mono font-semibold transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
            Видалити
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="h-8 px-3 rounded border border-[#1e293b] bg-[#141b27] hover:bg-[#1a2233] text-slate-300 text-xs font-mono transition-colors"
            >
              Скасувати
            </button>
            <button
              onClick={handleSave}
              className="inline-flex items-center gap-1.5 h-8 px-4 rounded bg-[#10b981] hover:bg-[#10b981]/90 text-slate-950 text-xs font-mono font-bold shadow-sm transition-all"
            >
              {isSaved ? <Check className="w-3.5 h-3.5" /> : <Save className="w-3.5 h-3.5" />}
              {isSaved ? 'Збережено' : 'Застосувати зміни'}
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default NodeInspectorModal;
