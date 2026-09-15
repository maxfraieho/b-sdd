# ADR-002: Deterministic Pre-Flight Compilation & Sub-500 Word Budget

* **Status:** Accepted
* **Date:** 2026-09-15
* **Component:** core
* **Supersedes:** None

## Context and Problem Statement
When an AI agent is invoked, passing hundreds of pages of documentation, specifications, and previous ADRs introduces context degradation ("needle-in-a-haystack" degradation, prompt bloat, high token costs, and slow generation). The agent needs a razor-sharp, dense summary of mandatory invariants before executing any task.

## Decision Drivers
* Instantaneous startup: pre-flight execution must take under 50ms so developers feel zero lag.
* Strict density ceiling: compiled active rules must strictly remain under 500 words to conserve token context.
* Zero third-party runtime dependencies in core execution.

## Considered Options
1. On-demand dynamic LLM summarization of active documents before each turn.
2. Naive concatenation of all markdown files.
3. Deterministic regex-based parser with local SQLite hashing and word-budget truncation.

## Decision Outcome
Chosen option: **Deterministic Pre-Flight Compiler with SQLite Caching** (Option 3).
The compiler scans `.specify/constitution.md`, `docs/adr/*.md`, and `specs/**/spec.md`. It extracts structured invariants, checks MD5 hashes against local `.context/intents_cache.sqlite`, and deterministically truncates lower-priority rules to fit within a strict 500-word ceiling.

## Invariants
- Warm compilation latency must strictly remain under 50 milliseconds.
- Compiled active rules snapshot must strictly remain under 500 words.
- All code in `src/core/` must be 100% pure Python Standard Library.
