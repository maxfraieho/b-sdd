// src/components/CopilotPanel/CopilotStream.tsx
// Astryx-native LLM Copilot Streaming Terminal (ADR-008, ADR-009)
import React, { useState, useRef, useEffect } from 'react';
import type { ModelSlot, ModelSlotId, CopilotLogMessage, TokenBudget } from '@/types/copilot';
import { TokenGauge } from './TokenGauge';
import { ContextBadges } from './ContextBadges';
import { useCopilotStream } from '@/hooks/useCopilotStream';
import { Button, Badge, Banner, Dot } from '@/components/astryx/primitives';
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

  const handleSendPrompt = () => {
    if (!inputPrompt.trim() || isStreaming) return;

    const userMsg: CopilotLogMessage = {
      id: `u_${Date.now()}`,
      timestamp: new Date().toLocaleTimeString(),
      role: 'user',
      content: inputPrompt,
    };

    const assistantId = `a_${Date.now()}`;
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
    <div className="h-full flex flex-col bg-[#0d121c] text-slate-100 select-none">
      {/* Top: Model Slots Selector */}
      <div className="p-3 border-b border-[#1e293b] bg-[#141b27]/60 flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-amber" />
            <span className="text-xs font-mono font-bold uppercase tracking-wider">
              Sovereign LLM Pool (.184)
            </span>
          </div>
          <span className="text-[10px] font-mono text-slate-400">
            Avg Latency: <span className="text-emerald">{activeSlot.latencyAvg}</span>
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
                className={`p-2 rounded border text-left flex flex-col transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-[#1a2233] border-amber text-amber font-semibold shadow-xs'
                    : 'bg-[#141b27] hover:bg-[#1a2233] border-[#1e293b] text-slate-300'
                }`}
              >
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span>{slot.name}</span>
                  {isSelected && <Dot tone="amber" />}
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
        className="flex-1 p-3 overflow-y-auto font-mono text-xs space-y-3 bg-[#090d13]/60"
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`p-2.5 rounded border text-xs leading-relaxed ${
              msg.role === 'system'
                ? 'bg-cyan/10 border-cyan/30 text-cyan-200'
                : msg.role === 'user'
                ? 'bg-[#1a2233] border-[#1e293b] text-slate-200'
                : 'bg-[#141b27] border-[#1e293b] text-slate-100'
            }`}
          >
            <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1 border-b border-[#1e293b]/50 pb-1">
              <span className="uppercase font-bold tracking-wider text-slate-400">
                {msg.role === 'assistant' ? `🤖 ${msg.slot || 'LLM Gateway'}` : msg.role}
              </span>
              <span>{msg.timestamp}</span>
            </div>
            <p className="whitespace-pre-wrap font-mono text-[11px]">{msg.content}</p>
          </div>
        ))}

        {isStreaming && (
          <div className="p-2.5 rounded border border-amber/30 bg-amber/5 text-amber text-xs font-mono flex items-center gap-2">
            <Sparkles className="w-4 h-4 animate-spin text-amber" />
            <span className="flex-1 animate-pulse">
              SSE stream from <span className="font-bold">{activeSlot.name}</span>
              {totalTokens > 0 && <span className="text-slate-400"> · {totalTokens} tok</span>}
            </span>
            <Button
              variant="destructive"
              size="sm"
              icon={<Square className="w-3 h-3" />}
              onClick={handleKillStream}
              title="Kill sovereign SSE stream and rollback partial tokens"
            >
              Kill Stream
            </Button>
          </div>
        )}

        {!isStreaming && streamError && (
          <Banner tone="error" icon={<WifiOff className="w-4 h-4" />}>
            <span>Sovereign gateway offline — next prompt will use fallback simulation.</span>
          </Banner>
        )}
      </div>

      {/* Bottom: Context Attachments & Input Bar */}
      <div className="p-3 border-t border-[#1e293b] bg-[#141b27]/70 flex flex-col gap-2">
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
            className="flex-1 bg-[#090d13] border border-[#1e293b] rounded px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber font-mono"
          />

          <Button
            variant="primary"
            size="md"
            icon={<Send className="w-3.5 h-3.5" />}
            onClick={handleSendPrompt}
            disabled={isStreaming || !inputPrompt.trim()}
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  );
};
