# ADR-001: Bitemporal Intent Graph & Transaction Time Horizon

* **Status:** Accepted
* **Date:** 2026-09-15
* **Component:** core
* **Supersedes:** None

## Context and Problem Statement
LLM-based autonomous coding agents suffer from severe architectural drift over long-running development sessions. Traditional prompt injection approaches (.cursorrules, static markdown files) either bloat the context window beyond usable limits or cause contradictions when old decisions are superseded by newer architectural mandates. Vector RAG systems fail probabilistically when old and new decisions share identical semantic vocabulary (e.g. replacing Stripe with QR-bill).

## Decision Drivers
* Mathematical elimination of outdated or superseded architectural rules.
* Zero semantic hallucination or probabilistic retrieval errors.
* Centralized truth synchronized across heterogeneous cluster nodes (workstations, dev servers, DB nodes).

## Considered Options
1. Flat static rule files (.cursorrules / .windsurfrules).
2. Probabilistic vector memory / RAG (Chroma, pgvector).
3. Bitemporal Directed Acyclic Graph (DAG) with valid time and transaction time stored in Utopia DB.

## Decision Outcome
Chosen option: **Bitemporal Directed Acyclic Graph in Utopia DB** (Option 3).
Architectural intents are stored with two time dimensions:
- `valid_from` / `valid_to`: The real-world horizon when a rule or constraint applies to the codebase.
- `system_from` / `system_to`: The immutable transaction time when the record was written to the ledger.
When an ADR supersedes an earlier decision, the supersession edge is explicitly recorded in `intent_store.intent_supersessions`, and the old intent's `valid_to` is atomically updated to `CURRENT_TIMESTAMP`.

## Invariants
- Bitemporal isolation: rules where `valid_to < NOW` must never be compiled into the active agent context.
- Explicit supersession: every superseded decision must maintain a directed graph edge to its replacement.
- Immutable audit ledger: no historical intent records may be physically deleted from the database.
