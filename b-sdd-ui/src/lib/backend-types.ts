// src/lib/backend-types.ts
//
// DTOs exposed by src/server/workbench_server.py (100% Python stdlib) on
// http://localhost:8765. Mirrors — do NOT drift these types from the backend
// contract. If the backend changes shape, update here first, then bump the
// Handoff document (docs/decision/HANDOFF_BACKEND.md §6).

import type { DrakonSchemaIR } from '@/types/drakon';
import type { BitemporalAdr } from '@/types/adr';
import type { ModelSlotId } from '@/types/copilot';

// ---- Health ---------------------------------------------------------------

export type NodeStatus = 'online' | 'offline' | 'degraded' | 'unknown';

export interface HealthNode {
  readonly host: string;
  readonly port: number;
  readonly status: NodeStatus;
  readonly latency_ms?: number;
  readonly detail?: string;
}

export interface HealthResponse {
  readonly server: NodeStatus;
  readonly utopia_db: HealthNode;
  readonly llm_gateway: HealthNode & {
    readonly slots_available?: number;
  };
  readonly checked_at: string;
}

// ---- Active Rules (Pre-Flight Compilation snapshot) -----------------------

export interface ActiveRulesResponse {
  readonly compiled_snapshot: string;
  readonly word_count: number;
  readonly max_budget: 500;
  readonly recommended_skills: readonly string[];
  readonly latency_ms?: number;
  readonly compiled_at?: string;
}

// ---- ADRs (bitemporal) ----------------------------------------------------

export interface AdrsResponse {
  readonly adrs: readonly BitemporalAdr[];
  readonly valid_time?: string;
  readonly transaction_time?: string;
  readonly total: number;
}

// ---- DRAKON schema --------------------------------------------------------

export type DrakonWidgetDiagram = Record<string, unknown>; // widget-native format

export interface DrakonSchemaResponse {
  readonly schema_ir: DrakonSchemaIR;
  readonly diagram: DrakonWidgetDiagram;
  readonly validation: {
    readonly is_valid: boolean;
    readonly violations?: readonly string[];
    readonly crossings?: number;
    readonly planar?: boolean;
  };
  readonly source_path?: string;
}

export interface DrakonSchemaSavePayload {
  readonly schema_ir: DrakonSchemaIR;
  readonly diagram?: DrakonWidgetDiagram;
  readonly target_path?: string;
}

export interface DrakonSchemaSaveResponse {
  readonly saved: boolean;
  readonly target_path: string;
  readonly validation: DrakonSchemaResponse['validation'];
  readonly bytes_written?: number;
}

// ---- Sprint state & review -----------------------------------------------

export type SprintReviewAction = 'approve' | 'reject';

export interface SprintStateResponse {
  readonly sprint_id: string;
  readonly current_phase: string;
  readonly can_approve: boolean;
  readonly can_reject: boolean;
  readonly fitness_summary?: {
    readonly passed: number;
    readonly total: number;
    readonly ast_isolation_score: number;
    readonly latency_ms: number;
    readonly token_count: number;
  };
}

export interface SprintReviewPayload {
  readonly action: SprintReviewAction;
  readonly negative_invariants?: readonly string[];
  readonly rationale?: string;
  readonly rollback_depth?: number;
  readonly operator_signature?: string;
}

export interface SprintReviewResponse {
  readonly action: SprintReviewAction;
  readonly sprint_id: string;
  readonly next_sprint_id?: string;
  readonly cycle_id?: string;
  readonly worm_locked?: boolean;
  readonly launch_command?: string;
  readonly handoff_path?: string;
  readonly created_branch?: string;
  readonly signature?: string;
}

// ---- Copilot proxy (SSE) --------------------------------------------------

export interface CopilotProxyPayload {
  readonly prompt: string;
  readonly slot: ModelSlotId;
  readonly stream: true;
  readonly attached_contexts?: readonly string[];
}

/**
 * Server-Sent Event frames emitted by POST /api/copilot/proxy.
 * The stream terminates when `type: 'done'` is received or the socket closes.
 */
export type CopilotSseEvent =
  | { readonly type: 'token'; readonly delta: string }
  | { readonly type: 'meta'; readonly slot: ModelSlotId; readonly latency_ms?: number }
  | { readonly type: 'done'; readonly total_tokens?: number; readonly reason?: string }
  | { readonly type: 'error'; readonly message: string };
