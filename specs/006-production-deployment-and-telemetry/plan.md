# Plan 006: Production Deployment & Telemetry Instrumentation

## Architecture Overview
```
┌───────────────────────────┐           ┌────────────────────────────┐
│      Cloudflare Edge      │           │    Sovereign Runner Host   │
│  b-sdd-ui.pages.dev       │           │       192.168.3.184        │
│  bsdd.exodus.pp.ua:443    │           │  systemd: b-sdd-workbench  │
└─────────────▲─────────────┘           └──────────────▲─────────────┘
              │                                        │
     Cloudflare Tunnel                       systemctl / rsync / probe
              │                                        │
┌─────────────▼────────────────────────────────────────▼─────────────┐
│                   src/server/workbench_server.py                   │
│   • GET /api/telemetry            • GET /api/metrics (Prometheus)  │
│   • GET /api/realtime/telemetry   • GET /api/health                │
│   • Auto-instrumentation on all HTTP routes                        │
└─────────────▲────────────────────────────────────────▲─────────────┘
              │                                        │
              │                                        │
┌─────────────▼─────────────┐           ┌──────────────▼─────────────┐
│  src/adapters/telemetry.py │           │       Astryx Cockpit       │
│  • Ring buffer quantiles  │           │   • Topbar Telemetry Pill  │
│  • Pure stdlib counters   │           │   • TelemetryDrawer        │
│  • Prometheus generator   │           │   • Realtime SSE hook      │
└───────────────────────────┘           └────────────────────────────┘
```

## Phases
1. **Phase 1: Pure Stdlib Telemetry Adapter**
   - Implement `src/adapters/telemetry.py` with thread-safe counters, gauges, quantile calculations, and Prometheus generator.
2. **Phase 2: Workbench Server Telemetry & Graceful Shutdown**
   - Integrate request latency tracking, `/api/telemetry`, `/api/metrics`, `/api/realtime/telemetry`, and signal handlers in `src/server/workbench_server.py`.
3. **Phase 3: Production Deployment Suite**
   - Author `deploy/systemd/b-sdd-workbench.service`, `deploy/tunnel/bsdd-tunnel.yml`, `scripts/deploy_production.sh`, and `scripts/verify_production_health.sh`.
4. **Phase 4: Visual DRAKON Algorithm**
   - Construct planar DRAKON diagram `specs/006-production-deployment-and-telemetry/logic.drakon.json` and catalog template `src/drakon/templates/production_deployment_and_telemetry.json`.
5. **Phase 5: Frontend Astryx Cockpit Integration**
   - Add types to `backend-types.ts`, API methods to `api.ts`, hook `useTelemetryRealtime.ts`, and component `TelemetryDrawer.tsx`.
   - Wire telemetry pill into `Topbar.tsx` and `App.tsx`.
6. **Phase 6: Automated Verification & Architectural Fitness**
   - Add tests `tests/test_telemetry.py` and `tests/test_production_deployment.py`.
   - Run `pytest` and `npm run build`.
   - Compile active rules and synthesize handoff.
