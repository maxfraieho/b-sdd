# ADR-010: Universal Multi-Project Context and Standard Algorithmic Pipeline Catalog

* **Status:** Accepted
* **Date:** 2026-09-17
* **Component:** core
* **Supersedes:** None

## Context and Problem Statement
The initial implementation of B-SDD was strictly bound to a single local repository directory (`/home/vokov/projects/b-sdd`), preventing software architects from using the developer workbench to manage multiple repositories, connect GitHub accounts, or switch project workspaces. Furthermore, developers lacked a standard library of pre-built, mathematically verified DRAKON algorithms and B-SDD operational engineering pipelines, forcing teams to formulate routine workflows from scratch. A universal software engineering workbench must support project context switching across arbitrary repositories and provide an immutable catalog of standard canonical algorithms.

## Decision Drivers
* Enable universal project management across any local workspace and remote GitHub repository.
* Expose dynamic project switching APIs (`GET /api/projects`, `POST /api/projects/switch`) in the pure Python standard library gateway.
* Provide an immutable, mathematically verified catalog of standard DRAKON algorithmic patterns and B-SDD pipelines (`GET /api/pipelines/catalog`).
* Guarantee 100% planarity (zero line crossings) and bitemporal traceability for all bundled standard templates.
* Maintain universal zero-setup portability with 100% pure standard library in `src/`.

## Considered Options
1. Single-repository lock-in with manual directory paths (Zero multi-project support, high friction).
2. Heavy third-party multi-tenant orchestrators requiring external database clusters and complex cloud setups.
3. Universal Project Adapter & Standard Template Catalog built entirely with Python standard library and responsive frontend modals (Chosen).

## Decision Outcome
Chosen option: **Universal Multi-Project Context and Standard Algorithmic Pipeline Catalog** (Option 3).

### 1. Universal Project Context
The workbench gateway decouples runtime execution from a hardcoded directory:
* Dynamic workspace registry supporting local filesystem repositories and GitHub account integration.
* Topbar project switcher with visual repository status, branch indicators, and instant workspace transition.
* Configuration persistence via `b_sdd.config.json` and standard Git discovery.

### 2. Standard Algorithmic & Pipeline Catalog
A curated library of canonical templates is packaged under `src/drakon/templates/`:
* **B-SDD Engineering Pipelines:**
  - `bsdd_preflight_pipeline.json`: Pre-flight active rules compilation (<50ms, <500w).
  - `tdd_verification_loop.json`: Red-Green-Refactor test cycle with ΔC negative invariant injection.
  - `rule_of_2_crystallizer.json`: Autonomous procedural skill crystallization workflow.
  - `utopia_sync_workflow.json`: Bitemporal intent synchronization with Utopia DB Knowledge Graph.
* **Canonical Algorithmic Patterns:**
  - `drakon_binary_search.json`: Classical binary search adhering to the Vertical Skewer and "Right-is-Worse" branching.
  - `drakon_state_machine.json`: Finite State Machine lifecycle pattern with silhouette decomposition.

## Invariants
- ADR-010-INV-01: B-SDD framework must support universal repository context switching across any local workspace and remote GitHub project.
- ADR-010-INV-02: Framework must provide an immutable catalog of standard canonical DRAKON algorithmic patterns and B-SDD operational engineering pipelines.
- ADR-010-INV-03: All standard pipeline templates must pass 100% mathematical planarity and DAG validity gates before distribution.
- ADR-010-INV-04: Cross-Reference (ADR-015): The standard algorithm catalog seamlessly unifies with B-SDD procedural skills via `<skill_name>.drakon.json` schemas and `CALL_SKILL` composition.

