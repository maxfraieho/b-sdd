# ADR-004: AST Impact Graph Routing via GitNexus

* **Status:** Accepted
* **Date:** 2026-09-15
* **Component:** core
* **Supersedes:** None

## Context and Problem Statement
When a developer or agent modifies a file (e.g., `src/adapters/utopia_db.py`), passing rules for unrelated domains (e.g., frontend CSS or mobile push notifications) wastes tokens and dilutes attention. The compiler must selectively activate only the rules and skills pertinent to the modified code's dependency neighborhood.

## Decision Drivers
* Fast, deterministic resolution of modified files to architectural components.
* Dependency-aware upward propagation (e.g. modifying a core model impacts dependent API endpoints).
* Graceful fallback when an external AST index is not yet built.

## Considered Options
1. Flat keyword search on filenames.
2. Direct integration with GitNexus code intelligence graph (`.gitnexus/index.sqlite`).
3. Running a full AST parser over the entire repository on every pre-flight invocation.

## Decision Outcome
Chosen option: **GitNexus Code Intelligence Graph with Deterministic Path Fallback** (Option 2).
The `GitNexusDomainResolver` inspects `.gitnexus/index.sqlite` to trace recursive component edges and upstream symbol impacts. If the database is missing or unindexed, it instantly falls back to deterministic filesystem path matching with zero performance penalty.

## Invariants
- Domain resolution must execute in sub-millisecond time (<1ms).
- Graceful degradation: lack of a GitNexus index must never block or crash rule compilation.
