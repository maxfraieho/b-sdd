# B-SDD: Bitemporal Spec-Driven Development

[![Fitness Tests](https://img.shields.io/badge/Architecture%20Fitness-5%2F5%20Passing-brightgreen)](tests/test_architecture_fitness.py)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-100%25%20Python%20Stdlib-blue)](src/)
[![Latency](https://img.shields.io/badge/Compile%20Latency-%3C20ms-orange)](src/core/compiler.py)
[![Prompt Density](https://img.shields.io/badge/Prompt%20Ceiling-%3C500%20words-purple)](.context/active_rules.md)
[![Language](https://img.shields.io/badge/Documentation-English%20%7C%20Ukrainian-informational)](docs/B_SDD_METHODOLOGY.md)

> **Continuous Architectural Invariants without Context Drift.**  
> The deterministic reference architecture and pre-flight compiler for autonomous AI coding agents (Claude Code, OpenAI Codex CLI, Google Antigravity CLI).

---

## 🌐 Documentation
- 📖 [Full Methodology Specification & Manifesto (English)](docs/B_SDD_METHODOLOGY.md)
- 📖 [Повна специфікація та маніфест методології (Українська)](docs/B_SDD_METHODOLOGY.ua.md)
- 🇺🇦 [Українська версія README](README.ua.md)

---

## 💡 What is B-SDD?

When AI agents work on software over extended sessions, they suffer from **Architecture Drift**: they resurrect deprecated code, violate module boundaries, and hallucinate outdated requirements.

**B-SDD (Bitemporal Spec-Driven Development)** solves this through a deterministic 5-pillar synthesis:

$$\text{B-SDD} = \underbrace{\text{Bitemporal Invariants (Utopia DB)}}_{\text{WHAT (Boundaries \& Mandates)}} + \underbrace{\text{AST Code Graph (GitNexus)}}_{\text{WHERE (Component Topology)}} + \underbrace{\text{Procedural Skills (MCP)}}_{\text{HOW (Playbooks \& Tools)}} + \underbrace{\text{Deterministic Compiler}}_{\text{WHEN (Pre-Flight <20ms)}} + \underbrace{\text{Fitness Gates}}_{\text{VERIFY (pytest 5/5)}}$$

---

## ⚡ Quick Start (30 Seconds)

### 1. Pre-Flight Compilation
Before starting work or launching an agent, compile the active architectural rules:
```bash
./run_agy.sh
# or manually:
python3 -m src.cli.main compile
```
Output is generated in [`.context/active_rules.md`](.context/active_rules.md) in **< 20 ms**, strictly budgeted under **500 words**.

### 2. Run Architecture Fitness Tests
Verify that all 5 architectural fitness invariants pass:
```bash
pytest -v tests/test_architecture_fitness.py
```

### 3. Synchronize to Utopia DB (Optional)
Push active intents and graph relationships to the central Utopia Knowledge Graph:
```bash
python3 scripts/sync_utopia.py
```

---

## 📊 Industry Comparison Matrix

| Feature | Cursor / Windsurf Rules | Vector RAG / MemGPT | DSPy Optimization | Plain Agent Skills | **B-SDD Framework** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Deterministic Supersession** | ❌ None | ❌ Probabilistic failure | ❌ None | ❌ None | ✅ **Mathematical DAG (`valid_to = NOW`)** |
| **Prompt Word Count** | ⚠️ Unbounded (>2000w) | ⚠️ Unbounded chunk dump | ⚠️ Variable | ⚠️ Skill payload only | ✅ **Strict ceiling (<500 words)** |
| **Pre-Flight Latency** | 0ms (Static file) | 300–1200ms (Embedding/DB) | 500–2500ms (LLM call) | 0ms (Static file) | ✅ **<20ms (Warm cached compiler)** |
| **Code Impact Graph** | ❌ None | ❌ None | ❌ None | ❌ None | ✅ **GitNexus AST Graph Routing** |
| **Procedural Dexterity** | ❌ Text prompt only | ❌ Text prompt only | ❌ Prompt only | ✅ High (Tool playbooks) | ✅ **Integrated Skills + Rule of 2** |
| **Automated Fitness Gates** | ❌ None | ❌ None | ⚠️ Metric evaluations | ❌ None | ✅ **Pytest Architecture Gates (5/5)** |
| **Runtime Dependencies** | 0 | Heavy (Chroma/Torch/LangChain) | Heavy (PyTorch/DSPy) | Low | ✅ **Zero (Pure Python stdlib in `src/`)** |

---

## 🔄 The 6-Phase Development Lifecycle

```
[ Phase 0: Pre-Flight Hook ] ──────────> run_agy.sh / b-sdd compile
                                          │
                                          ▼
[ Phase 1: Intent & Skill Routing ] ───> .context/active_rules.md (<20ms, <500w)
                                          - MANDATORY ARCHITECTURAL INVARIANTS
                                          - RECOMMENDED PROCEDURAL SKILLS
                                          │
                                          ▼
[ Phase 2: Skill Alignment ] ──────────> Agent selects playbook (or invokes find-skills)
                                          │
                                          ▼
[ Phase 3: Spec Authoring ] ───────────> specs/<NNN>/ (spec.md, plan.md, tasks.md)
                                          │
                                          ▼
[ Phase 4: Implementation ] ───────────> Code edits strictly respecting invariants
                                          │
                                          ▼
[ Phase 5: Fitness Gate ] ─────────────> pytest tests/test_architecture_fitness.py (5/5 OK)
                                          │
                                          ▼
[ Phase 6: Skill Evolution (Rule of 2)]> If workflow repeated >= 2 times: skill-creator!
```

---

## 🛠️ CLI Reference

```bash
# Compile active rules for current repo
python3 -m src.cli.main compile

# Selective compilation for modified files
python3 -m src.cli.main compile --files src/core/compiler.py

# Sync to central Utopia DB
python3 -m src.cli.main sync

# Run fitness gates
python3 -m src.cli.main fitness

# Scaffold B-SDD in a new or brownfield repo
python3 -m src.cli.main init --name "My Project"

# Scaffold a new Architectural Decision Record (ADR)
python3 -m src.cli.main adr new "WebSocket Protocol" --component core --supersedes ADR-002
```

---

## 📁 Repository Structure

```
b-sdd/
├── .agents/skills/b-sdd/     # Universal B-SDD Agent Skill (SKILL.md)
├── .context/                # Compiled active rules & local SQLite cache
│   ├── active_rules.md      # Auto-compiled <500w prompt snapshot
│   └── intents_cache.sqlite # Local bitemporal cache
├── .specify/                # Project constitution & fundamental principles
│   └── constitution.md
├── docs/
│   ├── adr/                 # Architectural Decision Records (MADR / Nygard)
│   ├── B_SDD_METHODOLOGY.md # Complete English specification
│   └── B_SDD_METHODOLOGY.ua.md # Complete Ukrainian specification
├── specs/                   # Spec-Driven Development work packets
├── src/                     # 100% Pure Python Standard Library
│   ├── core/compiler.py     # Deterministic Pre-Flight Compiler (<20ms)
│   ├── adapters/
│   │   ├── utopia_db.py     # Bitemporal Utopia DB & Knowledge Graph Adapter
│   │   └── gitnexus_graph.py# GitNexus AST Impact Resolver
│   ├── gateway/             # NotebookLM Safety Verification Gateway
│   └── cli/main.py          # Universal B-SDD CLI
├── templates/               # Greenfield / Brownfield Scaffolding Templates
│   ├── adr/
│   ├── spec/
│   └── constitution.md
├── tests/
│   └── test_architecture_fitness.py # Automated Architecture Fitness Gates
├── run_agy.sh               # Bash pre-flight runner hook
└── run_agy.bat              # Windows pre-flight runner hook
```

---

## 📜 License
MIT License. Created by [@maxfraieho](https://github.com/maxfraieho).
