# Spec 005: Live GitHub API Sync & Appwrite Realtime Phase Sync

## 1. Problem Statement
The developer workbench currently relies on static mock data for GitHub repositories in `ProjectSwitcherModal`, and the Human-in-the-Loop (HITL) sprint phase workflow is stored only in local React state. To enable enterprise collaboration, developers require:
1. Live GitHub API synchronization to list, introspect, and switch to GitHub repositories, complete with local offline caching.
2. Appwrite BaaS control plane integration to store sprint cycle states and verify operator signatures.
3. Sub-second Realtime phase synchronization across connected web clients via Server-Sent Events (SSE).

## 2. Requirements & Scenarios

### 2.1 Live GitHub Sync
- Connect to GitHub REST API (`https://api.github.com/users/{user}/repos`) using pure Python standard library (`urllib.request`).
- Support `GITHUB_TOKEN` environment variable if configured; gracefully fallback to unauthenticated public API with a dedicated User-Agent.
- Cache fetched repositories to `.context/github_cache.json`.
- When offline or rate-limited, serve from disk cache with `source: "cache"` and `offline_parity: true`.
- Expose REST endpoints:
  - `GET /api/github/repos`
  - `POST /api/github/sync`
- Update `GET /api/projects` to return live-synced GitHub repositories.

### 2.2 Appwrite BaaS Control Plane & Realtime Phase Sync
- Pure Python standard library Appwrite adapter (`src/adapters/appwrite_client.py`).
- Maintain current sprint phase ($\Phi_1$ through $\Phi_7$) and persist transitions into Appwrite collections (`b_sdd_cycles`).
- Expose Realtime SSE endpoint `GET /api/realtime/phases` streaming live phase events:
  ```json
  {"event": "phase_transition", "phase": "phi_6", "sprint_id": "...", "timestamp": "...", "operator": "Head Architect"}
  ```
- Expose `POST /api/sprint/phase` to advance/set phase and broadcast to all connected operators.
- Support Ed25519 / HMAC cryptographic operator signature verification in `POST /api/sprint/review`.

### 2.3 Frontend Cockpit Integration
- Add Live GitHub refresh / sync button with status indicators to `ProjectSwitcherModal`.
- Add Live Appwrite Realtime phase subscription in UI (`b-sdd-ui`) using SSE so phase state stays synchronized.
- Display "Appwrite RT" and "GitHub API" status chips in `Topbar`.
- Add operator signature signing support to `ReviewGateModal`.
