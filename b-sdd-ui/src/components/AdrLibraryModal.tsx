// src/components/AdrLibraryModal.tsx
import React, { useState } from 'react';
import type { BitemporalAdr } from '@/types/adr';
import {
  X,
  BookOpen,
  Search,
  FileText,
  Shield,
  Layers,
  Calendar,
  Clock,
  ExternalLink,
  Copy,
  Check,
} from 'lucide-react';

interface AdrLibraryModalProps {
  isOpen: boolean;
  onClose: () => void;
  adrs: BitemporalAdr[];
  onSelectAdrForInspect?: (adr: BitemporalAdr) => void;
}

export const AdrLibraryModal: React.FC<AdrLibraryModalProps> = ({
  isOpen,
  onClose,
  adrs,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAdrId, setSelectedAdrId] = useState<string>(adrs[0]?.id || '');
  const [copiedInvId, setCopiedInvId] = useState<string | null>(null);

  if (!isOpen) return null;

  const filteredAdrs = adrs.filter(
    (adr) =>
      adr.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      adr.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (adr.content && adr.content.toLowerCase().includes(searchQuery.toLowerCase())),
  );

  const currentAdr =
    filteredAdrs.find((a) => a.id === selectedAdrId) || filteredAdrs[0] || adrs[0] || null;

  const handleCopyInvariant = (id: string) => {
    void navigator.clipboard.writeText(id).then(() => {
      setCopiedInvId(id);
      window.setTimeout(() => setCopiedInvId(null), 1500);
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-150">
      <div className="w-full max-w-6xl h-[88vh] bg-panel border border-border-subtle rounded-xl shadow-2xl flex flex-col overflow-hidden text-slate-100">
        {/* Header */}
        <div className="px-6 py-4 bg-card border-b border-border-subtle flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2.5">
            <BookOpen className="w-5 h-5 text-emerald-400" />
            <div>
              <h2 className="text-sm font-bold text-slate-100 font-mono">
                Бібліотека Архітектурних Рішень (ADR & Decision Records)
              </h2>
              <span className="text-[11px] text-slate-400 font-mono">
                Доступно {adrs.length} чинних та бітемпоральних документів (docs/adr & docs/decision)
              </span>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 2-Column Layout */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Column: ADR List & Search */}
          <div className="w-80 border-r border-border-subtle flex flex-col bg-card/40 shrink-0">
            <div className="p-3 border-b border-border-subtle">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
                <input
                  type="text"
                  placeholder="Пошук ADR або інваріанту..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-canvas border border-border-subtle rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 font-mono focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
              {filteredAdrs.map((adr) => {
                const isSelected = adr.id === currentAdr?.id;
                const statusColor =
                  adr.status === 'accepted'
                    ? 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10'
                    : adr.status === 'superseded'
                      ? 'text-slate-500 border-slate-700 bg-slate-900 line-through'
                      : 'text-blue-400 border-blue-500/30 bg-blue-500/10';

                return (
                  <div
                    key={adr.id}
                    onClick={() => setSelectedAdrId(adr.id)}
                    className={`p-2.5 rounded-lg border text-xs cursor-pointer select-none transition-all ${
                      isSelected
                        ? 'bg-panel border-emerald-500 ring-1 ring-emerald-500 shadow-md'
                        : 'bg-card/70 border-border-subtle hover:bg-slate-800 hover:border-slate-600'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono font-bold text-amber">{adr.id}</span>
                      <span className={`text-[9px] font-mono uppercase px-1.5 py-0.2 rounded border ${statusColor}`}>
                        {adr.status}
                      </span>
                    </div>
                    <h4 className="font-medium text-slate-200 line-clamp-2 text-[11px]">
                      {adr.title}
                    </h4>
                    <div className="flex items-center justify-between text-[10px] text-slate-500 mt-2 font-mono">
                      <span>{adr.invariants.length} інваріантів</span>
                      <span>{adr.date}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Column: Full ADR Markdown Viewer */}
          <div className="flex-1 flex flex-col bg-canvas overflow-hidden">
            {currentAdr ? (
              <>
                {/* Document Topbar */}
                <div className="px-6 py-3 bg-card border-b border-border-subtle flex items-center justify-between shrink-0">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-amber px-2 py-0.5 rounded bg-amber/10 border border-amber/30">
                        {currentAdr.id}
                      </span>
                      <span className="text-xs font-bold text-slate-100">{currentAdr.title}</span>
                    </div>
                    {currentAdr.file_path && (
                      <span className="text-[10px] text-slate-500 font-mono block">
                        Файл: <code>{currentAdr.file_path}</code>
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-3 text-xs font-mono text-slate-400">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5 text-amber" />
                      <span>{currentAdr.date}</span>
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-cyan-400" />
                      <span>{currentAdr.valid_from.split('T')[0]} → PRESENT</span>
                    </span>
                  </div>
                </div>

                {/* Invariants Bar */}
                {currentAdr.invariants && currentAdr.invariants.length > 0 && (
                  <div className="px-6 py-2 bg-panel border-b border-border-subtle flex items-center gap-2 overflow-x-auto text-[11px] font-mono">
                    <span className="text-amber font-semibold flex items-center gap-1 shrink-0">
                      <Shield className="w-3.5 h-3.5" />
                      <span>Інваріанти:</span>
                    </span>
                    {currentAdr.invariants.map((inv) => (
                      <div
                        key={inv.id}
                        className="px-2 py-0.5 rounded bg-card border border-border-subtle text-slate-300 flex items-center gap-1.5 shrink-0"
                      >
                        <span className="text-amber font-bold">{inv.id}</span>
                        <button
                          onClick={() => handleCopyInvariant(inv.id)}
                          className="hover:text-slate-100"
                          title="Скопіювати ID"
                        >
                          {copiedInvId === inv.id ? (
                            <Check className="w-3 h-3 text-emerald-400" />
                          ) : (
                            <Copy className="w-3 h-3 text-slate-500" />
                          )}
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Markdown View Area */}
                <div className="flex-1 overflow-y-auto p-6 font-mono text-[13px] leading-relaxed select-text bg-canvas text-slate-200 whitespace-pre-wrap">
                  {currentAdr.content || (
                    <div className="p-8 text-center text-slate-500">
                      Повний текст документа не знайдено.
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-slate-500 font-mono">
                Оберіть ADR зі списку ліворуч для перегляду
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-card border-t border-border-subtle flex items-center justify-between text-xs font-mono text-slate-400 shrink-0">
          <span>B-SDD Architectural Decision Records · Full Text Reader</span>
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
