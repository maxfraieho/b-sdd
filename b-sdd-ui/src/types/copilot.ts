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

export interface CopilotLogMessage {
  id: string;
  timestamp: string;
  role: 'system' | 'assistant' | 'user';
  content: string;
  slot?: ModelSlotId;
  tokensUsed?: number;
}

export interface TokenBudget {
  maxWords: number; // 500 words strict invariant
  currentWords: number;
  tokensEstimated: number;
  isExceeded: boolean;
}
