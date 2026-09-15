# Plan 001: Compiler Core Implementation

## Architecture
- `BSDDCompiler` class managing parsing, hashing, local SQLite caching, and rendering.
- Markdown parsers for MADR/Nygard ADRs, SDD specs, and constitution.
- Domain resolver with GitNexus AST impact support and path fallbacks.

## Verification
- Automated unit and fitness tests (`pytest tests/test_architecture_fitness.py`).
