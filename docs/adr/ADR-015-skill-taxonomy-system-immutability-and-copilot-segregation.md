# ADR-015: B-SDD System Skills Taxonomy, Immutability & Copilot Segregation, and Bi-directional Visual Round-Trip Editing

* **Status:** Accepted
* **Date:** 2026-09-22
* **Component:** core
* **Supersedes:** None

## Context and Problem Statement
Under the B-SDD paradigm, skills located in `~/.agents/skills/` and workspace mirrors provide operational capabilities for autonomous software engineering agents. However, prior to this ADR:
1. All skills were treated uniformly without distinction between universal meta-cognitive infrastructure skills (e.g. `b-sdd`, `b-sdd-sprint-closure`, `drakon-compiler`, `utopia-intent-ledger`, `laya-decision-router`) and project-specific domain skills.
2. Sprint closure routines, autonomous pruning scripts, and LLM cleanup passes posed a critical risk of deleting or degrading core system skills.
3. Skills were stored purely as markdown (`SKILL.md`), lacking visual algorithmic representation in DRAKON diagrams. This prevented architects from visually editing skill control flow, inspecting cross-skill composition (`CALL_SKILL`), or verifying algorithmic planarity ($X=0, C=0$).
4. Copilot agents could inadvertently mutate system-level capabilities during ordinary feature sprints.

A formal taxonomy, strict immutability barriers, bi-directional visual round-trip editing via DRAKON schemas, and copilot segregation are required to safeguard and orchestrate the B-SDD skill ecosystem.

## Decision Drivers
* Strict architectural taxonomy distinguishing immutable system skills (`SYSTEM_SKILL`) from project domain skills (`PROJECT_SKILL`).
* Ironclad non-deletion and mutation safeguards for system skills across all sprint closures and automated tools.
* Bi-directional Visual DRAKON Invariant extending the Rule of 2 (ADR-003): every skill directory must contain `<skill_name>.drakon.json` alongside `SKILL.md`.
* Visual round-trip editing in Astryx Cockpit / DrakonStudio: changes in the DRAKON visual canvas synchronize to `SKILL.md`, and markdown edits synchronize to the schema.
* Explicit cross-skill composition using `CALL_SKILL` macro-nodes aligned to the vertical skewer ($X=0, C=0$).
* Copilot segregation: project copilots are isolated to project domain skills and cannot alter system-level execution logic without explicit meta-sprints.
* 100% Pure Python Standard Library implementation in `src/core/` (ADR-002).

## Considered Options
1. Retain flat unstructured markdown skills without visual representation (High risk of skill mutation, zero visual traceability).
2. External visual editor plugin with binary diagram formats (Violates zero-setup, pure stdlib, and git-native storage).
3. First-class B-SDD System Skills Taxonomy, Immutability Barrier, and Bi-directional Visual DRAKON Round-Trip Bridge (Chosen).

## Decision Outcome
Chosen option: **B-SDD System Skills Taxonomy, Immutability & Copilot Segregation, and Bi-directional Visual Round-Trip Editing** (Option 3).

### 1. Taxonomy & Frontmatter Invariant
Every skill's `SKILL.md` frontmatter must define its classification:
```yaml
---
name: b-sdd
description: Enforces bitemporal architectural invariants, ADR compliance, and pre-flight compilation under the B-SDD framework.
type: SYSTEM_SKILL  # SYSTEM_SKILL | PROJECT_SKILL
category: bssd-system-skill
immutable: true     # Mandatory true for SYSTEM_SKILL
---
```
- **SYSTEM_SKILL**: Foundational meta-cognitive engine skills (`b-sdd`, `b-sdd-sprint-closure`, `drakon-compiler`, `laya-decision-router`, `utopia-intent-ledger`, `session-distiller`, `safe-refactor`, `surgical-patch`, `code-reviewer`, `test-driven-development`, `diagnosing-bugs`, etc.).
- **PROJECT_SKILL**: Domain-specific skills authored or modified during normal project development.

### 2. Immutability & Non-Deletion Barrier
Sprint closures (`b_sdd_sprint_closure.py`), automated pruning scripts, and LLM cleanup passes must enforce an unconditional guard:
- Any deletion, renaming, or unauthorized modification of a `SYSTEM_SKILL` or any skill with `immutable: true` triggers an immediate invariant violation failure (`ADR-015-INV-02`).
- System skills are permanent, immutable foundational infrastructure.

### 3. Bi-directional Visual DRAKON Invariant (Rule of 2 Extension)
Every skill directory in `~/.agents/skills/<skill_name>/` and repository mirrors must maintain two paired artifacts:
1. `SKILL.md`: Human and LLM readable procedural playbook and instruction set.
2. `<skill_name>.drakon.json`: Machine-executable DRAKON-IR schema adhering to ADR-008.

The DRAKON schema defines:
- The algorithm's control flow on the vertical skewer ($X=0, C=0$).
- Condition branches (`question`) following the "Right-is-Worse / Right-is-Alternative" rule.
- Cross-skill invocations via `CALL_SKILL` nodes (`insertion` or `action` with `skill_id` binding).
- Text instructions, prompts, and contract assertions.

### 4. Visual Round-Trip Editing in Astryx Cockpit
The workbench gateway (`src/server/workbench_server.py`) provides REST endpoints for visual round-trip editing:
- `GET /api/skills`: Returns `SkillDTO` list partitioned by taxonomy.
- `GET /api/skills/{name}/drakon`: Returns the visual DRAKON schema. If `<name>.drakon.json` does not exist, the visual bridge synthesizes a canonical planar schema from `SKILL.md`.
- `PUT /api/skills/{name}/drakon`: Saves visual canvas modifications to `<name>.drakon.json` and updates the instruction flow in `SKILL.md`.

### 5. Copilot Segregation
- **Universal System Copilot Plane**: Governs system-level workflows using `SYSTEM_SKILL` components.
- **Project Domain Copilot Plane**: Restricted to project workspace and `PROJECT_SKILL` domain logic, preventing unintended mutations to core engineering standards.

## Invariants
- **ADR-015-INV-01 (Taxonomy & Frontmatter):** Every skill must declare its type (`SYSTEM_SKILL` or `PROJECT_SKILL`) in `SKILL.md` frontmatter. System skills must include `category: bssd-system-skill` and `immutable: true`.
- **ADR-015-INV-02 (Immutability & Non-Deletion):** Sprint closures, cleanup routines, and autonomous scripts are strictly prohibited from deleting, renaming, or pruning `SYSTEM_SKILL` entries.
- **ADR-015-INV-03 (Bi-directional Visual DRAKON / Rule of 2):** Every skill directory must contain `<skill_name>.drakon.json` alongside `SKILL.md`.
- **ADR-015-INV-04 (Planar Skewer & Skill Composition):** Visual skill schemas must satisfy 100% mathematical planarity ($C=0$) with the main spine on the vertical skewer ($X=0$). Cross-skill links must use `CALL_SKILL` semantics.
- **ADR-015-INV-05 (Copilot Segregation):** Project-level copilot activities cannot mutate system skills without an explicit architectural meta-sprint.
- **ADR-015-INV-06 (Tripartite Skill Specification):** Cross-Reference (ADR-016): The internal structure of skills must adhere to the Tripartite Standard, embedding canonical Algorithmic Pseudocode in `SKILL.md` as the primary logic structure isomorphic to the DRAKON schema.

