# B-SDD Mega-ADR Master Architecture Ledger

> **Canonical Warm-Tier Architectural Source of Truth (SSoT)**  
> **Ecosystem:** B-SDD (Bitemporal Spec-Driven Development) & Astryx Cockpit  
> **Normative Framework:** ADR-001 (WORM Ledger), ADR-002 (Pure Stdlib Core), ADR-005 (<500 Words Active Rules), ADR-010 (Tripartite Ontology), ADR-015 (Skill Taxonomy & Immutability), ADR-016 (Tripartite Skill Architecture & Pseudocode Standard).  
> **Cold Tier Backing:** Utopia DB WORM (:9622), Google Drive Permanent Telemetry Archive (`1UUyflLo1LZrK-2r9b957elyVxaxZmCge`).

---

## 1. Overview & Architectural Principles

The B-SDD framework operates as a high-fidelity, autonomous, skill-driven engineering architecture.  
To resolve the *Context Explosion vs Amnesia Dilemma*, all architecture decision records (ADRs) are consolidated into this master cumulative ledger, categorized strictly under the **Tripartite Ontology (ADR-010)**:
1. **DataADR:** Data schemas, DTO serialization contracts, database migrations, and bitemporal WORM storage semantics.
2. **SkillADR:** Autonomous agent procedural capabilities, DRAKON planar graphs, algorithmic pseudocode, and skill taxonomy.
3. **SpecADR:** Pre-commit risk gates, compiler latency SLAs, verification bounds, and system invariant rules.

---

## 2. Category I: DataADR (Data Schemas & Ledger Contracts)

### [DataADR-001] Bitemporal Architectural Invariants & WORM Ledger
- **Status**: ACTIVE
- **Valid Time**: `2026-09-15T00:00:00Z` .. `INFINITY`
- **Component**: `src/adapters/utopia_db.py`, `src/core/compiler.py`
- **Core Invariants**:
  - System architecture is governed by declarative Architectural Decision Records (ADRs) with bitemporal valid-time horizons (`valid_from` / `valid_to`) and explicit DAG supersession edges.
  - Superseded decisions are mathematically pruned from active context.
  - No intent record is physically deleted; all state mutations append immutable records to Utopia DB WORM.

### [DataADR-002] Zero-Dependency Pure Stdlib Runtime & Deterministic Compilation
- **Status**: ACTIVE
- **Valid Time**: `2026-09-15T00:00:00Z` .. `INFINITY`
- **Component**: `src/core/`, `src/cli/`
- **Core Invariants**:
  - All core compiler and adapter components in `src/` must strictly use the Python Standard Library (ADR-002).
  - Pre-flight rule compilation must execute in under 50ms warm cache (< 20ms baseline).

### [DataADR-010] Tripartite ADR Ontology & Universal Classification
- **Status**: ACTIVE
- **Valid Time**: `2026-09-17T00:00:00Z` .. `INFINITY`
- **Component**: `src/core/dto/`, `docs/ADR/`
- **Core Invariants**:
  - Every architectural decision and sprint delta must be classified into DataADR, SkillADR, or SpecADR.
  - Cross-domain references must preserve explicit category prefixes.

### [DataADR-013] Utopia DAG Visualization & Bitemporal Graph State
- **Status**: ACTIVE
- **Valid Time**: `2026-09-18T00:00:00Z` .. `INFINITY`
- **Component**: `src/adapters/utopia_db.py`, `b-sdd-ui/`
- **Core Invariants**:
  - Valid time slices ($T_v$) and transaction time logs ($T_x$) must be visualizable in Astryx Cockpit Timeline Radar.

---

## 3. Category II: SkillADR (Autonomous Skills & DRAKON Visual Standard)

### [SkillADR-003] Procedural Skill Lifecycle & The Rule of 2
- **Status**: ACTIVE (Extended by ADR-015 and ADR-016)
- **Valid Time**: `2026-09-15T00:00:00Z` .. `INFINITY`
- **Component**: `~/.agents/skills/`
- **Core Invariants**:
  - Any engineering pattern or workflow repeated $\ge 2$ times must be crystallized into an autonomous agent skill via `skill-creator`.
  - Skills must follow standard agent format (`SKILL.md` with YAML metadata).

### [SkillADR-006] Multi-Harness Session Distillation & Context Compaction
- **Status**: ACTIVE
- **Valid Time**: `2026-09-15T10:00:00Z` .. `INFINITY`
- **Component**: `src/core/session_distiller.py`, `~/.agents/skills/session-distiller/`
- **Core Invariants**:
  - Long conversational sessions must be distilled into structured intelligence before context resets.

### [SkillADR-008] DRAKON Visual Logic & Developer Workbench
- **Status**: ACTIVE (Extended by ADR-016)
- **Valid Time**: `2026-09-16T16:00:00Z` .. `INFINITY`
- **Component**: `src/core/drakon/`, `b-sdd-ui/`
- **Core Invariants**:
  - Planar visual logic strictly along the vertical skewer $X=0.0$ ($C=0$).
  - Degradation and error handling branches directed strictly rightward at $X=4.0$.
  - [SUPERSEDED BY: ADR-016 for skill pseudocode isomorphism].

### [SkillADR-015] Skill Taxonomy, System Immutability & Copilot Segregation
- **Status**: ACTIVE
- **Valid Time**: `2026-09-22T00:00:00Z` .. `INFINITY`
- **Component**: `src/core/dto/skills.py`, `~/.agents/skills/`
- **Core Invariants**:
  - Binary classification: `SYSTEM_SKILL` vs `PROJECT_SKILL`.
  - Non-Deletion Invariant: System skills cannot be modified or deleted by user-space actions; mutations require explicit operator escalation.
  - Dual location: `~/.agents/skills/<name>/` and `.agents/skills/<name>/`.

### [SkillADR-016] Tripartite Skill Architecture, Algorithmic Pseudocode & Visual DRAKON
- **Status**: ACTIVE
- **Valid Time**: `2026-09-22T00:00:00Z` .. `INFINITY`
- **Component**: `~/.agents/skills/`, `src/core/intent_verification/`
- **Core Invariants**:
  - Tripartite layout for every skill: `SKILL.md` + `<skill>.drakon.json` + executable scripts/tools.
  - `SKILL.md` must include `<!-- ALGORITHMIC_PSEUDOCODE_START -->` block with formal `ALGORITHM Execute...`.
  - Isomorphism: 100% 1-to-1 match between pseudocode control structures and `.drakon.json` nodes.

---

## 4. Category III: SpecADR (Gates, Constraints & Verification Bounds)

### [SpecADR-004] AST Impact Graph Routing & Selective Verification
- **Status**: ACTIVE
- **Valid Time**: `2026-09-15T00:00:00Z` .. `INFINITY`
- **Component**: `src/core/diff_risk_gatekeeper.py`, `GitNexus`
- **Core Invariants**:
  - Modified files are mapped to architectural components via Abstract Syntax Tree (AST) impact analysis.

### [SpecADR-005] Active Rules Token Budget (< 500 Words Invariant)
- **Status**: ACTIVE
- **Valid Time**: `2026-09-15T00:00:00Z` .. `INFINITY`
- **Component**: `.context/active_rules.md`, `tests/test_architecture_fitness.py`
- **Core Invariants**:
  - Compiled prompt snapshot in `.context/active_rules.md` must strictly remain under 500 words (currently 464 words).

### [SpecADR-007] Multi-Session Sprint Chaining & Handoff Protocol
- **Status**: ACTIVE
- **Valid Time**: `2026-09-16T15:00:00Z` .. `INFINITY`
- **Component**: `docs/HANDOFF_PLANNING_PROTOCOL.md`
- **Core Invariants**:
  - Discrete phase chaining: Phase Φ1 (Contracts) -> Phase Φ2 (Red TDD) -> Phase Φ3-5 (Green) -> Phase Φ6 (Validation) -> Phase Φ7 (Distillation & Transit Purge).

### [SpecADR-012] Production Deployment & Telemetry Instrumentation
- **Status**: ACTIVE
- **Valid Time**: `2026-09-17T16:00:00Z` .. `INFINITY`
- **Component**: `scripts/deploy_cloudflare_pages.sh`, `b-sdd-ui/`
- **Core Invariants**:
  - Astryx Cockpit UI is continuously deployable to Cloudflare Pages (`b-sdd-ui.pages.dev`).
  - Health gateway exposed at `bsdd.exodus.pp.ua/api/health`.

### [SpecADR-014] Laya System 1 Fast Decision Engine & Circuit Breaker
- **Status**: ACTIVE
- **Valid Time**: `2026-09-22T08:00:00Z` .. `INFINITY`
- **Component**: `src/core/laya_client.py`, `Pixel 7 :9623`
- **Core Invariants**:
  - Sub-40ms non-autoregressive decision classification on Pixel 7 Podroid.
  - Circuit breaker: automatic fallback to local AST heuristics if Laya is unreachable.

---

## 5. Cumulative Sprint Distillation Ledger

### Sprint 030 Knowledge Delta
- **Commit Hash**: `97527e2a632b84cf8295e7d40760abe659cb53aa`
- **Timestamp**: `2026-09-22T08:54:00Z`
- **Verified Invariants**:
  - ✓ Fast-Path pre-commit diff risk evaluation executes in ~14ms.
  - ✓ Suspicious dynamic code execution patterns (`eval`, `exec`, `shell=True`) trigger `HALT_FOR_INSPECTION`.
  - ✓ Active rules word count strictly preserved under 500 words (464 words).
- **Tripartite ADR Decisions**:
  - **[DataADR]**: Added `SkillDTO` and `SkillsResponseDTO` schemas in `src/core/dto/skills.py`.
  - **[SkillADR]**: Restored `cloudflare-pages-expert` and established full 59 skills standardization.
  - **[SpecADR]**: Implemented Vector 2 Fast-Path Diff Risk Gatekeeper in `src/core/diff_risk_gatekeeper.py`.
- **Summary**: Delivered Vector 2 Fast-Path pre-commit risk gatekeeper with Laya System 1 integration.

### Sprint 031 Knowledge Delta
- **Commit Hash**: `12447d6ec094a034b638bdc7301f5f459495328c`
- **Timestamp**: `2026-09-22T12:08:47.645696+00:00`
- **Verified Invariants**:
  - ✓ [INVARIANT-1] Vector 3 Intent Verification enforces S_intent >= 0.82 and 0 missing asserts in pre-commit.
  - ✓ [INVARIANT-2] Fast-path pre-commit completes sub-50ms (<40ms SLA) with circuit breaker fallback.
  - ✓ [INVARIANT-3] Cumulative Vault Distiller appends knowledge quantum into B_SDD_MEGA_ADR_MASTER.md.
  - ✓ [INVARIANT-4] Bitemporal WORM ledger record generated with immutable Tx and valid-time interval.
  - ✓ [INVARIANT-5] Active architectural rules strictly constrained to 464 words (< 500 words ADR-005).
- **Tripartite ADR Decisions**:
  - **[DataADR]**: Added IntentGraphDTO, CodeASTSignaturesDTO, and IntentVerificationResultDTO in src/core/dto/intent_verification.py.
  - **[DataADR]**: Added SprintDistillationDTO and WormPayloadDTO in src/core/dto/distillation.py.
  - **[SkillADR]**: Created b-sdd-sprint-distiller system skill with ADR-016 pseudocode and companion planar DRAKON diagram.
  - **[SpecADR]**: Deployed Vector 3 Intent Gatekeeper and updated scripts/install_laya_precommit_hook.sh to dual-gate.
- **Superseded Invariants**:
  - ⚠️ [SUPERSEDED]: Supersedes raw individual sprint report accumulation in SSoT; established B_SDD_MEGA_ADR_MASTER.md warm ledger.
- **Summary**: Distilled quantum from sprint_031_closure_raw.md: 5 invariants, 4 ADR deltas.
