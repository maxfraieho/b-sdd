# Spec 001: B-SDD Pre-Flight Intent & Capability Compiler

## Objective
Provide a deterministic, zero-dependency pre-flight compiler that parses ADRs, Specs, and Constitution to produce a <500-word active rules snapshot in <20ms.

## Invariants
- Execution latency: warm cache execution < 50ms (target < 20ms).
- Token budget: word count <= 500 words.
- Zero dependencies: standard library Python only.
- Strict supersession: decisions marked as superseded are mathematically excluded from active rules.
