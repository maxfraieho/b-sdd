# ADR-012: Production Deployment and Telemetry Instrumentation

* **Status:** Accepted
* **Date:** 2026-09-17
* **Component:** server
* **Supersedes:** None

## Context and Problem Statement
With the B-SDD Workbench supporting live GitHub API synchronization, Appwrite Realtime phase sync, and sovereign model inference, the framework requires production-grade deployment and real-time observability. Production deployments across sovereign bare-metal servers (`192.168.3.184`, `192.168.3.251`), Cloudflare Tunnels (`bsdd.exodus.pp.ua`), and Cloudflare Pages (`b-sdd-ui.pages.dev`) must ensure continuous availability, sub-50ms compiler SLA enforcement, zero invariant regressions, and live operator telemetry without introducing heavy external third-party observability agents.

## Decision Drivers
* Zero third-party dependency runtime in `src/` (pure Python Standard Library).
* Sub-millisecond (<1ms) telemetry collection overhead to prevent polluting compilation latency.
* High-precision latency quantiles (p50, p90, p95, p99) for compiler runs, API requests, and visual DRAKON validations.
* Standard Prometheus text exposition format (`/api/metrics`) and JSON snapshot (`/api/telemetry`).
* Real-time Server-Sent Events (SSE) telemetry stream for the Astryx Cockpit UI.
* Automated multi-tier production deployment pipeline with systemd daemon management and post-deployment health verification probes.

## Considered Options
1. External monitoring agents (Prometheus client_python, Datadog agent, OpenTelemetry SDK) — Violates B-SDD Zero-Dependency Pure Runtime Invariant.
2. Static server log files without runtime aggregation — Poor operator visibility, high disk I/O, no live UI gauge capability.
3. Pure Python Standard Library Telemetry Adapter with Prometheus Exporter, Realtime SSE Streaming, and Sovereign Deployment Daemon (Chosen).

## Decision Outcome
Chosen option: **Pure Python Standard Library Telemetry Adapter with Prometheus Exporter, Realtime SSE Streaming, and Sovereign Deployment Daemon** (Option 3).

### 1. Telemetry Collector (`src/adapters/telemetry.py`)
* Lightweight ring-buffer latency tracking with exact percentile computation (p50, p90, p95, p99).
* Request, error, invariant check, and cache hit/miss counters.
* Context manager `measure_latency()` with <0.05ms overhead.
* Prometheus exposition generator (`/api/metrics`) and JSON summary generator (`/api/telemetry`).

### 2. Workbench Server Instrumentation (`src/server/workbench_server.py`)
* Automatic instrumentation of all incoming HTTP requests and responses.
* Compile latency tracking linked to the sub-50ms SLA budget.
* Periodic SSE telemetry broadcaster (`/api/realtime/telemetry`) streaming live vitals to connected Astryx cockpits.
* Production daemon support with systemd service definition and graceful shutdown.

### 3. Production Deployment Suite (`scripts/deploy_production.sh`)
* Automated staged rollout: pre-flight compile -> test suite -> frontend build -> Cloudflare Pages deploy -> systemd restart on sovereign runner -> end-to-end health probe verification.

## Invariants
- ADR-012-INV-01: Telemetry collector must strictly use Python Standard Library with zero third-party dependencies.
- ADR-012-INV-02: Telemetry collection overhead must remain strictly under 1 millisecond per request.
- ADR-012-INV-03: Metrics must be exportable in standard Prometheus exposition format and JSON over HTTP.
- ADR-012-INV-04: Production deployment must support automated health verification probes before traffic cutover.
- ADR-012-INV-05: Realtime telemetry stream must broadcast system metrics and latency percentiles via SSE.
