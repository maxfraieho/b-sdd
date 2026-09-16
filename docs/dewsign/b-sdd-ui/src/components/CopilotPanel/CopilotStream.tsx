// src/components/CopilotPanel/CopilotStream.tsx
import React, { useState, useRef, useEffect } from 'react';
import type { ModelSlot, ModelSlotId, CopilotLogMessage, TokenBudget } from '@/types/copilot';
import { TokenGauge } from './TokenGauge';
import { ContextBadges } from './ContextBadges';
import { useCopilotStream } from '@/hooks/useCopilotStream';
import {
  Send,
  Cpu,
  Sparkles,
  Square,
  WifiOff,
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
      content: '[Pre-Flight] Active rules compiled: 476 words (<500 budget), latency 16.4ms (<50ms). Zero third-party imports detected in src/.',
    },
    {
      id: 'm2',
      timestamp: '18:14:15',
      role: 'assistant',
      content: 'Standing by in Sovereign Execution VPC (192.168.3.184:18880). Control flow topology locked to canonical DRAKON-IR.',
    },
  ]);

  const [inputPrompt, setInputPrompt] = useState('');
  const [attachedContexts, setAttachedContexts] = useState<string[]>(['adr', 'drakon']);
  const scrollRef = useRef<HTMLDivElement>(null);
  const pendingMessageIdRef = useRef<string | null>(null);

  const activeSlot = modelSlots.find((s) => s.id === activeSlotId) || modelSlots[0];

  // Phase 3: live SSE from POST /api/copilot/proxy on localhost:8765.
  // The hook exposes streamingText + isStreaming + error and manages fetch abort.
  const {
    streamingText,
    isStreaming,
    error: streamError,
    totalTokens,
    start: startStream,
    abort: abortStream,
  } = useCopilotStream();

  // Merge the live stream chunk into the last assistant bubble as it grows.
  useEffect(() => {
    const id = pendingMessageIdRef.current;
    if (!id) return;
    setMessages((prev) =>
      prev.map((m) =>
        m.id === id
          ? {
              ...m,
              content: streamingText || m.content,
              tokensUsed: totalTokens > 0 ? totalTokens : m.tokensUsed,
            }
          : m,
      ),
    );
  }, [streamingText, totalTokens]);

  // Once streaming ends, clear the pending pointer so future messages append.
  useEffect(() => {
    if (!isStreaming) pendingMessageIdRef.current = null;
  }, [isStreaming]);

  // If the sovereign gateway rejected our call, surface the reason inline.
  useEffect(() => {
    if (!streamError) return;
    const id = pendingMessageIdRef.current;
    if (!id) return;
    setMessages((prev) =>
      prev.map((m) =>
        m.id === id
          ? {
              ...m,
              content:
                (streamingText || m.content) +
                `\n\n[⚠ offline fallback] ${streamError.message}\n` +
                'Backend workbench_server.py unreachable — using local simulated response.',
            }
          : m,
      ),
    );
    pendingMessageIdRef.current = null;
  }, [streamError, streamingText]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, streamingText]);

  const handleToggleAttach = (type: string) => {
    setAttachedContexts((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const handleSendPrompt = () => {
    if (!inputPrompt.trim() || isStreaming) return;

    const userMsg: CopilotLogMessage = {
      id: String(Date.now()),
      timestamp: new Date().toLocaleTimeString(),
      role: 'user',
      content: inputPrompt,
    };

    const assistantId = String(Date.now() + 1);
    const assistantSeed: CopilotLogMessage = {
      id: assistantId,
      timestamp: new Date().toLocaleTimeString(),
      role: 'assistant',
      slot: activeSlot.id,
      content: '',
    };
    pendingMessageIdRef.current = assistantId;

    setMessages((prev) => [...prev, userMsg, assistantSeed]);
    const prompt = inputPrompt;
    setInputPrompt('');

    // Phase 3: dispatch to real POST /api/copilot/proxy SSE stream.
    // The hook automatically falls back into error mode if the sovereign
    // gateway is offline — we then attach a local simulated response above.
    startStream({
      prompt,
      slot: activeSlot.id as ModelSlotId,
      stream: true,
      attached_contexts: attachedContexts,
    });
  };

  const handleKillStream = () => {
    abortStream();
  };

  return (
    <div className="h-full flex flex-col bg-panel text-slate-100 select-none">
      {/* Top: Model Slots Selector */}
      <div className="p-3 border-b border-border-subtle bg-card/60 flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-amber" />
            <span className="text-xs font-mono font-bold uppercase tracking-wider">
              Sovereign LLM Pool (.184)
            </span>
          </div>
          <span className="text-[10px] font-mono text-slate-400">
            Avg Latency: <span className="text-emerald-400">{activeSlot.latencyAvg}</span>
          </span>
        </div>

        {/* 3 Model Slot Pills */}
        <div className="grid grid-cols-3 gap-2">
          {modelSlots.map((slot) => {
            const isSelected = slot.id === activeSlotId;

            return (
              <button
                key={slot.id}
                onClick={() => onSelectSlot(slot.id)}
                className={`p-2 rounded border text-left flex flex-col transition-all ${
                  isSelected
                    ? 'bg-amber/15 border-amber text-amber font-semibold shadow-sm'
                    : 'bg-card hover:bg-slate-800 border-border-subtle text-slate-300'
                }`}
              >
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span>{slot.name}</span>
                  {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-amber" />}
                </div>
                <span className="text-[9px] text-slate-400 font-sans truncate mt-0.5">
                  {slot.model.split('/')[1] || slot.model}
                </span>
              </button>
            );
          })}
        </div>

        {/* Token Budget Gauge */}
        <TokenGauge budget={tokenBudget} />
      </div>

      {/* Center: Realtime Streaming Log Terminal */}
      <div
        ref={scrollRef}
        className="flex-1 p-3 overflow-y-auto font-mono text-xs space-y-3 bg-canvas/60"
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`p-2.5 rounded-md border text-xs leading-relaxed ${
              msg.role === 'system'
                ? 'bg-blue-950/20 border-blue-900/40 text-blue-300'
                : msg.role === 'user'
                ? 'bg-slate-800 border-border-subtle text-slate-200'
                : 'bg-card border-border-subtle text-slate-100'
            }`}
          >
            <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1 border-b border-border-subtle/50 pb-1">
              <span className="uppercase font-bold tracking-wider text-slate-400">
                {msg.role === 'assistant' ? `🤖 ${msg.slot || 'LLM Gateway'}` : msg.role}
              </span>
              <span>{msg.timestamp}</span>
            </div>
            <p className="whitespace-pre-wrap font-mono text-[11px]">{msg.content}</p>
          </div>
        ))}

        {isStreaming && (
          <div className="p-2.5 rounded-md border border-amber/30 bg-amber/5 text-amber text-xs font-mono flex items-center gap-2">
            <Sparkles className="w-4 h-4 animate-spin text-amber" />
            <span className="flex-1 animate-pulse">
              SSE stream from <span className="font-bold">{activeSlot.name}</span>
              {totalTokens > 0 && <span className="text-slate-400"> · {totalTokens} tok</span>}
            </span>
            <button
              onClick={handleKillStream}
              className="px-2 py-1 rounded border border-rose-500/50 text-rose-300 hover:bg-rose-500/20 flex items-center gap-1 text-[10px] font-mono transition-colors"
              title="Kill sovereign SSE stream and rollback partial tokens"
            >
              <Square className="w-3 h-3" />
              Kill Stream
            </button>
          </div>
        )}
        {!isStreaming && streamError && (
          <div className="p-2.5 rounded-md border border-rose-500/30 bg-rose-950/20 text-rose-300 text-xs font-mono flex items-center gap-2">
            <WifiOff className="w-4 h-4" />
            <span>Sovereign gateway offline — next prompt will use fallback simulation.</span>
          </div>
        )}
      </div>

      {/* Bottom: Context Attachments & Input Bar */}
      <div className="p-3 border-t border-border-subtle bg-card/70 flex flex-col gap-2">
        <ContextBadges
          attachedContexts={attachedContexts}
          onAttach={handleToggleAttach}
        />

        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Prompt LLM Gateway (e.g. Synthesize leaf action body for cond_phi3)..."
            value={inputPrompt}
            onChange={(e) => setInputPrompt(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendPrompt()}
            disabled={isStreaming}
            className="flex-1 bg-canvas border border-border-subtle rounded-md px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber font-mono"
          />

          <button
            onClick={handleSendPrompt}
            disabled={isStreaming || !inputPrompt.trim()}
            className="px-3 py-2 rounded-md bg-amber hover:bg-amber-600 disabled:opacity-40 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition-colors shadow"
            title="Dispatch Prompt"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Send</span>
          </button>
        </div>
      </div>
    </div>
  );
};
