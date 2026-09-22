/**
 * B-SDD Cluster Health & Proactive Telemetry Types.
 * Sprint 032 - Astryx Cockpit UI.
 */

export type ServiceHealthStatus = "UP" | "DOWN" | "DEGRADED";

export interface ServiceHealth {
  service_id: string;
  host: string;
  port: number;
  is_up: boolean;
  latency_ms: number;
  error_message?: string | null;
}

export interface ClusterHealthReport {
  timestamp: string;
  services: ServiceHealth[];
  overall_status: ServiceHealthStatus;
}

export interface Vector3IntentState {
  cosine_alignment: number;
  threshold: number;
  verdict: "VERDICT_INTENT_ALIGNED" | "VERDICT_INTENT_DRIFT_WARNING" | "VERDICT_INTENT_VIOLATION";
  allow_commit: boolean;
  latency_ms: number;
  missing_invariants: string[];
}
