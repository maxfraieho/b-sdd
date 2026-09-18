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

export interface MutationCardData {
  tx_id: string;
  operation: string;
  target_symbol?: string;
  new_name?: string;
  cow_branch?: string;
  mutations_applied: number;
  files_affected?: Array<{ workspace: string; file: string }>;
  status: 'committed' | 'rolled_back' | 'dry_run_completed';
}

export interface CopilotLogMessage {
  id: string;
  timestamp: string;
  role: 'system' | 'assistant' | 'user';
  content: string;
  slot?: ModelSlotId;
  tokensUsed?: number;
  symbolCard?: SymbolCardData;
  mutationCard?: MutationCardData;
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
