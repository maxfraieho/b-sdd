// src/components/AdrReaderModal.tsx
import React, { useEffect, useState } from 'react';
import type { BitemporalAdr } from '@/types/adr';
import {
  X,
  FileText,
  Shield,
  Clock,
  ArrowRight,
  Copy,
  Check,
  Calendar,
  Layers,
  ExternalLink,
} from 'lucide-react';

interface AdrReaderModalProps {
  adr: BitemporalAdr | null;
  allAdrs: BitemporalAdr[];
  onClose: () => void;
  onSelectAdr: (adr: BitemporalAdr) => void;
}

export const AdrReaderModal: React.FC<AdrReaderModalProps> = ({
  adr,
  allAdrs,
  onClose,
  onSelectAdr,
}) => {
  const [copiedInvId, setCopiedInvId] = useState<string | null>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!adr) return null;

  const handleCopyInvariant = (id: string) => {
    void navigator.clipboard.writeText(id).then(() => {
      setCopiedInvId(id);
      window.setTimeout(() => setCopiedInvId(null), 1500);
    });
  };

  const statusColor =
    adr.status === 'accepted'
      ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
      : adr.status === 'superseded'
        ? 'bg-rose-500/15 text-rose-400 border-rose-500/30 line-through'
        : 'bg-blue-500/15 text-blue-400 border-blue-500/30';

  // Render raw markdown content into structured sections if available
  const content = adr.content || '';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-150">
      <div className="w-full max-w-4xl max-h-[90vh] bg-panel border border-border-subtle rounded-xl shadow-2xl flex flex-col overflow-hidden text-slate-100">
        {/* Header */}
        <div className="px-6 py-4 bg-card border-b border-border-subtle flex items-start justify-between shrink-0">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-amber px-2 py-0.5 rounded bg-amber/10 border border-amber/30">
                {adr.id}
              </span>
              <span className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border ${statusColor}`}>
                {adr.status}
              </span>
              <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                <Layers className="w-3.5 h-3.5" />
                {adr.component}
              </span>
              {adr.file_path && (
                <span className="text-[10px] font-mono text-slate-500">
                  ({adr.file_path})
                </span>
              )}
            </div>
            <h2 className="text-lg font-bold text-slate-100 leading-snug">{adr.title}</h2>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
            title="Закрити (Esc)"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Bitemporal & DAG Metadata Bar */}
        <div className="px-6 py-2.5 bg-canvas/80 border-b border-border-subtle flex items-center justify-between text-xs font-mono text-slate-400">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-amber" />
              <span>Date: {adr.date}</span>
            </span>
            <span className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-cyan-400" />
              <span>Valid: {adr.valid_from.split('T')[0]} → {adr.valid_to ? adr.valid_to.split('T')[0] : 'PRESENT'}</span>
            </span>
          </div>

          {adr.supersedes && (
            <div className="flex items-center gap-2">
              <span className="text-slate-500">Supersedes:</span>
              <button
                onClick={() => {
                  const target = allAdrs.find((a) => a.id === adr.supersedes);
                  if (target) onSelectAdr(target);
                }}
                className="px-2 py-0.5 rounded bg-card hover:bg-slate-800 text-amber border border-border-subtle text-[11px] flex items-center gap-1"
              >
                <span>{adr.supersedes}</span>
                <ExternalLink className="w-2.5 h-2.5" />
              </button>
            </div>
          )}

          {adr.superseded_by && (
            <div className="flex items-center gap-2">
              <span className="text-rose-400">Superseded by:</span>
              <button
                onClick={() => {
                  const target = allAdrs.find((a) => a.id === adr.superseded_by);
                  if (target) onSelectAdr(target);
                }}
                className="px-2 py-0.5 rounded bg-card hover:bg-slate-800 text-rose-400 border border-border-subtle text-[11px] flex items-center gap-1"
              >
                <span>{adr.superseded_by}</span>
                <ExternalLink className="w-2.5 h-2.5" />
              </button>
            </div>
          )}
        </div>

        {/* Modal Body: Scrollable ADR Content */}
        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-6 select-text">
          {/* Invariants Summary Section */}
          {adr.invariants && adr.invariants.length > 0 && (
            <div className="p-4 rounded-lg bg-card/60 border border-border-subtle space-y-3">
              <div className="flex items-center gap-2 text-xs font-semibold text-amber">
                <Shield className="w-4 h-4" />
                <span>Зафіксовані архітектурні інваріанти ({adr.invariants.length})</span>
              </div>
              <div className="space-y-2">
                {adr.invariants.map((inv) => (
                  <div
                    key={inv.id}
                    className="p-2.5 rounded bg-canvas border border-border-subtle flex items-start justify-between gap-3 text-xs"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-amber text-[11px]">{inv.id}</span>
                        {inv.severity && (
                          <span className="px-1.5 py-0.2 rounded bg-amber/15 text-amber text-[9px] uppercase font-mono">
                            {inv.severity}
                          </span>
                        )}
                      </div>
                      <p className="text-slate-300 font-sans leading-relaxed">{inv.statement}</p>
                    </div>
                    <button
                      onClick={() => handleCopyInvariant(inv.id)}
                      className="p-1.5 text-slate-400 hover:text-slate-200 rounded hover:bg-slate-800 transition-colors shrink-0"
                      title="Скопіювати Invariant ID"
                    >
                      {copiedInvId === inv.id ? (
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Full Markdown Body */}
          {content ? (
            <div className="prose prose-invert max-w-none font-sans text-sm leading-relaxed space-y-4 text-slate-200 whitespace-pre-wrap font-mono bg-canvas p-4 rounded-lg border border-border-subtle overflow-x-auto text-[13px]">
              {content}
            </div>
          ) : (
            <div className="space-y-4 text-xs">
              <div>
                <h4 className="text-slate-400 font-mono uppercase text-[11px] mb-1">Контекст та проблема</h4>
                <p className="p-3 bg-canvas rounded border border-border-subtle text-slate-300">
                  {adr.context || 'Опис контексту рішення.'}
                </p>
              </div>

              <div>
                <h4 className="text-slate-400 font-mono uppercase text-[11px] mb-1">Прийняте рішення</h4>
                <p className="p-3 bg-canvas rounded border border-border-subtle text-slate-300">
                  {adr.decision_outcome || 'Опис результату рішення.'}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-card border-t border-border-subtle flex items-center justify-between text-xs">
          <span className="text-slate-400 font-mono">
            B-SDD Bitemporal Spec-Driven Architecture Document
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium transition-colors"
          >
            Закрити
          </button>
        </div>
      </div>
    </div>
  );
};
