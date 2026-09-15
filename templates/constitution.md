# Project Constitution (.specify/constitution.md)

## 1. Fundamental System Principles
1. **Spec-Driven Consistency:** All new features, refactors, and core alterations must be preceded by an isolated specification in `specs/<feature-name>/` (spec.md, plan.md, tasks.md).
2. **Architecture Continuity & Supersession:** Architectural changes are authored as ADRs. Obsolete decisions must be explicitly superseded (`Supersedes: ADR-XXX`) and never left as ambiguous conflicting rules.
3. **Procedural Skill Lifecycle (The Rule of 2):** Any operational sequence, command pattern, or diagnostic workflow repeated $\ge 2$ times must be formalized into an autonomous agent skill using `skill-creator`.
4. **Deterministic Pre-Flight Gating:** Agents must run pre-flight rules compilation before writing code to ensure active constraints are loaded into working memory.

## Invariants
- Zero unverified architecture drift: all code commits must strictly conform to active ADR invariants.
- Context density ceiling: compiled prompt snapshots must strictly remain under 500 words.
- Autonomous skill crystallization: patterns repeated >= 2 times must be crystallized into skills.
