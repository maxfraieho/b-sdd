# Tasks: Spec 005 - Live GitHub API Sync & Appwrite Realtime Phase Sync

- [x] `task-001`: Implement `src/adapters/github_sync.py` (pure standard library, disk cache, offline fallback).
- [x] `task-002`: Implement `src/adapters/appwrite_client.py` (pure stdlib Appwrite client & Ed25519 signature verification).
- [x] `task-003`: Add Realtime SSE broadcaster and phase management endpoints to `src/server/workbench_server.py`.
- [x] `task-004`: Wire GitHub endpoints `GET /api/github/repos` and `POST /api/github/sync` into `src/server/workbench_server.py`.
- [x] `task-005`: Create planar DRAKON algorithm `specs/005-github-api-and-appwrite-realtime/logic.drakon.json` and catalog template.
- [x] `task-006`: Extend frontend `b-sdd-ui` with GitHub sync, Appwrite Realtime phase sync, and Topbar health badges.
- [x] `task-007`: Add automated tests for GitHub sync and Appwrite Realtime phase sync.
- [x] `task-008`: Execute architecture fitness tests, verify zero 3rd-party dependencies, sub-50ms compile latency, and build frontend.
