# ADR-011: Live GitHub API Sync and Appwrite Realtime Phase Sync

* **Status:** Accepted
* **Date:** 2026-09-17
* **Component:** adapters
* **Supersedes:** None

## Context and Problem Statement
The developer workbench (`b-sdd-ui` and `workbench_server.py`) previously presented simulated GitHub repository data in `ProjectSwitcherModal` and retained sprint phase progression solely in ephemeral browser React state. In production multi-tenant environments, engineering teams require:
1. Live synchronization with GitHub repositories (`maxfraieho` and corporate enterprise orgs) to introspect branches, commits, and repository metadata directly from the workbench.
2. Centralized, real-time synchronization of Human-in-the-Loop (HITL) sprint phases ($\Phi_1$ through $\Phi_7$) through the Appwrite BaaS control plane, broadcasting phase transitions to all connected engineering operators.
3. Cryptographically signed operator approvals (Ed25519 / WORM audit ledger) during the $\Phi_6 \to \Phi_7$ Review Gate to ensure non-repudiation.

## Decision Drivers
* Implement pure Python Standard Library adapters in `src/adapters/` with zero external pip dependencies.
* Provide live GitHub REST API querying with disk-backed cache (`.context/github_cache.json`) and offline fallback.
* Implement Appwrite BaaS control plane adapter and Realtime Server-Sent Events (SSE) streaming gateway for sub-second phase synchronization.
* Enforce cryptographic operator signature verification on sprint approval requests.
* Maintain all B-SDD foundational fitness gates: compile latency <50ms, context words <500, pure stdlib.

## Considered Options
1. Require external third-party SDKs (`PyGithub`, `appwrite`, `nacl`) — Violates B-SDD Zero-Dependency Pure Runtime Invariant.
2. Restrict to browser-only client-side API keys — Leaks credentials and fails to maintain sovereign audit logs on backend.
3. Pure Python Standard Library Adapters with Live GitHub HTTP Client, Appwrite Control Plane Client, and Realtime SSE Phase Synchronizer (Chosen).

## Decision Outcome
Chosen option: **Pure Python Standard Library Adapters with Live GitHub HTTP Client, Appwrite Control Plane Client, and Realtime SSE Phase Synchronizer** (Option 3).

### 1. Live GitHub API Sync Adapter (`src/adapters/github_sync.py`)
* Uses `urllib.request` with optional `GITHUB_TOKEN` authentication and custom User-Agent.
* Exposes `fetch_user_repositories(username)` and `sync_repositories()` with intelligent disk cache in `.context/github_cache.json`.
* Provides offline parity: if remote GitHub is unreachable or rate-limited, returns cached repository snapshot with live=False indicator.
* Integrated into `GET /api/github/repos`, `POST /api/github/sync`, and `GET /api/projects`.

### 2. Appwrite BaaS Control Plane Adapter (`src/adapters/appwrite_client.py`)
* Implements pure stdlib HTTP client for Appwrite Database & Collections (`b_sdd_cycles`).
* Manages sprint phase states ($\Phi_1$ Framing to $\Phi_7$ Distillation) and writes WORM audit records.
* Verifies cryptographic operator signatures (`Ed25519` / HMAC-SHA256 non-repudiation tokens) before advancing $\Phi_6 \to \Phi_7$.

### 3. Realtime Phase Event Streaming Gateway (`src/server/workbench_server.py`)
* Implements thread-safe pub/sub event broadcaster delivering real-time phase change events.
* Exposes `GET /api/realtime/phases` (SSE stream) for instant push updates to client cockpits.
* Exposes `POST /api/sprint/phase` to advance or set phase, automatically broadcasting to all connected operators and syncing with Appwrite.

## Invariants
- ADR-011-INV-01: GitHub API sync adapter must operate strictly via Python Standard Library with disk-backed offline fallback parity.
- ADR-011-INV-02: Appwrite Realtime phase sync must broadcast state transitions in real time via SSE/WebSocket with offline fallback parity.
- ADR-011-INV-03: Phase review approvals must accept and cryptographically verify operator signature before unlocking next sprint execution.
