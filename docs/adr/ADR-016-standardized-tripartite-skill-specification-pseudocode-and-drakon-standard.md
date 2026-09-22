# ADR-016: Standardized Tripartite Skill Specification, Algorithmic Pseudocode & Visual DRAKON Round-Trip Standard

* **Status:** Accepted
* **Date:** 2026-09-22
* **Component:** core
* **Supersedes:** None

## Context and Problem Statement
In previous iterations of B-SDD and agent frameworks (Claude Code, AGY, Codex), procedural skills were stored as free-form Markdown (`SKILL.md`). While ADR-003 established the Rule of 2 for procedural crystallization and ADR-015 introduced the taxonomy and `.drakon.json` file pair, the internal structure of skills remained unstandardized:
1. Skills used diverse formatting styles, missing explicit preconditions, error degradation paths, or structured control flow.
2. Natural language instructions in `SKILL.md` are prone to non-deterministic interpretation by LLMs, leading to execution drift, skipped validation steps, and unhandled failure modes.
3. While DRAKON diagrams (`<skill_name>.drakon.json`) capture algorithmic topology visually, developers and autonomous agents need a standardized, unambiguous textual representation of the algorithm inside `SKILL.md` to guide execution when viewing or editing code textually.
4. There was no formal contract ensuring that textual skill logic and visual DRAKON schemas are mathematically isomorphic.

A comprehensive B-SDD Skill Specification Standard is required to formalize the Tripartite Skill Architecture, establish Algorithmic Pseudocode as the primary structural logic principle, and guarantee round-trip synchrony with DRAKON visual editors.

## Decision Drivers
* Standardized Tripartite Skill Architecture: Every active skill consists of a unified triad: `SKILL.md` (Manifest + Narrative + Pseudocode), `<skill_name>.drakon.json` (Visual Algorithmic Twin), and optional executable harnesses (`scripts/` / tests).
* **Algorithmic Pseudocode as the Primary Structural Principle:** Every skill must contain a deterministic, structured pseudocode block that acts as the textual isomorphic twin of the visual DRAKON schema.
* Deterministic Agent Execution: Agents parsing `SKILL.md` follow the explicit algorithmic control flow (`BEGIN/END`, `ASSERT`, `IF/ELSE/FI`, `BRANCH_RIGHT`, `CALL_SKILL`, `HALT_AND_DEGRADE`) rather than guessing execution order from prose.
* Bi-directional Visual Verification: Human architects can review, edit, or generate skills via Astryx Cockpit / DrakonStudio; the visual graph and pseudocode synchronize bi-directionally without drift.
* Explicit Skill Composition: Inter-skill invocations (`CALL_SKILL`) must be explicitly declared in both YAML frontmatter (`invoked_skills`) and the pseudocode/DRAKON flow.
* Strict Backward Compatibility & Pure Python Standard Library (ADR-002).

## Considered Options
1. Retaining unstructured markdown with informal bullet points (High hallucination risk, no algorithmic verification).
2. Requiring executable Python scripts for all skills without markdown (Removes promptability, limits agent introspection, complicates zero-dependency environments).
3. Standardized Tripartite Skill Architecture with Algorithmic Pseudocode and Visual DRAKON Twin (Chosen).

## Decision Outcome
Chosen option: **Standardized Tripartite Skill Architecture, Algorithmic Pseudocode & Visual DRAKON Round-Trip Standard** (Option 3).

### 1. The Tripartite Skill File Layout
Every active skill folder under `~/.agents/skills/<skill-name>/` (and workspace mirrors) must strictly follow the canonical structure:
```text
~/.agents/skills/<skill-name>/
├── SKILL.md                          # Mandatory: Manifest, Narrative, Algorithmic Pseudocode
├── <skill-name>.drakon.json          # Mandatory: Editable Planar DRAKON-IR Schema (X=0, C=0)
└── scripts/                          # Optional: Pure stdlib helper scripts, CLI tools, tests
```

### 2. Mandatory Structural Sections of `SKILL.md`
Every `SKILL.md` must contain four sequenced sections:

#### Section A: Standard YAML Frontmatter
```yaml
---
name: <skill-name>
description: <Concise 1-2 sentence description of capability and scope>
type: SYSTEM_SKILL | PROJECT_SKILL
category: bssd-system-skill | <domain-category>
immutable: true | false
invoked_skills: [<skill-1>, <skill-2>]
---
```

#### Section B: Architectural Context & Negative Invariants
- Declares WHAT invariants must never be broken during execution.
- Binds the skill to applicable ADRs and constitutional constraints.

#### Section C: Canonical Algorithmic Pseudocode (Primary Logic Structure)
A structured, unambiguous pseudocode block defining the algorithmic spine:
```text
ALGORITHM Execute<SkillName>(params: Context)
BEGIN
    TRY
        ASSERT PreconditionsSatisfied(params)
        
        STEP 1: Primary Action on Vertical Skewer (X=0)
        EXECUTE Operation(...)
        
        STEP 2: Conditional Evaluation
        IF ConditionHolds(...) THEN
            CONTINUE along Skewer (X=0)
        ELSE
            BRANCH_RIGHT(X=4.0): Alternative / Degradation Path
            CALL_SKILL(fallback-skill, params)
            IF FallbackFailed THEN
                HALT_AND_DEGRADE("Reason")
            FI
        FI
        
        STEP 3: Cross-Skill Composition
        CALL_SKILL(target-skill, params)
        
        STEP 4: Verification & Telemetry
        ASSERT VerificationPassed(...)
        EMIT_TELEMETRY(status="COMPLETED")
        RETURN Success
    CATCH Error AS e
        LOG_CRITICAL("Skill execution failed: " + e.Message)
        HALT_AND_DEGRADE(e.Message)
    END
END
```

#### Section D: Visual DRAKON Synchronization Anchor & Operational Guide
- Contains the `<!-- DRAKON_VISUAL_FLOW_START -->` anchor listing nodes.
- Provides concrete CLI commands, parameters, file templates, and environment prerequisites.

### 3. The Visual DRAKON Algorithmic Twin (`<skill_name>.drakon.json`)
- Strict compliance with ADR-008: Vertical Skewer $X=0, C=0$ for the primary success path; alternative/degradation branches positioned strictly to the right ($X > 0$).
- Cross-skill orchestration nodes typed as `insertion` or annotated with `semantic_binding: {"call_skill": "<name>"}`.
- Editable visually in Astryx Cockpit / DrakonStudio with round-trip synchronization to `SKILL.md`.

## Invariants
- **ADR-016-INV-01 (Tripartite Skill Invariant):** Every active skill must contain both `SKILL.md` and `<skill_name>.drakon.json`.
- **ADR-016-INV-02 (Algorithmic Pseudocode Invariant):** Every `SKILL.md` must include a formal `ALGORITHM` pseudocode block defining its control flow, condition branches, and degradation paths.
- **ADR-016-INV-03 (Isomorphism Invariant):** The algorithmic pseudocode in `SKILL.md` and the visual nodes in `<skill_name>.drakon.json` must be strictly isomorphic — sharing identical step identifiers, branching conditions, and `CALL_SKILL` invocations.
- **ADR-016-INV-04 (Immutability & Integrity Guard):** Automated sprint closures and scripts must verify that all system skills comply with the tripartite format before allowing commit or sealing.
