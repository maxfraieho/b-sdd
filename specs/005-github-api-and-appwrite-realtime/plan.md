# Plan 005: Live GitHub API Sync & Appwrite Realtime Phase Sync

## Architecture Overview
```
┌─────────────────────────┐          ┌───────────────────────────┐
│       GitHub API        │          │       Appwrite BaaS       │
│  api.github.com/users   │          │   Collections & Realtime  │
└────────────▲────────────┘          └─────────────▲─────────────┘
             │                                     │
   urllib.request (pure stdlib)          urllib.request (pure stdlib)
             │                                     │
┌────────────▼─────────────────────────────────────▼─────────────┐
│                       src/adapters/                            │
│     github_sync.py               appwrite_client.py            │
└────────────▲─────────────────────────────────────▲─────────────┘
             │                                     │
┌────────────▼─────────────────────────────────────▼─────────────┐
│                 src/server/workbench_server.py                 │
│  GET /api/github/repos            GET /api/realtime/phases(SSE)│
│  POST /api/github/sync            POST /api/sprint/phase       │
│  GET /api/projects                POST /api/sprint/review      │
└────────────▲─────────────────────────────────────▲─────────────┘
             │                                     │
             │           HTTP / SSE                │
             │                                     │
┌────────────▼─────────────────────────────────────▼─────────────┐
│               b-sdd-ui (Astryx Cockpit Frontend)               │
│  • ProjectSwitcherModal (GitHub sync button & live repos)       │
│  • Topbar (Appwrite RT & GitHub health badges)                 │
│  • PhaseStepper (Realtime phase sync via SSE)                  │
│  • ReviewGateModal (Ed25519 operator signing)                  │
└────────────────────────────────────────────────────────────────┘
```

## Phases
1. **Phase 1: Backend Adapters**
   - Implement `src/adapters/github_sync.py` with pure standard library, disk cache, and offline parity.
   - Implement `src/adapters/appwrite_client.py` with pure standard library, phase persistence, and Ed25519 signature checks.
2. **Phase 2: Gateway Endpoints & Event Broadcaster**
   - Add thread-safe Realtime phase broadcaster to `src/server/workbench_server.py`.
   - Wire `GET /api/realtime/phases`, `POST /api/sprint/phase`, `GET /api/github/repos`, `POST /api/github/sync`.
   - Update `GET /api/projects` and `GET /api/health` with GitHub & Appwrite status.
3. **Phase 3: Visual DRAKON Algorithm Template**
   - Create `specs/005-github-api-and-appwrite-realtime/logic.drakon.json` and catalog template `src/drakon/templates/github_appwrite_sync.json`.
   - Validate planarity with `DrakonValidator`.
4. **Phase 4: Frontend UI Integration**
   - Add types to `b-sdd-ui/src/lib/backend-types.ts`.
   - Add API calls to `b-sdd-ui/src/lib/api.ts`.
   - Add hook `b-sdd-ui/src/hooks/usePhaseRealtime.ts`.
   - Update `Topbar.tsx`, `ProjectSwitcherModal.tsx`, and `ReviewGateModal.tsx`.
5. **Phase 5: Automated Tests & Fitness Verification**
   - Implement unit and integration tests in `tests/test_github_sync.py` and `tests/test_appwrite_realtime.py`.
   - Verify `pytest` passing 100% and `npm run build` passing cleanly.
