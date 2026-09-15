# ADR-007: Multi-Session Sprint Chaining and Dynamic Handoff Protocol

* **Status:** Proposed
* **Date:** 2026-09-15
* **Component:** core
* **Supersedes:** None

## Context and Problem Statement
Complex software engineering projects require multiple sequential AI agent sessions (sprints). Pre-authoring a static sequence of prompts for future sprints causes a Waterfall trap: downstream sprints fail to account for implementation-level decisions, file structures, and edge cases discovered during upstream execution. Conversely, unbounded long sessions cause severe context degradation. A formal mechanism is needed to connect discrete, fresh-context agent sessions into an uninterrupted, self-propagating development chain.

## Decision Drivers
* Prevent context fatigue by isolating each milestone into a clean session.
* Eliminate human cognitive overhead in formulating the next prompt.
* Guarantee that Sprint N+1 is strictly grounded in the actual codebase state left by Sprint N.
* Enforce automated pre-flight fitness verification at every session boundary.

## Considered Options
1. Static multi-sprint prompt lists (Waterfall, brittle to implementation changes).
2. Autonomous continuous execution in a single giant session (Context bloat and hallucination risks).
3. Dynamic Handoff Protocol via `.context/sprint_handoff.json` and `main.py handoff` (Chosen).

## Decision Outcome
Chosen option: **Dynamic Handoff Protocol** (Option 3).
1. **Session Termination Lifecycle:**
   - Every sprint concludes with three gates:
     a) `main.py fitness` (must pass 100%).
     b) `main.py distill` (updates transcript intelligence).
     c) `main.py handoff` (generates `.context/next_sprint.md` and machine-readable `sprint_handoff.json`).
2. **Next Sprint Prompt Generation:**
   - The handoff engine introspects git changes, passing tests, and project roadmap to assemble the exact, executable command for the next sprint (`./run_b_sdd.sh "<refined_prompt>"`).
3. **Optional Auto-Chaining:**
   - Support `--auto-chain` in `run_b_sdd.sh` to allow automated dispatch to the next session without human copy-pasting when running in unattended/CI modes.

## Invariants
- A session cannot generate a handoff artifact if architectural fitness tests are failing.
- Handoff prompts must explicitly cite created class names, file paths, and target ADR invariants.
- Handoff state must be committed to git alongside session code changes.
