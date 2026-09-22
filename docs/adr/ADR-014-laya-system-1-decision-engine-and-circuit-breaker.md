# ADR-014: Non-Autoregressive System 1 Decision Engine (Laya) & Podroid Edge Circuit Breaker

* **Status:** Accepted
* **Date:** 2026-09-22
* **Component:** core, daemon, infrastructure
* **Supersedes:** None

## Context and Problem Statement
Autoregressive LLM calls for task classification, architectural invariant checks, and procedural skill routing introduce unacceptable latency (500ms–3000ms), consume context tokens, and increase operational cost. In the B-SDD feedback loop, incoming tasks from Telegram, NotebookLM, or CLI must undergo immediate pre-flight gatekeeping and skill injection without placing RAM or computational overhead on the primary developer host (192.168.3.161). Furthermore, edge nodes (such as Google Pixel 7 running Podroid Alpine VM) are subject to Android aggressive battery management and sleep cycles, requiring resilient fallback and stateful circuit breaking.

## Decision Drivers
* Sub-40ms inference latency for System 1 fast-path cognitive classification.
* Zero RAM overhead and zero 3rd-party dependencies on Host .161 (ADR-002 Pure Standard Library).
* Automatic state transition and fault tolerance: dynamic Circuit Breaker (ONLINE ↔ OFFLINE) with debounced Telegram alerting.
* Formal mathematical primitives (`choice`, `score`, `noul`) for discrete branching and invariant fitness gating.
* Automated routing to the 48 Golden Core procedural skills catalog.
* Seamless bidirectional synchronization with Utopia DB intent store and knowledge graph on Pixel 7 (192.168.3.251).

## Considered Options
1. Local heavy Transformer/ONNX runtime on Host .161 (consumes host RAM, slows down development cycles).
2. Remote cloud API calls for pre-flight routing (introduces WAN dependency, high latency, recurring token fees).
3. Dedicated Edge Inference Node on Google Pixel 7 (Podroid Alpine VM `192.168.3.251:9623`) with Host .161 Circuit Breaker & Local Heuristic Fallback (Chosen).

## Decision Outcome
Chosen option: **Option 3: Dedicated Edge Inference Node on Pixel 7 (Podroid) with Laya Circuit Breaker & Pre-Flight Capsule Injection**.

1. **Edge Daemon (`laya_daemon.py`):** Deployed on Pixel 7 Podroid Alpine VM at `192.168.3.251:9623`, running under OpenRC service `podroid-laya` with port forwarding via `podroid-forward`. Delivers sub-40ms response times (measured 5–15ms).
2. **Mathematical Primitives:**
   - `choice`: Discrete action (`PROCEED`, `REMEDIATE_INVARIANTS`, `HALT_FOR_INSPECTION`, `CLARIFY_QUESTIONS`).
   - `score`: Confidence / invariant fitness coefficient ($1.0 - P(\text{violation})$).
   - `noul`: Non-Operative Unit Logic (neutral invariant pass-through gate).
3. **Domain & Golden Core Skill Routing:** Categorizes requests into `core`, `ui`, `skills`, or `infrastructure`, and injects prioritized skills (`@b-sdd`, `@intent-continuity`, `@frontend-design`, etc.).
4. **Resilient Circuit Breaker (`LayaCircuitBreaker`):** Maintained in `bsdd_supervisor.py`. Automatically detects timeouts or connection refusals, switches to `OFFLINE` mode with `LocalHeuristicFallback`, and fires debounced Telegram notifications strictly upon state transitions (`ONLINE` ↔ `OFFLINE`).
5. **Universal Pre-Flight Hook:** Built into `./run_b_sdd.sh` (Step 4) and supervisor dispatch, prepending `[LAYA DECISION: ...]` capsules to agent prompts before harness execution.

## Invariants
- INV-014-01: `LayaClient` must use 100% Python Standard Library (zero external dependencies) and must never throw unhandled connection exceptions.
- INV-014-02: Pre-flight decision querying must enforce a strict timeout ($\le 3.0\text{s}$) and immediately degrade to `LocalHeuristicFallback` upon failure.
- INV-014-03: Telegram notifications for Circuit Breaker status must be state-debounced (zero spam; triggers only on discrete transitions).
- INV-014-04: The pre-flight hook in `run_b_sdd.sh` must remain idempotent (never duplicate an existing Laya capsule in prompt).
- INV-014-05: All ADR updates and structural invariants must synchronize with Utopia DB on Pixel 7 (`192.168.3.251`).
- INV-014-06: Fast-Path Pre-Commit Gatekeeper: P(violation) < 0.15 grants instant commit; offline degrades to local heuristics.
