# B-SDD Framework Constitution (.specify/constitution.md)

## 1. Fundamental System Principles
1. **Bitemporal Architectural Invariants:** System architecture is governed by declarative Architectural Decision Records (ADRs) with bitemporal valid-time horizons (`valid_from` / `valid_to`) and explicit DAG supersession edges. Superseded decisions are mathematically pruned from agent context.
2. **Deterministic Pre-Flight Compilation:** The agent's working context is prepared before turn 1 via a deterministic pre-flight compiler (<20ms latency) that compresses thousands of pages into an ultra-dense snapshot strictly under 500 words.
3. **Procedural Skill Lifecycle & Self-Authoring (The Rule of 2):** Procedural skills provide the operational capabilities for executing architectural domains. Any engineering pattern or workflow repeated $\ge 2$ times must be crystallized into an autonomous agent skill via `skill-creator`.
4. **Static Code Intelligence Graph (GitNexus):** Modified files are mapped to architectural domains and components via Abstract Syntax Tree (AST) impact analysis.
5. **Zero-Dependency Pure Runtime:** All core compiler and adapter components in `src/` must strictly use the Python Standard Library to ensure universal zero-setup portability across dev servers, containers, and bare-metal nodes.

## Invariants
- Bitemporal intent continuity: superseded ADRs and specifications must never be injected into active rules.
- Deterministic compile latency: pre-flight rule compilation must execute in under 50ms warm cache.
- Strict token budget: compiled prompt snapshots must strictly remain under 500 words.
- Zero-dependency runtime: pure standard library in src/ with zero external runtime package requirements.
- Autonomous skill crystallization: operational patterns repeated >= 2 times must be crystallized into skills.
