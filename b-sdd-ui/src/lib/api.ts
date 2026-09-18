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
  GithubSyncResponse,
  PhaseTransitionEvent,
  TelemetrySummaryResponse,
  SymbolsSearchResponse,
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

export function getDrakonSchema(fallback: DrakonSchemaResponse, specId?: string) {
  const url = specId ? `/api/drakon/schema?spec=${encodeURIComponent(specId)}` : '/api/drakon/schema';
  return fetchWithFallback<DrakonSchemaResponse>(url, fallback);
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

export function getGithubRepos(fallback: GithubSyncResponse) {
  return fetchWithFallback<GithubSyncResponse>('/api/github/repos', fallback);
}

export function syncGithubRepos(username?: string) {
  return postJson<GithubSyncResponse>('/api/github/sync', { username });
}

export function setSprintPhase(phaseId: string, operatorSignature?: string) {
  return postJson<{
    status: string;
    current_phase: string;
    from_phase: string;
    phases: any[];
    record_id?: string;
    appwrite_synced?: boolean;
    timestamp: string;
  }>('/api/sprint/phase', { phase_id: phaseId, operator_signature: operatorSignature });
}

/**
 * Subscribes to live Appwrite/B-SDD Realtime phase event stream via SSE (ADR-011).
 */
export function subscribeRealtimePhases(
  onEvent: (e: PhaseTransitionEvent) => void,
  onError?: (err: any) => void,
): () => void {
  if (typeof window === 'undefined' || typeof EventSource === 'undefined') {
    return () => {};
  }

  const url = `${API_BASE_URL}/api/realtime/phases`;
  let es: EventSource | null = null;
  let isClosed = false;

  const connect = () => {
    if (isClosed) return;
    try {
      es = new EventSource(url);
      es.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onEvent(data);
        } catch {
          // ignore keep-alive or ping
        }
      };
      es.onerror = (err) => {
        if (onError) onError(err);
        es?.close();
        // Retry connection after 5 seconds
        if (!isClosed) {
          setTimeout(connect, 5000);
        }
      };
    } catch (e) {
      if (onError) onError(e);
    }
  };

  connect();

  return () => {
    isClosed = true;
    es?.close();
  };
}

// ---------------------------------------------------------------------------
// Telemetry & Observability (ADR-012)
// ---------------------------------------------------------------------------

const MOCK_TELEMETRY: TelemetrySummaryResponse = {
  status: 'healthy',
  timestamp: new Date().toISOString(),
  uptime_seconds: 3600,
  memory_rss_mb: 42.5,
  compiler: {
    last_compile_ms: 14.5,
    compile_count: 12,
    failed_compiles: 0,
    word_count: 476,
    max_budget: 500,
    sla_target_ms: 50.0,
    sla_passed: true,
    sla_violations: 0,
    quantiles: { count: 12, min: 11.2, max: 24.1, avg: 14.5, p50: 13.8, p90: 18.2, p95: 21.0, p99: 24.1 },
  },
  http: {
    total_requests: 142,
    requests_per_sec: 2.4,
    status_codes: { '200': 140, '304': 2 },
    top_endpoints: { 'GET /api/health': 60, 'GET /api/rules/active': 40, 'GET /api/telemetry': 20 },
    active_sse_connections: 1,
    sse_events_broadcast: 48,
    quantiles: { count: 142, min: 0.8, max: 12.4, avg: 2.1, p50: 1.8, p90: 3.5, p95: 5.2, p99: 10.1 },
  },
  cache: {
    github: { hits: 18, misses: 2, hit_ratio: 0.9 },
    utopia: { hits: 34, misses: 1, hit_ratio: 0.97 },
  },
  deployment: {
    environment: 'production',
    cf_pages_url: 'https://b-sdd-ui.pages.dev',
    gateway_url: 'https://bsdd.exodus.pp.ua',
    systemd_service: 'b-sdd-workbench.service',
    systemd_status: 'running',
  },
};

/**
 * Fetches structured telemetry and metrics summary from the backend (ADR-012).
 */
export async function getTelemetry(
  fallback: TelemetrySummaryResponse = MOCK_TELEMETRY,
): Promise<TelemetrySummaryResponse> {
  const result = await fetchWithFallback<TelemetrySummaryResponse>('/api/telemetry', fallback);
  return result.data;
}

/**
 * Fetches standard Prometheus text metrics exposition (ADR-012).
 */
export async function getMetrics(): Promise<string> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/metrics`, {
      headers: { Accept: 'text/plain' },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.text();
  } catch {
    return '# Prometheus metrics fallback (server offline)';
  }
}

/**
 * Subscribes to Realtime SSE telemetry vitals stream (ADR-012).
 */
export function subscribeRealtimeTelemetry(
  onData: (data: TelemetrySummaryResponse) => void,
  onError?: (err: any) => void,
): () => void {
  if (typeof window === 'undefined' || typeof EventSource === 'undefined') {
    return () => {};
  }

  const url = `${API_BASE_URL}/api/realtime/telemetry`;
  let es: EventSource | null = null;
  let isClosed = false;

  const connect = () => {
    if (isClosed) return;
    try {
      es = new EventSource(url);
      es.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onData(data);
        } catch {
          // ignore parsing error
        }
      };
      es.onerror = (err) => {
        if (onError) onError(err);
        es?.close();
        if (!isClosed) {
          setTimeout(connect, 5000);
        }
      };
    } catch (e) {
      if (onError) onError(e);
    }
  };

  connect();

  return () => {
    isClosed = true;
    es?.close();
  };
}

/**
 * Searches AST symbols across all registered workspaces (INV-014-04).
 */
export async function searchCrossWorkspaceSymbols(
  query: string,
  workspace?: string,
): Promise<SymbolsSearchResponse> {
  const fallback: SymbolsSearchResponse = {
    query,
    workspace: workspace ?? null,
    total_matches: 0,
    symbols: [],
    workspaces: [
      { name: 'b-sdd', path: '/home/vokov/projects/b-sdd', is_active: true, indexed_count: 0 },
    ],
  };

  const params = new URLSearchParams();
  if (query) params.set('q', query);
  if (workspace) params.set('workspace', workspace);

  const endpoint = `/api/symbols/search${params.toString() ? `?${params.toString()}` : ''}`;
  const res = await fetchWithFallback<SymbolsSearchResponse>(endpoint, fallback, { quiet: true });
  return res.data;
}


