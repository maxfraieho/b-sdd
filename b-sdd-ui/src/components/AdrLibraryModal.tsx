// src/components/AdrLibraryModal.tsx
// Astryx-native ADR Library Dialog (ADR-009, ADR-010)
import React, { useState } from 'react';
import type { BitemporalAdr } from '@/types/adr';
import { Dialog, Button, Badge } from './astryx/primitives';
import {
  BookOpen,
  Search,
  Shield,
  Calendar,
  Clock,
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
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      maxWidth="max-w-6xl"
      title={
        <div className="flex items-center gap-2.5">
          <BookOpen className="w-5 h-5 text-emerald-400 shrink-0" />
          <div>
            <div className="text-sm font-bold text-slate-100 font-mono">
              Бібліотека Архітектурних Рішень (ADR & Decision Records)
            </div>
            <span className="text-[11px] text-slate-400 font-mono font-normal">
              Доступно {adrs.length} чинних та бітемпоральних документів (docs/adr & docs/decision)
            </span>
          </div>
        </div>
      }
      footer={
        <div className="flex items-center justify-between w-full text-xs font-mono text-slate-400">
          <span>B-SDD Architectural Decision Records · Full Text Reader</span>
          <Button variant="secondary" size="sm" onClick={onClose}>
            Закрити
          </Button>
        </div>
      }
    >
      {/* 2-Column Layout */}
      <div className="h-[70vh] flex overflow-hidden -m-4">
        {/* Left Column: ADR List & Search */}
        <div className="w-80 border-r border-[#1e293b] flex flex-col bg-[#0d121c]/60 shrink-0">
          <div className="p-3 border-b border-[#1e293b]">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
              <input
                type="text"
                placeholder="Пошук ADR або інваріанту..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#090d13] border border-[#1e293b] rounded pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 font-mono focus:border-amber focus:outline-none"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
            {filteredAdrs.map((adr) => {
              const isSelected = adr.id === currentAdr?.id;
              const tone =
                adr.status === 'accepted'
                  ? 'emerald'
                  : adr.status === 'superseded'
                    ? 'neutral'
                    : 'cyan';

              return (
                <div
                  key={adr.id}
                  onClick={() => setSelectedAdrId(adr.id)}
                  className={`p-2.5 rounded border text-xs cursor-pointer select-none transition-all ${
                    isSelected
                      ? 'bg-[#1a2233] border-amber/60 shadow-sm'
                      : 'bg-[#141b27]/60 border-[#1e293b] hover:bg-[#1a2233] hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono font-bold text-amber">{adr.id}</span>
                    <Badge tone={tone} outline={adr.status === 'accepted'}>
                      {adr.status}
                    </Badge>
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
        <div className="flex-1 flex flex-col bg-[#090d13] overflow-hidden">
          {currentAdr ? (
            <>
              {/* Document Topbar */}
              <div className="px-6 py-3 bg-[#0d121c] border-b border-[#1e293b] flex items-center justify-between shrink-0">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <Badge tone="amber" outline>
                      {currentAdr.id}
                    </Badge>
                    <span className="text-xs font-bold text-slate-100 font-mono">{currentAdr.title}</span>
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
                    <Clock className="w-3.5 h-3.5 text-cyan" />
                    <span>{currentAdr.valid_from.split('T')[0]} → PRESENT</span>
                  </span>
                </div>
              </div>

              {/* Invariants Bar */}
              {currentAdr.invariants && currentAdr.invariants.length > 0 && (
                <div className="px-6 py-2 bg-[#0d121c]/80 border-b border-[#1e293b] flex items-center gap-2 overflow-x-auto text-[11px] font-mono">
                  <span className="text-amber font-semibold flex items-center gap-1 shrink-0">
                    <Shield className="w-3.5 h-3.5" />
                    <span>Інваріанти:</span>
                  </span>
                  {currentAdr.invariants.map((inv) => (
                    <div
                      key={inv.id}
                      className="px-2 py-0.5 rounded bg-[#141b27] border border-[#1e293b] text-slate-300 flex items-center gap-1.5 shrink-0"
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
              <div className="flex-1 overflow-y-auto p-6 font-mono text-[13px] leading-relaxed select-text bg-[#090d13] text-slate-200 whitespace-pre-wrap">
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
    </Dialog>
  );
};
