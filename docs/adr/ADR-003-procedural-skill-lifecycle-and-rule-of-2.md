# ADR-003: Procedural Skill Lifecycle & The Rule of 2 Self-Authoring

* **Status:** Accepted
* **Date:** 2026-09-15
* **Component:** core
* **Supersedes:** None

## Context and Problem Statement
Architectural invariants define the boundaries ("WHAT must never be violated"), but do not provide operational playbooks for execution ("HOW to perform domain-specific refactoring, migrations, or database queries"). Without standardized procedural skills, agents spend unnecessary cycles re-deriving execution steps, leading to variability in code quality and operational friction.

## Decision Drivers
* Dynamic capability injection based on modified files and active architectural domains.
* Autonomous system evolution: self-improving agents that crystallize repeatable procedures into permanent skills.
* Modular reusability across projects and developer teams.

## Considered Options
1. Embedding operational instructions into every ADR or Spec.
2. Relying solely on default agent base models without specialized tools.
3. Decoupled procedural skills with dynamic compiler routing and the "Rule of 2" crystallization mandate.

## Decision Outcome
Chosen option: **Dynamic Skill Routing & The Rule of 2 Self-Authoring** (Option 3).
- The pre-flight compiler maps active domains (`core`, `api`, `web`, `specs`, `docs`) to recommended skills.
- The agent activates relevant `SKILL.md` playbooks during Phase 2/3 of task intake.
- If a missing capability is detected, the agent discovers it via `find-skills`.
- **The Rule of 2:** Whenever an operational sequence, command pattern, or diagnostic workflow repeats $\ge 2$ times without a formalized skill, the agent is mandated to invoke `skill-creator` and crystallize the pattern into a permanent reusable skill.

## Invariants
- Pre-flight compiled active rules must always output a `RECOMMENDED PROCEDURAL SKILLS` block.
- Operational workflows repeated >= 2 times must be proposed for crystallization into an agent skill.
- Skills must follow standard agent skill format (`SKILL.md` with YAML metadata).
