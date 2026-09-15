# ADR-008: DRAKON Visual Algorithmic Logic & Developer Workbench Integration

* **Status:** Proposed
* **Date:** 2026-09-15
* **Component:** specs
* **Supersedes:** None

## Context and Problem Statement
Describing complex multi-branching business logic, recovery paths, and state transitions in unstructured natural language creates ambiguity for AI agents, resulting in hallucinated edge cases and unhandled exceptions. Furthermore, developers lack a centralized visual interface to observe bitemporal ADR states, verify algorithmic completeness, and steer multi-sprint progress.

## Decision Drivers
* Provide zero-ambiguity algorithmic representations for critical business and agent logic.
* Eliminate visual and logical spaghetti code by adhering to mathematical visual graph grammars.
* Integrate the visual modeling capabilities of `ai-drakon` into the B-SDD ecosystem.
* Provide an intuitive web workbench for human architects to monitor and trigger sprints.

## Considered Options
1. Informal flowchart diagrams (PlantUML, Mermaid) without formal execution grammar.
2. Code-only implementation without algorithmic pre-flight visual contracts.
3. DRAKON Visual Logic (Drakon-as-Spec) paired with an interactive Developer Workbench based on `ai-drakon-scaffolder` (Chosen).

## Decision Outcome
Chosen option: **DRAKON Algorithmic Logic & Developer Workbench** (Option 3).
1. **Drakon-as-Spec (`specs/XXX/logic.drn`):**
   - Critical workflows are modeled following DRAKON rules: the main path is strictly vertical ("the skewer"), branches to the right represent progressively worse/exceptional alternatives, and line crossings are prohibited.
   - B-SDD parser translates DRAKON schemes into deterministic state machines and prompt constraints for AI agents.
2. **ADR to Algorithm Mapping:**
   - Visual nodes in DRAKON schemes map directly to ADR invariants, ensuring that every algorithmic branch satisfies bitemporal constraints.
3. **Developer Workbench (`b-sdd-ui`):**
   - A lightweight local web cockpit porting the UI from `ai-drakon-scaffolder`:
     - Visualizes active vs superseded ADRs in a bitemporal graph.
     - Renders and edits DRAKON schemes.
     - Displays live sprint progression with a 1-click "Launch Next Sprint" runner.

## Invariants
- All DRAKON schemes must be mathematically valid (no unconnected nodes, no crossing lines, complete branch conditions).
- Algorithmic parsers and AST generators in core must remain 100% Python standard library compliant.
- The web workbench must operate offline against local project metadata (`.context/`, `specs/`, `docs/adr/`).
