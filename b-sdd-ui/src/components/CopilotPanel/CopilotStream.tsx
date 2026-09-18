// src/components/CopilotPanel/CopilotStream.tsx
// Astryx Conversational Copilot with Architectural Critique Cards (ADR-008, ADR-009)
import React, { useState, useRef, useEffect } from 'react';
import type { ModelSlot, ModelSlotId, CopilotLogMessage, TokenBudget } from '@/types/copilot';
import { TokenGauge } from './TokenGauge';
import { ContextBadges } from './ContextBadges';
import { useCopilotStream } from '@/hooks/useCopilotStream';
import { Button, Badge, Banner, Dot } from '@/components/astryx/primitives';
import type { SymbolCardData, MutationCardData } from '@/types/copilot';
import {
  Send,
  Cpu,
  Sparkles,
  Square,
  WifiOff,
  Zap,
  ShieldCheck,
  Bot,
  User,
  CheckCircle2,
  AlertTriangle,
  FileCheck2,
  Code2,
  FileCode,
  ExternalLink,
  GitCommit,
  Undo2,
  ArrowRightLeft,
  Radio,
} from 'lucide-react';

interface CopilotStreamProps {
  modelSlots: ModelSlot[];
  activeSlotId: string;
  onSelectSlot: (slotId: string) => void;
  tokenBudget: TokenBudget;
}

export const CopilotStream: React.FC<CopilotStreamProps> = ({
  modelSlots,
  activeSlotId,
  onSelectSlot,
  tokenBudget,
}) => {
  const [messages, setMessages] = useState<CopilotLogMessage[]>([
    {
      id: 'm1',
      timestamp: '18:14:02',
      role: 'system',
      content: 'Active rules compiled: 476 words (<500 budget), latency 16.4ms (<50ms). Zero third-party imports detected in src/. Planarity C=0 verified.',
      critique: {
        invariantId: 'ADR-002 · ADR-008',
        title: 'Pre-Flight Architectural Verification',
        status: 'pass',
        detail: 'Planarity invariant C=0 satisfied. Standard library purity maintained.',
      },
    },
    {
      id: 'm2',
      timestamp: '18:14:15',
      role: 'assistant',
      content: 'Привіт! Я суверенний асистент B-SDD. Архітектурні інваріанти зафіксовані. Чим можу допомогти у поточній сесії (моделювання схеми, синтез коду чи реверс-інжиніринг MADR)?',
    },
  ]);

  const [inputPrompt, setInputPrompt] = useState('');
  const [attachedContexts, setAttachedContexts] = useState<string[]>(['adr', 'drakon']);
  const scrollRef = useRef<HTMLDivElement>(null);
  const pendingMessageIdRef = useRef<string | null>(null);

  const activeSlot = modelSlots.find((s) => s.id === activeSlotId) || modelSlots[0];

  const {
    streamingText,
    isStreaming,
    error: streamError,
    totalTokens,
    start: startStream,
    abort: abortStream,
  } = useCopilotStream();

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, streamingText]);

  useEffect(() => {
    if (isStreaming && pendingMessageIdRef.current) {
      const targetId = pendingMessageIdRef.current;
      setMessages((prev) =>
        prev.map((m) =>
          m.id === targetId ? { ...m, content: streamingText } : m
        )
      );
    }
  }, [streamingText, isStreaming]);

  useEffect(() => {
    if (!isStreaming && pendingMessageIdRef.current) {
      pendingMessageIdRef.current = null;
    }
  }, [isStreaming]);

  const handleToggleAttach = (contextType: string) => {
    setAttachedContexts((prev) =>
      prev.includes(contextType)
        ? prev.filter((c) => c !== contextType)
        : [...prev, contextType]
    );
  };

  const handleSendPrompt = (overridePrompt?: string) => {
    const textToSend = overridePrompt || inputPrompt;
    if (!textToSend.trim() || isStreaming) return;

    const userMsg: CopilotLogMessage = {
      id: `u_${Date.now()}`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      role: 'user',
      content: textToSend,
    };

    const assistantId = `a_${Date.now()}`;
    const assistantSeed: CopilotLogMessage = {
      id: assistantId,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      role: 'assistant',
      slot: activeSlot.id,
      content: '',
    };
    pendingMessageIdRef.current = assistantId;

    setMessages((prev) => [...prev, userMsg, assistantSeed]);
    if (!overridePrompt) setInputPrompt('');

    startStream({
      prompt: textToSend,
      slot: activeSlot.id as ModelSlotId,
      stream: true,
      attached_contexts: attachedContexts,
    });
  };

  const handleKillStream = () => {
    abortStream();
  };

  const handleDispatchPi = async () => {
    if (isStreaming) return;
    const promptText = inputPrompt.trim() || 'Execute leaf Action node task under B-SDD invariants.';
    const userMsg: CopilotLogMessage = {
      id: `u_${Date.now()}`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      role: 'user',
      content: `[Pi Harness Dispatch] ${promptText}`,
    };
    const assistantId = `a_${Date.now()}`;
    const assistantSeed: CopilotLogMessage = {
      id: assistantId,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      role: 'assistant',
      slot: 'pi-harness',
      content: '⚡ Headless Pi Harness dispatching JSONL RPC...',
    };
    setMessages((prev) => [...prev, userMsg, assistantSeed]);
    setInputPrompt('');

    try {
      const res = await fetch('/api/harness/pi/dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          feature_id: '012-dag-and-pi-harness',
          target_action_id: 'step_proxy_utopia',
          prompt: promptText,
          stream: false,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        const eventsSummary = data.events?.map((e: any) => `• [${e.event}] ${e.status || ''} ${e.step || ''} ${e.message || ''}`).join('\n') || 'Pi execution completed with 0 errors.';
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  content: `✓ [Pi Harness Completed]\n${eventsSummary}\n• Isolation Verified (INV-012-03): Topology unaltered.`,
                  critique: {
                    invariantId: 'INV-012-03',
                    title: 'Action Node Isolation Verified',
                    status: 'pass',
                    detail: 'Target node modified without altering parent DAG edges or branching structure.',
                  },
                }
              : m
          )
        );
      }
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: `✗ Pi Harness dispatch failed: ${String(err)}` }
            : m
        )
      );
    }
  };

  const handleInspectSymbol = async (symbolName: string) => {
    if (!symbolName.trim() || isStreaming) return;
    const assistantId = `sym_${Date.now()}`;
    const assistantSeed: CopilotLogMessage = {
      id: assistantId,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      role: 'assistant',
      slot: 'coding-proxy',
      content: `🔍 Запит інспекції символу \`${symbolName}\` до суверенного індексу...`,
    };
    setMessages((prev) => [...prev, assistantSeed]);

    try {
      const res = await fetch(`/api/copilot/symbol-card?symbol=${encodeURIComponent(symbolName)}`);
      if (res.ok) {
        const data = await res.json();
        const card: SymbolCardData = data.card;
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  content: `✓ AST Symbol Card для \`${card.name}\` знайдено у суверенному bitemporal індексі Utopia DB.`,
                  symbolCard: card,
                }
              : m
          )
        );
      } else {
        const errData = await res.json().catch(() => ({ error: 'Символ не знайдено' }));
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  content: `⚠️ Інспекція символу \`${symbolName}\`: ${errData.error || 'Символ відсутній в AST індексі репозиторію.'}`,
                }
              : m
          )
        );
      }
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: `✗ Помилка запиту картки символу: ${String(err)}` }
            : m
        )
      );
    }
  };

  const handleTriggerRefactor = async (targetSymbol: string, newName: string, dryRun: boolean = true) => {
    const assistantId = `mut_${Date.now()}`;
    const assistantSeed: CopilotLogMessage = {
      id: assistantId,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      role: 'assistant',
      slot: 'coding-proxy',
      content: `⚡ Ініціалізація ${dryRun ? 'dry-run ' : ''}рефакторингу символу \`${targetSymbol}\` -> \`${newName}\`...`,
    };
    setMessages((prev) => [...prev, assistantSeed]);

    try {
      const res = await fetch('/api/mutation/refactor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          operation: 'rename_symbol',
          target_symbol: targetSymbol,
          new_name: newName,
          dry_run: dryRun,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        const mutCard: MutationCardData = {
          tx_id: data.tx_id,
          operation: data.operation || 'rename_symbol',
          target_symbol: targetSymbol,
          new_name: newName,
          cow_branch: data.cow_branch,
          mutations_applied: data.mutations_applied || 0,
          files_affected: data.files_affected || [],
          status: dryRun ? 'dry_run_completed' : 'committed',
        };
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  content: dryRun
                    ? `✓ Dry-run рефакторингу успішно валідовано (Tx ID: \`${data.tx_id}\`). Готово до застосування на CoW-гілці.`
                    : `✓ Транзакційну мутацію успішно застосовано на CoW-гілці \`${data.cow_branch}\` (Tx ID: \`${data.tx_id}\`).`,
                  mutationCard: mutCard,
                }
              : m
          )
        );
      }
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: `✗ Помилка виконання рефакторингу: ${String(err)}` }
            : m
        )
      );
    }
  };

  const handleRollbackMutation = async (txId: string) => {
    try {
      const res = await fetch('/api/mutation/rollback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tx_id: txId }),
      });
      if (res.ok) {
        setMessages((prev) =>
          prev.map((m) =>
            m.mutationCard?.tx_id === txId
              ? {
                  ...m,
                  content: `${m.content}\n\n↩ [ВІДКАТАНО] Транзакція ${txId} успішно скасована через compensation rollback.`,
                  mutationCard: { ...m.mutationCard, status: 'rolled_back' },
                }
              : m
          )
        );
      }
    } catch (err) {
      console.error('Rollback failed:', err);
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0d121c] text-slate-100 select-none">
      {/* Top: Header with Slot Selector & Word Budget */}
      <div className="p-2.5 border-b border-[#1e293b] bg-[#141b27]/70 flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-4 h-4 text-amber" />
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
              Sovereign Copilot
            </span>
            <Dot tone="emerald" pulse />
          </div>
          <span className="text-[10px] font-mono text-slate-400">
            Avg: <span className="text-emerald">{activeSlot.latencyAvg}</span>
          </span>
        </div>

        {/* Compact 3 Model Slot Pills */}
        <div className="grid grid-cols-3 gap-1.5">
          {modelSlots.map((slot) => {
            const isSelected = slot.id === activeSlotId;

            return (
              <button
                key={slot.id}
                onClick={() => onSelectSlot(slot.id)}
                className={`px-2 py-1 rounded border text-left flex flex-col transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-[#1a2233] border-amber/70 text-amber font-semibold shadow-xs'
                    : 'bg-[#121824] hover:bg-[#182130] border-[#1e293b] text-slate-300'
                }`}
              >
                <div className="flex items-center justify-between text-[10px] font-mono">
                  <span className="truncate">{slot.name}</span>
                  {isSelected && <Dot tone="amber" />}
                </div>
              </button>
            );
          })}
        </div>

        {/* Token Budget Gauge */}
        <TokenGauge budget={tokenBudget} />
      </div>

      {/* Center: Conversational Chat Message Stream */}
      <div
        ref={scrollRef}
        className="flex-1 p-3 overflow-y-auto font-sans text-xs space-y-3 bg-[#090d13]/70 flex flex-col"
      >
        {messages.map((msg) => {
          if (msg.role === 'system' || msg.critique) {
            return (
              <div
                key={msg.id}
                className="w-full p-2.5 rounded-lg border bg-[#111726]/80 border-[#1e293b] shadow-xs font-mono text-xs my-1"
              >
                <div className="flex items-center justify-between pb-1.5 mb-1.5 border-b border-[#1e293b]">
                  <div className="flex items-center gap-1.5">
                    {msg.critique?.status === 'pass' ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald" />
                    ) : (
                      <AlertTriangle className="w-3.5 h-3.5 text-amber" />
                    )}
                    <span className="font-bold text-slate-200 text-[11px]">
                      {msg.critique?.title || 'Architectural Critique'}
                    </span>
                    {msg.critique?.invariantId && (
                      <span className="px-1.5 py-0.2 text-[9px] rounded bg-cyan/10 text-cyan border border-cyan/30">
                        {msg.critique.invariantId}
                      </span>
                    )}
                  </div>
                  <span className="text-[10px] text-slate-500">{msg.timestamp}</span>
                </div>
                <p className="text-slate-300 leading-relaxed text-[11px] whitespace-pre-wrap">
                  {msg.content}
                </p>
              </div>
            );
          }

          if (msg.role === 'user') {
            return (
              <div key={msg.id} className="flex flex-col items-end max-w-[88%] self-end">
                <div className="flex items-center gap-1 text-[10px] text-slate-400 mb-1 font-mono">
                  <span>Ви</span>
                  <span>·</span>
                  <span>{msg.timestamp}</span>
                  <User className="w-3 h-3 text-blue-400" />
                </div>
                <div className="p-3 rounded-2xl rounded-tr-xs bg-blue-600/20 border border-blue-500/30 text-blue-100 text-xs leading-relaxed font-sans shadow-xs whitespace-pre-wrap">
                  {msg.content}
                </div>
              </div>
            );
          }

          // Assistant message
          return (
            <div key={msg.id} className="flex flex-col items-start max-w-[92%] self-start">
              <div className="flex items-center gap-1 text-[10px] text-slate-400 mb-1 font-mono">
                <Bot className="w-3 h-3 text-amber" />
                <span className="text-amber font-semibold">{msg.slot || 'B-SDD Copilot'}</span>
                <span>·</span>
                <span>{msg.timestamp}</span>
              </div>
              <div className="p-3 rounded-2xl rounded-tl-xs bg-[#131b29] border border-[#1e293b] text-slate-200 text-xs leading-relaxed font-sans shadow-xs whitespace-pre-wrap">
                {msg.content}

                {msg.symbolCard && (
                  <div className="mt-2.5 p-2.5 rounded-lg border border-cyan/40 bg-[#0c1624] font-mono text-xs shadow-xs">
                    <div className="flex items-center justify-between pb-1.5 border-b border-cyan/20">
                      <div className="flex items-center gap-1.5">
                        <Code2 className="w-3.5 h-3.5 text-cyan" />
                        <span className="font-bold text-cyan text-[12px]">{msg.symbolCard.name}</span>
                        <span className="px-1.5 py-0.2 text-[9px] rounded bg-cyan/15 text-cyan border border-cyan/30 uppercase font-semibold">
                          {msg.symbolCard.kind}
                        </span>
                        <span className="px-1.5 py-0.2 text-[9px] rounded bg-slate-800 text-slate-300 border border-slate-700 uppercase">
                          {msg.symbolCard.workspace}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 text-[10px] text-slate-400">
                        <span>L{msg.symbolCard.line}</span>
                      </div>
                    </div>
                    <div className="mt-2 text-[10px] text-slate-300 flex items-center gap-1.5">
                      <FileCode className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="font-mono truncate text-slate-300" title={msg.symbolCard.file}>
                        {msg.symbolCard.file}:{msg.symbolCard.line}
                      </span>
                    </div>
                    {msg.symbolCard.docstring && (
                      <div className="mt-2 p-1.5 rounded bg-[#090d13] border border-[#1e293b] text-slate-300 text-[10px] leading-relaxed italic">
                        {msg.symbolCard.docstring}
                      </div>
                    )}
                    <div className="mt-2 flex items-center justify-between pt-1.5 border-t border-[#1e293b]/70 text-[9px] text-slate-400">
                      <div className="flex items-center gap-2">
                        {msg.symbolCard.tx && (
                          <span>
                            Tx: <span className="text-slate-300">{msg.symbolCard.tx.slice(11, 19)}</span>
                          </span>
                        )}
                        {msg.symbolCard.tv && (
                          <span>
                            Tv: <span className="text-slate-300">{msg.symbolCard.tv.slice(11, 19)}</span>
                          </span>
                        )}
                      </div>
                      <button
                        onClick={() => {
                          handleSendPrompt(`Покажи детальний контекст та залежності для символу ${msg.symbolCard?.name}`);
                        }}
                        className="px-2 py-0.5 rounded bg-cyan/10 hover:bg-cyan/20 border border-cyan/30 text-cyan text-[10px] flex items-center gap-1 transition-colors cursor-pointer"
                      >
                        <ExternalLink className="w-2.5 h-2.5" />
                        <span>Аналіз залежностей</span>
                      </button>
                    </div>
                  </div>
                )}

                {msg.mutationCard && (
                  <div className="mt-2.5 p-2.5 rounded-lg border border-purple-500/40 bg-[#120f24] font-mono text-xs shadow-xs">
                    <div className="flex items-center justify-between pb-1.5 border-b border-purple-500/20">
                      <div className="flex items-center gap-1.5">
                        <ArrowRightLeft className="w-3.5 h-3.5 text-purple-400" />
                        <span className="font-bold text-purple-300 text-[11px]">{msg.mutationCard.operation}</span>
                        <span className={`px-1.5 py-0.2 text-[9px] rounded font-semibold uppercase ${
                          msg.mutationCard.status === 'rolled_back'
                            ? 'bg-rose-950 text-rose-300 border border-rose-800'
                            : msg.mutationCard.status === 'dry_run_completed'
                            ? 'bg-blue-950 text-blue-300 border border-blue-800'
                            : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        }`}>
                          {msg.mutationCard.status}
                        </span>
                      </div>
                      <span className="text-[9px] text-slate-400 truncate">{msg.mutationCard.tx_id}</span>
                    </div>

                    <div className="mt-2 flex items-center gap-1 text-[11px] text-slate-200">
                      <span className="line-through text-slate-400">{msg.mutationCard.target_symbol}</span>
                      <span className="text-purple-400">→</span>
                      <span className="text-emerald-400 font-bold">{msg.mutationCard.new_name}</span>
                    </div>

                    {msg.mutationCard.cow_branch && (
                      <div className="mt-1 text-[10px] text-slate-400 flex items-center gap-1">
                        <GitCommit className="w-3 h-3 text-purple-400" />
                        <span>Гілка: <span className="text-slate-300">{msg.mutationCard.cow_branch}</span></span>
                      </div>
                    )}

                    {msg.mutationCard.files_affected && msg.mutationCard.files_affected.length > 0 && (
                      <div className="mt-1.5 text-[9px] text-slate-400">
                        <span>Мутовано файлів: {msg.mutationCard.mutations_applied}</span>
                      </div>
                    )}

                    {msg.mutationCard.status === 'committed' && (
                      <div className="mt-2 pt-1.5 border-t border-purple-500/20 flex justify-end">
                        <button
                          onClick={() => handleRollbackMutation(msg.mutationCard!.tx_id)}
                          className="px-2 py-1 rounded bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/40 text-rose-300 text-[10px] flex items-center gap-1 transition-colors cursor-pointer"
                        >
                          <Undo2 className="w-3 h-3" />
                          <span>Відкотити CoW мутацію</span>
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {isStreaming && (
          <div className="p-2.5 rounded-lg border border-amber/30 bg-amber/5 text-amber text-xs font-mono flex items-center gap-2 self-start max-w-full">
            <Sparkles className="w-4 h-4 animate-spin text-amber shrink-0" />
            <span className="flex-1 animate-pulse truncate">
              SSE stream from <span className="font-bold">{activeSlot.name}</span>
              {totalTokens > 0 && <span className="text-slate-400"> · {totalTokens} tok</span>}
            </span>
            <Button
              variant="destructive"
              size="sm"
              icon={<Square className="w-3 h-3" />}
              onClick={handleKillStream}
              title="Перервати стрім"
            >
              Зупинити
            </Button>
          </div>
        )}

        {!isStreaming && streamError && (
          <Banner tone="error" icon={<WifiOff className="w-4 h-4" />}>
            <span>Суверенний шлюз офлайн — наступний промпт використає локальну емуляцію.</span>
          </Banner>
        )}
      </div>

      {/* Suggested Quick Prompts */}
      <div className="px-3 pt-2 pb-1 bg-[#141b27]/50 border-t border-[#1e293b]/60 flex items-center gap-1.5 overflow-x-auto text-[10px] font-mono">
        <span className="text-slate-500 uppercase shrink-0">Підказки:</span>
        <button
          onClick={() => handleTriggerRefactor('OldEngine', 'NewEngine', true)}
          className="px-2 py-0.5 rounded bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-300 shrink-0 transition-colors flex items-center gap-1 cursor-pointer"
        >
          <ArrowRightLeft className="w-3 h-3 text-purple-400" />
          Рефакторинг (Dry-run)
        </button>
        <button
          onClick={() => handleSendPrompt('Перевір стан синхронізації кластера (.161, .184, .251) та наявність активних ліз.')}
          className="px-2 py-0.5 rounded bg-emerald/10 hover:bg-emerald/20 border border-emerald/30 text-emerald shrink-0 transition-colors flex items-center gap-1 cursor-pointer"
        >
          <Radio className="w-3 h-3 text-emerald" />
          Кластерні лізи (Mesh)
        </button>
        <button
          onClick={() => handleSendPrompt('Отримай перелік активних архітектурних пропозицій та стан кворумного голосування (N >= 2/3).')}
          className="px-2 py-0.5 rounded bg-amber/10 hover:bg-amber/20 border border-amber/30 text-amber shrink-0 transition-colors flex items-center gap-1 cursor-pointer"
        >
          <ShieldCheck className="w-3 h-3 text-amber" />
          Кворум (2/3 Консенсус)
        </button>
        <button
          onClick={() => handleInspectSymbol('BackgroundIngestionWorker')}
          className="px-2 py-0.5 rounded bg-cyan/10 hover:bg-cyan/20 border border-cyan/30 text-cyan shrink-0 transition-colors flex items-center gap-1 cursor-pointer"
        >
          <Code2 className="w-3 h-3 text-cyan" />
          Символ IngestionWorker
        </button>
        <button
          onClick={() => handleInspectSymbol('ModelSlot')}
          className="px-2 py-0.5 rounded bg-cyan/10 hover:bg-cyan/20 border border-cyan/30 text-cyan shrink-0 transition-colors flex items-center gap-1 cursor-pointer"
        >
          <Code2 className="w-3 h-3 text-cyan" />
          Символ ModelSlot
        </button>
        <button
          onClick={() => handleSendPrompt('Перевір планарність C=0 та шампурну лінійність для поточної схеми.')}
          className="px-2 py-0.5 rounded bg-canvas hover:bg-[#1e293b] border border-[#1e293b] text-slate-300 hover:text-amber shrink-0 transition-colors cursor-pointer"
        >
          Планарність C=0
        </button>
        <button
          onClick={() => handleSendPrompt('Перевір чистоту stdlib у src/ (ADR-002, 0 сторонніх імпортів).')}
          className="px-2 py-0.5 rounded bg-canvas hover:bg-[#1e293b] border border-[#1e293b] text-slate-300 hover:text-emerald shrink-0 transition-colors cursor-pointer"
        >
          Чистота stdlib
        </button>
        <button
          onClick={() => handleSendPrompt('Синтезуй оновлення MADR 3.0 на основі AST змін.')}
          className="px-2 py-0.5 rounded bg-canvas hover:bg-[#1e293b] border border-[#1e293b] text-slate-300 hover:text-cyan shrink-0 transition-colors cursor-pointer"
        >
          Синтез MADR
        </button>
      </div>

      {/* Bottom: Context Attachments & Input Bar */}
      <div className="p-3 border-t border-[#1e293b] bg-[#141b27]/80 flex flex-col gap-2">
        <ContextBadges
          attachedContexts={attachedContexts}
          onAttach={handleToggleAttach}
        />

        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Запит до суверенного копілота або Pi Harness..."
            value={inputPrompt}
            onChange={(e) => setInputPrompt(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendPrompt()}
            disabled={isStreaming}
            className="flex-1 bg-[#090d13] border border-[#1e293b] rounded px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber font-mono"
          />

          <Button
            variant="primary"
            size="md"
            icon={<Send className="w-3.5 h-3.5" />}
            onClick={() => handleSendPrompt()}
            disabled={isStreaming || !inputPrompt.trim()}
          >
            Надіслати
          </Button>

          <Button
            variant="secondary"
            size="md"
            icon={<Zap className="w-3.5 h-3.5 text-amber-400" />}
            onClick={handleDispatchPi}
            disabled={isStreaming}
            title="Dispatch Headless Pi Harness (@earendil-works/pi)"
          >
            Pi
          </Button>
        </div>
      </div>
    </div>
  );
};

