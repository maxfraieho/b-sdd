"""Generator script for Doc 4: B-SDD Methodology and Ergonomic Blueprint."""
from pathlib import Path

ROOT = Path('/home/vokov/projects/b-sdd')
OUT_DIR = ROOT / 'docs' / 'notebooklm_sources'
OUT_DIR.mkdir(parents=True, exist_ok=True)

doc4_content = """# B-SDD METHODOLOGY, ASTRYX DESIGN SYSTEM & ERGONOMIC BLUEPRINT

**System:** B-SDD (Bitemporal Spec-Driven Development) Operator Workbench  
**Framework Version:** 1.0 (Pure Python Standard Library Runtime + React 19 Cockpit)  
**Standard References:** ADR-001 through ADR-012, ADR-FE-001, Astryx Design System

---

## 1. The B-SDD Philosophy & Core Axioms

B-SDD is an architectural paradigm designed to eliminate AI agent hallucination, context drift, and architectural decay during autonomous software engineering. It achieves this through five non-negotiable axioms:

1. **Axiom 1: Specification Precedes Code (Formal Pre-Condition)**
   - No code may be authored until the behavioral logic and architectural invariants are formally expressed as a DRAKON visual schema and recorded in an ADR.
2. **Axiom 2: Zero Foreign Runtime Dependencies (Sovereignty)**
   - The core compilation, validation, and handoff runtime must execute exclusively on the Python 3.12+ Standard Library with zero pip dependencies.
3. **Axiom 3: Deterministic Pre-Flight Gate (<50ms, <500 Words)**
   - Before an LLM agent receives any prompt, active rules are deterministically compiled from the bitemporal intent graph. The compiled rules payload must compile in under 50ms and strictly obey a budget under 500 words to prevent context crowding.
4. **Axiom 4: Bitemporal Auditability (Tv / Tt Duality)**
   - Every architectural intent possesses two distinct temporal coordinates:
     - **Valid Time ($T_v$):** When the architectural rule is valid in the business domain.
     - **Transaction Time ($T_t$):** When the rule was physically committed to the immutable WORM (Write-Once-Read-Many) ledger.
5. **Axiom 5: Human-in-the-Loop Sovereign Review (HITL Gate Φ6)**
   - AI agents propose solutions; the human architect holds sovereign decision authority. No sprint cycle may merge or distill without explicit cryptographic approval or Copy-on-Write branching.

---

## 2. The Seven HITL Phases (The Φ-Automaton)

The B-SDD lifecycle progresses through seven strictly deterministic states:

```
  ┌─────────────────────────────────────────────────────────────┐
  │                 B-SDD Deterministic Lifecycle               │
  └─────────────────────────────────────────────────────────────┘
      │
      ▼
  [ Φ1: Intent Framing ]
      │  • Operator defines problem statement & scope
      ▼
  [ Φ2: DRAKON Visual Logic ]
      │  • Algorithm constructed with 0 crossings on vertical skewer
      ▼
  [ Φ3: Formal TDD & Contracts ]
      │  • Invariants turned into executable assertions before implementation
      ▼
  [ Φ4: Pure Implementation ]
      │  • Autonomous AI coding strictly bounded by AST blast radius
      ▼
  [ Φ5: Automated Fitness Verification ]
      │  • 100% tests must pass; AST visitor verifies 0 unauthorized imports
      ▼
  [ Φ6: HITL Operator Review Gate ] ◄── (Human Architect Decision Point)
      │
      ├───────────────────────────────┐
      ▼ (Approve: Ed25519 signature)  ▼ (Reject & Branch: ΔC logged)
  [ Φ7: Session Distillation ]    [ Φ1: Intent Framing (COW Branch) ]
      │  • Multi-sprint handoff payload generated
      ▼
  [ Next Sprint Cycle (N+1) ]
```

### Phase Definitions:
- **Φ1: Intent Framing** — Formal capture of architectural intents, valid time bounds, and ADR creation.
- **Φ2: DRAKON Visual Logic** — Visual modeling of the control flow topology. Enforces planar skewer and eliminates ambiguous branching before a single line of implementation code is written.
- **Φ3: Formal TDD & Contracts** — Synthesizing unit, invariant, and contract tests from the DRAKON-IR and ADR specifications.
- **Φ4: Pure Implementation** — Bounded code generation by coding agents. Context is constrained by AST impact graph routing (ADR-004) to prevent hallucinated cross-domain refactoring.
- **Φ5: Automated Fitness Verification** — Strict execution of automated fitness functions: 100% test pass rate, AST import boundary checks, and pre-flight compilation benchmark (<50ms).
- **Φ6: HITL Operator Review Gate** — The human architect inspects the entire delta, test runs, and DRAKON topology. The architect either approves by providing a cryptographic Ed25519 signature or rejects with a negative invariant vector ($\Delta C$), triggering a Copy-on-Write (COW) rollback branch.
- **Φ7: Session Distillation & Handoff** — Compaction of sprint history, extraction of crystallizable skills under the Rule of 2 (ADR-003), and synthesis of `sprint_handoff.json` for seamless multi-session chaining.

---

## 3. Astryx Design System & Operator Cockpit Ergonomics

### 3.1 Design Philosophy: The Bloomberg Terminal for Software Architects
The Astryx design system is rooted in the Swiss High-Tech design philosophy:
- **Information Density:** High data density designed for 1080p and 1440p professional displays. Zero wasted whitespace, zero decorative animations that impede cognitive processing.
- **Single-Screen Observability:** The entire sprint state, visual topology, copilot terminal, and bitemporal timeline must be visible simultaneously on a single screen (100vh height, `body { overflow: hidden }`). Page-level scrolling is strictly prohibited (`FE-INV-01`).
- **Fault-Domain Isolation:** Every major functional zone is wrapped in an independent React `ErrorBoundary`. An uncaught exception in the Drakon canvas or Copilot terminal must never crash the Human Review Gate.

### 3.2 Chromatic Palette & Visual Hierarchy
- **Canvas Base (`#090d13`):** Deep void dark background maximizing contrast and reducing optical fatigue.
- **Panel Surface (`#0d121c`):** Structural borders and secondary structural containers.
- **Card / Surface (`#141b27`):** Elevated interactive widgets, modals, and inspector panels.
- **Subtle Borders (`#1e293b`):** Clean, crisp 1px division lines without blurry drop-shadows.
- **Semantic Accents:**
  - **Amber (`#f59e0b`):** Active sprint execution, primary controls, DRAKON action highlights.
  - **Emerald (`#10b981`):** Passed fitness gates, verified invariants, active valid time, live system health.
  - **Rose (`#f43f5e`):** Failed fitness checks, budget overflows, gate rejections, critical SLA alerts.
  - **Cyan (`#06b6d4`):** External VCS / GitHub sync, network endpoints, telemetry indicators.
  - **Violet (`#8b5cf6`):** Bitemporal invariants, ADR decision markers, formal ontology tags.

### 3.3 Typography
- **UI & Labels:** Inter / system-ui (400, 500, 600 weight) for crisp legibility at small point sizes (10px–13px).
- **Code, Logic & Telemetry:** JetBrains Mono (monospaced) for timestamps, node identifiers, invariant codes, and token metrics.

---

## 4. DRAKON Visual Logic Ergonomics

ADR-008 mandates that all algorithmic processes conform to the DRAKON visual language standard:
1. **Vertical Skewer (Шампур):** The main "happy path" of an algorithm flows strictly vertically from top to bottom on the leftmost vertical line.
2. **Right is Worse (Праворуч — гірше):** Any conditional branch that handles exceptions, errors, or alternative fallbacks MUST branch to the right. The positive ("Yes / Success") branch continues straight down along the skewer.
3. **Zero Line Crossings (Нуль перетинів):** No two connection lines may cross each other. All control graphs must remain strictly planar ($C = 0$).
4. **Symmetry & Planar Alignment:** Nodes at the same logical depth must align horizontally across columns to preserve visual scanning rhythm.
5. **Silhouette Macro-Structure:** Complex algorithms exceeding 15 nodes must be partitioned into named silhouettes with clear entry and exit contracts.

---

## 5. Anti-Drift Invariants and Governance

| Code | Invariant Statement | Validation Method | Failure Consequence |
|---|---|---|---|
| **A001-INV-01** | Historical records in WORM log are immutable | SHA-256 hash chaining | Immediate engine halt |
| **A002-INV-01** | Active rules compilation latency < 50ms | In-memory microbenchmark | Φ2 gate compilation error |
| **A002-INV-02** | Active rules word count < 500 raw words | Whitespace tokenizer | Φ2 gate budget overflow |
| **A003-INV-01** | Rule of 2: Pattern observed $\ge 2$ times before crystallization | Distiller pattern counter | Skill creation deferred |
| **A004-INV-01** | Code generation bounded to AST impact graph | GitNexus symbol traversal | Blast radius containment fault |
| **A005-INV-01** | Automated test suite passes 100% | Pytest test runner | Φ5 gate rejection |
| **A005-INV-02** | Zero unauthorized foreign imports in `src/` | AST import visitor | Φ5 fitness failure |
| **A007-INV-01** | Sprint handoff payload contains $\Delta C$ and checksum | JSON schema validator | Handoff rejection |
| **A008-INV-01** | DRAKON diagrams have 0 line crossings ($C = 0$) | Planar graph analyzer | Diagram save block |
| **FE-INV-01** | Workbench document body has `overflow: hidden` | Automated CSS linter | PR build failure |
| **FE-INV-02** | All UI colors derived exclusively from CSS tokens | AST CSS validator | Style violation |
"""

with open(OUT_DIR / '04_BSDD_METHODOLOGY_AND_ERGONOMIC_BLUEPRINT.md', 'w', encoding='utf-8') as fp:
    fp.write(doc4_content)
print('Generated Doc 4, size:', len(doc4_content))
