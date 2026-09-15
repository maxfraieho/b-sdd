# B-SDD: Bitemporal Spec-Driven Development
## Architecture Specification, Methodology Manifesto, and Universal Engineering Standard

---

## Abstract
Modern software engineering increasingly relies on autonomous and semi-autonomous AI coding agents (Claude Code, OpenAI Codex CLI, Google Antigravity CLI, Cursor, Windsurf). However, long-running agent workflows inevitably suffer from **Architectural Drift** — the gradual degradation of structural boundaries, resurrection of deprecated decisions, context bloat, and subtle contract violations across iterations.

**B-SDD (Bitemporal Spec-Driven Development)** is a deterministic engineering framework that unifies:
1. **Bitemporal Architectural Ledgers (WHAT):** Architectural Decision Records (ADRs) governed by two orthogonal time dimensions (*valid time* and *transaction time*) with an explicit Directed Acyclic Graph (DAG) of supersession edges.
2. **Static Code Intelligence Graphs (WHERE):** Abstract Syntax Tree (AST) code property graphs (GitNexus) that map changed files to architectural components and upstream dependencies.
3. **Procedural Agent Skills (HOW):** Decoupled operational capabilities and playbooks (`SKILL.md`) that are dynamically routed to agents and self-crystallize when patterns repeat ($\ge 2$ times).
4. **Deterministic Pre-Flight Compilation (WHEN):** An ultra-fast (<20ms), lightweight (<500 words), zero-dependency compiler that extracts active constraints before turn 1 of agent execution.
5. **Automated Architectural Fitness Gates (VERIFY):** Continuous unit tests (`pytest`) that enforce latency, token budget, dependency purity, and DAG integrity as code.

$$\text{B-SDD} = \text{Bitemporal Invariants} + \text{AST Graph Routing} + \text{Procedural Skills} + \text{Deterministic Compiler} + \text{Fitness Gates}$$

---

## 1. Why Existing Paradigms Fail (The Architecture Drift Crisis)

To understand why B-SDD is necessary, we must analyze the structural failure modes of current industry solutions:

```
+---------------------------------------------------------------------------------------------+
|                                    THE DRIFT SPECTRUM                                       |
|                                                                                             |
|   [ Flat Rules (.cursorrules) ]          [ Naive Vector RAG ]           [ Plain Agent Skills ]   |
|   - Context Window Bloat (>2000w)        - Probabilistic Cosine Match   - Knows HOW to edit      |
|   - No Supersession Awareness            - Resurrects Deprecated Code   - Ignores WHAT is banned |
|   - Contradictory Invariants             - Fails on Keyword Overlap     - No Project Invariants  |
|                                                                                             |
|                                         V                                                   |
|                         [ B-SDD Deterministic Framework ]                                   |
|                         - Bitemporal DAG: valid_to = NOW                                    |
|                         - Mathematical Pruning of Old Decisions                             |
|                         - Pre-Flight Compile < 20ms, < 500 words                            |
|                         - Automated Fitness Gates (pytest)                                  |
+---------------------------------------------------------------------------------------------+
```

### 1.1. Flat Static Rule Files (`.cursorrules`, `.windsurfrules`, Copilot Instructions)
- **Mechanism:** A static markdown file is injected verbatim into every agent prompt.
- **Fatal Flaw:** As a project matures, the rules file balloons past 2,000–5,000 tokens. When a team switches from technology $A$ to technology $B$, developers append new rules without removing old nuances. The LLM receives contradictory mandates, suffers attention dilution, and hallucinates deprecated patterns.

### 1.2. Naive Vector RAG (LangChain, LlamaIndex, MemGPT / Letta)
- **Mechanism:** Architecture documents are chunked, embedded, and retrieved via cosine similarity on the prompt.
- **Fatal Flaw (Supersession Failure):** Vector embeddings measure *topical proximity*, not *chronological validity*. If `ADR-008` specified *"Direct Stripe integration"* and `ADR-013` specified *"Stripe is retired in favor of Swiss QR-bill"*, a prompt asking *"How do we handle payments?"* retrieves both documents because their semantic embeddings overlap heavily. The agent frequently hallucinates the obsolete pattern.

### 1.3. Procedural Agent Skills in Isolation (Anthropic MCP, Claude Code Skills)
- **Mechanism:** Specialized tool folders (`SKILL.md`) providing instructions on how to invoke APIs, run CLI tools, or build components.
- **Fatal Flaw:** Skills provide procedural dexterity (**HOW**), but have no awareness of project-specific architectural boundaries (**WHAT IS FORBIDDEN**). An agent equipped with a generic web design skill does not know that this specific banking project prohibits third-party CDN fonts or restricts database access to an isolated internal subnet.

### 1.4. The B-SDD Solution
B-SDD resolves these failures through mathematical determinism:
- Invariants are stored in a bitemporal ledger where superseded decisions have `valid_to = CURRENT_TIMESTAMP`.
- The pre-flight compiler mathematically excludes any record where `valid_to < NOW`.
- Only active, non-superseded invariants relevant to the modified files are compiled into the agent's prompt, budgeted strictly under 500 words.

---

## 2. The 5 Pillars of B-SDD

### Pillar 1: Bitemporal Architectural Truth (Utopia DB)
In standard databases, updates overwrite history. In B-SDD, architectural decisions adhere to the SQL:2011 bitemporal model:
- **Valid Time (`valid_from`, `valid_to`):** The interval during which an architectural invariant represents true, active policy in the software system.
- **Transaction Time (`tx_from`, `tx_to`):** The physical timestamp when the record was committed to the immutable ledger.

```sql
-- Atomic supersession in Utopia DB
SELECT intent_store.register_and_supersede_intent(
    p_intent_key      := 'ADR-021',
    p_component       := 'api',
    p_rule_type       := 'invariant',
    p_scope           := 'global',
    p_target_key      := 'WebSocket Notification Protocol',
    p_target_value    := 'All real-time notifications must stream over WSS.',
    p_source_file     := 'docs/adr/ADR-021-websocket-notifications.md',
    p_source_hash     := 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    p_supersedes_adr  := 'ADR-014',
    p_reason          := 'High polling latency on mobile clients'
);
```

### Pillar 2: Static Code Intelligence Graph (GitNexus)
Rather than guessing which rules apply, B-SDD queries the GitNexus code property graph (`.gitnexus/index.sqlite`). When a file is modified:
1. GitNexus traces recursive caller/callee relationships and component boundaries.
2. The impacted architectural domains (`core`, `api`, `web`, `db`, `workers`) are computed upstream.
3. The compiler activates only the invariants and skills pertinent to those domains.

### Pillar 3: Procedural Skill Lifecycle & The Rule of 2
B-SDD separates *declarative boundaries* (ADRs) from *procedural execution* (Skills):
- **Compilation:** The compiler emits a `RECOMMENDED PROCEDURAL SKILLS` block in `.context/active_rules.md`.
- **Intake:** The agent matches its task to recommended playbooks (`architecture-designer`, `safe-refactor`, `frontend-design`).
- **Discovery Fallback:** If a required capability is missing, the agent invokes `find-skills`.
- **The Rule of 2 (Autonomous Self-Authoring):**
  $$\text{Workflow Frequency} \ge 2 \implies \text{Mandatory Crystallization via } \texttt{skill-creator}$$
  Whenever an engineering pattern or sequence repeats two or more times without a formalized skill, the agent is mandated to author and test `.agents/skills/<new-skill>/SKILL.md`.

### Pillar 4: Deterministic Pre-Flight Compiler
The compiler (`src/core/compiler.py`):
- Operates in **100% pure Python Standard Library** with zero runtime dependencies.
- Compiles within **<20ms warm latency** via in-memory mtime hashing and SQLite caching.
- Enforces a **strict 500-word context ceiling**, ensuring maximum token efficiency and zero agent fatigue.

### Pillar 5: Automated Architectural Fitness Gates
CI/CD and local hooks run `tests/test_architecture_fitness.py` before any commit:
1. `test_compile_latency_sub_50ms`: Latency verification.
2. `test_context_budget_sub_500_words`: Token density verification.
3. `test_zero_third_party_dependencies_in_src`: Architectural runtime purity.
4. `test_supersession_dag_mathematical_pruning`: Guarantees superseded rules never appear in active prompts.
5. `test_procedural_skill_recommendation_present`: Procedural skill routing integrity.

---

## 3. The 6-Phase B-SDD Development Lifecycle

```
[ Phase 0: Pre-Flight Hook ]
       │  (run_agy.sh / b-sdd compile)
       ▼
[ Phase 1: Intent & Skill Compilation ] ────> .context/active_rules.md (<20ms, <500w)
       │                                     - Mandatory Invariants
       │                                     - Recommended Procedural Skills
       ▼
[ Phase 2: Skill Alignment & Discovery ] ───> Agent selects playbooks (or find-skills)
       │
       ▼
[ Phase 3: Specification Authoring ] ───────> specs/<NNN-feature>/ (spec.md, plan.md, tasks.md)
       │
       ▼
[ Phase 4: Implementation Execution ] ──────> Code edits governed by active invariants & skills
       │
       ▼
[ Phase 5: Fitness Gate Verification ] ─────> pytest tests/test_architecture_fitness.py (5/5 OK)
       │
       ▼
[ Phase 6: Skill Crystallization (Rule of 2)]> If pattern repeated >=2: invoke skill-creator
```

---

## 4. Industry Comparative Analysis Matrix

| Metric / Dimension | Cursor / Windsurf Rules | Vector RAG / MemGPT | DSPy Prompt Optimization | Anthropic Plain Skills | **B-SDD Framework** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Deterministic Supersession** | ❌ None | ❌ Probabilistic failure | ❌ None | ❌ None | ✅ **Mathematical DAG (`valid_to = NOW`)** |
| **Prompt Word Count** | ⚠️ Unbounded (>2000w) | ⚠️ Unbounded chunk dump | ⚠️ Variable | ⚠️ Skill payload only | ✅ **Strict ceiling (<500 words)** |
| **Pre-Flight Latency** | 0ms (Static file) | 300–1200ms (Embedding/DB) | 500–2500ms (LLM call) | 0ms (Static file) | ✅ **<20ms (Warm cached compiler)** |
| **Code Impact Graph** | ❌ None | ❌ None | ❌ None | ❌ None | ✅ **GitNexus AST Graph Routing** |
| **Procedural Dexterity** | ❌ Text prompt only | ❌ Text prompt only | ❌ Prompt only | ✅ High (Tool playbooks) | ✅ **Integrated Skills + Rule of 2** |
| **Automated Fitness Gates** | ❌ None | ❌ None | ⚠️ Metric evaluations | ❌ None | ✅ **Pytest Architecture Gates (5/5)** |
| **Runtime Dependencies** | 0 | Heavy (Chroma/Torch/LangChain) | Heavy (PyTorch/DSPy) | Low | ✅ **Zero (Pure Python stdlib in `src/`)** |

---

## 5. Universal CLI Reference

B-SDD includes a zero-dependency CLI (`src/cli/main.py`):

```bash
# Compile active rules for current workspace
python3 -m src.cli.main compile

# Compile active rules selectively for changed files
python3 -m src.cli.main compile --files src/core/compiler.py

# Synchronize all active intents and graph entities to Utopia DB
python3 -m src.cli.main sync --kb 01a08474-0000-7000-8000-000000000001

# Execute automated architectural fitness tests
python3 -m src.cli.main fitness

# Initialize B-SDD directory structure in a new or brownfield repo
python3 -m src.cli.main init --name "My Enterprise Project"

# Scaffold a new Architectural Decision Record
python3 -m src.cli.main adr new "Kafka Event Streaming" --component core --supersedes ADR-002
```

---

## 6. Conclusion & Vision
B-SDD elevates AI agent engineering from ad-hoc prompt hacking into a mathematically rigorous, verifiable science. By coupling bitemporal ledgers, AST code property graphs, dynamic procedural skills, and deterministic context compilers, software teams can safely build massive, long-running systems with autonomous AI agents without fear of architectural drift.
