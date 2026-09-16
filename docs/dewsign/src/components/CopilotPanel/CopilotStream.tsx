// src/components/CopilotPanel/CopilotStream.tsx
import React, { useState, useRef, useEffect } from 'react';
import type { ModelSlot, CopilotLogMessage, TokenBudget } from '@/types/copilot';
import { TokenGauge } from './TokenGauge';
import { ContextBadges } from './ContextBadges';
import {
  Send,
  Cpu,
  Terminal,
  Play,
  RotateCw,
  Sparkles,
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
  const [isStreaming, setIsStreaming] = useState(false);
  const [attachedContexts, setAttachedContexts] = useState<string[]>(['adr', 'drakon']);
  const scrollRef = useRef<HTMLDivElement>(null);

  const activeSlot = modelSlots.find((s) => s.id === activeSlotId) || modelSlots[0];

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

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

    setMessages((prev) => [...prev, userMsg]);
    setInputPrompt('');
    setIsStreaming(true);

    // Simulate sovereign SSE token streaming
    setTimeout(() => {
      const responseMsg: CopilotLogMessage = {
        id: String(Date.now() + 1),
        timestamp: new Date().toLocaleTimeString(),
        role: 'assistant',
        slot: activeSlot.id,
        content: `[${activeSlot.name}] Validating invariants for: "${userMsg.content}"\n\n` +
          `• Bitemporal isolation: active ADR-008 verified.\n` +
          `• Leaf action body mapped to Utopia DB entity ent_madr_root.\n` +
          `• Pytest architecture fitness suite executed: 25/25 passed. Ready for Human Review Gate (Φ6).`,
      };
      setMessages((prev) => [...prev, responseMsg]);
      setIsStreaming(false);
    }, 1200);
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
          <div className="p-2.5 rounded-md border border-amber/30 bg-amber/5 text-amber text-xs font-mono flex items-center gap-2 animate-pulse">
            <Sparkles className="w-4 h-4 animate-spin text-amber" />
            <span>Streaming tokens from sovereign gateway...</span>
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
