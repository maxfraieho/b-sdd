// src/lib/api.ts
//
// Universal fetch wrapper for the B-SDD Workbench Server (localhost:8765).
// EVERY call has an offline-parity fallback: if the server is unreachable
// (network error, DNS failure, HTTP 5xx, or user-controlled kill-switch),
// we return the cached mock snapshot so the operator UI stays interactive.
//
// This preserves ADR-008-INV: "Developer workbench must function in full
// standalone offline mode against local repository files without requiring
// external cloud accounts."

import type {
  ActiveRulesResponse,
  AdrsResponse,
  DrakonSchemaResponse,
  DrakonSchemaSavePayload,
  DrakonSchemaSaveResponse,
  HealthResponse,
  SprintReviewPayload,
  SprintReviewResponse,
  SprintStateResponse,
} from './backend-types';

// ---------------------------------------------------------------------------
// Base URL resolution — supports .env override, defaults to Phase 3 spec.
// ---------------------------------------------------------------------------

export const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  'http://localhost:8765';

/** Milliseconds before we abort a stalled request and fall back to mocks. */
const REQUEST_TIMEOUT_MS = 3_500;

// ---------------------------------------------------------------------------
// Live-mode telemetry — subscribable so the Topbar can flip an "OFFLINE" chip.
// ---------------------------------------------------------------------------

export type LiveModeState = 'unknown' | 'online' | 'offline';

let liveMode: LiveModeState = 'unknown';
const liveModeListeners = new Set<(m: LiveModeState) => void>();

export function subscribeLiveMode(cb: (m: LiveModeState) => void): () => void {
  liveModeListeners.add(cb);
  cb(liveMode);
  return () => liveModeListeners.delete(cb);
}

function setLiveMode(next: LiveModeState): void {
  if (next === liveMode) return;
  liveMode = next;
  for (const cb of liveModeListeners) cb(next);
}

export function getLiveMode(): LiveModeState {
  return liveMode;
}

// ---------------------------------------------------------------------------
// Core: fetchWithFallback — the single choke-point for GET requests.
// ---------------------------------------------------------------------------

export interface FetchOptions {
  readonly signal?: AbortSignal;
  readonly headers?: HeadersInit;
  /** Suppress console.warn on offline fallback. */
  readonly quiet?: boolean;
}

export async function fetchWithFallback<T>(
  endpoint: string,
  fallbackData: T,
  options: FetchOptions = {},
): Promise<{ data: T; live: boolean }> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  // Chain the caller's abort signal into ours.
  if (options.signal) {
    if (options.signal.aborted) controller.abort();
    else options.signal.addEventListener('abort', () => controller.abort(), { once: true });
  }

  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      signal: controller.signal,
      headers: options.headers,
      // Cookies deliberately omitted — this is a same-origin local server.
    });

    if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);

    const data = (await res.json()) as T;
    setLiveMode('online');
    return { data, live: true };
  } catch (err) {
    if (!options.quiet) {
      console.warn(
        `[b-sdd] Offline fallback for GET ${endpoint} — ${err instanceof Error ? err.message : String(err)}`,
      );
    }
    setLiveMode('offline');
    return { data: fallbackData, live: false };
  } finally {
    window.clearTimeout(timeoutId);
  }
}

// ---------------------------------------------------------------------------
// POST wrapper — no automatic fallback for write endpoints (would silently
// swallow user intent). Callers get the raw error and decide the UX.
// ---------------------------------------------------------------------------

export async function postJson<TResp, TBody = unknown>(
  endpoint: string,
  body: TBody,
  options: FetchOptions = {},
): Promise<TResp> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  if (options.signal) {
    if (options.signal.aborted) controller.abort();
    else options.signal.addEventListener('abort', () => controller.abort(), { once: true });
  }

  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers ?? {}),
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const text = await res.text().catch(() => '');
      throw new Error(`HTTP ${res.status} ${res.statusText}${text ? ` — ${text}` : ''}`);
    }

    const data = (await res.json()) as TResp;
    setLiveMode('online');
    return data;
  } catch (err) {
    setLiveMode('offline');
    throw err;
  } finally {
    window.clearTimeout(timeoutId);
  }
}

// ---------------------------------------------------------------------------
// Typed thin wrappers for the 5 Phase-3 endpoints — one function per contract.
// Each takes an optional `fallback` so callers own their offline-mode default.
// ---------------------------------------------------------------------------

export function getHealth(fallback: HealthResponse) {
  return fetchWithFallback<HealthResponse>('/api/health', fallback);
}

export function getActiveRules(fallback: ActiveRulesResponse) {
  return fetchWithFallback<ActiveRulesResponse>('/api/rules/active', fallback);
}

export function getAdrs(
  fallback: AdrsResponse,
  params?: { readonly validTime?: string; readonly txTime?: string },
) {
  const search = new URLSearchParams();
  if (params?.validTime) search.set('valid_time', params.validTime);
  if (params?.txTime) search.set('transaction_time', params.txTime);
  const qs = search.toString();
  return fetchWithFallback<AdrsResponse>(`/api/adrs${qs ? `?${qs}` : ''}`, fallback);
}

export function getDrakonSchema(fallback: DrakonSchemaResponse) {
  return fetchWithFallback<DrakonSchemaResponse>('/api/drakon/schema', fallback);
}

export function saveDrakonSchema(payload: DrakonSchemaSavePayload) {
  return postJson<DrakonSchemaSaveResponse, DrakonSchemaSavePayload>(
    '/api/drakon/schema',
    payload,
  );
}

export function getSprintState(fallback: SprintStateResponse) {
  return fetchWithFallback<SprintStateResponse>('/api/sprint/state', fallback);
}

export function submitSprintReview(payload: SprintReviewPayload) {
  return postJson<SprintReviewResponse, SprintReviewPayload>('/api/sprint/review', payload);
}

export function getProjects(fallback: import('@/types/specs').ProjectsResponse) {
  return fetchWithFallback<import('@/types/specs').ProjectsResponse>('/api/projects', fallback);
}

export function getSpecs(fallback: import('@/types/specs').SpecsResponse) {
  return fetchWithFallback<import('@/types/specs').SpecsResponse>('/api/specs', fallback);
}

export function toggleTask(payload: { spec_id: string; task_id: string; completed?: boolean }) {
  return postJson<{ success: boolean; spec_id: string; task_id: string; completed: boolean }>(
    '/api/tasks/toggle',
    payload,
  );
}

export function saveAdr(payload: { id: string; file_path: string; content: string }) {
  return postJson<{
    success: boolean;
    id: string;
    file_path: string;
    bytes_written: number;
    recompiled_rules: boolean;
    saved_at: string;
  }>('/api/adrs/save', payload);
}

export function syncUtopia(kbId?: string) {
  return postJson<{
    success: boolean;
    intents_registered?: number;
    intents_total?: number;
    supersessions?: number;
    kg_entities?: number;
    kg_facts?: number;
    synced_at: string;
    error?: string;
  }>('/api/sync/utopia', { kb_id: kbId });
}

