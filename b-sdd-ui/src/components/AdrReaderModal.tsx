// src/components/AdrReaderModal.tsx
import React, { useEffect, useState, useCallback } from 'react';
import type { BitemporalAdr } from '@/types/adr';
import { saveAdr } from '@/lib/api';
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
  Edit3,
  Eye,
  Save,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Undo2,
} from 'lucide-react';

interface AdrReaderModalProps {
  adr: BitemporalAdr | null;
  allAdrs: BitemporalAdr[];
  onClose: () => void;
  onSelectAdr: (adr: BitemporalAdr) => void;
  onAdrSaved?: () => void;
}

export const AdrReaderModal: React.FC<AdrReaderModalProps> = ({
  adr,
  allAdrs,
  onClose,
  onSelectAdr,
  onAdrSaved,
}) => {
  const [copiedInvId, setCopiedInvId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'preview' | 'edit'>('preview');
  const [editedContent, setEditedContent] = useState<string>('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveFeedback, setSaveFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Sync content when active ADR changes
  useEffect(() => {
    if (adr) {
      setEditedContent(adr.content || '');
      setSaveFeedback(null);
    }
  }, [adr]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        void handleSave();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose, editedContent, adr]);

  if (!adr) return null;

  const handleCopyInvariant = (id: string) => {
    void navigator.clipboard.writeText(id).then(() => {
      setCopiedInvId(id);
      window.setTimeout(() => setCopiedInvId(null), 1500);
    });
  };

  const handleSave = async () => {
    if (!adr.file_path) {
      setSaveFeedback({ type: 'error', message: 'Відсутній шлях до файлу для збереження.' });
      return;
    }

    setIsSaving(true);
    setSaveFeedback(null);

    try {
      const res = await saveAdr({
        id: adr.id,
        file_path: adr.file_path,
        content: editedContent,
      });

      if (res.success) {
        setSaveFeedback({
          type: 'success',
          message: `Збережено у ${res.file_path} (${res.bytes_written} байт). Правила оновлено!`,
        });
        adr.content = editedContent;
        onAdrSaved?.();
        window.setTimeout(() => setSaveFeedback(null), 4000);
      }
    } catch (err) {
      setSaveFeedback({
        type: 'error',
        message: `Помилка збереження: ${err instanceof Error ? err.message : String(err)}`,
      });
    } finally {
      setIsSaving(false);
    }
  };

  const statusColor =
    adr.status === 'accepted'
      ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
      : adr.status === 'superseded'
        ? 'bg-rose-500/15 text-rose-400 border-rose-500/30 line-through'
        : 'bg-blue-500/15 text-blue-400 border-blue-500/30';

  // Count words and invariants in edited text
  const wordCount = editedContent.trim().split(/\s+/).filter(Boolean).length;
  const invariantCount = (editedContent.match(/-\s+(ADR-[\w-]+-INV-\d+|[A-Z0-9_-]+:)/g) || []).length;
  const isDirty = editedContent !== (adr.content || '');

  // Simple clean markdown formatter for preview mode
  const renderFormattedMarkdown = (raw: string) => {
    const lines = raw.split('\n');
    return lines.map((line, idx) => {
      if (line.startsWith('# ')) {
        return (
          <h1 key={idx} className="text-xl font-bold text-slate-100 mt-2 mb-3 pb-2 border-b border-border-subtle">
            {line.substring(2)}
          </h1>
        );
      }
      if (line.startsWith('## ')) {
        return (
          <h2 key={idx} className="text-base font-semibold text-amber mt-5 mb-2 flex items-center gap-2">
            <span className="w-1.5 h-4 bg-amber rounded-xs"></span>
            {line.substring(3)}
          </h2>
        );
      }
      if (line.startsWith('### ')) {
        return (
          <h3 key={idx} className="text-sm font-semibold text-slate-200 mt-3 mb-1.5">
            {line.substring(4)}
          </h3>
        );
      }
      if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        const bulletText = line.trim().substring(2);
        const isInvariant = bulletText.includes('INV-') || bulletText.startsWith('ADR-');
        return (
          <li
            key={idx}
            className={`ml-5 list-disc my-1 leading-relaxed ${
              isInvariant ? 'text-amber font-mono font-medium' : 'text-slate-300'
            }`}
          >
            {bulletText}
          </li>
        );
      }
      if (line.trim() === '') {
        return <div key={idx} className="h-2" />;
      }
      return (
        <p key={idx} className="text-slate-300 leading-relaxed my-1">
          {line}
        </p>
      );
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-150">
      <div className="w-full max-w-5xl max-h-[92vh] bg-panel border border-border-subtle rounded-xl shadow-2xl flex flex-col overflow-hidden text-slate-100">
        {/* Header */}
        <div className="px-6 py-3.5 bg-card border-b border-border-subtle flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
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
              <span className="text-[11px] font-mono text-slate-400 bg-canvas px-2 py-0.5 rounded border border-border-subtle">
                {adr.file_path}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* View Mode Switcher */}
            <div className="flex items-center rounded-lg bg-canvas p-0.5 border border-border-subtle text-xs font-mono">
              <button
                onClick={() => setViewMode('preview')}
                className={`flex items-center gap-1 px-3 py-1 rounded transition-colors ${
                  viewMode === 'preview'
                    ? 'bg-amber text-slate-950 font-bold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Eye className="w-3.5 h-3.5" />
                <span>Читання</span>
              </button>
              <button
                onClick={() => setViewMode('edit')}
                className={`flex items-center gap-1 px-3 py-1 rounded transition-colors ${
                  viewMode === 'edit'
                    ? 'bg-amber text-slate-950 font-bold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span>Редагування</span>
                {isDirty && <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>}
              </button>
            </div>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
              title="Закрити (Esc)"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Bitemporal & DAG Metadata Bar */}
        <div className="px-6 py-2 bg-canvas/90 border-b border-border-subtle flex items-center justify-between text-xs font-mono text-slate-400">
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

          <div className="flex items-center gap-3">
            {adr.supersedes && (
              <div className="flex items-center gap-1 text-[11px]">
                <span className="text-slate-500">Supersedes:</span>
                <button
                  onClick={() => {
                    const target = allAdrs.find((a) => a.id === adr.supersedes);
                    if (target) onSelectAdr(target);
                  }}
                  className="px-2 py-0.5 rounded bg-card hover:bg-slate-800 text-amber border border-border-subtle flex items-center gap-1"
                >
                  <span>{adr.supersedes}</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </button>
              </div>
            )}

            {adr.superseded_by && (
              <div className="flex items-center gap-1 text-[11px]">
                <span className="text-rose-400">Superseded by:</span>
                <button
                  onClick={() => {
                    const target = allAdrs.find((a) => a.id === adr.superseded_by);
                    if (target) onSelectAdr(target);
                  }}
                  className="px-2 py-0.5 rounded bg-card hover:bg-slate-800 text-rose-400 border border-border-subtle flex items-center gap-1"
                >
                  <span>{adr.superseded_by}</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-hidden flex flex-col">
          {viewMode === 'preview' ? (
            <div className="flex-1 overflow-y-auto px-8 py-6 space-y-6 select-text bg-panel">
              {/* Invariants Summary Section */}
              {adr.invariants && adr.invariants.length > 0 && (
                <div className="p-4 rounded-xl bg-card/80 border border-amber/30 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs font-semibold text-amber">
                      <Shield className="w-4 h-4 text-amber" />
                      <span>Архітектурні інваріанти рішення ({adr.invariants.length})</span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-400">Клікніть для копіювання ID</span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                    {adr.invariants.map((inv) => (
                      <div
                        key={inv.id}
                        className="p-3 rounded-lg bg-canvas border border-border-subtle flex flex-col justify-between gap-2 text-xs hover:border-amber/50 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-mono font-bold text-amber text-[11px]">{inv.id}</span>
                          <span className="px-1.5 py-0.2 rounded bg-amber/10 text-amber text-[9px] uppercase font-mono border border-amber/20">
                            {inv.severity || 'mandatory'}
                          </span>
                        </div>
                        <p className="text-slate-300 font-sans leading-relaxed">{inv.statement}</p>
                        <button
                          onClick={() => handleCopyInvariant(inv.id)}
                          className="self-end text-[10px] font-mono text-slate-400 hover:text-amber flex items-center gap-1 mt-1"
                        >
                          {copiedInvId === inv.id ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-400" />
                              <span className="text-emerald-400">Скопійовано</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" />
                              <span>Копіювати ID</span>
                            </>
                          )}
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Formatted Markdown Body */}
              <div className="p-6 rounded-xl bg-canvas border border-border-subtle space-y-2">
                {renderFormattedMarkdown(editedContent || adr.content || '')}
              </div>
            </div>
          ) : (
            /* Live Markdown Editor */
            <div className="flex-1 flex flex-col bg-canvas overflow-hidden">
              <div className="px-4 py-2 bg-card/60 border-b border-border-subtle flex items-center justify-between text-xs font-mono text-slate-400">
                <div className="flex items-center gap-4">
                  <span>Слів: <strong className="text-slate-200">{wordCount}</strong></span>
                  <span>Символів: <strong className="text-slate-200">{editedContent.length}</strong></span>
                  <span>Виявлено інваріантів: <strong className="text-amber">{invariantCount}</strong></span>
                </div>
                <div className="text-[11px] text-slate-500">
                  Ctrl+S або Cmd+S для миттєвого збереження на диск
                </div>
              </div>

              <textarea
                value={editedContent}
                onChange={(e) => setEditedContent(e.target.value)}
                className="flex-1 w-full p-6 bg-transparent text-slate-200 font-mono text-xs leading-relaxed resize-none focus:outline-hidden selection:bg-amber/30"
                placeholder="Введіть повний Markdown текст архітектурного рішення..."
                spellCheck={false}
              />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-card border-t border-border-subtle flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            {saveFeedback ? (
              <div
                className={`flex items-center gap-1.5 font-mono text-xs ${
                  saveFeedback.type === 'success' ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {saveFeedback.type === 'success' ? (
                  <CheckCircle2 className="w-4 h-4" />
                ) : (
                  <AlertCircle className="w-4 h-4" />
                )}
                <span>{saveFeedback.message}</span>
              </div>
            ) : (
              <span className="text-slate-500 font-mono text-[11px]">
                {isDirty ? 'Є незбережені зміни' : 'Файл синхронізовано з диском'}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {viewMode === 'edit' && isDirty && (
              <button
                onClick={() => setEditedContent(adr.content || '')}
                className="px-3 py-1.5 rounded-lg border border-border-subtle hover:bg-slate-800 text-slate-400 hover:text-slate-200 flex items-center gap-1.5 transition-colors"
              >
                <Undo2 className="w-3.5 h-3.5" />
                <span>Скинути</span>
              </button>
            )}

            {viewMode === 'edit' && (
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold flex items-center gap-1.5 transition-all shadow-md disabled:opacity-50"
              >
                {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                <span>Зберегти на диск</span>
              </button>
            )}

            <button
              onClick={onClose}
              className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium transition-colors"
            >
              Закрити
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdrReaderModal;
