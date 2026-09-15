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
