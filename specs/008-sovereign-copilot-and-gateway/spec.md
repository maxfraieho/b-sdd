# SPEC-008: Sovereign Backend Gateway & Copilot Streaming

**Phase:** Φ1 Intent Framing  
**Status:** implemented  
**Author:** B-SDD Autonomous Systems Agent  
**Standard References:** ADR-002, ADR-004, ADR-005, ADR-007  
**Word Budget:** <500 words (ADR-002 invariant)  

---

## 1. Intent & Problem Statement
The current B-SDD workbench UI and backend suffer from three operational decoupling defects:
1. **DEF-05 (Mock Copilot Streaming):** The `/api/copilot/proxy` endpoint streams hardcoded static string tokens rather than proxying requests to the sovereign LLM Gateway (`http://192.168.3.184:18880/v1/chat/completions`).
2. **DEF-08 (Static 16-Day Scrubber):** The `TimelineSlider.tsx` component restricts temporal navigation to a static 16-day window (Sept 1 - Sept 16, 2026), failing to dynamically track repository commits and real timestamps.
3. **DEF-09 (Mixed Content Cloudflare Pages):** Direct client HTTP calls to local backend ports trigger browser Mixed Content blocks when served over HTTPS from `https://b-sdd-ui.pages.dev`.

## 2. Formal Specification & Invariants
1. **ADR-005-INV-01 (Sovereign LLM Proxying):**
   `handle_post_copilot_proxy` in `src/server/workbench_server.py` MUST establish a real streaming connection to the upstream sovereign LLM at `192.168.3.184:18880` (or `SOVEREIGN_LLM_URL`) via standard library `urllib.request`. Tokens received from upstream MUST stream to the client via Server-Sent Events (SSE) with `[ADR]`, `[DRAKON]`, and `[RULES]` system prompt injection.
2. **ADR-004-INV-01 (Dynamic Bitemporal Timeline):**
   A new endpoint `GET /api/temporal/timeline` MUST extract git history (`git log --pretty=format:"%H|%at|%s"`) to provide dynamically bounded timestamps ($T_v / T_t$) spanning from repository genesis to the current moment.
3. **Dynamic Frontend Scrubber Adaptation:**
   `TimelineSlider.tsx` MUST consume `/api/temporal/timeline` or dynamically compute the date boundaries up to the current day, eliminating static 16-day clamping.
4. **ADR-002-INV-01 (Zero External Dependencies):**
   All proxying and git parsing in `src/` MUST use Python standard library exclusively (`urllib.request`, `subprocess`, `json`, `os`).

## 3. Success Criteria
- [x] `POST /api/copilot/proxy` initiates real HTTP connection to sovereign gateway with fallback resilience.
- [x] `GET /api/temporal/timeline` returns valid commit list with UNIX timestamps and ISO dates.
- [x] `TimelineSlider` dynamically scales beyond Sept 16, 2026 without hardcoded ranges.
- [x] Automated test suite `tests/test_sovereign_gateway_and_timeline.py` passes 100%.
