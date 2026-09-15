# ADR-006: Multi-Harness Session Distillation & Context Compaction

* **Status:** Accepted
* **Date:** 2026-09-15
* **Component:** core
* **Supersedes:** None

## Context and Problem Statement
Long-running AI agent sessions (e.g. 100-300+ turns spanning days of development) accumulate tens of megabytes of raw conversational and tool execution transcripts. As conversation history grows, LLM context windows suffer from attention degradation, high token costs, and loss of original architectural intent. Furthermore, modern development workflows leverage heterogeneous AI CLI harnesses (`agy`, `claude`, `codex`, `aider`), each with distinct execution models.

## Decision Drivers
* Enable continuous single-session development without loss of architectural memory or performance degradation.
* Provide streaming, lightweight distillation (<100MB RAM, zero external dependencies) to compact transcripts into actionable invariants and milestones.
* Support multi-agent harness interoperability so projects can seamlessly alternate between `agy`, `claude`, `codex`, or headless CI agents.
* Guarantee that every agent execution starts with fresh, compiled active rules (`.context/active_rules.md`).

## Considered Options
1. Truncate conversation history arbitrarily without structured extraction.
2. Rely on cloud-hosted proprietary session memory APIs.
3. Local streaming Session Distiller and multi-harness orchestration runner (`run_b_sdd.sh`) native to B-SDD.

## Decision Outcome
Chosen option: **Local Streaming Session Distiller & Multi-Harness Runner** (Option 3).
1. **Streaming Distiller (`src/core/session_distiller.py`):**
   - Line-by-line parsing of JSON Lines transcripts (AGY `transcript.jsonl`, expandable to Claude/Codex session logs).
   - Extracts cleansed user directives, modified file seams, and tool frequency metrics.
   - Distills raw transcripts into `.context/session_distillation.md` and structured JSON.
2. **Multi-Harness Orchestration Runner (`run_b_sdd.sh`):**
   - Pre-flight: runs B-SDD rule compilation (`b-sdd compile`) and fitness gates.
   - Context injection: loads compiled active rules and distilled milestones.
   - Harness adapter: selects and executes the configured harness (`agy`, `claude`, `codex`, or `auto`-detected).

## Invariants
- Distillation must operate strictly using Python Standard Library streaming (no multi-megabyte whole-file JSON loading into memory).
- The resulting `.context/session_distillation.md` must be concise and actionable, keeping active invariants prominently visible.
- `run_b_sdd.sh` must remain cross-platform POSIX compliant and cleanly support `--agent <name>`.
