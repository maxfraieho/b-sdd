# Tasks: Sovereign Backend Gateway & Copilot Streaming (Sprint 008)

- [x] task-043: Create test suite `tests/test_sovereign_gateway_and_timeline.py` verifying `/api/temporal/timeline` and `/api/copilot/proxy` upstream routing.
- [x] task-044: Implement dynamic git timeline extraction `GET /api/temporal/timeline` in `src/server/workbench_server.py`.
- [x] task-045: Upgrade `handle_post_copilot_proxy` in `src/server/workbench_server.py` with real upstream streaming proxy to `SOVEREIGN_LLM_URL` using pure `urllib.request`.
- [x] task-046: Update `b-sdd-ui/src/components/BitemporalRadar/TimelineSlider.tsx` to dynamically support variable date ranges and NOW timestamp.
- [x] task-047: Verify all tests in `tests/` pass 100%, compile latency <50ms, and execute `./run_sprint_008.sh`.
