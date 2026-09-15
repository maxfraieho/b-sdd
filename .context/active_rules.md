# Active Architectural Invariants (B-SDD Framework)
<!-- Auto-compiled by B-SDD Compiler for domains: all components -->
MANDATORY INVARIANTS:
- [GLOBAL] **Bitemporal Architectural Invariants:** System architecture is governed by declarative Architectural Decision Records (ADRs) with bitemporal valid-time horizons (`valid_from` / `valid_to`) and explicit DAG supersession edges. Superseded decisions are mathematically pruned from agent context. (Ref: .specify/constitution.md)
- [GLOBAL] **Deterministic Pre-Flight Compilation:** The agent's working context is prepared before turn 1 via a deterministic pre-flight compiler (<20ms latency) that compresses thousands of pages into an ultra-dense snapshot strictly under 500 words. (Ref: .specify/constitution.md)
- [GLOBAL] **Procedural Skill Lifecycle & Self-Authoring (The Rule of 2):** Procedural skills provide the operational capabilities for executing architectural domains. Any engineering pattern or workflow repeated $\ge 2$ times must be crystallized into an autonomous agent skill via `skill-creator`. (Ref: .specify/constitution.md)
- [GLOBAL] **Static Code Intelligence Graph (GitNexus):** Modified files are mapped to architectural domains and components via Abstract Syntax Tree (AST) impact analysis. (Ref: .specify/constitution.md)
- [GLOBAL] **Zero-Dependency Pure Runtime:** All core compiler and adapter components in `src/` must strictly use the Python Standard Library to ensure universal zero-setup portability across dev servers, containers, and bare-metal nodes. (Ref: .specify/constitution.md)
- [GLOBAL] Bitemporal intent continuity: superseded ADRs and specifications must never be injected into active rules. (Ref: .specify/constitution.md)
- [GLOBAL] Deterministic compile latency: pre-flight rule compilation must execute in under 50ms warm cache. (Ref: .specify/constitution.md)
- [GLOBAL] Strict token budget: compiled prompt snapshots must strictly remain under 500 words. (Ref: .specify/constitution.md)
- [GLOBAL] Zero-dependency runtime: pure standard library in src/ with zero external runtime package requirements. (Ref: .specify/constitution.md)
- [GLOBAL] Autonomous skill crystallization: operational patterns repeated >= 2 times must be crystallized into skills. (Ref: .specify/constitution.md)
- [CORE] Bitemporal isolation: rules where `valid_to < NOW` must never be compiled into the active agent context. (Ref: docs/adr/ADR-001-bitemporal-intent-graph.md)
- [CORE] Explicit supersession: every superseded decision must maintain a directed graph edge to its replacement. (Ref: docs/adr/ADR-001-bitemporal-intent-graph.md)
- [CORE] Immutable audit ledger: no historical intent records may be physically deleted from the database. (Ref: docs/adr/ADR-001-bitemporal-intent-graph.md)
- [CORE] Warm compilation latency must strictly remain under 50 milliseconds. (Ref: docs/adr/ADR-002-deterministic-pre-flight-compilation.md)
- [CORE] Compiled active rules snapshot must strictly remain under 500 words. (Ref: docs/adr/ADR-002-deterministic-pre-flight-compilation.md)
- [CORE] All code in `src/core/` must be 100% pure Python Standard Library. (Ref: docs/adr/ADR-002-deterministic-pre-flight-compilation.md)
- [CORE] Pre-flight compiled active rules must always output a `RECOMMENDED PROCEDURAL SKILLS` block. (Ref: docs/adr/ADR-003-procedural-skill-lifecycle-and-rule-of-2.md)
- [CORE] Operational workflows repeated >= 2 times must be proposed for crystallization into an agent skill. (Ref: docs/adr/ADR-003-procedural-skill-lifecycle-and-rule-of-2.md)
- [CORE] Skills must follow standard agent skill format (`SKILL.md` with YAML metadata). (Ref: docs/adr/ADR-003-procedural-skill-lifecycle-and-rule-of-2.md)
- [CORE] Domain resolution must execute in sub-millisecond time (<1ms). (Ref: docs/adr/ADR-004-ast-impact-graph-routing.md)
<!-- truncated: active rules exceeded word limit, lowest priority rules dropped -->

RECOMMENDED PROCEDURAL SKILLS:
- Active Skills: architecture-designer, b-sdd, find-skills, safe-refactor, skill-creator
- Skill Guidance: Use 'find-skills' if capability missing, or 'skill-creator' if process repeats >=2 times.
