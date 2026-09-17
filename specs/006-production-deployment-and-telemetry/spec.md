# Spec 006: Production Deployment & Telemetry Instrumentation

## 1. Problem Statement
The B-SDD framework developer workbench serves as an operations cockpit across local workstations, sovereign servers (`192.168.3.184`, `192.168.3.251`), and Cloudflare edge networks (`b-sdd-ui.pages.dev`, `bsdd.exodus.pp.ua`). To operate reliably in production:
1. The backend server requires sub-millisecond telemetry instrumentation to monitor compile latency, HTTP throughput, cache hit ratios, and active SSE connections without third-party dependencies.
2. The server must expose standard Prometheus metrics (`/api/metrics`) and structured JSON telemetry (`/api/telemetry`).
3. The server must provide a Realtime SSE telemetry channel (`/api/realtime/telemetry`) to stream live vitals to the Astryx Cockpit UI.
4. The system needs an automated production deployment pipeline that verifies pre-flight invariants, builds the frontend, deploys to Cloudflare Pages, installs/updates the sovereign systemd daemon, and validates end-to-end health.

## 2. Requirements & Scenarios

### 2.1 Pure Python Standard Library Telemetry Adapter
- Implement `src/adapters/telemetry.py` using 100% Python Standard Library.
- Record request metrics: path, method, status code, duration in milliseconds.
- Record compiler metrics: compile latency (ms), word count, budget status, SLA compliance (<50ms).
- Record DRAKON validation metrics and cache hits/misses (GitHub, Utopia DB).
- Compute statistical quantiles: min, max, average, p50, p90, p95, p99 using in-memory sliding ring buffers.
- Generate standard Prometheus text exposition format.
- Keep collection overhead strictly under 1 millisecond.

### 2.2 Workbench Server Endpoints
- Instrument all incoming requests and outgoing responses in `src/server/workbench_server.py`.
- Expose `GET /api/telemetry`: returns JSON snapshot of system, compiler, http, cache, and deployment metrics.
- Expose `GET /api/metrics`: returns Prometheus text exposition metrics.
- Expose `GET /api/realtime/telemetry`: SSE event stream emitting telemetry vitals every 2 seconds or on major events.
- Update `GET /api/health` to include high-level telemetry summary.
- Add graceful shutdown handling for SIGINT and SIGTERM.

### 2.3 Production Deployment Pipeline & Daemon
- Systemd unit definition: `deploy/systemd/b-sdd-workbench.service`.
- Cloudflare Tunnel ingress configuration: `deploy/tunnel/bsdd-tunnel.yml`.
- Master deployment script: `scripts/deploy_production.sh`.
- Health verification probe script: `scripts/verify_production_health.sh`.

### 2.4 Frontend Astryx Cockpit Integration
- Extend `b-sdd-ui/src/lib/backend-types.ts` with telemetry data models.
- Implement API client methods `getTelemetry()`, `getMetrics()`, and `subscribeTelemetrySSE()`.
- Create `useTelemetryRealtime` hook.
- Implement `TelemetryDrawer.tsx` in `b-sdd-ui` with real-time gauges, compile SLA indicator, deployment status, and metrics inspection.
- Add live telemetry pill/button in `Topbar.tsx` displaying real-time compiler latency and health status.
