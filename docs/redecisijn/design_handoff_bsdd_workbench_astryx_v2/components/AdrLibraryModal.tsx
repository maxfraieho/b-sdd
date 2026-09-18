// src/components/AdrLibraryModal.tsx
// -----------------------------------------------------------------------------
// Astryx ADR Library — Reader + Editor (MADR 3.0)
//   • Ліва колонка: пошук + список + кнопка [+ Новий ADR]
//   • Права колонка:
//        MODE 'read'  — Markdown reader з інваріантами
//        MODE 'edit'  — форма MADR 3.0 (Context / Decision / Consequences / Invariants)
//                        і кнопки [Amend (superseded_by)] / [Save Draft] / [Publish]
// -----------------------------------------------------------------------------
import React, { useMemo, useState } from 'react';
import type { BitemporalAdr } from '@/types/adr';
import { Dialog, Button, Badge } from './astryx/primitives';
import {
  BookOpen,
  Search,
  Shield,
  Calendar,
  Copy,
  Check,
  Plus,
  Pencil,
  Eye,
  Save,
  GitBranch,
  ShieldPlus,
  Trash2,
} from 'lucide-react';

type Mode = 'read' | 'edit';

interface AdrLibraryModalProps {
  isOpen: boolean;
  onClose: () => void;
  adrs: BitemporalAdr[];
  onCreateAdr?: (draft: Partial<BitemporalAdr>) => void;
  onSaveAdr?: (adr: BitemporalAdr) => void;
  onAmendAdr?: (base: BitemporalAdr, amended: Partial<BitemporalAdr>) => void;
}

const emptyDraft = (nextId: string): Partial<BitemporalAdr> => ({
  id: nextId,
  title: '',
  status: 'proposed',
  date: new Date().toISOString().slice(0, 10),
  valid_from: new Date().toISOString(),
  invariants: [],
  content: `# ${nextId} — <TITLE>

## Context
Опишіть системний контекст і сили, що впливають на це рішення…

## Decision
Ми ухвалили…

## Consequences
### Positive
- …

### Negative
- …

## Invariants
- INV-XX-01 — …
`,
});

export const AdrLibraryModal: React.FC<AdrLibraryModalProps> = ({
  isOpen,
  onClose,
  adrs,
  onCreateAdr,
  onSaveAdr,
  onAmendAdr,
}) => {
  const [q, setQ] = useState('');
  const [selectedId, setSelectedId] = useState<string>(adrs[0]?.id || '');
  const [mode, setMode] = useState<Mode>('read');
  const [draft, setDraft] = useState<Partial<BitemporalAdr> | null>(null);
  const [copiedInv, setCopiedInv] = useState<string | null>(null);

  const filtered = useMemo(
    () =>
      adrs.filter(
        (a) =>
          a.title.toLowerCase().includes(q.toLowerCase()) ||
          a.id.toLowerCase().includes(q.toLowerCase()) ||
          (a.content || '').toLowerCase().includes(q.toLowerCase()),
      ),
    [adrs, q],
  );

  const current = filtered.find((a) => a.id === selectedId) || filtered[0] || adrs[0] || null;
  const editing = mode === 'edit' && draft;

  const startNew = () => {
    const nextNum = String(adrs.length + 1).padStart(3, '0');
    setDraft(emptyDraft(`ADR-${nextNum}`));
    setMode('edit');
  };

  const startEdit = () => {
    if (!current) return;
    setDraft({ ...current });
    setMode('edit');
  };

  const startAmend = () => {
    if (!current) return;
    const nextNum = String(adrs.length + 1).padStart(3, '0');
    const amended: Partial<BitemporalAdr> = {
      ...emptyDraft(`ADR-${nextNum}`),
      title: `${current.title} (Amended)`,
      content: `# ADR-${nextNum} — ${current.title} (Amended)

> Supersedes **${current.id}** — див. попередній контекст.

## Context
${''}

## Decision
Ми амендуємо ${current.id}. Нове рішення полягає в тому, що…

## Consequences

## Invariants
`,
    };
    setDraft(amended);
    setMode('edit');
  };

  const commit = (publish: boolean) => {
    if (!draft || !draft.id) return;
    const finalAdr = { ...draft, status: publish ? 'accepted' : 'proposed' } as BitemporalAdr;
    if (adrs.some((a) => a.id === draft.id)) {
      onSaveAdr?.(finalAdr);
    } else {
      onCreateAdr?.(finalAdr);
    }
    setMode('read');
    setDraft(null);
    setSelectedId(finalAdr.id);
  };

  const copyInv = (id: string) => {
    void navigator.clipboard.writeText(id).then(() => {
      setCopiedInv(id);
      window.setTimeout(() => setCopiedInv(null), 1500);
    });
  };

  if (!isOpen) return null;

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      maxWidth="max-w-6xl"
      title={
        <div className="flex items-center gap-2.5">
          <BookOpen className="w-5 h-5 text-[#10b981] shrink-0" />
          <div>
            <div className="text-sm font-bold text-slate-100 font-mono">
              Бібліотека Архітектурних Рішень · MADR 3.0
            </div>
            <span className="text-[11px] text-slate-400 font-mono font-normal">
              {adrs.length} документів · Reader + Editor + Amend
            </span>
          </div>
        </div>
      }
      footer={
        <div className="flex items-center justify-between w-full text-xs font-mono text-slate-400">
          <span>docs/adr/ · docs/decision/</span>
          <Button variant="secondary" size="sm" onClick={onClose}>
            Закрити
          </Button>
        </div>
      }
    >
      <div className="h-[72vh] flex overflow-hidden -m-4">
        {/* ============ LEFT: list + search + [+ Новий ADR] ================ */}
        <aside className="w-80 shrink-0 border-r border-[#1e293b] bg-[#0d121c]/60 flex flex-col">
          <div className="p-3 border-b border-[#1e293b] space-y-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
              <input
                type="text"
                placeholder="Пошук ADR або INV…"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                className="w-full h-8 bg-[#090d13] border border-[#1e293b] rounded pl-8 pr-3 text-xs text-slate-200 placeholder-slate-500 font-mono focus:border-[#f59e0b] focus:outline-none"
              />
            </div>
            <button
              onClick={startNew}
              className="w-full h-8 inline-flex items-center justify-center gap-1.5 rounded bg-[#f59e0b] hover:bg-[#f59e0b]/90 text-slate-950 text-xs font-mono font-bold shadow-sm transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              Новий ADR
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
            {filtered.map((adr) => {
              const isSel = adr.id === current?.id;
              const tone =
                adr.status === 'accepted'
                  ? 'emerald'
                  : adr.status === 'superseded'
                    ? 'neutral'
                    : 'cyan';
              return (
                <button
                  key={adr.id}
                  onClick={() => {
                    setSelectedId(adr.id);
                    setMode('read');
                    setDraft(null);
                  }}
                  className={`w-full text-left p-2.5 rounded border text-xs transition-all ${
                    isSel
                      ? 'bg-[#1a2233] border-[#f59e0b]/60 shadow-sm'
                      : 'bg-[#141b27]/60 border-[#1e293b] hover:bg-[#1a2233] hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono font-bold text-[#f59e0b]">{adr.id}</span>
                    <Badge tone={tone as any} outline={adr.status === 'accepted'}>
                      {adr.status}
                    </Badge>
                  </div>
                  <h4 className="font-medium text-slate-200 line-clamp-2 text-[11px]">
                    {adr.title}
                  </h4>
                  <div className="flex items-center justify-between text-[10px] text-slate-500 mt-2 font-mono">
                    <span>{adr.invariants.length} INV</span>
                    <span className="tabular-nums">{adr.date}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </aside>

        {/* ============ RIGHT: Reader OR Editor =========================== */}
        <div className="flex-1 flex flex-col bg-[#090d13] overflow-hidden">
          {!current && mode === 'read' && (
            <div className="flex-1 flex items-center justify-center text-slate-500 font-mono">
              Оберіть ADR або створіть новий
            </div>
          )}

          {current && mode === 'read' && (
            <>
              {/* Reader topbar */}
              <div className="px-5 py-3 bg-[#0d121c] border-b border-[#1e293b] flex items-center justify-between shrink-0">
                <div className="space-y-0.5 min-w-0">
                  <div className="flex items-center gap-2">
                    <Badge tone="amber" outline>
                      {current.id}
                    </Badge>
                    <span className="text-xs font-bold text-slate-100 font-mono truncate">
                      {current.title}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-[10px] text-slate-500 font-mono">
                    {current.file_path && <code>{current.file_path}</code>}
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3 text-[#f59e0b]" />
                      {current.date}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 shrink-0">
                  <button
                    onClick={startEdit}
                    className="inline-flex items-center gap-1.5 h-7 px-2.5 rounded border border-[#1e293b] bg-[#141b27] hover:bg-[#1a2233] text-slate-200 text-xs font-mono transition-colors"
                  >
                    <Pencil className="w-3 h-3" />
                    Редагувати
                  </button>
                  <button
                    onClick={startAmend}
                    className="inline-flex items-center gap-1.5 h-7 px-2.5 rounded border border-[#8b5cf6]/40 bg-[#8b5cf6]/10 hover:bg-[#8b5cf6]/20 text-[#8b5cf6] text-xs font-mono font-bold transition-colors"
                    title="Створити новий ADR що замінює цей (superseded_by)"
                  >
                    <GitBranch className="w-3 h-3" />
                    Amend
                  </button>
                </div>
              </div>

              {/* Invariants bar */}
              {current.invariants?.length > 0 && (
                <div className="px-5 py-2 bg-[#0d121c]/80 border-b border-[#1e293b] flex items-center gap-2 overflow-x-auto text-[11px] font-mono shrink-0">
                  <span className="text-[#f59e0b] font-semibold flex items-center gap-1 shrink-0">
                    <Shield className="w-3.5 h-3.5" />
                    Інваріанти:
                  </span>
                  {current.invariants.map((inv) => (
                    <div
                      key={inv.id}
                      className="px-2 py-0.5 rounded bg-[#141b27] border border-[#1e293b] text-slate-300 flex items-center gap-1.5 shrink-0"
                    >
                      <span className="text-[#f59e0b] font-bold">{inv.id}</span>
                      <button
                        onClick={() => copyInv(inv.id)}
                        className="hover:text-slate-100"
                        title="Копіювати ID"
                      >
                        {copiedInv === inv.id ? (
                          <Check className="w-3 h-3 text-[#10b981]" />
                        ) : (
                          <Copy className="w-3 h-3 text-slate-500" />
                        )}
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* Markdown viewer */}
              <div className="flex-1 overflow-y-auto p-6 font-mono text-[13px] leading-relaxed select-text bg-[#090d13] text-slate-200 whitespace-pre-wrap">
                {current.content || (
                  <div className="p-8 text-center text-slate-500">
                    Повний текст документа не знайдено.
                  </div>
                )}
              </div>
            </>
          )}

          {editing && draft && (
            <EditorForm
              draft={draft}
              setDraft={setDraft}
              onCancel={() => {
                setMode('read');
                setDraft(null);
              }}
              onSaveDraft={() => commit(false)}
              onPublish={() => commit(true)}
            />
          )}
        </div>
      </div>
    </Dialog>
  );
};

// -----------------------------------------------------------------------------

interface EditorFormProps {
  draft: Partial<BitemporalAdr>;
  setDraft: (d: Partial<BitemporalAdr>) => void;
  onCancel: () => void;
  onSaveDraft: () => void;
  onPublish: () => void;
}

const EditorForm: React.FC<EditorFormProps> = ({
  draft,
  setDraft,
  onCancel,
  onSaveDraft,
  onPublish,
}) => {
  const update = (patch: Partial<BitemporalAdr>) => setDraft({ ...draft, ...patch });

  const addInvariant = () => {
    const nextNum = String((draft.invariants?.length || 0) + 1).padStart(2, '0');
    update({
      invariants: [
        ...(draft.invariants || []),
        { id: `INV-NEW-${nextNum}`, statement: '' } as any,
      ],
    });
  };

  const removeInvariant = (id: string) => {
    update({ invariants: (draft.invariants || []).filter((i) => i.id !== id) });
  };

  return (
    <>
      {/* Editor topbar */}
      <div className="px-5 py-3 bg-[#0d121c] border-b border-[#1e293b] flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <Badge tone="cyan" outline>
            {draft.id}
          </Badge>
          <span className="text-xs font-bold text-slate-100 font-mono">
            Editor · MADR 3.0
          </span>
          <span className="text-[10px] text-slate-500 font-mono">
            {draft.status || 'proposed'}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <button
            onClick={onCancel}
            className="inline-flex items-center gap-1.5 h-7 px-2.5 rounded border border-[#1e293b] bg-[#141b27] hover:bg-[#1a2233] text-slate-300 text-xs font-mono transition-colors"
          >
            <Eye className="w-3 h-3" /> Read Mode
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-4 select-text">
        {/* Meta */}
        <div className="grid grid-cols-3 gap-3">
          <div className="col-span-2">
            <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
              Title
            </label>
            <input
              value={draft.title || ''}
              onChange={(e) => update({ title: e.target.value })}
              placeholder="Коротке декларативне рішення…"
              className="w-full h-8 bg-[#090d13] border border-[#1e293b] rounded px-2.5 text-slate-100 text-sm font-sans focus:border-[#f59e0b] focus:outline-none focus:ring-1 focus:ring-[#f59e0b]/30"
            />
          </div>
          <div>
            <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
              Status
            </label>
            <select
              value={draft.status || 'proposed'}
              onChange={(e) => update({ status: e.target.value as any })}
              className="w-full h-8 bg-[#090d13] border border-[#1e293b] rounded px-2 text-slate-100 font-mono text-xs focus:border-[#f59e0b] focus:outline-none"
            >
              <option value="proposed">proposed</option>
              <option value="accepted">accepted</option>
              <option value="deprecated">deprecated</option>
              <option value="superseded">superseded</option>
            </select>
          </div>
        </div>

        {/* MADR body */}
        <div>
          <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
            MADR body (Markdown)
          </label>
          <textarea
            value={draft.content || ''}
            onChange={(e) => update({ content: e.target.value })}
            rows={16}
            className="w-full bg-[#090d13] border border-[#1e293b] rounded p-3 text-slate-200 font-mono text-[12px] leading-relaxed focus:border-[#f59e0b] focus:outline-none resize-y"
          />
          <p className="text-[10px] text-slate-500 font-mono mt-1">
            MADR 3.0 sections: <code className="text-[#f59e0b]">Context</code>{' · '}
            <code className="text-[#f59e0b]">Decision</code>{' · '}
            <code className="text-[#f59e0b]">Consequences</code>{' · '}
            <code className="text-[#f59e0b]">Invariants</code>.
          </p>
        </div>

        {/* Invariants list */}
        <div className="rounded border border-[#1e293b] bg-[#0d121c] p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5 text-[#f59e0b]" />
              Інваріанти ({(draft.invariants || []).length})
            </span>
            <button
              onClick={addInvariant}
              className="inline-flex items-center gap-1 h-6 px-2 rounded border border-[#1e293b] bg-[#141b27] hover:bg-[#1a2233] text-slate-300 text-[11px] font-mono transition-colors"
            >
              <ShieldPlus className="w-3 h-3 text-[#10b981]" />
              + INV
            </button>
          </div>

          <div className="space-y-1.5">
            {(draft.invariants || []).map((inv, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <input
                  value={inv.id}
                  onChange={(e) => {
                    const next = [...(draft.invariants || [])];
                    next[idx] = { ...next[idx], id: e.target.value };
                    update({ invariants: next });
                  }}
                  className="w-32 h-7 bg-[#090d13] border border-[#1e293b] rounded px-2 text-[#f59e0b] font-mono text-[11px] focus:border-[#f59e0b] focus:outline-none"
                />
                <input
                  value={inv.statement}
                  onChange={(e) => {
                    const next = [...(draft.invariants || [])];
                    next[idx] = { ...next[idx], statement: e.target.value };
                    update({ invariants: next });
                  }}
                  placeholder="Формулювання інваріанту…"
                  className="flex-1 h-7 bg-[#090d13] border border-[#1e293b] rounded px-2 text-slate-200 text-[11px] focus:border-[#f59e0b] focus:outline-none"
                />
                <button
                  onClick={() => removeInvariant(inv.id)}
                  className="w-7 h-7 rounded border border-[#1e293b] text-slate-500 hover:text-[#f43f5e] hover:border-[#f43f5e]/40 flex items-center justify-center"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Editor footer */}
      <footer className="flex items-center justify-between px-5 py-3 bg-[#0d121c] border-t border-[#1e293b] shrink-0">
        <button
          onClick={onCancel}
          className="h-8 px-3 rounded border border-[#1e293b] bg-[#141b27] hover:bg-[#1a2233] text-slate-300 text-xs font-mono transition-colors"
        >
          Скасувати
        </button>
        <div className="flex items-center gap-2">
          <button
            onClick={onSaveDraft}
            className="inline-flex items-center gap-1.5 h-8 px-3 rounded border border-[#1e293b] bg-[#141b27] hover:bg-[#1a2233] text-slate-200 text-xs font-mono transition-colors"
          >
            <Save className="w-3.5 h-3.5" />
            Save Draft
          </button>
          <button
            onClick={onPublish}
            className="inline-flex items-center gap-1.5 h-8 px-4 rounded bg-[#10b981] hover:bg-[#10b981]/90 text-slate-950 text-xs font-mono font-bold shadow-sm transition-colors"
          >
            <Check className="w-3.5 h-3.5" />
            Publish (accepted)
          </button>
        </div>
      </footer>
    </>
  );
};

export default AdrLibraryModal;
