# ADR-007: Multi-Session Sprint Chaining and Dynamic Handoff Protocol

* **Status:** Accepted
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
* Maintain 100% pure Python Standard Library runtime in core modules.

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
   - The handoff engine introspects git status, passing tests, and project roadmap (`specs/**/tasks.md`) to assemble the exact executable command for the next sprint (`./run_b_sdd.sh "<refined_prompt>"`).
3. **Machine-Readable & Human Handoff Artifacts:**
   - `.context/sprint_handoff.json`: contains structured metadata (schema version, session ID, timestamp, git branch/commit, modified files, fitness gate status, completed/pending tasks, next sprint prompt and run command).
   - `.context/next_sprint.md`: concise briefing document summarizing upstream accomplishments and downstream objectives.
4. **Auto-Chaining Execution (`run_b_sdd.sh --auto-chain`):**
   - Support `--auto-chain [N]` in `run_b_sdd.sh` to automatically loop across successive sprints with fresh session contexts until all tasks complete or max sprints reached.

## Invariants
- Downstream sprints cannot generate a handoff artifact if upstream architectural fitness tests are failing.
- Handoff prompts must deterministically prefix active rules and explicitly cite target task and modified seams.
- Handoff artifacts must be emitted in both machine-readable JSON (`sprint_handoff.json`) and human-readable Markdown (`next_sprint.md`).
- Core handoff synthesis in `src/` must strictly use 100% pure Python Standard Library.
- Auto-chain runner must verify zero invariant deviation before launching subsequent fresh sessions.
