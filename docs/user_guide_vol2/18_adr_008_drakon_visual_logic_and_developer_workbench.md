# ADR-008: DRAKON Visual Algorithmic Logic & Developer Workbench Integration

* **Status:** Accepted
* **Date:** 2026-09-16
* **Component:** specs
* **Supersedes:** None

## Context and Problem Statement
Unstructured natural language and ambiguous Markdown specifications exhibit high semantic entropy, causing stochastic large language model (LLM) attention drift, hallucinated control flows, and unhandled edge cases in autonomous coding agents. Furthermore, standard diagramming tools (Mermaid, PlantUML) lack formal mathematical graph grammars, permitting topological spaghetti and non-planar line crossings. Finally, human architects lack a unified visual cockpit to observe bitemporal ADR state, trace algorithmic paths, verify mathematical diagram completeness, and orchestrate multi-session sprint handoffs with Human-in-the-Loop (HITL) review.

## Decision Drivers
* Eliminate algorithmic ambiguity by establishing formal visual graph grammars ("Drakon-as-Spec") with deterministic intermediate representations.
* Guarantee bitemporal traceability by directly binding visual flowchart nodes to active Architectural Decision Record (ADR) invariant IDs.
* Prevent topological hallucination by restricting AI coding agents to implementing isolated leaf action bodies without altering control-flow graphs.
* Formalize a 7-Phase HITL State Machine with a synchronous, blocking Human Review Gate and a structured Reject & Branch protocol.
* Provide an interactive, high-density Developer Workbench (`b-sdd-ui`) supporting bitemporal timeline navigation ($T_v$, $T_t$), DRAKON editing, and multi-session sprint dispatching.
* Maintain 100% pure Python Standard Library runtime in `src/drakon/` and guarantee offline local repository parity without mandatory cloud dependencies.

## Considered Options
1. Unstructured text and informal Markdown specifications only (High ambiguity, stochastic drift).
2. Informal flowchart diagrams (PlantUML, Mermaid) without formal execution grammar or topological constraints.
3. DRAKON Algorithmic Logic (Drakon-as-Spec) paired with DRAKON-IR and an Interactive Developer Workbench (`b-sdd-ui`) based on `ai-drakon-scaffolder` (Chosen).

## Decision Outcome
Chosen option: **DRAKON Algorithmic Logic & Developer Workbench** (Option 3).

### 1. Drakon-as-Spec Algorithmic Grammar
Algorithmic workflows in `specs/**/logic.drn` (and `.drakon.json`) must strictly adhere to four foundational DRAKON mathematical rules:
1. **The Vertical Skewer ("Шампур"):** The primary success trajectory ("happy path") is strictly vertical from headline to terminal node on the left-most coordinate.
2. **Right-is-Worse Branching ("Чем правее, тем хуже"):** Normal execution flows downward; deviations, degradation, exceptions, and failovers branch exclusively to the right, ordered monotonically by severity.
3. **Planarity and Zero Line Crossings:** Control-flow edges must never intersect, guaranteeing unambiguous topological parseability.
4. **Silhouette Architecture ("Силуэт"):** Complex algorithms are decomposed into ordered vertical subtrees evaluated strictly left-to-right, eliminating unreachable dead code and unbounded loops.

### 2. DRAKON Intermediate Representation (`DRAKON-IR`)
Visual diagrams are parsed into a canonical JSON AST (`DRAKON-IR`):
* `node_id`: Deterministic UUID identifying the graph element.
* `node_type`: Primitive type (`headline`, `question`, `action`, `silhouette_route`, `end`).
* `label`: Natural-language description indexed in Utopia DB / Tantivy.
* `semantic_binding`:
  - `adr_invariant_id`: Foreign key to an active ADR invariant (e.g. `ADR-004-INV-01`).
  - `utopia_entity_id`: Entity identifier in the corporate world model.
  - `temporal_scope`: Valid-time interval $[V_{start}, V_{end})$ verified against current system time.
* `edges`: Strictly partitioned into `down` (success skewer) and `right` (degradation / branch).

AI code generators are prohibited from altering diagram topology; their generation scope is strictly bounded to the function bodies of `action` nodes.

### 3. Seven-Phase Human-in-the-Loop (HITL) State Machine
Project execution progresses through seven discrete phases:
* **$\Phi_1$ Intent Framing (ADR):** Formulate MADR in Utopia DB with bitemporal horizons (100% HITL).
* **$\Phi_2$ Algorithmic Specification (DRAKON):** Visual algorithmic design adhering to DRAKON grammar (50% HITL).
* **$\Phi_3$ Pre-Flight Compilation:** Validate rules, token budget (<500 words), and latency (<50ms) (0% HITL, automated gate).
* **$\Phi_4$ Phased Code Execution:** Synthesize code for action node leaf bodies via sovereign LLM (0% HITL).
* **$\Phi_5$ Automated Fitness Verification:** Execute pytest architectural fitness suite and AST isolation checks (0% HITL).
* **$\Phi_6$ Human Review Gate:** Blocking inspection of diffs and fitness reports with cryptographic sign-off (100% HITL).
* **$\Phi_7$ Session Distillation & Dynamic Handoff:** Compact transcripts into `.context/next_sprint.md` and `sprint_handoff.json` (20% HITL).

#### Reject & Branch Protocol:
If rejected at $\Phi_6$, a copy-on-write snapshot is recorded at $T_{reject}$, the rejected branch is terminated ($V_{end} = T_{current}$), and downstream execution is initialized with clean context and a minimal negative invariant vector:
$$\Delta C = \{ \text{Invariant}_k \mid \text{Violation}(\text{Invariant}_k, \text{Run}_{prev}) = \text{True} \}$$

### 4. Developer Workbench Architecture (`b-sdd-ui`)
A lightweight, high-density local web cockpit (ported from `ai-drakon-scaffolder`) structured in a 4-zone spatial grid:
1. **Topbar & Dev Cycle Stepper (64px):** Continuous phase tracking ($\Phi_1 - \Phi_7$) with Approve and Reject & Branch controls.
2. **DRAKON Algorithmic Studio (Left 55%):** Interactive visual canvas enforcing grid alignment, non-crossing lines, and invariant binding badges.
3. **Sovereign LLM Copilot Panel (Right 45%):** Model slot selector (vLLM/Ollama on `.184`), token-budget gauge, and streaming execution monitor.
4. **Bitemporal ADR Radar & Timeline Slider (Bottom 120px):** Dual scrubbers for Valid Time ($T_v$) and Transaction Time ($T_t$) visualizing active vs superseded ADRs.
5. **Invariant Inspector Drawer (Right 420px):** Slide-out drawer with hybrid Tantivy + pgvector search across Utopia DB rules.

### 5. Sovereign Execution VPC and Hybrid Topology
* **Sovereign Execution VPC:** Internal network hosting Utopia DB (`.251:9922`) and LLM Gateway (`.184:18880`).
* **Offline Parity:** Workbench operates 100% standalone against local repository metadata (`.context/`, `specs/`, `docs/adr/`).
* **Sovereign Runner Daemon:** Employs outbound mTLS reverse tunnels for optional Appwrite SaaS control-plane telemetry without inbound firewall exposure.

## Invariants
- All DRAKON schemes must strictly satisfy the 4 canonical topological rules: vertical skewer, right-is-worse branching, zero line crossings, and planar silhouette decomposition.
- Core DRAKON parser, schema validator, and AST generators in `src/drakon/` must be 100% pure Python Standard Library with zero third-party dependencies.
- Visual DRAKON decision and action nodes must maintain verifiable semantic bindings to active ADR invariant IDs, rejecting superseded ADRs (`valid_to < NOW`).
- AI code generation agents are strictly restricted to synthesizing leaf action bodies and must never mutate control-flow topology.
- Developer workbench must function in full standalone offline mode against local repository files without requiring external cloud accounts.
- Transitions through the Human Review Gate ($\Phi_6$) require synchronous human sign-off; rejections must trigger the Reject & Branch protocol with negative invariant injection $\Delta C$.
