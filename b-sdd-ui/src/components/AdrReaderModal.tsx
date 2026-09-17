// src/components/AdrReaderModal.tsx
// Astryx-native ADR Reader & Editor Dialog (ADR-009, ADR-010)
import React, { useEffect, useState } from 'react';
import type { BitemporalAdr } from '@/types/adr';
import { saveAdr } from '@/lib/api';
import { Dialog, Button, Badge, Segmented, Banner } from './astryx/primitives';
import {
  Shield,
  Clock,
  Copy,
  Check,
  Calendar,
  Layers,
  ExternalLink,
  Edit3,
  Eye,
  Save,
  Loader2,
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
  const [viewMode, setViewMode] = useState<string>('preview');
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

  const statusTone =
    adr.status === 'accepted'
      ? 'emerald'
      : adr.status === 'superseded'
        ? 'rose'
        : 'cyan';

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
          <h1 key={idx} className="text-xl font-bold text-slate-100 mt-2 mb-3 pb-2 border-b border-[#1e293b]">
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
    <Dialog
      isOpen={Boolean(adr)}
      onClose={onClose}
      maxWidth="max-w-5xl"
      title={
        <div className="flex items-center justify-between w-full pr-6">
          <div className="flex items-center gap-3">
            <Badge tone="amber" outline>
              {adr.id}
            </Badge>
            <Badge tone={statusTone} outline>
              {adr.status}
            </Badge>
            <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
              <Layers className="w-3.5 h-3.5" />
              {adr.component}
            </span>
            {adr.file_path && (
              <span className="text-[11px] font-mono text-slate-400 bg-[#090d13] px-2 py-0.5 rounded border border-[#1e293b]">
                {adr.file_path}
              </span>
            )}
          </div>

          <Segmented
            value={viewMode}
            onChange={(val) => setViewMode(val)}
            options={[
              {
                value: 'preview',
                label: (
                  <span className="flex items-center gap-1">
                    <Eye className="w-3.5 h-3.5" />
                    <span>Читання</span>
                  </span>
                ),
              },
              {
                value: 'edit',
                label: (
                  <span className="flex items-center gap-1">
                    <Edit3 className="w-3.5 h-3.5" />
                    <span>Редагування</span>
                    {isDirty && <span className="w-1.5 h-1.5 rounded-full bg-amber animate-pulse"></span>}
                  </span>
                ),
              },
            ]}
          />
        </div>
      }
      footer={
        <div className="flex items-center justify-between w-full text-xs font-mono">
          <div className="flex items-center gap-2">
            {saveFeedback ? (
              <span className={saveFeedback.type === 'success' ? 'text-emerald-400' : 'text-rose-400'}>
                {saveFeedback.message}
              </span>
            ) : (
              <span className="text-slate-500 text-[11px]">
                {isDirty ? 'Є незбережені зміни' : 'Файл синхронізовано з диском'}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {viewMode === 'edit' && isDirty && (
              <Button
                variant="ghost"
                size="sm"
                icon={<Undo2 className="w-3.5 h-3.5" />}
                onClick={() => setEditedContent(adr.content || '')}
              >
                Скинути
              </Button>
            )}

            {viewMode === 'edit' && (
              <Button
                variant="success"
                size="sm"
                icon={isSaving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
                onClick={handleSave}
                disabled={isSaving}
              >
                Зберегти на диск
              </Button>
            )}

            <Button variant="secondary" size="sm" onClick={onClose}>
              Закрити
            </Button>
          </div>
        </div>
      }
    >
      <div className="-m-4 flex flex-col h-[75vh] overflow-hidden">
        {/* Bitemporal & DAG Metadata Bar */}
        <div className="px-6 py-2 bg-[#090d13] border-b border-[#1e293b] flex items-center justify-between text-xs font-mono text-slate-400 shrink-0">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-amber" />
              <span>Date: {adr.date}</span>
            </span>
            <span className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-cyan" />
              <span>Valid: {adr.valid_from.split('T')[0]} → {adr.valid_to ? adr.valid_to.split('T')[0] : 'PRESENT'}</span>
            </span>
          </div>

          <div className="flex items-center gap-3">
            {adr.supersedes && (
              <div className="flex items-center gap-1 text-[11px]">
                <span className="text-slate-500">Supersedes:</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    const target = allAdrs.find((a) => a.id === adr.supersedes);
                    if (target) onSelectAdr(target);
                  }}
                  iconRight={<ExternalLink className="w-2.5 h-2.5" />}
                >
                  {adr.supersedes}
                </Button>
              </div>
            )}

            {adr.superseded_by && (
              <div className="flex items-center gap-1 text-[11px]">
                <span className="text-rose-400">Superseded by:</span>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => {
                    const target = allAdrs.find((a) => a.id === adr.superseded_by);
                    if (target) onSelectAdr(target);
                  }}
                  iconRight={<ExternalLink className="w-2.5 h-2.5" />}
                >
                  {adr.superseded_by}
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-hidden flex flex-col">
          {viewMode === 'preview' ? (
            <div className="flex-1 overflow-y-auto px-8 py-6 space-y-6 select-text bg-[#0d121c]">
              {/* Invariants Summary Section */}
              {adr.invariants && adr.invariants.length > 0 && (
                <div className="p-4 rounded-xl bg-[#141b27] border border-amber/30 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs font-semibold text-amber font-mono">
                      <Shield className="w-4 h-4 text-amber" />
                      <span>Архітектурні інваріанти рішення ({adr.invariants.length})</span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-400">Клікніть для копіювання ID</span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                    {adr.invariants.map((inv) => (
                      <div
                        key={inv.id}
                        className="p-3 rounded-lg bg-[#090d13] border border-[#1e293b] flex flex-col justify-between gap-2 text-xs hover:border-amber/50 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-mono font-bold text-amber text-[11px]">{inv.id}</span>
                          <Badge tone="amber" outline>
                            {inv.severity || 'mandatory'}
                          </Badge>
                        </div>
                        <p className="text-slate-300 font-sans leading-relaxed">{inv.statement}</p>
                        <button
                          onClick={() => handleCopyInvariant(inv.id)}
                          className="self-end text-[10px] font-mono text-slate-400 hover:text-amber flex items-center gap-1 mt-1 cursor-pointer"
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
              <div className="p-6 rounded-xl bg-[#090d13] border border-[#1e293b] space-y-2">
                {renderFormattedMarkdown(editedContent || adr.content || '')}
              </div>
            </div>
          ) : (
            /* Live Markdown Editor */
            <div className="flex-1 flex flex-col bg-[#090d13] overflow-hidden">
              <div className="px-4 py-2 bg-[#0d121c] border-b border-[#1e293b] flex items-center justify-between text-xs font-mono text-slate-400">
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
                className="flex-1 w-full p-6 bg-transparent text-slate-200 font-mono text-xs leading-relaxed resize-none focus:outline-none selection:bg-amber/30"
                placeholder="Введіть повний Markdown текст архітектурного рішення..."
                spellCheck={false}
              />
            </div>
          )}
        </div>
      </div>
    </Dialog>
  );
};

export default AdrReaderModal;
