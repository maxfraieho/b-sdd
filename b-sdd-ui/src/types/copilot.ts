// src/types/copilot.ts

export type ModelSlotId = 'agent-proxy' | 'coding-proxy' | 'reasoning-proxy' | 'pi-harness';

export interface ModelSlot {
  id: ModelSlotId;
  name: string;
  endpoint: string;
  model: string;
  description: string;
  latencyAvg: string;
  active: boolean;
}

export interface SymbolCardData {
  name: string;
  kind: string;
  workspace: string;
  file: string;
  line: number;
  docstring: string;
  tx?: string;
  tv?: string;
  dependencies?: string[];
}

export interface CopilotLogMessage {
  id: string;
  timestamp: string;
  role: 'system' | 'assistant' | 'user';
  content: string;
  slot?: ModelSlotId;
  tokensUsed?: number;
  symbolCard?: SymbolCardData;
  critique?: {
    invariantId: string;
    title: string;
    status: 'pass' | 'warn' | 'fail';
    detail: string;
  };
}

export interface TokenBudget {
  maxWords: number; // 500 words strict invariant
  currentWords: number;
  tokensEstimated: number;
  isExceeded: boolean;
}
