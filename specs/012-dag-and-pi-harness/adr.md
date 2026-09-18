# ADR-013: Utopia DB Bitemporal DAG View, Headless Pi Harness Orchestration & Dual-Contour Ingestion

* **Status:** Accepted
* **Date:** 2026-09-18
* **Component:** core, server, ui
* **Supersedes:** None

## Context and Problem Statement
The B-SDD Developer Workbench requires interactive visibility into historical and active decision dependencies stored in Utopia DB (:9922). Furthermore, executing implementation-level tasks requires autonomous execution without risking architectural regressions. Finally, onboarding legacy or external codebases (brownfield projects) requires an automated dual-contour ingestion engine to map AST dependencies and synthesize initial MADR 3.0 records.

## Decision Drivers
* Bitemporal DAG transparency: dynamically visualize `supersedes`, `depends-on`, and `conflicts-with` edges with $T_v$ (Valid Time) filtering in Zone D.
* Headless Pi Harness isolation: delegate Action node implementation to `@earendil-works/pi` with deterministic token-compressed `AGENTS.md` (<500 words) while strictly forbidding graph mutations.
* Dual-contour ingestion: use GitNexus AST mapping to bootstrap base architectural decisions and standard controller scaffolds.
* 100% Python 3 Standard Library in `src/` (ADR-002) and $C=0$ planar DRAKON flows (ADR-008).

## Considered Options
1. Client-side heavy graph rendering with direct database connections (violates isolation and credentials security).
2. Pure server-rendered static charts without interactive bitemporal scrubbing (lacks real-time reactivity).
3. Sovereign Proxy Gateway with SVG DAG View, Headless Pi JSONL RPC, and AST-driven MADR bootstrapping (Chosen).

## Decision Outcome
Chosen option: **Option 3: Sovereign Proxy Gateway, Interactive SVG DAG Canvas, Headless Pi Harness RPC & Ingestion Engine**.
1. **Utopia DAG Proxy:** `GET /api/utopia/graph` proxies bitemporal graph records from Utopia DB (`192.168.3.251:9922`) with $T_v/T_t$ filtering.
2. **Zone D Dual-View:** Interactive toggle `[ Cards | DAG View ]` in `TimelineSlider.tsx` rendering `UtopiaDagCanvas.tsx`.
3. **Pi Harness Engine:** `PiHarnessRunner` generates compressed `AGENTS.md` and coordinates execution via subprocess JSONL streaming to SSE.
4. **Brownfield Ingestion:** `POST /api/projects/ingest` triggers GitNexus AST analysis and bootstraps starter MADRs.

## Invariants
- INV-012-01: The generated `AGENTS.md` context must strictly remain under 500 words.
- INV-012-02: Action node leaf bounding ensures graph topology immutability during execution.
- INV-012-03: Pi Harness receives authority only over Action node implementation bodies; modifying DRAKON topology is prohibited.
- INV-012-04: Utopia DAG filter prunes future nodes and flags superseded nodes where `valid_to <= T_v`.
- INV-012-05: Brownfield Ingestion Engine analyzes AST components and synthesizes standard MADR 3.0 records.
