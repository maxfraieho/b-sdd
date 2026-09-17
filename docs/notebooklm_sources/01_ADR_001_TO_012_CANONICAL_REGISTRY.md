# B-SDD CANONICAL ARCHITECTURE REGISTRY (ADR-001 TO ADR-012)

Authoritative Architectural Decision Records for Bitemporal Spec-Driven Development (B-SDD).
Every system capability, phase transition, constraint, and telemetry probe is governed by these contracts.

## Architectural Invariant Matrix

| ADR | Title | Key Invariants | Enforcement | Penalty on Violation |
|---|---|---|---|---|
| ADR-001 | Bitemporal Intent Graph | Tv/Tt duality, WORM log | Pre-Flight Compiler & Utopia DB | Reject mutation, audit halt |
| ADR-002 | Deterministic Pre-Flight Compiler | <50ms compile, <500 words budget | Pure stdlib compiler, zero third-party deps | Gate Φ2 block |
| ADR-003 | Procedural Skill Lifecycle | Rule of 2, anti-hallucination | Session Distiller | Skill rejection |
| ADR-004 | AST Impact Graph Routing | Exact blast radius, topological order | GitNexus AST analyzer | Unbounded test trigger block |
| ADR-005 | Automated Architectural Fitness Gates | 100% test pass, zero foreign imports | Pytest suite & AST visitor | Gate Φ5 rejection |
| ADR-006 | Multi-Harness Session Distillation | Strict context compaction, <4000 tokens | SessionDistiller & LLM Gateway | Context overflow |
| ADR-007 | Multi-Session Sprint Chaining | Negative invariant vector ΔC, COW branch | sprint_handoff.json protocol | Sprint desynchronization |
| ADR-008 | DRAKON Visual Logic & Workbench | Planar skewer, zero-crossing, HITL cockpit | DrakonValidator, DrakonWidget | Diagram invalidation |
| ADR-009 | Astryx Design System & Universal Cockpit | Swiss high-tech density, 100vh no-body-scroll | CSS custom properties, Boundary isolation | Ergonomic rejection |
| ADR-010 | Universal Multi-Project & Algorithm Catalog | Planar template library, multi-repo switcher | src/drakon/templates, workbench_server | Pipeline rejection |
| ADR-011 | Live GitHub API & Appwrite Realtime Sync | Realtime phase sync via SSE, Ed25519 review | Appwrite Client, GitHub Sync Adapter | HITL desync |
| ADR-012 | Production Deployment & Telemetry | SLA <50ms, Cloudflare Pages live preview | TelemetryCollector, Prometheus/JSON exporter| SLA alert |

---

# ADR-001: Bitemporal Intent Graph & Transaction Time Horizon

* **Status:** Accepted
* **Date:** 2026-09-15
* **Component:** core
* **Supersedes:** None

## Context and Problem Statement
LLM-based autonomous coding agents suffer from severe architectural drift over long-running development sessions. Traditional prompt injection approaches (.cursorrules, static markdown files) either bloat the context window beyond usable limits or cause contradictions when old decisions are superseded by newer architectural mandates. Vector RAG systems fail probabilistically when old and new decisions share identical semantic vocabulary (e.g. replacing Stripe with QR-bill).

## Decision Drivers
* Mathematical elimination of outdated or superseded architectural rules.
* Zero semantic hallucination or probabilistic retrieval errors.
* Centralized truth synchronized across heterogeneous cluster nodes (workstations, dev servers, DB nodes).

## Considered Options
1. Flat static rule files (.cursorrules / .windsurfrules).
2. Probabilistic vector memory / RAG (Chroma, pgvector).
3. Bitemporal Directed Acyclic Graph (DAG) with valid time and transaction time stored in Utopia DB.

## Decision Outcome
Chosen option: **Bitemporal Directed Acyclic Graph in Utopia DB** (Option 3).
Architectural intents are stored with two time dimensions:
- `valid_from` / `valid_to`: The real-world horizon when a rule or constraint applies to the codebase.
- `system_from` / `system_to`: The immutable transaction time when the record was written to the ledger.
When an ADR supersedes an earlier decision, the supersession edge is explicitly recorded in `intent_store.intent_supersessions`, and the old intent's `valid_to` is atomically updated to `CURRENT_TIMESTAMP`.

## Invariants
- Bitemporal isolation: rules where `valid_to < NOW` must never be compiled into the active agent context.
- Explicit supersession: every superseded decision must maintain a directed graph edge to its replacement.
- Immutable audit ledger: no historical intent records may be physically deleted from the database.


---

# ADR-002: Deterministic Pre-Flight Compilation & Sub-500 Word Budget

* **Status:** Accepted
* **Date:** 2026-09-15
* **Component:** core
* **Supersedes:** None

## Context and Problem Statement
When an AI agent is invoked, passing hundreds of pages of documentation, specifications, and previous ADRs introduces context degradation ("needle-in-a-haystack" degradation, prompt bloat, high token costs, and slow generation). The agent needs a razor-sharp, dense summary of mandatory invariants before executing any task.

## Decision Drivers
* Instantaneous startup: pre-flight execution must take under 50ms so developers feel zero lag.
* Strict density ceiling: compiled active rules must strictly remain under 500 words to conserve token context.
* Zero third-party runtime dependencies in core execution.

## Considered Options
1. On-demand dynamic LLM summarization of active documents before each turn.
2. Naive concatenation of all markdown files.
3. Deterministic regex-based parser with local SQLite hashing and word-budget truncation.

## Decision Outcome
Chosen option: **Deterministic Pre-Flight Compiler with SQLite Caching** (Option 3).
The compiler scans `.specify/constitution.md`, `docs/adr/*.md`, and `specs/**/spec.md`. It extracts structured invariants, checks MD5 hashes against local `.context/intents_cache.sqlite`, and deterministically truncates lower-priority rules to fit within a strict 500-word ceiling.

## Invariants
- Warm compilation latency must strictly remain under 50 milliseconds.
- Compiled active rules snapshot must strictly remain under 500 words.
- All code in `src/core/` must be 100% pure Python Standard Library.


---

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


---

# ADR-004: AST Impact Graph Routing via GitNexus

* **Status:** Accepted
* **Date:** 2026-09-15
* **Component:** core
* **Supersedes:** None

## Context and Problem Statement
When a developer or agent modifies a file (e.g., `src/adapters/utopia_db.py`), passing rules for unrelated domains (e.g., frontend CSS or mobile push notifications) wastes tokens and dilutes attention. The compiler must selectively activate only the rules and skills pertinent to the modified code's dependency neighborhood.

## Decision Drivers
* Fast, deterministic resolution of modified files to architectural components.
* Dependency-aware upward propagation (e.g. modifying a core model impacts dependent API endpoints).
* Graceful fallback when an external AST index is not yet built.

## Considered Options
1. Flat keyword search on filenames.
2. Direct integration with GitNexus code intelligence graph (`.gitnexus/index.sqlite`).
3. Running a full AST parser over the entire repository on every pre-flight invocation.

## Decision Outcome
Chosen option: **GitNexus Code Intelligence Graph with Deterministic Path Fallback** (Option 2).
The `GitNexusDomainResolver` inspects `.gitnexus/index.sqlite` to trace recursive component edges and upstream symbol impacts. If the database is missing or unindexed, it instantly falls back to deterministic filesystem path matching with zero performance penalty.

## Invariants
- Domain resolution must execute in sub-millisecond time (<1ms).
- Graceful degradation: lack of a GitNexus index must never block or crash rule compilation.


---

# ADR-005: Automated Architectural Fitness Gates

* **Status:** Accepted
* **Date:** 2026-09-15
* **Component:** core
* **Supersedes:** None

## Context and Problem Statement
Methodologies and architectural conventions tend to rot unless continuously enforced by automated CI/CD gates. Relying on human reviewers or non-deterministic LLM-as-a-judge prompts to verify architectural rules introduces latency and subjectivity.

## Decision Drivers
* Objective, automated pass/fail verification before any commit is pushed.
* Micro-second to sub-second test execution time.
* Zero runtime dependency pollution.

## Considered Options
1. Post-hoc manual code review.
2. LLM-based pull request audit scripts.
3. Automated pytest fitness test suite enforcing architectural invariants as code.

## Decision Outcome
Chosen option: **Automated Pytest Architecture Fitness Suite** (Option 3).
The suite `tests/test_architecture_fitness.py` verifies 5 foundational fitness criteria:
1. **Compilation Latency:** Warm compiler execution time strictly < 50ms.
2. **Context Budget:** Output rule snapshot strictly < 500 words.
3. **Pure Runtime:** Pure Python 3 Standard Library in `src/` (zero third-party dependencies).
4. **Supersession DAG Integrity:** Superseded ADRs are never included in active rule snapshots.
5. **Skill Mapping Integrity:** Recommended procedural skills are accurately mapped to active components.

## Invariants
- All 5 fitness tests must be green before merging or releasing any feature.
- Fitness tests must execute in under 2 seconds total runtime.


---

# ADR-006: Multi-Harness Session Distillation & Context Compaction

* **Status:** Accepted
* **Date:** 2026-09-15
* **Component:** core
* **Supersedes:** None

## Context and Problem Statement
Long-running AI agent sessions (e.g. 100-300+ turns spanning days of development) accumulate tens of megabytes of raw conversational and tool execution transcripts. As conversation history grows, LLM context windows suffer from attention degradation, high token costs, and loss of original architectural intent. Furthermore, modern development workflows leverage heterogeneous AI CLI harnesses (`agy`, `claude`, `codex`, `aider`), each with distinct execution models.

## Decision Drivers
* Enable continuous single-session development without loss of architectural memory or performance degradation.
* Provide streaming, lightweight distillation (<100MB RAM, zero external dependencies) to compact transcripts into actionable invariants and milestones.
* Support multi-agent harness interoperability so projects can seamlessly alternate between `agy`, `claude`, `codex`, or headless CI agents.
* Guarantee that every agent execution starts with fresh, compiled active rules (`.context/active_rules.md`).

## Considered Options
1. Truncate conversation history arbitrarily without structured extraction.
2. Rely on cloud-hosted proprietary session memory APIs.
3. Local streaming Session Distiller and multi-harness orchestration runner (`run_b_sdd.sh`) native to B-SDD.

## Decision Outcome
Chosen option: **Local Streaming Session Distiller & Multi-Harness Runner** (Option 3).
1. **Streaming Distiller (`src/core/session_distiller.py`):**
   - Line-by-line parsing of JSON Lines transcripts (AGY `transcript.jsonl`, expandable to Claude/Codex session logs).
   - Extracts cleansed user directives, modified file seams, and tool frequency metrics.
   - Distills raw transcripts into `.context/session_distillation.md` and structured JSON.
2. **Multi-Harness Orchestration Runner (`run_b_sdd.sh`):**
   - Pre-flight: runs B-SDD rule compilation (`b-sdd compile`) and fitness gates.
   - Context injection: loads compiled active rules and distilled milestones.
   - Harness adapter: selects and executes the configured harness (`agy`, `claude`, `codex`, or `auto`-detected).

## Invariants
- Distillation must operate strictly using Python Standard Library streaming (no multi-megabyte whole-file JSON loading into memory).
- The resulting `.context/session_distillation.md` must be concise and actionable, keeping active invariants prominently visible.
- `run_b_sdd.sh` must remain cross-platform POSIX compliant and cleanly support `--agent <name>`.


---

# ADR-007: Multi-Session Sprint Chaining and Dynamic Handoff Protocol

* **Status:** Accepted
* **Date:** 2026-09-15
* **Component:** core
* **Supersedes:** None

## Context and Problem Statement
Complex software engineering projects require multiple sequential AI agent sessions (sprints). Pre-authoring a static sequence of prompts for future sprints causes a Waterfall trap: downstream sprints fail to account for implementation-level decisions, file structures, and edge cases discovered during upstream execution. Conversely, unbounded long sessions cause severe context degradation. A formal mechanism is needed to connect discrete, fresh-context agent sessions into an uninterrupted, self-propagating development chain.

## Decision Drivers
* Prevent context fatigue by isolating each milestone into a clean session.
* Eliminate human cognitive overhead in formulating the next prompt.
* Guarantee that Sprint N+1 is strictly grounded in the actual codebase state left by Sprint N.
* Enforce automated pre-flight fitness verification at every session boundary.
* Maintain 100% pure Python Standard Library runtime in core modules.

## Considered Options
1. Static multi-sprint prompt lists (Waterfall, brittle to implementation changes).
2. Autonomous continuous execution in a single giant session (Context bloat and hallucination risks).
3. Dynamic Handoff Protocol via `.context/sprint_handoff.json` and `main.py handoff` (Chosen).

## Decision Outcome
Chosen option: **Dynamic Handoff Protocol** (Option 3).
1. **Session Termination Lifecycle:**
   - Every sprint concludes with three gates:
     a) `main.py fitness` (must pass 100%).
     b) `main.py distill` (updates transcript intelligence).
     c) `main.py handoff` (generates `.context/next_sprint.md` and machine-readable `sprint_handoff.json`).
2. **Next Sprint Prompt Generation:**
   - The handoff engine introspects git status, passing tests, and project roadmap (`specs/**/tasks.md`) to assemble the exact executable command for the next sprint (`./run_b_sdd.sh "<refined_prompt>"`).
3. **Machine-Readable & Human Handoff Artifacts:**
   - `.context/sprint_handoff.json`: contains structured metadata (schema version, session ID, timestamp, git branch/commit, modified files, fitness gate status, completed/pending tasks, next sprint prompt and run command).
   - `.context/next_sprint.md`: concise briefing document summarizing upstream accomplishments and downstream objectives.
4. **Auto-Chaining Execution (`run_b_sdd.sh --auto-chain`):**
   - Support `--auto-chain [N]` in `run_b_sdd.sh` to automatically loop across successive sprints with fresh session contexts until all tasks complete or max sprints reached.

## Invariants
- Downstream sprints cannot generate a handoff artifact if upstream architectural fitness tests are failing.
- Handoff prompts must deterministically prefix active rules and explicitly cite target task and modified seams.
- Handoff artifacts must be emitted in both machine-readable JSON (`sprint_handoff.json`) and human-readable Markdown (`next_sprint.md`).
- Core handoff synthesis in `src/` must strictly use 100% pure Python Standard Library.
- Auto-chain runner must verify zero invariant deviation before launching subsequent fresh sessions.


---

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


---

# ADR-009: Astryx Design System Architecture and Universal Responsive Cockpit

* **Status:** Accepted
* **Date:** 2026-09-17
* **Component:** ui
* **Supersedes:** None

## Context and Problem Statement
The developer workbench (`b-sdd-ui`) originally relied on ad-hoc Tailwind styling and lacked uniform design system primitives, causing visual inconsistency, fragile responsive layouts, and unergonomic mobile behavior. Furthermore, as documented in `docs/decision/DELTA_C_ASTRYX_OMISSION.md`, early frontend builds lacked formal Astryx component primitives and failed to provide accessible, touch-safe mobile operation for field engineers. Operator interfaces require a high-density, Swiss High-Tech Dark design system with strict accessibility, responsive ergonomics, and robust separation between desktop multi-zone views and mobile execution cockpits.

## Decision Drivers
* Standardize on the Astryx component architecture (`Button`, `IconButton`, `Badge`, `Dot`, `Banner`, `Selector`, `Segmented`, `Dialog`, `Drawer`, `Toast`).
* Enforce the Swiss High-Tech Dark design language (dark canvas `#090d13`, panel `#0d121c`, card `#141b27`, amber and emerald semantic accents).
* Provide full responsive parity between desktop wide screens and mobile touchscreen devices.
* Guarantee touch-safe ergonomic interaction for DRAKON logic modeling and HITL Phase reviews.
* Maintain universal portability and zero runtime regression in client bundles.

## Considered Options
1. Retain ad-hoc Tailwind classes with no unified component contracts (High visual fragmentation, broken mobile experience).
2. Heavy third-party proprietary component libraries requiring cloud telemetry or conflicting CSS runtimes.
3. Astryx Design System architecture with Swiss High-Tech Dark CSS custom properties, typed primitives, and dual responsive cockpits (Desktop & Mobile) (Chosen).

## Decision Outcome
Chosen option: **Astryx Design System Architecture and Universal Responsive Cockpit** (Option 3).

### 1. Astryx Primitives Layer
The UI standardizes on accessible Astryx primitives in `src/components/astryx/`:
* `Button` / `IconButton`: Strict variant contracts (`primary`, `secondary`, `success`, `destructive`, `ghost`) and sizing (`sm`, `md`, `lg`).
* `Badge` / `Dot`: Status indicators supporting `emerald`, `amber`, `cyan`, `rose`, `violet`, and pulsing states.
* `Banner`: Contextual invariant feedback with action slots.
* `Selector`: Stylized bound selection for specifications, projects, and pipeline templates.
* `Segmented`: Keyboard-navigable multi-state mode switches.
* `Dialog` / `Drawer`: High-density modal flows and sliding side drawers.
* `Toast`: Ephemeral notification queue for synchronous server operations.

### 2. Dual Responsive Cockpit Modes
The workbench provides two synchronized view modes:
* **Desktop Cockpit (>=768px):** Full 4-zone high-density view (Topbar, HITL Stepper, DRAKON Studio, LLM Copilot panel, Bitemporal Radar strip).
* **Mobile Cockpit (<768px or explicit toggle):** Touch-friendly single-view interface with bottom navigation tabs (`ДРАКОН`, `Копілот`, `Радар`, `Фази`) and touch-safe vertical workflow visualization.
* **Manual Override:** Operators can explicitly toggle between Desktop and Mobile preview modes at any time.

## Invariants
- ADR-009-INV-01: Operator cockpit UI must strictly compose Astryx-shaped primitives adhering to the Swiss High-Tech Dark design specification.
- ADR-009-INV-02: Operator cockpit must support dual responsive rendering (Desktop Multi-Zone & Mobile Ergonomic) with explicit user-controllable preview toggles.
- ADR-009-INV-03: Mobile view must provide touch-safe vertical workflow visualization and prevent mouse-dependent CAD drag locks on mobile touchscreens.


---

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


---

# ADR-011: Live GitHub API Sync and Appwrite Realtime Phase Sync

* **Status:** Accepted
* **Date:** 2026-09-17
* **Component:** adapters
* **Supersedes:** None

## Context and Problem Statement
The developer workbench (`b-sdd-ui` and `workbench_server.py`) previously presented simulated GitHub repository data in `ProjectSwitcherModal` and retained sprint phase progression solely in ephemeral browser React state. In production multi-tenant environments, engineering teams require:
1. Live synchronization with GitHub repositories (`maxfraieho` and corporate enterprise orgs) to introspect branches, commits, and repository metadata directly from the workbench.
2. Centralized, real-time synchronization of Human-in-the-Loop (HITL) sprint phases ($\Phi_1$ through $\Phi_7$) through the Appwrite BaaS control plane, broadcasting phase transitions to all connected engineering operators.
3. Cryptographically signed operator approvals (Ed25519 / WORM audit ledger) during the $\Phi_6 \to \Phi_7$ Review Gate to ensure non-repudiation.

## Decision Drivers
* Implement pure Python Standard Library adapters in `src/adapters/` with zero external pip dependencies.
* Provide live GitHub REST API querying with disk-backed cache (`.context/github_cache.json`) and offline fallback.
* Implement Appwrite BaaS control plane adapter and Realtime Server-Sent Events (SSE) streaming gateway for sub-second phase synchronization.
* Enforce cryptographic operator signature verification on sprint approval requests.
* Maintain all B-SDD foundational fitness gates: compile latency <50ms, context words <500, pure stdlib.

## Considered Options
1. Require external third-party SDKs (`PyGithub`, `appwrite`, `nacl`) — Violates B-SDD Zero-Dependency Pure Runtime Invariant.
2. Restrict to browser-only client-side API keys — Leaks credentials and fails to maintain sovereign audit logs on backend.
3. Pure Python Standard Library Adapters with Live GitHub HTTP Client, Appwrite Control Plane Client, and Realtime SSE Phase Synchronizer (Chosen).

## Decision Outcome
Chosen option: **Pure Python Standard Library Adapters with Live GitHub HTTP Client, Appwrite Control Plane Client, and Realtime SSE Phase Synchronizer** (Option 3).

### 1. Live GitHub API Sync Adapter (`src/adapters/github_sync.py`)
* Uses `urllib.request` with optional `GITHUB_TOKEN` authentication and custom User-Agent.
* Exposes `fetch_user_repositories(username)` and `sync_repositories()` with intelligent disk cache in `.context/github_cache.json`.
* Provides offline parity: if remote GitHub is unreachable or rate-limited, returns cached repository snapshot with live=False indicator.
* Integrated into `GET /api/github/repos`, `POST /api/github/sync`, and `GET /api/projects`.

### 2. Appwrite BaaS Control Plane Adapter (`src/adapters/appwrite_client.py`)
* Implements pure stdlib HTTP client for Appwrite Database & Collections (`b_sdd_cycles`).
* Manages sprint phase states ($\Phi_1$ Framing to $\Phi_7$ Distillation) and writes WORM audit records.
* Verifies cryptographic operator signatures (`Ed25519` / HMAC-SHA256 non-repudiation tokens) before advancing $\Phi_6 \to \Phi_7$.

### 3. Realtime Phase Event Streaming Gateway (`src/server/workbench_server.py`)
* Implements thread-safe pub/sub event broadcaster delivering real-time phase change events.
* Exposes `GET /api/realtime/phases` (SSE stream) for instant push updates to client cockpits.
* Exposes `POST /api/sprint/phase` to advance or set phase, automatically broadcasting to all connected operators and syncing with Appwrite.

## Invariants
- ADR-011-INV-01: GitHub API sync adapter must operate strictly via Python Standard Library with disk-backed offline fallback parity.
- ADR-011-INV-02: Appwrite Realtime phase sync must broadcast state transitions in real time via SSE/WebSocket with offline fallback parity.
- ADR-011-INV-03: Phase review approvals must accept and cryptographically verify operator signature before unlocking next sprint execution.


---

# ADR-012: Production Deployment and Telemetry Instrumentation

* **Status:** Accepted
* **Date:** 2026-09-17
* **Component:** server
* **Supersedes:** None

## Context and Problem Statement
With the B-SDD Workbench supporting live GitHub API synchronization, Appwrite Realtime phase sync, and sovereign model inference, the framework requires production-grade deployment and real-time observability. Production deployments across sovereign bare-metal servers (`192.168.3.184`, `192.168.3.251`), Cloudflare Tunnels (`bsdd.exodus.pp.ua`), and Cloudflare Pages (`b-sdd-ui.pages.dev`) must ensure continuous availability, sub-50ms compiler SLA enforcement, zero invariant regressions, and live operator telemetry without introducing heavy external third-party observability agents.

## Decision Drivers
* Zero third-party dependency runtime in `src/` (pure Python Standard Library).
* Sub-millisecond (<1ms) telemetry collection overhead to prevent polluting compilation latency.
* High-precision latency quantiles (p50, p90, p95, p99) for compiler runs, API requests, and visual DRAKON validations.
* Standard Prometheus text exposition format (`/api/metrics`) and JSON snapshot (`/api/telemetry`).
* Real-time Server-Sent Events (SSE) telemetry stream for the Astryx Cockpit UI.
* Automated multi-tier production deployment pipeline with systemd daemon management and post-deployment health verification probes.

## Considered Options
1. External monitoring agents (Prometheus client_python, Datadog agent, OpenTelemetry SDK) — Violates B-SDD Zero-Dependency Pure Runtime Invariant.
2. Static server log files without runtime aggregation — Poor operator visibility, high disk I/O, no live UI gauge capability.
3. Pure Python Standard Library Telemetry Adapter with Prometheus Exporter, Realtime SSE Streaming, and Sovereign Deployment Daemon (Chosen).

## Decision Outcome
Chosen option: **Pure Python Standard Library Telemetry Adapter with Prometheus Exporter, Realtime SSE Streaming, and Sovereign Deployment Daemon** (Option 3).

### 1. Telemetry Collector (`src/adapters/telemetry.py`)
* Lightweight ring-buffer latency tracking with exact percentile computation (p50, p90, p95, p99).
* Request, error, invariant check, and cache hit/miss counters.
* Context manager `measure_latency()` with <0.05ms overhead.
* Prometheus exposition generator (`/api/metrics`) and JSON summary generator (`/api/telemetry`).

### 2. Workbench Server Instrumentation (`src/server/workbench_server.py`)
* Automatic instrumentation of all incoming HTTP requests and responses.
* Compile latency tracking linked to the sub-50ms SLA budget.
* Periodic SSE telemetry broadcaster (`/api/realtime/telemetry`) streaming live vitals to connected Astryx cockpits.
* Production daemon support with systemd service definition and graceful shutdown.

### 3. Production Deployment Suite (`scripts/deploy_production.sh`)
* Automated staged rollout: pre-flight compile -> test suite -> frontend build -> Cloudflare Pages deploy -> systemd restart on sovereign runner -> end-to-end health probe verification.

## Invariants
- ADR-012-INV-01: Telemetry collector must strictly use Python Standard Library with zero third-party dependencies.
- ADR-012-INV-02: Telemetry collection overhead must remain strictly under 1 millisecond per request.
- ADR-012-INV-03: Metrics must be exportable in standard Prometheus exposition format and JSON over HTTP.
- ADR-012-INV-04: Production deployment must support automated health verification probes before traffic cutover.
- ADR-012-INV-05: Realtime telemetry stream must broadcast system metrics and latency percentiles via SSE.


---

