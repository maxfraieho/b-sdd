# Tasks: Spec 006 - Production Deployment & Telemetry Instrumentation

- [x] `task-001`: Implement `src/adapters/telemetry.py` (pure standard library, latency quantiles, Prometheus exporter, sub-1ms overhead).
- [x] `task-002`: Integrate telemetry, `/api/telemetry`, `/api/metrics`, `/api/realtime/telemetry`, and graceful shutdown into `src/server/workbench_server.py`.
- [x] `task-003`: Create production deployment suite (`scripts/deploy_production.sh`, `scripts/verify_production_health.sh`, `deploy/systemd/b-sdd-workbench.service`, `deploy/tunnel/bsdd-tunnel.yml`).
- [x] `task-004`: Create planar DRAKON algorithm `specs/006-production-deployment-and-telemetry/logic.drakon.json` and catalog template `src/drakon/templates/production_deployment_and_telemetry.json`.
- [x] `task-005`: Extend frontend `b-sdd-ui` with telemetry types, API methods, `useTelemetryRealtime` hook, `TelemetryDrawer`, and `Topbar` telemetry trigger.
- [x] `task-006`: Implement unit and integration tests in `tests/test_telemetry.py` and `tests/test_production_deployment.py`.
- [x] `task-007`: Verify architecture fitness gates (compile latency < 50ms, context words < 500, zero 3rd-party dependencies in `src/`, clean frontend build).
- [x] `task-008`: Synchronize with Utopia DB and synthesize Sprint N+5 handoff artifacts.
